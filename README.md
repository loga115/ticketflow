# 🎫 TicketFlow - Jira-like Ticket Management System

![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql)

A comprehensive **Jira-inspired ticket management system** with intelligent employee assignment, time tracking, performance analytics, and recommendation engine. Built with React and Python FastAPI.

---

# Deployed at: https://ticketflow-2-n132.onrender.com/

## Key Features

### Ticket Management
- **Complete CRUD Operations** - Create, read, update, and delete tickets
- **Ticket Categories** - Organize tickets with custom categories (Backend, Frontend, Bug Fix, etc.)
- **Flexible Status Workflow** - Open → In Progress → In Review → Resolved → Closed
- **Priority Levels** - Low, Medium, High, Urgent
- **Auto-generated Ticket Numbers** - Format: TICK-0001, TICK-0002, etc.
- **Comments System** - Internal and external comments with threading
- **Activity History** - Complete audit trail of all ticket changes
- **Tags & Labels** - Multiple tags for better organization
- **Due Dates & Time Tracking** - Estimated vs actual hours tracking

### Employee Management
- **Employee Profiles** - Name, email, position, department, salary, contact
- **Specializations** - Skill-based categorization (Python, React, Database, etc.)
- **Department Organization** - Group employees by departments
- **Active/Inactive Status** - Employee lifecycle management
- **Workload Tracking** - Real-time view of assigned tickets per employee
- **Performance Metrics** - Completion rates, time efficiency, productivity stats

### Intelligent Recommendation System
- **Specialization Matching** - Match ticket categories with employee skills
- **Workload Balancing** - Prefer less busy employees
- **Experience Weighting** - Consider completion history
- **Smart Scoring Algorithm** - Multi-factor recommendation engine
- **Top 5 Recommendations** - Best-fit employees with reasoning

### Time Tracking & Review
- **Employee Time Logs** - Track hours worked on tickets
- **Billable vs Non-Billable** - Separate tracking for billing purposes
- **Ticket Time Analysis** - Compare estimated vs actual time
- **Daily/Weekly Reports** - Time breakdowns by employee, ticket, department
- **Performance Metrics** - Completion times, efficiency rates
- **Trend Analysis** - Time tracking patterns over periods

###  Admin Dashboard
- **Real-time Statistics** - Total tickets, in progress, resolved, urgent counts
- **Advanced Filtering** - Search, status, priority, assignee filters
- **Inline Assignment** - Drag-and-drop ticket assignment
- **Quick Status Changes** - Update ticket status directly from dashboard
- **Priority Management** - Change priorities on the fly
- **Visual Indicators** - Color-coded statuses and priorities

### User Interface
- **Dark Mode** - Toggle between light and dark themes
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Intuitive Navigation** - Easy-to-use sidebar navigation
- **Modal Dialogs** - Ticket details in overlay modals
- **Live Updates** - Real-time data synchronization
- **Color-coded Categories** - Visual organization with custom colors

---

##  Technology Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.2 | UI framework |
| React Router | 6.x | Client-side routing |
| Lucide React | Latest | Icon library |
| Vite | 5.0 | Build tool & dev server |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.115 | Web framework |
| Pydantic | 2.9 | Data validation |
| Uvicorn | 0.32 | ASGI server |
| Supabase Client | 2.9 | Database & auth |

### Database & Infrastructure
| Technology | Purpose |
|-----------|---------|
| PostgreSQL | Primary database |
| Supabase | Database hosting & auth |
| JWT | Authentication tokens |

---

## Project Structure

```
ticketflow/
├── backend/
│   ├── config/
│   │   └── supabase_client.py      # Database connection
│   ├── middleware/
│   │   └── auth.py                 # JWT authentication
│   ├── routers/
│   │   ├── tickets.py              # Ticket CRUD & comments (30+ endpoints)
│   │   ├── employees.py            # Employee management & stats (15+ endpoints)
│   │   └── employee_time.py        # Time tracking & review (12+ endpoints)
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   ├── schema.sql                  # Database schema
│   ├── seed_data.py                # Dummy data generator & tests
│   └── README.md                   # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminDashboard.jsx  # Main ticket dashboard
│   │   │   ├── AdminDashboard.css
│   │   │   ├── TicketDetail.jsx    # Ticket detail modal
│   │   │   ├── TicketDetail.css
│   │   │   ├── EmployeeManager.jsx # Employee CRUD
│   │   │   ├── EmployeeManager.css
│   │   │   ├── Layout.jsx          # App layout
│   │   │   ├── Layout.css
│   │   │   ├── Auth.jsx            # Authentication
│   │   │   └── Auth.css
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx     # Auth state management
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── App.jsx                 # Main app component
│   │   └── main.jsx                # Entry point
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── README.md                       # This file
```

---

