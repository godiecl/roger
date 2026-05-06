/**
 * User Activity Tracker
 * Tracks user activity and manages session timeout
 */
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds

interface ActivityState {
  lastActivity: number;
  isActive: boolean;
}

function createActivityTracker() {
  const { subscribe, set, update } = writable<ActivityState>({
    lastActivity: Date.now(),
    isActive: true
  });

  let inactivityTimer: number | null = null;

  function updateActivity() {
    update(state => ({
      ...state,
      lastActivity: Date.now(),
      isActive: true
    }));

    // Reset inactivity timer
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }

    // Set new timer for inactivity
    inactivityTimer = setTimeout(() => {
      update(state => ({ ...state, isActive: false }));
    }, INACTIVITY_TIMEOUT) as unknown as number;
  }

  function startTracking() {
    if (!browser) return;

    // Track various user activities
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];

    events.forEach(event => {
      window.addEventListener(event, updateActivity);
    });

    // Initial activity
    updateActivity();
  }

  function stopTracking() {
    if (!browser) return;

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];

    events.forEach(event => {
      window.removeEventListener(event, updateActivity);
    });

    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }
  }

  function getTimeSinceLastActivity(): number {
    let lastActivity = Date.now();
    subscribe(state => {
      lastActivity = state.lastActivity;
    })();

    return Date.now() - lastActivity;
  }

  return {
    subscribe,
    startTracking,
    stopTracking,
    updateActivity,
    getTimeSinceLastActivity
  };
}

export const activityTracker = createActivityTracker();
