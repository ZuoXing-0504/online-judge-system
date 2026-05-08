import { apiFetch } from "../api.js";
import { isLoggedIn, state } from "../state.js";
import { t } from "../i18n.js";
import { escapeHtml, translateDifficulty, translateStatus, translateRole, difficultyClass, statusClass, showSkeleton } from "../ui.js";
import { DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";

function localizeProblemTitle(slug, fallbackTitle) {
  return DEMO_PROBLEM_TRANSLATIONS[state.language]?.[slug]?.title || fallbackTitle || slug;
}

function localizeProblem(problem) {
  if (!problem) return problem;
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[problem.slug];
  return translated ? { ...problem, ...translated } : problem;
}

function renderProblemCard(problem) {
  const localized = localizeProblem(problem);
  return `
    <a class="problem-card" href="/problem?slug=${encodeURIComponent(problem.slug)}" data-problem-link>
      <strong>${escapeHtml(localized.title)}</strong>
      <p>${escapeHtml(problem.slug)}</p>
      <div class="meta-row">
        <span class="status-chip ${difficultyClass(problem.difficulty)}">${escapeHtml(translateDifficulty(problem.difficulty))}</span>
        <span class="status-chip neutral">${escapeHtml(problem.is_public ? t("visibility.public") : t("visibility.private"))}</span>
      </div>
    </a>`;
}

function renderFeaturedProblems(listEl) {
  if (!listEl) return;
  const items = state.problems.slice(0, 4);
  if (!items.length) {
    listEl.innerHTML = `<div class="empty-state">${escapeHtml(t("problems.empty"))}</div>`;
  } else {
    listEl.innerHTML = items.map(p => renderProblemCard(p)).join("");
  }
}

async function loadProblemsIntoState(search = "", difficulty = "") {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (search) params.set("search", search);
  if (difficulty) params.set("difficulty", difficulty);
  try {
    const resp = await apiFetch(`/api/v1/problems?${params.toString()}`);
    state.problems = resp.items || [];
  } catch {
    state.problems = [];
  }
}

async function loadSubmissionsIntoState(status = "") {
  const params = new URLSearchParams({ page: "1", page_size: "20" });
  if (status) params.set("status", status);
  try {
    const resp = await apiFetch(`/api/v1/submissions?${params.toString()}`, {}, true);
    state.submissions = resp.items || [];
  } catch {
    state.submissions = [];
  }
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

export async function initHomePage() {
  showSkeleton("featured-problems", 4);
  await loadProblemsIntoState();
  if (isLoggedIn()) {
    await loadSubmissionsIntoState();
  }
  renderHomeState();
}

export function renderHomeState() {
  const metricApi = document.getElementById("metric-api");
  const metricProblems = document.getElementById("metric-problems");
  const metricSubmissions = document.getElementById("metric-submissions");
  const metricSession = document.getElementById("metric-session");
  const featuredProblems = document.getElementById("featured-problems");

  if (metricApi) metricApi.textContent = state.apiHealth === "healthy" ? t("health.healthy") : state.apiHealth === "offline" ? t("health.offline") : t("health.booting");
  if (metricProblems) metricProblems.textContent = String(state.problems.length);
  if (metricSubmissions) metricSubmissions.textContent = String(state.submissions.length);
  if (metricSession) metricSession.textContent = state.user ? translateRole(state.user.role) : t("session.guest");
  renderFeaturedProblems(featuredProblems);
  renderUserStats();
}

function renderUserStats() {
  const stats = document.getElementById("user-stats");
  if (!stats || !isLoggedIn() || !state.submissions.length) { if (stats) stats.style.display = "none"; return; }
  const accepted = state.submissions.filter(s => s.status === "accepted").length;
  stats.style.display = "";
  stats.innerHTML = `
    <div class="panel-heading"><p class="eyebrow">Your Progress</p><h2>Submission Stats</h2></div>
    <div class="stat-grid" style="margin-top:8px">
      <div class="stat-card"><span>Total</span><strong>${state.submissions.length}</strong></div>
      <div class="stat-card"><span>Accepted</span><strong>${accepted}</strong></div>
      <div class="stat-card"><span>Rate</span><strong>${Math.round(accepted / Math.max(1, state.submissions.length) * 100)}%</strong></div>
    </div>`;
