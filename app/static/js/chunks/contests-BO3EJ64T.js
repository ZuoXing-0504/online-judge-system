import{e as f,m as l,o as h,r as a}from"./chunk-XE672ANK.js";async function I(){let e=document.getElementById("refresh-contests");e&&e.addEventListener("click",$),await $()}async function $(){let e=document.getElementById("contest-list");if(e)try{let t=(await l("/api/v1/contests")).items||[];if(!t.length){e.innerHTML='<div class="empty-state">No contests available yet.</div>';return}e.innerHTML=t.map(s=>`
      <button class="submission-card" data-contest-slug="${a(s.slug)}" type="button">
        <strong>${a(s.title)}</strong>
        <p>${a(s.slug)}</p>
        <div class="meta-row">
          <span class="status-chip success">${s.problem_count} problems</span>
          <span class="status-chip neutral">${s.participant_count} participants</span>
        </div>
      </button>
    `).join(""),e.querySelectorAll("[data-contest-slug]").forEach(s=>{s.addEventListener("click",async()=>{let o=s.dataset.contestSlug;await M(o)})})}catch{e.innerHTML='<div class="empty-state">Failed to load contests.</div>'}}var g=null,w="";function y(){g&&(clearInterval(g),g=null)}async function M(e){y(),w=e,document.getElementById("contest-detail")&&(await b(e),g=setInterval(async()=>{let t=new Date,s=document.getElementById("contest-countdown");if(s){let o=await l(`/api/v1/contests/${e}`),m=new Date(o.start_time),c=new Date(o.end_time),v=new Date(c.getTime()-o.freeze_minutes*6e4);if(t<m){let i=Math.max(0,m-t),d=Math.floor(i/36e5),u=Math.floor(i%36e5/6e4),p=Math.floor(i%6e4/1e3);s.textContent=`Starts in ${d}h ${u}m ${p}s`,s.className="status-chip warning"}else if(t<c){let i=Math.max(0,c-t),d=Math.floor(i/36e5),u=Math.floor(i%36e5/6e4),p=Math.floor(i%6e4/1e3),n=o.freeze_minutes>0&&t>=v;s.textContent=`${n?"(FROZEN) ":""}Ends in ${d}h ${u}m ${p}s`,s.className=n?"status-chip warning":"status-chip running"}else s.textContent="Contest ended",s.className="status-chip danger",y()}Math.floor(Date.now()/3e4)%2===0&&await E(e)},1e4))}async function b(e){let r=document.getElementById("contest-detail");try{let t=await l(`/api/v1/contests/${e}`),s=await l(`/api/v1/contests/${e}/leaderboard`),o=new Date,m=new Date(t.start_time),c=new Date(t.end_time),v=new Date(c.getTime()-t.freeze_minutes*6e4),i=o<m?"Upcoming":o>c?"Ended":"Running",d=t.freeze_minutes>0&&o>=v&&o<c,u=s.length?s.map(n=>`
      <div class="test-card">
        <strong>#${n.rank} ${a(n.username)}</strong>
        <div class="meta-row">
          <span class="status-chip success">${n.solved_count} solved</span>
          <span class="status-chip neutral">${Math.floor(n.penalty/60)}m ${n.penalty%60}s</span>
        </div>
      </div>
    `).join(""):'<div class="empty-state">No participants on the leaderboard yet.</div>';r.innerHTML=`
      <div class="panel-heading">
        <p class="eyebrow">${i}${d?" \xB7 Board Frozen":""}</p>
        <h2>${a(t.title)}</h2>
      </div>
      <div style="margin-bottom:14px"><span id="contest-countdown" class="status-chip neutral">Loading...</span></div>
      <p>${a(t.description||"")}</p>
      <div class="stat-grid">
        <div class="stat-card"><span>Start</span><strong>${m.toLocaleString()}</strong></div>
        <div class="stat-card"><span>End</span><strong>${c.toLocaleString()}</strong></div>
        <div class="stat-card"><span>Problems</span><strong>${t.problem_count}</strong></div>
        <div class="stat-card"><span>Participants</span><strong>${t.participant_count}</strong></div>
      </div>
      ${t.problems&&t.problems.length?`
        <div class="panel-heading" style="margin-top:18px">
          <p class="eyebrow">Problems</p><h2>Contest problems</h2>
        </div>
        <div class="stack-list">
          ${t.problems.map(n=>`
            <a class="problem-card" href="/problem?slug=${a(n.slug)}">
              <strong><span class="problem-num">${a(n.label||"?")}</span> ${a(n.title||n.slug)}</strong>
              <p>${a(n.slug)}</p>
            </a>
          `).join("")}
        </div>
      `:""}
      ${f()?`<button class="primary-button" id="register-contest-btn" style="margin-top:14px" data-slug="${e}">Register</button>`:""}
      <div class="panel-heading" style="margin-top:20px">
        <p class="eyebrow">Leaderboard${d?" (FROZEN)":""}</p>
        <h2>Rankings</h2>
      </div>
      <div class="stack-list" id="leaderboard-list">${u}</div>
    `;let p=document.getElementById("register-contest-btn");p&&p.addEventListener("click",async()=>{try{await l(`/api/v1/contests/${e}/register`,{method:"POST"},!0),h("Registered successfully!","success"),await b(e)}catch(n){h(n.message,"error")}})}catch{r.innerHTML='<div class="empty-state">Failed to load contest detail.</div>'}}async function E(e){try{let r=await l(`/api/v1/contests/${e}/leaderboard`),t=document.getElementById("leaderboard-list");if(!t)return;if(!r.length){t.innerHTML='<div class="empty-state">No participants yet.</div>';return}t.innerHTML=r.map(s=>`
      <div class="test-card">
        <strong>#${s.rank} ${a(s.username)}</strong>
        <div class="meta-row">
          <span class="status-chip success">${s.solved_count} solved</span>
          <span class="status-chip neutral">${Math.floor(s.penalty/60)}m ${s.penalty%60}s</span>
        </div>
      </div>
    `).join("")}catch{}}export{I as initContestsPage};
//# sourceMappingURL=contests-BO3EJ64T.js.map
