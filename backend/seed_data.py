"""
Dummy Data Generator and Test Cases for TicketFlow
This script generates realistic test data for the ticket management system
"""

import requests
import json
from datetime import datetime, timedelta, date
import random

BASE_URL = "http://localhost:3000/api"

# You'll need to replace this with your actual auth token
# Get it by logging in through the frontend first
AUTH_TOKEN = "YOUR_SUPABASE_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# ============================================
# DUMMY DATA
# ============================================

TICKET_CATEGORIES = [
    {"name": "Backend", "description": "Backend development tasks", "color": "#10b981", "icon": "Server"},
    {"name": "Frontend", "description": "Frontend/UI tasks", "color": "#3b82f6", "icon": "Layout"},
    {"name": "Database", "description": "Database related tasks", "color": "#8b5cf6", "icon": "Database"},
    {"name": "Bug Fix", "description": "Bug fixes and issues", "color": "#ef4444", "icon": "Bug"},
    {"name": "Feature", "description": "New feature development", "color": "#f59e0b", "icon": "Sparkles"},
    {"name": "DevOps", "description": "DevOps and infrastructure", "color": "#06b6d4", "icon": "Cloud"},
    {"name": "Documentation", "description": "Documentation tasks", "color": "#6366f1", "icon": "FileText"},
    {"name": "Testing", "description": "Testing and QA", "color": "#ec4899", "icon": "CheckCircle"}
]

EMPLOYEES = [
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "position": "Senior Backend Developer",
        "department": "Engineering",
        "phone": "+1-555-0101",
        "salary": 120000,
        "specializations": ["Backend", "Python", "API", "Database"],
        "is_active": True
    },
    {
        "name": "Mike Chen",
        "email": "mike.chen@example.com",
        "position": "Frontend Lead",
        "department": "Engineering",
        "phone": "+1-555-0102",
        "salary": 115000,
        "specializations": ["Frontend", "React", "TypeScript", "UI/UX"],
        "is_active": True
    },
    {
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@example.com",
        "position": "Full Stack Developer",
        "department": "Engineering",
        "phone": "+1-555-0103",
        "salary": 105000,
        "specializations": ["Backend", "Frontend", "Python", "React"],
        "is_active": True
    },
    {
        "name": "David Kim",
        "email": "david.kim@example.com",
        "position": "DevOps Engineer",
        "department": "Operations",
        "phone": "+1-555-0104",
        "salary": 110000,
        "specializations": ["DevOps", "AWS", "Docker", "CI/CD"],
        "is_active": True
    },
    {
        "name": "Lisa Wang",
        "email": "lisa.wang@example.com",
        "position": "QA Engineer",
        "department": "Quality Assurance",
        "phone": "+1-555-0105",
        "salary": 95000,
        "specializations": ["Testing", "Automation", "Python"],
        "is_active": True
    },
    {
        "name": "James Wilson",
        "email": "james.wilson@example.com",
        "position": "Database Administrator",
        "department": "Operations",
        "phone": "+1-555-0106",
        "salary": 105000,
        "specializations": ["Database", "PostgreSQL", "Performance"],
        "is_active": True
    },
    {
        "name": "Rachel Martinez",
        "email": "rachel.martinez@example.com",
        "position": "Junior Developer",
        "department": "Engineering",
        "phone": "+1-555-0107",
        "salary": 75000,
        "specializations": ["Backend", "Python"],
        "is_active": True
    },
    {
        "name": "Tom Anderson",
        "email": "tom.anderson@example.com",
        "position": "Technical Writer",
        "department": "Documentation",
        "phone": "+1-555-0108",
        "salary": 70000,
        "specializations": ["Documentation", "Technical Writing"],
        "is_active": True
    }
]

