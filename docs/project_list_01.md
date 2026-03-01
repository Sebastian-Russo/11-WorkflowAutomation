The Full Project List

-------------------------------------------------------------------------------------------

## Project                   Model Type                          Learning Type
0 MNIST Digit Classifier     CNN (Neural Network)                Deep Learning
1 Customer Churn Predictor   Logistic Regression, Random Forest  Classical ML
2 Sentiment Analyzer         Logistic Regression + BERT          Classical ML + Deep Learning
3 Stock Price Forecaster     Linear Regression, LSTM             Classical ML + Deep Learning
4 Text Generator             Character RNN, GPT-2                Deep Learning
5 RAG Q&A System             Embeddings + LLM                    Deep Learning + Retrieval
6 Agent System               LLM + Tools                         Deep Learning + Planning

-------------------------------------------------------------------------------------------

## Data types across projects so far:

Project                     Input Data                      Output Type
0 - MNISTImage              (28x28 pixel grid)              Multi-class (10 digits)
1 - ChurnTabular            (structured rows/columns)       Binary (churn yes/no)
2 - SentimentText           (variable length strings)       Binary (positive/negative)
3 - StockTime series        (sequential numerical)          Regression (continuous price)
4 - Text GenText            (sequential characters/tokens)  Generative (next token prediction)
5 - RAGText documents       (unstructured)                  Generative (natural language answer)
6 - Agent                   TBD                             ReAct, LangChain Agents, AutoGPT, CrewAI, function-calling LLMs

-------------------------------------------------------------------------------------------

## Classical ML vs Deep Learning

Classical ML is what you used in the churn predictor — logistic regression, random forests, decision trees. You hand-engineer the features (age, tenure, monthly charges), feed them in, and the model learns relatively simple mathematical relationships between those features and the output. These models have thousands to maybe millions of parameters. They're fast, interpretable, and often good enough. Your churn predictor and the logistic regression sentiment model are both classical ML.
Deep learning is when you use neural networks with multiple layers — that's the "deep" part, just referring to depth of layers. The key difference is the model learns its own features instead of you engineering them. With MNIST, you didn't tell the CNN "look for curves and straight lines to identify digits" — it figured that out itself through the convolutional layers. Same with LSTM for stock forecasting and the character RNN. These models have millions to billions of parameters and need way more data and compute.
The line between them isn't always clean. Your sentiment project showed this perfectly — logistic regression (classical) performed competitively with BERT (deep learning). More complexity doesn't always mean better results.


-------------------------------------------------------------------------------------------

## Why Some Feel More "AI" Than Others

This comes down to what the model does:
Discriminative models take an input and classify it or predict a value. MNIST looks at pixels and says "that's a 7." Churn predictor looks at customer data and says "they'll leave." Sentiment analyzer reads text and says "positive." These feel less "AI" because they're doing pattern matching — sophisticated pattern matching, but still just mapping input to a label.
Generative models create new content that didn't exist before. The text generator takes "Once upon a time" and writes a story. This feels more "AI" because it's producing something novel. GPT-2, DALL-E, Claude — these are all generative.
The progression you experienced:

MNIST: "Is this a 3 or a 7?" → Classification
Churn: "Will they leave?" → Prediction
Sentiment: "Positive or negative?" → Classification
Stock: "What's tomorrow's price?" → Regression (prediction)
Text Generator: "Write me a story" → Generation
RAG: "Answer my question using these documents" → Retrieval + Generation
Agent: "Go accomplish this task" → Planning + Action

Each step up the list feels progressively more "intelligent" because the task itself is more open-ended.

-------------------------------------------------------------------------------------------
## The Key Model Architectures You've Touched

CNNs (Convolutional Neural Networks) — MNIST. Designed for spatial data like images. Slides filters across the image to detect patterns (edges, shapes, textures). Great for anything grid-structured.

RNNs/LSTMs (Recurrent Neural Networks) — Stock forecaster, character RNN. Designed for sequential data where order matters. Processes one step at a time and maintains a "memory" of previous steps. The LSTM variant solves the problem of forgetting long-ago information. You saw the limitation though — the character RNN couldn't maintain coherence over long sequences.

Transformers — BERT (sentiment), GPT-2 (text generator). This is the architecture that changed everything. Instead of processing sequentially like RNNs, transformers use "attention" — they can look at the entire input at once and learn which parts are relevant to which other parts. BERT uses transformers for understanding text (reading). GPT-2 uses them for generating text (writing). Every major AI model today (Claude, GPT-4, Gemini) is a transformer.

-------------------------------------------------------------------------------------------
## Supervised vs Unsupervised vs Self-Supervised

Supervised — you give the model labeled examples. "Here's customer data, here's whether they churned." MNIST, churn, sentiment were all supervised.

Unsupervised — no labels, the model finds patterns on its own. Clustering, dimensionality reduction. We haven't done a pure unsupervised project.

Self-supervised — this is the clever one. GPT-2's pre-training doesn't use human labels. Instead, it takes text and predicts the next word — the label is literally the next word in the sequence, which you get for free from any text. This is how models can train on the entire internet without humans labeling anything. BERT does something similar but masks random words and predicts them instead.

-------------------------------------------------------------------------------------------

## What Makes RAG Different

RAG is interesting because it's not really training a model at all. Instead you're combining:

An embedding model — converts text chunks into vectors (numbers that capture meaning)
A vector database — stores those vectors so you can search by similarity
An LLM — takes the retrieved chunks + your question and generates an answer

When you ask "What spell did Harry use against Voldemort?", it doesn't generate from memory like GPT-2 does. It searches your documents, finds relevant passages, and hands those to the LLM to synthesize an answer. This is why it can work with private documents — the knowledge is in your files, not baked into model weights.

-------------------------------------------------------------------------------------------

## Concepts Worth Going Deeper On Later

A few things to be aware of that connect to everything you've done:

Overfitting vs underfitting — you've seen this across projects. The LSTM stock model overfit to training data and failed on test data. The character RNN memorized patterns but couldn't generalize. This tension shows up everywhere.

Transfer learning — using a pre-trained model and adapting it. You did this with BERT (sentiment) and GPT-2 (text generator). This is the most important practical technique in modern AI — almost nobody trains from scratch anymore.

Embeddings — turning things (words, sentences, images) into vectors. This will be central to RAG. The idea that "king" and "queen" are closer together in vector space than "king" and "banana" is what makes semantic search work.

Attention mechanism — the core innovation of transformers. Understanding this deeply will connect BERT, GPT-2, RAG, and agents all together.

-------------------------------------------------------------------------------------------

## How it connects:

The LSTM here and the character RNN in the text generator are the same architecture family — both recurrent, both process sequences, both maintain memory. The difference is the task: regression (predict a number) vs generation (predict the next character). You saw LSTMs struggle in both cases — stock prediction couldn't beat naive, and the character RNN produced gibberish. Transformers (BERT, GPT-2) ended up being the better architecture for text.

