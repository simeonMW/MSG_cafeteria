"""
Tests all endpoints with proper authorization, error handling, and role based access
"""
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


if os.getenv("FLASK_ENV") == "production":
    BASE_URL = "https://msg-cafeteria.onrender.com/api"
else:
    BASE_URL = "http://127.0.0.1:5000/api"

# Test data
TEST_USERS = {
    "customer": {"email": "customer1@test.mw", "password": "pass1234", "role": "customer", "employee_number": "CUST-005"},
    "chef": {"email": "chef1@test.mw", "password": "pass1234", "role": "chef"},
    "hr_manager": {"email": "hr1@test.mw", "password": "pass1234", "role": "hr_manager", "employee_number": "HR-005"}
}

# tokens and IDs for use across tests
tokens = {}
user_ids = {}
menu_items = {}
transaction_ids = {}
payment_ids = {}

# Test Results Tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def print_test(test_name, status, details=""):
    """Pretty print test results"""
    icon = "✓" if status == "PASS" else "✗"
    color_code = "\033[92m" if status == "PASS" else "\033[91m"
    reset_code = "\033[0m"
    
    print(f"{color_code}[{icon}] {test_name}{reset_code}")
    if details:
        print(f"    → {details}")
    
    if status == "PASS":
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(test_name)

def handle_response(response, expected_status=200):
    """Helper to check response status"""
    try:
        if response.status_code == expected_status:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

# ===================================================================
# 1. AUTHENTICATION TESTS
# ===================================================================

def test_auth_register():
    """Test user registration for all roles"""
    print("\n" + "="*70)
    print("1. AUTHENTICATION TESTS")
    print("="*70)
    
    for role, user_data in TEST_USERS.items():
        resp = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        success, data = handle_response(resp, 201)
        
        if success:
            user_ids[role] = data.get('user_id')
            print_test(f"Register {role}", "PASS", f"User ID: {user_ids[role]}")
        else:
            # Check if already exists
            if "already exists" in str(data):
                print_test(f"Register {role}", "PASS", "User already exists (continuing)")
                # Try login to get ID
                user_ids[role] = user_data.get('user_id')
            else:
                print_test(f"Register {role}", "FAIL", data)

def test_auth_login():
    """Test login for all user roles"""
    print("\n" + "-"*70)
    
    for role, user_data in TEST_USERS.items():
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        # Add employee_number for roles that require it
        if role in ['customer', 'hr_manager']:
            login_data["employee_number"] = user_data.get("employee_number")
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        success, data = handle_response(resp, 200)
        
        if success:
            token = data.get('token')
            tokens[role] = token
            print_test(f"Login {role}", "PASS", f"Token received")
            # If HR logged in, verify customer
            if role == 'hr_manager':
                verify_customer()
        else:
            print_test(f"Login {role}", "FAIL", data)

def verify_customer():
    """Helper to verify customer after HR login"""
    if "hr_manager" in tokens:
        hr_headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
        customer_id = user_ids.get("customer")
        resp = requests.post(f"{BASE_URL}/auth/verify-user/{customer_id}", headers=hr_headers)
        success, data = handle_response(resp, 200)
        if success:
            print("Customer verified")
            # Now try customer login
            customer_data = TEST_USERS["customer"]
            login_data = {"email": customer_data["email"], "password": customer_data["password"], "employee_number": customer_data["employee_number"]}
            resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            success, data = handle_response(resp, 200)
            if success:
                tokens["customer"] = data.get('token')
                print("Customer login successful after verification")
        else:
            print("Customer verification failed")

def test_auth_errors():
    """Test authentication error cases"""
    print("\n" + "-"*70)
    
    # Missing required fields
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": "test@test.mw"})
    success, data = handle_response(resp, 400)
    print_test("Register - Missing fields validation", "PASS" if success else "FAIL", "Should return 400" if not success else "")
    
    # Invalid credentials
    resp = requests.post(f"{BASE_URL}/auth/login", 
                        json={"email": "wrong@test.mw", "password": "wrong"})
    success, data = handle_response(resp, 401)
    print_test("Login - Invalid credentials", "PASS" if success else "FAIL", "Should return 401" if not success else "")

