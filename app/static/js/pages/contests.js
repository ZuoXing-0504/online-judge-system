import { apiFetch } from "../api.js";
import { state, isLoggedIn } from "../state.js";
import { t } from "../i18n.js";
import { escapeHtml, showToast } from "../ui.js";

export async function initContestsPage() {
  const refresh = document.getElementById("refresh-contests");
  if (refresh) refresh.addEventListener("click", loadContests);
  await loadContests();
}

async function loadContests() {
  const list = document.getElementById("contest-list");
  if (!list) return;
  try {
    const resp = await apiFetch("/api/v1/contests");
    const items = resp.items || [];
    if (!items.length) {
      list.innerHTML = `<div class="empty-state">No contests available yet.</div>`;
      return;
    }
    list.innerHTML = items.map(c => `
      <button class="submission-card" data-contest-slug="${escapeHtml(c.slug)}" type="button">
        <strong>${escapeHtml(c.title)}</strong>
        <p>${escapeHtml(c.slug)}</p>
        <div class="meta-row">
          <span class="status-chip success">${c.problem_count} problems</span>
          <span class="status-chip neutral">${c.participant_count} participants</span>
        </div>
      </button>
    `).join("");

    list.querySelectorAll("[data-contest-slug]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const slug = btn.dataset.contestSlug;
        await loadContestDetail(slug);
      });
    });
  } catch {
    list.innerHTML = `<div class="empty-state">Failed to load contests.</div>`;
  }
}

let _contestTimer = null;
let _currentContestSlug = "";

function stopContestTimer() {
  if (_contestTimer) { clearInterval(_contestTimer); _contestTimer = null; }
}

async function loadContestDetail(slug) {
  stopContestTimer();
  _currentContestSlug = slug;
  const detail = document.getElementById("contest-detail");
  if (!detail) return;
  await renderContestDetail(slug);

  _contestTimer = setInterval(async () => {
    const now = new Date();
    const countdownEl = document.getElementById("contest-countdown");
    if (countdownEl) {
      const c = await apiFetch(`/api/v1/contests/${slug}`);
      const start = new Date(c.start_time);
      const end = new Date(c.end_time);
      const freezeAt = new Date(end.getTime() - c.freeze_minutes * 60000);

      if (now < start) {
        const diff = Math.max(0, start - now);
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        countdownEl.textContent = `Starts in ${h}h ${m}m ${s}s`;
        countdownEl.className = "status-chip warning";
      } else if (now < end) {
        const diff = Math.max(0, end - now);
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        const frozen = c.freeze_minutes > 0 && now >= freezeAt;
        countdownEl.textContent = `${frozen ? "(FROZEN) " : ""}Ends in ${h}h ${m}m ${s}s`;
        countdownEl.className = frozen ? "status-chip warning" : "status-chip running";
      } else {
        countdownEl.textContent = "Contest ended";
        countdownEl.className = "status-chip danger";
        stopContestTimer();
      }
    }
    // Refresh leaderboard every other tick (60s)
    if (Math.floor(Date.now() / 30000) % 2 === 0) {
      await refreshLeaderboard(slug);
    }
  }, 10000);
}

async function renderContestDetail(slug) {
  const detail = document.getElementById("contest-detail");
  try {
    const c = await apiFetch(`/api/v1/contests/${slug}`);
    const lb = await apiFetch(`/api/v1/contests/${slug}/leaderboard`);
    const now = new Date();
    const start = new Date(c.start_time);
    const end = new Date(c.end_time);
    const freezeAt = new Date(end.getTime() - c.freeze_minutes * 60000);
    const status = now < start ? "Upcoming" : now > end ? "Ended" : "Running";
    const frozen = c.freeze_minutes > 0 && now >= freezeAt && now < end;

    let lbHtml = lb.length ? lb.map(e => `
      <div class="test-card">
        <strong>#${e.rank} ${escapeHtml(e.username)}</strong>
        <div class="meta-row">
          <span class="status-chip success">${e.solved_count} solved</span>
          <span class="status-chip neutral">${Math.floor(e.penalty / 60)}m ${e.penalty % 60}s</span>
        </div>
      </div>
    `).join("") : `<div class="empty-state">No participants on the leaderboard yet.</div>`;

    detail.innerHTML = `
      <div class="panel-heading">
        <p class="eyebrow">${status}${frozen ? " · Board Frozen" : ""}</p>
        <h2>${escapeHtml(c.title)}</h2>
      </div>
      <div style="margin-bottom:14px"><span id="contest-countdown" class="status-chip neutral">Loading...</span></div>
      <p>${escapeHtml(c.description || "")}</p>
      <div class="stat-grid">
        <div class="stat-card"><span>Start</span><strong>${start.toLocaleString()}</strong></div>
        <div class="stat-card"><span>End</span><strong>${end.toLocaleString()}</strong></div>
        <div class="stat-card"><span>Problems</span><strong>${c.problem_count}</strong></div>
        <div class="stat-card"><span>Participants</span><strong>${c.participant_count}</strong></div>
      </div>
      ${isLoggedIn() ? `<button class="primary-button" id="register-contest-btn" style="margin-top:14px" data-slug="${slug}">Register</button>` : ''}
      <div class="panel-heading" style="margin-top:20px">
        <p class="eyebrow">Leaderboard${frozen ? " (FROZEN)" : ""}</p>
        <h2>Rankings</h2>
      </div>
      <div class="stack-list" id="leaderboard-list">${lbHtml}</div>
    `;

    const regBtn = document.getElementById("register-contest-btn");
    if (regBtn) {
      regBtn.addEventListener("click", async () => {
        try {
          await apiFetch(`/api/v1/contests/${slug}/register`, { method: "POST" }, true);
          showToast("Registered successfully!", "success");
          await renderContestDetail(slug);
        } catch (e) { showToast(e.message, "error"); }
      });
    }
  } catch (e) {
    detail.innerHTML = `<div class="empty-state">Failed to load contest detail.</div>`;
  }
}

async function refreshLeaderboard(slug) {
  try {
    const lb = await apiFetch(`/api/v1/contests/${slug}/leaderboard`);
    const list = document.getElementById("leaderboard-list");
    if (!list) return;
    if (!lb.length) {
      list.innerHTML = `<div class="empty-state">No participants yet.</div>`;
      return;
    }
    list.innerHTML = lb.map(e => `
      <div class="test-card">
        <strong>#${e.rank} ${escapeHtml(e.username)}</strong>
        <div class="meta-row">
          <span class="status-chip success">${e.solved_count} solved</span>
          <span class="status-chip neutral">${Math.floor(e.penalty / 60)}m ${e.penalty % 60}s</span>
        </div>
      </div>
    `).join("");
  } catch {}
}
