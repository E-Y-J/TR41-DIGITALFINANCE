# AI Architecture - Multi-Model Design

## Digital Finance Tracker - Sprint 2/3 AI Implementation

This document outlines the multi-model AI architecture based on team discussions
and PM requirements.

---

## Table of Contents

1. [Multi-Model Overview](#multi-model-overview)
2. [Model Assignments](#model-assignments)
3. [NLP Requirements](#nlp-requirements)
4. [Integration Flow](#integration-flow)
5. [Implementation Plan](#implementation-plan)
6. [Server Resources](#server-resources)
7. [Recommendations](#recommendations)

---

## Multi-Model Overview

We use a **multi-model agent architecture** with specialized models for different tasks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-MODEL AI ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────────────────────┐   │
│  │   USER MESSAGE      │         │  MODEL ROUTER                       │   │
│  │ "Show my spending   │────────▶│  Determines which model to use      │   │
│  │  on food last week" │         │  based on intent type               │   │
│  └─────────────────────┘         └───────────────┬─────────────────────┘   │
│                                                  │                         │
│                    ┌─────────────────────────────┼─────────────────────┐   │
│                    │                             │                     │   │
│                    ▼                             ▼                     ▼   │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌────────────┐ │
│  │  SENTENCE TRANSFORMER   │  │     DISTILBERT          │  │  GEMINI    │ │
│  │  (MiniLM-L6)            │  │  (Fine-tuned by Jae)    │  │  (Cloud)   │ │
│  ├─────────────────────────┤  ├─────────────────────────┤  ├────────────┤ │
│  │ Purpose:                │  │ Purpose:                │  │ Purpose:   │ │
│  │ • Intent Detection      │  │ • Transaction           │  │ • Fallback │ │
│  │ • Semantic Search       │  │   Categorization        │  │ • Chat     │ │
│  │ • Chat/Summarization    │  │ • Label Classification  │  │ • Complex  │ │
│  │ • Query Understanding   │  │                         │  │   NLP      │ │
│  └─────────────────────────┘  └─────────────────────────┘  └────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Model Assignments

### Model 1: DistilBERT (Transaction Categorization)

| Attribute | Value |
|-----------|-------|
| **HuggingFace Model** | `distilbert-base-uncased` (fine-tuned) |
| **Purpose** | Classify transactions into categories |
| **Architecture** | Sequence Classification |
| **Size** | ~250MB |
| **GPU Required** | No |
| **Output** | `{"category": "Food & Dining", "confidence": 0.95}` |

**Why DistilBERT for Categorization:**
- Designed for **classification** (not similarity)
- Outputs **probability per category**
- Can be fine-tuned on our transaction dataset
- Fast inference (~50ms per transaction)

**Training Data:**
```
| Merchant         | Category               |
|------------------|------------------------|
| Starbucks        | Food & Dining          |
| Uber             | Transportation         |
| Amazon           | Shopping & Retail      |
| Netflix          | Entertainment          |
```

---

### Model 2: Sentence Transformer MiniLM (Intent & Chat)

| Attribute | Value |
|-----------|-------|
| **HuggingFace Model** | `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` |
| **Purpose** | Intent detection, semantic search, chat understanding |
| **Architecture** | Sentence Embedding |
| **Size** | ~80MB |
| **GPU Required** | No |
| **Output** | Vector embeddings (384 dimensions) |

**Why MiniLM for Intent Detection:**
- Understands **semantic similarity**
- "Summarize my transactions" ≈ "Show me all my transactions"
- Pre-trained on 215M+ QA pairs
- Perfect for RAG (Retrieval-Augmented Generation)

**Use Cases:**
```python
# Intent matching via similarity
user_input = "show my spending"
intents = [
    "summarize transactions",  # similarity: 0.89
    "add new transaction",     # similarity: 0.32
    "delete transaction"       # similarity: 0.28
]
# → Best match: "summarize transactions"
```

---

### Model 3: Gemini (Cloud Fallback & Complex Chat)

| Attribute | Value |
|-----------|-------|
| **Model** | `gemini-2.0-flash-lite` |
| **Purpose** | Fallback categorization, complex chat, entity extraction |
| **Rate Limit** | 15 req/min, 1000/day (free tier) |
| **When Used** | When local models have low confidence (<70%) |

**Use Cases:**
- Complex natural language parsing
- Entity extraction (amount, date, category from text)
- Generating human-readable responses
- Handling edge cases local models can't

---

## NLP Requirements

Based on PM standup requirements:

### 1. Intent Classification (Lightweight)

| Requirement | Implementation |
|-------------|---------------|
| ML Intent Classifier | MiniLM (sentence similarity matching) |
| Downloadable/Local | ✅ ~80MB model, no API needed |
| Rule-Based Complement | JSON-based keyword rules + regex patterns |

**Supported Intents:**
```python
SUPPORTED_INTENTS = [
    "summarize_transactions",    # "Summarize my transactions"
    "show_transactions",         # "Show me all my transactions"
    "add_transaction",           # "Add $50 for lunch"
    "edit_transaction",          # "Change my last transaction"
    "delete_transaction",        # "Delete my last transaction"
    "query_spending",            # "How much did I spend on food?"
    "categorize_help",           # "What category is Uber?"
    "budget_status",             # "Am I over budget?"
]
```

### 2. Named Entity Recognition (NER)

| Entity | Example | Extraction Method |
|--------|---------|-------------------|
| Amount | "$50", "50 dollars" | Regex + Gemini |
| Date | "yesterday", "last week" | dateutil + Gemini |
| Category | "food", "transportation" | MiniLM similarity |
| Description | "lunch at Subway" | Gemini parsing |

**Example:**
```
Input: "Add $25 for coffee at Starbucks yesterday"

Extracted:
  amount: 25.00
  merchant: "Starbucks"
  category: "Food & Dining"
  date: "2026-01-21"
  description: "coffee"
```

### 3. Function Calling Based on Intent

```python
# Once intent confidence > 80% and entities extracted:
INTENT_TO_FUNCTION = {
    "add_transaction": transaction_service.create_transaction,
    "edit_transaction": transaction_service.update_transaction,
    "delete_transaction": transaction_service.delete_transaction,
    "summarize_transactions": summary_service.get_spending_summary,
    "query_spending": summary_service.get_category_spending,
}
```

### 4. Guardrails (Finance-Only Scope)

| Out-of-Scope Request | Response |
|---------------------|----------|
| "How do I make bread?" | "I can only help with finance tracking." |
| "What's the weather?" | "That's outside my scope. Try asking about your spending!" |
| "Tell me a joke" | "I'm focused on your finances. Need help with transactions?" |

**Implementation:**
```python
FINANCE_KEYWORDS = ["spend", "transaction", "budget", "money", "category", ...]

def is_finance_related(text: str) -> bool:
    """Check if request is within finance scope."""
    # 1. Keyword check
    if any(kw in text.lower() for kw in FINANCE_KEYWORDS):
        return True
    # 2. MiniLM similarity to finance topics
    similarity = compute_similarity(text, FINANCE_TOPICS)
    return similarity > 0.6
```

---

## Integration Flow

### How Models Work Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     USER: "Add $50 for lunch at Subway"                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: GUARDRAILS (Is this finance-related?)                              │
│  ─────────────────────────────────────────────                              │
│  • Check for finance keywords: "add", "$50", "lunch" → ✅ PASS              │
│  • If fail → Return "Sorry, I only help with finance tracking"             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ ✅ Pass
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: INTENT DETECTION (MiniLM)                                          │
│  ─────────────────────────────────                                          │
│  • Embed user message → vector                                              │
│  • Compare to intent vectors (pre-computed)                                 │
│  • Best match: "add_transaction" (similarity: 0.92)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ Intent: add_transaction
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ENTITY EXTRACTION (Regex + Gemini)                                 │
│  ──────────────────────────────────────────                                 │
│  • Amount: $50 (regex: \$[\d.]+)                                            │
│  • Merchant: "Subway" (Gemini parsing)                                      │
│  • Date: today (default)                                                    │
│  • Description: "lunch" (Gemini parsing)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ Entities extracted
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: CATEGORIZATION (DistilBERT)                                        │
│  ──────────────────────────────────                                         │
│  • Input: "Subway lunch"                                                    │
│  • Output: {"category": "Food & Dining", "confidence": 0.96}                │
│  • (If <70% → Fallback to Gemini)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ Category assigned
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: FUNCTION CALLING                                                   │
│  ────────────────────────                                                   │
│  • Intent: add_transaction                                                  │
│  • Confidence: 0.92 (above threshold)                                       │
│  • Entities: complete                                                       │
│  → Call: transaction_service.create_transaction(data)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESPONSE: "Added $50 expense at Subway (Food & Dining)"                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Model Integration (Current Sprint)

| Task | Status | Files |
|------|--------|-------|
| DistilBERT fine-tuning | 🔄 In Progress | External |
| MiniLM integration | 📋 TODO | `intent_classifier.py` |
| Model router | 📋 TODO | `model_router.py` |
| Update orchestrator | 📋 TODO | `orchestrator.py` |

### Phase 2: NLP Features

| Task | Status | Files |
|------|--------|-------|
| Intent classification | 📋 TODO | `intent_classifier.py` |
| Entity extraction | 📋 TODO | `entity_extractor.py` |
| Guardrails | 📋 TODO | `guardrails.py` |
| Function calling | 📋 TODO | `chat_handler.py` |

### Phase 3: RAG Enhancement

| Task | Status | Files |
|------|--------|-------|
| Embeddings with MiniLM | 📋 TODO | `rag.py` |
| Vector store (ChromaDB) | 📋 TODO | `vector_store.py` |
| Similarity search | 📋 TODO | `rag.py` |

---

## Server Resources

### IONOS VPS Linux L Specs

| Resource | Available | MiniLM | DistilBERT | Both |
|----------|-----------|--------|------------|------|
| vCPU | 4 cores | ~0.5 cores | ~1 core | ~1.5 cores |
| RAM | 8 GB | ~500 MB | ~1 GB | ~1.5 GB |
| Disk | 240 GB NVMe | ~80 MB | ~250 MB | ~330 MB |
| GPU | None | Not needed | Not needed | ✅ OK |

**Memory Estimate (Runtime):**
```
MiniLM loaded:     ~500 MB RAM
DistilBERT loaded: ~1.0 GB RAM
Flask app:         ~300 MB RAM
PostgreSQL:        ~500 MB RAM
Redis cache:       ~100 MB RAM
OS/system:         ~1.0 GB RAM
────────────────────────────────
Total:             ~3.4 GB RAM
Available:         8.0 GB RAM
Headroom:          ~4.6 GB RAM ✅
```

**Conclusion:** Both models can run simultaneously on your server.

---

## Recommendations

### Recommendation 1: Model Loading Strategy

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **A: Load Both at Startup** | Fast inference, always ready | Uses ~1.5GB RAM continuously |
| **B: Lazy Loading** | Lower idle RAM | First request is slow (3-5s) |
| **C: Preload MiniLM, Lazy DistilBERT** | Fast intent, less RAM | Categorization has cold start |

**My Recommendation:** Option A (Load Both at Startup)
- You have 8GB RAM with 4.6GB headroom
- User experience matters - no cold starts
- Models stay warm in memory

---

### Recommendation 2: Replace Current bart-large-mnli

**Current:** `facebook/bart-large-mnli` (1.6GB)
**Replace with:** Jae's fine-tuned DistilBERT (~250MB)

**Why:**
- DistilBERT is 6x smaller
- Fine-tuned for YOUR categories (better accuracy)
- Faster inference

**Implementation:**
```python
# In categorizer.py
# OLD:
MODEL_NAME = "facebook/bart-large-mnli"

# NEW:
MODEL_NAME = "path/to/jae-finetuned-distilbert"  # or HuggingFace Hub path
```

---

### Recommendation 3: Intent Classifier Module

**Create new file:** `app/ai/intent_classifier.py`

```python
# Intent classifier using MiniLM
from sentence_transformers import SentenceTransformer

class IntentClassifier:
    INTENTS = {
        "summarize_transactions": [
            "summarize my transactions",
            "show me a summary",
            "what did I spend",
        ],
        "add_transaction": [
            "add a transaction",
            "log an expense",
            "I bought something",
        ],
        # ... more intents
    }

    def classify(self, text: str) -> tuple[str, float]:
        """Returns (intent, confidence)"""
        # Embed user text
        # Compare to pre-computed intent embeddings
        # Return best match
```

---

### Recommendation 4: Guardrails Module

**Create new file:** `app/ai/guardrails.py`

```python
# Finance-only scope enforcement
FINANCE_TOPICS = [
    "spending", "transaction", "budget", "money", "expense",
    "income", "category", "bill", "payment", "balance"
]

OUT_OF_SCOPE_RESPONSE = (
    "I can only help with finance tracking. "
    "Try asking about your transactions, spending, or budget!"
)

def is_in_scope(text: str, embedder) -> tuple[bool, str]:
    """Check if request is finance-related."""
    # ... implementation
```

---

### Recommendation 5: Model Router

**Create new file:** `app/ai/model_router.py`

```python
# Routes requests to appropriate model
class ModelRouter:
    def route(self, request_type: str, text: str):
        if request_type == "categorize":
            return self.distilbert.predict(text)
        elif request_type == "intent":
            return self.minilm.classify_intent(text)
        elif request_type == "embed":
            return self.minilm.embed(text)
        else:
            return self.gemini.process(text)
```

---

### Decision Points for You

Please decide on these options:

| # | Decision | Options |
|---|----------|---------|
| 1 | Model loading | A: Both at startup, B: Lazy, C: Hybrid |
| 2 | Replace bart-large-mnli with DistilBERT? | Yes / No / Wait for Jae |
| 3 | Create new intent_classifier.py? | Yes / No |
| 4 | Create guardrails.py? | Yes / No |
| 5 | Create model_router.py? | Yes / No |
| 6 | MiniLM for RAG embeddings? | Yes / Later |

---

## File Structure (Proposed)

```
backend/app/ai/
├── __init__.py              # Module exports
├── categorizer.py           # DistilBERT (Jae's model)
├── intent_classifier.py     # ✅ IMPLEMENTED: MiniLM intent detection
├── entity_extractor.py      # NEW: NER for amounts, dates, etc.
├── guardrails.py            # ✅ IMPLEMENTED: Finance scope enforcement
├── model_router.py          # ✅ IMPLEMENTED: Routes to correct model
├── orchestrator.py          # ✅ UPDATED: Uses model router
├── gemini_client.py         # Gemini fallback (existing)
├── chat_handler.py          # ✅ UPDATED: Uses intent classifier
├── rag.py                   # ✅ UPDATED: Foundation scaffolding
├── service.py               # ✅ NEW: Unified AI service facade
├── anomaly_detector.py      # Existing
├── clarification.py         # Existing
├── user_learning.py         # ✅ IMPLEMENTED: User correction learning
└── model_store/
    ├── distilbert/          # Jae's fine-tuned model
    └── minilm/              # sentence-transformers model
```

---

## Implementation Status (January 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| IntentClassifier (MiniLM) | ✅ Complete | With keyword fallback |
| Guardrails | ✅ Complete | 87 keywords, 8 semantic topics |
| ModelRouter | ✅ Complete | Routes to all 3 models |
| AIService Facade | ✅ Complete | Microservice-ready design |
| ChatHandler Integration | ✅ Complete | 3-tier parsing |
| User Learning | ✅ Complete | Per-user + global patterns |
| RAG Foundation | ✅ Scaffolding | Ready for future implementation |
| API Routes | ✅ Complete | 7 endpoints including /health |
| Configuration | ✅ Complete | 6 environment variables |
| Unit Tests | ✅ Complete | 45 tests passing |

See [AI_CHANGELOG.md](AI_CHANGELOG.md) for detailed change history.

---

*Last Updated: January 22, 2026*
