-- Jira-like Ticket Management System Database Schema for Supabase/PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CORE TABLES
-- ============================================
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS ticket_categories CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS ticket_comments CASCADE;
DROP TABLE IF EXISTS ticket_history CASCADE;
DROP TABLE IF EXISTS employee_time_logs CASCADE;
DROP TABLE IF EXISTS ticket_attachments CASCADE;
DROP TABLE IF EXISTS ticket_watchers CASCADE;
DROP TABLE IF EXISTS employee_metrics CASCADE;


-- Employees table with specializations
CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  position VARCHAR(255) NOT NULL,
  department VARCHAR(255),
  phone VARCHAR(50),
  salary DECIMAL(12, 2),
  specializations TEXT[], -- Array of specializations (e.g., ['Backend', 'Python', 'API'])
  avatar_url TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ticket categories
CREATE TABLE ticket_categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  color VARCHAR(7) DEFAULT '#3b82f6', -- Hex color code
  icon VARCHAR(50), -- Icon name for UI
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, name)
);

-- Tickets table (replaces tasks/boards)
CREATE TABLE tickets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  ticket_number VARCHAR(20) UNIQUE NOT NULL, -- e.g., TICK-1001
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category_id UUID REFERENCES ticket_categories(id) ON DELETE SET NULL,
  status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'in_review', 'resolved', 'closed', 'blocked')),
  priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  assigned_to UUID REFERENCES employees(id) ON DELETE SET NULL,
  reported_by VARCHAR(255), -- Name or email of reporter
  reporter_email VARCHAR(255),
  due_date TIMESTAMP WITH TIME ZONE,
  estimated_hours DECIMAL(5, 2),
  actual_hours DECIMAL(5, 2) DEFAULT 0,
  tags TEXT[], -- Array of tags for filtering
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  assigned_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE
);

-- Ticket comments
CREATE TABLE ticket_comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  is_internal BOOLEAN DEFAULT FALSE, -- Internal notes vs customer-visible
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ticket history/activity log
CREATE TABLE ticket_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
  action VARCHAR(100) NOT NULL, -- 'created', 'assigned', 'status_changed', 'priority_changed', etc.
  old_value TEXT,
  new_value TEXT,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee time logs (replaces time_entries and pomodoro)
CREATE TABLE employee_time_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  ticket_id UUID REFERENCES tickets(id) ON DELETE SET NULL,
  description TEXT,
  hours_worked DECIMAL(5, 2) NOT NULL,
  work_date DATE NOT NULL DEFAULT CURRENT_DATE,
  start_time TIMESTAMP WITH TIME ZONE,
  end_time TIMESTAMP WITH TIME ZONE,
  is_billable BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ticket attachments (optional, for future enhancement)
CREATE TABLE ticket_attachments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  file_url TEXT NOT NULL,
  file_size INTEGER, -- in bytes
  mime_type VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ticket watchers (users following specific tickets)
CREATE TABLE ticket_watchers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(ticket_id, employee_id)
);

-- Employee performance metrics (cached/computed data)
CREATE TABLE employee_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  tickets_assigned INTEGER DEFAULT 0,
  tickets_completed INTEGER DEFAULT 0,
  avg_completion_time DECIMAL(10, 2), -- in hours
  total_hours_logged DECIMAL(10, 2) DEFAULT 0,
  utilization_rate DECIMAL(5, 2), -- percentage
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(employee_id, period_start, period_end)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Employee indexes
CREATE INDEX idx_employees_user_id ON employees(user_id);
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_active ON employees(is_active);
CREATE INDEX idx_employees_specializations ON employees USING GIN(specializations);

-- Ticket category indexes
CREATE INDEX idx_ticket_categories_user_id ON ticket_categories(user_id);

-- Ticket indexes
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_category_id ON tickets(category_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_tickets_due_date ON tickets(due_date);
CREATE INDEX idx_tickets_tags ON tickets USING GIN(tags);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);

-- Comment indexes
CREATE INDEX idx_ticket_comments_ticket_id ON ticket_comments(ticket_id);
CREATE INDEX idx_ticket_comments_created_at ON ticket_comments(created_at DESC);

-- History indexes
CREATE INDEX idx_ticket_history_ticket_id ON ticket_history(ticket_id);
CREATE INDEX idx_ticket_history_created_at ON ticket_history(created_at DESC);

-- Time log indexes
CREATE INDEX idx_employee_time_logs_employee_id ON employee_time_logs(employee_id);
CREATE INDEX idx_employee_time_logs_ticket_id ON employee_time_logs(ticket_id);
CREATE INDEX idx_employee_time_logs_work_date ON employee_time_logs(work_date DESC);
CREATE INDEX idx_employee_time_logs_user_id ON employee_time_logs(user_id);

-- Attachment indexes
CREATE INDEX idx_ticket_attachments_ticket_id ON ticket_attachments(ticket_id);

