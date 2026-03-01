# 10-ResearchAgent

## What's New Here

**The Anthropic web search tool** — Claude can call a built-in web search tool natively through the API. Instead of us scraping URLs ourselves, we give Claude the ability to search and read pages as part of its reasoning loop. This is different from every previous project — the LLM is now deciding what to search for, not us.

**Gap detection** — after each round of research, the agent reads what it has found and asks "what important questions about this topic are still unanswered?" Those gaps become the next round of searches. This is what makes it genuinely autonomous.

**Multi-round planning** — the agent doesn't just search once. It plans, searches, evaluates gaps, plans again, searches again, until either the gaps are filled or it hits the max rounds limit.

### The Loop
topic given
    ↓
[PLAN]    generate initial search queries
    ↓
[SEARCH]  run searches, scrape results
    ↓
[EVALUATE] what gaps remain?
    ↓
gaps exist + rounds left → back to PLAN with new queries
    ↓
no gaps or max rounds hit
    ↓
[REPORT]  synthesize everything into structured report

### Project Structure

```
10-ResearchAgent/
├── src/
│   ├── config.py
│   ├── planner.py        ← generate search queries from topic + gaps
│   ├── searcher.py       ← run web searches via Anthropic tool
│   ├── gap_detector.py   ← identify what's still missing
│   ├── reporter.py       ← synthesize final report
│   ├── research_agent.py ← orchestrates the full loop
│   └── __init__.py
├── static/
│   └── index.html
├── reports/              ← saved markdown reports
├── app.py
├── requirements.txt
└── .gitignore
```


Start with what the user does and follow it all the way through.

## You type a topic and hit Start Research

The browser sends the topic and depth setting to **/research** in **app.py**. Flask hands it to **ResearchAgent.research()**. From here the user just waits — everything that happens next is autonomous.

### Round 1 — broad exploration

The agent calls **planner.py** first. Since it's round 1 with no gaps yet, the planner asks Haiku to think about the topic and generate 3-5 broad search queries covering different angles. For "nuclear fusion energy" it might return: "current state nuclear fusion 2025", "nuclear fusion energy companies progress", "ITER fusion reactor timeline".

Those queries go to **searcher.py**. For each query, it calls the Anthropic API with the web search tool enabled. This is different from every previous project — Claude itself decides what pages to visit, reads them, and returns a written summary of what it found. We don't scrape anything directly. We just get back a paragraph of synthesized findings per query.

All results accumulate in **all_research** — a running list of every query and its findings across all rounds.

### Gap detection — should we keep going?

**gap_detector.py** reads everything in **all_research** so far and asks Haiku: "given all this, what important aspects of the topic are still missing?" It returns a list like: "no information on fusion energy costs", "missing coverage of private sector investment", "nothing about timeline to commercial viability".

Then **is_research_complete()** checks the count. If fewer than 3 gaps remain, research is considered complete and the loop exits early. If 3 or more gaps exist and rounds remain, the loop continues.

### Round 2+ — targeted gap filling

The planner gets called again, but this time it receives the gap list. Instead of broad queries it generates targeted ones aimed specifically at what's missing — "nuclear fusion energy cost per kilowatt", "private fusion startups Commonwealth Fusion TAE Technologies", "when will fusion be commercially viable".

The searcher runs those, results go into **all_research**, gap detector runs again. This repeats until either the gaps drop below the threshold or the max rounds limit is hit.

### Report generation

Once the loop exits, **reporter.py** takes the entire **all_research** list — every finding from every round — and sends it to Claude Sonnet with a structured prompt: write a professional markdown report with an executive summary, clear section headers, specific facts from the research, and a key takeaways section.

Sonnet synthesizes everything into a coherent document. The report gets saved to disk with a timestamp filename and returned to the browser simultaneously.

### What makes this genuinely agentic

Every previous project had a fixed pipeline — inputs went in, outputs came out, same steps every time. This agent makes decisions mid-run. It decides how many rounds to run based on what it finds. It decides what to search for in round 2 based on what was missing in round 1. It decides when enough is enough. The path through the code is different every time depending on the topic and what the searches return. Sonnet 4.6


--------------------------------------------------------------------------------------------

## Search Adjustments

**More searches per round** — just increase SEARCHES_PER_ROUND in config. Easy but costs more tokens.
**More rounds** — increase MAX_ROUNDS. The genocide topic hit the ceiling at 2, bumping to 3-4 would let it keep filling gaps.
**Lower the gap threshold** — currently stops when fewer than 3 gaps remain. Dropping to 1 means it keeps searching until it's nearly complete.
**Smarter gap detection** — right now it finds 5 gaps every round even when research is improving. We could change the prompt to score gap severity and only continue if high-severity gaps remain.
**Cross-referencing** — after all searches complete, have Claude identify where sources agree vs conflict before writing the report. Adds a verification layer.
**Source diversity check** — tell the planner to explicitly vary search angles each round so it doesn't circle back to similar queries.

