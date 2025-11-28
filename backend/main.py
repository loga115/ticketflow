from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from pathlib import Path

from routers import tickets, employees, employee_time
from config.supabase_client import supabase

# Load environment variables
load_dotenv()

app = FastAPI(
    title="TicketFlow - Jira-like Ticket Management System",
    version="3.0.0",
    description="Complete ticket management system with employee assignments, time tracking, and recommendations"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(employee_time.router, prefix="/api/time", tags=["time-tracking"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "TicketFlow API is running", "version": "3.0.0"}

# Mount static files for production
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return None
        
        # Serve API docs
        if full_path in ["docs", "openapi.json", "redoc"]:
            return None  # Let FastAPI handle these
        
        # Try to serve static file, otherwise serve index.html for SPA routing
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to TicketFlow - Jira-like Ticket Management System",
            "version": "3.0.0",
            "docs": "/docs",
            "features": [
                "Ticket Management with Categories",
                "Employee Assignment & Recommendations",
                "Time Tracking & Review System",
                "Comments & Activity History",
                "Performance Analytics"
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
