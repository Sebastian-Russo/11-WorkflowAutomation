# Harry Potter RPG Game

Before we touch any code, let me lay out what's new in this project compared to what you've already built — because this one introduces a genuinely new concept: persistent state.
Every project so far has been stateless. You send a question, you get an answer, the system forgets everything. Each request starts fresh.
An RPG can't work that way. The game needs to remember:

- What year you're in at Hogwarts
- What spells you've learned
- What house you're in
- What happened in previous scenes
- Who you've met, what items you have


## Let me lay out the full architecture before we write a single file.

### What's New in This Project
State management — the game remembers who you are and what happened. Every action reads the current state, updates it, and saves it back to disk.
Prompt engineering at scale — the LLM needs to know your character, the current scene, retrieved lore, and your action all at once. Structuring that prompt correctly is what makes the game feel coherent instead of random.
A game loop instead of a pipeline — Agentic RAG was linear: plan → retrieve → synthesize. The RPG is a loop: action → retrieve lore → update state → generate narrative → repeat forever.

### The Components
player action (browser)
        ↓
   game_engine.py        ← orchestrator (like rag_pipeline.py)
    ↙        ↘
state_manager.py    lore_retriever.py
(read/write JSON)   (reuses vector store)
        ↘        ↙
    prompt_builder.py    ← assembles the full LLM prompt
            ↓
        Claude (Sonnet)
            ↓
    narrative + state update
            ↓
      back to browser

The State Shape
This is what gets saved to disk for each player:
json{
  "player_name": "Sebastian",
  "house": "Gryffindor",
  "year": 1,
  "spells_learned": ["Lumos", "Wingardium Leviosa"],
  "inventory": ["wand", "owl", "Hogwarts letter"],
  "relationships": {"Harry Potter": "friendly", "Draco Malfoy": "rival"},
  "current_location": "Diagon Alley",
  "scene_history": ["You arrived at Diagon Alley...", "You entered Ollivanders..."],
  "health": 100
}
```

Every request reads this, passes it to the prompt, and writes back any changes Claude returns.

---

## Project Structure
```
8-HPRPG/
├── src/
│   ├── config.py
│   ├── state_manager.py     ← read/write player JSON
│   ├── lore_retriever.py    ← thin wrapper around vector store
│   ├── prompt_builder.py    ← assembles the full context prompt
│   ├── game_engine.py       ← orchestrator
│   └── __init__.py
├── static/
│   └── index.html           ← the web UI
├── saves/                   ← player JSON files live here
├── vectorstore/             ← symlink or copy from project 7
├── data/                    ← HP PDFs
├── app.py
├── requirements.txt
└── .gitignore


## Copyright Concerns

Totally valid thing to pause on.
You're right on the copyright point — you can't sell a game built on HP books. But the RPG project isn't really about Harry Potter. HP is just familiar source material that makes it easy to test and understand the system. The skills you're building are:

- Persistent state management
- Combining RAG with generative storytelling
- Prompt engineering for interactive narrative
- A game loop architecture

Those skills transfer directly to things you could actually ship.
Real world versions of this exact system:
**A Dungeons & Dragons campaign assistant** — DMs upload their own homebrew lore, the system retrieves relevant world details during play, tracks character state. Entirely original content, fully sellable.
**A corporate training simulator** — a company uploads their internal docs, policies, product manuals. Employees interact with realistic scenarios grounded in actual company knowledge. Companies pay serious money for this.
**A choose your own adventure tool** — someone uploads their own original story bible and the system generates interactive fiction from it. You'd be selling the platform, not the content.
**A historical education game** — public domain source material (Civil War documents, ancient texts, Shakespeare). Grounded in real historical sources, completely legal.

The pattern is always the same:

Private or original document corpus + RAG for grounding + state management + generative narrative = interactive experience grounded in real knowledge.

HP is just the training wheels. The architecture is the product.
