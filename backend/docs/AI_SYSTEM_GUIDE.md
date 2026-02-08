# AI System Documentation

## Digital Finance Tracker - AI-Powered Features

This document provides comprehensive documentation for the AI system, including architecture, endpoints, setup guide, and integration instructions for the frontend team.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [API Endpoints](#api-endpoints)
5. [Setup Guide](#setup-guide)
6. [Frontend Integration](#frontend-integration)
7. [Database Requirements](#database-requirements)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What Does the AI System Do?

The AI system provides intelligent transaction categorization and spending insights:

| Feature | Description |
|---------|-------------|
| **Auto-Categorization** | Automatically assigns categories to transactions based on merchant name |
| **User Learning** | Learns from user corrections to improve accuracy over time |
| **Spending Insights** | Analyzes spending patterns and detects anomalies |
| **Chat Interface** | Natural language commands for CRUD operations |
| **Clarification Flow** | Prompts users when AI confidence is low |

### Key Benefits

- ✅ **No manual categorization** - AI handles 90%+ of transactions
- ✅ **Personalized** - Learns each user's preferences
- ✅ **Free to run** - Uses open-source models + free API tier
- ✅ **Offline capable** - HuggingFace model runs locally

---

## Architecture

### 5-Tier Categorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TRANSACTION: "Coffee Shop ABC $5.00"                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 0: USER LEARNED (Highest Priority)                                    │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Check if THIS USER corrected this merchant before                        │
│  • If found → Return immediately with 95% confidence                        │
│  • Source: "user_learned"                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ Not found
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: KEYWORD MATCHING (Instant)                                         │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Check against 200+ known merchant keywords                               │
│  • "starbucks" → Food & Dining, "uber" → Transportation                     │
│  • If match → Return with 100% confidence                                   │
│  • Source: "keyword"                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ No match
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: HUGGINGFACE (Local AI, ~2 sec)                                     │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Model: facebook/bart-large-mnli (1.6GB)                                  │
│  • Zero-shot classification - no fine-tuning needed                         │
│  • If confidence >= 70% → Return result                                     │
│  • If confidence 50-70% → Continue but flag for review                      │
│  • Source: "huggingface"                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ < 70% confidence
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3: GEMINI API (Cloud Fallback, ~1 sec)                                │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Model: gemini-2.0-flash-lite                                             │
│  • Rate limit: 15 req/min, 1000/day (free tier)                             │
│  • Includes reasoning in response                                           │
│  • Source: "gemini"                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ < 50% confidence
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 4: UNKNOWN (Needs User Input)                                         │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Returns "Unknown" category                                               │
│  • Sets needs_clarification: true                                           │
│  • Provides alternatives for user to choose                                 │
│  • Creates clarification request                                            │
│  • Source: "unknown"                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Orchestrator (`app/ai/orchestrator.py`)

The main coordinator that manages the categorization flow.

```python
from app.ai.orchestrator import get_orchestrator

orchestrator = get_orchestrator()
orchestrator.initialize()

result = orchestrator.categorize(
    merchant_name="Starbucks Coffee",
    amount=5.50,
    transaction_type="expense",
    user_id=user_uuid  # For personalized learning
)

# Result:
# {
#     "category": "Food & Dining",
#     "category_id": "uuid-string",
#     "confidence": 1.0,
#     "source": "keyword",
#     "needs_clarification": False,
#     "alternatives": []
# }
```

### 2. Categorizer (`app/ai/categorizer.py`)

HuggingFace zero-shot classification.

- **Model**: `facebook/bart-large-mnli` (non-gated, free)
- **Size**: ~1.6GB (downloads on first use)
- **Type**: Zero-shot classification
- **Categories**: 10 predefined types

### 3. Gemini Client (`app/ai/gemini_client.py`)

Google Gemini API for fallback categorization.

- **Model**: `gemini-2.0-flash-lite`
- **Rate Limits**: 15/min, 1000/day
- **Features**: Structured JSON output, reasoning

### 4. User Learning (`app/ai/user_learning.py`)

Learns from user corrections.

```python
from app.ai.user_learning import get_learning_engine

engine = get_learning_engine()

# Record when user corrects a category
engine.record_correction(
    user_id=uuid,
    merchant_name="Local Shop ABC",
    correct_category="Food & Dining",
    original_category="Shopping & Retail",
    original_source="huggingface"
)

# Next time, system uses learned category
```

### 5. Anomaly Detector (`app/ai/anomaly_detector.py`)

Detects unusual spending patterns.

- **HIGH_SPENDING**: Category spending 2x+ baseline
- **LARGE_TRANSACTION**: Single transaction > $500
- **UNUSUAL_CATEGORY**: First time in category

### 6. Chat Handler (`app/ai/chat_handler.py`)

Natural language command parsing.

```
"Add $50 for lunch at Subway" → CREATE_TRANSACTION intent
"How much did I spend on food?" → QUERY_SPENDING intent
"Delete my last transaction" → DELETE_TRANSACTION intent
```

### 7. RAG Foundation (`app/ai/rag.py`)

Scaffolding for future RAG implementation (not active yet).

---

## API Endpoints

### Base URL

```
/api/v1/ai
```

### Authentication

All endpoints require Auth0 authentication via Bearer token:

```
Authorization: Bearer <auth0_token>
```

---

### POST `/api/v1/ai/categorize`

Categorize a transaction based on merchant name.

**Request:**
```json
{
    "text": "Starbucks Coffee #1234",
    "amount": 5.50,
    "transaction_type": "expense"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "category": "Food & Dining",
        "category_id": "550e8400-e29b-41d4-a716-446655440001",
        "confidence": 1.0,
        "source": "keyword",
        "needs_clarification": false,
        "alternatives": [],
        "reasoning": "Matched by keyword"
    }
}
```

**Source Values:**
| Source | Meaning |
|--------|---------|
| `user_learned` | User corrected this merchant before (95% conf) |
| `keyword` | Matched known merchant keyword (100% conf) |
| `huggingface` | Local AI model prediction |
| `gemini` | Cloud AI fallback |
| `unknown` | Low confidence, needs user input |

---

### POST `/api/v1/ai/chat`

Process a natural language command.

**Request:**
```json
{
    "message": "Add $50 for lunch at Subway",
    "context": {}
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "intent": "create_transaction",
        "response": "I'll add a $50 expense at Subway under Food & Dining. Should I proceed?",
        "requires_confirmation": true,
        "parsed_data": {
            "amount": 50.00,
            "merchant_name": "Subway",
            "category": "Food & Dining",
            "transaction_type": "expense"
        },
        "alternatives": []
    }
}
```

**Intent Types:**
| Intent | Description |
|--------|-------------|
| `create_transaction` | User wants to add a transaction |
| `edit_transaction` | User wants to modify a transaction |
| `delete_transaction` | User wants to remove a transaction |
| `query_spending` | User asking about spending |
| `categorize` | User asking what category something is |
| `general_chat` | General conversation |

---

### GET `/api/v1/ai/insights`

Get AI-powered spending insights.

**Query Parameters:**
- `period`: `day`, `week`, `month`, `year` (default: `month`)

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "period": "Last 30 days",
        "top_categories": [
            {
                "category_id": "uuid",
                "category_name": "Food & Dining",
                "total_spent": 450.00,
                "transaction_count": 25,
                "avg_per_transaction": 18.00
            }
        ],
        "unusual_activity": [
            {
                "type": "high_spending",
                "message": "Food & Dining spending is 2.5x your usual",
                "created_at": "2026-01-15T10:00:00Z"
            }
        ],
        "spending_trend": "increasing",
        "recommendations": [
            "Your spending has increased recently. Consider reviewing your budget."
        ]
    }
}
```

---

### GET `/api/v1/ai/clarifications`

Get pending clarification requests for the user.

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440099",
            "type": "category",
            "transaction_id": "550e8400-e29b-41d4-a716-446655440050",
            "alternatives": [
                {"category": "Food & Dining", "confidence": 0.45},
                {"category": "Shopping & Retail", "confidence": 0.35},
                {"category": "Entertainment", "confidence": 0.15}
            ],
            "context": {
                "merchant_name": "Unknown Store ABC",
                "amount": 25.00
            },
            "status": "pending",
            "created_at": "2026-01-15T10:00:00Z",
            "expires_at": "2026-01-16T10:00:00Z"
        }
    ]
}
```

---

### POST `/api/v1/ai/clarifications/{id}/resolve`

Resolve a clarification with user's choice.

**Request:**
```json
{
    "choice": "Food & Dining"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "status": "resolved",
        "user_choice": "Food & Dining"
    }
}
```

**Side Effect:** The user's choice is recorded for future learning.

---

### POST `/api/v1/ai/clarifications/{id}/dismiss`

Dismiss a clarification without responding.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "status": "dismissed"
    }
}
```

---

### GET `/api/v1/ai/status`

Get AI system status (useful for debugging).

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "orchestrator": {
            "is_initialized": true,
            "services": {
                "huggingface": true,
                "gemini": true,
                "keyword": true
            },
            "thresholds": {
                "huggingface_threshold": 0.70,
                "unknown_threshold": 0.50
            },
            "categories_cached": 11
        },
        "gemini": {
            "is_initialized": true,
            "api_key_set": true,
            "daily_requests_used": 15,
            "daily_limit": 1000,
            "requests_remaining_today": 985
        },
        "chat": {
            "is_initialized": true
        },
        "clarifications": {
            "total_pending": 3,
            "total_requests": 50
        },
        "user_learning": {
            "total_corrections": 25,
            "unique_merchants_learned": 18
        }
    }
}
```