TICKET_TEMPLATES = [
    {
        "title": "Implement user authentication API",
        "description": "Create JWT-based authentication endpoints with refresh token support. Include login, logout, and token refresh functionality.",
        "priority": "high",
        "estimated_hours": 8,
        "tags": ["authentication", "security", "api"]
    },
    {
        "title": "Design dashboard UI mockups",
        "description": "Create Figma mockups for the new admin dashboard with dark mode support",
        "priority": "medium",
        "estimated_hours": 6,
        "tags": ["design", "ui", "dashboard"]
    },
    {
        "title": "Fix database connection pool leak",
        "description": "Investigate and fix memory leak in database connection pool. Monitor long-running connections and implement proper cleanup.",
        "priority": "urgent",
        "estimated_hours": 4,
        "tags": ["bug", "database", "performance"]
    },
    {
        "title": "Add pagination to employee list",
        "description": "Implement server-side pagination for employee list endpoint to improve performance with large datasets",
        "priority": "medium",
        "estimated_hours": 3,
        "tags": ["feature", "performance", "backend"]
    },
    {
        "title": "Set up CI/CD pipeline",
        "description": "Configure GitHub Actions for automated testing and deployment to staging environment",
        "priority": "high",
        "estimated_hours": 12,
        "tags": ["devops", "automation", "ci/cd"]
    },
    {
        "title": "Write API documentation",
        "description": "Document all REST API endpoints with examples and request/response schemas",
        "priority": "medium",
        "estimated_hours": 10,
        "tags": ["documentation", "api"]
    },
    {
        "title": "Implement real-time notifications",
        "description": "Add WebSocket support for real-time ticket updates and notifications",
        "priority": "low",
        "estimated_hours": 16,
        "tags": ["feature", "websocket", "real-time"]
    },
    {
        "title": "Optimize database queries",
        "description": "Add indexes and optimize slow queries identified in production logs",
        "priority": "high",
        "estimated_hours": 5,
        "tags": ["database", "performance", "optimization"]
    },
    {
        "title": "Create unit tests for ticket service",
        "description": "Write comprehensive unit tests for ticket CRUD operations and business logic",
        "priority": "medium",
        "estimated_hours": 8,
        "tags": ["testing", "quality"]
    },
    {
        "title": "Implement export to CSV feature",
        "description": "Add ability to export ticket data to CSV format with filtering options",
        "priority": "low",
        "estimated_hours": 4,
        "tags": ["feature", "export"]
    },
    {
        "title": "Fix mobile responsive layout",
        "description": "Fix responsive design issues on mobile devices for ticket detail page",
        "priority": "medium",
        "estimated_hours": 3,
        "tags": ["bug", "ui", "mobile"]
    },
    {
        "title": "Add email notifications",
        "description": "Send email notifications when tickets are assigned or updated",
        "priority": "high",
        "estimated_hours": 6,
        "tags": ["feature", "notifications", "email"]
    },
    {
        "title": "Implement advanced search",
        "description": "Add full-text search with filters for tickets, support multiple criteria",
        "priority": "medium",
        "estimated_hours": 10,
        "tags": ["feature", "search"]
    },
    {
        "title": "Security audit and fixes",
        "description": "Conduct security audit of API endpoints and fix identified vulnerabilities",
        "priority": "urgent",
        "estimated_hours": 12,
        "tags": ["security", "audit"]
    },
    {
        "title": "Create onboarding documentation",
        "description": "Write step-by-step guide for new team members to set up development environment",
        "priority": "low",
        "estimated_hours": 5,
        "tags": ["documentation", "onboarding"]
    }
]

REPORTER_NAMES = [
    "John Smith", "Alice Brown", "Bob Taylor", "Carol White",
    "Dan Green", "Eva Black", "Frank Blue", "Grace Red",
    "Henry Gold", "Iris Silver"
]

STATUSES = ["open", "in_progress", "in_review", "resolved", "closed", "blocked"]
PRIORITIES = ["low", "medium", "high", "urgent"]

# ============================================
# HELPER FUNCTIONS
# ============================================

