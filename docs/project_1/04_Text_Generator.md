# What you built:

A model that takes a text prompt and generates new fantasy-style text, trained on public domain fairy tale books.

**The data type:** Text (sequential tokens). Similar to sentiment analysis in that the input is text, but the task is completely different. Sentiment reads text and outputs a label. Text generation reads text and outputs more text — one token at a time, each predicted token becoming input for the next prediction. This is autoregressive generation.

**The models:** Character RNN (LSTM-based, built from scratch) and fine-tuned GPT-2 (pre-trained transformer). The character RNN learned letter by letter — given a sequence of characters, predict the next character. GPT-2 works at the token level (words/subwords) and already knows English from pre-training on billions of words. You just fine-tuned it to learn the fantasy style.

**The big lesson:** Training from scratch vs fine-tuning is night and day. The character RNN produced "liberted" and "besuped." GPT-2 produced coherent sentences with real words and grammar — still repetitive and logically weak, but leagues ahead. This hammered home why transfer learning dominates modern AI. Nobody trains from scratch anymore unless they're OpenAI or Anthropic with massive compute budgets.

**Core lessons:**

Generative models predict one step at a time, feeding output back as input

Temperature controls the randomness/creativity trade-off

Repetition is the main failure mode of small language models — solved with repetition penalty, no_repeat_ngram, top-k/top-p sampling

Fine-tuning a pre-trained model beats training from scratch on limited data and compute

124M parameters is tiny by modern standards — explains the quality ceiling

Attention masks, tokenization, and decoding strategies matter for generation quality
