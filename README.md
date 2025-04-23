# Function Tool (OpenAi Agent SDK)
## Code Explanation


## STEP 1: Importing the Tools You Need

                import os
                import requests
                import chainlit as cl
                from dotenv import load_dotenv
                from typing import cast, List
                from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
                from agents.run import RunConfig
                from agents.tool import function_tool


### Explanation:

* import os: Lets you work with your computer’s environment variables (like secret keys).

  * Real-world analogy: Think of os as a keychain holder—your app gets keys from it.

* import requests: Helps your code make requests to websites/APIs.

  * Like sending a message to a weather website saying “What’s the weather in Lahore?”

* import chainlit as cl: You're using the Chainlit framework, which helps you create chatbot-like web UIs.

* from dotenv import load_dotenv: Reads secret credentials (like API keys) from a .env file.

  * This file is like a hidden drawer where you keep passwords.

* from typing import cast, List: Helps Python understand the types of data we're working with.

* from agents...: You are bringing in different tools to build an AI agent that can:

  * Read messages

  * Decide how to reply

  * Use special tools (like weather finder)


## STEP 2: Load Secret Keys

                load_dotenv()

### Explanation:

 * This line loads your .env file so you can use GEMINI_API_KEY and OPENWEATHER_API_KEY.

                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if not gemini_api_key:
                    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")


* This grabs your Gemini API Key from the .env file.

* If it's not there, it raises an error telling you to go put it in.


## STEP 3: Define a Weather Tool

            @function_tool("get_weather")
            def get_weather(location: str, unit: str = None) -> str:

### Explanation:

* This is your own little weather app inside the agent.

* You’re giving your AI the power to fetch real weather using a tool called "get_weather".            


                api_key = os.getenv("OPENWEATHER_API_KEY")
                if not api_key:
                    return "API key not found. Please set OPENWEATHER_API_KEY in .env file."


* Pulls the weather API key. If it's missing, show an error message.


                        if not unit:
                            unit = "C"


* Default unit is Celsius unless user says otherwise.

                        unit_map = {"C": "metric", "F": "imperial"}
                        owm_unit = unit_map.get(unit.upper(), "metric")


* Converts human input into the OpenWeather format (like metric for Celsius).

                        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={owm_unit}"


* Forms a URL to ask OpenWeather: “Hey, give me the weather for this place in this unit.”

                            response = requests.get(url)

* Sends the actual request to the weather website.

                            if response.status_code != 200:
                                return f"Couldn't fetch weather for {location}. Please check the location name."

* If something goes wrong (like bad city name), it shows an error.

                            data = response.json()
                            temp = data['main']['temp']
                            description = data['weather'][0]['description'].capitalize()

* Extracts temperature and description (like "cloudy") from the data.

                        return (
                            f"City of {location.title()},\n"
                            f"Weather search, {unit.upper()} scale,\n"
                            f"{temp}° with {description}."
                        )

* Returns the weather as a poetic haiku!


## STEP 4: Student Finder Tool

                @function_tool("piaic_student_finder")
                def student_finder(student_roll: int) -> str:
                    data = {
                        1: "Qasim",
                        2: "Sir Zia",
                        3: "Daniyal"
                    }
                    return data.get(student_roll, "Not Found")

### Explanation:

* You’ve created another tool that helps the agent look up students using their roll numbers.

 * Example: “Who is student number 2?” → “Sir Zia”



## STEP 5: Chat Options When Chat Starts

                    @cl.set_starters
                    async def set_starts() -> List[cl.Starter]:
                    return [
                        cl.Starter(label="Weather", message="Tell me the weather of Karachi"),
                        cl.Starter(label="Student Finder", message="Find student with roll number 2"),
                    ]

### Explanation:

* This sets the buttons/options the user sees when they open your chatbot app.

 * Like clickable shortcuts: “Check weather” or “Find student.”