-- Watcher indexes
CREATE INDEX idx_ticket_watchers_ticket_id ON ticket_watchers(ticket_id);
CREATE INDEX idx_ticket_watchers_employee_id ON ticket_watchers(employee_id);
CREATE INDEX idx_ticket_watchers_user_id ON ticket_watchers(user_id);

-- Metrics indexes
CREATE INDEX idx_employee_metrics_employee_id ON employee_metrics(employee_id);
CREATE INDEX idx_employee_metrics_period ON employee_metrics(period_start, period_end);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_time_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_watchers ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_metrics ENABLE ROW LEVEL SECURITY;

-- Employee policies
CREATE POLICY "Users can view their own employees" 
  ON employees FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own employees" 
  ON employees FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own employees" 
  ON employees FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own employees" 
  ON employees FOR DELETE 
  USING (auth.uid() = user_id);

-- Ticket category policies
CREATE POLICY "Users can view their own ticket categories" 
  ON ticket_categories FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own ticket categories" 
  ON ticket_categories FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own ticket categories" 
  ON ticket_categories FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own ticket categories" 
  ON ticket_categories FOR DELETE 
  USING (auth.uid() = user_id);

-- Ticket policies
CREATE POLICY "Users can view their own tickets" 
  ON tickets FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own tickets" 
  ON tickets FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own tickets" 
  ON tickets FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own tickets" 
  ON tickets FOR DELETE 
  USING (auth.uid() = user_id);

-- Comment policies
CREATE POLICY "Users can view comments on their tickets" 
  ON ticket_comments FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create comments on their tickets" 
  ON ticket_comments FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own comments" 
  ON ticket_comments FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments" 
  ON ticket_comments FOR DELETE 
  USING (auth.uid() = user_id);

-- History policies
CREATE POLICY "Users can view history of their tickets" 
  ON ticket_history FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create history entries" 
  ON ticket_history FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Time log policies
CREATE POLICY "Users can view their employee time logs" 
  ON employee_time_logs FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create employee time logs" 
  ON employee_time_logs FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their employee time logs" 
  ON employee_time_logs FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their employee time logs" 
  ON employee_time_logs FOR DELETE 
  USING (auth.uid() = user_id);

-- Attachment policies
CREATE POLICY "Users can view attachments on their tickets" 
  ON ticket_attachments FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create attachments on their tickets" 
  ON ticket_attachments FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their attachments" 
  ON ticket_attachments FOR DELETE 
  USING (auth.uid() = user_id);

-- Watcher policies
CREATE POLICY "Users can view watchers on their tickets" 
  ON ticket_watchers FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can add watchers to their tickets" 
  ON ticket_watchers FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can remove watchers from their tickets" 
  ON ticket_watchers FOR DELETE 
  USING (auth.uid() = user_id);

-- Metrics policies
CREATE POLICY "Users can view metrics for their employees" 
  ON employee_metrics FOR SELECT 
  USING (employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()));

CREATE POLICY "Users can create metrics for their employees" 
  ON employee_metrics FOR INSERT 
  WITH CHECK (employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()));

CREATE POLICY "Users can update metrics for their employees" 
  ON employee_metrics FOR UPDATE 
  USING (employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete metrics for their employees" 
  ON employee_metrics   FOR DELETE 
  USING (employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()));

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ticket_comments_updated_at BEFORE UPDATE ON ticket_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_time_logs_updated_at BEFORE UPDATE ON employee_time_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_metrics_updated_at BEFORE UPDATE ON employee_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate ticket number
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
DECLARE
    next_number INTEGER;
    new_ticket_number VARCHAR(20);
BEGIN
    -- Get the next ticket number for this user
    SELECT COALESCE(MAX(CAST(SUBSTRING(ticket_number FROM 6) AS INTEGER)), 0) + 1
    INTO next_number
    FROM tickets
    WHERE user_id = NEW.user_id;
    
    -- Generate ticket number like TICK-1001
    new_ticket_number := 'TICK-' || LPAD(next_number::TEXT, 4, '0');
    
    NEW.ticket_number := new_ticket_number;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate ticket number
CREATE TRIGGER generate_ticket_number_trigger
    BEFORE INSERT ON tickets
    FOR EACH ROW
    WHEN (NEW.ticket_number IS NULL)
    EXECUTE FUNCTION generate_ticket_number();

