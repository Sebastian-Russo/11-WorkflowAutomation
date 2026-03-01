# Project 3: Stock Price Forecaster

What you built: A model that takes historical stock prices and technical indicators and predicts tomorrow's closing price.

**The data type:** Time series — sequential numerical data where order and time matter. You had daily price data (open, high, low, close, volume) plus engineered features like RSI, MACD, and Bollinger Bands. Unlike tabular data in churn where each row is independent, here every row depends on the rows before it. Shuffling the data would destroy it.

**The model:** Three approaches — naive baseline (tomorrow = today), linear regression, and LSTM. The naive baseline is deceptively simple: just predict that tomorrow's price equals today's price. Linear regression treated it like a tabular problem, ignoring the sequential nature. LSTM (Long Short-Term Memory) is a recurrent neural network designed specifically for sequences — it processes data step by step and maintains a memory of what it's seen.

**The big surprise:** The naive baseline was incredibly hard to beat. Your LSTM with 40 engineered features and thousands of parameters performed comparably to just saying "tomorrow equals today." Stock prices are close to a random walk — past patterns don't reliably predict future movements. This was the second major lesson about complexity vs simplicity, after sentiment analysis.

### Core lessons:

Time series data requires chronological train/test splits — no random shuffling, no data leakage from the future

Feature engineering for sequences: rolling averages, momentum indicators, volatility bands

RNNs/LSTMs process data sequentially and maintain hidden state (memory)

Simple baselines should always be your first benchmark — if you can't beat naive, your complex model isn't learning anything useful

**Some problems are fundamentally hard regardless of model sophistication**
Overfitting is dangerous when patterns in training data don't generalize

**Data types across projects so far:**

ProjectInput Data TypeOutput Type0 - MNISTImage (28x28 pixel grid)Multi-class (10 digits)1 - ChurnTabular (structured rows/columns)Binary (churn yes/no)2 - SentimentText (variable length strings)Binary (positive/negative)3 - StockTime series (sequential numerical)Regression (continuous price)4 - Text GenText (sequential characters/tokens)Generative (next token prediction)5 - RAGText documents (unstructured)Generative (natural language answer)

**How it connects:** The LSTM here and the character RNN in the text generator are the same architecture family — both recurrent, both process sequences, both maintain memory. The difference is the task: regression (predict a number) vs generation (predict the next character). You saw LSTMs struggle in both cases — stock prediction couldn't beat naive, and the character RNN produced gibberish. Transformers (BERT, GPT-2) ended up being the better architecture for text.