---

## Setup Guide

### Prerequisites

1. **Python 3.11+**
2. **PostgreSQL** with categories seeded
3. **~2GB disk space** for HuggingFace model

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key AI packages:
```
transformers>=4.36.0
torch>=2.1.0
google-genai>=1.0.0
```

### Step 2: Set Environment Variables

Add to `.env`:

```bash
# Required for Gemini fallback
GEMINI_API_KEY=AIzaSy...your-key-here

# Optional: Override HuggingFace model
HUGGINGFACE_MODEL=facebook/bart-large-mnli
```

### Step 3: Ensure Database is Ready

The AI system requires:
- `categories` table seeded with 11 default categories
- `users` table for user_id references
- `transactions` table for anomaly detection
- `alerts` table for notifications

```bash
# Run migrations
flask db upgrade

# Seed categories (if not already done)
flask seed-categories
```

### Step 4: First-Time Model Download

The HuggingFace model (~1.6GB) downloads automatically on first use.
To pre-download:

```bash
python -c "
from app.ai.categorizer import get_categorizer
cat = get_categorizer()
cat.load_model()
print('Model downloaded!')
"
```

### Step 5: Verify AI is Working

```bash
python -c "
from app import create_app
app = create_app('development')

with app.app_context():
    from app.ai.orchestrator import get_orchestrator

    orch = get_orchestrator()
    status = orch.initialize()
    print('AI Status:', status)

    result = orch.categorize(merchant_name='Starbucks')
    print('Test:', result['category'], '(' + result['source'] + ')')
"
```

