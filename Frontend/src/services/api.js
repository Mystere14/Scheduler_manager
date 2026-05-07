// This file contains functions to interact with the backend API for the Scheduler Manager.
// It handles API calls for managing Code_ens (teachers), Cours (sessions), and Absences.

const BASE_URL = 'http://localhost:8000';

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers,
  });
  if (res.status === 204) return [];

  let data;
  try {
    data = await res.json();
  } catch (_e) {
    data = [];
  }

  if (!res.ok) {
    const message = typeof data === 'object' && data && data.detail ? data.detail : JSON.stringify(data);
    const error = new Error(`API ${res.status}: ${message}`);
    error.status = res.status;
    error.payload = data;
    throw error;
  }
  return data;
}

export { request };

export default {
  // ===== Code_ens (Teachers) =====
  getCodeEns() {
    return request('/code_ens/');
  },
  getCodeEnsById(code) {
    return request(`/code_ens/${encodeURIComponent(code)}`);
  },
  createCodeEns(codeEnsData) {
    return request('/code_ens/', {
      method: 'POST',
      body: JSON.stringify(codeEnsData),
    });
  },
  updateCodeEns(code, codeEnsData) {
    return request(`/code_ens/${encodeURIComponent(code)}`, {
      method: 'PUT',
      body: JSON.stringify(codeEnsData),
    });
  },
  deleteCodeEns(code) {
    return request(`/code_ens/${encodeURIComponent(code)}`, {
      method: 'DELETE',
    });
  },

  // ===== Cours (Sessions) =====
  getCours() {
    return request('/cours/');
  },
  getCoursByTeacher(teacher) {
    return request(`/cours/teacher/${encodeURIComponent(teacher)}`);
  },
  createCours(coursData) {
    return request('/cours/', {
      method: 'POST',
      body: JSON.stringify(coursData),
    });
  },
  updateCours(id, coursData) {
    return request(`/cours/${id}`, {
      method: 'PUT',
      body: JSON.stringify(coursData),
    });
  },
  deleteCours(id) {
    return request(`/cours/${id}`, {
      method: 'DELETE',
    });
  },

  // ===== Absence (Absences) =====

  getAbsenceByEnseignant(enseignant) {
    return request(`/absences/teacher/${encodeURIComponent(enseignant)}`);
  },
  createAbsence(absenceData) {
    return request('/absences/', {
      method: 'POST',
      body: JSON.stringify(absenceData),
    });
  },
  updateAbsence(id, absenceData) {
    return request(`/absences/${id}`, {
      method: 'PUT',
      body: JSON.stringify(absenceData),
    });
  },
  deleteAbsence(id) {
    return request(`/absences/${id}`, {
      method: 'DELETE',
    });
  },
};

