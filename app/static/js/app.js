import { state, persistSession, clearSession, isLoggedIn, initSession } from "./state.js";
import { t, resolveLanguage, detectLanguage, SUPPORTED_LANGUAGES, RTL_LANGUAGES } from "./i18n.js";
import { apiFetch } from "./api.js";
import { ensureToastContainer, showToast, escapeHtml, setFeedback, translateRole, translateDifficulty } from "./ui.js";
import { initHomePage, renderHomeState } from "./pages/home.js";
import { initAuthPage, initRegisterPage } from "./pages/auth.js";
import { initProblemsPage } from "./pages/problems.js";
import { initProblemDetailPage, renderDetail } from "./pages/problem.js";
import { initSubmitPage, renderSubmit } from "./pages/submit.js";
import { initSubmissionsPage } from "./pages/submissions.js";
import { initAdminPage } from "./pages/admin.js";
import { initContestsPage } from "./pages/contests.js";

const PAGE = document.body.dataset.page || "home";
const DEFAULT_USER_PATH = "/portal";
const DEFAULT_ADMIN_PATH = "/admin";

const PAGE_TO_NAV = {
  home: "home", auth: "auth", register: "auth",
  problems: "problems", "problem-detail": "problems",
  submit: "submit", submissions: "submissions", admin: "admin", contests: "contests",
};

const PAGE_META = {
  home: { title: "meta.homeTitle", description: "meta.homeDescription" },
  auth: { title: "meta.authTitle", description: "meta.authDescription" },
  register: { title: "meta.registerTitle", description: "meta.registerDescription" },
  problems: { title: "meta.problemsTitle", description: "meta.problemsDescription" },
  "problem-detail": { title: "meta.problemTitle", description: "meta.problemDescription" },
  submit: { title: "meta.submitTitle", description: "meta.submitDescription" },
  submissions: { title: "meta.submissionsTitle", description: "meta.submissionsDescription" },
  admin: { title: "meta.adminTitle", description: "meta.adminDescription" },
  contests: { title: "Contests - Online Judge System", description: "Browse and join coding contests." },
};

const PROTECTED_PAGES = new Set(["home", "problems", "problem-detail", "submit", "submissions", "admin", "contests"]);
const PROTECTED_PATHS = new Set(["/portal", "/problems", "/problem", "/submit", "/submissions", "/admin"]);

// Init
state.language = resolveLanguage(localStorage.getItem("oj_language") || detectLanguage());

document.addEventListener("DOMContentLoaded", async () => {
  buildLanguageOptions();
  bindGlobalEvents();
  activateNav();
  applyLanguage(state.language, false);
  syncHeader();
  ensureToastContainer();
  bindKeyboardShortcuts();
  initTheme();
  registerServiceWorker();
  injectManifest();
  await initSession();
  syncHeader();
  if (!enforcePageAccess()) return;
  await loadHealth();
  await initializePage();
});

function injectManifest() {
  if (document.querySelector('link[rel="manifest"]')) return;
  const link = document.createElement("link");
  link.rel = "manifest";
  link.href = "/static/manifest.json";
  document.head.appendChild(link);
}

function registerServiceWorker() {
  if ("serviceWorker" in navigator && !navigator.serviceWorker.controller) {
    navigator.serviceWorker.register("/static/sw.js");
  }
}

function bindKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    const isCtrlAlt = e.ctrlKey || e.metaKey;
    const tag = e.target.tagName;

    if (e.key === "Escape") {
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      const from = document.getElementById("submission-status-filter");
      if (from) from.value = "";
      if (PAGE === "submissions") {
        state.selectedSubmission = null;
        import("./pages/submissions.js").then(m => m.initSubmissionsPage());
      }
      if (PAGE === "problems") {
        import("./pages/problems.js").then(m => m.initProblemsPage());
      }
      return;
    }

    if (!isCtrlAlt) return;
    if (e.key === "Enter" && PAGE === "submit") {
      e.preventDefault();
      document.getElementById("submit-code")?.click();
    }
    if (e.key === "k" || e.key === "K") {
      e.preventDefault();
      if (PAGE === "problems") {
        document.getElementById("problem-search")?.focus();
      } else {
        window.location.assign("/problems");
      }
    }
    if (e.shiftKey && (e.key === "L" || e.key === "l") && PAGE === "submit") {
      e.preventDefault();
      document.getElementById("load-template")?.click();
    }
  });
}

