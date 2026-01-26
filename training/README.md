# Transaction Categorization Training

This directory contains the research, data exploration, and fine-tuning logic used to create the transaction classification model.

The goal of this module is to produce a model artifact that is lightweight enough for our backend API but accurate enough to handle messy transaction descriptions.

## Contents

- **`transaction_classifier.ipynb`**: The main notebook containing the end-to-end pipeline (Data loading -> Cleaning -> Training -> Export).

## Model Details

- **Base Architecture:** `distilbert-base-uncased`
- **Why this model?** DistilBERT was chosen because it retains ~97% of BERT's performance while being 40% smaller and 60% faster. This is critical for keeping latency low in the backend API.
- **Dataset:** [Transaction Categorization](https://huggingface.co/datasets/mitulshah/transaction-categorization) (HuggingFace).

## The Pipeline

The notebook performs the following steps:

1.  **Data Ingestion**: Pulls raw transaction data.
2.  **Preprocessing & Balancing**:
    - The dataset is balanced (undersampling) to prevent the model from biasing toward common categories.
    - Text cleaning via Regex to remove noise (transaction IDs, dates, special chars).
3.  **Tokenization**: Inputs are padded/truncated to a max length of **42 tokens** (sufficient for short bank descriptors).
4.  **Fine-Tuning**: The model is trained for 3 epochs using the HuggingFace `Trainer` API.
