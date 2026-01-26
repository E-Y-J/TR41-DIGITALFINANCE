# AI Categorization & Notifications Implementation Plan

> **Status:** 🟡 FOUNDATION COMPLETE - AI INTEGRATION PENDING
> **Prepared by:** Backend Team
> **Last Updated:** January 7, 2026

---

## 📊 Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1: Database Foundation** | Models, schemas, services, routes | ✅ COMPLETE |
| **Phase 2: AI Integration** | HuggingFace + Gemini categorization | ⏳ PENDING |
| **Phase 3: Automatic Alerts** | Anomaly detection logic | ⏳ PENDING |

### Phase 1 Completed Items ✅
- Categories model (11 defaults) + service + routes
- Notifications model (6 types) + service + routes
- Alerts model (foundation) + service + routes
- Summary service + routes (daily/weekly/monthly/yearly/ytd)
- Database migration ready
- 21 integration tests passing
- Keyword-based auto-categorization (rule-based, no AI)

### Phase 2 Pending Items ⏳
- HuggingFace model integration (`app/ai/categorize.py`)
- Gemini API fallback integration
- AI endpoints (`/api/ai/categorize`, `/api/ai/chat`)
- Automatic alert generation (anomaly detection)

---

## 📋 Executive Summary

This document outlines the backend foundation for:
1. **AI Transaction Categorization** - Auto-categorize transactions using HuggingFace model + Gemini fallback
2. **Notifications System** - Support frontend notification requests
3. **Spending Summaries** - Data structure for daily/weekly/monthly/yearly reports

---

## 🎯 Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Approach | **Hybrid** (HuggingFace + Gemini) | Best accuracy, cost-efficient |
| HF Model Confidence Threshold | **70%** | Below 70% → fallback to Gemini |
| Unknown Threshold | **50%** | Below 50% → mark as "Unknown" |
| Store AI Feedback | **No** | Simplify for initial release |
| Notification Types | **6 core types** | Cover essential use cases |
| Category Icons/Colors | **Frontend handles** | Keep backend simple |
| Subcategories | **No** | Main categories only |

---

## 🗄️ Database Schema Changes

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA - AI FOUNDATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────┐                                                      │
│  │      users        │                                                      │
│  │   (existing)      │◄─────────────────────────────────┐                  │
│  └───────────────────┘                                  │                  │
│           │                                             │                  │
│           │ 1:N                                         │ 1:N              │
│           ▼                                             │                  │
│  ┌───────────────────┐         ┌───────────────────┐    │                  │
│  │   transactions    │         │   notifications   │────┘                  │
│  │   (modified)      │         │      (NEW)        │                       │
│  └───────────────────┘         └───────────────────┘                       │
│           │                                                                 │
│           │ N:1                                                             │
│           ▼                                                                 │
│  ┌───────────────────┐                                                      │
│  │    categories     │                                                      │
│  │      (NEW)        │                                                      │
│  └───────────────────┘                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### NEW TABLE: `categories`

