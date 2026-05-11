import{a as e,e as p,i as _,l as a,m as c,q as f,r as n,t as u,x as m}from"./chunk-XE672ANK.js";function b(t,s){return _[e.language]?.[t]?.title||s||t}function y(t){let s=e.selectedSubmission&&e.selectedSubmission.id===t.id,i=b(t.problem_slug,t.problem_title||t.problem_slug);return`
    <button class="submission-card ${s?"active":""}" type="button" data-submission-id="${n(t.id)}">
      <strong>${n(i)}</strong>
      <p>${n(t.problem_slug||"")}</p>
      <div class="meta-row">
        <span class="status-chip ${m(t.status)}">${n(u(t.status))}</span>
        <span class="status-chip neutral">${n(a("common.passed",{passed:t.passed_test_cases,total:t.total_test_cases}))}</span>
        <span class="status-chip neutral">${n(a("common.ms",{value:Math.round(t.max_execution_time_ms||0)}))}</span>
      </div>
    </button>`}async function P(){let t=document.getElementById("refresh-submissions"),s=document.getElementById("submission-status-filter");t&&t.addEventListener("click",d),s&&s.addEventListener("change",d),await d()}async function d(){if(!p()){e.submissions=[],e.selectedSubmission=null,g();return}let t=document.getElementById("submission-status-filter")?.value||"";f("submission-list",5),await S(t),g(),e.submissions.some(s=>["pending","running"].includes(s.status))?T(d):$()}async function S(t=""){let s=new URLSearchParams({page:"1",page_size:"20"});t&&s.set("status",t);try{let i=await c(`/api/v1/submissions?${s.toString()}`,{},!0);e.submissions=i.items||[]}catch{e.submissions=[]}}function g(){let t=document.getElementById("submission-list");if(t){if(!p()){t.innerHTML=`<div class="empty-state">${n(a("submissionsPage.loginPrompt"))}</div>`,r(null);return}if(!e.submissions.length){t.innerHTML=`<div class="empty-state">${n(a("submissionsPage.noSubmissions"))}</div>`,r(null);return}t.innerHTML=e.submissions.map(s=>y(s)).join(""),t.querySelectorAll("[data-submission-id]").forEach(s=>{s.addEventListener("click",async()=>{let i=s.getAttribute("data-submission-id");try{let o=await c(`/api/v1/submissions/${i}`,{},!0);e.selectedSubmission=o,g()}catch{r(null)}})}),!e.selectedSubmission&&e.submissions[0]?c(`/api/v1/submissions/${e.submissions[0].id}`,{},!0).then(s=>{e.selectedSubmission=s,r(s)}).catch(()=>r(null)):r(e.selectedSubmission)}}function r(t){let s=document.getElementById("submission-detail-title"),i=document.getElementById("submission-summary"),o=document.getElementById("test-results");if(!s||!i||!o)return;if(!t){s.textContent=a("submissionsPage.detailTitle"),i.textContent=a("submissionsPage.detailEmpty"),o.innerHTML="";return}let h=b(t.problem_slug,t.problem_title||t.problem_slug);if(s.textContent=`${h} - ${u(t.status)}`,i.innerHTML=`
    <div class="meta-row">
      <span class="status-chip ${m(t.status)}">${n(u(t.status))}</span>
      <span class="status-chip neutral">${n(a("common.passed",{passed:t.passed_test_cases,total:t.total_test_cases}))}</span>
      <span class="status-chip neutral">${n(a("common.ms",{value:Math.round(t.max_execution_time_ms||0)}))}</span>
      <span class="status-chip neutral">${n(a("common.kb",{value:Math.round(t.max_memory_used_kb||0)}))}</span>
    </div>
    <p>${n(t.error_message||a("detail.noRuntimeError"))}</p>`,!t.test_results||!t.test_results.length){o.innerHTML=`<div class="empty-state">${n(a("detail.noResults"))}</div>`;return}o.innerHTML=t.test_results.map((l,v)=>`
    <article class="test-card">
      <strong>${n(a("detail.testLabel",{index:v+1}))}</strong>
      <div class="meta-row">
        <span class="status-chip ${m(l.status)}">${n(u(l.status))}</span>
        <span class="status-chip neutral">${n(a("common.ms",{value:Math.round(l.execution_time_ms||0)}))}</span>
        <span class="status-chip neutral">${n(a("common.kb",{value:Math.round(l.memory_used_kb||0)}))}</span>
      </div>
      <p>${n(l.error_message||a("detail.noErrorMessage"))}</p>
      ${l.output?`<pre class="content-block">${n(l.output)}</pre>`:""}
    </article>`).join("")}function T(t){$(),e.pollTimer=window.setInterval(t,3e3)}function $(){e.pollTimer&&(clearInterval(e.pollTimer),e.pollTimer=null)}export{P as initSubmissionsPage};
//# sourceMappingURL=submissions-4Q2HWO2R.js.map