##  Quick Start

### Prerequisites
- **Python 3.11+** installed
- **Node.js 16+** and npm installed
- **Supabase account** (free tier works)
- Git installed

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ticketflow.git
cd ticketflow
```

### 2. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → **New Query**
3. Copy and paste the entire `backend/schema.sql` file
4. Click **Run** to create all tables, indexes, views, and triggers
5. Get your credentials from **Settings** → **API**:
   - Project URL
   - anon/public API key

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `backend/.env`:**
```env
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
FRONTEND_URL=http://localhost:5173
```

**Start the backend:**
```bash
python main.py
```

Backend running at http://localhost:3000  
API documentation at http://localhost:3000/docs

### 4. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

**Edit `frontend/.env`:**
```env
VITE_SUPABASE_URL=https://yourproject.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
VITE_API_URL=http://localhost:3000/api
```

**Start the frontend:**
```bash
npm run dev
```

Frontend running at http://localhost:5173

### 5. Create Test Data (Optional)

```bash
cd backend
python seed_data.py
```

**Note:** You'll need to update the `AUTH_TOKEN` in `seed_data.py` with your JWT token after logging in.

---

## API Documentation

You may use the attached python codes reset_test_data.py and test_endpoints.py as an example of testing the endpoints.

### Ticket Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets` | List all tickets with filters |
| GET | `/api/tickets/{id}` | Get ticket details with comments & history |
| POST | `/api/tickets` | Create new ticket |
| PUT | `/api/tickets/{id}` | Update ticket |
| DELETE | `/api/tickets/{id}` | Delete ticket |
| POST | `/api/tickets/{id}/assign` | Assign/reassign ticket to employee |
| GET | `/api/tickets/{id}/recommend-employees` | Get AI recommendations |
| GET | `/api/tickets/stats/overview` | Get ticket statistics |
| GET | `/api/tickets/stats/by-category` | Tickets grouped by category |

### Ticket Comment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/{id}/comments` | List ticket comments |
| POST | `/api/tickets/{id}/comments` | Add comment |
| PUT | `/api/tickets/{id}/comments/{comment_id}` | Update comment |
| DELETE | `/api/tickets/{id}/comments/{comment_id}` | Delete comment |

### Ticket Category Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/categories` | List all categories |
| POST | `/api/tickets/categories` | Create category |
| PUT | `/api/tickets/categories/{id}` | Update category |
| DELETE | `/api/tickets/categories/{id}` | Delete category |

### Employee Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees` | List all employees with filters |
| GET | `/api/employees/{id}` | Get employee details |
| POST | `/api/employees` | Create employee |
| PUT | `/api/employees/{id}` | Update employee |
| DELETE | `/api/employees/{id}` | Delete employee |
| GET | `/api/employees/{id}/tickets` | Get employee's tickets |
| GET | `/api/employees/{id}/workload` | Get employee workload |
| GET | `/api/employees/{id}/performance` | Get performance metrics |
| GET | `/api/employees/specializations/list` | List all specializations |
| GET | `/api/employees/by-specialization/{spec}` | Filter by specialization |
| GET | `/api/employees/departments/list` | List departments |
| GET | `/api/employees/departments/{dept}/stats` | Department statistics |

### Time Tracking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/time` | List time logs with filters |
| GET | `/api/time/{id}` | Get time log details |
| POST | `/api/time` | Create time log |
| POST | `/api/time/batch` | Create multiple time logs |
| PUT | `/api/time/{id}` | Update time log |
| DELETE | `/api/time/{id}` | Delete time log |
| GET | `/api/time/review/employee/{id}` | Employee time review |
| GET | `/api/time/review/ticket/{id}` | Ticket time review |
| GET | `/api/time/stats/summary` | Time tracking summary |
| GET | `/api/time/stats/trends` | Time trends analysis |

**Total: 50+ API endpoints**

---

## Use Cases

### For Project Managers
1. **Create tickets** from customer requests
2. **Get AI recommendations** for best employee to assign
3. **Track progress** through status changes
4. **Monitor workload** across team members
5. **Review time spent** vs estimates

### For Team Leads
1. **Assign tickets** to team members
2. **Monitor department performance**
3. **Balance workload** using recommendations
4. **Track billable hours**
5. **Generate time reports**

### For Employees
1. **View assigned tickets**
2. **Update ticket status**
3. **Add comments** and notes
4. **Log time worked**
5. **Track personal performance**

---

## Security Features

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Row Level Security (RLS)** - Database-level access control
- ✅ **User Isolation** - Users only see their own data
- ✅ **CORS Protection** - Configured origins
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **XSS Protection** - Input sanitization
- ✅ **Environment Variables** - Sensitive data in .env files
- ✅ **Password Hashing** - Supabase built-in security

---

## Database Schema