function buildLanguageOptions() {
  const select = document.getElementById("language-select");
  if (!select) return;
  select.innerHTML = SUPPORTED_LANGUAGES.map(l => `<option value="${escapeHtml(l.code)}">${escapeHtml(l.label)}</option>`).join("");
  select.value = state.language;
}

function bindGlobalEvents() {
  const langSelect = document.getElementById("language-select");
  const logoutBtn = document.getElementById("logout-button");
  if (langSelect) langSelect.addEventListener("change", e => applyLanguage(e.currentTarget.value));
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  bindProtectedLinks();
}

function activateNav() {
  const current = PAGE_TO_NAV[PAGE] || PAGE;
  document.querySelectorAll("[data-nav]").forEach(link => {
    link.classList.toggle("active", link.dataset.nav === current);
  });
}

function enforcePageAccess() {
  if ((PAGE === "auth" || PAGE === "register") && isLoggedIn()) {
    window.location.replace(isLoggedIn() && state.user?.role === "admin" ? DEFAULT_ADMIN_PATH : DEFAULT_USER_PATH);
    return false;
  }
  if (PAGE === "admin" && isLoggedIn() && state.user?.role !== "admin") {
    window.location.replace(DEFAULT_USER_PATH);
    return false;
  }
  if (PAGE === "auth" || isLoggedIn()) return true;
  if (PROTECTED_PAGES.has(PAGE)) { redirectToAuth(); return false; }
  return true;
}

