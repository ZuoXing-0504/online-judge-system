import { apiFetch } from "../api.js";
import { isLoggedIn, state } from "../state.js";
import { t, DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";
import { escapeHtml, translateStatus, statusClass, showSkeleton } from "../ui.js";

function localizeProblemTitle(slug, fallbackTitle) {
  return DEMO_PROBLEM_TRANSLATIONS[state.language]?.[slug]?.title || fallbackTitle || slug;
}

function renderSubmissionCard(submission) {
  const active = state.selectedSubmission && state.selectedSubmission.id === submission.id;
  const problemTitle = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  return `
    <button class="submission-card ${active ? "active" : ""}" type="button" data-submission-id="${escapeHtml(submission.id)}">
      <strong>${escapeHtml(problemTitle)}</strong>
      <p>${escapeHtml(submission.problem_slug || "")}</p>
      <div class="meta-row">
        <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
      </div>
    </button>`;
}

export async function initSubmissionsPage() {
  const refresh = document.getElementById("refresh-submissions");
  const filter = document.getElementById("submission-status-filter");
  if (refresh) refresh.addEventListener("click", loadData);
  if (filter) filter.addEventListener("change", loadData);
  await loadData();
}

async function loadData() {
  if (!isLoggedIn()) {
    state.submissions = [];
    state.selectedSubmission = null;
    renderPage();
    return;
  }
  const status = document.getElementById("submission-status-filter")?.value || "";
  showSkeleton("submission-list", 5);
  await loadIntoState(status);
  renderPage();
  if (state.submissions.some(s => ["pending", "running"].includes(s.status))) {
    startPolling(loadData);
  } else {
    stopPolling();
  }
}

async function loadIntoState(status = "") {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (status) params.set("status", status);
  try {
    const resp = await apiFetch(`/api/v1/submissions?${params.toString()}`, {}, true);
    state.submissions = resp.items || [];
  } catch {
    state.submissions = [];
  }
}

function renderPage() {
  const list = document.getElementById("submission-list");
  if (!list) return;
  if (!isLoggedIn()) { list.innerHTML = `<div class="empty-state">${escapeHtml(t("submissionsPage.loginPrompt"))}</div>`; renderDetail(null); return; }
  if (!state.submissions.length) { list.innerHTML = `<div class="empty-state">${escapeHtml(t("submissionsPage.noSubmissions"))}</div>`; renderDetail(null); return; }
  list.innerHTML = state.submissions.map(s => renderSubmissionCard(s)).join("");
  list.querySelectorAll("[data-submission-id]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-submission-id");
      try {
        const detail = await apiFetch(`/api/v1/submissions/${id}`, {}, true);
        state.selectedSubmission = detail;
        renderPage();
      } catch { renderDetail(null); }
    });
  });
  if (!state.selectedSubmission && state.submissions[0]) {
    apiFetch(`/api/v1/submissions/${state.submissions[0].id}`, {}, true)
      .then(d => { state.selectedSubmission = d; renderDetail(d); })
      .catch(() => renderDetail(null));
  } else {
    renderDetail(state.selectedSubmission);
  }
}

function renderDetail(submission) {
  const title = document.getElementById("submission-detail-title");
  const summary = document.getElementById("submission-summary");
  const results = document.getElementById("test-results");
  if (!title || !summary || !results) return;
  if (!submission) { title.textContent = t("submissionsPage.detailTitle"); summary.textContent = t("submissionsPage.detailEmpty"); results.innerHTML = ""; return; }
  const problemTitle = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  title.textContent = `${problemTitle} - ${translateStatus(submission.status)}`;
  summary.innerHTML = `
    <div class="meta-row">
      <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.kb", { value: Math.round(submission.max_memory_used_kb || 0) }))}</span>
    </div>
    <p>${escapeHtml(submission.error_message || t("detail.noRuntimeError"))}</p>`;
  if (!submission.test_results || !submission.test_results.length) {
    results.innerHTML = `<div class="empty-state">${escapeHtml(t("detail.noResults"))}</div>`;
    return;
  }
  results.innerHTML = submission.test_results.map((r, i) => `
    <article class="test-card">
      <strong>${escapeHtml(t("detail.testLabel", { index: i + 1 }))}</strong>
      <div class="meta-row">
        <span class="status-chip ${statusClass(r.status)}">${escapeHtml(translateStatus(r.status))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(r.execution_time_ms || 0) }))}</span>
        <span class="status-chip neutral">${escapeHtml(t("common.kb", { value: Math.round(r.memory_used_kb || 0) }))}</span>
      </div>
      <p>${escapeHtml(r.error_message || t("detail.noErrorMessage"))}</p>
      ${r.output ? `<pre class="content-block">${escapeHtml(r.output)}</pre>` : ""}
    </article>`).join("");
}

function startPolling(callback) { stopPolling(); state.pollTimer = window.setInterval(callback, 3000); }
function stopPolling() { if (state.pollTimer) { clearInterval(state.pollTimer); state.pollTimer = null; } }
