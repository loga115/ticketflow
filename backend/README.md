# Python FastAPI Backend

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
FRONTEND_URL=http://localhost:5173
```

5. Run the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

The API will be available at `http://localhost:3000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

## Endpoints

### Boards
- `GET /api/boards` - Get all boards
- `GET /api/boards/{id}` - Get board with tasks
- `POST /api/boards` - Create board
- `PUT /api/boards/{id}` - Update board
- `DELETE /api/boards/{id}` - Delete board

### Tasks
- `GET /api/tasks/board/{boardId}` - Get tasks by board
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Pomodoro
- `GET /api/pomodoro` - Get pomodoro sessions
- `GET /api/pomodoro/stats` - Get statistics
- `POST /api/pomodoro` - Create session
- `PUT /api/pomodoro/{id}` - Update session

### Time Tracker
- `GET /api/timetracker` - Get time entries
- `GET /api/timetracker/active` - Get active entry
- `GET /api/timetracker/stats` - Get statistics
- `POST /api/timetracker` - Create time entry
- `PUT /api/timetracker/{id}` - Update time entry
- `DELETE /api/timetracker/{id}` - Delete time entry

### Employees
- `GET /api/employees` - Get all employees
- `GET /api/employees/{id}` - Get employee by ID
- `POST /api/employees` - Create employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee
- `GET /api/employees/department/{department}` - Get employees by department
