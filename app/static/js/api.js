import { hasBearerToken, state } from "./state.js";

export async function apiFetch(path, options = {}, authenticated = false) {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if ((authenticated || hasBearerToken()) && hasBearerToken()) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }
  // Inject CSRF token from cookie
  const csrf = document.cookie.split("; ").find(r => r.startsWith("csrf_token="));
  if (csrf && !["GET", "HEAD", "OPTIONS"].includes(options.method || "GET")) {
    headers.set("X-CSRF-Token", csrf.split("=")[1]);
  }

  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  });
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof payload === "string" ? payload : payload.detail || "Request failed";
    throw new Error(message);
  }
  return payload;
}
