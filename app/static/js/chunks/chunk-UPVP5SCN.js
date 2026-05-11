import{a as e,e as r,i as c,l as n,m as l,q as m,r as i,u as p,v as u,w as d}from"./chunk-XE672ANK.js";function f(t){if(!t)return t;let s=c[e.language]?.[t.slug];return s?{...t,...s}:t}function h(t){let s=f(t);return`
    <a class="problem-card" href="/problem?slug=${encodeURIComponent(t.slug)}" data-problem-link>
      <strong>${i(s.title)}</strong>
      <p>${i(t.slug)}</p>
      <div class="meta-row">
        <span class="status-chip ${d(t.difficulty)}">${i(p(t.difficulty))}</span>
        <span class="status-chip neutral">${i(t.is_public?n("visibility.public"):n("visibility.private"))}</span>
      </div>
    </a>`}function b(t){if(!t)return;let s=e.problems.slice(0,4);s.length?t.innerHTML=s.map(a=>h(a)).join(""):t.innerHTML=`<div class="empty-state">${i(n("problems.empty"))}</div>`}async function y(t="",s=""){let a=new URLSearchParams({page:"1",page_size:"20"});t&&a.set("search",t),s&&a.set("difficulty",s);try{let o=await l(`/api/v1/problems?${a.toString()}`);e.problems=o.items||[]}catch{e.problems=[]}}async function v(t=""){let s=new URLSearchParams({page:"1",page_size:"20"});t&&s.set("status",t);try{let a=await l(`/api/v1/submissions?${s.toString()}`,{},!0);e.submissions=a.items||[]}catch{e.submissions=[]}}async function L(){m("featured-problems",4),await y(),r()&&await v(),S()}function S(){let t=document.getElementById("metric-api"),s=document.getElementById("metric-problems"),a=document.getElementById("metric-submissions"),o=document.getElementById("metric-session"),g=document.getElementById("featured-problems");t&&(t.textContent=e.apiHealth==="healthy"?n("health.healthy"):e.apiHealth==="offline"?n("health.offline"):n("health.booting")),s&&(s.textContent=String(e.problems.length)),a&&(a.textContent=String(e.submissions.length)),o&&(o.textContent=e.user?u(e.user.role):n("session.guest")),b(g),$()}function $(){let t=document.getElementById("user-stats");if(!t||!r()||!e.submissions.length){t&&(t.style.display="none");return}let s=e.submissions.filter(a=>a.status==="accepted").length;t.style.display="",t.innerHTML=`
    <div class="panel-heading"><p class="eyebrow">Your Progress</p><h2>Submission Stats</h2></div>
    <div class="stat-grid" style="margin-top:8px">
      <div class="stat-card"><span>Total</span><strong>${e.submissions.length}</strong></div>
      <div class="stat-card"><span>Accepted</span><strong>${s}</strong></div>
      <div class="stat-card"><span>Rate</span><strong>${Math.round(s/Math.max(1,e.submissions.length)*100)}%</strong></div>
    </div>`}export{L as a,S as b};
//# sourceMappingURL=chunk-UPVP5SCN.js.map
