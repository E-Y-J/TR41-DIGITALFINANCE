# 🎬 AI Demo Guide - Digital Finance Tracker

## Quick Start (Docker)

### 1. Start All Services
```bash
# From project root directory
docker-compose up --build
```

Wait for all services to be healthy (check with `docker ps`).

### 2. Run the AI Demo CLI
```bash
# Open interactive AI demo
docker exec -it flask_backend python tools/demo_cli.py
```

---

## 🤖 What the AI System Does

### Overview
Our AI system provides **intelligent financial management** through natural language:

| Feature | Description | Technology |
|---------|-------------|------------|
| **Transaction Categorization** | Auto-categorize expenses (Starbucks → Food & Dining) | HuggingFace + Gemini |
| **Natural Language Commands** | "Add $50 for lunch at Subway" | Gemini NLP |
| **Spending Queries** | "How much did I spend on food?" | Intent Classification |
| **Smart Guardrails** | Keeps AI focused on finance topics | MiniLM Semantic Search |

### AI Architecture (3-Tier Fallback)
```
User Input → HuggingFace (local, fast)
          → Gemini (cloud, accurate)
          → Keyword Matching (reliable fallback)
```

---

## 📋 Demo Scenarios to Show

### Scenario 1: Natural Language Transaction Creation
```
You: Add $45.50 for dinner at Olive Garden

AI: I'll add a $45.50 expense at Olive Garden under "Food & Dining".
    Date: Today
    Category: Food & Dining (confidence: 95%)

    Should I proceed? (yes/no)

You: yes

AI: ✓ Transaction added successfully!
```

### Scenario 2: Spending Analysis
```
You: How much did I spend on food this month?

AI: Based on your transactions this month:
    • Food & Dining: $342.50
    • 12 transactions
    • Avg per transaction: $28.54

    Your top merchants: Starbucks ($45), Chipotle ($38)
```

### Scenario 3: Smart Categorization
```
You: What category is Uber?

AI: "Uber" is categorized as "Transportation" with 92% confidence.

    Similar merchants in this category:
    • Lyft, Gas stations, Public transit
```

### Scenario 4: Guardrails in Action
```
You: How do I make pasta?

AI: I specialize in personal finance tracking and can't help with
    cooking questions.

    I can help you with:
    • Adding/viewing transactions
    • Analyzing spending patterns
    • Managing budgets
    • Categorizing expenses
```

### Scenario 5: Budget Check
```
You: Am I over budget this month?

AI: Budget Status for January 2026:
    • Food & Dining: $342/$400 (85%) ⚠️
    • Transportation: $120/$200 (60%) ✓
    • Entertainment: $89/$100 (89%) ⚠️

    You're within budget overall, but watch Food & Entertainment!
```

---

## 🔧 Demo CLI Commands

| Command | Description |
|---------|-------------|
| `demo` | Run automated demo scenarios |
| `test` | Quick AI component health check |
| `help` | Show available commands |
| `clear` | Start fresh conversation |
| `quit` | Exit the demo |

### Or just type naturally:
- "Add $25 for coffee at Starbucks"
- "Show my transactions this week"
- "Delete my last transaction"
- "What category is Amazon?"

---

## 🧪 Quick AI Test (show component status)

In the demo CLI, type `test` to see:

```
═══════════════════════════════════════════════════════
                  AI Component Quick Test
═══════════════════════════════════════════════════════

--- 1. Gemini API Client ---
✓ Gemini initialized successfully
✓ Test categorization: Starbucks → Food & Dining (85%)

--- 2. Intent Classifier (MiniLM) ---
✓ MiniLM model loaded successfully
  ✓ 'Add $50 for lunch' → add_transaction (92%)
  ✓ 'Show my spending' → show_transactions (88%)
  ✓ 'Delete last transaction' → delete_transaction (91%)

--- 3. Guardrails (Scope Enforcement) ---
  ✓ 'How much did I spend on food?' → IN SCOPE
  ✓ 'Add $25 for coffee' → IN SCOPE
  ✓ 'How do I make bread?' → OUT OF SCOPE
  ✓ 'What's the weather today?' → OUT OF SCOPE
✓ Guardrails working correctly

--- 4. AI Orchestrator (Tiered Categorization) ---
  ✓ HuggingFace Model: Ready
  ✓ Gemini Fallback: Ready
  ✓ Keyword Matching: Ready
  → McDonald's            = Food & Dining    (huggingface, 94%)
  → Shell Gas Station     = Transportation   (keyword, 100%)
  → Netflix               = Entertainment    (huggingface, 91%)
✓ Orchestrator working correctly

--- 5. Chat Handler (Natural Language) ---
✓ Chat handler initialized

Result: 5/5 components working
```

---

## 🐳 Docker Commands Reference

```bash
# Start services
docker-compose up --build

# Start services (background)
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Run demo CLI
docker exec -it flask_backend python tools/demo_cli.py

# Run quick AI test
docker exec -it flask_backend python tools/test_ai.py

# Check service health
docker ps

# Stop services
docker-compose down

# Full rebuild
docker-compose down && docker-compose up --build
```

---

## 🔍 Showing API Endpoints (Optional)

If the PM wants to see the API:

### Health Check
```bash
curl http://localhost:8000/health/
```

### AI Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Add $50 for lunch"}'
```

### Categorize Transaction
```bash
curl -X POST http://localhost:8000/api/v1/ai/categorize \
  -H "Content-Type: application/json" \
  -d '{"merchant": "Starbucks", "amount": 5.50}'
```

---

## 📊 Key Metrics to Highlight

- **Response Time**: < 500ms for most queries
- **Categorization Accuracy**: ~90% with HuggingFace, 95%+ with Gemini
- **Model Size**: ~80MB MiniLM + ~250MB DistilBERT
- **Memory Usage**: ~1.5GB for all AI models
- **Fallback Reliability**: 3-tier system ensures always gets a result

---

## 💡 Demo Tips

1. **Start with the test command** to show all components are working
2. **Show natural language flow** - add transaction, query spending, get insights
3. **Demonstrate guardrails** - ask off-topic question to show scope enforcement
4. **Highlight speed** - response times are shown in the CLI
5. **Show confidence scores** - AI tells you how sure it is

---

## ❓ Common Questions & Answers

**Q: What happens if Gemini API is down?**
A: The system falls back to HuggingFace, then keyword matching. Always returns a result.

**Q: How does categorization work?**
A: 3-tier system:
1. HuggingFace (local model, fast) - if confidence ≥ 70%, use it
2. Gemini (cloud API) - if HuggingFace < 70%, try Gemini
3. Keyword matching - reliable fallback for common merchants

**Q: Is the AI fine-tuned for finance?**
A: Yes! We fine-tuned DistilBERT on financial transaction data.

**Q: How do guardrails work?**
A: MiniLM semantic similarity compares user input against finance topics. Off-topic requests are politely redirected.

---

## 🎯 Demo Checklist

- [ ] Docker services running (`docker ps` shows all healthy)
- [ ] Demo CLI launches without errors
- [ ] `test` command shows all components working
- [ ] Can add transaction via natural language
- [ ] Can query spending
- [ ] Guardrails block off-topic questions
- [ ] Response times are reasonable (< 1 second)

---

*Last updated: January 2026*
*Sprint 2/3 - AI Foundation Implementation*