Expected output:
```
AI Status: {'huggingface': True, 'gemini': True, 'keyword': True}
Test: Food & Dining (keyword)
```

---

## Frontend Integration

### Auto-Categorization on Transaction Create

When user enters a transaction, call categorize endpoint:

```javascript
// Frontend: When user types merchant name
const categorize = async (merchantName, amount) => {
    const response = await fetch('/api/v1/ai/categorize', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: merchantName,
            amount: amount,
            transaction_type: 'expense'
        })
    });

    const data = await response.json();

    if (data.success) {
        // Auto-select the category
        setCategoryId(data.data.category_id);

        // Show confidence indicator
        if (data.data.confidence < 0.7) {
            showWarning("AI is not sure about this category");
        }

        // Handle low confidence
        if (data.data.needs_clarification) {
            showCategoryPicker(data.data.alternatives);
        }
    }
};
```

### Handling User Corrections

When user changes AI-assigned category:

```javascript
// Frontend: When user selects different category
const handleCategoryChange = async (transactionId, oldCategory, newCategory) => {
    // Save the transaction with new category
    await updateTransaction(transactionId, { category_id: newCategory.id });

    // Record the correction for learning
    // This happens automatically on the backend when category changes
};
```

### Displaying Clarifications

```javascript
// Frontend: Check for pending clarifications
const getClarifications = async () => {
    const response = await fetch('/api/v1/ai/clarifications', {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    const data = await response.json();

    if (data.data.length > 0) {
        showClarificationModal(data.data[0]);
    }
};

// Frontend: Resolve clarification
const resolveClarification = async (clarificationId, choice) => {
    await fetch(`/api/v1/ai/clarifications/${clarificationId}/resolve`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ choice: choice })
    });
};
```

