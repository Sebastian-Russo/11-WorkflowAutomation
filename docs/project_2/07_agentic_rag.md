## Agentic RAG

### What Agentic RAG Actually Is

Your HP RAG system was passive. It did exactly one thing every time:
User question → embed → search → top 5 chunks → stuff into prompt → answer
It never asked: Are these chunks actually good? Did I search the right way? Did I miss something?
Agentic RAG makes the system active. It treats retrieval as a problem to solve, not a step to execute.
User question
    ↓
[PLAN] How should I search for this?
    ↓
[SEARCH] Execute the searches
    ↓
[EVALUATE] Are these results sufficient to answer the question?
    ↓
[DECIDE] Good enough → answer / Not good enough → search differently
    ↓
[SYNTHESIZE] Generate answer with citations
That loop in the middle — evaluate → decide → maybe search again — is what makes it "agentic."

### The 3 Core Upgrades Over Your HP RAG

1. Query Decomposition
Instead of searching with the user's raw question, the agent first thinks about what sub-questions need to be answered.
"Compare how Dumbledore and Snape viewed Harry's role in defeating Voldemort"
→ becomes 3 separate searches:

"Dumbledore's plan for Harry and Voldemort"
"Snape's true loyalties and mission regarding Harry"
"Harry as the chosen one prophecy"

Each search gets better chunks than one big search ever would.
2. Retrieval Evaluation
After searching, the agent reads the retrieved chunks and scores them: Do these actually contain enough information to answer the sub-question? If the score is too low, it generates a different search query and tries again. This is the self-evaluation loop.
3. Synthesis with Reasoning
Instead of dumping chunks into a prompt and hoping, the agent explicitly tracks which chunks answered which sub-questions, then synthesizes a structured answer. You get better responses AND you know why.

### The Architecture

┌─────────────────────────────────────────────────────┐
│                  Agentic RAG System                  │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │  Query   │    │Retrieval │    │  Synthesis   │  │
│  │ Planner  │───▶│  Agent   │───▶│   Engine     │  │
│  └──────────┘    └──────────┘    └──────────────┘  │
│       │               │                             │
│  Decomposes      ┌────┴────┐                        │
│  question into   │Evaluator│ ← checks chunk quality │
│  sub-queries     └────┬────┘                        │
│                       │                             │
│              Good? ───┤─── Not good? → re-search   │
│                       ↓                             │
│              Collect all chunks                     │
└─────────────────────────────────────────────────────┘
Components you're building:

query_planner.py — takes a question, returns sub-queries
retrieval_agent.py — executes searches, runs eval loop
evaluator.py — scores chunk relevance, decides if re-search needed
synthesizer.py — builds final answer from collected evidence
app.py — Flask API (same as before)
config.py — settings

### What the Evaluator Actually Does
This is the novel piece. After retrieving chunks for a sub-query, the evaluator asks Claude:

"Given the question '{sub_query}', do these retrieved passages contain sufficient information to answer it? Rate 0-10 and explain what's missing if anything."

If score < threshold (say, 6), the retrieval agent generates a reformulated query and searches again. It does this up to N times (max iterations) before giving up and moving on.
This is exactly what a good researcher does — if your first search returns garbage, you don't just use it, you search differently.

### What's Reused from HP RAG

Almost everything at the bottom of the stack:

Your vector store (ChromaDB or whatever you used)
Your sentence transformer embeddings
Your hybrid search (semantic + keyword)
Your chunk storage

The agentic layer sits on top of this. You're not rebuilding retrieval — you're building a smarter controller for retrieval.

### Project Structure
7-AgenticRAG/
├── data/
│   └── (HP books, already processed or re-process)
├── vectorstore/
│   └── (persisted embeddings)
├── src/
│   ├── __init__.py
│   ├── config.py            # settings, thresholds, model names
│   ├── vector_store.py      # load/query your existing store (reused)
│   ├── query_planner.py     # decompose question → sub-queries
│   ├── evaluator.py         # score chunk relevance
│   ├── retrieval_agent.py   # search loop with re-query logic
│   ├── synthesizer.py       # build final answer
│   └── rag_pipeline.py      # orchestrates all components
├── app.py                   # Flask API
├── requirements.txt
├── .env
└── .gitignore

### Key Design Decisions to Understand

Why use Claude for decomposition AND evaluation?
Because query planning and relevance judgment are language tasks — they need semantic understanding, not just keyword matching. Claude is already in your stack from HP RAG's query expansion.
Why a max iterations limit?
Without it, a hard question could loop forever. In practice, 2-3 iterations is almost always enough. If it can't find good chunks by then, either the information isn't in the books or the question is unanswerable from the source.
Why track which chunks answered which sub-query?
Transparency and quality. The synthesizer can say "According to retrieved passages about Snape's loyalties..." instead of just asserting things. It also helps you debug when something goes wrong.

### Question about the project

Why use Claude for decomposition AND evaluation? Because query planning and relevance judgment are language tasks — they need semantic understanding, not just keyword matching. Claude is already in your stack from HP RAG's query expansion.

define  decomposition AND evaluation.
they need semantic understanding. what do you mean?

does this mean we're cheating a bit? like before with the harry potter text generator and claude helped form the queries better

