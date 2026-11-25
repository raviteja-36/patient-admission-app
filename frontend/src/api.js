// Same-origin by default (backend serves the frontend). Set VITE_API_URL if hosted separately.
const BASE = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}/api${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw Object.assign(new Error("Cannot reach the server. Check your connection and try again."), { fieldErrors: {} });
  }
  if (res.status === 204) return null;
  let data = null;
  try { data = await res.json(); } catch { /* non-JSON response */ }
  if (!res.ok) {
    throw Object.assign(new Error(data?.message || "Something went wrong. Please try again."), {
      fieldErrors: data?.errors || {},
    });
  }
  return data;
}

export const api = {
  options: () => request("/options"),
  list: (filters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    return request(`/patients?${params}`);
  },
  create: (body) => request("/patients", { method: "POST", body: JSON.stringify(body) }),
  update: (id, body) => request(`/patients/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  discharge: (id) => request(`/patients/${id}/discharge`, { method: "PATCH" }),
  remove: (id) => request(`/patients/${id}`, { method: "DELETE" }),
};
