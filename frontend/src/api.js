const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export function apiFetch(path, options = {}) {
  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers || {});

  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`, {
    ...options,
    headers,
  });
}

export async function readApiResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || Object.values(payload).flat().find((value) => typeof value === "string") || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return payload;
}

export function saveSession(payload) {
  if (!payload?.gallery || !payload?.token) {
    throw new Error("The server returned an invalid authentication response.");
  }
  localStorage.setItem("user", JSON.stringify(payload.gallery));
  localStorage.setItem("authToken", payload.token);
}

export function clearSession() {
  localStorage.removeItem("user");
  localStorage.removeItem("authToken");
  localStorage.removeItem("item");
  localStorage.removeItem("item_index");
  localStorage.removeItem("gallary_id");
}

export async function logoutSession() {
  try {
    await apiFetch("/api/auth/logout/", { method: "POST" });
  } finally {
    clearSession();
  }
}
