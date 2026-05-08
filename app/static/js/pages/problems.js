import { apiFetch } from "../api.js";
import { state } from "../state.js";
import { t, DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";
import { escapeHtml, translateDifficulty, difficultyClass, showSkeleton } from "../ui.js";

const PAGE_SIZE = 20;

function localizeProblem(problem) {
  if (!problem) return problem;
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[problem.slug];
  return translated ? { ...problem, ...translated } : problem;
}

function getProblemTags(slug) {
  const m = {
    "hello-world":"IO","a-plus-b":"IO","even-odd":"If","prime-check":"Math","fibonacci":"DP",
    "valid-parentheses":"Stack","binary-search":"BS","two-sum":"Hash","fizzbuzz":"Loop",
    "max-subarray-sum":"DP","climbing-stairs":"DP","gcd":"Math","palindrome-number":"Str",
    "n-queens-count":"BT","remove-duplicates":"Set","bubble-sort":"Sort",
    "queue-simulation":"Q","stack-simulation":"Stack","josephus":"Math",
    "word-count":"Str","factorial":"Math","knapsack-01":"DP","edit-distance":"DP",
    "subset-sum":"DP","coin-change":"DP","permutations":"BT",
  };
  return m[slug] || "";
}

function renderProblemCard(problem, globalIndex) {
  const localized = localizeProblem(problem);
  const tags = getProblemTags(problem.slug);
  return `
    <a class="problem-card" href="/problem?slug=${encodeURIComponent(problem.slug)}" data-problem-link>
      <strong><span class="problem-num">#${globalIndex}</span> ${escapeHtml(localized.title)}</strong>
      <p>${escapeHtml(problem.slug)}</p>
      <div class="meta-row">
        <span class="status-chip ${difficultyClass(problem.difficulty)}">${escapeHtml(translateDifficulty(problem.difficulty))}</span>
        ${tags ? `<span class="status-chip neutral" style="font-size:0.7rem">${escapeHtml(tags)}</span>` : ""}
      </div>
    </a>`;
}

async function loadProblemsIntoState(search = "", difficulty = "", page = 1) {
  const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (search) params.set("search", search);
  if (difficulty) params.set("difficulty", difficulty);
  try {
    const resp = await apiFetch(`/api/v1/problems?${params.toString()}`);
    state.problems = resp.items || [];
    state.problemsTotal = resp.total || 0;
    state.problemsPage = resp.page || 1;
    state.problemsTotalPages = resp.total_pages || 1;
  } catch {
    state.problems = [];
    state.problemsTotal = 0;
    state.problemsPage = 1;
    state.problemsTotalPages = 1;
  }
}

async function loadWithFilters(page = 1) {
  const searchEl = document.getElementById("problem-search");
  const diffEl = document.getElementById("problem-difficulty");
  const search = searchEl?.value.trim() || "";
  const difficulty = diffEl?.value || "";
  showSkeleton("problem-list", 6);
  await loadProblemsIntoState(search, difficulty, page);
  renderPage();
}

function renderPagination() {
  const container = document.getElementById("pagination-container");
  if (!container) return;
  const page = state.problemsPage || 1;
  const total = state.problemsTotalPages || 1;
  if (total <= 1) { container.innerHTML = ""; return; }

  let html = '<div class="pagination">';
  html += `<button class="pagination-btn" data-page="${page - 1}" ${page <= 1 ? "disabled" : ""}>« Prev</button>`;

  const start = Math.max(1, page - 2);
  const end = Math.min(total, page + 2);
  if (start > 1) html += `<button class="pagination-btn" data-page="1">1</button>`;
  if (start > 2) html += `<span class="pagination-ellipsis">...</span>`;

  for (let p = start; p <= end; p++) {
    html += `<button class="pagination-btn ${p === page ? "active" : ""}" data-page="${p}">${p}</button>`;
  }

  if (end < total - 1) html += `<span class="pagination-ellipsis">...</span>`;
  if (end < total) html += `<button class="pagination-btn" data-page="${total}">${total}</button>`;

  html += `<button class="pagination-btn" data-page="${page + 1}" ${page >= total ? "disabled" : ""}>Next »</button>`;
  html += `<span class="pagination-info">${page} / ${total} (${state.problemsTotal} total)</span>`;
  html += "</div>";

  container.innerHTML = html;
  container.querySelectorAll(".pagination-btn:not([disabled])").forEach(btn => {
    btn.addEventListener("click", () => {
      const p = parseInt(btn.dataset.page);
      if (p >= 1 && p <= total) loadWithFilters(p);
    });
  });
}

function renderPage() {
  const list = document.getElementById("problem-list");
  const count = document.getElementById("problem-count");
  if (count) count.textContent = t("problemsPage.resultCount", { count: state.problemsTotal || state.problems.length });
  if (!list) return;
  if (!state.problems.length) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(t("problems.empty"))}</div>`;
  } else {
    const offset = ((state.problemsPage || 1) - 1) * PAGE_SIZE;
    list.innerHTML = state.problems.map((p, i) => renderProblemCard(p, offset + i + 1)).join("");
  }
  renderPagination();
}

export async function initProblemsPage() {
  const search = document.getElementById("problem-search");
  const difficulty = document.getElementById("problem-difficulty");
  const refresh = document.getElementById("refresh-problems");
  if (search) search.addEventListener("input", debounce(() => loadWithFilters(1), 240));
  if (difficulty) difficulty.addEventListener("change", () => loadWithFilters(1));
  if (refresh) refresh.addEventListener("click", () => loadWithFilters(1));
  await loadWithFilters(1);
}

function debounce(fn, delayMs) {
  let timerId = null;
  return (...args) => {
    if (timerId) clearTimeout(timerId);
    timerId = window.setTimeout(() => fn(...args), delayMs);
  };
}
