# RAG (Project 5)

breaks that pattern. You're not training a model at all. You're wiring together pre-trained components — an embedding model to vectorize text, a vector database to store and search, and an LLM to generate answers. The skill is in the architecture and pipeline design, not in training. How you chunk documents, which embedding model you choose, how many chunks you retrieve, how you format the prompt to the LLM — those decisions determine quality, not gradient descent.

--------------------------------------------------------------------------------

## Types of RAG Systems

**Basic RAG** — what most people build first. You chunk documents, embed them, store in a vector database, retrieve relevant chunks on query, pass to LLM for answer. Simple pipeline: question → search → answer. This is what we'll build.

**Conversational RAG** — same as basic but with chat history. It remembers previous questions so you can ask follow-ups like "what about the second book?" without repeating context. Adds a memory layer.

**Multi-modal RAG** — handles not just text but images, tables, PDFs with charts. Useful for technical documents where a diagram is the answer, not a paragraph.

**Agentic RAG** — the RAG system decides how to search. Instead of one simple retrieval, it might rephrase your question, search multiple times, filter results, or decide it needs a different source entirely. This overlaps with our agent project later.

**Hybrid RAG** — combines keyword search (traditional, like Ctrl+F) with semantic search (vector similarity, meaning-based). Sometimes the exact word match matters more than meaning.

For our project, we'll build basic RAG with room to extend to conversational if you want.

## Common Types of Data People Load In

### Personal/private use:

Books and textbooks you own (your Harry Potter idea)
Class notes, lecture PDFs
Personal journals or writing
Tax documents, medical records, legal contracts

### Professional:

Company documentation, SOPs, internal wikis
Codebase documentation
Slack/email archives
Meeting transcripts

### Technical:

API docs, technical manuals
Research papers
Programming language docs

### Creative:

World-building docs for D&D campaigns or fiction writing
Recipe collections
Travel journals/guides

The whole point of RAG is it works with whatever you throw at it — PDFs, text files, markdown, even web pages. The system doesn't care about the content, it just chunks it, embeds it, and retrieves what's relevant.

What sounds useful to you? You mentioned Harry Potter before — we could also do something you'd actually keep using after the project, like a personal knowledge base with documents you already have.

--------------------------------------------------------------------------------

## What RAG Actually Is

RAG is not training a model. There's no training at all. Here's what's happening:

**Phase 1:** Load & Chunk (done) — Take your Harry Potter PDFs, extract the text, break it into searchable pieces.
**Phase 2:** Embed (done) — Convert every chunk into a vector so we can search by meaning, not just keywords.
**Phase 3:** Retrieve — When you ask a question, embed your question into a vector, find the most similar chunks from your documents. This is just math — cosine similarity between your question vector and all 12,921 chunk vectors.
**Phase 4:** Generate — Take those retrieved chunks + your question, pass them to an LLM, and say "answer this question using only this context." The LLM is just the engine that reads the passages and formulates a response.

**Why We Need an LLM**

You're right that Claude already knows a lot about Harry Potter from its training data. So for this specific dataset, yeah, you could just ask Claude directly.
But here's what makes RAG different and why it matters:
The LLM doesn't use its own knowledge. We explicitly tell it: "Answer ONLY based on the provided context. If the answer isn't in the context, say you don't know." It becomes a reading comprehension engine, not a knowledge engine. It reads the specific passages we retrieved and synthesizes an answer from them.

**Why this matters:**

Think about your personal documents idea. If you loaded your tax returns, medical records, journal entries, work notes — Claude has zero knowledge of any of that. There's nothing on the internet about your personal stuff. Without RAG, the LLM is useless for those questions. With RAG, it can answer "what did I spend on rent in 2024?" because the retrieval step found the relevant chunk from your tax docs, and the LLM just reads it and answers.

**Harry Potter is training wheels.** The architecture is identical whether the documents are Harry Potter books or your private financial records. You're building the retrieval pipeline — that's the skill. The LLM is just a plug-in component at the end.

**The analogy:** Think of it like a librarian. The retrieval system is the librarian who knows exactly which pages in which books are relevant to your question. The LLM is the person who reads those pages and gives you a summary. The librarian is what we're building. The reader (Claude/OpenAI) is just a tool we plug in.

**We're using Claude as an engine.**
Specifically we're using the API to call it programmatically, with a system prompt that restricts it to only use the retrieved context. We're not using Claude's built-in knowledge at all.

## The Flow

Here's exactly what happens when you ask "What are the three Deathly Hallows?":

**Step 1:** Embed your question. Your question gets converted into a 384-dimensional vector using the same MiniLM model we used on the chunks. Now your question is a list of 384 numbers, just like every chunk.
**Step 2:** Compare against all 12,921 chunks. We calculate cosine similarity between your question vector and every single chunk vector. This is just math — dot product divided by magnitudes. It gives a score from 0 to 1 for each chunk. Higher means more semantically similar to your question.
**Step 3:** Grab the top 5. Sort all 12,921 scores, take the 5 highest. For the Deathly Hallows question, the top chunk scored 0.4917 — it happened to be the passage where Xenophilius draws the symbol and names all three objects. The retrieval found the right passage out of nearly 13,000 chunks.
**Step 4:** Build a prompt. We take those 5 passages, format them into a prompt that says "here's context from Harry Potter, answer this question using ONLY this context," and send it to Claude via the API.
**Step 5:** Claude reads and answers. Claude doesn't use its own Harry Potter knowledge. It reads those 5 specific passages like a reading comprehension test and formulates an answer.


# Improvements

There are a few approaches we can stack together. Let me explain each one, then we'll implement them.

**1. Hybrid Search (Keyword + Semantic)** — Right now we only do semantic search (meaning-based). But sometimes you want exact word matching. If you ask "Who is Dobby?", semantic search might find chunks about house-elves in general. Keyword search would find every chunk that literally contains "Dobby." Combining both gives better results.

**2. Re-ranking** — Right now we grab the top 10 closest chunks and send all of them to Claude. But some of those chunks might be noise. Re-ranking takes the initial results, scores them more carefully against the question, and keeps only the best ones. Think of it as a second pass — the first search is fast and broad, the re-ranker is slower but more precise.

**3. Query Expansion** — When you asked "how old is Harry in the first book" it failed because the books never phrase it that way. Query expansion takes your question and generates alternative phrasings: "Harry's age", "Harry's eleventh birthday", "Harry turned eleven." Then it searches for all of them and merges the results.