### Core Tables

**employees**
- Stores employee information with specializations array
- Unique email constraint
- Active/inactive status

**tickets**
- Main ticket information with auto-generated ticket numbers
- Foreign keys to categories and employees
- Status workflow tracking with timestamps
- Tags array for flexible categorization

**ticket_categories**
- Custom categories with colors and icons
- User-specific categories

**ticket_comments**
- Comment threads on tickets
- Internal vs external comments
- Soft deletion support

**ticket_history**
- Complete audit trail
- Automatic logging via triggers
- Action types: created, assigned, status_changed, priority_changed

**employee_time_logs**
- Time tracking entries
- Billable/non-billable hours
- Links to tickets for accuracy

**Views:**
- `ticket_summary` - Pre-joined ticket data with employee info
- `employee_workload` - Real-time workload calculations

**Triggers:**
- Auto-generate ticket numbers
- Log ticket assignment changes
- Track status transitions
- Update actual hours from time logs

---

## Testing

### Running Test Suite

```bash
cd backend
python seed_data.py
```

### Test Cases Included

1.  Create new ticket
2.  Assign ticket to employee
3.  Add comment to ticket
4.  Get employee recommendations
5.  Check employee workload
6.  Create time log entry
7.  Get performance metrics
8.  Retrieve ticket statistics

### Sample Data Generated

- 8 employees with various specializations
- 8 ticket categories (Backend, Frontend, Bug Fix, etc.)
- 15+ realistic tickets
- Multiple comments per ticket
- Time log entries
- Ticket assignment history

---

## UI/UX Features

### Admin Dashboard
- **Statistics Cards** - Quick overview of ticket counts
- **Advanced Filters** - Search, status, priority, assignee
- **Inline Editing** - Change status/priority/assignee directly
- **Color Coding** - Visual status and priority indicators
- **Responsive Table** - Works on all screen sizes

### Ticket Detail Modal
- **Full Information** - All ticket details in one view
- **Comments Section** - Add and view comments
- **Activity History** - Complete audit trail
- **Smart Recommendations** - AI-suggested employees
- **Quick Actions** - Update status, priority, assignment
- **Time Tracking** - View estimated vs actual hours

### Employee Manager
- **Card Grid Layout** - Visual employee cards
- **Search & Filter** - Find employees quickly
- **Specialization Tags** - Visual skill indicators
- **Statistics Dashboard** - Employee counts and metrics
- **Dark Mode Support** - Eye-friendly interface

---

## Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions including:

- Vercel deployment for frontend
- Render/Railway deployment for backend
- Supabase database hosting
- Environment configuration
- Production best practices

### Deploying on Render (quick guide)

- **What this repo contains:**
   - `backend/` — FastAPI app (requires Python & dependencies)
   - `frontend/` — Vite + React app (static site build to `frontend/dist`)

- **Included manifest:** `render.yaml` (at project root) configures two services:
   - `productivity-hub-backend` — a Python web service. Build installs `backend/requirements.txt` and start command is `uvicorn main:app --host 0.0.0.0 --port $PORT` (working directory: `backend`).
   - `productivity-hub-frontend` — a Static site. Build command runs `npm ci` and `vite build` inside `frontend` and publishes `frontend/dist`.

- **Manual (GUI) steps**
   1. Create a new Render account or sign in at https://render.com
   2. Create a new **Web Service** for the backend:
       - Connect your Git repo and select the `backend` service or use the `render.yaml` detected in repo root.
       - Set Environment to `Python`.
       - Build Command: leave empty if using `render.yaml` or set to `pip install -r backend/requirements.txt`.
       - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT` (ensure working directory is `backend`).
       - Add any required environment variables (e.g. `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `FRONTEND_URL`).

   3. Create a new **Static Site** or Static Web Service for the frontend:
       - Connect your repo and select the `frontend` service (or let `render.yaml` create it).
       - Build Command: `npm ci --prefix frontend && npm run build --prefix frontend`.
       - Publish Directory: `frontend/dist`.
       - Add environment variables used by the frontend (e.g. `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL`).

- **Important notes**
   - The backend must expose `$PORT`. The `uvicorn` start command above uses `$PORT` provided by Render.
   - Keep secrets out of the repo — set them via Render's dashboard as environment variables.
   - If you prefer a single Docker service, create a `Dockerfile` at repo root and deploy as a single web service (I can add this if you'd like).

### Local test commands (Windows PowerShell)

```powershell
# Backend
cd backend; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt; uvicorn main:app --host 0.0.0.0 --port 3000

# Frontend
cd frontend; npm install; npm run build; # serve `frontend/dist` with any static server to verify
```

---

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://yourproject.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
VITE_API_URL=http://localhost:3000/api
```
# Made for the ProU Assignment by Logamithran M.R.