1:19 AM
Good questions. Let me break both down clearly.

Decomposition
Taking a complex question and breaking it into simpler, focused sub-questions.

Input: "Compare how Dumbledore and Snape viewed Harry's role in defeating Voldemort"

Output:

"What was Dumbledore's plan for Harry regarding Voldemort?"
"What did Snape believe about Harry's purpose?"
"What does the prophecy say about the chosen one?"
That's it. Decomposition is just structured question-breaking. The reason you need a language model to do it is that it requires understanding what the question is really asking — recognizing that "compare" means you need both sides, that Dumbledore and Snape are the two subjects, that "role" means purpose/plan. You can't do that with regex or keyword splitting.

Evaluation
After you retrieve chunks for a sub-query, evaluation is asking: did the retrieval actually find what we needed?

You send Claude something like:

"Sub-question: What did Snape believe about Harry's purpose?
Retrieved passages: [chunk1, chunk2, chunk3]
Do these passages contain enough information to answer the sub-question? Score 0-10."

Claude reads the chunks and says "6/10 — the passages mention Snape's loyalty to Lily but don't explicitly address his beliefs about Harry's mission." That score triggers a re-search.

Semantic Understanding
"Semantic" means meaning, as opposed to form (exact words).

A keyword search for "Snape Harry purpose" matches documents that contain those words. It doesn't understand that "Snape's true mission" or "his vow to Dumbledore" or "protect the boy" all mean the same thing in context.

Semantic understanding means the system grasps what something means regardless of the exact words used. Embeddings give you this for retrieval. Claude gives you this for planning and evaluation — it understands that a chunk about "Snape's oath to protect the boy" is highly relevant to "what did Snape believe about Harry's purpose," even though none of those exact words overlap.

Are We Cheating?
Sort of — and it's worth being honest about.

Yes, you're using Claude (a powerful external model) to make your system smarter. Same as HP RAG used Claude to expand queries. The system isn't figuring this out from scratch — it's borrowing Claude's language understanding.

But here's why it's not really cheating: this is how production AI systems actually work. Almost nobody trains their own LLM for these reasoning steps. The skill being built is system design — knowing what tasks need language understanding, where to put the evaluation loops, how to structure the prompts, how to wire the components together. Claude is a tool in your toolkit, like numpy or Flask.

The alternative would be training a small classifier to score chunk relevance, which would take thousands of labeled examples and still perform worse. Using Claude for these language tasks is just the right tool for the job.

The honest framing: you're building the architecture and logic, Claude provides the language intelligence inside specific steps. That division of responsibility is the real skill here.


## Difference between Evaluator and Retrieval Agent

**Evaluator** — only has one job: look at chunks and score them
It takes a sub-query and some chunks, asks Claude "are these good enough?", and returns a score plus optionally a reformulated query. That's it. It doesn't know what happens before or after. It has no memory of previous attempts. It just judges what it's handed.

**Retrieval agent** — runs the loop and makes decisions based on the evaluator's output
It's the one that actually does something with the evaluation. It decides whether to accept the chunks, whether to retry, which reformulated query to use, how many attempts have been made, and what the best attempt was if we run out of retries. It's the manager.

**Analogy**
Think of a job interview process. The evaluator is the hiring rubric — a scorecard that says "did the candidate meet the bar?" The retrieval agent is the recruiter — they run the interview, read the scorecard, and decide "do we move forward or bring in another candidate?"
The rubric doesn't schedule interviews. The recruiter doesn't define what a good candidate looks like. Separate responsibilities.

In code terms: the evaluator is a pure function that takes inputs and returns a judgment. The retrieval agent is a stateful loop that tracks attempts, calls the evaluator, and acts on the result.


## Cheating?

before we move on. I just feel a little bit cheating still. like the claude part seemed to formulate really good query question with names like cho chang that I didn't give it. did it get that from claudes extensive knowledge or from looping? I think looping wasn't working on that question yet though

You're right to question this — and it's a great observation.

That was Claude's training knowledge, not the retrieval loop. When the query planner decomposed "why didn't Harry and Hermione date" into sub-queries, it already knew Cho Chang and Ginny Weasley are Harry's love interests. That came from Claude's training data — it has read the Harry Potter books as part of its training.

So yes, there is a layer of "cheating" happening in the query planner specifically. Claude isn't going in blind and discovering those names from the vector store — it already knows the answer before it even searches.

This is actually a known limitation of agentic RAG in practice. It's called the "knowledgeable planner problem." The planner uses world knowledge to generate better searches, which produces better results, but the quality of your sub-queries depends on how much the LLM already knows about your domain.

You can see this clearly if you imagine swapping HP for a private internal document set — company emails, your own notes. Claude would have no prior knowledge, sub-queries would be much more generic, and retrieval quality would drop.

The loop was genuinely working though — the reformulation steps used the retrieved chunks to judge quality, not Claude's prior knowledge. The evaluator reads actual chunks and scores them. That part is honest.

So the honest breakdown is:

Query planning = partly Claude's prior knowledge
Evaluation and re-search = genuinely agentic, based on retrieved evidence
Synthesis = Claude's reasoning over retrieved chunks only
Not pure cheating, but not pure RAG either. This is just the reality of building with powerful foundation models.