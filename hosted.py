import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from agents.tool import function_tool
# from agents.hosted import WebSearchTool  # ✅ Import WebSearchTool

import requests

# 🔹 Load environment variables
load_dotenv()

# 🔹 Gemini client setup
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

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

# ✅ Function Tool: Weather Fetcher
@function_tool("get_weather")
def get_weather(location: str, unit: str = None) -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Please add OPENWEATHER_API_KEY to your .env file."

    if not unit:
        unit = "C"

    unit_map = {"C": "metric", "F": "imperial"}
    owm_unit = unit_map.get(unit.upper(), "metric")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={owm_unit}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Couldn't fetch weather for {location}."

    data = response.json()
    temp = data['main']['temp']
    description = data['weather'][0]['description'].capitalize()

    return (
        f"City of {location.title()},\n"
        f"Weather search, {unit.upper()} scale,\n"
        f"{temp}° with {description}."
    )

# ✅ Function Tool: Student Finder
@function_tool("piaic_student_finder")
def student_finder(student_roll: int) -> str:
    data = {
        1: "Qasim",
        2: "Sir Zia",
        3: "Daniyal"
    }
    return data.get(student_roll, "Not Found")

# ✅ Main runner
async def main():
    agent = Agent(
        name="Smart Assistant",
        instructions="You help with both real-world data and web search when needed.",
        tools=[
            get_weather,
            student_finder,
             # ✅ Add web search tool!
        ],
        model=model
    )

    # Try a message that may trigger both tools
    result = await Runner.run(agent, "What's the weather in Lahore and who is the current prime minister of Pakistan?")
    print("\n📍 Final Output:\n", result.final_output)

# ✅ Script entry
if __name__ == "__main__":
    asyncio.run(main())