-- Function to log ticket assignment
CREATE OR REPLACE FUNCTION log_ticket_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Log assignment change
    IF (TG_OP = 'UPDATE' AND OLD.assigned_to IS DISTINCT FROM NEW.assigned_to) THEN
        INSERT INTO ticket_history (ticket_id, user_id, employee_id, action, old_value, new_value, description)
        VALUES (
            NEW.id,
            NEW.user_id,
            NEW.assigned_to,
            'assigned',
            COALESCE((SELECT name FROM employees WHERE id = OLD.assigned_to), 'Unassigned'),
            COALESCE((SELECT name FROM employees WHERE id = NEW.assigned_to), 'Unassigned'),
            'Ticket assignment changed'
        );
        
        -- Update assigned_at timestamp
        NEW.assigned_at := NOW();
    END IF;
    
    -- Log status change
    IF (TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status) THEN
        INSERT INTO ticket_history (ticket_id, user_id, employee_id, action, old_value, new_value, description)
        VALUES (
            NEW.id,
            NEW.user_id,
            NEW.assigned_to,
            'status_changed',
            OLD.status,
            NEW.status,
            'Ticket status changed from ' || OLD.status || ' to ' || NEW.status
        );
        
        -- Update completed_at for resolved/closed tickets
        IF NEW.status IN ('resolved', 'closed') AND OLD.status NOT IN ('resolved', 'closed') THEN
            NEW.completed_at := NOW();
        END IF;
    END IF;
    
    -- Log priority change
    IF (TG_OP = 'UPDATE' AND OLD.priority IS DISTINCT FROM NEW.priority) THEN
        INSERT INTO ticket_history (ticket_id, user_id, employee_id, action, old_value, new_value, description)
        VALUES (
            NEW.id,
            NEW.user_id,
            NEW.assigned_to,
            'priority_changed',
            OLD.priority,
            NEW.priority,
            'Ticket priority changed from ' || OLD.priority || ' to ' || NEW.priority
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to log ticket changes
CREATE TRIGGER log_ticket_changes
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION log_ticket_assignment();

-- Function to update ticket actual hours from time logs
CREATE OR REPLACE FUNCTION update_ticket_actual_hours()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE tickets
    SET actual_hours = (
        SELECT COALESCE(SUM(hours_worked), 0)
        FROM employee_time_logs
        WHERE ticket_id = NEW.ticket_id
    )
    WHERE id = NEW.ticket_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update actual hours when time log is added/updated/deleted
CREATE TRIGGER update_ticket_hours_on_insert
    AFTER INSERT ON employee_time_logs
    FOR EACH ROW
    WHEN (NEW.ticket_id IS NOT NULL)
    EXECUTE FUNCTION update_ticket_actual_hours();

CREATE TRIGGER update_ticket_hours_on_update
    AFTER UPDATE ON employee_time_logs
    FOR EACH ROW
    WHEN (NEW.ticket_id IS NOT NULL)
    EXECUTE FUNCTION update_ticket_actual_hours();

CREATE TRIGGER update_ticket_hours_on_delete
    AFTER DELETE ON employee_time_logs
    FOR EACH ROW
    WHEN (OLD.ticket_id IS NOT NULL)
    EXECUTE FUNCTION update_ticket_actual_hours();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View for ticket summary with employee details
CREATE OR REPLACE VIEW ticket_summary AS
SELECT 
    t.id,
    t.user_id,
    t.ticket_number,
    t.title,
    t.description,
    t.status,
    t.priority,
    t.due_date,
    t.estimated_hours,
    t.actual_hours,
    t.created_at,
    t.updated_at,
    t.assigned_at,
    t.completed_at,
    tc.name AS category_name,
    tc.color AS category_color,
    e.id AS employee_id,
    e.name AS employee_name,
    e.email AS employee_email,
    e.department AS employee_department,
    (SELECT COUNT(*) FROM ticket_comments WHERE ticket_id = t.id) AS comment_count,
    (SELECT COUNT(*) FROM ticket_watchers WHERE ticket_id = t.id) AS watcher_count
FROM tickets t
LEFT JOIN ticket_categories tc ON t.category_id = tc.id
LEFT JOIN employees e ON t.assigned_to = e.id;

-- View for employee workload
CREATE OR REPLACE VIEW employee_workload AS
SELECT 
    e.id AS employee_id,
    e.name AS employee_name,
    e.email,
    e.department,
    e.specializations,
    COUNT(CASE WHEN t.status NOT IN ('resolved', 'closed') THEN 1 END) AS active_tickets,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) AS in_progress_tickets,
    COUNT(CASE WHEN t.status IN ('resolved', 'closed') THEN 1 END) AS completed_tickets,
    COALESCE(SUM(CASE WHEN t.status NOT IN ('resolved', 'closed') THEN t.estimated_hours ELSE 0 END), 0) AS estimated_hours_remaining,
    COALESCE(SUM(t.actual_hours), 0) AS total_hours_logged
FROM employees e
LEFT JOIN tickets t ON e.id = t.assigned_to
GROUP BY e.id, e.name, e.email, e.department, e.specializations;

-- ============================================
-- INITIAL DATA / SEED DATA
-- ============================================

-- Insert default ticket categories (these will be added per user via API)
-- Categories are intentionally left empty to be created by users
