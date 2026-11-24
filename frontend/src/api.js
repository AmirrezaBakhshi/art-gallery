const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

let csrfToken = null;
let csrfTokenRequest = null;

async function getCsrfToken() {
  if (csrfToken) return csrfToken;

  if (!csrfTokenRequest) {
    csrfTokenRequest = fetch(`${API_BASE_URL}/api/auth/csrf/`, {
      credentials: "include",
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Unable to initialize a secure session. Check API CORS and cookie settings.");
        }
        const payload = await response.json();
        if (!payload.csrfToken) {
          throw new Error("The server did not return a CSRF token.");
        }
        csrfToken = payload.csrfToken;
        return csrfToken;
      })
      .finally(() => {
        csrfTokenRequest = null;
      });
  }

  return csrfTokenRequest;
}

export async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const method = (options.method || "GET").toUpperCase();

  if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    headers.set("X-CSRFToken", await getCsrfToken());
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`, {
    ...options,
    credentials: "include",
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
  if (!payload?.gallery) {
    throw new Error("The server returned an invalid authentication response.");
  }
  localStorage.setItem("user", JSON.stringify(payload.gallery));
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
