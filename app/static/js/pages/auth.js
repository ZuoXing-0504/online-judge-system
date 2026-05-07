import { apiFetch } from "../api.js";
import { isLoggedIn, state, persistSession } from "../state.js";
import { t } from "../i18n.js";
import { showToast, setFeedback } from "../ui.js";

function getPostAuthRedirectPath() {
  const candidate = new URLSearchParams(window.location.search).get("next");
  if (!candidate) return "";
  try {
    const url = new URL(candidate, window.location.origin);
    if (url.origin !== window.location.origin) return "";
    if (url.pathname === "/" || url.pathname === "/auth") return "/portal";
    return `${url.pathname}${url.search}${url.hash}`;
  } catch { return ""; }
}

function openRegisterWindow() {
  const registerUrl = "/register";
  if (window.innerWidth < 768) {
    window.location.assign(registerUrl);
    return;
  }
  const w = 620, h = 760;
  const left = Math.max(0, window.screenX + Math.round((window.outerWidth - w) / 2));
  const top = Math.max(0, window.screenY + Math.round((window.outerHeight - h) / 2));
  const popup = window.open(registerUrl, "oj-register-window", `width=${w},height=${h},left=${left},top=${top},resizable=yes,scrollbars=yes`);
  if (!popup) window.location.assign(registerUrl);
  else popup.focus();
}

export function initAuthPage() {
  const feedback = document.getElementById("auth-feedback");
  const nextPath = getPostAuthRedirectPath();
  const loginForm = document.getElementById("login-form");
  const openRegister = document.getElementById("open-register");
  const registered = new URLSearchParams(window.location.search).get("registered");
  if (feedback && nextPath && !isLoggedIn()) {
    setFeedback(feedback, t("authPage.continuePrompt"));
  } else if (feedback && registered === "1") {
    setFeedback(feedback, t("auth.registerSuccess"), "success");
  }
  if (loginForm) loginForm.addEventListener("submit", handleLogin);
  if (openRegister) openRegister.addEventListener("click", openRegisterWindow);
  window.addEventListener("message", handleRegisterWindowMessage);
}

async function handleLogin(event) {
  event.preventDefault();
  const feedback = document.getElementById("auth-feedback");
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());
  try {
    const data = await apiFetch("/api/v1/auth/login", { method: "POST", body: JSON.stringify(payload) });
    persistSession(data.access_token, data.user);
    const nextPath = getPostAuthRedirectPath() || (data.user?.role === "admin" ? "/admin" : "/portal");
    showToast(t("auth.loginSuccess"), "success");
    setFeedback(feedback, t("auth.loginSuccessRedirect"), "success");
    window.setTimeout(() => { window.location.assign(nextPath); }, 120);
  } catch (error) {
    setFeedback(feedback, error.message || t("auth.loginFailed"), "error");
  }
}

function handleRegisterWindowMessage(event) {
  if (event.origin !== window.location.origin || event.data?.type !== "oj-register-success") return;
  const feedback = document.getElementById("auth-feedback");
  const usernameInput = document.querySelector('#login-form input[name="username"]');
  if (feedback) setFeedback(feedback, t("auth.registerSuccess"), "success");
  if (usernameInput && event.data.username) usernameInput.value = event.data.username;
  usernameInput?.focus();
}

export function initRegisterPage() {
  const registerForm = document.getElementById("register-form");
  const closeButton = document.getElementById("close-register-window");
  if (registerForm) registerForm.addEventListener("submit", handleRegister);
  if (closeButton) closeButton.addEventListener("click", () => {
    if (window.opener && !window.opener.closed) { window.close(); return; }
    window.location.assign("/auth");
  });
}

async function handleRegister(event) {
  event.preventDefault();
  const feedback = document.getElementById("register-feedback");
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());
  try {
    await apiFetch("/api/v1/auth/register", { method: "POST", body: JSON.stringify(payload) });
    event.currentTarget.reset();
    showToast(t("auth.registerSuccess"), "success");
    setFeedback(feedback, t("auth.registerSuccess"), "success");
    completeRegisterFlow(payload.username);
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

function completeRegisterFlow(username = "") {
  const openerWindow = window.opener;
  if (openerWindow && !openerWindow.closed) {
    try {
      openerWindow.postMessage({ type: "oj-register-success", username }, window.location.origin);
      window.setTimeout(() => window.close(), 360);
      return;
    } catch {}
  }
  const params = new URLSearchParams({ registered: "1" });
  if (username) params.set("username", username);
  window.setTimeout(() => { window.location.assign(`/auth?${params.toString()}`); }, 420);
}
