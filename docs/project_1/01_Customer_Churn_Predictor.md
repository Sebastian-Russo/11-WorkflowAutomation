# Project 1: Customer Churn Predictor

What you built: A model that takes customer data (age, tenure, monthly charges, contract type, etc.) and predicts whether they'll cancel their subscription.

The model: Classical ML — logistic regression and random forest. No neural networks, no deep learning. These models work directly on structured tabular data with hand-engineered features. You told the model exactly what to look at (tenure, charges, contract type), and it learned the mathematical relationship between those features and churn.

What made this project unique compared to MNIST: With MNIST the CNN figured out its own features from raw pixels. Here, you were the feature engineer. You decided which columns mattered, handled missing values, encoded categorical variables, scaled numerical ones. The model was simpler but the data preparation was heavier.

### Core lessons:

- Data preprocessing is most of the work in real ML projects — cleaning, encoding, scaling
- Feature engineering matters more than model complexity for tabular data
- Random forest vs logistic regression — ensemble methods (many decision trees voting together) vs a single linear boundary
- Evaluation metrics beyond accuracy: precision, recall, F1 score. With churn, catching the customers who will leave matters more than overall accuracy
- Train/test split to check if the model generalizes

### How it connects forward:

This was your baseline for understanding that not everything needs deep learning. When you later saw BERT barely beat logistic regression on sentiment, that lesson hit harder because you'd already seen how capable classical models are on the right problem.
