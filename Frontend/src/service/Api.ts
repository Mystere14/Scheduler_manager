// This file contains functions to interact with the backend API for the Scheduler Manager.
// It handles API calls for managing CodeEns (teachers), Cours (sessions), and Absences.

// Use dynamic API URL for desktop app compatibility
const BASEURL = (window as any).__APIURL__ || 'http://localhost:8000';

async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, any> = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const url = `${BASEURL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers,
  });

  const text = await res.text(); 

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${text}`);
  }

  // si pas de body
  if (!text) return null;

  return JSON.parse(text);
}

export { request };

export default {
// ===== AnalyticsTimeslot (Analytics) =====
  getAnalyticsTimeslot() { 
    return request('/analyticsTimeslot/', {
      method: 'GET',
    });
  },
  createAnalyticsTimeslot(analyticsTimeslotData: any) {
    return request('/analyticsTimeslot/', {
      method: 'POST',
      body: JSON.stringify(analyticsTimeslotData),
    });
  },
  async createAnalyticsTimeslotByPreprocessedSchedulerPlanned(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const headers: Record<string, any> = {};
    
    const url = `${(window as any).__APIURL__}/analyticsTimeslot/preprocessedSchedulerPlanned`;
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    const text = await res.text();

    if (!res.ok) {
      throw new Error(`API ${res.status}: ${text}`);
    }

    if (!text) return null;
    return JSON.parse(text);
  },
  async createAnalyticsTimeslotFromVcalendar(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const headers: Record<string, any> = {};
    // Don't set Content-Type, let the browser set it with boundary
    
    const url = `${(window as any).__APIURL__ || 'http://localhost:8000'}/analyticsTimeslot/vcalendar`;
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    const text = await res.text();

    if (!res.ok) {
      throw new Error(`API ${res.status}: ${text}`);
    }

    if (!text) return null;
    return JSON.parse(text);
  },
  async createAnalyticsTimeslotWithEachSpreadsheet(schedulerPlanned: any,schedulerPlaced: any) {
    const formData = new FormData();
    
    const plannedBlob = new Blob([JSON.stringify(schedulerPlanned)], { type: 'application/json' });
    const placedBlob = new Blob([JSON.stringify(schedulerPlaced)], { type: 'application/json' });
    
    formData.append('FileschedulerPlanned', plannedBlob, 'scheduled_planned.json');
    formData.append('schedulerPlaced', placedBlob, 'scheduled_placed.json');

    const url = `${(window as any).__APIURL__ || 'http://localhost:8000'}/analyticsTimeslot/withEachSpreadsheet`;
    const res = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    const text = await res.text();

    if (!res.ok) {
      throw new Error(`API ${res.status}: ${text}`);
    }

  },
  updateAnalyticsTimeslot(analyticsTimeslotData: any) {
    return request('/analyticsTimeslot/', {
      method: 'PUT',
      body: JSON.stringify(analyticsTimeslotData),
    });
  },
  deleteAnalyticsTimeslot() {
    return request('/analyticsTimeslot/', {
      method: 'DELETE',
    });
  },
  // ===== lesson  =====
  getCompareScheduler() {
    return request('/lesson/', {
      method: 'GET',
    });
  },
  getTrueLesson() {
    return request('/lesson/getTrueLesson', {
      method: 'GET',
    });
  },
  getFalseLesson() {
    return request('/lesson/getFalseLesson', {
      method: 'GET',
    });
  },
  deleteLesson() {
    return request('/lesson/', {
      method: 'DELETE',
    });
  },
  deleteTrueLesson() {
    return request('/lesson/trueLesson', {
      method: 'DELETE',
    });
  },
};

