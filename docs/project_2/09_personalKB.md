# Personal Knowledge Base

Is this really going to be able to be hooked up with my financial webapps?

Not directly, no — and it's worth being honest about what this system actually is.

What you're building is a read-only knowledge base from public web content. You paste URLs, it scrapes and stores the text. That's it. It has no connection to your actual financial accounts, transactions, or live data.

To hook into real financial apps you'd need one of two things:

Official APIs — Plaid, for example, is a service that connects to thousands of banks and brokerages. You authenticate through them and get access to your actual transaction data, balances, holdings. Companies like Mint, YNAB, and Robinhood use Plaid under the hood. This is real engineering work and requires account approval, OAuth flows, and handling sensitive financial data responsibly.

Exported data — most financial apps let you download your data as CSV or PDF. You could drop those files into this knowledge base and query them. Not live, but real data.

**What this project actually teaches is the ingestion pipeline pattern** — scrape or import a document, chunk it, tag it, store it, query it. That pattern is identical whether the source is a URL, a CSV export from your bank, or a Plaid API response. The architecture transfers directly.

So no, not plug-and-play with your financial apps. But the skill you're building is exactly what you'd use to build that connection once you have the data source.

## Flow Chart

![Flow Chart](flow_chart.png)

Start at the top and follow a URL all the way through, then a question all the way through.

### When you paste a URL and hit Save

The browser sends a POST to **/ingest** with the URL. Flask receives it in **app.py** and hands it to **IngestionPipeline.ingest_url()**.
The ingestion pipeline calls **scraper.py** first. Trafilatura fetches the raw HTML from the internet, strips everything that isn't article content — ads, navigation, footers — and returns clean text plus a title. If the page is paywalled or blocks scrapers, it returns failure here and the pipeline stops.

If scraping succeeded, the text goes to **tagger.py**. It sends the first 2000 characters to Claude Haiku with a simple prompt: "what topics is this about?" Haiku returns a JSON list like ["investing", "index-funds", "passive-investing"]. Cheap and fast because it's just classification.

Now **vector_store.py** takes the clean text, title, tags, and URL. It chunks the text into 800-character overlapping pieces, embeds each chunk using the sentence transformer model, and stores everything in ChromaDB. Each chunk gets metadata attached — the source URL, title, tags as a comma-separated string, and today's date. The vector store returns a count of how many chunks were stored.

The result goes back to the browser: "Saved 'Why Index Funds Beat Active Management' — 12 chunks, tags: investing, index-funds, personal-finance."
The sidebar refreshes by calling **/documents**, which reads all unique URLs from ChromaDB metadata and returns them as a list.

### When you type a question and hit Ask

The browser sends a POST to **/query** with the question and an optional tag filter. Flask hands it to **Retriever.query()**.
The retriever embeds your question using the same sentence transformer model — this is critical, both the stored chunks and the query must use the same model or the similarity math doesn't work. It sends that embedding to ChromaDB, which finds the 5 stored chunks whose embeddings are numerically closest to the question's embedding. If you typed a tag filter, ChromaDB adds a **WHERE tags CONTAINS "investing"** condition before searching.
The returned chunks each carry their source metadata — title, URL, tags, similarity score. The retriever formats them into an evidence block: each chunk prefixed with its source title and URL.
That evidence block plus your original question goes to Claude Sonnet in a tightly constrained prompt: "answer using ONLY the retrieved content, mention your sources naturally." Sonnet synthesizes a coherent answer grounded in what you actually saved, not its training knowledge.
The response comes back with three things — the answer text, a deduplicated list of source documents, and a count of how many chunks were used. The browser renders the answer, shows clickable source cards below it, and makes each tag clickable so you can instantly filter by topic.

### What the two pipelines never share

Ingestion writes to ChromaDB. Retrieval reads from ChromaDB. They never call each other. The vector store is the only shared component — it's the dividing line between the two halves of the system. This matters because in a real product you might run ingestion on a schedule in the background while retrieval happens in real time for users. Keeping them separate means you can scale or modify either side independently.

### ChromaDB is a database purpose-built for storing and searching embeddings.

#### The problem it solves
A regular database like MySQL stores rows of text and lets you search by exact match or keyword. That doesn't work for AI — you need to search by meaning, which means searching by embedding vectors (lists of numbers). A regular database has no concept of "find me the numbers most similar to these numbers."
ChromaDB is designed specifically for that problem.

#### What it actually stores
For each chunk you give it, ChromaDB stores three things together:

The raw text ("Index funds typically outperform active managers over 20 years...")
The embedding vector ([0.231, -0.847, 0.103, ... 384 numbers])
Metadata ({"url": "...", "tags": "investing", "date": "2026-02-28"})
For each chunk you give it, ChromaDB stores three things together:

The raw text ("Index funds typically outperform active managers over 20 years...")
The embedding vector ([0.231, -0.847, 0.103, ... 384 numbers])
Metadata ({"url": "...", "tags": "investing", "date": "2026-02-28"})

Those three things are always linked — when you get a chunk back, you get all three.

#### How similarity search works
When you query with "what did I read about passive investing", ChromaDB converts that to an embedding and then does math across every stored embedding to find which ones are closest. This is called nearest neighbor search. The chunks whose vectors are closest to your query vector come back as results.
Think of embeddings as coordinates in space. Similar meanings cluster near each other. ChromaDB's job is to efficiently find the nearest coordinates to your query.

#### Why persistent client
You'll notice in the code we always use chromadb.PersistentClient(path="vectorstore"). This means ChromaDB saves everything to disk in that folder. Every time you restart the server, the embeddings are already there — you never recompute them. Without persistence you'd lose everything on restart.

#### What ChromaDB is not
It's not a general purpose database. You wouldn't store user accounts or transaction records in it. It's a specialist tool — extremely good at one thing, not designed for anything else. In production systems ChromaDB is often paired with a regular database: PostgreSQL for structured data, ChromaDB for embeddings.