Looking at your run, the most obvious issue is that gaps never dropped below 5 across both rounds — meaning the gap detector isn't distinguishing between "critical missing information" and "would be nice to have." The planner was generating good targeted queries but the evaluator kept finding new gaps instead of acknowledging progress.

## Adjustments to be made

1. **Smarter gap detection** — severity scoring
Instead of just counting gaps, score each one 1-3:

3 = critical, report is incomplete without this
2 = important, would strengthen the report
1 = nice to have, minor detail

Only continue searching if any score-3 gaps remain. This stops the agent from chasing minor gaps forever and explains why your genocide topic kept hitting 5 gaps — some of those were genuinely critical, others were just "more detail would be nice."

2. **Progress awareness in the gap detector**
Right now the gap detector reads all research but doesn't know what round it's on or how much progress was made since last round. We should tell it: "last round you found these 5 gaps, here's the new research, which gaps were actually filled?" That way it evaluates improvement not just remaining gaps, which is a much more honest stopping condition.
These two changes work together — severity tells you what matters, progress awareness tells you if you're actually getting closer.
One more I'd add:

3. **Deduplicate queries across rounds**
Your round 2 queries were good but slightly overlapped with round 1. The planner should receive the full list of queries already run so it never searches the same angle twice. One line change in **research_agent.py** — pass **all_research** queries to the planner so it knows what's already been covered.


## What tools actually are

When you call the Anthropic API normally, Claude receives text and returns text. That's it — a one-shot input/output.

### Tools change this into a conversation between your code and Claude:

You → Claude: "here's a question, here are tools you can use"
Claude → You: "I want to call tool X with these arguments"
You → Claude: "here's what tool X returned"
Claude → You: "based on that result, here's my answer"
Claude doesn't execute tools itself — it just says "I want to use this tool with these inputs." Your code runs the actual tool and feeds the result back. Claude then continues reasoning with that result.

### How tools are defined

Every tool is a JSON schema you pass in the tools parameter:

```pythontools = [
    {
        "name": "web_search",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
]
```

Claude reads the description fields — that's how it decides when and how to use each tool. Good descriptions are everything.

### The web search tool is special

The tool we're using in searcher.py is different from custom tools:
pythontools = [{"type": "web_search_20250305", "name": "web_search"}]
This is a built-in Anthropic tool — Anthropic hosts and runs the actual search infrastructure. You don't implement the execution yourself. You just declare it and Claude handles the full search-and-read cycle internally. That's why searcher.py is so short — there's no scraping code because Anthropic's servers do it.

### Tools you could build yourself

These are custom tools where YOU write the execution code:

Calculator
```python
python{
    "name": "calculate",
    "description": "Evaluate a mathematical expression",
    "input_schema": {
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"]
    }
}
```
You already built this in your ReAct agent (project 6).

File reader
```python
python{
    "name": "read_file",
    "description": "Read the contents of a file from disk",
    "input_schema": {
        "properties": {"filepath": {"type": "string"}},
        "required": ["filepath"]
    }
}
```

Database query
```python
python{
    "name": "query_database",
    "description": "Run a SQL query against the database",
    "input_schema": {
        "properties": {"sql": {"type": "string"}},
        "required": ["sql"]
    }
}
```

HTTP request
```python
python{
    "name": "fetch_url",
    "description": "Fetch the content of a URL",
    "input_schema": {
        "properties": {"url": {"type": "string"}},
        "required": ["url"]
    }
}
```

Send email
```python
python{
    "name": "send_email",
    "description": "Send an email to a recipient",
    "input_schema": {
        "properties": {
            "to":      {"type": "string"},
            "subject": {"type": "string"},
            "body":    {"type": "string"}
        },
        "required": ["to", "subject", "body"]
    }
}
```

How you'd implement a custom tool in searcher.py

If you wanted to add a custom tool alongside web search — say, a tool that searches your Personal KB from project 9 — it would look like this:

```python
pythontools = [
    # Built-in Anthropic tool
    {"type": "web_search_20250305", "name": "web_search"},

    # Custom tool you define
    {
        "name": "search_personal_kb",
        "description": "Search the user's personal knowledge base for previously saved articles",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
]
```

Then after the API call you check if Claude used your custom tool and execute it:

```python
for block in response.content:
    if block.type == "tool_use" and block.name == "search_personal_kb":
        # Claude wants to search the KB — you run it
        kb_results = personal_kb.query(block.input["query"])
        # Feed results back to Claude in a follow-up message
```

Why this matters for your remaining projects

Workflow Automation — the whole project is tools. Gmail API becomes a send_email tool. Google Calendar becomes a check_calendar tool. Claude decides which tools to chain based on your request.

Multi-Agent — agents call other agents as tools. The research agent becomes a tool that the manager agent can invoke. That's literally how multi-agent systems work under the hood.

Tools are the mechanism that turns Claude from a text generator into something that can actually do things in the world.