function applyLanguage(language, persist = true) {
  state.language = resolveLanguage(language);
  if (persist) localStorage.setItem("oj_language", state.language);
  document.documentElement.lang = state.language;
  document.documentElement.dir = RTL_LANGUAGES.has(state.language) ? "rtl" : "ltr";
  const sel = document.getElementById("language-select");
  if (sel) sel.value = state.language;
  const meta = PAGE_META[PAGE] || PAGE_META.home;
  document.title = t(meta.title);
  const desc = document.getElementById("page-description");
  if (desc) desc.setAttribute("content", t(meta.description));
  document.querySelectorAll("[data-i18n]").forEach(n => { n.textContent = t(n.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(n => { n.setAttribute("placeholder", t(n.dataset.i18nPlaceholder)); });
  syncHeader();
  renderHealth();
  applyAccessibility();
  if (PAGE === "home") renderHomeState();
  else if (PAGE === "problems") { import("./pages/problems.js").then(m => m.initProblemsPage()); }
  else if (PAGE === "problem-detail") renderDetail();
  else if (PAGE === "submit") renderSubmit();
  else if (PAGE === "submissions") { import("./pages/submissions.js").then(m => m.initSubmissionsPage()); }
  else if (PAGE === "admin") { import("./pages/admin.js").then(m => m.initAdminPage()); }
}

function syncHeader() {
  const loggedIn = isLoggedIn();
  const name = document.getElementById("session-name");
  const role = document.getElementById("session-role");
  const authLink = document.getElementById("auth-link");
  const adminEntry = document.getElementById("admin-entry");
  const logoutBtn = document.getElementById("logout-button");

  if (name) name.textContent = loggedIn ? state.user.username : t("session.guest");
  if (role) role.textContent = loggedIn ? `${translateRole(state.user.role)} - ${state.user.email}` : t("session.guestHint");
  if (authLink) { authLink.textContent = loggedIn ? t("session.account") : t("session.signIn"); authLink.href = loggedIn ? (state.user?.role === "admin" ? DEFAULT_ADMIN_PATH : DEFAULT_USER_PATH) : "/"; authLink.classList.toggle("hidden", false); }
  if (adminEntry) adminEntry.classList.toggle("hidden", !(loggedIn && state.user?.role === "admin"));
  if (logoutBtn) logoutBtn.classList.toggle("hidden", !loggedIn);
}

async function loadHealth() {
  try { await apiFetch("/api/v1/health"); state.apiHealth = "healthy"; }
  catch { state.apiHealth = "offline"; }
  renderHealth();
}

function renderHealth() {
  const pill = document.getElementById("health-pill");
  if (!pill) return;
  if (state.apiHealth === "healthy") { pill.textContent = t("health.onlinePill"); pill.className = "status-chip success"; }
  else if (state.apiHealth === "offline") { pill.textContent = t("health.offlinePill"); pill.className = "status-chip danger"; }
  else { pill.textContent = t("health.checking"); pill.className = "status-chip neutral"; }
}

async function initializePage() {
  if (PAGE === "home") { await initHomePage(); return; }
  if (PAGE === "auth") { initAuthPage(); return; }
  if (PAGE === "register") { initRegisterPage(); return; }
  if (PAGE === "problems") { await initProblemsPage(); return; }
  if (PAGE === "problem-detail") { await initProblemDetailPage(); return; }
  if (PAGE === "submit") { initSubmitPage(); return; }
  if (PAGE === "submissions") { await initSubmissionsPage(); return; }
  if (PAGE === "admin") { await initAdminPage(); }
  if (PAGE === "contests") { await initContestsPage(); }
}

function initTheme() {
  document.documentElement.setAttribute("data-theme", "light");
}

async function logout() {
  try { await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" }); } catch {}
  clearSession();
  stopAllPolling();
  showToast(t("auth.logoutSuccess"), "info");
  window.setTimeout(() => { window.location.assign("/"); }, 100);
}

function stopAllPolling() {
  if (state.pollTimer) {
    if (state.pollTimer.close) state.pollTimer.close();
    else clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

function applyAccessibility() {
  document.querySelectorAll(".status-chip:not([role])").forEach(el => {
    el.setAttribute("role", "status");
    if (!el.getAttribute("aria-label")) el.setAttribute("aria-label", el.textContent?.trim() || "");
  });
  document.querySelectorAll("nav a:not([aria-label])").forEach(el => {
    el.setAttribute("aria-label", el.textContent?.trim() || "");
  });
  document.querySelectorAll("input:not([id])").forEach((el, i) => {
    const label = el.closest("label");
    if (label) {
      el.id = el.id || `field-${i}-${Math.random().toString(36).slice(2, 7)}`;
      const span = label.querySelector("span");
      if (span && !span.getAttribute("for")) span.setAttribute("for", el.id);
    }
  });
  const codeEditor = document.getElementById("code-editor");
  if (codeEditor && codeEditor.tagName !== "TEXTAREA" && !codeEditor.getAttribute("aria-label")) {
    codeEditor.setAttribute("aria-label", "Code editor");
  }
  document.querySelectorAll("[data-page]").forEach(el => {
    el.setAttribute("role", "main");
  });
}

function redirectToAuth(nextPath = currentLocationPath()) {
  const target = sanitizeNextPath(nextPath);
  const params = new URLSearchParams();
  if (target) params.set("next", target);
  window.location.replace(params.toString() ? `/?${params.toString()}` : "/");
}

function sanitizeNextPath(candidate) {
  if (!candidate) return "";
  try {
    const url = new URL(candidate, window.location.origin);
    if (url.origin !== window.location.origin) return "";
    if (url.pathname === "/" || url.pathname === "/auth") return "";
    return `${url.pathname}${url.search}${url.hash}`;
  } catch { return ""; }
}

function currentLocationPath() {
  return `${window.location.pathname}${window.location.search}${window.location.hash}`;
}

function bindProtectedLinks(root = document) {
  root.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute("href");
    if (!href || href.startsWith("#")) return;
    let url;
    try { url = new URL(link.href, window.location.origin); }
    catch { return; }
    if (url.origin !== window.location.origin || !PROTECTED_PATHS.has(url.pathname)) return;
    link.addEventListener("click", (event) => {
      if (isLoggedIn()) return;
      event.preventDefault();
      redirectToAuth(`${url.pathname}${url.search}${url.hash}`);
    });
  });
}
