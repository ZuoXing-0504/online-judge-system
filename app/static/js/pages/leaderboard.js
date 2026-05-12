import { apiFetch } from "../api.js";
import { escapeHtml } from "../ui.js";

export async function initLeaderboardPage() {
  const list = document.getElementById("lb-list");
  const sel = document.getElementById("lb-contest");
  if (!list || !sel) return;

  try {
    const resp = await apiFetch("/api/v1/contests");
    const contests = resp.items || [];
    sel.innerHTML = contests.map(c => `<option value="${c.slug}">${escapeHtml(c.title)}</option>`).join("");
    if (contests.length) await loadLB(contests[0].slug);
  } catch { list.innerHTML = '<div class="empty-state">No contests yet.</div>'; }

  sel.addEventListener("change", () => loadLB(sel.value));
}

async function loadLB(slug) {
  const list = document.getElementById("lb-list");
  try {
    const lb = await apiFetch(`/api/v1/contests/${slug}/leaderboard`);
    if (!lb.length) { list.innerHTML = '<div class="empty-state">No participants.</div>'; return; }
    list.innerHTML = lb.map((e, i) => `
      <div class="test-card">
        <strong>${i < 3 ? ["🥇","🥈","🥉"][i] : `#${e.rank}`} ${escapeHtml(e.username)}</strong>
        <div class="meta-row">
          <span class="status-chip success">${e.solved_count} solved</span>
          <span class="status-chip neutral">${Math.floor(e.penalty/60)}m ${e.penalty%60}s</span>
        </div>
      </div>`).join("");
  } catch { list.innerHTML = '<div class="empty-state">Failed to load.</div>'; }
}
