import os
import requests
import chainlit as cl
from dotenv import load_dotenv
from typing import cast, List
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.tool import function_tool

# Load environment variables
load_dotenv()

# Get Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

# ✅ Your Preferred get_weather Tool
@function_tool("get_weather")
def get_weather(location: str, unit: str = None) -> str:
    """
    Fetches the real weather for a given location from OpenWeatherMap,
    returning a poetic haiku-style response.
    Defaults to Celsius if unit is not provided.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "API key not found. Please set OPENWEATHER_API_KEY in .env file."

    if not unit:
        unit = "C"

    unit_map = {"C": "metric", "F": "imperial"}
    owm_unit = unit_map.get(unit.upper(), "metric")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={owm_unit}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Couldn't fetch weather for {location}. Please check the location name."

    data = response.json()
    temp = data['main']['temp']
    description = data['weather'][0]['description'].capitalize()

    return (
        f"City of {location.title()},\n"
        f"Weather search, {unit.upper()} scale,\n"
        f"{temp}° with {description}."
    )

# 🎓 Student Finder Tool
@function_tool("piaic_student_finder")
def student_finder(student_roll: int) -> str:
    """
    Find the PIAIC student based on the roll number.
    """
    data = {
        1: "Qasim",
        2: "Sir Zia",
        3: "Daniyal"
    }
    return data.get(student_roll, "Not Found")

# 🟢 Chainlit Starters
@cl.set_starters
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(label="Weather", message="Tell me the weather of Karachi"),
        cl.Starter(label="Student Finder", message="Find student with roll number 2"),
    ]

# 🟢 On Chat Start
@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    agent = Agent(
        name="Assistant",
        instructions="You only respond in a professional way.",
        model=model,
        tools=[get_weather, student_finder]
    )
    cl.user_session.set("agent", agent)

    await cl.Message(content="👋 Welcome! Ask me about the weather or find a student.").send()

# 🟢 On Message
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="🤔 Thinking...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_sync(agent, history, run_config=config)
        response_content = result.final_output

        msg.content = response_content
        await msg.update()

        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