## STEP 6: When Chat Starts

                        @cl.on_chat_start
                        async def start():

* This function runs when the chatbot opens. Let’s break the parts:

                        external_client = AsyncOpenAI(
                            api_key=gemini_api_key,
                            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                        )

* It sets up Gemini (Google’s AI brain) so it can chat.

                        model = OpenAIChatCompletionsModel(
                            model="gemini-2.0-flash",
                            openai_client=external_client
                        )

* You tell the system: “Use Gemini 2.0 Flash model for responses.”

                        config = RunConfig(
                            model=model,
                            model_provider=external_client,
                            tracing_disabled=True
                        )

* Sets up the brain's settings like turning off extra logging (tracing).

                    cl.user_session.set("chat_history", [])
                    cl.user_session.set("config", config)

* Prepares memory for each user.

                        agent = Agent(
                            name="Assistant",
                            instructions="You only respond in a professional way.",
                            model=model,
                            tools=[get_weather, student_finder]
                        )
                        cl.user_session.set("agent", agent)

* Builds your AI Assistant, giving it the brain (model), behavior (instructions), and tools (weather & student finder).

                        await cl.Message(content="👋 Welcome! Ask me about the weather or find a student.").send()

* Sends the welcome message. 


## STEP 7: When a User Sends a Message

                        @cl.on_message
                        async def main(message: cl.Message):

This gets triggered every time the user says something.

                        msg = cl.Message(content="🤔 Thinking...")
                        await msg.send()

* Temporarily says “Thinking…” while the AI is working.

                        agent: Agent = cast(Agent, cl.user_session.get("agent"))
                        config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
                        history = cl.user_session.get("chat_history") or []

* Grabs the AI brain, settings, and previous messages.

                          history.append({"role": "user", "content": message.content})

* Saves the user message into memory.

                        result = Runner.run_sync(agent, history, run_config=config)
                        response_content = result.final_output

* Runs the agent with all the messages and gets the final reply.

                        msg.content = response_content
                        await msg.update()

* Updates the “thinking…” message with the actual AI reply.

                        history.append({"role": "assistant", "content": response_content})
                        cl.user_session.set("chat_history", history)

* Saves the assistant’s reply too, so it remembers next time.

                        except Exception as e:
                        msg.content = f"❌ Error: {str(e)}"
                        await msg.update()

* If something crashes, you show the error.



## Real-World Example:
Imagine you’re building a chatbot for your university. It can:

 * Tell weather using real-time data.

 * Find students by roll number.

 * Respond professionally using Google's Gemini model.

 * Run in a cool web-based chat interface.

This code connects everything: smart brain, tools, user messages, and a polished front-end.



# OpenAi Agent SDK Overview (Tools)

## 🧠 Quick Summary (For Busy Readers)

The OpenAI Agents SDK helps developers build smart AI agents that can do tasks like searching the internet, using tools, calling functions, and even working with other agents. These tools let the AI act more like a human assistant that can take action—not just answer questions.

New features are coming that will:

 * Make agents smarter (reason better, plan steps)

 * Help them remember stuff (long-term memory)

 * Let multiple agents work together (like a team)

 * Connect to real-world systems (IoT, websites)

 * Stay safe and reliable (guardrails)

 * Learn from experience (like trial and error)

 * Understand images, voice, and more (multimodal)

 * Be easier to build (low-code tools)


## 🪜 Step-by-Step Explanation for Beginners
Let’s imagine you are building your own AI assistant. You want it to do more than just chat. You want it to do things, like:

 * Look up something on Google

 * Read a file

 * Call a calculator function

 * Schedule a meeting

 * Use other mini-AIs
 
This is where the OpenAI Agents SDK comes in—it’s like a toolkit that gives your assistant superpowers. 


### 🧰 1. Types of Tools

**Tools** are like apps or skills the agent can use.

#### a. Hosted Tools (pre-made):

* Think of them as tools already made and hosted by OpenAI.

