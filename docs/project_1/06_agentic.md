# Agent (Project 6) goes even further.

The model isn't just answering questions — it's deciding what actions to take. It gets a goal, plans steps, uses tools (search, code execution, APIs), observes results, and adjusts. This is where everything converges: the LLM understands language (like sentiment/text gen), retrieves information (like RAG), and takes sequential actions (like time series — step by step, each depending on the last).

--------------------------------------------------------------------------------

Before we write any code — let me explain what we're building and how it differs from everything else.

## What is an Agent?

Every project so far has been reactive — you give input, you get output, done. The agent is different. It gets a **goal**, then **decides what to do**, **takes actions**, **observes results**, and **decides what to do next**. It loops until the goal is met.

The core pattern is called **ReAct** (Reason + Act):
```
1. THINK:  "The user wants to know the weather in Paris and
            convert it to Fahrenheit. I need to first get
            the weather, then do math."
2. ACT:    Call weather tool for Paris → gets 18°C
3. OBSERVE: "Got 18°C, now I need to convert"
4. THINK:  "I need to calculate Fahrenheit"
5. ACT:    Call calculator tool → (18 × 9/5) + 32 = 64.4°F
6. OBSERVE: "Got 64.4°F, I have everything I need"
7. ANSWER: "It's 18°C (64.4°F) in Paris"

------------------------------------------------------------------------------------------

## Common agent projects people build

**Research Agent** — you give it a topic, it searches the web, reads articles, summarizes findings, and writes a report. "Research the pros and cons of electric vs gas cars" and it autonomously searches, reads multiple sources, and synthesizes everything.

**Code Assistant Agent** — you describe what you want, it writes code, runs it, sees the errors, fixes them, and reruns until it works. Basically a mini version of what tools like Claude Code do.

**Customer Support Agent** — it reads a customer message, looks up their order in a database, checks shipping status via API, and writes a response. The kind of thing companies actually deploy.

**Data Analysis Agent** — you give it a CSV or database, it decides what queries to run, generates charts, finds patterns, and writes insights. "Analyze my sales data and tell me what's interesting."

**Personal Assistant** — combines weather, web search, note-taking, reminders, calculations. A general-purpose helper that picks the right tool for whatever you ask.

**Web Scraping Agent** — you give it a goal like "find the 5 cheapest flights from NYC to London in March" and it navigates websites, extracts data, and compiles results.

**Multi-step Planner** — more complex version where the agent breaks a big goal into subtasks. "Plan a 3-day trip to Tokyo" becomes: search for flights, find hotels, look up restaurants, check weather, build itinerary.

For learning purposes, the research agent or personal assistant are the best starting points because they clearly demonstrate the ReAct loop and tool-use pattern without needing complex infrastructure like databases or sandboxed code execution.

