import { apiFetch } from "../api.js";
import { state, isLoggedIn } from "../state.js";
import { showToast, escapeHtml } from "../ui.js";

export async function initSettingsPage() {
  if (!isLoggedIn()) return;

  document.getElementById("settings-username").textContent = state.user?.username || "--";
  document.getElementById("settings-email").textContent = state.user?.email || "--";
  document.getElementById("settings-role").textContent = state.user?.role || "--";
  document.getElementById("settings-joined").textContent = state.user?.created_at
    ? new Date(state.user.created_at).toLocaleDateString() : "--";

  const form = document.getElementById("password-form");
  if (form) form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const fb = document.getElementById("password-feedback");
    try {
      await apiFetch("/api/v1/users/me/password", {
        method: "PATCH",
        body: JSON.stringify(Object.fromEntries(fd)),
      }, true);
      showToast("Password updated", "success");
      fb.textContent = "Password changed successfully.";
      fb.className = "feedback success";
      e.target.reset();
    } catch (err) {
      fb.textContent = err.message;
      fb.className = "feedback error";
    }
  });
}
