"""
Reset Test Data - Cleanup script for test endpoints
This will delete all test data created during endpoint testing
"""
from os import getenv
import requests
import json

# Configuration 
BASE_URL = "http://ticketflow-2-n132.onrender.com/api" # change for local/global testing
AUTH_TOKEN = getenv("TEST_AUTH_TOKEN", "YOUR_TOKEN_HERE")  # Use the same token from test_endpoints.py

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def delete_test_data():
    """Delete test tickets, employees, categories, and comments"""
    print("\n" + "="*60)
    print("RESETTING TEST DATA")
    print("="*60)
    
    # Get all tickets
    response = requests.get(f"{BASE_URL}/tickets/", headers=headers)
    if response.status_code == 200:
        tickets = response.json()["tickets"]
        print(f"\nFound {len(tickets)} tickets to delete...")
        
        for ticket in tickets:
            if ticket["ticket_number"].startswith("TICK-"):
                print(f"Deleting ticket {ticket['ticket_number']}...")
                delete_resp = requests.delete(f"{BASE_URL}/tickets/{ticket['id']}", headers=headers)
                if delete_resp.status_code == 200:
                    print(f"  ✅ Deleted {ticket['ticket_number']}")
                else:
                    print(f"  ❌ Failed to delete {ticket['ticket_number']}: {delete_resp.status_code}")
    
    # Get all employees
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    if response.status_code == 200:
        employees = response.json()["employees"]
        print(f"\nFound {len(employees)} employees...")
        
        # Delete test employee (Alice Johnson)
        for emp in employees:
            if emp["name"] == "Alice Johnson" and emp["email"] == "alice@example.com":
                print(f"Deleting test employee {emp['name']}...")
                delete_resp = requests.delete(f"{BASE_URL}/employees/{emp['id']}", headers=headers)
                if delete_resp.status_code == 200:
                    print(f"  ✅ Deleted {emp['name']}")
                else:
                    print(f"  ❌ Failed to delete {emp['name']}: {delete_resp.status_code}")
    
    # Get all categories
    response = requests.get(f"{BASE_URL}/tickets/categories", headers=headers)
    if response.status_code == 200:
        categories = response.json()["categories"]
        print(f"\nFound {len(categories)} categories...")
        
        # Delete test category (Bug Fix)
        for cat in categories:
            if cat["name"] == "Bug Fix":
                print(f"Deleting test category {cat['name']}...")
                delete_resp = requests.delete(f"{BASE_URL}/tickets/categories/{cat['id']}", headers=headers)
                if delete_resp.status_code == 200:
                    print(f"  ✅ Deleted {cat['name']}")
                else:
                    print(f"  ❌ Failed to delete {cat['name']}: {delete_resp.status_code}")
    
    print("\n" + "="*60)
    print("RESET COMPLETE")
    print("="*60)
    print("\nYou can now re-run test_endpoints.py with a clean slate!")

if __name__ == "__main__":
    if AUTH_TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  WARNING: Please update AUTH_TOKEN in this script!")
        print("Use the same token from test_endpoints.py")
    else:
        delete_test_data()
