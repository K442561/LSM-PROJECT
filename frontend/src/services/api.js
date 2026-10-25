/**
 * Backend API Client with Offline Fallback.
 */

import { storage } from './storage';

const API_BASE = import.meta.env.VITE_API_URL || '';

async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 8000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

export const api = {
  async planTrip(payload) {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `Server responded with ${res.status}`);
      }

      const data = await res.json();
      // Cache fresh plan
      storage.savePlan(data);
      return { data, isOfflineData: false };
    } catch (err) {
      console.warn('Network plan request failed, checking offline cache...', err);
      const cached = storage.getLastPlan();
      if (cached && cached.data) {
        return { data: cached.data, isOfflineData: true, savedAt: cached.savedAt };
      }
      throw new Error(`Unable to fetch plan: ${err.message}. No offline saved plan found.`);
    }
  },

  async lockRoute(payload) {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/lock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Lock failed with status ${res.status}`);
      }
      const data = await res.json();
      storage.saveLockedRoute(data);
      return { data, isOfflineData: false };
    } catch (err) {
      // Offline fallback: save locally
      console.warn('Network lock failed, saving locally...', err);
      const offlineLock = {
        locked_id: Date.now(),
        is_active: true,
        route_id: payload.route_id,
        route_name: payload.route_data?.route_name || 'Locked Route',
        ...payload
      };
      storage.saveLockedRoute(offlineLock);
      return { data: offlineLock, isOfflineData: true };
    }
  },

  async getLockedRoute() {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/lock`);
      if (res.ok) {
        const data = await res.json();
        if (data.is_active) {
          storage.saveLockedRoute(data);
        } else {
          storage.clearLockedRoute();
        }
        return { data, isOfflineData: false };
      }
    } catch (err) {
      console.warn('Could not fetch active lock from server, checking local storage...');
    }

    const cached = storage.getLockedRoute();
    if (cached && cached.data && cached.data.is_active) {
      return { data: cached.data, isOfflineData: true };
    }
    return { data: { is_active: false }, isOfflineData: false };
  },

  async unlockRoute() {
    try {
      await fetchWithTimeout(`${API_BASE}/unlock`, { method: 'POST' });
    } catch (e) {}
    storage.clearLockedRoute();
    return { is_active: false };
  },

  async logTrip(payload) {
    const res = await fetchWithTimeout(`${API_BASE}/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to submit trip log');
    }
    return await res.json();
  },

  async getHistory() {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/history`);
      if (res.ok) {
        const data = await res.json();
        storage.saveHistory(data);
        return { data, isOfflineData: false };
      }
    } catch (err) {
      console.warn('History fetch failed, using local cache', err);
    }

    const cached = storage.getHistory();
    if (cached) {
      return { data: cached, isOfflineData: true };
    }
    return { data: { total_trips: 0, average_delay_min: 0, logs: [] }, isOfflineData: true };
  },

  async checkHealth() {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/health`, { timeout: 3000 });
      return res.ok;
    } catch {
      return false;
    }
  }
};
