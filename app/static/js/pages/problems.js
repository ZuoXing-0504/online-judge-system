import { apiFetch } from "../api.js";
import { state } from "../state.js";
import { t, DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";
import { escapeHtml, translateDifficulty, difficultyClass, showSkeleton } from "../ui.js";

function localizeProblem(problem) {
  if (!problem) return problem;
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[problem.slug];
  return translated ? { ...problem, ...translated } : problem;
}

function renderProblemCard(problem, index) {
  const localized = localizeProblem(problem);
  return `
    <a class="problem-card" href="/problem?slug=${encodeURIComponent(problem.slug)}" data-problem-link>
      <strong><span class="problem-num">#${index + 1}</span> ${escapeHtml(localized.title)}</strong>
      <p>${escapeHtml(problem.slug)}</p>
      <div class="meta-row">
        <span class="status-chip ${difficultyClass(problem.difficulty)}">${escapeHtml(translateDifficulty(problem.difficulty))}</span>
        <span class="status-chip neutral">${escapeHtml(problem.is_public ? t("visibility.public") : t("visibility.private"))}</span>
      </div>
    </a>`;
}

async function loadProblemsIntoState(search = "", difficulty = "", page = 1) {
  const params = new URLSearchParams({ page: String(page), page_size: "100" });
  if (search) params.set("search", search);
  if (difficulty) params.set("difficulty", difficulty);
  const url = `/api/v1/problems?${params.toString()}`;
  console.log("[problems] fetch:", url);
  try {
    const resp = await apiFetch(url);
    console.log("[problems] response total:", resp.total, "items:", resp.items?.length);
    state.problems = resp.items || [];
    state.problemsTotal = resp.total || 0;
    state.problemsPage = resp.page || 1;
  } catch (e) {
    console.log("[problems] fetch error:", e);
    state.problems = [];
    state.problemsTotal = 0;
  }
}

async function loadWithFilters() {
  const searchEl = document.getElementById("problem-search");
  const diffEl = document.getElementById("problem-difficulty");
  const search = searchEl?.value.trim() || "";
  const difficulty = diffEl?.value || "";
  console.log("[problems] loadWithFilters — search:", JSON.stringify(search), "difficulty:", JSON.stringify(difficulty));
  showSkeleton("problem-list", 6);
  await loadProblemsIntoState(search, difficulty);
  renderPage();
}

function renderPage() {
  const list = document.getElementById("problem-list");
  const count = document.getElementById("problem-count");
  console.log("[problems] renderPage — items:", state.problems.length, "total:", state.problemsTotal);
  if (count) count.textContent = t("problemsPage.resultCount", { count: state.problemsTotal || state.problems.length });
  if (!list) return;
  if (!state.problems.length) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("problems.empty"))}</div>`;
    return;
  }
  list.innerHTML = state.problems.map((p, i) => renderProblemCard(p, i)).join("");
}

export async function initProblemsPage() {
  console.log("[problems] initProblemsPage");
  const search = document.getElementById("problem-search");
  const difficulty = document.getElementById("problem-difficulty");
  const refresh = document.getElementById("refresh-problems");
  console.log("[problems] searchEl:", !!search, "diffEl:", !!difficulty, "refreshEl:", !!refresh);
  if (search) search.addEventListener("input", debounce(loadWithFilters, 240));
  if (difficulty) difficulty.addEventListener("change", loadWithFilters);
  if (refresh) refresh.addEventListener("click", loadWithFilters);
  await loadWithFilters();
}

function debounce(fn, delayMs) {
  let timerId = null;
  return (...args) => {
    if (timerId) clearTimeout(timerId);
    timerId = window.setTimeout(() => fn(...args), delayMs);
  };
}