Stores the 11 transaction categories (10 main + 1 Unknown).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT uuid4 | Primary key |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Category name |
| `description` | TEXT | NULL | Category description |
| `transaction_type` | ENUM | NOT NULL | "income", "expense", or "both" |
| `is_system` | BOOLEAN | DEFAULT TRUE | System category (cannot delete) |
| `display_order` | INTEGER | DEFAULT 0 | UI display order |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_categories_name` on `name`
- `idx_categories_transaction_type` on `transaction_type`

---

### NEW TABLE: `notifications`

Stores user notifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT uuid4 | Primary key |
| `user_id` | UUID | FK → users.id, NOT NULL | User who receives notification |
| `type` | VARCHAR(50) | NOT NULL, DEFAULT "default" | Notification type |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT "unread" | "unread" or "read" |
| `message` | TEXT | NOT NULL | Notification message |
| `metadata` | JSON | NULL | Extra data (transaction_id, etc.) |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

**Indexes:**
- `idx_notifications_user_id` on `user_id`
- `idx_notifications_user_status` on (`user_id`, `status`)
- `idx_notifications_user_type` on (`user_id`, `type`)

**Notification Types (6 core):**
| Type | Trigger | Example |
|------|---------|---------|
| `default` | Generic/system | "Welcome to Digital Finance!" |
| `new_transaction` | Transaction created | "New transaction: -$50.00 at Starbucks" |
| `deleted_transaction` | Transaction deleted | "Transaction deleted: -$25.00 at Amazon" |
| `edited_profile` | Profile updated | "Your profile was updated successfully" |
| `weekly_summary_ready` | Weekly report ready | "Your weekly spending summary is ready!" |
| `category_updated` | AI re-categorized | "Transaction re-categorized to Food & Dining" |

---

### MODIFIED TABLE: `transactions`

Add AI categorization fields.

| New Column | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `category_id` | UUID | FK → categories.id, NULL | Link to categories table |
| `ai_confidence` | FLOAT | NULL, CHECK 0.0-1.0 | AI confidence score |
| `ai_source` | VARCHAR(20) | NULL | "huggingface", "gemini", or "user" |
| `is_user_override` | BOOLEAN | DEFAULT FALSE | User manually set category? |
| `original_category_id` | UUID | FK → categories.id, NULL | AI's original suggestion (if overridden) |

**Note:** Keep existing `category` VARCHAR field for backward compatibility during migration. Deprecate after migration.

**New Indexes:**
- `idx_transaction_category_id` on `category_id`
- `idx_transaction_ai_source` on `ai_source`

---

## 🏷️ Category Seed Data

11 categories to seed into the database:

| # | Name | Description | Type | Display Order |
|---|------|-------------|------|---------------|
| 1 | Food & Dining | Restaurants, groceries, fast food, coffee shops, food delivery | expense | 1 |
| 2 | Transportation | Gas, rideshare, airlines, public transport, car rental | expense | 2 |
| 3 | Shopping & Retail | Online shopping, electronics, retail, fashion, home & garden | expense | 3 |
| 4 | Entertainment & Recreation | Streaming, gaming, movies, music, sports | expense | 4 |
| 5 | Healthcare & Medical | Medical, pharmacy, dental, vision, fitness | expense | 5 |
| 6 | Utilities & Services | Electricity, water, gas, internet & phone, cable | expense | 6 |
| 7 | Financial Services | Banking, insurance, credit cards, investments, taxes | expense | 7 |
| 8 | Income | Salary, freelance, business, investments, government benefits | income | 8 |
| 9 | Government & Legal | Taxes, licenses, legal services, government fees | expense | 9 |
| 10 | Charity & Donations | Charitable, religious, community, political donations | expense | 10 |
| 11 | Unknown | Uncategorized transactions (AI confidence < 50%) | both | 99 |

---

## 🤖 AI Categorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI CATEGORIZATION WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Transaction Created                                                        │
│  (merchant_name, amount, description)                                       │
│          │                                                                  │
│          ▼                                                                  │
│  ┌─────────────────────────────────────┐                                   │
│  │  TIER 1: HuggingFace Model          │                                   │
│  │  mitulshah/global-financial-        │                                   │
│  │  transaction-classifier             │                                   │
│  │  (Local, Free, ~267MB)              │                                   │
│  └─────────────────────────────────────┘                                   │
│          │                                                                  │
│          ├── Confidence ≥ 70% ────────────────────▶ ✅ Save Category       │
│          │                                          ai_source: "huggingface"│
│          │                                                                  │
│          ▼ (Confidence < 70%)                                              │
│  ┌─────────────────────────────────────┐                                   │
│  │  TIER 2: Gemini API                 │                                   │
│  │  (Fallback for edge cases)          │                                   │
│  │  (Cloud, ~$0.01 per call)           │                                   │
│  └─────────────────────────────────────┘                                   │
│          │                                                                  │
│          ├── Confidence ≥ 50% ────────────────────▶ ✅ Save Category       │
│          │                                          ai_source: "gemini"     │
│          │                                                                  │
│          ▼ (Confidence < 50%)                                              │
│  ┌─────────────────────────────────────┐                                   │
│  │  TIER 3: Unknown Category           │                                   │
│  │  (User needs to manually categorize)│                                   │
│  └─────────────────────────────────────┘                                   │
│          │                                                                  │
│          ▼                                                                  │
│  ┌─────────────────────────────────────┐                                   │
│  │  Notification: "category_updated"   │                                   │
│  │  (If marked Unknown)                │                                   │
│  └─────────────────────────────────────┘                                   │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  User Override Flow:                                                        │
│  ┌─────────────────────────────────────┐                                   │
│  │  User manually changes category     │                                   │
│  └─────────────────────────────────────┘                                   │
│          │                                                                  │
│          ▼                                                                  │
│  • is_user_override = TRUE                                                  │
│  • original_category_id = previous category                                 │
│  • ai_source = "user"                                                       │
│  • ai_confidence = 1.0                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### Category Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/categories` | List all categories | Required |
| GET | `/api/categories/{id}` | Get single category | Required |

