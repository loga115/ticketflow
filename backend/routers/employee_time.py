from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, timedelta
from config.supabase_client import supabase
from middleware.auth import get_current_user

router = APIRouter()

# ============================================
# PYDANTIC MODELS
# ============================================

class TimeLogCreate(BaseModel):
    employee_id: str
    ticket_id: Optional[str] = None
    description: str
    hours_worked: float = Field(gt=0, le=24)
    work_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_billable: bool = True

class TimeLogUpdate(BaseModel):
    employee_id: Optional[str] = None
    ticket_id: Optional[str] = None
    description: Optional[str] = None
    hours_worked: Optional[float] = Field(None, gt=0, le=24)
    work_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_billable: Optional[bool] = None

class TimeLogBatch(BaseModel):
    logs: List[TimeLogCreate]

# ============================================
# TIME LOG CRUD ENDPOINTS
# ============================================

@router.get("/")
async def list_time_logs(
    employee_id: Optional[str] = None,
    ticket_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_billable: Optional[bool] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List employee time logs with optional filtering"""
    try:
        query = supabase.table("employee_time_logs")\
            .select("*, employees(id, name, position, department), tickets(ticket_number, title)")\
            .eq("user_id", current_user.id)
        
        if employee_id:
            query = query.eq("employee_id", employee_id)
        if ticket_id:
            query = query.eq("ticket_id", ticket_id)
        if start_date:
            query = query.gte("work_date", start_date.isoformat())
        if end_date:
            query = query.lte("work_date", end_date.isoformat())
        if is_billable is not None:
            query = query.eq("is_billable", is_billable)
        
        response = query.order("work_date", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return {"time_logs": response.data, "count": len(response.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{log_id}")
async def get_time_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single time log entry"""
    try:
        response = supabase.table("employee_time_logs")\
            .select("*, employees(id, name, position), tickets(ticket_number, title, status)")\
            .eq("id", log_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Time log not found")
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
async def create_time_log(
    log: TimeLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new time log entry"""
    try:
        # Verify employee exists
        emp_check = supabase.table("employees")\
            .select("id")\
            .eq("id", log.employee_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not emp_check.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Verify ticket if provided
        if log.ticket_id:
            ticket_check = supabase.table("tickets")\
                .select("id")\
                .eq("id", log.ticket_id)\
                .eq("user_id", current_user.id)\
                .single()\
                .execute()
            
            if not ticket_check.data:
                raise HTTPException(status_code=404, detail="Ticket not found")
        
        log_data = {
            "user_id": current_user.id,
            "employee_id": log.employee_id,
            "ticket_id": log.ticket_id,
            "description": log.description,
            "hours_worked": log.hours_worked,
            "work_date": log.work_date.isoformat(),
            "start_time": log.start_time.isoformat() if log.start_time else None,
            "end_time": log.end_time.isoformat() if log.end_time else None,
            "is_billable": log.is_billable
        }
        
        response = supabase.table("employee_time_logs").insert(log_data).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", status_code=201)
async def create_time_logs_batch(
    batch: TimeLogBatch,
    current_user: dict = Depends(get_current_user)
):
    """Create multiple time log entries at once"""
    try:
        log_data_list = []
        
        for log in batch.logs:
            log_data_list.append({
                "user_id": current_user.id,
                "employee_id": log.employee_id,
                "ticket_id": log.ticket_id,
                "description": log.description,
                "hours_worked": log.hours_worked,
                "work_date": log.work_date.isoformat(),
                "start_time": log.start_time.isoformat() if log.start_time else None,
                "end_time": log.end_time.isoformat() if log.end_time else None,
                "is_billable": log.is_billable
            })
        
        response = supabase.table("employee_time_logs").insert(log_data_list).execute()
        
        return {"created": len(response.data), "time_logs": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{log_id}")
async def update_time_log(
    log_id: str,
    log: TimeLogUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a time log entry"""
    try:
        update_data = {}
        for key, value in log.dict().items():
            if value is not None:
                if key in ["work_date", "start_time", "end_time"] and isinstance(value, (date, datetime)):
                    update_data[key] = value.isoformat()
                else:
                    update_data[key] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("employee_time_logs")\
            .update(update_data)\
            .eq("id", log_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Time log not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{log_id}")
async def delete_time_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a time log entry"""
    try:
        response = supabase.table("employee_time_logs")\
            .delete()\
            .eq("id", log_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Time log not found")
        
        return {"message": "Time log deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# EMPLOYEE TIME REVIEW & ANALYTICS
# ============================================

@router.get("/review/employee/{employee_id}")
async def review_employee_time(
    employee_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Review time logs for a specific employee with ticket assignment and completion metrics
    """
    try:
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get employee info
        emp_response = supabase.table("employees")\
            .select("*")\
            .eq("id", employee_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not emp_response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee = emp_response.data
        
        # Get time logs for period
        logs_response = supabase.table("employee_time_logs")\
            .select("*, tickets(ticket_number, title, status, priority)")\
            .eq("employee_id", employee_id)\
            .gte("work_date", start_date.isoformat())\
            .lte("work_date", end_date.isoformat())\
            .order("work_date", desc=True)\
            .execute()
        
        logs = logs_response.data
        
        # Get tickets assigned in this period
        tickets_response = supabase.table("tickets")\
            .select("*")\
            .eq("assigned_to", employee_id)\
            .gte("created_at", start_date.isoformat())\
            .lte("created_at", end_date.isoformat())\
            .execute()
        
        tickets_assigned = tickets_response.data
        
        # Get tickets completed in this period
        completed_tickets_response = supabase.table("tickets")\
            .select("*")\
            .eq("assigned_to", employee_id)\
            .in_("status", ["resolved", "closed"])\
            .gte("completed_at", start_date.isoformat())\
            .lte("completed_at", end_date.isoformat())\
            .execute()
        
        tickets_completed = completed_tickets_response.data
        
        # Calculate metrics
        total_hours = sum(log["hours_worked"] for log in logs)
        billable_hours = sum(log["hours_worked"] for log in logs if log.get("is_billable"))
        
        # Group logs by ticket
        ticket_time_map = {}
        for log in logs:
            if log.get("ticket_id"):
                ticket_id = log["ticket_id"]
                if ticket_id not in ticket_time_map:
                    ticket_time_map[ticket_id] = {
                        "ticket_info": log.get("tickets"),
                        "total_hours": 0,
                        "log_count": 0
                    }
                ticket_time_map[ticket_id]["total_hours"] += log["hours_worked"]
                ticket_time_map[ticket_id]["log_count"] += 1
        
        # Calculate completion times for completed tickets
        completion_times = []
        for ticket in tickets_completed:
            if ticket.get("assigned_at") and ticket.get("completed_at"):
                assigned = datetime.fromisoformat(ticket["assigned_at"].replace('Z', '+00:00'))
                completed = datetime.fromisoformat(ticket["completed_at"].replace('Z', '+00:00'))
                hours = (completed - assigned).total_seconds() / 3600
                completion_times.append({
                    "ticket_number": ticket["ticket_number"],
                    "title": ticket["title"],
                    "hours_to_complete": round(hours, 2),
                    "hours_logged": ticket.get("actual_hours", 0)
                })
        
        avg_completion_time = sum(ct["hours_to_complete"] for ct in completion_times) / len(completion_times) if completion_times else 0
        
        # Daily breakdown
        daily_hours = {}
        for log in logs:
            work_date = log["work_date"]
            if work_date not in daily_hours:
                daily_hours[work_date] = {
                    "date": work_date,
                    "total_hours": 0,
                    "billable_hours": 0,
                    "log_count": 0
                }
            daily_hours[work_date]["total_hours"] += log["hours_worked"]
            if log.get("is_billable"):
                daily_hours[work_date]["billable_hours"] += log["hours_worked"]
            daily_hours[work_date]["log_count"] += 1
        
        return {
            "employee": employee,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days + 1
            },
            "time_summary": {
                "total_hours": round(total_hours, 2),
                "billable_hours": round(billable_hours, 2),
                "non_billable_hours": round(total_hours - billable_hours, 2),
                "avg_hours_per_day": round(total_hours / ((end_date - start_date).days + 1), 2),
                "total_logs": len(logs)
            },
            "ticket_metrics": {
                "assigned": len(tickets_assigned),
                "completed": len(tickets_completed),
                "completion_rate": round((len(tickets_completed) / len(tickets_assigned) * 100) if tickets_assigned else 0, 2),
                "avg_completion_hours": round(avg_completion_time, 2),
                "tickets_with_time": len(ticket_time_map)
            },
            "time_by_ticket": list(ticket_time_map.values()),
            "completed_tickets": completion_times,
            "daily_breakdown": sorted(daily_hours.values(), key=lambda x: x["date"], reverse=True),
            "recent_logs": logs[:20]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/review/ticket/{ticket_id}")
async def review_ticket_time(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Review all time logs for a specific ticket"""
    try:
        # Get ticket info
        ticket_response = supabase.table("tickets")\
            .select("*, employees(name, position)")\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not ticket_response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket = ticket_response.data
        
        # Get all time logs for this ticket
        logs_response = supabase.table("employee_time_logs")\
            .select("*, employees(name, position, department)")\
            .eq("ticket_id", ticket_id)\
            .order("work_date", desc=False)\
            .execute()
        
        logs = logs_response.data
        
        total_hours = sum(log["hours_worked"] for log in logs)
        estimated_hours = ticket.get("estimated_hours", 0) or 0
        
        # Group by employee
        employee_hours = {}
        for log in logs:
            emp_id = log["employee_id"]
            if emp_id not in employee_hours:
                employee_hours[emp_id] = {
                    "employee": log.get("employees"),
                    "hours": 0,
                    "log_count": 0
                }
            employee_hours[emp_id]["hours"] += log["hours_worked"]
            employee_hours[emp_id]["log_count"] += 1
        
        return {
            "ticket": ticket,
            "time_summary": {
                "total_hours_logged": round(total_hours, 2),
                "estimated_hours": round(estimated_hours, 2),
                "variance": round(total_hours - estimated_hours, 2),
                "variance_percentage": round(((total_hours - estimated_hours) / estimated_hours * 100) if estimated_hours > 0 else 0, 2),
                "total_logs": len(logs)
            },
            "by_employee": list(employee_hours.values()),
            "time_logs": logs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_time_stats_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get overall time tracking statistics"""
    try:
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get all time logs for period
        logs_response = supabase.table("employee_time_logs")\
            .select("*, employees(name, department)")\
            .eq("user_id", current_user.id)\
            .gte("work_date", start_date.isoformat())\
            .lte("work_date", end_date.isoformat())\
            .execute()
        
        logs = logs_response.data
        
        total_hours = sum(log["hours_worked"] for log in logs)
        billable_hours = sum(log["hours_worked"] for log in logs if log.get("is_billable"))
        
        # By employee
        employee_hours = {}
        for log in logs:
            emp_id = log["employee_id"]
            if emp_id not in employee_hours:
                employee_hours[emp_id] = {
                    "employee_name": log.get("employees", {}).get("name", "Unknown"),
                    "department": log.get("employees", {}).get("department"),
                    "hours": 0
                }
            employee_hours[emp_id]["hours"] += log["hours_worked"]
        
        # By department
        dept_hours = {}
        for log in logs:
            dept = log.get("employees", {}).get("department", "Unassigned")
            dept_hours[dept] = dept_hours.get(dept, 0) + log["hours_worked"]
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days + 1
            },
            "summary": {
                "total_hours": round(total_hours, 2),
                "billable_hours": round(billable_hours, 2),
                "non_billable_hours": round(total_hours - billable_hours, 2),
                "billable_percentage": round((billable_hours / total_hours * 100) if total_hours > 0 else 0, 2),
                "total_logs": len(logs)
            },
            "by_employee": sorted(employee_hours.values(), key=lambda x: x["hours"], reverse=True),
            "by_department": [{"department": k, "hours": round(v, 2)} for k, v in sorted(dept_hours.items(), key=lambda x: x[1], reverse=True)]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/trends")
async def get_time_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get time logging trends over specified period"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        logs_response = supabase.table("employee_time_logs")\
            .select("work_date, hours_worked, is_billable")\
            .eq("user_id", current_user.id)\
            .gte("work_date", start_date.isoformat())\
            .lte("work_date", end_date.isoformat())\
            .execute()
        
        logs = logs_response.data
        
        # Daily aggregation
        daily_data = {}
        current = start_date
        while current <= end_date:
            daily_data[current.isoformat()] = {
                "date": current.isoformat(),
                "total_hours": 0,
                "billable_hours": 0,
                "log_count": 0
            }
            current += timedelta(days=1)
        
        for log in logs:
            date_key = log["work_date"]
            if date_key in daily_data:
                daily_data[date_key]["total_hours"] += log["hours_worked"]
                if log.get("is_billable"):
                    daily_data[date_key]["billable_hours"] += log["hours_worked"]
                daily_data[date_key]["log_count"] += 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "daily_trends": sorted(daily_data.values(), key=lambda x: x["date"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

