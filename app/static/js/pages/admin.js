import { apiFetch } from "../api.js";
import { state } from "../state.js";
import { t } from "../i18n.js";
import { showToast, setFeedback, escapeHtml, translateRole, formToJson } from "../ui.js";

export async function initAdminPage() {
  const problemForm = document.getElementById("problem-create-form");
  const testCaseForm = document.getElementById("test-case-form");
  const refreshUsers = document.getElementById("refresh-users");
  if (problemForm) problemForm.addEventListener("submit", handleProblemCreate);
  if (testCaseForm) testCaseForm.addEventListener("submit", handleTestCaseCreate);
  if (refreshUsers) refreshUsers.addEventListener("click", loadAdminUsers);
  renderGate();
  if (state.user?.role === "admin") await loadAdminUsers();
}

function renderGate() {
  const gate = document.getElementById("admin-gate-message");
  if (!gate) return;
  if (state.user?.role === "admin") { setFeedback(gate, t("adminPage.accessGranted"), "success"); setFormsDisabled(false); }
  else { setFeedback(gate, t("adminPage.accessDenied"), "error"); setFormsDisabled(true); }
}

function setFormsDisabled(disabled) {
  ["problem-create-form", "test-case-form"].forEach(id => {
    const form = document.getElementById(id);
    if (!form) return;
    form.querySelectorAll("input, textarea, select, button").forEach(node => { node.disabled = disabled; });
  });
  const refresh = document.getElementById("refresh-users");
  if (refresh) refresh.disabled = disabled;
}

async function handleProblemCreate(event) {
  event.preventDefault();
  const feedback = document.getElementById("problem-create-feedback");
  try {
    const payload = formToJson(event.currentTarget);
    payload.is_public = Boolean(payload.is_public);
    const created = await apiFetch("/api/v1/problems", { method: "POST", body: JSON.stringify(payload) }, true);
    showToast(t("adminPage.createProblemSuccess", { slug: created.slug }), "success");
    setFeedback(feedback, t("adminPage.createProblemSuccess", { slug: created.slug }), "success");
    event.currentTarget.reset();
  } catch (error) { setFeedback(feedback, error.message, "error"); }
}

async function handleTestCaseCreate(event) {
  event.preventDefault();
  const feedback = document.getElementById("test-case-feedback");
  try {
    const payload = formToJson(event.currentTarget);
    const slug = payload.problem_slug;
    const request = { input: payload.input, expected_output: payload.expected_output, is_sample: Boolean(payload.is_sample), order: Number(payload.order || 0) };
    await apiFetch(`/api/v1/problems/${encodeURIComponent(slug)}/test-cases`, { method: "POST", body: JSON.stringify(request) }, true);
    showToast(t("adminPage.createTestCaseSuccess", { slug }), "success");
    setFeedback(feedback, t("adminPage.createTestCaseSuccess", { slug }), "success");
    event.currentTarget.reset();
  } catch (error) { setFeedback(feedback, error.message, "error"); }
}

async function loadAdminUsers() {
  if (state.user?.role !== "admin") { renderUsers(); return; }
  try { const resp = await apiFetch("/api/v1/admin/users?page=1&page_size=50", {}, true); state.adminUsers = resp.items || []; }
  catch { state.adminUsers = []; }
  renderUsers();
}

function renderUsers() {
  const list = document.getElementById("admin-user-list");
  if (!list) return;
  if (state.user?.role !== "admin") { list.innerHTML = `<div class="empty-state">${escapeHtml(t("adminPage.accessDenied"))}</div>`; return; }
  const users = state.adminUsers || [];
  if (!users.length) { list.innerHTML = `<div class="empty-state">${escapeHtml(t("adminPage.noUsers"))}</div>`; return; }
  list.innerHTML = users.map(user => `
    <article class="user-card" data-user-id="${escapeHtml(user.id)}">
      <strong>${escapeHtml(user.username)}</strong>
      <p>${escapeHtml(user.email)}</p>
      <div class="meta-row"><span class="status-chip neutral">${escapeHtml(translateRole(user.role))}</span></div>
      <div class="user-actions">
        <select data-role-select>
          <option value="user" ${user.role === "user" ? "selected" : ""}>${escapeHtml(t("session.roleUser"))}</option>
          <option value="admin" ${user.role === "admin" ? "selected" : ""}>${escapeHtml(t("session.roleAdmin"))}</option>
        </select>
        <button class="secondary-button compact" type="button" data-change-role>${escapeHtml(t("adminPage.changeRole"))}</button>
      </div>
    </article>`).join("");
  list.querySelectorAll("[data-change-role]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const card = btn.closest("[data-user-id]");
      const userId = card?.getAttribute("data-user-id");
      const role = card?.querySelector("[data-role-select]")?.value;
      await changeRole(userId, role);
    });
  });
}

async function changeRole(userId, role) {
  const feedback = document.getElementById("admin-user-feedback");
  try {
    const updated = await apiFetch(`/api/v1/admin/users/${userId}/role?role=${encodeURIComponent(role)}`, { method: "PATCH" }, true);
    showToast(t("adminPage.roleUpdated", { username: updated.username }), "success");
    setFeedback(feedback, t("adminPage.roleUpdated", { username: updated.username }), "success");
    await loadAdminUsers();
  } catch (error) { setFeedback(feedback, error.message, "error"); }
}