**Response Example:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid-here",
            "name": "Food & Dining",
            "description": "Restaurants, groceries, fast food...",
            "transaction_type": "expense",
            "display_order": 1
        }
    ]
}
```

---

### Notification Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/notifications` | Get all notifications for current user | Required |
| GET | `/api/notifications/{id}` | Get single notification | Required |
| PATCH | `/api/notifications/{id}/read` | Mark notification as read | Required |
| PATCH | `/api/notifications/read-all` | Mark all as read | Required |
| DELETE | `/api/notifications/{id}` | Delete notification | Required |

**Query Parameters for GET `/api/notifications`:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | all | Filter: "unread", "read", or "all" |
| `type` | string | all | Filter by notification type |
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 100) |

**Response Example:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid-here",
            "type": "new_transaction",
            "status": "unread",
            "message": "New transaction: -$50.00 at Starbucks",
            "metadata": {
                "transaction_id": "txn-uuid-here"
            },
            "created_at": "2026-01-06T10:30:00Z"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 5,
        "total_pages": 1,
        "unread_count": 3
    }
}
```

---

### Transaction Endpoints (Enhanced)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/transactions` | Get all transactions for current user | Required |
| POST | `/api/transactions` | Create transaction (triggers AI categorization) | Required |
| PATCH | `/api/transactions/{id}/category` | Override transaction category | Required |

**POST `/api/transactions` Request:**
```json
{
    "amount": 50.00,
    "transaction_type": "expense",
    "date": "2026-01-06",
    "merchant_name": "McDonald's #1234",
    "description": "Lunch"
}
```

