import { t } from "./i18n.js";

export function ensureToastContainer() {
  if (!document.getElementById("toast-container")) {
    const el = document.createElement("div");
    el.id = "toast-container";
    el.className = "toast-container";
    el.setAttribute("aria-live", "polite");
    document.body.appendChild(el);
  }
}

export function showToast(message, kind = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${kind}`;
  toast.textContent = message;
  container.appendChild(toast);
  toast.addEventListener("animationend", () => {
    if (toast.style.opacity === "0") toast.remove();
  });
  return toast;
}

showToast.promise = function (promise, { loading, success, error }) {
  const toast = showToast(loading, "info");
  promise.then(() => {
    if (toast.parentNode) toast.remove();
    showToast(success, "success");
  }).catch((e) => {
    if (toast.parentNode) toast.remove();
    showToast(error || e.message, "error");
  });
};

showToast.undo = function (message, undoAction, duration = 5000) {
  const toast = showToast(message + " (Undo)", "warning");
  toast.style.cursor = "pointer";
  toast.addEventListener("click", () => { undoAction(); toast.remove(); });
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, duration);
};

export function setFeedback(node, message, kind = "") {
  if (!node) return;
  node.textContent = message;
  node.className = "feedback";
  if (kind) node.classList.add(kind);
}

export function renderSkeletonCards(count) {
  return Array.from({ length: count }, () => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>
  `).join("");
}

export function showSkeleton(containerId, count = 4) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = renderSkeletonCards(count);
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function debounce(fn, delayMs) {
  let timerId = null;
  return (...args) => {
    if (timerId) clearTimeout(timerId);
    timerId = window.setTimeout(() => fn(...args), delayMs);
  };
}

export function formToJson(form) {
  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    if (payload[key] !== undefined) return;
    const field = form.querySelector(`[name="${CSS.escape(key)}"]`);
    if (field?.type === "checkbox") {
      payload[key] = field.checked;
    } else {
      payload[key] = value;
    }
  });
  form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    if (!(checkbox.name in payload)) payload[checkbox.name] = checkbox.checked;
  });
  return payload;
}

export function translateStatus(status) {
  return t(`status.${status}`) || status;
}

export function translateDifficulty(difficulty) {
  return t(`difficulty.${difficulty}`);
}

export function translateRole(role) {
  return role === "admin" ? t("session.roleAdmin") : t("session.roleUser");
}

export function difficultyClass(difficulty) {
  if (difficulty === "easy") return "success";
  if (difficulty === "medium") return "warning";
  return "danger";
}

export function statusClass(status) {
  if (status === "accepted") return "success";
  if (status === "pending" || status === "running") return "running";
  if (status === "wrong_answer" || status === "time_limit_exceeded") return "warning";
  return "danger";
}
