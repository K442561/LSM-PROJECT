/**
 * LocalStorage Cache Manager for Weak-Internet and Offline PWA Mode.
 */

const KEYS = {
  LAST_PLAN: 'mre_last_plan',
  LOCKED_ROUTE: 'mre_locked_route',
  TRIP_HISTORY: 'mre_trip_history',
};

export const storage = {
  savePlan(planData) {
    try {
      localStorage.setItem(KEYS.LAST_PLAN, JSON.stringify({
        data: planData,
        savedAt: new Date().toISOString()
      }));
    } catch (e) {
      console.warn('Could not cache plan to localStorage', e);
    }
  },

  getLastPlan() {
    try {
      const raw = localStorage.getItem(KEYS.LAST_PLAN);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  saveLockedRoute(lockData) {
    try {
      localStorage.setItem(KEYS.LOCKED_ROUTE, JSON.stringify({
        data: lockData,
        savedAt: new Date().toISOString()
      }));
    } catch (e) {
      console.warn('Could not cache locked route', e);
    }
  },

  getLockedRoute() {
    try {
      const raw = localStorage.getItem(KEYS.LOCKED_ROUTE);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  clearLockedRoute() {
    try {
      localStorage.removeItem(KEYS.LOCKED_ROUTE);
    } catch (e) {}
  },

  saveHistory(historyData) {
    try {
      localStorage.setItem(KEYS.TRIP_HISTORY, JSON.stringify(historyData));
    } catch (e) {}
  },

  getHistory() {
    try {
      const raw = localStorage.getItem(KEYS.TRIP_HISTORY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }
};