**POST `/api/transactions` Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid-here",
        "amount": 50.00,
        "transaction_type": "expense",
        "date": "2026-01-06",
        "merchant_name": "McDonald's #1234",
        "category": {
            "id": "category-uuid",
            "name": "Food & Dining"
        },
        "ai_confidence": 0.95,
        "ai_source": "huggingface",
        "is_user_override": false
    }
}
```

**PATCH `/api/transactions/{id}/category` Request:**
```json
{
    "category_id": "new-category-uuid"
}
```

---

### Spending Summary Endpoints (For AI Summary Feature)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/summary/daily` | Daily spending summary | Required |
| GET | `/api/summary/weekly` | Weekly spending summary | Required |
| GET | `/api/summary/monthly` | Monthly spending summary | Required |
| GET | `/api/summary/yearly` | Yearly spending summary | Required |
| GET | `/api/summary/ytd` | Year-to-date summary | Required |

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date` | string | today | Reference date (YYYY-MM-DD) |

**Response Example (Weekly):**
```json
{
    "success": true,
    "data": {
        "period": "weekly",
        "start_date": "2025-12-30",
        "end_date": "2026-01-05",
        "totals": {
            "income": 2500.00,
            "expense": 850.00,
            "net": 1650.00
        },
        "transaction_count": {
            "income": 2,
            "expense": 15
        },
        "by_category": [
            {
                "category": "Food & Dining",
                "amount": 250.00,
                "count": 8,
                "percentage": 29.4
            },
            {
                "category": "Transportation",
                "amount": 150.00,
                "count": 4,
                "percentage": 17.6
            },
            {
                "category": "Unknown",
                "amount": 50.00,
                "count": 2,
                "percentage": 5.9,
                "flagged": true
            }
        ]
    }
}
```

---

## 📁 Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `backend/app/models/category.py` | Category SQLAlchemy model |
| `backend/app/models/notification.py` | Notification SQLAlchemy model |
| `backend/app/schemas/category_schema.py` | Category Marshmallow schema |
| `backend/app/schemas/notification_schema.py` | Notification Marshmallow schema |
| `backend/app/services/category_service.py` | Category business logic |
| `backend/app/services/notification_service.py` | Notification business logic |
| `backend/app/services/summary_service.py` | Spending summary calculations |
| `backend/app/api/routes/categories.py` | Category API endpoints |
| `backend/app/api/routes/notifications.py` | Notification API endpoints |
| `backend/app/api/routes/summary.py` | Summary API endpoints |
| `backend/app/ai/__init__.py` | AI module init |
| `backend/app/ai/categorizer.py` | AI categorization service (HF + Gemini) |
| `backend/migrations/versions/xxx_sprint2_categories_notifications.py` | Database migration |

### Modified Files

| File | Changes |
|------|---------|
| `backend/app/models/__init__.py` | Export Category, Notification |
| `backend/app/models/enums.py` | Add NotificationType, NotificationStatus enums |
| `backend/app/models/transaction.py` | Add category_id, ai_confidence, ai_source, is_user_override, original_category_id |
| `backend/app/schemas/__init__.py` | Export new schemas |
| `backend/app/services/__init__.py` | Export new services |
| `backend/app/api/__init__.py` | Register new blueprints |
| `backend/requirements.txt` | Add torch, transformers, google-generativeai |

---

## 📦 New Dependencies

Add to `requirements.txt`:

```
# AI/ML - Transaction Categorization
torch>=2.0.0                  # PyTorch for HuggingFace model
transformers>=4.30.0          # HuggingFace transformers library
google-generativeai>=0.3.0    # Gemini API client

