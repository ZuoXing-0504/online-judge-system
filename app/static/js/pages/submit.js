import { apiFetch } from "../api.js";
import { hasBearerToken, isLoggedIn, state } from "../state.js";
import { t } from "../i18n.js";
import { showToast, setFeedback, escapeHtml, translateStatus, statusClass } from "../ui.js";
import { DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";

function localizeProblemTitle(slug, fallbackTitle) {
  return DEMO_PROBLEM_TRANSLATIONS[state.language]?.[slug]?.title || fallbackTitle || slug;
}

let _contestSlug = "";

export function initSubmitPage() {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get("slug");
  _contestSlug = params.get("contest") || "";
  const slugInput = document.getElementById("manual-problem-slug");
  const templateButton = document.getElementById("load-template");
  const submitButton = document.getElementById("submit-code");
  console.log("[submit] init — templateBtn:", !!templateButton, "submitBtn:", !!submitButton, "CodeEditor:", !!window.CodeEditor, "contest:", _contestSlug);

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
  const contestBanner = document.getElementById("contest-banner");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  if (target) target.textContent = slug ? t("common.target", { slug }) : t("submitPage.noTarget");
  if (hint) hint.textContent = state.user ? t("editor.authedHint") : t("editor.loginHint");
  if (contestBanner && _contestSlug) {
    contestBanner.innerHTML = `Contest: <strong>${escapeHtml(_contestSlug)}</strong> - submission will count toward standings`;
    contestBanner.className = "status-chip warning";
    contestBanner.style.display = "";
  }
}

function loadCodeTemplate() {
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "problem-slug";
  const lang = document.getElementById("language-select-submit")?.value || "python";
  const templates = {
    python: ["def solve() -> None:", "    # Read from stdin, write to stdout", `    # Problem slug: ${slug}`, "    pass", "", 'if __name__ == "__main__":', "    solve()"].join("\n"),
    cpp: ["#include <iostream>", "using namespace std;", "", "int main() {", "    // Read from stdin, write to stdout", `    // Problem slug: ${slug}`, "    ", "    return 0;", "}"].join("\n"),
    java: ["import java.util.*;", "", "// Read from stdin, write to stdout", `// Problem slug: ${slug}`, "public class Main {", "    public static void main(String[] args) {", "        Scanner sc = new Scanner(System.in);", "        ", "    }", "}"].join("\n"),
  };
  const code = templates[lang] || templates.python;
  console.log("[submit] loadCodeTemplate — slug:", slug, "lang:", lang);
  if (window.CodeEditor) {
    window.CodeEditor.setValue(code);
  } else {
    console.log("[submit] loadCodeTemplate — ERROR: window.CodeEditor is undefined!");
  }
}

async function handleSubmit() {
  const feedback = document.getElementById("submit-feedback");
  const slug = document.getElementById("manual-problem-slug")?.value.trim() || "";
  const code = window.CodeEditor ? window.CodeEditor.getValue() : "";
  const lang = document.getElementById("language-select-submit")?.value || "python";
  if (!isLoggedIn()) { setFeedback(feedback, t("editor.noAuth"), "error"); return; }
  if (!slug) { setFeedback(feedback, t("editor.slugRequired"), "error"); return; }
  const payload = { problem_slug: slug, code, language: lang };
  if (_contestSlug) payload.contest_slug = _contestSlug;

  // Offline queue
  if (!navigator.onLine) {
    const queue = JSON.parse(localStorage.getItem("oj_offline_queue") || "[]");
    queue.push({ ts: Date.now(), payload });
    localStorage.setItem("oj_offline_queue", JSON.stringify(queue));
    showToast("Saved offline. Will submit when back online.", "warning");
    return;
  }

  try {
    const submission = await apiFetch("/api/v1/submissions", {
      method: "POST", body: JSON.stringify(payload),
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

// Offline queue flush
async function flushOfflineQueue() {
  const raw = localStorage.getItem("oj_offline_queue");
  if (!raw) return;
  const queue = JSON.parse(raw);
  if (!queue.length) return;
  showToast(`Submitting ${queue.length} queued solution(s)...`, "info");
  for (const item of queue) {
    try {
      await apiFetch("/api/v1/submissions", { method: "POST", body: JSON.stringify(item.payload) }, true);
    } catch {}
  }
  localStorage.removeItem("oj_offline_queue");
  showToast("Queued submissions sent!", "success");
}
window.addEventListener("online", flushOfflineQueue);
if (navigator.onLine) flushOfflineQueue();
