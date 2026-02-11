/**
 * Notifications store
 * Manages toast notifications and alerts
 */
import { writable } from 'svelte/store';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  title?: string;
  duration?: number;
  dismissible?: boolean;
}

interface NotificationsState {
  notifications: Notification[];
}

const initialState: NotificationsState = {
  notifications: []
};

function createNotificationsStore() {
  const { subscribe, update } = writable<NotificationsState>(initialState);

  let idCounter = 0;

  function generateId(): string {
    return `notification-${Date.now()}-${idCounter++}`;
  }

  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = generateId();
    const newNotification: Notification = {
      id,
      dismissible: true,
      duration: 5000,
      ...notification
    };

    update(state => ({
      notifications: [...state.notifications, newNotification]
    }));

    // Auto-dismiss after duration
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }

  function removeNotification(id: string) {
    update(state => ({
      notifications: state.notifications.filter(n => n.id !== id)
    }));
  }

  return {
    subscribe,

    success(message: string, title?: string, duration?: number) {
      return addNotification({
        type: 'success',
        message,
        title,
        duration
      });
    },

    error(message: string, title?: string, duration?: number) {
      return addNotification({
        type: 'error',
        message,
        title,
        duration: duration || 7000 // Errors stay longer
      });
    },

    warning(message: string, title?: string, duration?: number) {
      return addNotification({
        type: 'warning',
        message,
        title,
        duration
      });
    },

    info(message: string, title?: string, duration?: number) {
      return addNotification({
        type: 'info',
        message,
        title,
        duration
      });
    },

    dismiss(id: string) {
      removeNotification(id);
    },

    dismissAll() {
      update(() => initialState);
    }
  };
}

export const notificationsStore = createNotificationsStore();
