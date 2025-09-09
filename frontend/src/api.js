// frontend/src/api.js
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handle(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
  }
  // если пустой ответ — вернём null, иначе JSON
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : null;
}

export function apiGet(path) {
  return fetch(`${API}${path}`, {
    method: "GET",
    headers: { "Accept": "application/json" },
  }).then(handle);
}

export function apiPost(path, body) {
  return fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify(body ?? {}),
  }).then(handle);
}

// Быстрый тест соединения с бэком (эндпоинт /ping должен отдавать JSON)
export function pingBackend() {
  return apiGet("/ping");
}
