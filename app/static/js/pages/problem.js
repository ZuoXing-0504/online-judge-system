import { apiFetch } from "../api.js";
import { state } from "../state.js";
import { t, DEMO_PROBLEM_TRANSLATIONS } from "../i18n.js";
import { escapeHtml, translateDifficulty, difficultyClass } from "../ui.js";

function localizeProblem(problem) {
  if (!problem) return problem;
  const translated = DEMO_PROBLEM_TRANSLATIONS[state.language]?.[problem.slug];
  return translated ? { ...problem, ...translated } : problem;
}

export async function initProblemDetailPage() {
  const slug = new URLSearchParams(window.location.search).get("slug");
  if (!slug) {
    state.selectedProblem = null;
    renderDetail();
    return;
  }
  try {
    state.selectedProblem = await apiFetch(`/api/v1/problems/${slug}`);
  } catch {
    state.selectedProblem = null;
  }
  renderDetail();
}

export function renderDetail() {
  const title = document.getElementById("problem-title");
  const intro = document.getElementById("problem-intro");
  const diff = document.getElementById("problem-difficulty-pill");
  const slugPill = document.getElementById("problem-slug-pill");
  const time = document.getElementById("problem-time-limit");
  const mem = document.getElementById("problem-memory-limit");
  const visibility = document.getElementById("problem-visibility");
  const desc = document.getElementById("problem-description");
  const input = document.getElementById("problem-input");
  const output = document.getElementById("problem-output");
  const sampleIn = document.getElementById("problem-sample-input");
  const sampleOut = document.getElementById("problem-sample-output");
  const submitLink = document.getElementById("problem-to-submit");

  if (!state.selectedProblem) {
    if (title) title.textContent = t("problemPage.placeholderTitle");
    if (intro) intro.textContent = t("problemPage.missingSlug");
    if (diff) { diff.textContent = t("problemPage.noSelection"); diff.className = "status-chip neutral"; }
    if (slugPill) slugPill.textContent = t("problemPage.slugNone");
    if (time) time.textContent = "--";
    if (mem) mem.textContent = "--";
    if (visibility) visibility.textContent = "--";
    if (desc) desc.textContent = t("problemPage.placeholderBody");
    if (input) input.textContent = t("problemPage.placeholderBody");
    if (output) output.textContent = t("problemPage.placeholderBody");
    if (sampleIn) sampleIn.textContent = "--";
    if (sampleOut) sampleOut.textContent = "--";
    if (submitLink) submitLink.href = "/submit";
    return;
  }

  const problem = localizeProblem(state.selectedProblem);
  if (title) title.textContent = problem.title;
  if (intro) intro.textContent = t("problemPage.introLoaded", { title: problem.title });
  if (diff) { diff.textContent = translateDifficulty(problem.difficulty); diff.className = `status-chip ${difficultyClass(problem.difficulty)}`; }
  if (slugPill) slugPill.textContent = t("common.slug", { slug: problem.slug });
  if (time) time.textContent = t("common.ms", { value: problem.time_limit_ms });
  if (mem) mem.textContent = t("common.kb", { value: problem.memory_limit_kb });
  if (visibility) visibility.textContent = problem.is_public ? t("visibility.public") : t("visibility.private");
  if (desc) desc.textContent = problem.description || t("statement.noDescription");
  if (input) input.textContent = problem.input_description || t("statement.noInput");
  if (output) output.textContent = problem.output_description || t("statement.noOutput");
  if (sampleIn) sampleIn.textContent = problem.sample_input || t("statement.noSample");
  if (sampleOut) sampleOut.textContent = problem.sample_output || t("statement.noSample");
  if (submitLink) submitLink.href = `/submit?slug=${encodeURIComponent(problem.slug)}`;
  renderSolution(problem);
}

function renderSolution(problem) {
  const toggleBtn = document.getElementById("solution-toggle");
  const header = document.getElementById("solution-header");
  const area = document.getElementById("solution-area");
  const explanation = document.getElementById("solution-explanation");
  const codeBlock = document.getElementById("solution-code-block");

  console.log("[solution] renderSolution called");
  console.log("[solution] toggleBtn:", !!toggleBtn, "header:", !!header, "area:", !!area);
  console.log("[solution] problem.slug:", problem.slug, "solution_code:", !!problem.solution_code, "solution_explanation:", !!problem.solution_explanation);

  if (!toggleBtn || !header || !area) {
    console.log("[solution] MISSING DOM elements — bailing");
    return;
  }

  const hasSolution = Boolean(problem.solution_code);
  console.log("[solution] hasSolution:", hasSolution);

  if (!hasSolution) {
    console.log("[solution] no solution for this problem — hiding UI");
    toggleBtn.hidden = true;
    header.hidden = true;
    area.hidden = true;
    return;
  }

  toggleBtn.hidden = false;
  toggleBtn.textContent = "Show solution";
  header.hidden = true;
  area.hidden = true;
  console.log("[solution] button visible, waiting for click");

  toggleBtn.onclick = () => {
    const visible = !area.hidden;
    console.log("[solution] button clicked — currently visible:", visible);
    if (visible) {
      header.hidden = true;
      area.hidden = true;
      toggleBtn.textContent = "Show solution";
    } else {
      if (explanation && problem.solution_explanation) {
        explanation.innerHTML = `<strong>Explanation</strong><p>${escapeHtml(problem.solution_explanation)}</p>`;
        console.log("[solution] explanation rendered, len:", problem.solution_explanation.length);
      }
      if (codeBlock && problem.solution_code) {
        codeBlock.textContent = problem.solution_code;
        console.log("[solution] code block rendered, lines:", problem.solution_code.split("\n").length);
      }
      header.hidden = false;
      area.hidden = false;
      toggleBtn.textContent = "Hide solution";
    }
  };
}
