# Data Generators Package

Modular test data generation system for the Digital Finance Tracker.

## Overview

This package provides specialized generators that create realistic financial data for testing. Each generator is responsible for a specific domain (transactions, budgets, notifications, etc.) and can be used independently or orchestrated together.

## Architecture

```
data_generators/
├── __init__.py          # Package exports
├── base.py              # BaseGenerator - shared utilities
├── recurring.py         # RecurringGenerator - rent, utilities, subscriptions
├── income.py            # IncomeGenerator - salary, freelance, refunds
├── daily_spending.py    # DailySpendingGenerator - everyday purchases
├── anomalies.py         # AnomalyGenerator - edge cases for AI testing
├── ai_sessions.py       # AISessionGenerator - chat conversations
├── budgets.py           # BudgetGenerator - category budgets
├── notifications.py     # NotificationGenerator - various notification types
├── alerts.py            # AlertGenerator - budget/anomaly/recurring alerts
├── loans.py             # LoanGenerator - loans with payment history
├── jae_generator.py     # JaeDataGenerator - orchestrator for Jae's account
└── README.md            # This file
```

## Quick Start

### Generate Data for Jae Young Seo

```python
from tools.data_generators import JaeDataGenerator

# Get or create Jae's user record
user = JaeDataGenerator.get_or_create_jae_user(db.session)

# Generate all data (12 months)
generator = JaeDataGenerator(db_session=db.session, months_back=12)
results = generator.generate_all()

print(f"Generated {sum(results.values())} total records")
```

### Use Individual Generators

```python
from app.models import User, Category
from tools.data_generators import (
    RecurringGenerator,
    IncomeGenerator,
    DailySpendingGenerator,
)

# Get user and categories
user = User.query.filter_by(email="jaeyseo0922@gmail.com").first()
categories = Category.query.all()

# Generate recurring transactions
generator = RecurringGenerator(user=user, categories=categories, months_back=12)
count = generator.generate(db.session)
db.session.commit()

print(f"Created {count} recurring transactions")
```

## Generators

### BaseGenerator

Base class providing shared utilities:
- `get_category(name)` - Find category by name
- `get_date_days_ago(days)` - Calculate date from days ago
- `get_random_date_in_month(year, month)` - Random date in a month
- `stdout_write(msg, indent=0)` - Formatted console output

### RecurringGenerator

Creates predictable recurring transactions:
- **Rent**: $2,100/month (1st of each month)
- **Utilities**: $45-180/month based on season
- **Subscriptions**: Netflix, Spotify, gym, etc.
- **Insurance**: Car, renters policies

**Output**: ~212 transactions over 12 months

### IncomeGenerator

Creates income transactions:
- **Salary**: Bi-weekly payroll deposits ($3,450)
- **Freelance**: Occasional side income
- **Refunds**: Random refunds throughout the year

**Output**: ~49 transactions over 12 months

### DailySpendingGenerator

Creates realistic daily purchases with patterns:
- **Weekday patterns**: Morning coffee, lunch, commute
- **Weekend patterns**: Dining out, entertainment
- **Categories**: Food, shopping, transportation, entertainment

**Output**: ~1,450+ transactions over 12 months

### AnomalyGenerator

Creates edge cases for AI anomaly detection:
- Luxury purchases (Louis Vuitton, Rolex)
- Medical emergencies
- Duplicate transactions
- Late night purchases
- Legal/unusual categories
- Multiple same-day transactions
- Micro-transactions
- Round number patterns
- Foreign transactions

**Output**: 42 anomaly transactions

### AISessionGenerator

Creates realistic chat conversations covering 24 intents:

| Intent Category | Intents |
|-----------------|---------|
| Summary/Analysis | `get_summary`, `get_spending`, `category_breakdown` |
| Budgets | `budget_check`, `budget_suggestion`, `budget_set` |
| Transactions | `find_transactions`, `explain_transaction` |
| AI Detection | `anomaly_detection`, `recurring_detection` |
| Loans | `loan_status`, `loan_payoff` |
| Goals | `savings_goal`, `financial_health` |
| Meta | `greeting`, `help_request`, `clarification_needed` |

**Output**: 25 chat sessions

### BudgetGenerator

Creates category-based budgets:
- Monthly budgets for all expense categories
- Varying amounts based on realistic spending

**Output**: 13 budgets

### NotificationGenerator

Creates various notification types:
- **AI Insights**: Analysis results
- **Alerts**: Budget warnings, anomaly alerts
- **Budget**: Approaching/exceeded notifications
- **Transactions**: Large transaction alerts
- **System**: App tips and updates

**Output**: 46 notifications

### AlertGenerator

Creates detailed alerts:
- Budget warnings (approaching 80-95%)
- Budget exceeded (over 100%)
- Anomaly alerts (large transactions, unusual patterns)
- Recurring pattern alerts

**Output**: 16 alerts

### LoanGenerator

Creates loans with payment history:
- Car loan: $18,500 @ 4.9% (48 months)
- Student loan: $32,000 @ 5.5% (120 months)
- Personal loan: $5,000 @ 8.9% (24 months)
- Credit card: $2,500 @ 21.99% (12 months)

Each loan includes payment transactions in Financial Services category.

**Output**: 4 loans + payment transactions

## Testing

### Unit Tests

```bash
cd backend
python tools/test_data_generators.py
```

Tests all generators with mock objects (no database required).

### Integration Tests

```bash
# Start Docker first
docker compose up -d postgres_db redis_cache

# Run integration test
cd backend
python tools/test_integration.py
```

Tests against real Docker database.

## CLI Usage

```bash
# Populate database with Jae's quality data
python tools/populate_db.py --jae-quality-data

# Clear Jae's data first, then repopulate
python tools/populate_db.py --jae-quality-data --clear-jae
```

## Data Summary

For Jae Young Seo's account (12 months):

| Entity | Count |
|--------|-------|
| Transactions | ~1,757 |
| AI Sessions | 25 |
| Budgets | 13 |
| Notifications | 46 |
| Alerts | 16 |
| Loans | 4 |
| **Total** | **~1,861** |

## Extending

To add a new generator:

1. Create a new file in `data_generators/`
2. Inherit from `BaseGenerator`
3. Implement `generate(db_session) -> int`
4. Export in `__init__.py`
5. Add to `JaeDataGenerator.generate_all()` if needed
6. Add unit test in `test_data_generators.py`

Example:

```python
from .base import BaseGenerator

class MyGenerator(BaseGenerator):
    """Generate custom test data."""

    def generate(self, db_session) -> int:
        count = 0
        # Generate records...
        db_session.add(record)
        count += 1
        return count
```