def create_categories():
    """Create ticket categories"""
    print("\n📁 Creating ticket categories...")
    created_categories = []
    
    for cat in TICKET_CATEGORIES:
        try:
            response = requests.post(
                f"{BASE_URL}/tickets/categories",
                headers=headers,
                json=cat
            )
            if response.status_code == 201:
                created_categories.append(response.json())
                print(f"  ✅ Created category: {cat['name']}")
            else:
                print(f"  ⚠️  Category {cat['name']} may already exist")
        except Exception as e:
            print(f"  ❌ Error creating category {cat['name']}: {e}")
    
    return created_categories

def create_employees():
    """Create employees"""
    print("\n👥 Creating employees...")
    created_employees = []
    
    for emp in EMPLOYEES:
        try:
            response = requests.post(
                f"{BASE_URL}/employees",
                headers=headers,
                json=emp
            )
            if response.status_code == 201:
                created_employees.append(response.json())
                print(f"  ✅ Created employee: {emp['name']} ({emp['position']})")
            else:
                print(f"  ⚠️  Employee {emp['name']} may already exist")
        except Exception as e:
            print(f"  ❌ Error creating employee {emp['name']}: {e}")
    
    return created_employees

def create_tickets(categories, employees):
    """Create tickets with realistic data"""
    print("\n🎫 Creating tickets...")
    created_tickets = []
    
    for i, template in enumerate(TICKET_TEMPLATES):
        # Randomly assign category
        category = random.choice(categories) if categories else None
        
        # Find employees with matching specialization for better assignment
        matching_employees = []
        if category:
            for emp in employees:
                if emp.get('specializations') and category['name'] in emp['specializations']:
                    matching_employees.append(emp)
        
        # Assign to matching employee or random employee
        assigned_to = None
        if random.random() > 0.2:  # 80% chance of being assigned
            if matching_employees:
                assigned_to = random.choice(matching_employees)['id']
            elif employees:
                assigned_to = random.choice(employees)['id']
        
        # Random status
        status = random.choice(STATUSES)
        if not assigned_to:
            status = "open"  # Unassigned tickets are always open
        
        # Create ticket data
        due_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        ticket_data = {
            **template,
            "category_id": category['id'] if category else None,
            "status": status,
            "assigned_to": assigned_to,
            "reported_by": random.choice(REPORTER_NAMES),
            "reporter_email": f"{random.choice(REPORTER_NAMES).lower().replace(' ', '.')}@company.com",
            "due_date": due_date.isoformat()
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/tickets",
                headers=headers,
                json=ticket_data
            )
            if response.status_code == 201:
                ticket = response.json()
                created_tickets.append(ticket)
                print(f"  ✅ Created ticket: {ticket['ticket_number']} - {template['title']}")
            else:
                print(f"  ❌ Error creating ticket: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error creating ticket: {e}")
    
    return created_tickets

def create_comments(tickets, employees):
    """Add comments to some tickets"""
    print("\n💬 Adding comments to tickets...")
    
    comment_templates = [
        "Working on this now, will update soon.",
        "Blocked by dependency, waiting on external team.",
        "Made good progress today, about 60% complete.",
        "Found the root cause, implementing fix.",
        "Code review completed, making requested changes.",
        "This is more complex than initially estimated.",
        "Successfully tested in staging environment.",
        "Merged to main branch, closing ticket.",
        "Need clarification on requirements before proceeding.",
        "Deployed to production, monitoring for issues."
    ]
    
    for ticket in random.sample(tickets, min(10, len(tickets))):
        num_comments = random.randint(1, 4)
        
        for _ in range(num_comments):
            comment_data = {
                "content": random.choice(comment_templates),
                "is_internal": random.random() > 0.7  # 30% internal comments
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/tickets/{ticket['id']}/comments",
                    headers=headers,
                    json=comment_data
                )
                if response.status_code == 201:
                    print(f"  ✅ Added comment to {ticket['ticket_number']}")
            except Exception as e:
                print(f"  ❌ Error adding comment: {e}")

