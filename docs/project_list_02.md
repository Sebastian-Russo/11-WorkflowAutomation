# Project List 2 - Mix and match projects/models

## Professional:

Company documentation, SOPs, internal wikis
Codebase documentation
Slack/email archives
Meeting transcripts

## Technical:

API docs, technical manuals
Research papers
Programming language docs

## Creative:

World-building docs for D&D campaigns or fiction writing
Recipe collections
Travel journals/guides
-------------------------------------------------------------------------------------------

# Project list 2

**Personal Knowledge Base** — You take all your documents (notes, PDFs, bookmarks, code snippets, journal entries, saved articles) and build a RAG system over your entire life's information. "What was that article I read about investing in index funds?" or "What did I write about my goals last January?" The retrieval pipeline is the same as HP RAG, but the value is massive because no existing product does this well with YOUR data. You could add an agent layer that automatically ingests new documents, categorizes them, and updates the vector store. Over time it becomes a second brain that actually knows everything you've ever saved.

**Harry Potter RPG** — This one combines almost everything you've built. The RAG system retrieves accurate lore from the books so the game stays canon. An agent manages game state — your character's house, year, spells learned, inventory, relationships. The LLM generates narrative and dialogue based on your actions. You'd need a game state manager (new component), a character system, and a prompt engine that feeds the LLM your current state plus retrieved lore plus your action. "You're in the Forbidden Forest. A centaur blocks your path." → you type "I cast Lumos" → the agent checks if you've learned Lumos, retrieves lore about centaurs from the books, updates your state, and generates what happens next. This is a legit project that showcases agentic RAG, state management, and creative generation all in one.

**Research Agent** — You give it a topic and it autonomously searches the web, reads full articles (add a web scraping tool), takes notes on what it finds, identifies gaps in its research, searches again, and compiles a structured report. The difference from basic web search is depth — it doesn't just return search snippets, it actually reads sources, cross-references them, and synthesizes findings. "Research the current state of nuclear fusion energy" and it comes back with a multi-section report with sources. This builds directly on your agent by adding smarter tools and multi-step planning.

**Agentic RAG** — Your current RAG system does one search and hopes it finds the right chunks. An agentic RAG system thinks about the question first, decides how to search, evaluates the results, and searches again if they're not good enough. "Compare how Dumbledore and Snape viewed Harry's role in defeating Voldemort" — a basic RAG would do one search and maybe miss half the picture. An agentic RAG would break it into sub-questions ("How did Dumbledore view Harry's role?", "How did Snape view Harry's role?"), search for each separately, evaluate if the results are sufficient, and synthesize a comparison. This is the natural evolution of your RAG project combined with the agent's planning loop.

**Workflow Automation Agent** — A personal assistant that connects to real services. Email integration to draft and send responses, calendar management, file organization, task tracking. You'd add tools for each service (Gmail API, Google Calendar API, file system operations). "Check my calendar for tomorrow, draft an email to the team summarizing what we have scheduled, and create a reminder to prep for the 2pm meeting." Three tools, one request, fully automated. This is what companies actually pay engineers to build.

**Multi-Agent System** — Instead of one agent doing everything, you build specialized agents that collaborate. A research agent that gathers information, an analyst agent that evaluates it, a writer agent that produces the output. They pass work between each other. This is the cutting edge of what people are building with frameworks like CrewAI and AutoGen. More complex architecture but the individual pieces are all things you already know.

-------------------------------------------------------------------------------------------

### The Conceptual Map — How It All Connects

Here's the mental model for where AI is right now:
PERCEPTION          REASONING           ACTION
(understand input)  (think about it)    (do something)

Embeddings    →     LLMs          →     Agents
"what does        "what does           "go do it
this mean?"        this mean for        in the world"
                   my goal?"
Everything you've built fits somewhere in this map. The new projects are about combining all three layers into systems that can actually do things.

-------------------------------------------------------------------------------------------

### The 6 New Projects — The Pattern They Share

Here's what's interesting: your 6 new projects aren't 6 different things. They're variations on one architecture with different tools and domains:

[Retrieval Layer]  +  [Reasoning Layer]  +  [Action Layer]
      RAG                  LLM/Agent             Tools

ProjectRetrievalReasoningActions
Personal KBYour documentsClaudeIngest, categorize, answer
HP RPGHP lore chunksGame state agentUpdate state, generate narrative
Research AgentWeb search + scrapingPlanning loopRead, synthesize, report
Agentic RAGMulti-query searchEvaluate + re-searchStructured synthesis
Workflow AutomationCalendar/email/filesTask decomposerAPI calls
Multi-AgentDistributed retrievalAgent-to-agentParallel specialized work

The core new skill across all of them: making the system decide how to retrieve and act, rather than just doing one fixed retrieval and one fixed response.

### The 3 Key Patterns You'll Learn

1. **Agentic RAG** (used in: all 6 projects)
    - Instead of: query → search → answer
    - You do: query → plan searches → search → evaluate results → re-search if needed → synthesize

2. **State Management** (used in: RPG, Workflow, Multi-Agent)
    - Your ReAct agent was stateless — each call was fresh. These new projects need persistent state: what has the character learned? what tasks are in progress? what has the research agent already found?

3. **Tool Orchestration at Scale** (used in: Research, Workflow, Multi-Agent)
    - Your current agent has 5 simple tools. Real systems have dozens of tools, and the intelligence is in which tools to chain in what order, handling failures, and knowing when a tool's output is insufficient.

### What's Actually New (What You Haven't Seen Yet)

- **Persistent memory / state stores** — keeping context between sessions (Redis, SQLite, or even JSON files done well)
- **Multi-step planning** — breaking a goal into a dependency graph before executing, not just reacting
- **Self-evaluation loops** — the system checks its own output quality and decides whether to try again
- **Real API integrations** — Gmail, Google Calendar, file systems (not fake tools)
- **Agent-to-agent communication** — one agent calling another as a tool
- **Streaming responses** — returning output incrementally rather than waiting for completion


### Recommended Order

Based on what builds on what, I'd suggest:

**Agentic RAG** — natural evolution of HP RAG, teaches self-evaluation loops (no new infra needed)

**HP RPG** — adds state management on top of agentic RAG (builds directly on #1)

**Personal Knowledge Base** — same RAG pipeline, adds auto-ingestion agent (now you understand it deeply)

**Research Agent** — adds web scraping + multi-step planning to your existing agent

**Workflow Automation** — real API integrations, highest practical value

**Multi-Agent** — builds on everything, most complex architecture



-------------------------------------------------------------------------------------------