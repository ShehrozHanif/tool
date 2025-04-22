# without chainlit app making function as tool , add weather api and student finder tool


import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from agents.tool import function_tool
import requests
from typing import Optional

# Load .env variables
load_dotenv()

# Gemini API Key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

# Set up Gemini client and model
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

set_default_openai_client(external_client)
set_tracing_disabled(disabled=True)

# Function to fetch weather
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

    # Default to Celsius if not provided
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



# 🎓 Just a sample student finder tool
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

# 🧪 Main async run
async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in a professional way.",
        tools=[get_weather, student_finder],
        model=model
    )

    result = await Runner.run(agent, "tell me the weather in lahore.")
    print(result.final_output)

# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(main())
