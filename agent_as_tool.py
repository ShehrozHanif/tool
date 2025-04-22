#Without Chainlit Agent as Tool
# Compare this snippet from agent_as_tool_chainlit.py:

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled

# Load environment variables
load_dotenv()

# Setup Gemini client and model
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in .env")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

set_default_openai_client(external_client)
set_tracing_disabled(disabled=True)

# 🗣️ Spanish Agent
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You translate the user's message to Spanish.",
    model=model
)

# 🗣️ French Agent
french_agent = Agent(
    name="French Agent",
    instructions="You translate the user's message to French.",
    model=model
)

# 🧠 Orchestrator Agent with tools
orchestrator_agent = Agent(
    name="Orchestrator Agent",
    instructions="You are a translation agent. Use the tools provided to translate as requested.",
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate input to Spanish."
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate input to French."
        )
    ],
    model=model
)

# 🚀 Main async function
async def main():
    result = await Runner.run(
        orchestrator_agent,
        input="Say 'Hello, how are you?' in Spanish."
    )
    print("🟢 Final Output:\n", result.final_output)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
