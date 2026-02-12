# =============================================================================
# Digital Finance Tracker - Live Server Integration Test
# PURPOSE: Comprehensive API tests against the production server
# =============================================================================
"""
Live Server Integration Test Suite

This script tests all major API endpoints against the live production server:
- Health & connectivity checks
- Categories system
- Transactions CRUD + filtering
- Budgets CRUD + suggestions
- Loans CRUD + validation
- AI Chat system
- Summary & analytics
- Notifications & alerts

Usage:
    python backend/tools/test_live_server.py [--token JWT_TOKEN]

Note: 
    Some endpoints require authentication via JWT token
    Get a token from browser dev tools after logging into the frontend
"""

import argparse
import json
import sys
import time
import uuid
from datetime import date, datetime, timedelta
from typing import Optional
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

API_BASE = "https://securebankai.mysticdatanode.net"
FRONTEND_URL = "https://securebankai.vercel.app"

# Test results storage
RESULTS = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def log_test(name: str, status: str, message: str = "", response_code: int = None):
    """Log test result"""
    icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⚠️"}.get(status, "•")
    code_str = f"[{response_code}]" if response_code else ""
    print(f"{icon} {name} {code_str} {message}")
    
    RESULTS["tests"].append({
        "name": name,
        "status": status,
        "message": message,
        "response_code": response_code
    })
    
    if status == "PASS":
        RESULTS["passed"] += 1
    elif status == "FAIL":
        RESULTS["failed"] += 1
    else:
        RESULTS["skipped"] += 1


