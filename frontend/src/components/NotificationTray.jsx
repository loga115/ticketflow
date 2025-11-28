import { useState } from 'react';
import { Bell, X, Check, CheckCheck, Trash2 } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import './NotificationTray.css';

const NotificationTray = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, removeNotification, markAsRead, markAllAsRead, clearAll, getUnreadCount } = useNotifications();

  const unreadCount = getUnreadCount();

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'ticket_update':
        return '🎫';
      case 'new_ticket':
        return '✨';
      case 'employee_action':
        return '👤';
      case 'status_change':
        return '🔄';
      default:
        return '📢';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - new Date(timestamp);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className="notification-tray">
      <button 
        className="notification-bell"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="notification-overlay" onClick={() => setIsOpen(false)} />
          <div className="notification-panel">
            <div className="notification-header">
              <h3>Notifications</h3>
              <div className="notification-actions">
                {notifications.length > 0 && (
                  <>
                    <button 
                      onClick={markAllAsRead}
                      className="btn-icon"
                      title="Mark all as read"
                    >
                      <CheckCheck size={18} />
                    </button>
                    <button 
                      onClick={clearAll}
                      className="btn-icon"
                      title="Clear all"
                    >
                      <Trash2 size={18} />
                    </button>
                  </>
                )}
                <button 
                  onClick={() => setIsOpen(false)}
                  className="btn-icon"
                  title="Close"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="notification-list">
              {notifications.length === 0 ? (
                <div className="notification-empty">
                  <Bell size={48} />
                  <p>No notifications</p>
                  <span>You're all caught up!</span>
                </div>
              ) : (
                notifications.map(notification => (
                  <div 
                    key={notification.id}
                    className={`notification-item ${notification.read ? 'read' : 'unread'}`}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    <div className="notification-icon">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="notification-content">
                      <div className="notification-title">{notification.title}</div>
                      <div className="notification-message">{notification.message}</div>
                      <div className="notification-time">{formatTime(notification.timestamp)}</div>
                    </div>
                    <div className="notification-status">
                      {!notification.read && <div className="unread-dot" />}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeNotification(notification.id);
                        }}
                        className="btn-remove"
                        title="Dismiss"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationTray;