def create_time_logs(tickets, employees):
    """Create time log entries"""
    print("\n⏱️  Creating time log entries...")
    
    for ticket in tickets:
        # Only add time logs for assigned tickets
        if not ticket.get('assigned_to'):
            continue
        
        # Skip some tickets
        if random.random() < 0.3:
            continue
        
        # Create 1-5 time log entries per ticket
        num_logs = random.randint(1, 5)
        
        for _ in range(num_logs):
            hours_worked = round(random.uniform(0.5, 8.0), 2)
            work_date = date.today() - timedelta(days=random.randint(0, 14))
            
            log_data = {
                "employee_id": ticket['assigned_to'],
                "ticket_id": ticket['id'],
                "description": f"Working on {ticket['title']}",
                "hours_worked": hours_worked,
                "work_date": work_date.isoformat(),
                "is_billable": random.random() > 0.1  # 90% billable
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/time",
                    headers=headers,
                    json=log_data
                )
                if response.status_code == 201:
                    print(f"  ✅ Logged {hours_worked}h for {ticket['ticket_number']}")
            except Exception as e:
                print(f"  ❌ Error creating time log: {e}")

# ============================================
# TEST CASES
# ============================================

def test_ticket_creation():
    """Test Case 1: Create a new ticket"""
    print("\n🧪 TEST CASE 1: Create New Ticket")
    
    ticket_data = {
        "title": "Test Ticket - API Integration",
        "description": "This is a test ticket created via API",
        "priority": "medium",
        "estimated_hours": 4,
        "tags": ["test", "api"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tickets",
            headers=headers,
            json=ticket_data
        )
        
        if response.status_code == 201:
            ticket = response.json()
            print(f"  ✅ PASS: Ticket created successfully")
            print(f"     Ticket Number: {ticket['ticket_number']}")
            print(f"     ID: {ticket['id']}")
            return ticket
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return None

def test_ticket_assignment(ticket_id, employee_id):
    """Test Case 2: Assign ticket to employee"""
    print("\n🧪 TEST CASE 2: Assign Ticket to Employee")
    
    try:
        response = requests.post(
            f"{BASE_URL}/tickets/{ticket_id}/assign",
            headers=headers,
            json={"assigned_to": employee_id}
        )
        
        if response.status_code == 200:
            print(f"  ✅ PASS: Ticket assigned successfully")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_add_comment(ticket_id):
    """Test Case 3: Add comment to ticket"""
    print("\n🧪 TEST CASE 3: Add Comment to Ticket")
    
    comment_data = {
        "content": "This is a test comment from the API test suite",
        "is_internal": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tickets/{ticket_id}/comments",
            headers=headers,
            json=comment_data
        )
        
        if response.status_code == 201:
            print(f"  ✅ PASS: Comment added successfully")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_recommendation_system(ticket_id):
    """Test Case 4: Get employee recommendations"""
    print("\n🧪 TEST CASE 4: Get Employee Recommendations")
    
    try:
        response = requests.get(
            f"{BASE_URL}/tickets/{ticket_id}/recommend-employees",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"  ✅ PASS: Got {len(recommendations['recommendations'])} recommendations")
            
            for i, rec in enumerate(recommendations['recommendations'][:3], 1):
                print(f"     {i}. {rec['employee_name']} (Score: {rec['recommendation_score']})")
                if rec['recommendation_reasons']:
                    print(f"        Reasons: {', '.join(rec['recommendation_reasons'])}")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_employee_workload(employee_id):
    """Test Case 5: Check employee workload"""
    print("\n🧪 TEST CASE 5: Check Employee Workload")
    
    try:
        response = requests.get(
            f"{BASE_URL}/employees/{employee_id}/workload",
            headers=headers
        )
        
        if response.status_code == 200:
            workload = response.json()
            print(f"  ✅ PASS: Retrieved workload data")
            print(f"     Employee: {workload['employee_name']}")
            print(f"     Active Tickets: {workload['active_tickets']}")
            print(f"     Completed Tickets: {workload['completed_tickets']}")
            print(f"     Total Hours Logged: {workload['total_hours_logged']}")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_time_log_creation(employee_id, ticket_id):
    """Test Case 6: Create time log entry"""
    print("\n🧪 TEST CASE 6: Create Time Log Entry")
    
    log_data = {
        "employee_id": employee_id,
        "ticket_id": ticket_id,
        "description": "Test time log entry",
        "hours_worked": 2.5,
        "work_date": date.today().isoformat(),
        "is_billable": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/time",
            headers=headers,
            json=log_data
        )
        
        if response.status_code == 201:
            print(f"  ✅ PASS: Time log created successfully")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_employee_performance(employee_id):
    """Test Case 7: Get employee performance metrics"""
    print("\n🧪 TEST CASE 7: Get Employee Performance Metrics")
    
    try:
        response = requests.get(
            f"{BASE_URL}/employees/{employee_id}/performance?days=30",
            headers=headers
        )
        
        if response.status_code == 200:
            perf = response.json()
            print(f"  ✅ PASS: Retrieved performance data")
            print(f"     Total Tickets: {perf['tickets']['total']}")
            print(f"     Completed: {perf['tickets']['completed']}")
            print(f"     Completion Rate: {perf['tickets']['completion_rate']}%")
            print(f"     Total Hours: {perf['time']['total_hours']}")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_ticket_stats():
    """Test Case 8: Get ticket statistics"""
    print("\n🧪 TEST CASE 8: Get Ticket Statistics")
    
    try:
        response = requests.get(
            f"{BASE_URL}/tickets/stats/overview",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"  ✅ PASS: Retrieved ticket statistics")
            print(f"     Total Tickets: {stats['total']}")
            print(f"     Open: {stats['open']}")
            print(f"     In Progress: {stats['in_progress']}")
            print(f"     Resolved: {stats['resolved']}")
            print(f"     Urgent: {stats['urgent']}")
            return True
        else:
            print(f"  ❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("🚀 TicketFlow - Dummy Data Generator & Test Suite")
    print("=" * 60)
    
    if "YOUR_SUPABASE_JWT_TOKEN_HERE" in AUTH_TOKEN:
        print("\n⚠️  WARNING: Please update AUTH_TOKEN with your actual token")
        print("   1. Log in through the frontend")
        print("   2. Get your token from browser dev tools (localStorage)")
        print("   3. Update AUTH_TOKEN in this script")
        return
    
    # Generate dummy data
    print("\n📊 GENERATING DUMMY DATA")
    print("-" * 60)
    
    categories = create_categories()
    employees = create_employees()
    tickets = create_tickets(categories, employees)
    create_comments(tickets, employees)
    create_time_logs(tickets, employees)
    
    print("\n✅ Dummy data generation complete!")
    print(f"   Categories: {len(categories)}")
    print(f"   Employees: {len(employees)}")
    print(f"   Tickets: {len(tickets)}")
    
    # Run test cases
    print("\n" + "=" * 60)
    print("🧪 RUNNING TEST CASES")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Create ticket
    test_ticket = test_ticket_creation()
    test_results.append(("Create Ticket", test_ticket is not None))
    
    if test_ticket and employees:
        test_employee = employees[0]
        
        # Test 2: Assign ticket
        test_results.append(("Assign Ticket", test_ticket_assignment(test_ticket['id'], test_employee['id'])))
        
        # Test 3: Add comment
        test_results.append(("Add Comment", test_add_comment(test_ticket['id'])))
        
        # Test 4: Recommendations
        test_results.append(("Get Recommendations", test_recommendation_system(test_ticket['id'])))
        
        # Test 5: Employee workload
        test_results.append(("Employee Workload", test_employee_workload(test_employee['id'])))
        
        # Test 6: Time log
        test_results.append(("Create Time Log", test_time_log_creation(test_employee['id'], test_ticket['id'])))
        
        # Test 7: Performance metrics
        test_results.append(("Performance Metrics", test_employee_performance(test_employee['id'])))
    
    # Test 8: Ticket stats
    test_results.append(("Ticket Statistics", test_ticket_stats()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed ({round(passed/total*100, 1)}%)")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