def get_headers(token: Optional[str] = None) -> dict:
    """Get request headers with optional auth token"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def safe_request(method: str, url: str, headers: dict, json_data: dict = None, timeout: int = 30):
    """Make a request with error handling"""
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=json_data, timeout=timeout)
        elif method == "PATCH":
            resp = requests.patch(url, headers=headers, json=json_data, timeout=timeout)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=json_data, timeout=timeout)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return None
        return resp
    except requests.exceptions.SSLError as e:
        print(f"  ⚠️ SSL Error: {str(e)[:100]}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"  ⚠️ Connection Error: {str(e)[:100]}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"  ⚠️ Timeout: {str(e)[:50]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Request Error: {str(e)[:100]}")
        return None


# =============================================================================
# HEALTH & CONNECTIVITY TESTS
# =============================================================================

def test_health_endpoint():
    """Test /health endpoint - no auth required"""
    print("\n" + "="*60)
    print("🏥 HEALTH & CONNECTIVITY TESTS")
    print("="*60)
    
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "healthy":
                log_test("Health Endpoint", "PASS", "Server is healthy", resp.status_code)
                return True
            else:
                log_test("Health Endpoint", "FAIL", f"Status: {data.get('status')}", resp.status_code)
        else:
            log_test("Health Endpoint", "FAIL", f"Unexpected status", resp.status_code)
    except Exception as e:
        log_test("Health Endpoint", "FAIL", str(e))
    return False


def test_api_test_endpoint():
    """Test /api/test endpoint"""
    try:
        resp = requests.get(f"{API_BASE}/api/test", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("message") == "Hello from backend!":
                log_test("API Test Endpoint", "PASS", "Backend responding", resp.status_code)
                return True
        log_test("API Test Endpoint", "FAIL", "", resp.status_code)
    except Exception as e:
        log_test("API Test Endpoint", "FAIL", str(e))
    return False


def test_api_docs():
    """Test API documentation endpoint"""
    try:
        resp = requests.get(f"{API_BASE}/api/docs/", timeout=10)
        if resp.status_code == 200:
            log_test("API Docs (Swagger)", "PASS", "Documentation accessible", resp.status_code)
            return True
        log_test("API Docs (Swagger)", "FAIL", "", resp.status_code)
    except Exception as e:
        log_test("API Docs (Swagger)", "FAIL", str(e))
    return False


def test_frontend_reachable():
    """Test frontend is accessible"""
    try:
        resp = requests.get(FRONTEND_URL, timeout=10)
        if resp.status_code == 200:
            log_test("Frontend Accessibility", "PASS", "Frontend is accessible", resp.status_code)
            return True
        log_test("Frontend Accessibility", "FAIL", "", resp.status_code)
    except Exception as e:
        log_test("Frontend Accessibility", "FAIL", str(e))
    return False


# =============================================================================
# CATEGORY TESTS
# =============================================================================

def test_categories_get(token: str) -> list:
    """Test GET /api/categories"""
    print("\n" + "="*60)
    print("📁 CATEGORY TESTS")
    print("="*60)
    
    headers = get_headers(token)
    resp = safe_request("GET", f"{API_BASE}/api/categories", headers)
    
    if resp is None:
        log_test("GET Categories", "FAIL", "Request failed")
        return []
    
    if resp.status_code == 401:
        log_test("GET Categories", "SKIP", "Auth required", resp.status_code)
        return []
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success") and isinstance(data.get("data"), list):
            count = len(data["data"])
            log_test("GET Categories", "PASS", f"Found {count} categories", resp.status_code)
            # Check for expected system categories
            names = [c["name"] for c in data["data"]]
            expected = ["Food & Dining", "Transportation", "Income"]
            found = sum(1 for e in expected if e in names)
            log_test("System Categories Check", "PASS" if found >= 2 else "FAIL", 
                    f"Found {found}/3 expected categories")
            return data["data"]
    
    log_test("GET Categories", "FAIL", "", resp.status_code)
    return []


def test_category_crud(token: str, categories: list):
    """Test CRUD operations on categories"""
    headers = get_headers(token)
    
    if not token:
        log_test("Category CRUD", "SKIP", "No auth token")
        return
    
    # Create custom category
    unique_name = f"Test Category {uuid.uuid4().hex[:6]}"
    create_data = {
        "name": unique_name,
        "description": "Test category created by live server tests",
        "category_type": "expense",
        "color": "#FF6B6B"
    }
    
    resp = safe_request("POST", f"{API_BASE}/api/categories", headers, create_data)
    
    if resp is None:
        log_test("Create Custom Category", "FAIL", "Request failed")
        return
        
    if resp.status_code == 401:
        log_test("Create Custom Category", "SKIP", "Auth required", resp.status_code)
        return
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        if data.get("success"):
            cat_id = data["data"]["id"]
            log_test("Create Custom Category", "PASS", f"Created {unique_name}", resp.status_code)
            
            # Update category
            update_resp = safe_request("PUT", f"{API_BASE}/api/categories/{cat_id}", headers, 
                                      {"name": f"Updated {unique_name}"})
            if update_resp and update_resp.status_code == 200:
                log_test("Update Custom Category", "PASS", "", update_resp.status_code)
            else:
                log_test("Update Custom Category", "FAIL", "", 
                        update_resp.status_code if update_resp else None)
            
            # Delete category
            delete_resp = safe_request("DELETE", f"{API_BASE}/api/categories/{cat_id}", headers)
            if delete_resp and delete_resp.status_code == 200:
                log_test("Delete Custom Category", "PASS", "", delete_resp.status_code)
            else:
                log_test("Delete Custom Category", "FAIL", "", 
                        delete_resp.status_code if delete_resp else None)
            return
    
    log_test("Create Custom Category", "FAIL", resp.text[:100] if resp else "", 
            resp.status_code if resp else None)


# =============================================================================
# TRANSACTION TESTS
# =============================================================================

def test_transactions(token: str, categories: list):
    """Test transaction CRUD operations"""
    print("\n" + "="*60)
    print("💰 TRANSACTION TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # GET transactions
    resp = safe_request("GET", f"{API_BASE}/api/transactions?page=1&per_page=20", headers)
    
    if resp is None:
        log_test("GET Transactions", "FAIL", "Request failed")
        return
    
    if resp.status_code == 401:
        log_test("GET Transactions", "SKIP", "Auth required", resp.status_code)
        return
    
    if resp.status_code == 200:
        data = resp.json()
        count = len(data.get("data", []))
        total = data.get("meta", {}).get("total", 0)
        log_test("GET Transactions", "PASS", f"Found {count}/{total} transactions", resp.status_code)
        
        # Test pagination meta
        if "meta" in data and all(k in data["meta"] for k in ["page", "per_page", "total"]):
            log_test("Pagination Meta", "PASS", "All pagination fields present")
        else:
            log_test("Pagination Meta", "FAIL", "Missing pagination fields")
    else:
        log_test("GET Transactions", "FAIL", "", resp.status_code)
        return
    
    if not token or not categories:
        log_test("Transaction CRUD", "SKIP", "No auth or categories")
        return
    
    # Find expense category
    expense_cat = next((c for c in categories if c.get("type") in ["expense", "both"] 
                       and c.get("name") != "Unknown"), None)
    
    if not expense_cat:
        log_test("Transaction Create", "SKIP", "No suitable category found")
        return
    
    # Create transaction
    txn_data = {
        "merchant_name": f"Test Transaction {uuid.uuid4().hex[:6]}",
        "amount": "42.00",
        "date": date.today().isoformat(),
        "transaction_type": "expense",
        "category_id": expense_cat["id"]
    }
    
    resp = safe_request("POST", f"{API_BASE}/api/transactions", headers, txn_data)
    
    if resp is not None and resp.status_code in [200, 201]:
        data = resp.json()
        if data.get("success"):
            txn_id = data["data"]["id"]
            log_test("Create Transaction", "PASS", f"ID: {txn_id[:8]}...", resp.status_code)
            
            # Update transaction
            update_resp = safe_request("PATCH", f"{API_BASE}/api/transactions/{txn_id}", 
                                      headers, {"merchant_name": "Updated Test Transaction"})
            if update_resp and update_resp.status_code == 200:
                log_test("Update Transaction", "PASS", "", update_resp.status_code)
            else:
                log_test("Update Transaction", "FAIL", "", 
                        update_resp.status_code if update_resp else None)
            
            # Get transaction summary
            summary_resp = safe_request("GET", f"{API_BASE}/api/transactions/summary", headers)
            if summary_resp and summary_resp.status_code == 200:
                log_test("Transaction Summary", "PASS", "", summary_resp.status_code)
            else:
                log_test("Transaction Summary", "FAIL", "", 
                        summary_resp.status_code if summary_resp else None)
            
            # Delete transaction
            delete_resp = safe_request("DELETE", f"{API_BASE}/api/transactions/{txn_id}", headers)
            if delete_resp and delete_resp.status_code == 200:
                log_test("Delete Transaction", "PASS", "", delete_resp.status_code)
            else:
                log_test("Delete Transaction", "FAIL", "", 
                        delete_resp.status_code if delete_resp else None)
            return
    
    log_test("Create Transaction", "FAIL" if resp else "FAIL", 
            resp.text[:100] if resp else "No response", 
            resp.status_code if resp else None)


def test_transaction_filters(token: str):
    """Test transaction filtering"""
    headers = get_headers(token)
    
    # Test date filter
    today = date.today().isoformat()
    resp = safe_request("GET", f"{API_BASE}/api/transactions?start_date={today}", headers)
    
    if resp is not None and resp.status_code == 200:
        log_test("Transaction Date Filter", "PASS", "", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Transaction Date Filter", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Transaction Date Filter", "FAIL", "", resp.status_code if resp else None)
    
    # Test type filter
    resp = safe_request("GET", f"{API_BASE}/api/transactions?transaction_type=expense", headers)
    if resp is not None and resp.status_code == 200:
        log_test("Transaction Type Filter", "PASS", "", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Transaction Type Filter", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Transaction Type Filter", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# BUDGET TESTS
# =============================================================================

def test_budgets(token: str, categories: list):
    """Test budget CRUD operations"""
    print("\n" + "="*60)
    print("📊 BUDGET TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # GET budgets
    resp = safe_request("GET", f"{API_BASE}/api/budgets", headers)
    
    if resp is None:
        log_test("GET Budgets", "FAIL", "Request failed")
        return
    
    if resp.status_code == 401:
        log_test("GET Budgets", "SKIP", "Auth required", resp.status_code)
        return
    
    if resp.status_code == 200:
        data = resp.json()
        count = len(data.get("data", []))
        log_test("GET Budgets", "PASS", f"Found {count} budgets", resp.status_code)
    else:
        log_test("GET Budgets", "FAIL", "", resp.status_code)
        return
    
    if not token:
        log_test("Budget CRUD", "SKIP", "No auth token")
        return
    
    # Create weekly budget (to avoid conflicts with existing monthly)
    budget_data = {
        "budget_type": "total",
        "amount": "1000.00",
        "period": "weekly"
    }
    
    resp = safe_request("POST", f"{API_BASE}/api/budgets", headers, budget_data)
    
    if resp is not None and resp.status_code in [200, 201]:
        data = resp.json()
        if data.get("success"):
            budget_id = data["data"]["id"]
            log_test("Create Total Budget", "PASS", f"ID: {budget_id[:8]}...", resp.status_code)
            
            # Update budget
            update_resp = safe_request("PUT", f"{API_BASE}/api/budgets/{budget_id}", 
                                      headers, {"amount": "1500.00"})
            if update_resp and update_resp.status_code == 200:
                log_test("Update Budget", "PASS", "", update_resp.status_code)
            else:
                log_test("Update Budget", "FAIL", "", 
                        update_resp.status_code if update_resp else None)
            
            # Delete budget
            delete_resp = safe_request("DELETE", f"{API_BASE}/api/budgets/{budget_id}", headers)
            if delete_resp and delete_resp.status_code == 200:
                log_test("Delete Budget", "PASS", "", delete_resp.status_code)
            else:
                log_test("Delete Budget", "FAIL", "", 
                        delete_resp.status_code if delete_resp else None)
    elif resp is not None and resp.status_code == 409:
        log_test("Create Total Budget", "SKIP", "Budget already exists", resp.status_code)
    else:
        log_test("Create Total Budget", "FAIL", "", resp.status_code if resp else None)
    
    # Test budget suggestions
    resp = safe_request("GET", f"{API_BASE}/api/budgets/suggestions?months=3", headers)
    if resp is not None and resp.status_code == 200:
        log_test("Budget Suggestions", "PASS", "", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Budget Suggestions", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Budget Suggestions", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# LOAN TESTS
# =============================================================================

def test_loans(token: str, categories: list):
    """Test loan CRUD operations"""
    print("\n" + "="*60)
    print("🏦 LOAN TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # GET loans
    resp = safe_request("GET", f"{API_BASE}/api/loans", headers)
    
    if resp is None:
        log_test("GET Loans", "FAIL", "Request failed")
        return
    
    if resp.status_code == 401:
        log_test("GET Loans", "SKIP", "Auth required", resp.status_code)
        return
    
    if resp.status_code == 200:
        data = resp.json()
        count = len(data.get("data", []))
        log_test("GET Loans", "PASS", f"Found {count} loans", resp.status_code)
    else:
        log_test("GET Loans", "FAIL", "", resp.status_code)
        return
    
    if not token or not categories:
        log_test("Loan CRUD", "SKIP", "No auth or categories")
        return
    
    # Find Financial Services category
    fin_cat = next((c for c in categories if c.get("name") == "Financial Services"), None)
    if not fin_cat:
        fin_cat = next((c for c in categories if c.get("type") in ["expense", "both"]), None)
    
    if not fin_cat:
        log_test("Create Loan", "SKIP", "No suitable category found")
        return
    
    # Create loan
    loan_data = {
        "name": f"Test Loan {uuid.uuid4().hex[:6]}",
        "original_amount": "5000.00",
        "remaining_amount": "5000.00",
        "category_id": fin_cat["id"],
        "start_date": date.today().isoformat()
    }
    
    resp = safe_request("POST", f"{API_BASE}/api/loans", headers, loan_data)
    
    if resp is not None and resp.status_code in [200, 201]:
        data = resp.json()
        if data.get("success"):
            loan_id = data["data"]["id"]
            log_test("Create Loan", "PASS", f"ID: {loan_id[:8]}...", resp.status_code)
            
            # Update loan
            update_resp = safe_request("PATCH", f"{API_BASE}/api/loans/{loan_id}", 
                                      headers, {"remaining_amount": "4500.00"})
            if update_resp and update_resp.status_code == 200:
                log_test("Update Loan (Payment)", "PASS", "", update_resp.status_code)
            else:
                log_test("Update Loan (Payment)", "FAIL", "", 
                        update_resp.status_code if update_resp else None)
            
            # Test loan status filter
            filter_resp = safe_request("GET", f"{API_BASE}/api/loans?status=open", headers)
            if filter_resp and filter_resp.status_code == 200:
                log_test("Loan Status Filter", "PASS", "", filter_resp.status_code)
            else:
                log_test("Loan Status Filter", "FAIL", "", 
                        filter_resp.status_code if filter_resp else None)
            return
    
    log_test("Create Loan", "FAIL", resp.text[:100] if resp else "", 
            resp.status_code if resp else None)


def test_loan_validation(token: str):
    """Test loan validation rules"""
    headers = get_headers(token)
    
    if not token:
        log_test("Loan Validation", "SKIP", "No auth token")
        return
    
    # Test missing category_id
    resp = safe_request("POST", f"{API_BASE}/api/loans", headers, {
        "name": "Invalid Loan",
        "original_amount": "1000.00",
        "remaining_amount": "1000.00"
        # Missing category_id
    })
    
    if resp is not None and resp.status_code == 422:
        log_test("Loan Validation (No Category)", "PASS", "Correctly rejected", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Loan Validation (No Category)", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Loan Validation (No Category)", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# AI SYSTEM TESTS
# =============================================================================

def test_ai_system(token: str):
    """Test AI chat and related endpoints"""
    print("\n" + "="*60)
    print("🤖 AI SYSTEM TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # Test AI status
    resp = safe_request("GET", f"{API_BASE}/api/v1/ai/status", headers)
    if resp is not None and resp.status_code == 200:
        data = resp.json()
        log_test("AI Status Endpoint", "PASS", f"AI enabled: {data.get('data', {}).get('enabled', 'unknown')}", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("AI Status Endpoint", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("AI Status Endpoint", "FAIL", "", resp.status_code if resp else None)
    
    # Test AI chat history
    resp = safe_request("GET", f"{API_BASE}/api/v1/ai/chat/history", headers)
    if resp is not None and resp.status_code == 200:
        data = resp.json()
        if data.get("success"):
            sessions = len(data.get("data", {}).get("sessions", []))
            log_test("AI Chat History", "PASS", f"Found {sessions} sessions", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("AI Chat History", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("AI Chat History", "FAIL", "", resp.status_code if resp else None)
    
    # Test AI Chat (if authenticated)
    if token:
        resp = safe_request("POST", f"{API_BASE}/api/v1/ai/chat", headers, {
            "message": "Hello, what are my spending habits?"
        })
        
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                log_test("AI Chat Message", "PASS", "AI responded successfully", resp.status_code)
            else:
                log_test("AI Chat Message", "FAIL", data.get("error", {}).get("message", ""), resp.status_code)
        elif resp is not None and resp.status_code == 401:
            log_test("AI Chat Message", "SKIP", "Auth required", resp.status_code)
        else:
            log_test("AI Chat Message", "FAIL", "", resp.status_code if resp else None)
        
        # Test AI transaction parsing
        resp = safe_request("POST", f"{API_BASE}/api/v1/ai/chat", headers, {
            "message": "I spent $50 at Starbucks yesterday"
        })
        
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                intent = data.get("data", {}).get("intent", "unknown")
                log_test("AI Transaction Parse", "PASS", f"Intent: {intent}", resp.status_code)
        elif resp is not None and resp.status_code == 401:
            log_test("AI Transaction Parse", "SKIP", "Auth required", resp.status_code)
        else:
            log_test("AI Transaction Parse", "FAIL", "", resp.status_code if resp else None)
    else:
        log_test("AI Chat Tests", "SKIP", "No auth token for chat tests")


# =============================================================================
# SUMMARY & ANALYTICS TESTS
# =============================================================================

def test_summary_endpoints(token: str):
    """Test summary and analytics endpoints"""
    print("\n" + "="*60)
    print("📈 SUMMARY & ANALYTICS TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # Monthly summary
    resp = safe_request("GET", f"{API_BASE}/api/summary/monthly", headers)
    if resp is not None and resp.status_code == 200:
        log_test("Monthly Summary", "PASS", "", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Monthly Summary", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Monthly Summary", "FAIL", "", resp.status_code if resp else None)
    
    # Category breakdown
    resp = safe_request("GET", f"{API_BASE}/api/summary/monthly/categories", headers)
    if resp is not None and resp.status_code == 200:
        log_test("Category Summary", "PASS", "", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Category Summary", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Category Summary", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# NOTIFICATION & ALERT TESTS
# =============================================================================

def test_notifications(token: str):
    """Test notification endpoints"""
    print("\n" + "="*60)
    print("🔔 NOTIFICATION & ALERT TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # Get notifications
    resp = safe_request("GET", f"{API_BASE}/api/notifications", headers)
    if resp is not None and resp.status_code == 200:
        data = resp.json()
        count = len(data.get("data", []))
        log_test("GET Notifications", "PASS", f"Found {count} notifications", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("GET Notifications", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("GET Notifications", "FAIL", "", resp.status_code if resp else None)
    
    # Get alerts
    resp = safe_request("GET", f"{API_BASE}/api/alerts", headers)
    if resp is not None and resp.status_code == 200:
        data = resp.json()
        count = len(data.get("data", []))
        log_test("GET Alerts", "PASS", f"Found {count} alerts", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("GET Alerts", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("GET Alerts", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

def test_edge_cases(token: str):
    """Test edge cases and error handling"""
    print("\n" + "="*60)
    print("🧪 EDGE CASE & ERROR HANDLING TESTS")
    print("="*60)
    
    headers = get_headers(token)
    
    # Invalid UUID
    resp = safe_request("GET", f"{API_BASE}/api/categories/not-a-valid-uuid", headers)
    if resp is not None and resp.status_code in [400, 422]:
        log_test("Invalid UUID Handling", "PASS", "Properly rejected", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Invalid UUID Handling", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Invalid UUID Handling", "FAIL", "", resp.status_code if resp else None)
    
    # Non-existent resource
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    resp = safe_request("GET", f"{API_BASE}/api/categories/{fake_uuid}", headers)
    if resp is not None and resp.status_code == 404:
        log_test("Non-existent Resource", "PASS", "Returns 404", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Non-existent Resource", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Non-existent Resource", "FAIL", "", resp.status_code if resp else None)
    
    # Empty body handling
    resp = safe_request("POST", f"{API_BASE}/api/transactions", headers, {})
    if resp is not None and resp.status_code == 422:
        log_test("Empty Body Handling", "PASS", "Properly rejected", resp.status_code)
    elif resp is not None and resp.status_code == 401:
        log_test("Empty Body Handling", "SKIP", "Auth required", resp.status_code)
    else:
        log_test("Empty Body Handling", "FAIL", "", resp.status_code if resp else None)


# =============================================================================
# MAIN RUNNER
# =============================================================================

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed:  {RESULTS['passed']}")
    print(f"❌ Failed:  {RESULTS['failed']}")
    print(f"⚠️  Skipped: {RESULTS['skipped']}")
    print(f"📊 Total:   {len(RESULTS['tests'])}")
    
    if RESULTS['failed'] > 0:
        print("\n❌ Failed Tests:")
        for test in RESULTS['tests']:
            if test['status'] == 'FAIL':
                print(f"  • {test['name']}: {test['message']}")
    
    # Overall status
    print("\n" + "="*60)
    if RESULTS['failed'] == 0:
        print("🎉 ALL TESTS PASSED (excluding skipped)")
    else:
        print(f"⚠️  {RESULTS['failed']} TESTS FAILED")
    print("="*60)


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run live server integration tests')
    parser.add_argument('--token', '-t', type=str, help='JWT authentication token')
    args = parser.parse_args()
    
    token = args.token
    
    print("="*60)
    print("🚀 LIVE SERVER INTEGRATION TEST SUITE")
    print("="*60)
    print(f"API URL:      {API_BASE}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Auth Token:   {'Provided' if token else 'Not provided (some tests will skip)'}")
    print(f"Timestamp:    {datetime.now().isoformat()}")
    print("="*60)
    
    # Run tests
    test_health_endpoint()
    test_api_test_endpoint()
    test_api_docs()
    test_frontend_reachable()
    
    categories = test_categories_get(token)
    test_category_crud(token, categories)
    
    test_transactions(token, categories)
    test_transaction_filters(token)
    
    test_budgets(token, categories)
    
    test_loans(token, categories)
    test_loan_validation(token)
    
    test_ai_system(token)
    
    test_summary_endpoints(token)
    
    test_notifications(token)
    
    test_edge_cases(token)
    
    # Print summary
    print_summary()
    
    # Return exit code
    return 0 if RESULTS['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