* 🧠 Example: Like Siri being able to search the web or open your calendar.

Examples:

* WebSearchTool: Search the internet

* FileSearchTool: Look inside files

* ComputerTool: Run tasks on your computer


#### b. Function Calling (custom tools):

* You can make your own tool using a Python function.

* Just add @function_tool to a function, and your agent can use it.

💡 Example: You create a convert_currency(amount, from, to) function. Now your AI can use this to convert currencies.


#### c. Agents as Tools:
 * One agent can use another agent like a tool.

👥 Example: A manager agent asks a "travel agent" AI to book tickets while another "budget agent" checks costs.


### 🔁 2. Tool Execution Flow
How does it work?

 * The AI sees it needs a tool

 * It runs the tool (e.g., a function)

 * Gets the result

 * Keeps working, like a human would

🎯 Real-world analogy: You ask your assistant, “What’s the weather?” They go to Google, search, return the result, and continue helping you.


### 🚨 3. Error Handling
If a tool breaks or fails:

* The SDK handles it gracefully

* Your AI won’t crash—it can recover and try again

🧯 Example: If a website is down, your assistant might try another one or say, “I couldn’t fetch it, want to try later?”


## 🚀 What’s Coming Next (Emerging Features)

These are future upgrades that will make AI agents even smarter and more human-like.


### 🧠 1. Smarter Thinking (Reasoning + Planning)

* AI could decide when to use a tool, all by itself.

* Break big tasks into small steps.

📌 Example: You say, "Plan a trip to Turkey."

* AI figures out: need dates → book flights → book hotel → check visa.

* It does all this by calling different tools at the right time.

### 🧠 2. Memory and Context

* Agents will be able to remember past conversations and info.

📘 Example: You told your AI last week you’re allergic to peanuts. Next time it plans meals, it avoids peanuts automatically.


### 🧑‍🤝‍🧑 3. Teamwork Between Agents

* Multiple AI agents can work together like a team.

* They hand off tasks and specialize.

👷 Example:

1. "Research Agent" finds all the laptops under $1000.

2. "Compare Agent" reviews specs.

3. "Decision Agent" picks the best one.


### 🌐 4. Real-World Integration (Beyond APIs)

 * Future agents might control IoT devices, GUIs, or generate tools on the fly.

🔌 Example: Your AI turns off your smart lights or books meetings directly from a web interface.


### 🛡️ 5. Safety and Guardrails

* Built-in safety to prevent bad actions (like deleting all files).

* Logging to explain decisions.

🦺 Example: Your agent won’t send your private files unless you approve it. And you can see why it took an action.


### 🧠 6. Reinforcement Learning

 * AI learns what works best over time through trial and error.

🎮 Example: Your scheduling AI tries different times for meetings, learns people prefer 2 PM, and starts picking that more often.


### 🎨 7. Multimodal (Text + Images + Audio)
 * Agents can understand images, voice, videos—not just text.

📷 Example: You show a photo of a broken part, and your AI finds the right replacement.


### 🧑‍💻 8. Low-Code Tools for Developers
 * Easier to build agents with drag-and-drop or simple code.

🔧 Example: You use a UI tool to build a customer service agent without needing deep programming skills.


## 🎯 Why All This Matters
Without these features, AI agents are like smart chatbots—they can talk, but not act.

With these features:

* They become true assistants.

* Can think, act, learn, and work together.

* Useful for businesses, education, automation, daily life.


## 🏁 Real-World Analogy

Imagine you hire a virtual assistant. At first:

 * They can just talk (chatbot).

Then you give them:

 * Tools (Google, calculator, booking system)

 * A memory (what you like/dislike)

 * A team (helpers for special tasks)

 * Safe boundaries (don’t share passwords)

Now, they’re not just chatting—they’re working like a real human assistant.

That’s the journey of AI agents. And the OpenAI Agents SDK is the toolkit that builds that assistant.