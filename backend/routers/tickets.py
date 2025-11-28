from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from middleware.auth import get_current_user
from config.supabase_client import supabase

router = APIRouter()

# ============================================
# PYDANTIC MODELS
# ============================================

class TicketCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3b82f6"
    icon: Optional[str] = None

class TicketCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    status: str = "open"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    reported_by: Optional[str] = None
    reporter_email: Optional[EmailStr] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = []

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    reported_by: Optional[str] = None
    reporter_email: Optional[EmailStr] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = None

class TicketAssign(BaseModel):
    assigned_to: Optional[str] = None  # employee_id or null to unassign

class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False

class CommentUpdate(BaseModel):
    content: str

# ============================================
# TICKET CATEGORY ENDPOINTS
# ============================================

@router.get("/categories")
async def list_categories(current_user: dict = Depends(get_current_user)):
    """List all ticket categories"""
    try:
        response = supabase.table("ticket_categories")\
            .select("*")\
            .eq("user_id", current_user.id)\
            .order("name")\
            .execute()
        
        return {"categories": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/categories", status_code=201)
async def create_category(
    category: TicketCategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new ticket category"""
    try:
        response = supabase.table("ticket_categories").insert({
            "user_id": current_user.id,
            "name": category.name,
            "description": category.description,
            "color": category.color,
            "icon": category.icon
        }).execute()
        
        return response.data[0]
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/categories/{category_id}")
async def update_category(
    category_id: str,
    category: TicketCategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a ticket category"""
    try:
        update_data = {k: v for k, v in category.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("ticket_categories")\
            .update(update_data)\
            .eq("id", category_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a ticket category"""
    try:
        response = supabase.table("ticket_categories")\
            .delete()\
            .eq("id", category_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {"message": "Category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TICKET ENDPOINTS
# ============================================

@router.get("/")
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List tickets with optional filtering"""
    try:
        query = supabase.table("ticket_summary")\
            .select("*")\
            .eq("user_id", current_user.id)
        
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
        if assigned_to:
            query = query.eq("employee_id", assigned_to)
        if category_id:
            query = query.eq("category_id", category_id)
        if search:
            query = query.or_(f"title.ilike.%{search}%,description.ilike.%{search}%,ticket_number.ilike.%{search}%")
        
        response = query.order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return {"tickets": response.data, "count": len(response.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single ticket with details"""
    try:
        # Get ticket from summary view
        response = supabase.table("ticket_summary")\
            .select("*")\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket = response.data
        
        # Get comments
        comments_response = supabase.table("ticket_comments")\
            .select("*, employees(name, email)")\
            .eq("ticket_id", ticket_id)\
            .order("created_at", desc=False)\
            .execute()
        
        ticket["comments"] = comments_response.data
        
        # Get history
        history_response = supabase.table("ticket_history")\
            .select("*, employees(name)")\
            .eq("ticket_id", ticket_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        ticket["history"] = history_response.data
        
        # Get watchers
        watchers_response = supabase.table("ticket_watchers")\
            .select("*, employees(id, name, email)")\
            .eq("ticket_id", ticket_id)\
            .execute()
        
        ticket["watchers"] = watchers_response.data
        
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
async def create_ticket(
    ticket: TicketCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new ticket"""
    try:
        ticket_data = {
            "user_id": current_user.id,
            "title": ticket.title,
            "description": ticket.description,
            "category_id": ticket.category_id,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_to": ticket.assigned_to,
            "reported_by": ticket.reported_by,
            "reporter_email": ticket.reporter_email,
            "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
            "estimated_hours": ticket.estimated_hours,
            "tags": ticket.tags
        }
        
        response = supabase.table("tickets").insert(ticket_data).execute()
        created_ticket = response.data[0]
        
        # Log creation in history
        supabase.table("ticket_history").insert({
            "ticket_id": created_ticket["id"],
            "user_id": current_user.id,
            "action": "created",
            "description": f"Ticket {created_ticket['ticket_number']} created"
        }).execute()
        
        return created_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    ticket: TicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a ticket"""
    try:
        update_data = {}
        for key, value in ticket.dict().items():
            if value is not None:
                if key == "due_date" and isinstance(value, datetime):
                    update_data[key] = value.isoformat()
                else:
                    update_data[key] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("tickets")\
            .update(update_data)\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a ticket"""
    try:
        response = supabase.table("tickets")\
            .delete()\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {"message": "Ticket deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    assignment: TicketAssign,
    current_user: dict = Depends(get_current_user)
):
    """Assign or reassign a ticket to an employee"""
    try:
        # Verify employee exists if assigning
        if assignment.assigned_to:
            emp_check = supabase.table("employees")\
                .select("id, name")\
                .eq("id", assignment.assigned_to)\
                .eq("user_id", current_user.id)\
                .single()\
                .execute()
            
            if not emp_check.data:
                raise HTTPException(status_code=404, detail="Employee not found")
        
        response = supabase.table("tickets")\
            .update({"assigned_to": assignment.assigned_to})\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TICKET COMMENT ENDPOINTS
# ============================================

@router.get("/{ticket_id}/comments")
async def list_comments(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all comments for a ticket"""
    try:
        # Verify ticket access
        ticket_check = supabase.table("tickets")\
            .select("id")\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not ticket_check.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        response = supabase.table("ticket_comments")\
            .select("*, employees(id, name, email)")\
            .eq("ticket_id", ticket_id)\
            .order("created_at")\
            .execute()
        
        return {"comments": response.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ticket_id}/comments", status_code=201)
async def create_comment(
    ticket_id: str,
    comment: CommentCreate,
    employee_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a ticket"""
    try:
        # Verify ticket access
        ticket_check = supabase.table("tickets")\
            .select("id, ticket_number")\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not ticket_check.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        response = supabase.table("ticket_comments").insert({
            "ticket_id": ticket_id,
            "user_id": current_user.id,
            "employee_id": employee_id,
            "content": comment.content,
            "is_internal": comment.is_internal
        }).execute()
        
        # Log comment in history
        supabase.table("ticket_history").insert({
            "ticket_id": ticket_id,
            "user_id": current_user.id,
            "employee_id": employee_id,
            "action": "commented",
            "description": f"Added a {'internal ' if comment.is_internal else ''}comment"
        }).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}/comments/{comment_id}")
async def update_comment(
    ticket_id: str,
    comment_id: str,
    comment: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a comment"""
    try:
        response = supabase.table("ticket_comments")\
            .update({"content": comment.content})\
            .eq("id", comment_id)\
            .eq("ticket_id", ticket_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticket_id}/comments/{comment_id}")
async def delete_comment(
    ticket_id: str,
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment"""
    try:
        response = supabase.table("ticket_comments")\
            .delete()\
            .eq("id", comment_id)\
            .eq("ticket_id", ticket_id)\
            .eq("user_id", current_user.id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        return {"message": "Comment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TICKET STATISTICS
# ============================================

@router.get("/stats/overview")
async def get_ticket_stats(current_user: dict = Depends(get_current_user)):
    """Get overall ticket statistics"""
    try:
        # Get all tickets
        response = supabase.table("tickets")\
            .select("status, priority, assigned_to")\
            .eq("user_id", current_user.id)\
            .execute()
        
        tickets = response.data
        
        stats = {
            "total": len(tickets),
            "open": len([t for t in tickets if t["status"] == "open"]),
            "in_progress": len([t for t in tickets if t["status"] == "in_progress"]),
            "in_review": len([t for t in tickets if t["status"] == "in_review"]),
            "resolved": len([t for t in tickets if t["status"] == "resolved"]),
            "closed": len([t for t in tickets if t["status"] == "closed"]),
            "blocked": len([t for t in tickets if t["status"] == "blocked"]),
            "unassigned": len([t for t in tickets if not t["assigned_to"]]),
            "urgent": len([t for t in tickets if t["priority"] == "urgent"]),
            "high": len([t for t in tickets if t["priority"] == "high"]),
            "medium": len([t for t in tickets if t["priority"] == "medium"]),
            "low": len([t for t in tickets if t["priority"] == "low"])
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/by-category")
async def get_tickets_by_category(current_user: dict = Depends(get_current_user)):
    """Get ticket count by category"""
    try:
        response = supabase.table("ticket_summary")\
            .select("category_id, category_name, category_color")\
            .eq("user_id", current_user.id)\
            .execute()
        
        # Count tickets by category
        category_counts = {}
        for ticket in response.data:
            cat_id = ticket["category_id"] or "uncategorized"
            cat_name = ticket["category_name"] or "Uncategorized"
            cat_color = ticket["category_color"] or "#gray"
            
            if cat_id not in category_counts:
                category_counts[cat_id] = {
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "color": cat_color,
                    "count": 0
                }
            category_counts[cat_id]["count"] += 1
        
        return {"categories": list(category_counts.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TICKET RECOMMENDATIONS
# ============================================

@router.get("/{ticket_id}/recommend-employees")
async def recommend_employees(
    ticket_id: str,
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get recommended employees for a ticket based on specializations and workload"""
    try:
        # Get ticket with category
        ticket_response = supabase.table("tickets")\
            .select("*, ticket_categories(name)")\
            .eq("id", ticket_id)\
            .eq("user_id", current_user.id)\
            .single()\
            .execute()
        
        if not ticket_response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket = ticket_response.data
        category_name = ticket.get("ticket_categories", {}).get("name") if ticket.get("ticket_categories") else None
        
        # Get employee workload
        workload_response = supabase.table("employee_workload")\
            .select("*")\
            .execute()
        
        employees = workload_response.data
        
        # Score employees
        scored_employees = []
        for emp in employees:
            score = 0
            reasons = []
            
            # Check if employee is active
            if not emp.get("is_active", True):
                continue
            
            # Specialization match (highest weight)
            if emp.get("specializations") and category_name:
                if category_name.lower() in [s.lower() for s in emp["specializations"]]:
                    score += 50
                    reasons.append(f"Specializes in {category_name}")
            
            # Workload consideration (prefer less busy employees)
            active = emp.get("active_tickets", 0)
            if active == 0:
                score += 30
                reasons.append("Available (no active tickets)")
            elif active <= 2:
                score += 20
                reasons.append("Light workload")
            elif active <= 5:
                score += 10
                reasons.append("Moderate workload")
            else:
                score -= 10
                reasons.append("Heavy workload")
            
            # Experience (based on completed tickets)
            completed = emp.get("completed_tickets", 0)
            if completed > 20:
                score += 15
                reasons.append("Highly experienced")
            elif completed > 10:
                score += 10
                reasons.append("Experienced")
            elif completed > 5:
                score += 5
                reasons.append("Some experience")
            
            # Add some randomness to prevent always recommending same person
            import random
            score += random.randint(0, 5)
            
            scored_employees.append({
                **emp,
                "recommendation_score": score,
                "recommendation_reasons": reasons
            })
        
        # Sort by score and return top N
        scored_employees.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return {
            "ticket_id": ticket_id,
            "ticket_title": ticket["title"],
            "category": category_name,
            "recommendations": scored_employees[:limit]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# EMPLOYEE-SIDE TICKET UPDATES
# ============================================

class EmployeeTicketUpdate(BaseModel):
    """Model for employees to update their assigned tickets"""
    status: Optional[str] = None
    description: Optional[str] = None  # Add notes/progress updates
    estimated_hours: Optional[float] = None

class PartialTicketCreate(BaseModel):
    """Model for creating tickets with minimal info - admin fills in details"""
    title: str
    description: Optional[str] = None
    reporter_email: Optional[EmailStr] = None
    reported_by: Optional[str] = None
    tags: Optional[List[str]] = []

@router.patch("/employee/{ticket_id}")
async def employee_update_ticket(
    ticket_id: str,
    update_data: EmployeeTicketUpdate,
    user=Depends(get_current_user)
):
    """
    Allow employees to update status and add notes to their assigned tickets.
    Creates notification for admin.
    """
    try:
        # Check if ticket exists and is assigned to this user's employee
        ticket_response = supabase.table('tickets')\
            .select('*, assigned_employee:employees!assigned_to(id, user_id, name)')\
            .eq('id', ticket_id)\
            .eq('user_id', user.id)\
            .single()\
            .execute()
        
        if not ticket_response.data:
            raise HTTPException(status_code=404, detail="Ticket not found or not assigned to you")
        
        ticket = ticket_response.data
        
        # Verify the ticket is assigned to an employee belonging to this user
        if not ticket.get('assigned_employee') or ticket['assigned_employee']['user_id'] != user.id:
            raise HTTPException(status_code=403, detail="You can only update tickets assigned to your employees")
        
        # Prepare update data
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update ticket
        response = supabase.table('tickets')\
            .update(update_dict)\
            .eq('id', ticket_id)\
            .execute()
        
        return {
            "message": "Ticket updated successfully",
            "ticket": response.data[0],
            "updated_by_employee": ticket['assigned_employee']['name']  # Frontend can use this for local notification
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ticket: {str(e)}")


@router.post("/partial", status_code=201)
async def create_partial_ticket(
    ticket: PartialTicketCreate,
    user=Depends(get_current_user)
):
    """
    Create a ticket with minimal information.
    Admin will later assign category, priority, employee, etc.
    """
    try:
        response = supabase.table('tickets')\
            .insert({
                'title': ticket.title,
                'description': ticket.description,
                'reported_by': ticket.reported_by,
                'reporter_email': ticket.reporter_email,
                'tags': ticket.tags,
                'status': 'open',
                'priority': 'medium',  # Default priority
                'user_id': user.id,
                # ticket_number will be auto-generated by trigger
            })\
            .execute()
        
        created_ticket = response.data[0]
        
        # Create notification for admin
        
        return {
            **created_ticket,
            "requires_review": True  # Frontend can use this flag for local notification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create partial ticket: {str(e)}")

