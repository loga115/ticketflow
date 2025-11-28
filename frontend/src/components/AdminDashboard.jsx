import React, { useState, useEffect, useRef } from 'react';
import { 
  Ticket, Plus, Search, Filter, Users, Clock, 
  AlertCircle, CheckCircle, Circle, MessageSquare,
  Calendar, TrendingUp, BarChart3, Zap
} from 'lucide-react';
import api from '../services/api';
import TicketDetail from './TicketDetail';
import { useApiNotifications } from '../hooks/useApiNotifications';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [categoryFormData, setCategoryFormData] = useState({
    name: '',
    description: '',
    color: '#3b82f6',
    icon: 'tag'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [assigneeFilter, setAssigneeFilter] = useState('');
  
  const { notifySuccess, notifyError, notifyUpdate, notifyAssignment, notifyNewTicket } = useApiNotifications();
  const previousTicketsRef = useRef([]);

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 3 seconds for live updates
    const interval = setInterval(() => {
      fetchDashboardData(true); // Silent refresh
    }, 3000);
    
    return () => clearInterval(interval);
  }, [statusFilter, priorityFilter, assigneeFilter, searchTerm]);

  // Detect ticket changes and trigger notifications
  useEffect(() => {
    const previousTickets = previousTicketsRef.current;
    
    if (previousTickets.length === 0) {
      // First load, just store the tickets
      previousTicketsRef.current = tickets;
      return;
    }

    // Check for new tickets
    tickets.forEach(ticket => {
      const existed = previousTickets.find(t => t.id === ticket.id);
      if (!existed) {
        // New ticket detected
        notifyNewTicket(
          ticket.ticket_number,
          ticket.title,
          !ticket.category_id // Requires review if no category
        );
      } else {
        // Check for status changes
        if (existed.status !== ticket.status) {
          notifyUpdate(
            `${ticket.ticket_number} Updated`,
            `Status changed from ${existed.status} to ${ticket.status}`
          );
        }
        // Check for assignment changes
        if (existed.employee_id !== ticket.employee_id && ticket.employee_id) {
          notifyAssignment(
            ticket.ticket_number,
            ticket.employee_name || 'an employee'
          );
        }
      }
    });

    // Check for deleted tickets
    previousTickets.forEach(oldTicket => {
      const stillExists = tickets.find(t => t.id === oldTicket.id);
      if (!stillExists) {
        notifySuccess(
          'Ticket Deleted',
          `${oldTicket.ticket_number}: ${oldTicket.title} has been deleted`
        );
      }
    });

    // Update the ref
    previousTicketsRef.current = tickets;
  }, [tickets, notifyNewTicket, notifyUpdate, notifyAssignment]);

  const fetchDashboardData = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      
      // Fetch tickets with filters
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (priorityFilter) params.append('priority', priorityFilter);
      if (assigneeFilter) params.append('assigned_to', assigneeFilter);
      if (searchTerm) params.append('search', searchTerm);
      
      const [ticketsRes, employeesRes, categoriesRes, statsRes] = await Promise.all([
        api.get(`/tickets?${params.toString()}`),
        api.get('/employees'),
        api.get('/tickets/categories'),
        api.get('/tickets/stats/overview')
      ]);

      setTickets(ticketsRes.tickets || []);
      setEmployees(employeesRes.employees || []);
      setCategories(categoriesRes.categories || []);
      setStats(statsRes);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignTicket = async (ticketId, employeeId) => {
    try {
      await api.post(`/tickets/${ticketId}/assign`, { assigned_to: employeeId });
      
      // Find ticket and employee for notification
      const ticket = tickets.find(t => t.id === ticketId);
      const employee = employees.find(e => e.id === employeeId);
      
      if (ticket && employee) {
        notifyAssignment(ticket.ticket_number, employee.name);
      }
      
      fetchDashboardData();
    } catch (error) {
      console.error('Error assigning ticket:', error);
      notifyError('Assignment Failed', 'Failed to assign ticket');
    }
  };

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      const ticket = tickets.find(t => t.id === ticketId);
      await api.put(`/tickets/${ticketId}`, { status: newStatus });
      
      if (ticket) {
        notifyUpdate(
          `${ticket.ticket_number} Updated`,
          `Status changed to ${newStatus.replace('_', ' ')}`
        );
      }
      
      fetchDashboardData();
    } catch (error) {
      console.error('Error updating status:', error);
      notifyError('Update Failed', 'Failed to update ticket status');
    }
  };

  const handlePriorityChange = async (ticketId, newPriority) => {
    try {
      const ticket = tickets.find(t => t.id === ticketId);
      await api.put(`/tickets/${ticketId}`, { priority: newPriority });
      
      if (ticket) {
        notifyUpdate(
          `${ticket.ticket_number} Updated`,
          `Priority changed to ${newPriority}`
        );
      }
      
      fetchDashboardData();
    } catch (error) {
      console.error('Error updating priority:', error);
      notifyError('Update Failed', 'Failed to update ticket priority');
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/tickets/categories', categoryFormData);
      notifySuccess('Category Created', `${categoryFormData.name} has been added`);
      fetchDashboardData();
      setShowCategoryModal(false);
      setCategoryFormData({
        name: '',
        description: '',
        color: '#3b82f6',
        icon: 'tag'
      });
    } catch (error) {
      console.error('Error creating category:', error);
      notifyError('Creation Failed', 'Failed to create category. Please try again.');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open': return <Circle size={16} />;
      case 'in_progress': return <Clock size={16} />;
      case 'in_review': return <AlertCircle size={16} />;
      case 'resolved': return <CheckCircle size={16} />;
      case 'closed': return <CheckCircle size={16} />;
      case 'blocked': return <AlertCircle size={16} />;
      default: return <Circle size={16} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return '#dc2626';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return '#6b7280';
      case 'in_progress': return '#3b82f6';
      case 'in_review': return '#8b5cf6';
      case 'resolved': return '#10b981';
      case 'closed': return '#059669';
      case 'blocked': return '#dc2626';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <div className="header-title">
          <BarChart3 size={32} />
          <h1>Admin Dashboard</h1>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="btn-new-ticket" 
            onClick={() => setShowCategoryModal(true)}
            style={{ 
              backgroundColor: '#8b5cf6',
              borderColor: '#8b5cf6'
            }}
          >
            <Plus size={20} />
            New Category
          </button>
          <button className="btn-new-ticket" onClick={() => setShowTicketModal(true)}>
            <Plus size={20} />
            New Ticket
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#3b82f6' }}>
              <Ticket size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Total Tickets</div>
              <div className="stat-value">{stats.total}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#f59e0b' }}>
              <Clock size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">In Progress</div>
              <div className="stat-value">{stats.in_progress}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#10b981' }}>
              <CheckCircle size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Resolved</div>
              <div className="stat-value">{stats.resolved}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#dc2626' }}>
              <AlertCircle size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Urgent</div>
              <div className="stat-value">{stats.urgent}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#8b5cf6' }}>
              <Users size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Unassigned</div>
              <div className="stat-value">{stats.unassigned}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#06b6d4' }}>
              <TrendingUp size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Open Tickets</div>
              <div className="stat-value">{stats.open}</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="dashboard-filters">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search tickets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <select 
          className="filter-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
          <option value="blocked">Blocked</option>
        </select>

        <select 
          className="filter-select"
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select 
          className="filter-select"
          value={assigneeFilter}
          onChange={(e) => setAssigneeFilter(e.target.value)}
        >
          <option value="">All Assignees</option>
          <option value="unassigned">Unassigned</option>
          {employees.map(emp => (
            <option key={emp.id} value={emp.id}>{emp.name}</option>
          ))}
        </select>
      </div>

      {/* Tickets Table */}
      <div className="tickets-table-container">
        <table className="tickets-table">
          <thead>
            <tr>
              <th>Ticket #</th>
              <th>Title</th>
              <th>Category</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Assigned To</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="8" className="no-tickets">
                  No tickets found
                </td>
              </tr>
            ) : (
              tickets.map(ticket => (
                <tr key={ticket.id} onClick={() => setSelectedTicket(ticket)}>
                  <td className="ticket-number">{ticket.ticket_number}</td>
                  <td className="ticket-title">
                    <div className="title-with-comments">
                      {ticket.title}
                      {ticket.comment_count > 0 && (
                        <span className="comment-badge">
                          <MessageSquare size={14} />
                          {ticket.comment_count}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    {ticket.category_name && (
                      <span 
                        className="category-badge"
                        style={{ backgroundColor: ticket.category_color }}
                      >
                        {ticket.category_name}
                      </span>
                    )}
                  </td>
                  <td>
                    <div className="status-cell">
                      <select
                        className="inline-select status-select"
                        value={ticket.status}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => handleStatusChange(ticket.id, e.target.value)}
                        style={{ color: getStatusColor(ticket.status) }}
                      >
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="in_review">In Review</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                        <option value="blocked">Blocked</option>
                      </select>
                    </div>
                  </td>
                  <td>
                    <select
                      className="inline-select priority-select"
                      value={ticket.priority}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => handlePriorityChange(ticket.id, e.target.value)}
                      style={{ color: getPriorityColor(ticket.priority) }}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </td>
                  <td>
                    <select
                      className="inline-select assignee-select"
                      value={ticket.employee_id || ticket.assigned_to || ''}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => handleAssignTicket(ticket.id, e.target.value || null)}
                    >
                      <option value="">Unassigned</option>
                      {employees.map(emp => (
                        <option key={emp.id} value={emp.id}>{emp.name}</option>
                      ))}
                    </select>
                  </td>
                  <td className="date-cell">
                    {new Date(ticket.created_at).toLocaleDateString()}
                  </td>
                  <td className="actions-cell">
                    <button 
                      className="btn-view"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedTicket(ticket.id);
                        setShowTicketModal(true);
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Quick Stats Footer */}
      <div className="dashboard-footer">
        <div className="footer-stat">
          <strong>{tickets.length}</strong> tickets shown
        </div>
        <div className="footer-stat">
          <strong>{employees.length}</strong> employees
        </div>
        <div className="footer-stat">
          <strong>{categories.length}</strong> categories
        </div>
      </div>

      {/* Ticket Detail Modal */}
      {showTicketModal && (
        <TicketDetail
          ticketId={selectedTicket}
          onClose={() => {
            setShowTicketModal(false);
            setSelectedTicket(null);
          }}
          onUpdate={() => {
            fetchDashboardData();
            setShowTicketModal(false);
            setSelectedTicket(null);
          }}
        />
      )}

      {/* Category Modal */}
      {showCategoryModal && (
        <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Category</h2>
              <button className="modal-close" onClick={() => setShowCategoryModal(false)}>×</button>
            </div>
            <form onSubmit={handleCategorySubmit}>
              <div className="form-group">
                <label>Category Name *</label>
                <input
                  type="text"
                  value={categoryFormData.name}
                  onChange={(e) => setCategoryFormData({ ...categoryFormData, name: e.target.value })}
                  placeholder="e.g., Bug Fix, Feature Request"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={categoryFormData.description}
                  onChange={(e) => setCategoryFormData({ ...categoryFormData, description: e.target.value })}
                  placeholder="Brief description of this category..."
                  rows="3"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Color</label>
                  <input
                    type="color"
                    value={categoryFormData.color}
                    onChange={(e) => setCategoryFormData({ ...categoryFormData, color: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Icon</label>
                  <select
                    value={categoryFormData.icon}
                    onChange={(e) => setCategoryFormData({ ...categoryFormData, icon: e.target.value })}
                  >
                    <option value="tag">Tag</option>
                    <option value="bug">Bug</option>
                    <option value="feature">Feature</option>
                    <option value="task">Task</option>
                    <option value="question">Question</option>
                    <option value="improvement">Improvement</option>
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setShowCategoryModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-submit">
                  Create Category
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