# Optional: For faster inference
accelerate>=0.20.0            # Speed up model loading
```

**Estimated additional requirements size:** ~500MB (mostly PyTorch)

---

## 🚀 Implementation Phases

### Phase 1: Database Foundation (Sprint 2 - Week 1) ✅ COMPLETE
**Goal:** Create tables and basic CRUD

| Task | Effort | Status |
|------|--------|--------|
| Create `categories` model | 1 hr | ✅ Done |
| Create `notifications` model | 1 hr | ✅ Done |
| Modify `transactions` model | 1 hr | ✅ Done |
| Create migration | 30 min | ✅ Done |
| Seed category data | 30 min | ✅ Done |
| Create schemas (category, notification) | 1 hr | ✅ Done |
| Create services (category, notification) | 2 hr | ✅ Done |
| Create API routes (categories, notifications) | 2 hr | ✅ Done |
| Unit tests | 2 hr | ✅ Done (21 tests) |

**Deliverable:** ✅ Working API endpoints for categories and notifications

---

### Phase 2: AI Integration (Sprint 2 - Week 2) ⏳ PENDING
**Goal:** Integrate HuggingFace model and Gemini fallback

| Task | Effort | Status |
|------|--------|--------|
| Download/setup HuggingFace model | 1 hr | ⏳ Pending |
| Create `categorizer.py` service | 3 hr | ⏳ Pending |
| Integrate with transaction creation | 2 hr | ⏳ Pending |
| Setup Gemini API client | 1 hr | ⏳ Pending |
| Implement fallback logic | 2 hr | ⏳ Pending |
| Add user override functionality | 1 hr | ⏳ Pending |
| Integration tests | 2 hr | ⏳ Pending |

**Deliverable:** Auto-categorization working on transaction creation

---

### Phase 3: Spending Summaries (Sprint 2/3) ✅ FOUNDATION COMPLETE
**Goal:** Implement summary endpoints for AI insights

| Task | Effort | Status |
|------|--------|--------|
| Create `summary_service.py` | 3 hr | ✅ Done |
| Create summary routes | 2 hr | ✅ Done |
| Optimize queries (indexes) | 1 hr | ⏳ Pending |
| Add caching (optional) | 1 hr | ⏳ Optional |
| Integration tests | 2 hr | ✅ Done |

**Deliverable:** ✅ Working summary endpoints (daily, weekly, monthly, yearly, YTD)

---

## 🔗 Frontend Integration Points

### For Frontend Team

**1. Categories API**
- Fetch categories for dropdowns: `GET /api/categories`
- Categories are static (seeded), no CRUD needed from frontend

**2. Notifications API**
- Fetch notifications: `GET /api/notifications?status=unread`
- Mark as read: `PATCH /api/notifications/{id}/read`
- Badge count: Use `meta.unread_count` from response

**3. Transactions API**
- Create transaction: `POST /api/transactions`
  - Backend auto-categorizes, returns `category` object
- Override category: `PATCH /api/transactions/{id}/category`
- Display `ai_confidence` as confidence indicator (optional)

**4. Summary API**
- Dashboard widgets: `GET /api/summary/weekly`
- Charts: Use `by_category` array for pie/bar charts

---

## ⚠️ Open Questions for Team Discussion

1. **Model Hosting:** Should HuggingFace model run on:
   - Same server as API? (simpler, but 267MB memory)
   - Separate microservice? (scalable, but more complex)

2. **Gemini API Key:** Who provides and manages the API key?
   - Store in environment variable: `GEMINI_API_KEY`

3. **Notification Delivery:**
   - Polling (frontend fetches periodically)?
   - WebSocket (real-time push)?
   - For Sprint 2, recommend polling (simpler)

4. **Category Changes:**
   - Can admin add new categories later?
   - For Sprint 2, recommend fixed 11 categories

5. **Migration Strategy:**
   - Existing transactions without category: backfill with AI?
   - Or leave as NULL and let users categorize?

---

## ✅ Acceptance Criteria

### AI Categorization
- [ ] Transaction creation auto-categorizes using HuggingFace model *(Pending - Phase 2)*
- [ ] Confidence < 70% falls back to Gemini *(Pending - Phase 2)*
- [ ] Confidence < 50% marks as "Unknown" *(Pending - Phase 2)*
- [x] User can override category *(Foundation Ready)*
- [x] Override sets `is_user_override = true` *(Model field exists)*

### Notifications
- [x] API returns all notifications for authenticated user
- [x] Can filter by status (unread/read)
- [x] Can mark individual notification as read
- [x] Can mark all notifications as read
- [x] Returns unread count in response meta

### Categories
- [x] 11 categories seeded on first migration
- [x] API returns all categories
- [x] Categories linked to transactions via foreign key

### Spending Summaries
- [x] Daily/weekly/monthly/yearly/YTD endpoints work
- [x] Returns totals (income, expense, net)
- [x] Returns breakdown by category
- [x] Flags "Unknown" category items

### Alerts (Foundation)
- [x] Alert model and schema created
- [x] CRUD endpoints for alerts
- [ ] Automatic anomaly detection triggers *(Pending - requires AI)*

---

## 📅 Timeline

| Phase | Start | End | Status |
|-------|-------|-----|--------|
| Phase 1: Database Foundation | Week 1 | Week 1 | ✅ **COMPLETE** |
| Phase 2: AI Integration | Week 2 | Week 2 | ⏳ Pending |
| Phase 3: Spending Summaries | Week 2-3 | Week 3 | ✅ **COMPLETE** (Foundation) |

---

## 📝 Notes

- This plan focuses on **backend foundation** only
- AI model fine-tuning is **out of scope** for Sprint 2
- Frontend notification UI handled by frontend team
- Cybersecurity review needed before production
- **UPDATE:** Phase 1 and Phase 3 Foundation complete - AI integration (Phase 2) is next

---

**Document Version:** 1.1
**Last Updated:** Sprint 2 Foundation Complete
**Next Step:** AI Integration (HuggingFace + Gemini)
