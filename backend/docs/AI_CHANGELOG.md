# AI System Changelog

## Digital Finance Tracker - AI Module Changes

This document tracks significant changes to the AI system architecture and implementation.

---

## [Sprint 2/3] February 2026 - Local AI Processing & Chat Improvements

### Overview

Major improvements to reduce cloud AI dependency and improve chat reliability:
- **SQLAlchemy Session Fixes** - Resolved DetachedInstanceError for AI sessions
- **Local Entity Extraction** - Parse transactions locally without Gemini API
- **Follow-up Response Handling** - Pending action system for multi-turn conversations
- **Improved Pattern Matching** - Handles typos and various transaction phrases

### Chat Handler Improvements (`app/ai/chat_handler.py`)

| Change | Description |
|--------|-------------|
| `_load_from_db()` | Now detects and merges detached SQLAlchemy sessions |
| `_get_session()` | Refreshes db session for cached ChatSession objects |
| `_extract_entities_locally()` | NEW: Regex-based entity extraction (amount, description, merchant, date) |
| `_parse_message()` | Added Tier 0 for pending action follow-ups, Tier 3 local extraction |
| `_handle_create_transaction()` | Saves pending action when asking for amount |

### Pattern Matching Improvements

**Amount Patterns Supported:**
- `$100`, `100 dollars`, `100 bucks`
- `spent/spend 100` (handles typos)
- `100 on shoes`, `100 for coffee`
- Standalone number follow-ups (e.g., user types "100" after being asked "How much?")

**Description Patterns Supported:**
- `bought shoes`, `spent on groceries`, `paid for coffee`
- `spent at restaurant`, `100 at Starbucks`
- Stops at action words: "yesterday", "add", "on the", "to the"

### Benefits
- ✅ **No Gemini quota usage** for simple transactions
- ✅ **Faster response** - local parsing < 50ms
- ✅ **Handles typos** - "spend" works same as "spent"
- ✅ **Multi-turn conversations** - pending actions preserved across requests

---

## [Sprint 2/3] January 2026 - Multi-Model AI Integration

### Overview

Complete implementation of the multi-model AI architecture integrating:
- **MiniLM** (Intent Classification)
- **DistilBERT** (Transaction Categorization)
- **Gemini** (Cloud Fallback & Complex NLP)

### New Files Created

| File | Purpose |
|------|---------|
| `app/ai/intent_classifier.py` | MiniLM-based semantic intent detection |
| `app/ai/guardrails.py` | Finance-only scope enforcement |
| `app/ai/model_router.py` | Routes requests to appropriate AI model |
| `app/ai/service.py` | Unified AI service facade (microservice-ready) |
| `app/ai/orchestrator.py` | Tiered categorization pipeline |
| `app/ai/user_learning.py` | User correction learning engine |
| `app/ai/rag.py` | RAG foundation (scaffolding for future) |
| `app/api/routes/ai.py` | REST API endpoints for AI features |
| `tests/unit/ai/test_intent_classifier.py` | Intent classifier unit tests |
| `tests/unit/ai/test_guardrails.py` | Guardrails unit tests |
| `tests/unit/ai/test_model_router.py` | Model router unit tests |
| `tests/unit/ai/test_service.py` | AI service unit tests |
| `tools/download_model.py` | Script to pre-download HuggingFace models |
| `tools/test_ai.py` | AI integration test script |
| `docs/AI_ARCHITECTURE.md` | Multi-model architecture documentation |
| `docs/AI_SYSTEM_GUIDE.md` | Comprehensive AI system guide |

### Files Modified

| File | Changes |
|------|---------|
| `app/ai/chat_handler.py` | Added IntentClassifier integration, 3-tier parsing |
| `app/ai/__init__.py` | Added lazy class exports via `__getattr__` |
| `app/core/config.py` | Added 6 new AI configuration variables |
| `app/__init__.py` | Registered AI blueprint, added model preloading |

---

## Key Features Implemented

### 1. Intent Classification (MiniLM)

**File:** `app/ai/intent_classifier.py`

Uses `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` for semantic similarity-based intent detection.

