export const state = {
  token: "",
  authMode: "none",
  user: null,
  language: "zh-CN",
  apiHealth: "booting",
  problems: [],
  problemsTotal: 0,
  problemsPage: 1,
  selectedProblem: null,
  submissions: [],
  selectedSubmission: null,
  adminUsers: [],
  pollTimer: null,
};

export async function initSession() {
  try {
    const resp = await fetch("/api/v1/auth/me", { credentials: "include" });
    if (!resp.ok) throw new Error("Not authenticated");
    const data = await resp.json();
    state.token = "";
    state.authMode = "cookie";
    state.user = data;
  } catch {
    state.token = "";
    state.authMode = "none";
    state.user = null;
  }
}

export function persistSession(token, user) {
  state.token = token || "";
  state.authMode = token ? "bearer" : "cookie";
  state.user = user;
}

export function clearSession() {
  state.token = "";
  state.authMode = "none";
  state.user = null;
}

export function isLoggedIn() {
  return Boolean(state.user);
}

export function hasBearerToken() {
  return state.authMode === "bearer" && Boolean(state.token);
}
