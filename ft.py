import asyncio
import json
import os
from typing_extensions import TypedDict, Any
from dotenv import load_dotenv

# Agents SDK Imports
from agents import Agent, FunctionTool, RunContextWrapper, function_tool

# Load environment variables
load_dotenv()


# 🔹 Define location as a TypedDict
class Location(TypedDict):
    lat: float
    long: float

# ✅ Function Tool: Fetch Weather
@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location."""
    # In a real-life scenario, we would call a weather API here
    return "sunny"  # For the example, return a static response.

# ✅ Function Tool: Read File (e.g., reading contents from a file)
@function_tool(name_override="fetch_data")
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file."""
    # In a real-life scenario, we would read the file from the filesystem
    return "<file contents>"  # Static example

# ✅ Create the agent
agent = Agent(
    name="Assistant",
    tools=[fetch_weather, read_file],  # Add the tools to the agent
)

# ✅ Function to send a prompt and get a response
async def run_agent(prompt: str):
    response = await agent.run(prompt)  # Agent handles the prompt and returns the result
    print("Response from agent:", response)

# ✅ Main execution block
if __name__ == "__main__":
    prompt = "What’s the weather in Islamabad?"  # Example prompt to the agent
    asyncio.run(run_agent(prompt))  # Run the agent with the provided prompt
