# =============================================================================
# Digital Finance Tracker - AI Sessions Generator
# PURPOSE: Generate comprehensive AI chat session conversations
# =============================================================================
"""
AI Sessions Generator

Generates rich AI chat sessions covering all user intents for testing:
- Spending queries (category breakdown, comparisons)
- Transaction creation flows
- Budget status checks
- Anomaly alerts
- Recurring detection
- Savings planning
- Year-over-year analysis
- Help/onboarding

Sessions cover multi-turn conversations with realistic responses.
"""

from datetime import timedelta
from typing import List, Dict, Any, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class AISessionGenerator(BaseGenerator):
    """
    Generator for AI chat session conversations.

    Creates comprehensive AI sessions covering all possible
    user intents and conversation patterns.
    """

    def _build_conversations(self) -> List[Dict[str, Any]]:
        """Build all conversation templates."""
        now = self.now

        return [
            # Session 1: Budget inquiry with follow-ups
            {
                "intent": "query_spending",
                "days_ago": 28,
                "messages": [
                    ("user", "How much have I spent on food this month?"),
                    ("assistant", "You've spent $687.32 on Food & Dining this month across 42 transactions. Your top merchants are:\n\n1. Trader Joe's: $245.00 (5 visits)\n2. DoorDash: $178.50 (8 orders)\n3. Starbucks: $89.50 (15 visits)\n4. Chipotle: $72.00 (5 visits)"),
                    ("user", "Is that more than last month?"),
                    ("assistant", "Yes, last month you spent $512.50 on Food & Dining. That's a 34% increase ($174.82 more). The biggest increase is in delivery services - DoorDash spending is up 85% from last month. Would you like me to set a budget alert for this category?"),
                    ("user", "Yes, set an alert at $600"),
                    ("assistant", "Done! I've set a budget alert for Food & Dining at $600/month. You'll be notified when you reach 80% ($480) and 100% ($600) of your budget. You're currently at 114% of this new limit."),
                ],
            },
            # Session 2: Transaction creation flow
            {
                "intent": "create_transaction",
                "days_ago": 14,
                "messages": [
                    ("user", "Add a $245 expense at Best Buy for a new monitor"),
                    ("assistant", "I'll create this transaction for you:\n\n**Amount:** $245.00\n**Merchant:** Best Buy\n**Category:** Shopping & Retail (suggested)\n**Date:** Today\n\nShould I categorize this as 'Shopping & Retail' or would you prefer a different category?"),
                    ("user", "Actually put it under Entertainment since it's for gaming"),
                    ("assistant", "Got it! I've created the transaction:\n\n✓ **$245.00** at Best Buy\n✓ Category: Entertainment & Recreation\n✓ Date: January 22, 2026\n\nYour Entertainment spending this month is now $412.50. You have $87.50 remaining in your Entertainment budget."),
                ],
            },
            # Session 3: Monthly summary request
            {
                "intent": "monthly_summary",
                "days_ago": 10,
                "messages": [
                    ("user", "Give me a complete summary of my finances this month"),
                    ("assistant", "Here's your January 2026 Financial Summary:\n\n💰 **INCOME**\nTotal: $6,785.00\n- Salary: $6,500.00 (2 deposits)\n- Freelance: $285.00\n\n📊 **EXPENSES**\nTotal: $3,892.45\n\n**By Category:**\n1. Rent & Utilities: $2,085.00 (53.6%)\n2. Food & Dining: $687.32 (17.7%)\n3. Transportation: $312.50 (8.0%)\n4. Shopping: $423.00 (10.9%)\n5. Entertainment: $245.00 (6.3%)\n6. Healthcare: $139.63 (3.6%)\n\n💵 **NET SAVINGS**\n$2,892.55 (42.6% savings rate)\n\n📈 **TRENDS**\n- Total spending up 12% from December\n- Delivery food up 85% (consider cooking more?)\n- Transportation down 15% (good job!)"),
                    ("user", "How does that compare to my 3-month average?"),
                    ("assistant", "Here's your 3-month comparison:\n\n| Category | Jan 2026 | 3-Mo Avg | Difference |\n|----------|----------|----------|------------|\n| Food | $687 | $545 | +26% 🔴 |\n| Transport | $312 | $368 | -15% 🟢 |\n| Shopping | $423 | $389 | +9% 🟡 |\n| Entertainment | $245 | $198 | +24% 🔴 |\n| Utilities | $2,085 | $2,042 | +2% ⚪ |\n\n**Key Insights:**\n- Your Food spending is trending up - mainly delivery\n- Great job reducing Transportation costs!\n- Consider reviewing subscription services ($72/mo total)"),
                ],
            },
            # Session 4: Anomaly detection alert
            {
                "intent": "anomaly_alert",
                "days_ago": 5,
                "messages": [
                    ("assistant", "⚠️ **Unusual Activity Detected**\n\nI noticed some transactions that seem out of pattern:\n\n1. **Louis Vuitton** - $2,450.00 (3 days ago)\n   This is 15x your average shopping transaction\n\n2. **Multiple gas stations on same day** (15 days ago)\n   3 gas purchases totaling $165.00\n\nAre these transactions legitimate?"),
                    ("user", "Yes the Louis Vuitton was a birthday gift for my wife and the gas was a road trip with friends"),
                    ("assistant", "Thanks for confirming! I've marked both as verified. I've also updated your spending patterns:\n\n- Added 'occasional luxury purchase' to your profile\n- Road trip expenses noted as one-time event\n\nWould you like me to exclude these from your regular spending analysis?"),
                    ("user", "Yes please"),
                    ("assistant", "Done! These transactions are now tagged as 'special occasions' and won't skew your regular spending averages. Your adjusted monthly spending (excluding one-time events) is $1,442.45."),
                ],
            },
            # Session 5: Category breakdown request
            {
                "intent": "query_spending",
                "days_ago": 20,
                "messages": [
                    ("user", "Break down my transportation costs"),
                    ("assistant", "Here's your Transportation breakdown for the last 30 days:\n\n🚗 **Total: $312.50**\n\n**By Type:**\n- Gas: $165.00 (52.8%)\n  - Shell: $85.00 (2 fill-ups)\n  - Chevron: $80.00 (2 fill-ups)\n- Rideshare: $95.00 (30.4%)\n  - Uber: $62.00 (4 rides)\n  - Lyft: $33.00 (2 rides)\n- Public Transit: $45.00 (14.4%)\n  - BART: $45.00 (12 trips)\n- Parking: $7.50 (2.4%)\n\n📈 **Insights:**\n- You average $4.50 per BART trip\n- Uber rides average $15.50 each\n- Gas costs ~$42.50 per fill-up"),
                    ("user", "Am I spending less on Uber than before?"),
                    ("assistant", "Yes! Your Uber spending has decreased:\n\n- This month: $62.00 (4 rides)\n- Last month: $145.00 (9 rides)\n- 2 months ago: $178.00 (12 rides)\n\nThat's a 65% reduction over 2 months! Looks like you're using BART more instead. At current rates, you're saving about $115/month. Great optimization! 🎉"),
                ],
            },
            # Session 6: Recurring transaction inquiry
            {
                "intent": "recurring_detection",
                "days_ago": 16,
                "messages": [
                    ("user", "What recurring charges do I have?"),
                    ("assistant", "I've identified 18 recurring charges in your account:\n\n**Subscriptions ($82.94/mo):**\n- Netflix: $15.99 (5th of month)\n- Spotify: $10.99 (8th)\n- Disney+: $13.99 (12th)\n- YouTube Premium: $13.99 (15th)\n- HBO Max: $15.99 (18th)\n- Amazon Prime: $14.99 (20th)\n\n**Memberships ($24.99/mo):**\n- Planet Fitness: $24.99 (1st)\n\n**Bills ($2,407.49/mo):**\n- Rent: $1,850.00 (1st)\n- PG&E: ~$127.50 (3rd, varies)\n- Comcast: $89.99 (7th)\n- AT&T Wireless: $95.00 (10th)\n- Water: $45.00 (15th)\n- Trash: $35.00 (20th)\n- Kaiser Insurance: $350.00 (1st)\n\n**Financial ($955.00/mo):**\n- Chase CC Payment: $500.00 (25th)\n- Car Insurance: $145.00 (18th)\n- Student Loan: $285.00 (15th)\n- Renters Insurance: $25.00 (5th)\n\n**Monthly Total: $3,470.42**"),
                    ("user", "Cancel Disney+ and YouTube Premium"),
                    ("assistant", "I can't directly cancel subscriptions, but here's how:\n\n**Disney+ ($13.99/mo):**\n→ disneyplus.com/account → Subscription → Cancel\n\n**YouTube Premium ($13.99/mo):**\n→ youtube.com/paid_memberships → Manage → Cancel\n\n**Potential Savings:** $27.98/month ($335.76/year)\n\nWant me to remind you to check these are cancelled next month?"),
                ],
            },
            # Session 7: Loan inquiry
            {
                "intent": "loan_status",
                "days_ago": 22,
                "messages": [
                    ("user", "What's the status of my car loan?"),
                    ("assistant", "Here's your Car Loan summary:\n\n🚗 **Geico Auto Financing**\n\n| Metric | Value |\n|--------|-------|\n| Original Amount | $18,500.00 |\n| Remaining Balance | $12,340.00 |\n| Monthly Payment | $425.00 |\n| Interest Rate | 4.9% APR |\n| Payments Made | 18 of 48 |\n| Next Payment Due | Feb 18, 2026 |\n\n📊 **Progress:**\n[████████░░░░░░░░░░░░] 33% paid off\n\n💡 **Tip:** If you pay an extra $100/month, you'd:\n- Pay off 8 months early\n- Save $485 in interest"),
                ],
            },
            # Session 8: Multi-turn savings plan
            {
                "intent": "complex_analysis",
                "days_ago": 4,
                "messages": [
                    ("user", "I want to save more money. What should I cut?"),
                    ("assistant", "Let me analyze your spending for savings opportunities:\n\n**🎯 Quick Wins (Easy to reduce):**\n\n1. **Food Delivery** → Save $100-150/mo\n   - Current: $178.50/mo (DoorDash, UberEats)\n   - Suggestion: Limit to 2x/week max\n\n2. **Coffee Shops** → Save $50-70/mo\n   - Current: $89.50/mo (Starbucks, Peet's)\n   - Suggestion: Brew at home 3 days/week\n\n3. **Streaming Services** → Save $28/mo\n   - Overlap detected: Disney+ AND Netflix\n   - Unused?: YouTube Premium (low activity)\n\n**💪 Medium Effort:**\n\n4. **Rideshare → BART** → Save $60-80/mo\n   - Already improving! Keep it up.\n\n5. **Groceries optimization** → Save $40-60/mo\n   - Whole Foods → Trader Joe's for basics\n\n**Potential Total Savings: $278-388/month**\n\nWant me to create a savings plan?"),
                    ("user", "Yes, create a realistic plan for saving $300/month"),
                    ("assistant", "Here's your personalized $300/month savings plan:\n\n**🎯 THE $300 SAVINGS CHALLENGE**\n\n**Week 1-2: Quick Wins ($128/mo)**\n□ Cancel YouTube Premium: +$14\n□ Cancel Disney+: +$14\n□ Coffee at home M/W/F: +$50\n□ Limit DoorDash to 2x/week: +$50\n\n**Week 3-4: Build Habits ($172/mo)**\n□ Pack lunch 3x/week: +$60\n□ Use BART instead of Uber for commute: +$50\n□ Grocery shop at Trader Joe's: +$35\n□ Cancel unused subscriptions: +$27\n\n**TRACKING:**\nI'll send you weekly progress updates and celebrate milestones!\n\n**Month 1 Goal:** $250 saved\n**Month 2 Goal:** $300 saved\n**Month 3+ Goal:** $300+ maintained\n\nShould I set up automatic tracking for these goals?"),
                    ("user", "Yes please"),
                    ("assistant", "You're all set! Here's what I've configured:\n\n✓ Weekly spending summary every Sunday\n✓ Alerts when approaching limits:\n  - Coffee: $40/mo (was $90)\n  - Food delivery: $80/mo (was $180)\n✓ Monthly savings report on the 1st\n✓ Celebration notifications at milestones\n\n**Your first target:** Save $75 this week\n\nI'll check in with you on Sunday with your progress. You've got this! 💪"),
                ],
            },
            # Session 9: Quick spending check
            {
                "intent": "quick_query",
                "days_ago": 2,
                "messages": [
                    ("user", "Did I spend anything at Amazon this week?"),
                    ("assistant", "Yes, you made 3 Amazon purchases this week:\n\n1. Feb 3: $45.99 - Shopping & Retail\n2. Feb 1: $23.50 - Shopping & Retail\n3. Jan 31: $89.99 - Shopping & Retail\n\n**Total: $159.48**\n\nThis is higher than your weekly average of $62.00. Would you like to see what you bought?"),
                ],
            },
            # Session 10: Budget status check
            {
                "intent": "budget_status",
                "days_ago": 8,
                "messages": [
                    ("user", "How are my budgets looking?"),
                    ("assistant", "Here's your February budget status:\n\n| Category | Budget | Spent | Remaining | Status |\n|----------|--------|-------|-----------|--------|\n| Food & Dining | $600 | $687 | -$87 | 🔴 Over |\n| Shopping | $400 | $423 | -$23 | 🔴 Over |\n| Entertainment | $300 | $245 | $55 | 🟢 OK |\n| Transportation | $400 | $312 | $88 | 🟢 OK |\n| Utilities | $2,200 | $2,085 | $115 | 🟢 OK |\n\n**Summary:**\n- 2 of 5 budgets exceeded\n- Total over-budget: $110\n- Days remaining: 23\n\n⚠️ **Alert:** Food budget exceeded by 14%. Consider meal prepping this weekend to get back on track."),
                ],
            },
            # Session 11: Year-over-year comparison
            {
                "intent": "year_comparison",
                "days_ago": 35,
                "messages": [
                    ("user", "Compare my spending to this time last year"),
                    ("assistant", "Here's your year-over-year spending comparison (Jan-Feb):\n\n| Category | 2025 | 2026 | Change |\n|----------|------|------|--------|\n| Food & Dining | $1,089 | $1,232 | +13% |\n| Transportation | $756 | $624 | -17% |\n| Shopping | $834 | $912 | +9% |\n| Entertainment | $423 | $456 | +8% |\n| Utilities | $4,012 | $4,127 | +3% |\n| Healthcare | $312 | $289 | -7% |\n\n**Key Changes:**\n📈 Food spending up (more delivery usage)\n📉 Transportation down (more WFH?)\n📈 Overall spending: +5% YoY\n\n**Income Comparison:**\n- 2025: $12,500\n- 2026: $13,570 (+8.6%)\n\n💡 Your income grew faster than spending - nice work!"),
                ],
            },
            # Session 12: Help/onboarding session
            {
                "intent": "help",
                "days_ago": 60,
                "messages": [
                    ("user", "What can you help me with?"),
                    ("assistant", "I'm your AI financial assistant! Here's what I can do:\n\n**💬 Ask me anything like:**\n\n📊 **Spending Analysis**\n- \"How much did I spend on food?\"\n- \"What's my biggest expense category?\"\n- \"Compare this month to last month\"\n\n➕ **Add Transactions**\n- \"Add $50 expense at Target\"\n- \"Log a $3000 paycheck\"\n- \"I spent $25 on groceries today\"\n\n📈 **Budgets & Goals**\n- \"What's my budget status?\"\n- \"Help me save $500 this month\"\n- \"Set a $200 entertainment budget\"\n\n🔄 **Recurring & Patterns**\n- \"What subscriptions do I have?\"\n- \"Show my recurring bills\"\n- \"Find duplicate charges\"\n\n🎯 **Insights & Tips**\n- \"How can I save more money?\"\n- \"Analyze my spending patterns\"\n- \"What's my savings rate?\"\n\nJust type naturally - I understand context! Try asking about your recent spending to get started."),
                ],
            },
            # Session 13: Bill reminder conversation
            {
                "intent": "bill_reminder",
                "days_ago": 12,
                "messages": [
                    ("user", "When are my bills due this week?"),
                    ("assistant", "Here are your upcoming bills for the next 7 days:\n\n📅 **This Week's Bills:**\n\n| Due Date | Bill | Amount | Status |\n|----------|------|--------|--------|\n| Feb 7 | Comcast | $89.99 | 🟡 Due Soon |\n| Feb 8 | Spotify | $10.99 | 🟡 Due Soon |\n| Feb 10 | AT&T | $95.00 | ⚪ Upcoming |\n\n**Total Due:** $195.98\n\n💡 You have $2,450.00 in your checking account - plenty to cover these.\n\nWant me to remind you the day before each is due?"),
                    ("user", "Yes, and also tell me about next week"),
                    ("assistant", "I'll send reminders the day before. Here's next week (Feb 11-17):\n\n📅 **Next Week's Bills:**\n\n| Due Date | Bill | Amount |\n|----------|------|--------|\n| Feb 12 | Disney+ | $13.99 |\n| Feb 15 | Water Utility | $45.00 |\n| Feb 15 | Student Loan | $285.00 |\n| Feb 15 | YouTube Premium | $13.99 |\n\n**Total Due:** $357.98\n\n⚠️ **Note:** Feb 15th is a busy day - 3 payments totaling $343.99. Make sure sufficient funds are available."),
                ],
            },
            # Session 14: Investment inquiry
            {
                "intent": "investment_query",
                "days_ago": 45,
                "messages": [
                    ("user", "How much could I invest if I saved better?"),
                    ("assistant", "Based on your spending patterns, here's your investment potential:\n\n**Current Situation:**\n- Monthly Income: ~$6,500\n- Monthly Expenses: ~$3,900\n- Current Savings Rate: 40%\n\n**If you optimize spending:**\n\n| Scenario | Monthly Savings | Investable |\n|----------|----------------|------------|\n| Current | $2,600 | $2,000 |\n| Cut $300/mo | $2,900 | $2,300 |\n| Cut $500/mo | $3,100 | $2,500 |\n\n**10-Year Projection (7% return):**\n- $2,000/mo → $347,000\n- $2,300/mo → $400,000\n- $2,500/mo → $434,000\n\nThat extra $300/mo in savings could mean an extra $53,000 in 10 years! 📈\n\nWant me to help identify where to cut $300-500?"),
                ],
            },
            # Session 15: Tax preparation help
            {
                "intent": "tax_help",
                "days_ago": 55,
                "messages": [
                    ("user", "Can you help me with tax deductions?"),
                    ("assistant", "I can help identify potentially deductible expenses! Here's what I found in your transactions:\n\n**💼 Potential Business Deductions:**\n(If you have freelance income)\n- Home office supplies: $245.00\n- Software subscriptions: $89.00\n- Professional memberships: $125.00\n\n**🏥 Medical Expenses:**\n- Kaiser Insurance: $4,200/year\n- Prescriptions: $312.00\n- Doctor visits: $175.00\n\n**🎁 Charitable Donations:**\n- Red Cross: $100.00\n- Local Food Bank: $50.00\n- GoFundMe donations: $75.00\n\n**📚 Education:**\n- Online courses: $299.00\n- Books: $125.00\n\n⚠️ **Disclaimer:** I'm not a tax professional. Please consult a CPA to confirm which expenses qualify.\n\nWant me to export these transactions for your tax preparer?"),
                ],
            },
            # Session 16: Goal tracking conversation
            {
                "intent": "goal_tracking",
                "days_ago": 7,
                "messages": [
                    ("user", "How am I doing on my savings goal?"),
                    ("assistant", "Here's your savings goal progress:\n\n**🎯 Emergency Fund Goal**\n- Target: $10,000\n- Current: $7,250\n- Progress: 72.5%\n\n[██████████████░░░░░░] 72.5%\n\n**Monthly Contributions:**\n- December: $800\n- January: $650\n- February (so far): $400\n\n**At current pace:** You'll reach your goal in ~4 months (June 2026)\n\n💡 **Tip:** If you increase monthly savings by $200, you'd hit it in just 2.5 months!"),
                    ("user", "What about my vacation fund?"),
                    ("assistant", "Here's your Vacation Fund status:\n\n**✈️ Hawaii Trip Fund**\n- Target: $3,500\n- Current: $1,875\n- Progress: 53.6%\n- Deadline: August 2026 (6 months)\n\n[██████████░░░░░░░░░░] 53.6%\n\n**Needed:** $270.83/month to hit target\n**Current pace:** $312/month\n\n✅ You're ahead of schedule! At this rate, you'll have $3,747 by August - enough for some extra spending money!"),
                ],
            },
            # Session 17: Fraud detection inquiry
            {
                "intent": "fraud_check",
                "days_ago": 3,
                "messages": [
                    ("user", "I don't recognize this $847 charge from TECHSHOP42"),
                    ("assistant", "⚠️ I'm taking this seriously. Let me analyze:\n\n**Transaction Details:**\n- Merchant: TECHSHOP42\n- Amount: $847.00\n- Date: Feb 2, 2026\n- Category: Shopping & Retail\n- Card ending: ****4523\n\n**My Analysis:**\n- ❌ This merchant has never appeared before\n- ❌ Amount is 8x your typical shopping transaction\n- ❌ Location data shows out-of-state (Nevada)\n- ❌ No similar online shopping pattern\n\n**Fraud Risk: HIGH** 🔴\n\n**Immediate Actions:**\n1. Contact your bank to dispute: 1-800-XXX-XXXX\n2. Request card replacement\n3. Review recent transactions\n\nShould I flag all transactions from the past week for review?"),
                    ("user", "Yes, and what else happened recently?"),
                    ("assistant", "I've flagged the week's transactions. Here's a detailed review:\n\n**📋 Past 7 Days Review:**\n\n✅ **Verified (known patterns):**\n- Trader Joe's: $78.50\n- Shell Gas: $45.00\n- Netflix: $15.99\n- Starbucks: $12.50\n\n⚠️ **Needs Review:**\n1. TECHSHOP42: $847.00 ← You reported\n2. ONLINE-STORE-321: $124.99 (same day)\n   - Also out-of-state, first time merchant\n\n🔴 **Recommendation:** You may have 2 fraudulent charges totaling $971.99. Contact your bank immediately.\n\nI've also:\n- Set up real-time alerts for any charge over $100\n- Flagged your account for enhanced monitoring\n- Created a report you can share with your bank"),
                ],
            },
            # Session 18: Spending limit and overspending alert
            {
                "intent": "overspending_alert",
                "days_ago": 6,
                "messages": [
                    ("assistant", "🚨 **Budget Alert!**\n\nYou've exceeded your Shopping budget:\n\n**Shopping & Retail**\n- Limit: $400.00\n- Spent: $523.00\n- Over by: $123.00 (30.8%)\n\n**Recent Shopping Transactions:**\n1. Target: $89.00 (Feb 1)\n2. Amazon: $156.00 (Jan 31)\n3. Best Buy: $245.00 (Jan 28)\n4. Nordstrom Rack: $33.00 (Jan 25)\n\n**Remaining days in month:** 23\n\nWould you like to:\n1. Adjust your budget temporarily\n2. Set purchase reminders\n3. Review and return items"),
                    ("user", "Can I adjust it to 500 just for this month?"),
                    ("assistant", "Done! I've updated your budget:\n\n**Shopping Budget Update:**\n- Previous limit: $400.00\n- New limit: $500.00 (February only)\n- Returns to $400.00 in March\n\n**Current Status:**\n- Spent: $523.00\n- New limit: $500.00\n- Still over by: $23.00\n\n💡 You're only $23 over now. Try to avoid shopping for the next week to get back on track.\n\nWant me to send you a reminder before any shopping purchase over $25?"),
                ],
            },
            # Session 19: Category recategorization learning
            {
                "intent": "category_correction",
                "days_ago": 18,
                "messages": [
                    ("user", "The Costco transaction should be groceries not shopping"),
                    ("assistant", "Got it! I've updated the transaction:\n\n**Before:**\n- Costco: $245.67 → Shopping & Retail\n\n**After:**\n- Costco: $245.67 → Groceries\n\n✅ Transaction recategorized!\n\n💡 **Learning Applied:**\nI noticed you shop at Costco frequently. Would you like me to:\n\n1. **Always categorize Costco as Groceries** (Recommended)\n2. **Split it** - Ask each time (some items might be household)\n3. **Keep as Shopping** - Just fix this one\n\nWhat would you prefer?"),
                    ("user", "Always as groceries"),
                    ("assistant", "Perfect! I've updated my learning:\n\n✅ **New Rule Created:**\nCostco transactions → Groceries (auto-apply)\n\n**Historical Update:**\nI found 8 other Costco transactions in the past 6 months. Would you like me to recategorize all of them to Groceries?\n\nThis would move $1,234.56 from 'Shopping' to 'Groceries' in your reports."),
                    ("user", "Yes do it"),
                    ("assistant", "Done! Here's what I updated:\n\n**8 Costco Transactions Recategorized:**\n\n| Date | Amount | Old Category | New Category |\n|------|--------|--------------|---------------|\n| Feb 1 | $245.67 | Shopping | Groceries ✓ |\n| Jan 15 | $178.90 | Shopping | Groceries ✓ |\n| Dec 28 | $145.00 | Shopping | Groceries ✓ |\n| Dec 12 | $198.45 | Shopping | Groceries ✓ |\n| Nov 25 | $165.32 | Shopping | Groceries ✓ |\n| Nov 8 | $134.56 | Shopping | Groceries ✓ |\n| Oct 22 | $89.00 | Shopping | Groceries ✓ |\n| Oct 5 | $77.66 | Shopping | Groceries ✓ |\n\n**Impact on Reports:**\n- Groceries monthly avg: ↑ $205.76\n- Shopping monthly avg: ↓ $205.76\n\nFuture Costco transactions will auto-categorize as Groceries."),
                ],
            },
            # Session 20: Subscription optimization
            {
                "intent": "subscription_review",
                "days_ago": 25,
                "messages": [
                    ("user", "Am I paying for anything I don't use?"),
                    ("assistant", "Let me analyze your subscription usage patterns:\n\n**📊 Subscription Activity Analysis:**\n\n**HIGH USAGE (Keep):**\n✅ Netflix: 45+ hours/month\n✅ Spotify: Daily usage detected\n✅ Amazon Prime: 12 orders last month\n\n**MEDIUM USAGE (Review):**\n🟡 Disney+: 8 hours last month\n🟡 HBO Max: 4 hours last month\n\n**LOW/NO USAGE (Consider Canceling):**\n🔴 YouTube Premium: $13.99/mo\n   - Last video watched: 6 weeks ago\n   - YouTube usage: mostly free content\n\n🔴 Adobe Creative Cloud: $54.99/mo\n   - No app opens in 3 months\n\n🔴 Headspace: $12.99/mo\n   - Last session: 4 months ago\n\n**Potential Monthly Savings: $81.97**\n**Potential Annual Savings: $983.64**\n\nWant me to show you how to cancel these?"),
                    ("user", "Cancel the Adobe subscription for sure"),
                    ("assistant", "Here's how to cancel Adobe Creative Cloud:\n\n**Adobe Creative Cloud Cancellation:**\n\n1. Go to: account.adobe.com\n2. Click 'Manage plan' → 'Cancel plan'\n3. Select cancellation reason\n4. Confirm cancellation\n\n⚠️ **Important Notes:**\n- Your billing date is the 15th\n- Cancel before Feb 14 to avoid next charge\n- You'll lose access to apps after billing period\n- Consider exporting any cloud files first\n\n**Alternative:** Adobe offers a photography plan for just $9.99/mo if you just need Photoshop/Lightroom.\n\nWant me to remind you on Feb 13 to cancel?"),
                ],
            },
            # Session 21: Weekly spending summary
            {
                "intent": "weekly_summary",
                "days_ago": 1,
                "messages": [
                    ("user", "How did I do this week?"),
                    ("assistant", "Here's your weekly spending recap (Jan 29 - Feb 4):\n\n**📊 WEEKLY SUMMARY**\n\n💸 **Total Spent:** $687.45\n(vs $542.30 last week: +27%)\n\n**By Category:**\n| Category | Amount | vs Avg |\n|----------|--------|--------|\n| Groceries | $156.78 | +5% |\n| Food & Dining | $124.50 | +45% 🔴 |\n| Transportation | $67.00 | -12% |\n| Shopping | $245.99 | +120% 🔴 |\n| Entertainment | $45.18 | Normal |\n| Bills | $48.00 | Normal |\n\n**🎯 Budget Status:**\n- 3 of 5 on track ✅\n- Food & Dining: 89% of monthly budget (careful!)\n- Shopping: 61% of monthly budget\n\n**💡 Key Insight:**\nShopping spike is from the Best Buy purchase. Excluding that, you're right on track!\n\n**Next Week Goal:** Keep food spending under $100"),
                ],
            },
            # Session 22: Payment reminder setup
            {
                "intent": "payment_setup",
                "days_ago": 30,
                "messages": [
                    ("user", "Help me never miss a bill payment"),
                    ("assistant", "Let's set up a bulletproof bill payment system! Here's what I recommend:\n\n**📅 Your Bill Calendar:**\n\n**Week 1 (1st-7th):**\n- Rent: $1,850 (1st)\n- Planet Fitness: $24.99 (1st)\n- Kaiser: $350 (1st)\n- PG&E: ~$127 (3rd)\n- Renters Insurance: $25 (5th)\n\n**Week 2 (8th-14th):**\n- Spotify: $10.99 (8th)\n- AT&T: $95 (10th)\n- Disney+: $13.99 (12th)\n\n**Week 3 (15th-21st):**\n- Student Loan: $285 (15th)\n- YouTube: $13.99 (15th)\n- Water: $45 (15th)\n- Car Insurance: $145 (18th)\n- HBO Max: $15.99 (18th)\n\n**Week 4 (22nd-31st):**\n- Amazon Prime: $14.99 (20th)\n- Trash: $35 (20th)\n- Chase CC: $500 (25th)\n\n**Setting up alerts:**\n- 3-day advance warning ⏰\n- Low balance alert if under $500\n- Confirmation after each payment\n\nShould I enable all these reminders?"),
                    ("user", "Yes enable them all"),
                    ("assistant", "All bill reminders are now active! Here's your confirmation:\n\n✅ **18 Bill Reminders Configured:**\n\n**Notification Settings:**\n- 📱 Push notification 3 days before\n- 📧 Email the day before\n- 🚨 Urgent alert on due date\n\n**Safety Nets:**\n- 💳 Low balance alert: When checking < $500\n- 📊 Weekly bill preview every Sunday\n- 🔔 Monthly summary on the 1st\n\n**This Month's Total Bills:** $3,470.42\n\nI'll send your first reminder on Feb 4th for your rent due on the 1st (wait, that already passed this month!).\n\nNext reminder: Feb 5th - PG&E due Feb 8th ($127)\n\nYou won't miss a bill again! 💪"),
                ],
            },
            # Session 23: Merchant spending analysis
            {
                "intent": "merchant_analysis",
                "days_ago": 40,
                "messages": [
                    ("user", "Where do I spend the most money?"),
                    ("assistant", "Here's your top merchants analysis (last 90 days):\n\n**🏆 TOP 10 MERCHANTS BY SPENDING:**\n\n| Rank | Merchant | Total | Transactions |\n|------|----------|-------|-------------|\n| 1 | Landlord (Rent) | $5,550 | 3 |\n| 2 | Chase (CC Payment) | $1,500 | 3 |\n| 3 | Kaiser | $1,050 | 3 |\n| 4 | Trader Joe's | $734 | 15 |\n| 5 | DoorDash | $534 | 28 |\n| 6 | Amazon | $489 | 12 |\n| 7 | Costco | $423 | 3 |\n| 8 | Shell | $340 | 8 |\n| 9 | Comcast | $270 | 3 |\n| 10 | Starbucks | $268 | 45 |\n\n**📊 Interesting Insights:**\n- Most visits: Starbucks (45 times!) @ $5.96 avg\n- Highest per-visit: Costco @ $141 avg\n- DoorDash sneaking up - $19 avg order x 28 = adds up!\n\n**💡 Optimization Tip:**\nStarbucks: $268 over 45 visits = brewing at home even half the time saves $134/quarter"),
                ],
            },
            # Session 24: Complex multi-intent query
            {
                "intent": "complex_query",
                "days_ago": 48,
                "messages": [
                    ("user", "Compare my restaurant spending vs groceries and tell me which is more cost effective"),
                    ("assistant", "Great question! Let me break down the cost-effectiveness:\n\n**📊 RESTAURANT vs GROCERIES ANALYSIS**\n(Last 3 months)\n\n**Restaurants/Takeout:**\n- Total: $1,650.00\n- Transactions: 67\n- Average meal: $24.63\n- Meals covered: ~67 (assuming 1 meal per transaction)\n- **Cost per meal: $24.63**\n\n**Groceries:**\n- Total: $987.54\n- Transactions: 18\n- Estimated meals (at home): ~180\n  (3 meals/day × 2 people × 30 days = normalized)\n- **Cost per meal: $5.49**\n\n**📈 Cost Comparison:**\n- Restaurant meal: $24.63\n- Home-cooked meal: $5.49\n- **Restaurants are 4.5x more expensive!**\n\n**💰 Potential Savings:**\nIf you replaced just 10 restaurant meals/month with cooking:\n- Monthly savings: $191\n- Annual savings: $2,292\n\n**🎯 Recommendation:**\n- Aim for 70/30 ratio (home/restaurant)\n- Current ratio: 50/50\n- Target: Cook 4 more meals per week\n\nWould you like meal prep tips to make this easier?"),
                ],
            },
            # Session 25: Income and cash flow analysis
            {
                "intent": "income_analysis",
                "days_ago": 15,
                "messages": [
                    ("user", "Analyze my income sources and cash flow"),
                    ("assistant", "Here's your complete income and cash flow analysis:\n\n**💵 INCOME SOURCES (Last 6 Months)**\n\n| Source | Monthly Avg | % of Total | Trend |\n|--------|-------------|------------|-------|\n| Primary Salary | $5,416 | 79.8% | Stable |\n| Freelance | $425 | 6.3% | ↑ Growing |\n| Side Gig | $312 | 4.6% | ↓ Declining |\n| Investment Dividends | $187 | 2.8% | Stable |\n| Cash Back/Rewards | $45 | 0.7% | Stable |\n| Other | $400 | 5.9% | Variable |\n\n**Total Monthly Income:** ~$6,785\n\n**📊 CASH FLOW PATTERN:**\n\n```\n Income ████████████████████ $6,785\nExpenses █████████████░░░░░░░ $4,120\n Savings █████░░░░░░░░░░░░░░░ $2,665\n```\n\n**Savings Rate: 39.3%** ✅ (Excellent - above 20% target)\n\n**💡 Cash Flow Timing:**\n- Paycheck: 1st & 15th\n- Biggest bills: 1st-3rd\n- Low balance risk: 12th-14th (pre-paycheck)\n\n**Recommendation:** Keep $500 buffer for the mid-month dip"),
                ],
            },
        ]

    def generate(self, db_session) -> int:
        """
        Generate AI chat sessions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of sessions created
        """
        from app.models.ai_session import AISession

        conversations = self._build_conversations()
        count = 0
        max_days = self.months_back * 30

        for conv_data in conversations:
            days_ago = conv_data["days_ago"]
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)
            is_active = days_ago <= 1

            # Build conversation history with timestamps
            messages = []
            for role, content in conv_data["messages"]:
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": created_at.isoformat(),
                })

            session = AISession(
                user_id=self.user.id,
                conversation_history=messages,
                last_intent=conv_data["intent"],
                is_active=is_active,
                created_at=created_at,
                updated_at=created_at + timedelta(minutes=len(messages) * 2),
                expires_at=created_at + (timedelta(minutes=30) if is_active else timedelta(minutes=-5)),
            )
            db_session.add(session)
            count += 1

        self.stdout_write(f"   Created {count} AI chat sessions", indent=3)
        return count
