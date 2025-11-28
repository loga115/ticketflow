import { useCallback } from 'react';
import { useNotifications } from '../contexts/NotificationContext';

/**
 * Hook to integrate API calls with notifications and live updates
 * Usage: const { notifySuccess, notifyError, notifyUpdate } = useApiNotifications();
 */
export const useApiNotifications = () => {
  const { addNotification } = useNotifications();

  const notifySuccess = useCallback((title, message, pinned = false) => {
    addNotification({
      type: 'success',
      title,
      message,
      pinned
    });
  }, [addNotification]);

  const notifyError = useCallback((title, message, pinned = false) => {
    addNotification({
      type: 'error',
      title,
      message,
      pinned
    });
  }, [addNotification]);

  const notifyUpdate = useCallback((title, message, pinned = false) => {
    addNotification({
      type: 'ticket_update',
      title,
      message,
      pinned
    });
  }, [addNotification]);

  const notifyNewTicket = useCallback((ticketNumber, title, requiresReview = false) => {
    addNotification({
      type: 'new_ticket',
      title: `New Ticket: ${ticketNumber}`,
      message: requiresReview ? `${title} - Requires admin review` : title,
      pinned: requiresReview
    });
  }, [addNotification]);

  const notifyEmployeeUpdate = useCallback((ticketNumber, employeeName, status) => {
    addNotification({
      type: 'ticket_update',
      title: `${ticketNumber} Updated`,
      message: `${employeeName} changed status to ${status}`,
      pinned: false
    });
  }, [addNotification]);

  const notifyAssignment = useCallback((ticketNumber, employeeName) => {
    addNotification({
      type: 'assignment',
      title: `Ticket Assigned`,
      message: `${ticketNumber} assigned to ${employeeName}`,
      pinned: false
    });
  }, [addNotification]);

  const notifyComment = useCallback((ticketNumber, commenter) => {
    addNotification({
      type: 'comment',
      title: `New Comment`,
      message: `${commenter} commented on ${ticketNumber}`,
      pinned: false
    });
  }, [addNotification]);

  return {
    notifySuccess,
    notifyError,
    notifyUpdate,
    notifyNewTicket,
    notifyEmployeeUpdate,
    notifyAssignment,
    notifyComment
  };
};
