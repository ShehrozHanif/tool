# In this code we are trying to use Agent as tool in chainlit app.

# chainlit_app.py
import os
import chainlit as cl
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled

# Load .env variables
load_dotenv()

# ✅ Setup Gemini client
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

# 🗣️ Spanish translation agent
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You translate the user's message to Spanish.",
    model=model
)

# 🗣️ French translation agent
french_agent = Agent(
    name="French Agent",
    instructions="You translate the user's message to French.",
    model=model
)

# 🧠 Orchestrator agent
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

# 🌐 Chainlit chat UI logic
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent", orchestrator_agent)
    await cl.Message(content="🌍 Welcome! Ask me to translate anything to Spanish or French.").send()

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    result = await Runner.run(agent, input=message.content)
    await cl.Message(content=result.final_output).send()
