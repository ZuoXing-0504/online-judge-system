import { apiFetch } from "../api.js";
import { hasBearerToken, isLoggedIn, state } from "../state.js";
import { t } from "../i18n.js";
import { showToast, setFeedback, escapeHtml, translateStatus, statusClass } from "../ui.js";
import { DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";

function localizeProblemTitle(slug, fallbackTitle) {
  return DEMO_PROBLEM_TRANSLATIONS[state.language]?.[slug]?.title || fallbackTitle || slug;
}

export function initSubmitPage() {
  const slug = new URLSearchParams(window.location.search).get("slug");
  const slugInput = document.getElementById("manual-problem-slug");
  const templateButton = document.getElementById("load-template");
  const submitButton = document.getElementById("submit-code");
  console.log("[submit] init — templateBtn:", !!templateButton, "submitBtn:", !!submitButton, "CodeEditor:", !!window.CodeEditor);

  if (slug && slugInput) slugInput.value = slug;
  if (templateButton) {
    templateButton.addEventListener("click", () => {
      console.log("[submit] '加载模板' button CLICKED");
      loadCodeTemplate();
    });
  } else {
    console.log("[submit] WARNING: #load-template button not found in DOM");
  }
  if (submitButton) submitButton.addEventListener("click", handleSubmit);
  renderSubmit();
}

export function renderSubmit() {
  const target = document.getElementById("editor-target");
  const hint = document.getElementById("editor-hint");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  if (target) target.textContent = slug ? t("common.target", { slug }) : t("submitPage.noTarget");
  if (hint) hint.textContent = state.user ? t("editor.authedHint") : t("editor.loginHint");
}

function loadCodeTemplate() {
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "problem-slug";
  const code = [
    "def solve() -> None:",
    `    ${t("editor.templateLine1")}`,
    `    ${t("editor.templateLine2", { slug })}`,
    "    pass",
    "",
    'if __name__ == "__main__":',
    "    solve()",
  ].join("\n");
  console.log("[submit] loadCodeTemplate — slug:", slug, "codeLen:", code.length, "CodeEditor:", !!window.CodeEditor, "enhanced:", window.CodeEditor?._enhanced);
  if (window.CodeEditor) {
    window.CodeEditor.setValue(code);
    console.log("[submit] loadCodeTemplate — setValue done, current value:", window.CodeEditor.getValue().slice(0, 60));
  } else {
    console.log("[submit] loadCodeTemplate — ERROR: window.CodeEditor is undefined!");
  }
}

async function handleSubmit() {
  const feedback = document.getElementById("submit-feedback");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  const code = window.CodeEditor ? window.CodeEditor.getValue() : "";
  if (!isLoggedIn()) { setFeedback(feedback, t("editor.noAuth"), "error"); return; }
  if (!slug) { setFeedback(feedback, t("editor.slugRequired"), "error"); return; }
  try {
    const submission = await apiFetch("/api/v1/submissions", {
      method: "POST", body: JSON.stringify({ problem_slug: slug, code, language: "python" }),
    }, true);
    showToast(t("editor.queueSuccess", { id: submission.id }), "success");
    setFeedback(feedback, t("editor.queueSuccess", { id: submission.id }), "success");
    renderSubmit();
    watchSingleSubmission(submission.id);
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

function watchSingleSubmission(submissionId) {
  stopPolling();
  const card = document.getElementById("latest-submission-card");
  if (card) { card.className = "empty-state"; card.textContent = `${t("submitPage.latestTitle")}: ${submissionId}`; }

  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  const tokenQuery = hasBearerToken() ? `?token=${encodeURIComponent(state.token)}` : "";
  const url = `${proto}://${window.location.host}/api/v1/submissions/${submissionId}/ws${tokenQuery}`;
  const socket = new WebSocket(url);
  socket.onmessage = (event) => {
    try {
      const detail = JSON.parse(event.data);
      if (detail.error) { renderLatestCard(null, detail.error); socket.close(); return; }
      state.selectedSubmission = detail;
      renderLatestCard(detail);
      if (!["pending", "running"].includes(detail.status)) socket.close();
    } catch {}
  };
  socket.onerror = () => renderLatestCard(null, "WebSocket connection failed");
  socket.onclose = () => stopPolling();
  state.pollTimer = { socket, close: () => socket.close() };
}

function renderLatestCard(submission, errorMessage = "") {
  const card = document.getElementById("latest-submission-card");
  if (!card) return;
  if (!submission) { card.className = "empty-state"; card.textContent = errorMessage || t("submitPage.resultEmpty"); return; }
  const title = localizeProblemTitle(submission.problem_slug, submission.problem_title || submission.problem_slug);
  card.className = "test-card";
  card.innerHTML = `
    <strong>${escapeHtml(title)}</strong>
    <p>${escapeHtml(translateStatus(submission.status))}</p>
    <div class="meta-row">
      <span class="status-chip ${statusClass(submission.status)}">${escapeHtml(translateStatus(submission.status))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.passed", { passed: submission.passed_test_cases, total: submission.total_test_cases }))}</span>
      <span class="status-chip neutral">${escapeHtml(t("common.ms", { value: Math.round(submission.max_execution_time_ms || 0) }))}</span>
    </div>`;
}

function stopPolling() {
  if (!state.pollTimer) return;
  if (state.pollTimer.close) state.pollTimer.close();
  else clearInterval(state.pollTimer);
  state.pollTimer = null;
}