**Supported Intents:**
- `summarize_transactions` - "Show me a summary"
- `show_transactions` - "List my transactions"
- `add_transaction` - "Add $50 for lunch"
- `edit_transaction` - "Change my last transaction"
- `delete_transaction` - "Remove my last expense"
- `query_spending` - "How much did I spend on food?"
- `categorize_help` - "What category is Uber?"
- `budget_status` - "Am I over budget?"
- `get_insights` - "Analyze my spending"
- `help` - "What can you do?"

**Fallback Mode:**
If `sentence-transformers` is not installed, automatically falls back to keyword-based matching.

```python
from app.ai.intent_classifier import get_intent_classifier

classifier = get_intent_classifier()
classifier.initialize()
intent, confidence = classifier.classify("show my spending")
# ("summarize_transactions", 0.87)
```

---

### 2. Guardrails (Finance Scope Enforcement)

**File:** `app/ai/guardrails.py`

Ensures AI only handles finance-related requests. Out-of-scope requests are politely redirected.

**Features:**
- 87 finance-related keywords for fast detection
- 8 semantic topic embeddings for similarity matching
- Graceful fallback to keyword-only mode

```python
from app.ai.guardrails import get_guardrails

guardrails = get_guardrails()
in_scope, message = guardrails.check_scope("How do I make bread?")
# (False, "I can only help with finance tracking...")
```

---

### 3. Model Router

**File:** `app/ai/model_router.py`

Central router that directs requests to the appropriate AI model.

**Routing Logic:**
- **Categorization:** DistilBERT → Gemini (if confidence < 70%)
- **Intent Detection:** MiniLM (semantic similarity)
- **Embeddings:** MiniLM (384-dimensional vectors)
- **Entity Extraction:** Gemini (complex NLP)
- **Chat:** Gemini (conversation)

```python
from app.ai.model_router import get_model_router

router = get_model_router()
router.initialize()

# Categorize
result = router.categorize("Starbucks Coffee")

# Detect intent
intent, conf = router.detect_intent("show my spending")

# Check scope
in_scope, msg = router.check_scope("how much did I spend?")
```

---

### 4. AI Service Facade (Microservice-Ready)

**File:** `app/ai/service.py`

Unified interface for all AI operations. Designed for easy extraction to a separate microservice.

**Features:**
- Single entry point for all AI operations
- Built-in metrics collection (Prometheus-ready)
- Health check endpoint for load balancers/k8s
- Clean separation from business logic

```python
from app.ai.service import get_ai_service

ai = get_ai_service()
ai.initialize()

# All operations via single interface
result = ai.categorize("Starbucks")
intent, conf = ai.detect_intent("add expense")
in_scope, msg = ai.check_scope("tell me a joke")
metrics = ai.get_metrics()
```

---

### 5. ChatHandler Integration

**File:** `app/ai/chat_handler.py`

Enhanced with 3-tier parsing:

1. **Tier 1: Rule-Based** - Fast regex patterns for common commands
2. **Tier 2: MiniLM** - Semantic intent classification
3. **Tier 3: Gemini** - Fallback for complex/ambiguous input

```python
from app.ai.chat_handler import get_chat_handler

handler = get_chat_handler()
handler.initialize()

result = handler.process_message(user_id, "Add $50 for lunch at Subway")
# {
#     "intent": "create_transaction",
#     "response": "I'll add a $50 expense at Subway...",
#     "requires_confirmation": True,
#     "parsed_data": {...}
# }
```

---

## Configuration

### New Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_INTENT_CLASSIFIER_ENABLED` | `1` | Enable/disable MiniLM intent classifier |
| `AI_CATEGORIZER_ENABLED` | `1` | Enable/disable DistilBERT categorizer |
| `AI_GUARDRAILS_ENABLED` | `1` | Enable/disable finance scope enforcement |
| `AI_GEMINI_ENABLED` | `1` | Enable/disable Gemini cloud fallback |
| `GEMINI_API_KEY` | - | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash-lite` | Gemini model to use |

### Usage

```bash
# Disable intent classifier (use keyword fallback)
AI_INTENT_CLASSIFIER_ENABLED=0

