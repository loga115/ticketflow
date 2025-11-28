import React, { useState, useEffect } from 'react';
import {
  X, User, Calendar, Clock, Tag, AlertCircle,
  MessageSquare, Send, Edit2, Trash2, Users as UsersIcon,
  TrendingUp, History, Sparkles
} from 'lucide-react';
import api from '../services/api';
import './TicketDetail.css';

const TicketDetail = ({ ticketId, onClose, onUpdate }) => {
  const [ticket, setTicket] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [categories, setCategories] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [isInternalComment, setIsInternalComment] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);

  useEffect(() => {
    if (ticketId) {
      fetchTicketDetails();
      fetchEmployees();
      fetchCategories();
    } else {
      // Creating new ticket - just fetch employees and set loading to false
      setLoading(false);
      fetchEmployees();
      fetchCategories();
    }
  }, [ticketId]);

  const fetchTicketDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/tickets/${ticketId}`);
      setTicket(response);
    } catch (error) {
      console.error('Error fetching ticket details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/employees');
      setEmployees(response.employees || []);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/tickets/categories');
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get(`/tickets/${ticketId}/recommend-employees`);
      setRecommendations(response.recommendations || []);
      setShowRecommendations(true);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      await api.post(`/tickets/${ticketId}/comments`, {
        content: newComment,
        is_internal: isInternalComment
      });
      setNewComment('');
      setIsInternalComment(false);
      fetchTicketDetails();
    } catch (error) {
      console.error('Error adding comment:', error);
      alert('Failed to add comment');
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;

    try {
      await api.delete(`/tickets/${ticketId}/comments/${commentId}`);
      fetchTicketDetails();
    } catch (error) {
      console.error('Error deleting comment:', error);
      alert('Failed to delete comment');
    }
  };

  const handleAssign = async (employeeId) => {
    try {
      await api.post(`/tickets/${ticketId}/assign`, { assigned_to: employeeId });
      fetchTicketDetails();
      if (onUpdate) onUpdate();
      setShowRecommendations(false);
    } catch (error) {
      console.error('Error assigning ticket:', error);
      alert('Failed to assign ticket');
    }
  };

  const handleCategoryChange = async (categoryId) => {
    try {
      await api.put(`/tickets/${ticketId}`, { category_id: categoryId || null });
      fetchTicketDetails();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating category:', error);
      alert('Failed to update category');
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await api.put(`/tickets/${ticketId}`, { status: newStatus });
      fetchTicketDetails();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    }
  };

  const handlePriorityChange = async (newPriority) => {
    try {
      await api.put(`/tickets/${ticketId}`, { priority: newPriority });
      fetchTicketDetails();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating priority:', error);
      alert('Failed to update priority');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
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
    return (
      <div className="ticket-detail-overlay">
        <div className="ticket-detail-modal">
          <div className="loading-state">Loading ticket details...</div>
        </div>
      </div>
    );
  }

  // Create mode - show simple message for now
  if (!ticketId) {
    return (
      <div className="ticket-detail-overlay" onClick={onClose}>
        <div className="ticket-detail-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Create New Ticket</h2>
            <button className="btn-close" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
          <div className="modal-body">
            <p>Manual ticket addition is not available yet, please use the endpoints</p>
          </div>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return null;
  }

  return (
    <div className="ticket-detail-overlay" onClick={onClose}>
      <div className="ticket-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-left">
            <h2>{ticket.ticket_number}</h2>
            <span 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(ticket.priority) }}
            >
              {ticket.priority.toUpperCase()}
            </span>
            <span 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(ticket.status) }}
            >
              {ticket.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <button className="btn-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          {/* Left Column - Main Info */}
          <div className="detail-main">
            <h3 className="ticket-title">{ticket.title}</h3>
            
            {ticket.description && (
              <div className="ticket-description">
                <p>{ticket.description}</p>
              </div>
            )}

            <div className="detail-section">
              <label><Tag size={16} /> Category</label>
              <select
                className="inline-select"
                value={ticket.category_id || ''}
                onChange={(e) => handleCategoryChange(e.target.value)}
                style={{ 
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb',
                  backgroundColor: ticket.category_color || '#f3f4f6',
                  color: ticket.category_color ? '#fff' : '#111827',
                  fontWeight: '500'
                }}
              >
                <option value="">No Category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="detail-row">
              <div className="detail-section">
                <label><Calendar size={16} /> Created</label>
                <span>{formatDate(ticket.created_at)}</span>
              </div>

              {ticket.due_date && (
                <div className="detail-section">
                  <label><Clock size={16} /> Due Date</label>
                  <span>{formatDate(ticket.due_date)}</span>
                </div>
              )}
            </div>

            {(ticket.estimated_hours || ticket.actual_hours) && (
              <div className="detail-row">
                {ticket.estimated_hours && (
                  <div className="detail-section">
                    <label><Clock size={16} /> Estimated Hours</label>
                    <span>{ticket.estimated_hours}h</span>
                  </div>
                )}
                {ticket.actual_hours > 0 && (
                  <div className="detail-section">
                    <label><TrendingUp size={16} /> Actual Hours</label>
                    <span>{ticket.actual_hours}h</span>
                  </div>
                )}
              </div>
            )}

            {ticket.reported_by && (
              <div className="detail-section">
                <label><User size={16} /> Reported By</label>
                <span>{ticket.reported_by}</span>
                {ticket.reporter_email && (
                  <span className="reporter-email">({ticket.reporter_email})</span>
                )}
              </div>
            )}

            {ticket.tags && ticket.tags.length > 0 && (
              <div className="detail-section">
                <label><Tag size={16} /> Tags</label>
                <div className="tags-list">
                  {ticket.tags.map((tag, index) => (
                    <span key={index} className="tag-pill">{tag}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Comments Section */}
            <div className="comments-section">
              <h4><MessageSquare size={20} /> Comments ({ticket.comments?.length || 0})</h4>
              
              <form onSubmit={handleSubmitComment} className="comment-form">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  rows="3"
                />
                <div className="comment-form-actions">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={isInternalComment}
                      onChange={(e) => setIsInternalComment(e.target.checked)}
                    />
                    Internal note
                  </label>
                  <button type="submit" disabled={submittingComment || !newComment.trim()}>
                    <Send size={16} />
                    Post Comment
                  </button>
                </div>
              </form>

              <div className="comments-list">
                {ticket.comments && ticket.comments.length > 0 ? (
                  ticket.comments.map((comment) => (
                    <div key={comment.id} className={`comment-item ${comment.is_internal ? 'internal' : ''}`}>
                      <div className="comment-header">
                        <div className="comment-author">
                          <User size={16} />
                          {comment.employees?.name || 'Unknown'}
                        </div>
                        <div className="comment-meta">
                          {comment.is_internal && <span className="internal-badge">Internal</span>}
                          <span className="comment-date">{formatDate(comment.created_at)}</span>
                          <button 
                            className="btn-delete-comment"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                      <div className="comment-content">{comment.content}</div>
                    </div>
                  ))
                ) : (
                  <div className="no-comments">No comments yet</div>
                )}
              </div>
            </div>

            {/* Activity History */}
            {ticket.history && ticket.history.length > 0 && (
              <div className="history-section">
                <h4><History size={20} /> Activity History</h4>
                <div className="history-list">
                  {ticket.history.slice(0, 10).map((entry) => (
                    <div key={entry.id} className="history-item">
                      <div className="history-icon">
                        <AlertCircle size={14} />
                      </div>
                      <div className="history-content">
                        <div className="history-description">{entry.description}</div>
                        <div className="history-meta">
                          {entry.employees?.name && <span>{entry.employees.name} • </span>}
                          <span>{formatDate(entry.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Actions & Assignment */}
          <div className="detail-sidebar">
            <div className="sidebar-section">
              <h4>Actions</h4>
              
              <div className="action-group">
                <label>Status</label>
                <select 
                  value={ticket.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  className="action-select"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="in_review">In Review</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                  <option value="blocked">Blocked</option>
                </select>
              </div>

              <div className="action-group">
                <label>Priority</label>
                <select 
                  value={ticket.priority}
                  onChange={(e) => handlePriorityChange(e.target.value)}
                  className="action-select"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div className="sidebar-section">
              <h4><UsersIcon size={18} /> Assignment</h4>
              
              <div className="current-assignee">
                {ticket.employee_name ? (
                  <div className="assignee-card">
                    <User size={20} />
                    <div>
                      <div className="assignee-name">{ticket.employee_name}</div>
                      <div className="assignee-email">{ticket.employee_email}</div>
                      {ticket.employee_department && (
                        <div className="assignee-dept">{ticket.employee_department}</div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="unassigned-notice">
                    <AlertCircle size={20} />
                    Unassigned
                  </div>
                )}
              </div>

              <button 
                className="btn-recommend"
                onClick={fetchRecommendations}
              >
                <Sparkles size={16} />
                Get Recommendations
              </button>

              {showRecommendations && recommendations.length > 0 && (
                <div className="recommendations-list">
                  <h5>Recommended Employees:</h5>
                  {recommendations.map((rec) => (
                    <div key={rec.employee_id} className="recommendation-item">
                      <div className="rec-info">
                        <div className="rec-name">{rec.employee_name}</div>
                        <div className="rec-reasons">
                          {rec.recommendation_reasons.slice(0, 2).map((reason, i) => (
                            <span key={i} className="reason-tag">{reason}</span>
                          ))}
                        </div>
                        <div className="rec-stats">
                          Active: {rec.active_tickets} | Completed: {rec.completed_tickets}
                        </div>
                      </div>
                      <button
                        className="btn-assign-rec"
                        onClick={() => handleAssign(rec.employee_id)}
                      >
                        Assign
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="action-group">
                <label>Manual Assignment</label>
                <select 
                  value={ticket.assigned_to || ''}
                  onChange={(e) => handleAssign(e.target.value || null)}
                  className="action-select"
                >
                  <option value="">Unassigned</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.name}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;
