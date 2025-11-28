from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date, timedelta
from config.supabase_client import supabase
from middleware.auth import get_current_user

router = APIRouter()

# ============================================
# PYDANTIC MODELS
# ============================================

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    position: str
    department: Optional[str] = None
    phone: Optional[str] = None
    salary: Optional[float] = None
    specializations: Optional[List[str]] = []
    avatar_url: Optional[str] = None
    is_active: bool = True

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    salary: Optional[float] = None
    specializations: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

# ============================================
# EMPLOYEE CRUD ENDPOINTS
# ============================================

@router.get("/")
async def get_employees(
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get all employees with optional filtering"""
    try:
        query = supabase.table('employees')\
            .select('*')\
            .eq('user_id', user.id)
        
        if department:
            query = query.eq('department', department)
        if is_active is not None:
            query = query.eq('is_active', is_active)
        if search:
            query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%,position.ilike.%{search}%")
        
        response = query.order('created_at', desc=True).execute()
        
        return {"employees": response.data, "count": len(response.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employees: {str(e)}")

@router.get("/{employee_id}")
async def get_employee(employee_id: str, user=Depends(get_current_user)):
    """Get a single employee by ID with detailed information"""
    try:
        response = supabase.table('employees')\
            .select('*')\
            .eq('id', employee_id)\
            .eq('user_id', user.id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee = response.data
        
        # Get assigned tickets
        tickets_response = supabase.table('tickets')\
            .select('id, ticket_number, title, status, priority, created_at, due_date')\
            .eq('assigned_to', employee_id)\
            .order('created_at', desc=True)\
            .limit(50)\
            .execute()
        
        employee["assigned_tickets"] = tickets_response.data
        
        # Get recent time logs
        time_logs_response = supabase.table('employee_time_logs')\
            .select('*')\
            .eq('employee_id', employee_id)\
            .order('work_date', desc=True)\
            .limit(20)\
            .execute()
        
        employee["recent_time_logs"] = time_logs_response.data
        
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee: {str(e)}")

@router.post("/", status_code=201)
async def create_employee(employee: EmployeeCreate, user=Depends(get_current_user)):
    """Create a new employee"""
    try:
        response = supabase.table('employees')\
            .insert({
                'name': employee.name,
                'email': employee.email,
                'position': employee.position,
                'department': employee.department,
                'phone': employee.phone,
                'salary': employee.salary,
                'specializations': employee.specializations,
                'avatar_url': employee.avatar_url,
                'is_active': employee.is_active,
                'user_id': user.id
            })\
            .execute()
        
        return response.data[0]
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@router.put("/{employee_id}")
async def update_employee(employee_id: str, employee: EmployeeUpdate, user=Depends(get_current_user)):
    """Update an employee"""
    try:
        update_data = {k: v for k, v in employee.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table('employees')\
            .update(update_data)\
            .eq('id', employee_id)\
            .eq('user_id', user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")

@router.delete("/{employee_id}")
async def delete_employee(employee_id: str, user=Depends(get_current_user)):
    """Delete an employee"""
    try:
        # Check if employee has assigned tickets
        tickets_check = supabase.table('tickets')\
            .select('id')\
            .eq('assigned_to', employee_id)\
            .neq('status', 'closed')\
            .execute()
        
        if tickets_check.data:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete employee with {len(tickets_check.data)} active assigned ticket(s)"
            )
        
        response = supabase.table('employees')\
            .delete()\
            .eq('id', employee_id)\
            .eq('user_id', user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {"message": "Employee deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {str(e)}")

# ============================================
# EMPLOYEE WORKLOAD & STATISTICS
# ============================================

@router.get("/{employee_id}/tickets")
async def get_employee_tickets(
    employee_id: str,
    status: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get all tickets assigned to an employee"""
    try:
        # Verify employee exists
        emp_check = supabase.table('employees')\
            .select('id, name')\
            .eq('id', employee_id)\
            .eq('user_id', user.id)\
            .single()\
            .execute()
        
        if not emp_check.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        query = supabase.table('ticket_summary')\
            .select('*')\
            .eq('employee_id', employee_id)
        
        if status:
            query = query.eq('status', status)
        
        response = query.order('created_at', desc=True).execute()
        
        return {
            "employee": emp_check.data,
            "tickets": response.data,
            "count": len(response.data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}/workload")
async def get_employee_workload(
    employee_id: str,
    user=Depends(get_current_user)
):
    """Get detailed workload information for an employee"""
    try:
        response = supabase.table('employee_workload')\
            .select('*')\
            .eq('employee_id', employee_id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}/performance")
async def get_employee_performance(
    employee_id: str,
    days: int = Query(30, ge=1, le=365),
    user=Depends(get_current_user)
):
    """Get employee performance metrics for the specified period"""
    try:
        # Verify employee
        emp_check = supabase.table('employees')\
            .select('id, name, position, department, specializations')\
            .eq('id', employee_id)\
            .eq('user_id', user.id)\
            .single()\
            .execute()
        
        if not emp_check.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Get tickets
        tickets_response = supabase.table('tickets')\
            .select('*')\
            .eq('assigned_to', employee_id)\
            .gte('created_at', start_date.isoformat())\
            .execute()
        
        tickets = tickets_response.data
        
        # Get time logs
        time_logs_response = supabase.table('employee_time_logs')\
            .select('*')\
            .eq('employee_id', employee_id)\
            .gte('work_date', start_date.isoformat())\
            .execute()
        
        time_logs = time_logs_response.data
        
        # Calculate metrics
        total_tickets = len(tickets)
        completed_tickets = len([t for t in tickets if t['status'] in ['resolved', 'closed']])
        active_tickets = len([t for t in tickets if t['status'] not in ['resolved', 'closed']])
        
        total_hours = sum(log['hours_worked'] for log in time_logs)
        billable_hours = sum(log['hours_worked'] for log in time_logs if log.get('is_billable'))
        
        # Calculate average completion time
        completed_with_times = [
            t for t in tickets 
            if t['status'] in ['resolved', 'closed'] and t.get('assigned_at') and t.get('completed_at')
        ]
        
        avg_completion_hours = 0
        if completed_with_times:
            total_completion_time = 0
            for t in completed_with_times:
                assigned = datetime.fromisoformat(t['assigned_at'].replace('Z', '+00:00'))
                completed = datetime.fromisoformat(t['completed_at'].replace('Z', '+00:00'))
                total_completion_time += (completed - assigned).total_seconds() / 3600
            avg_completion_hours = total_completion_time / len(completed_with_times)
        
        # Priority breakdown
        priority_counts = {}
        for ticket in tickets:
            priority = ticket.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "employee": emp_check.data,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().date().isoformat(),
                "days": days
            },
            "tickets": {
                "total": total_tickets,
                "completed": completed_tickets,
                "active": active_tickets,
                "completion_rate": round((completed_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2),
                "by_priority": priority_counts
            },
            "time": {
                "total_hours": round(total_hours, 2),
                "billable_hours": round(billable_hours, 2),
                "avg_hours_per_day": round(total_hours / days, 2) if days > 0 else 0,
                "avg_completion_hours": round(avg_completion_hours, 2)
            },
            "recent_tickets": tickets[:10]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SPECIALIZATIONS
# ============================================

@router.get("/specializations/list")
async def list_specializations(user=Depends(get_current_user)):
    """Get all unique specializations across all employees"""
    try:
        response = supabase.table('employees')\
            .select('specializations')\
            .eq('user_id', user.id)\
            .execute()
        
        all_specs = set()
        for emp in response.data:
            if emp.get('specializations'):
                all_specs.update(emp['specializations'])
        
        return {"specializations": sorted(list(all_specs))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-specialization/{specialization}")
async def get_employees_by_specialization(
    specialization: str,
    user=Depends(get_current_user)
):
    """Get all employees with a specific specialization"""
    try:
        response = supabase.table('employees')\
            .select('*')\
            .eq('user_id', user.id)\
            .execute()
        
        # Filter employees with matching specialization
        matching_employees = [
            emp for emp in response.data
            if emp.get('specializations') and specialization.lower() in [s.lower() for s in emp['specializations']]
        ]
        
        return {"specialization": specialization, "employees": matching_employees, "count": len(matching_employees)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DEPARTMENT STATISTICS
# ============================================

@router.get("/departments/list")
async def list_departments(user=Depends(get_current_user)):
    """Get all unique departments"""
    try:
        response = supabase.table('employees')\
            .select('department')\
            .eq('user_id', user.id)\
            .execute()
        
        departments = set(emp['department'] for emp in response.data if emp.get('department'))
        
        return {"departments": sorted(list(departments))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments/{department}/stats")
async def get_department_stats(
    department: str,
    user=Depends(get_current_user)
):
    """Get statistics for a specific department"""
    try:
        # Get employees in department
        emp_response = supabase.table('employees')\
            .select('id, name, position')\
            .eq('user_id', user.id)\
            .eq('department', department)\
            .execute()
        
        employees = emp_response.data
        employee_ids = [emp['id'] for emp in employees]
        
        if not employee_ids:
            return {
                "department": department,
                "employee_count": 0,
                "total_tickets": 0,
                "active_tickets": 0,
                "completed_tickets": 0
            }
        
        # Get tickets for department employees
        tickets_response = supabase.table('tickets')\
            .select('status')\
            .in_('assigned_to', employee_ids)\
            .execute()
        
        tickets = tickets_response.data
        
        return {
            "department": department,
            "employee_count": len(employees),
            "employees": employees,
            "total_tickets": len(tickets),
            "active_tickets": len([t for t in tickets if t['status'] not in ['resolved', 'closed']]),
            "completed_tickets": len([t for t in tickets if t['status'] in ['resolved', 'closed']])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