# Disable all AI (for testing without models)
AI_INTENT_CLASSIFIER_ENABLED=0
AI_CATEGORIZER_ENABLED=0
AI_GUARDRAILS_ENABLED=0
AI_GEMINI_ENABLED=0
```

---

## API Endpoints

### New Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/ai/categorize` | Required | Categorize a transaction |
| POST | `/api/v1/ai/chat` | Required | Process chat message |
| GET | `/api/v1/ai/insights` | Required | Get spending insights |
| GET | `/api/v1/ai/clarifications` | Required | Get pending clarifications |
| POST | `/api/v1/ai/clarifications/{id}/resolve` | Required | Resolve clarification |
| POST | `/api/v1/ai/clarifications/{id}/dismiss` | Required | Dismiss clarification |
| GET | `/api/v1/ai/status` | Required | Get AI system status |
| GET | `/api/v1/ai/health` | **None** | Health check for monitoring |

### Health Endpoint

The `/health` endpoint is designed for load balancers and Kubernetes probes:

```json
{
    "status": "healthy",
    "components": {
        "gemini": "ok",
        "intent_classifier": "ok",
        "categorizer": "ok",
        "guardrails": "ok"
    },
    "timestamp": "2026-01-22T10:30:00Z"
}
```

Status values: `healthy`, `degraded`, `unhealthy`

---

## Bug Fixes

### 1. ModelRouter Categorizer Method Call

**Issue:** `model_router.py` was calling `self.categorizer.initialize()` but the `TransactionCategorizer` class uses `load_model()`.

**Fix:** Changed to `self.categorizer.load_model()` on line 166.

### 2. Test Singleton Variable Names

**Issue:** Test files were resetting wrong singleton variable names.

**Files Fixed:**
- `test_intent_classifier.py`: `_intent_classifier_instance` → `_classifier`
- `test_guardrails.py`: `_guardrails_instance` → `_guardrails`
- `test_model_router.py`: `_model_router_instance` → `_router`
- `test_service.py`: `service_module._ai_service_instance` → `AIService._instance`

### 3. IntentClassifier Graceful Fallback

**Issue:** No fallback when `sentence-transformers` package is not installed.

**Fix:** Added `_use_fallback` flag and `_classify_by_keywords()` method for keyword-based fallback.

### 4. Guardrails Config Check

**Issue:** No way to disable guardrails via environment variable.

**Fix:** Added config flag check for `AI_GUARDRAILS_ENABLED`.

---

## Test Coverage

### New Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_intent_classifier.py` | 12 tests | Class existence, methods, intents, singleton |
| `test_guardrails.py` | 11 tests | Class existence, keywords, singleton |
| `test_model_router.py` | 9 tests | Class existence, methods, singleton |
| `test_service.py` | 13 tests | Class existence, methods, metrics, singleton |

### Test Results

```
45 passed in 0.66s
```

All tests use mocking to avoid loading actual ML models during CI/CD.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API LAYER: /api/v1/ai/                              │
│  ┌──────────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌────────┐                  │
│  │/categorize│ │/chat │ │/insights │ │/status │ │/health │                  │
│  └─────┬─────┘ └───┬──┘ └────┬─────┘ └───┬────┘ └───┬────┘                  │
│        └───────────┴─────────┴───────────┴─────────┴────────────────────────┤
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────┐           │
│  │                      AIService (Facade)                       │           │
│  │  • Unified interface • Metrics • Health checks • Microservice │           │
│  └─────────────────────────────────┬────────────────────────────┘           │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────┐           │
│  │                        ModelRouter                            │           │
│  │     Routes: Categorizer │ IntentClassifier │ Guardrails │ Gemini        │
│  └──────────┬──────────────────────┬────────────────────┬───────┘           │
│             │                      │                    │                   │
│  ┌──────────▼──────────┐ ┌─────────▼─────────┐ ┌───────▼───────┐           │
│  │  TransactionCategorizer │ │ IntentClassifier │ │ GeminiClient │           │
│  │  (DistilBERT ~250MB)    │ │ (MiniLM ~80MB)   │ │ (Cloud API)  │           │
│  └──────────┬──────────┘ └─────────┬─────────┘ └───────────────┘           │
│             │                      │                                        │
│  Fallback: keyword matching   keyword fallback                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Notes

### For Developers

1. **No breaking changes** to existing API endpoints
2. New AI features are additive
3. All new features have graceful fallbacks
4. Tests pass without ML model dependencies

### For DevOps

1. **New health endpoint:** `/api/v1/ai/health` (no auth)
2. **Model storage:** ~330MB for both models
3. **Memory usage:** ~1.5GB RAM with both models loaded
4. **Environment variables:** 6 new AI-related configs

---

*Last Updated: January 22, 2026*
