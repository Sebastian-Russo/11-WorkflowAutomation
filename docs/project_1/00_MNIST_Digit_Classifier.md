# Project 0: MNIST Digit Classifier

## What you built: A CNN that looks at handwritten digit images (28x28 pixels) and classifies them as 0-9.

## The model: Convolutional Neural Network. This was your first deep learning model. The key idea is that CNNs don't look at individual pixels — they slide small filters across the image to detect features. First layer finds edges and lines, second layer combines those into shapes (curves, corners), final layers recognize the full digit. The model learns what to look for on its own.

## What made this project unique: It's pure computer vision — the input is a grid of pixel values, not tabular data or text. The spatial relationships matter (a pixel's neighbors tell you more than the pixel alone). This is why CNNs exist — a regular neural network would treat every pixel independently and miss the spatial patterns.

## Core lessons:

- Neural networks can learn features without you engineering them
- More layers = more abstract feature detection (edges → shapes → digits)
- Softmax output gives you probabilities across all 10 classes, not just a yes/no
- This was your introduction to training loops, loss functions, and accuracy metrics

## How it connects to everything after: This was the foundation. Every project after used the same training pattern — feed data in, calculate loss, adjust weights, repeat. The difference was always the architecture and the data type.
