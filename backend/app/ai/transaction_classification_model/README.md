# Fine-Tuned DistilBERT Transaction Categorizer

## 📍 Location
```
backend/app/ai/transaction_classification_model/
```

## 🎯 Purpose
This directory contains Jae's fine-tuned DistilBERT model for transaction categorization.
The model classifies merchant names into one of 11 categories.

## ⚠️ IMPORTANT - Model Files Required

**This folder is GITIGNORED** because model files are too large (~250MB).

Jae (or whoever has the trained model) must manually add the model files here.

---

## 📁 Required Files

Place these files in this directory:

```
backend/app/ai/transaction_classification_model/
├── config.json              ← Model configuration
├── pytorch_model.bin        ← Model weights (OR model.safetensors)
├── tokenizer_config.json    ← Tokenizer settings
├── vocab.txt                ← Vocabulary file
├── special_tokens_map.json  ← Special tokens (optional)
└── README.md                ← This file (committed to git)
```

### File Details

| File | Required | Description |
|------|----------|-------------|
| `config.json` | ✅ Yes | Model architecture config (num_labels, id2label, etc.) |
| `pytorch_model.bin` | ✅ Yes* | PyTorch model weights (~250MB) |
| `model.safetensors` | ✅ Yes* | Alternative format for weights |
| `tokenizer_config.json` | ✅ Yes | Tokenizer configuration |
| `vocab.txt` | ✅ Yes | BERT vocabulary (30522 tokens) |
| `special_tokens_map.json` | Optional | Maps special tokens |

*Either `pytorch_model.bin` OR `model.safetensors` is required (not both).

---

## 🏷️ Expected Categories (11 total)

The model's `config.json` should have `id2label` mapping to these categories:

```json
{
  "id2label": {
    "0": "Food & Dining",
    "1": "Transportation",
    "2": "Shopping & Retail",
    "3": "Entertainment & Recreation",
    "4": "Healthcare & Medical",
    "5": "Utilities & Services",
    "6": "Financial Services",
    "7": "Income",
    "8": "Government & Legal",
    "9": "Charity & Donations",
    "10": "Unknown"
  }
}
```

**⚠️ These MUST match the database categories in:**
- `backend/app/models/category.py` → `DEFAULT_CATEGORIES`
- `backend/app/ai/constants.py` → `SYSTEM_CATEGORIES`

---

## 🔧 How It's Used

The model is loaded by `backend/app/ai/inference.py`:

```python
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

class TransactionClassifier:
    def __init__(self, model_dir="transaction_classification_model"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, model_dir)

        self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
```

---

## ✅ Verification

After adding model files, verify with:

```bash
cd backend
python tools/download_model.py --check
```

Expected output:
```
✅ Fine-Tuned Categorizer
   Path: .../backend/app/ai/transaction_classification_model
```

Or test directly:
```bash
cd backend
python -c "from app.ai.inference import TransactionClassifier; c = TransactionClassifier(); print(c.predict('Starbucks'))"
```

---

## 🐳 Docker Notes

- The Dockerfile does NOT include this model (gitignored)
- In development: Model is mounted via `./backend:/app` volume
- For production: Add model files before `docker build`

---

## 🔧 Training Notes (For Jae)

If retraining the model, ensure:

1. **Categories match** the 11 system categories listed above
2. **Save with:**
   ```python
   model.save_pretrained("transaction_classification_model")
   tokenizer.save_pretrained("transaction_classification_model")
   ```
3. **Test locally** before sharing with team
4. **Share via:** Google Drive, OneDrive, or direct transfer (not git)
