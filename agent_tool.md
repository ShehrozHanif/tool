# Agent-as-Tool (Code-Explanation)

## Project Goal:
You are building a multilingual translation chatbot using Chainlit + Gemini 2.0, where:

 * The main agent (Orchestrator) acts like a manager.

 * Two specialized agents act as tools: one for Spanish, one for French.


## Step 1: Importing Required Libraries

        import os
        import chainlit as cl
        from dotenv import load_dotenv
        from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled

### Why?

* os: Lets you access environment variables (e.g., API keys).

* chainlit: This is the library powering your chatbot UI.

* dotenv: To load sensitive info (like API keys) from a .env file.

* agents: Provides tools to define and run AI agents. This comes from the Agents SDK (like LangChain but cleaner).



## Step 2: Load API Key from .env

load_dotenv()

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env")

### Why?
You don’t want to hardcode secrets like your API key.
Instead:

* Save it in a .env file.

* Load it with dotenv.

* If it's missing, raise an error to avoid crashes.

### Real-world analogy:
Like getting your Google Maps API key before using the Maps feature in your app.


### Step 3: Setup Gemini Client

        external_client = AsyncOpenAI(
            api_key=gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

### Why?

You're using **Google Gemini** (not OpenAI).
This wraps Gemini to work with the **OpenAI-compatible interface** that Agents SDK supports.

### Real-world analogy:
It’s like plugging in a Google engine into a system designed for OpenAI — using an adapter.



## Step 4: Define the LLM Model

        model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=external_client
        )

### Why?
You tell your agents:

 "Hey, when you need to talk to an LLM, use Gemini 2.0 Flash."

This makes Gemini your **default AI brain.**


## Step 5: Set Defaults for All Agents

        set_default_openai_client(external_client)
        set_tracing_disabled(disabled=True)

### Why?
 * **set_default_openai_client:** Tells the system to use **Gemini for everything.**

 * **set_tracing_disabled:** Disables internal logs/tracing. (You can enable this in dev for debugging.)



## Step 6: Define the Spanish Agent

        spanish_agent = Agent(
            name="Spanish Agent",
            instructions="You translate the user's message to Spanish.",
            model=model
        )

### Why?
You define a specialized AI agent whose job is only one thing: **translate to Spanish.**

**Think of it as hiring a Spanish translator.**

## Step 7: Define the French Agent

        french_agent = Agent(
            name="French Agent",
            instructions="You translate the user's message to French.",
            model=model
        )

### Why?
Same idea, different specialist: This one translates to French.

#### Now you have 2 team members:

* Spanish expert

* French expert


## Step 8: Define the Orchestrator Agent

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


### Why?

This is your **boss agent** (Orchestrator). It:

Talks to the user

Looks at the user's request

Calls one of the translation agents based on the request

You use .as_tool() to turn other agents into callable tools.

### Real-world analogy:

 You (user) ask the receptionist (orchestrator), “Can you translate this to Spanish?”
 The receptionist forwards the task to the Spanish expert.


## Step 9: Setup Chainlit Chat on Start

        @cl.on_chat_start
        async def on_chat_start():
            cl.user_session.set("agent", orchestrator_agent)
            await cl.Message(content="🌍 Welcome! Ask me to translate anything to Spanish or French.").send()

### Why?

This function runs when the chat UI opens.

 * It stores the orchestrator agent in session.

 * Sends a welcome message.


## Step 10: Handle User Messages

        @cl.on_message
        async def on_message(message: cl.Message):
            agent = cl.user_session.get("agent")
            result = await Runner.run(agent, input=message.content)
            await cl.Message(content=result.final_output).send()

### Why?
 
 * Every time a user sends a message, this function is called.

 * It gets the orchestrator agent.

 * Passes the user’s message to the agent using Runner.run().

 * Sends the AI’s output back to the user.



# Project Overview

This project demonstrates how to use **Agent as Tool** in a Chainlit app, powered by the **Google Gemini** LLM.

## Key Components

| Part               | What it Does                             | Real-Life Analogy                               |
|--------------------|------------------------------------------|-------------------------------------------------|
| `.env` + `dotenv`   | Securely load your key                  | Keeping your passwords in a vault               |
| Gemini setup       | Connect to Google Gemini LLM            | Choosing which brain to use                     |
| Agent              | Defines a specialist                   | Hiring a translator                             |
| `as_tool()`        | Makes the agent callable                | Adding team members to the boss's contact list  |
| Orchestrator       | Main interface for user                 | A manager who delegates                         |
| Chainlit           | Provides Chat UI                        | A clean interface for users                     |

---

## Summary

- We load environment variables securely using `.env` and `dotenv`.
- We set up the Gemini LLM model to power our agents.
- Each **Agent** specializes in translating to a different language.
- Using `as_tool()`, agents can be called as tools by an **Orchestrator** agent.
- **Chainlit** provides a user-friendly chat interface where users can interact with the system.

## Real-World Understanding

Imagine you have a manager (Orchestrator) who has a list of expert translators (Agents).  
Whenever someone needs a translation, the manager checks their contact list (tools) and assigns the right translator for the job — all happening smoothly through a professional front desk (Chainlit UI).

---
