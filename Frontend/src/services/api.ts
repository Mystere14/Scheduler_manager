// This file contains functions to interact with the backend API for the Scheduler Manager.
// It handles API calls for managing Code_ens (teachers), Cours (sessions), and Absences.

const BASE_URL = 'http://localhost:8000';

async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, any> = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers,
  });

  const text = await res.text(); // 🔥 toujours lire brut

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${text}`);
  }

  // si pas de body
  if (!text) return null;

  return JSON.parse(text);
}

export { request };

export default {
  // ===== Code_ens (Teachers) =====
  getCodeEns() {
    return request('/code_ens/');
  },
  getCodeEnsById(code: string) {
    return request(`/code_ens/${encodeURIComponent(code)}`);
  },
  createCodeEns(codeEnsData: any) {
    return request('/code_ens/', {
      method: 'POST',
      body: JSON.stringify(codeEnsData),
    });
  },
  updateCodeEns(code: string, codeEnsData: any) {
    return request(`/code_ens/${encodeURIComponent(code)}`, {
      method: 'PUT',
      body: JSON.stringify(codeEnsData),
    });
  },
  deleteCodeEns(code: string) {
    return request(`/code_ens/${encodeURIComponent(code)}`, {
      method: 'DELETE',
    });
  },

  // ===== Cours (Sessions) =====
  getCours() {
    return request('/cours/');
  },
  getCoursByTeacher(teacher: string) {
    return request(`/cours/teacher/${encodeURIComponent(teacher)}`);
  },
  createCours(coursData: any) {
    return request('/cours/', {
      method: 'POST',
      body: JSON.stringify(coursData),
    });
  },
  updateCours(id: string, coursData: any) {
    return request(`/cours/${id}`, {
      method: 'PUT',
      body: JSON.stringify(coursData),
    });
  },
  deleteCours(id: string) {
    return request(`/cours/${id}`, {
      method: 'DELETE',
    });
  },

  // ===== Input_cours (Input Courses) =====
  getInputCours() {
    return request('/input_cours/');
  },
  createInputCours(inputCoursData: any) {
    return request('/input_cours/', {
      method: 'POST',
      body: JSON.stringify(inputCoursData),
    });
  },
  updateInputCours(id: string, inputCoursData: any) {
    return request(`/input_cours/${id}`, {
      method: 'PUT',
      body: JSON.stringify(inputCoursData),
    });
  },
  deleteInputCoursById(id: string) {
    return request(`/input_cours/${id}`, {
      method: 'DELETE',
    });
  },
  deleteInputCours() {
    return request('/input_cours/', {
      method: 'DELETE',
    });
  },
  // ===== Absence (Absences) =====

  getAbsenceByEnseignant(enseignant: string) {
    return request(`/absences/teacher/${encodeURIComponent(enseignant)}`);
  },
  createAbsence(absenceData: any) {
    return request('/absences/', {
      method: 'POST',
      body: JSON.stringify(absenceData),
    });
  },
  updateAbsence(id: string, absenceData: any) {
    return request(`/absences/${id}`, {
      method: 'PUT',
      body: JSON.stringify(absenceData),
    });
  },
  deleteAbsence(id: string) {
    return request(`/absences/${id}`, {
      method: 'DELETE',
    });
  },
};

