# Project 2: Sentiment Analyzer

What you built: A model that reads text (movie reviews, product feedback) and classifies it as positive or negative.

The model: You built two — logistic regression with TF-IDF features, and BERT (a pre-trained transformer). This was your first NLP project and your first encounter with transfer learning.

What made this project unique:

The input is text, which is messy. Numbers and images have fixed structure — text doesn't. The big challenge is turning words into numbers the model can use. You saw two approaches: TF-IDF (classical — just count how important each word is across documents) and BERT embeddings (deep learning — capture the actual meaning and context of words). "The movie was not good" and "The movie was bad" mean the same thing, and BERT understands that while TF-IDF just sees different word counts.

The big surprise: Logistic regression with TF-IDF performed competitively with BERT. A massive 110M parameter transformer barely edged out a simple model with bag-of-words features. This was one of the most important lessons across all your projects — complexity doesn't guarantee better results. For binary sentiment on straightforward reviews, word frequency patterns are often enough.

### Core lessons:

Text needs to be converted to numbers (vectorization) before any model can use it
TF-IDF: simple, fast, no context awareness
BERT: pre-trained on massive data, understands context and word relationships
Transfer learning — taking a model trained on one task and applying it to yours
Sometimes the simple approach wins, and that's fine

### How it connects:

BERT was your first transformer, which is the same architecture family as GPT-2 in the text generator. BERT reads and understands text (encoder), GPT-2 writes and generates text (decoder). Two sides of the same coin. And the embedding model we're using right now for RAG (MiniLM) is also a transformer — same family.