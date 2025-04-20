import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from agents.tool import function_tool

# Load environment variables
load_dotenv()

# Get API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Check your .env file.")

# Gemini client config
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Model setup
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Set default client
set_default_openai_client(external_client)
set_tracing_disabled(disabled=True)

# ------------------ TOOLS ------------------ #

@function_tool("piaic_student_finder")
def student_finder(student_roll: int) -> str:
    data = {
        1: "Qasim",
        2: "Sir Zia",
        3: "Daniyal"
    }
    return data.get(student_roll, "Not Found")

@function_tool("get_weather")
def get_weather(location: str, unit: str = None) -> str:
    """
    Returns a haiku about the weather in the specified location.
    Always in Celsius.
    """
    degree = "22 degrees Celsius"
    return (
        f"The weather in {location.title()},\n"
        f"{degree} fills the spring air,\n"
        f"Peaceful skies above."
    )

# ------------------ AGENT ------------------ #

async def main():
    agent = Agent(
        name="Assistant",
        instructions=(
            "You are a poetic assistant. Always respond in Professional way.\n"
            "When asked about weather, you must use the get_weather tool.\n"
            "Never guess. Always call the appropriate tool if it's available."
        ),
        tools=[get_weather, student_finder],
        model=model
    )

    # Prompt (try any variant!)
    result = await Runner.run(agent, "who is the founder of pakistan.")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