---

## Database Requirements

### Required Tables

| Table | Purpose | AI Component |
|-------|---------|--------------|
| `categories` | Category name → ID mapping | Orchestrator |
| `users` | User identification | User Learning |
| `transactions` | Spending history | Anomaly Detector |
| `alerts` | Anomaly notifications | Anomaly Detector |

### In-Memory (Not Persisted)

| Data | Storage | Limitation |
|------|---------|------------|
| User corrections | In-memory dict | Lost on restart |
| Chat sessions | In-memory dict | Lost on restart |
| Clarifications | In-memory dict | Lost on restart |

### Future Database Tables

For persistence (optional future sprint):

```sql
-- User category corrections (for learning)
CREATE TABLE user_category_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    merchant_pattern VARCHAR(255) NOT NULL,
    category_id UUID NOT NULL REFERENCES categories(id),
    correction_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, merchant_pattern)
);
```

---

## Troubleshooting

### "HuggingFace model not loaded"

**Cause:** Model hasn't been downloaded yet (1.6GB)

**Fix:** First request takes 1-2 minutes to download. Check internet connection.

### "Gemini rate limit exceeded"

**Cause:** Hit 15 req/min or 1000/day limit

**Fix:** Wait for rate limit reset. HuggingFace will be used as fallback.

### "Categories not cached"

**Cause:** Categories table empty or not seeded

**Fix:** Run `flask db upgrade` and ensure categories are seeded.

### "User learning not working"

**Cause:** Not passing `user_id` to categorize endpoint

**Fix:** Ensure auth token is valid and `g.user.id` is set.

### "Low confidence on all predictions"

**Cause:** Unknown merchant not in keyword map

**Expected behavior:** HuggingFace zero-shot has 50-80% confidence on unfamiliar merchants. This is normal.

---

## Performance

### Latency

| Tier | Latency | Notes |
|------|---------|-------|
| User Learned | <1ms | In-memory lookup |
| Keyword | <1ms | Dict lookup |
| HuggingFace | 1-3 sec | First call loads model |
| Gemini | 0.5-2 sec | Network latency |

### Memory

| Component | Memory |
|-----------|--------|
| HuggingFace model | ~1.6GB RAM |
| User learning cache | ~1MB per 10k corrections |
| Category cache | ~1KB |

### Recommendations

1. **Pre-warm** the HuggingFace model on app startup
2. **Use Redis** for rate limiting in production
3. **Monitor** Gemini daily quota usage

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) | Multi-model architecture design |
| [AI_CHANGELOG.md](AI_CHANGELOG.md) | Change history and release notes |
| [FRONTEND_API_GUIDE.md](FRONTEND_API_GUIDE.md) | Frontend integration guide |

---

*Last Updated: January 22, 2026*
