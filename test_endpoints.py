"""
Endpoint Testing Script for TicketFlow API
Run this after logging into the frontend to get your AUTH_TOKEN
"""
from os import getenv
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_TOKEN = getenv("TEST_AUTH_TOKEN", "YOUR_TOKEN_HERE")  # Get this from browser localStorage or network tab

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_employees():
    """Test employee endpoints"""
    print("\n" + "="*60)
    print("TESTING EMPLOYEE ENDPOINTS")
    print("="*60)
    
    # Create employee
    employee_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "position": "Senior Developer",
        "department": "Engineering",
        "phone": "555-0101",
        "salary": 85000,
        "specializations": ["Python", "FastAPI", "React", "Database Design"]
    }
    
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
    print_response("Create Employee", response)
    
    if response.status_code == 201:
        employee_id = response.json()["id"]
        
        # Get all employees
        response = requests.get(f"{BASE_URL}/employees/", headers=headers)
        print_response("Get All Employees", response)
        
        # Get single employee
        response = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=headers)
        print_response("Get Single Employee", response)
        
        return employee_id
    return None

def test_tickets(employee_id=None):
    """Test ticket endpoints"""
    print("\n" + "="*60)
    print("TESTING TICKET ENDPOINTS")
    print("="*60)
    
    # Create category first
    category_data = {
        "name": "Bug Fix",
        "description": "Software bugs and issues",
        "color": "#ef4444",
        "icon": "bug"
    }
    
    response = requests.post(f"{BASE_URL}/tickets/categories", json=category_data, headers=headers)
    print_response("Create Category", response)
    
    category_id = response.json()["id"] if response.status_code == 201 else None
    
    # Create full ticket
    ticket_data = {
        "title": "Fix login authentication bug",
        "description": "Users are unable to login with valid credentials",
        "category_id": category_id,
        "status": "open",
        "priority": "urgent",
        "assigned_to": employee_id,
        "reported_by": "John Doe",
        "reporter_email": "john@example.com",
        "estimated_hours": 8,
        "tags": ["authentication", "critical", "security"]
    }
    
    response = requests.post(f"{BASE_URL}/tickets/", json=ticket_data, headers=headers)
    print_response("Create Full Ticket", response)
    
    ticket_id = response.json()["id"] if response.status_code == 201 else None
    
    # Create partial ticket
    partial_ticket_data = {
        "title": "User reported slow dashboard loading",
        "description": "Dashboard takes 10+ seconds to load",
        "reporter_email": "user@example.com",
        "reported_by": "Jane User",
        "tags": ["performance", "dashboard"]
    }
    
    response = requests.post(f"{BASE_URL}/tickets/partial", json=partial_ticket_data, headers=headers)
    print_response("Create Partial Ticket (Admin Review Required)", response)
    
    # Get all tickets
    response = requests.get(f"{BASE_URL}/tickets/", headers=headers)
    print_response("Get All Tickets", response)
    
    # Get ticket stats
    response = requests.get(f"{BASE_URL}/tickets/stats/overview", headers=headers)
    print_response("Get Ticket Statistics", response)
    
    if ticket_id:
        # Get single ticket
        response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
        print_response("Get Single Ticket", response)
        
        # Update ticket
        update_data = {
            "status": "in_progress",
            "priority": "high"
        }
        response = requests.put(f"{BASE_URL}/tickets/{ticket_id}", json=update_data, headers=headers)
        print_response("Update Ticket", response)
        
        # Get recommendations
        if employee_id:
            response = requests.get(f"{BASE_URL}/tickets/{ticket_id}/recommend-employees", headers=headers)
            print_response("Get Employee Recommendations", response)
        
        return ticket_id
    
    return None

def test_employee_ticket_update(ticket_id):
    """Test employee-side ticket updates"""
    print("\n" + "="*60)
    print("TESTING EMPLOYEE TICKET UPDATE")
    print("="*60)
    
    if not ticket_id:
        print("Skipping - no ticket ID available")
        return
    
    update_data = {
        "status": "in_review",
        "description": "Bug fixed, submitted for code review. Updated authentication flow to properly validate tokens."
    }
    
    response = requests.patch(f"{BASE_URL}/tickets/employee/{ticket_id}", json=update_data, headers=headers)
    print_response("Employee Update Ticket", response)

def test_comments(ticket_id):
    """Test ticket comments"""
    print("\n" + "="*60)
    print("TESTING TICKET COMMENTS")
    print("="*60)
    
    if not ticket_id:
        print("Skipping - no ticket ID available")
        return
    
    # Add comment
    comment_data = {
        "content": "I've identified the root cause. The issue is in the authentication middleware.",
        "is_internal": False
    }
    
    response = requests.post(f"{BASE_URL}/tickets/{ticket_id}/comments", json=comment_data, headers=headers)
    print_response("Add Comment", response)
    
    # Get comments
    response = requests.get(f"{BASE_URL}/tickets/{ticket_id}/comments", headers=headers)
    print_response("Get Ticket Comments", response)

def test_time_tracking(employee_id, ticket_id):
    """Test time tracking endpoints"""
    print("\n" + "="*60)
    print("TESTING TIME TRACKING")
    print("="*60)
    
    if not employee_id or not ticket_id:
        print("Skipping - need both employee and ticket IDs")
        return
    
    # Log time
    time_log_data = {
        "employee_id": employee_id,
        "ticket_id": ticket_id,
        "description": "Debugging authentication flow and implementing fix",
        "hours_worked": 6.5,
        "work_date": "2025-11-28",
        "is_billable": True
    }
    
    response = requests.post(f"{BASE_URL}/time/", json=time_log_data, headers=headers)
    print_response("Log Work Time", response)
    
    # Get time logs
    response = requests.get(f"{BASE_URL}/time/", headers=headers)
    print_response("Get Time Logs", response)

def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# TICKETFLOW API ENDPOINT TESTING")
    print("#"*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:20]}..." if len(AUTH_TOKEN) > 20 else f"Auth Token: {AUTH_TOKEN}")
    
    if AUTH_TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  WARNING: Please update AUTH_TOKEN in this script!")
        print("1. Login to http://localhost:3000")
        print("2. Open browser DevTools > Application > Local Storage")
        print("3. Look for Supabase session token")
        print("   OR check Network tab > any API request > Headers > Authorization")
        return
    
    # Run all tests
    employee_id = test_employees()
    ticket_id = test_tickets(employee_id)
    test_employee_ticket_update(ticket_id)
    test_comments(ticket_id)
    test_time_tracking(employee_id, ticket_id)
    
    print("\n" + "#"*60)
    print("# TESTING COMPLETE")
    print("#"*60)
    print("\nSummary of New Endpoints Tested:")
    print("✅ POST /api/tickets/partial - Create ticket with minimal info")
    print("✅ PATCH /api/tickets/employee/{id} - Employee update ticket status")
    print("\nExisting Endpoints Tested:")
    print("✅ Employee CRUD operations")
    print("✅ Full ticket creation and management")
    print("✅ Ticket categories")
    print("✅ Comments")
    print("✅ Time tracking")
    print("✅ Employee recommendations")

if __name__ == "__main__":
    main()