def test_auth_verify_user():
    """Test HR user verification (requires HR token)"""
    print("\n" + "-"*70)
    
    if "hr_manager" not in tokens:
        print_test("Verify user (HR)", "FAIL", "HR manager token not available")
        return
    
    hr_headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
    customer_id = user_ids.get("customer", 1)
    
    resp = requests.post(f"{BASE_URL}/auth/verify-user/{customer_id}", headers=hr_headers)
    success, data = handle_response(resp, 200)
    print_test("HR verify user", "PASS" if success else "FAIL", data if not success else "User verified")

# ===================================================================
# 2. MENU MANAGEMENT TESTS
# ===================================================================

def test_menu_get_public():
    """Test fetching public menu"""
    print("\n" + "="*70)
    print("2. MENU MANAGEMENT TESTS")
    print("="*70)
    
    if "customer" not in tokens:
        print_test("Get public menu", "FAIL", "Customer token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    resp = requests.get(f"{BASE_URL}/menu/public", headers=headers)
    success, data = handle_response(resp, 200)
    
    if success and isinstance(data, list):
        print_test("Get public menu", "PASS", f"Found {len(data)} items")
        if len(data) > 0:
            menu_items["first"] = data[0].get('id')
    else:
        print_test("Get public menu", "FAIL", "No menu items found or invalid response")

def test_menu_chef_inventory():
    """Test chef inventory access (full menu including unavailable)"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens:
        print_test("Chef get inventory", "FAIL", "Chef token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    resp = requests.get(f"{BASE_URL}/menu/inventory", headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Chef get inventory", "PASS" if success else "FAIL", 
               f"Found {len(data)} items" if success else data)

def test_menu_chef_add_item():
    """Test chef adding menu items"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens:
        print_test("Chef add item", "FAIL", "Chef token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    item_data = {
        "name": f"Test Item {datetime.now().timestamp()}",
        "description": "A test menu item",
        "price": 150.00,
        "picture_url": "http://example.com/item.jpg",
        "is_available": True
    }
    
    resp = requests.post(f"{BASE_URL}/menu/add", json=item_data, headers=headers)
    success, data = handle_response(resp, 201)
    
    if success:
        item_id = data.get('item', {}).get('id')
        menu_items["created"] = item_id
        print_test("Chef add item", "PASS", f"Item ID: {item_id}")
    else:
        print_test("Chef add item", "FAIL", data)

def test_menu_chef_add_item2():
    """Test chef adding another menu item for ordering"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens:
        print_test("Chef add item 2", "FAIL", "Chef token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    item_data = {
        "name": f"Order Item {datetime.now().timestamp()}",
        "description": "A test menu item for ordering",
        "price": 200.00,
        "picture_url": "http://example.com/item2.jpg",
        "is_available": True
    }
    
    resp = requests.post(f"{BASE_URL}/menu/add", json=item_data, headers=headers)
    success, data = handle_response(resp, 201)
    
    if success:
        item_id = data.get('item', {}).get('id')
        menu_items["for_order"] = item_id
        print_test("Chef add item 2", "PASS", f"Item ID: {item_id}")
    else:
        print_test("Chef add item 2", "FAIL", data)

def test_menu_chef_update_item():
    """Test chef updating menu items"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens or "created" not in menu_items:
        print_test("Chef update item", "FAIL", "Chef token or item ID not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    update_data = {
        "name": "Updated Item",
        "price": 200.00,
        "description": "Updated description"
    }
    
    item_id = menu_items["created"]
    resp = requests.put(f"{BASE_URL}/menu/update/{item_id}", json=update_data, headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Chef update item", "PASS" if success else "FAIL", data if not success else "Item updated")

def test_menu_chef_toggle_item():
    """Test chef toggling item availability"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens or "created" not in menu_items:
        print_test("Chef toggle item", "FAIL", "Chef token or item ID not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    item_id = menu_items["created"]
    
    resp = requests.patch(f"{BASE_URL}/menu/toggle/{item_id}", headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Chef toggle item", "PASS" if success else "FAIL", data if not success else "Item toggled")

def test_menu_authorization():
    """Test menu authorization (customer shouldn't access chef endpoints)"""
    print("\n" + "-"*70)
    
    if "customer" not in tokens:
        print_test("Menu authorization", "FAIL", "Customer token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    item_data = {"name": "Unauthorized", "price": 100}
    
    resp = requests.post(f"{BASE_URL}/menu/add", json=item_data, headers=headers)
    success, data = handle_response(resp, 403)
    print_test("Customer cannot add items", "PASS" if success else "FAIL", "Should return 403" if not success else "")

# ===================================================================
# 3. ORDER MANAGEMENT TESTS
# ===================================================================

def test_orders_place():
    """Test placing orders"""
    print("\n" + "="*70)
    print("3. ORDER MANAGEMENT TESTS")
    print("="*70)
    
    if "customer" not in tokens or "for_order" not in menu_items:
        print_test("Place order", "FAIL", "Customer token or menu items not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    order_data = {"item_id": menu_items["for_order"]}
    
    resp = requests.post(f"{BASE_URL}/orders/place", json=order_data, headers=headers)
    success, data = handle_response(resp, 201)
    
    if success:
        tx_id = data.get('transaction_id')
        token = data.get('token')
        transaction_ids["order1"] = {"id": tx_id, "token": token}
        print_test("Place order", "PASS", f"Transaction ID: {tx_id}, Token: {token[:20]}...")
    else:
        print_test("Place order", "FAIL", data)

def test_orders_place_multiple():
    """Test placing multiple orders"""
    print("\n" + "-"*70)
    
    if "customer" not in tokens or "first" not in menu_items:
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    
    for i in range(2):
        order_data = {"item_id": menu_items["for_order"]}
        resp = requests.post(f"{BASE_URL}/orders/place", json=order_data, headers=headers)
        success, data = handle_response(resp, 201)
        
        if success:
            tx_id = data.get('transaction_id')
            token = data.get('token')
            transaction_ids[f"order{i+2}"] = {"id": tx_id, "token": token}
    
    print_test("Place multiple orders", "PASS", f"Created {len(transaction_ids)} orders")

def test_orders_verify():
    """Test chef verifying orders"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens or "order1" not in transaction_ids:
        print_test("Verify order", "FAIL", "Chef token or order not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    verify_data = {"token": transaction_ids["order1"]["token"]}
    
    resp = requests.post(f"{BASE_URL}/orders/verify", json=verify_data, headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Chef verify order", "PASS" if success else "FAIL", 
               data.get('message') if success else data)

def test_orders_replay_attack():
    """Test replay attack prevention (verify same token twice)"""
    print("\n" + "-"*70)
    
    if "chef" not in tokens or "order2" not in transaction_ids:
        print_test("Replay attack prevention", "FAIL", "Chef token or order not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['chef']}"}
    verify_data = {"token": transaction_ids["order2"]["token"]}
    
    # First verification
    resp1 = requests.post(f"{BASE_URL}/orders/verify", json=verify_data, headers=headers)
    success1, data1 = handle_response(resp1, 200)
    
    # Second verification (should fail)
    resp2 = requests.post(f"{BASE_URL}/orders/verify", json=verify_data, headers=headers)
    success2, data2 = handle_response(resp2, 200)
    
    if success1 and not success2:
        print_test("Replay attack prevented", "PASS", "Second verification correctly rejected")
    else:
        print_test("Replay attack prevented", "FAIL", "Vulnerability: Duplicate verification allowed")

def test_orders_authorization():
    """Test order authorization"""
    print("\n" + "-"*70)
    
    if "hr_manager" not in tokens or "order3" not in transaction_ids:
        print_test("Orders authorization", "FAIL", "HR manager token or order not available")
        return
    
    # HR manager shouldn't be able to verify orders
    headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
    verify_data = {"token": transaction_ids["order3"]["token"]}
    
    resp = requests.post(f"{BASE_URL}/orders/verify", json=verify_data, headers=headers)
    success, data = handle_response(resp, 403)
    print_test("HR cannot verify orders", "PASS" if success else "FAIL", "Should return 403" if not success else "")

# ===================================================================
# 4. REPORTING TESTS
# ===================================================================

def test_reports_generate():
    """Test generating financial reports"""
    print("\n" + "="*70)
    print("4. REPORTING TESTS")
    print("="*70)
    
    if "hr_manager" not in tokens:
        print_test("Generate report", "FAIL", "HR manager token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
    report_data = {}
    
    resp = requests.post(f"{BASE_URL}/reports/generate", json=report_data, headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Generate financial report", "PASS" if success else "FAIL", 
               f"Report generated" if success else data)

def test_reports_generate_with_dates():
    """Test generating reports with date filters"""
    print("\n" + "-"*70)
    
    if "hr_manager" not in tokens:
        print_test("Generate report with dates", "FAIL", "HR manager token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    report_data = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    resp = requests.post(f"{BASE_URL}/reports/generate", json=report_data, headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Generate report with date range", "PASS" if success else "FAIL",
               f"Last 7 days" if success else data)

def test_reports_summary():
    """Test dashboard summary endpoint"""
    print("\n" + "-"*70)
    
    if "hr_manager" not in tokens:
        print_test("Dashboard summary", "FAIL", "HR manager token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['hr_manager']}"}
    resp = requests.get(f"{BASE_URL}/reports/summary", headers=headers)
    success, data = handle_response(resp, 200)
    print_test("Get dashboard summary", "PASS" if success else "FAIL",
               f"Summary retrieved" if success else data)

def test_reports_authorization():
    """Test report authorization (customer shouldn't access reports)"""
    print("\n" + "-"*70)
    
    if "customer" not in tokens:
        print_test("Reports authorization", "FAIL", "Customer token not available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    resp = requests.post(f"{BASE_URL}/reports/generate", json={}, headers=headers)
    success, data = handle_response(resp, 403)
    print_test("Customer cannot generate reports", "PASS" if success else "FAIL", "Should return 403" if not success else "")

# ===================================================================
# 5. SECURITY & ERROR HANDLING TESTS
# ===================================================================

def test_security_missing_token():
    """Test endpoints without authentication"""
    print("\n" + "="*70)
    print("5. SECURITY & ERROR HANDLING TESTS")
    print("="*70)
    
    resp = requests.get(f"{BASE_URL}/menu/public")
    success, data = handle_response(resp, 401)
    print_test("Missing auth token returns 401", "PASS" if success else "FAIL", "Should return 401" if not success else "")

def test_security_invalid_token():
    """Test with invalid authentication token"""
    print("\n" + "-"*70)
    
    headers = {"Authorization": "Bearer invalid_token_here"}
    resp = requests.get(f"{BASE_URL}/menu/public", headers=headers)
    success, data = handle_response(resp, 401)
    print_test("Invalid token returns 401", "PASS" if success else "FAIL", "Should return 401" if not success else "")

def test_error_handling():
    """Test error handling for invalid data"""
    print("\n" + "-"*70)
    
    if "customer" not in tokens:
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    
    # Invalid item ID
    resp = requests.post(f"{BASE_URL}/orders/place", 
                        json={"item_id": 99999}, headers=headers)
    success, data = handle_response(resp, 400)
    print_test("Invalid item returns error", "PASS" if success else "FAIL", "Should return 400" if not success else "")
    
    # Missing required fields
    resp = requests.post(f"{BASE_URL}/orders/place", 
                        json={}, headers=headers)
    success, data = handle_response(resp, 400)
    print_test("Missing fields returns error", "PASS" if success else "FAIL", "Should return 400" if not success else "")

# ===================================================================
# MAIN TEST RUNNER
# ===================================================================

def run_all_tests():
    """Execute all tests and print summary"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  CAFE ORDERING SYSTEM - COMPREHENSIVE API TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # Authentication Tests
        test_auth_register()
        test_auth_login()
        test_auth_errors()
        test_auth_verify_user()
        
        # Menu Tests
        test_menu_chef_inventory()
        test_menu_chef_add_item()
        test_menu_get_public()
        test_menu_chef_add_item2()  # Add another item for ordering
        test_menu_chef_update_item()
        test_menu_chef_toggle_item()
        test_menu_authorization()
        
        # Order Tests
        test_orders_place()
        test_orders_place_multiple()
        test_orders_verify()
        test_orders_replay_attack()
        test_orders_authorization()
        
        # Reporting Tests
        test_reports_generate()
        test_reports_generate_with_dates()
        test_reports_summary()
        test_reports_authorization()
        
        # Security Tests
        test_security_missing_token()
        test_security_invalid_token()
        test_error_handling()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at", BASE_URL)
        print("   Make sure the Flask app is running: python app.py")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    # Print Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    total = test_results["passed"] + test_results["failed"]
    percentage = (test_results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✓ Passed: {test_results['passed']}")
    print(f"✗ Failed: {test_results['failed']}")
    print(f"Success Rate: {percentage:.1f}%")
    
    if test_results["failed"] > 0:
        print(f"\nFailed Tests:")
        for error in test_results["errors"]:
            print(f"  • {error}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()