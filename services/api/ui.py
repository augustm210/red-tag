# ruff: noqa: E501

from fastapi.responses import HTMLResponse


def judge_console() -> HTMLResponse:
    return HTMLResponse(
        content=r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Red Tag — Incident Command</title>
  <style>
    :root{--ink:#11100e;--paper:#f3efe6;--red:#f04438;--line:#cbc3b5;--muted:#6d685e}
    *{box-sizing:border-box} body{margin:0;background:var(--ink);color:var(--paper);font-family:Inter,ui-sans-serif,system-ui,sans-serif}
    body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.11;background-image:linear-gradient(rgba(255,255,255,.25) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.25) 1px,transparent 1px);background-size:48px 48px}
    main{position:relative;max-width:1180px;margin:auto;padding:28px 24px 64px}.nav{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #403d37;padding-bottom:20px}
    .brand{font-weight:900;letter-spacing:.18em}.tag{display:inline-block;background:var(--red);color:white;padding:5px 9px;margin-right:9px;transform:rotate(-2deg)}
    .live{font:12px ui-monospace,monospace;color:#9ef0b1}.live:before{content:"";display:inline-block;width:7px;height:7px;background:#46d369;border-radius:50%;margin-right:7px;box-shadow:0 0 12px #46d369}
    .hero{display:grid;grid-template-columns:1.35fr .65fr;gap:48px;padding:72px 0 56px}.eyebrow{font:12px ui-monospace,monospace;letter-spacing:.16em;color:#ff8e85;text-transform:uppercase}
    h1{font-size:clamp(48px,8vw,96px);letter-spacing:-.065em;line-height:.88;margin:18px 0 28px;max-width:820px}.hero p{font-size:19px;line-height:1.55;color:#bbb5aa;max-width:690px}
    .proof{align-self:end;border-left:1px solid #4b4740;padding-left:24px}.proof div{padding:14px 0;border-bottom:1px solid #34312d;font:13px ui-monospace,monospace}.proof b{display:block;color:white;font-size:18px;margin-bottom:4px}
    .console{background:var(--paper);color:var(--ink);border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.35)}.bar{background:var(--red);color:white;padding:15px 20px;display:flex;justify-content:space-between;font:700 12px ui-monospace,monospace;letter-spacing:.08em}
    .grid{display:grid;grid-template-columns:320px 1fr}.control{padding:28px;border-right:1px solid var(--line)}.control h2,.trace h2{margin:0 0 10px;font-size:22px}.control p{color:var(--muted);font-size:14px;line-height:1.5}
    button{width:100%;margin-top:18px;border:0;background:var(--ink);color:white;padding:15px 16px;font-weight:800;letter-spacing:.04em;cursor:pointer}button:hover{background:#292621}button:disabled{opacity:.5;cursor:wait}
    .note{font:11px/1.5 ui-monospace,monospace;color:var(--muted);margin-top:18px}.trace{padding:28px;min-height:430px}.empty{height:300px;display:grid;place-items:center;color:#898276;text-align:center}.empty b{display:block;color:var(--ink);font-size:17px;margin-bottom:6px}
    .status{display:flex;gap:9px;align-items:center;font:12px ui-monospace,monospace;margin:14px 0 22px}.pill{padding:5px 8px;border:1px solid var(--line)}
    .stage{display:grid;grid-template-columns:150px 1fr;gap:18px;padding:15px 0;border-top:1px solid var(--line);font-size:13px}.stage strong{font:700 11px ui-monospace,monospace;text-transform:uppercase}.stage span{color:var(--muted);line-height:1.5}.stage details{margin-top:7px}.stage summary{cursor:pointer;color:var(--ink);font:10px ui-monospace,monospace;letter-spacing:.08em}.stage pre{white-space:pre-wrap;max-height:260px;overflow:auto;background:#e8e2d6;padding:12px;font:11px/1.45 ui-monospace,monospace}
    .success{margin-top:18px;background:#dff4df;border-left:4px solid #248c3d;padding:15px;font:13px ui-monospace,monospace}.blocked{background:#ffe0dc;border-left-color:var(--red)}
    footer{color:#777168;font:11px ui-monospace,monospace;padding-top:24px;display:flex;justify-content:space-between}
    @media(max-width:800px){.hero,.grid{grid-template-columns:1fr}.hero{padding-top:48px}.proof{display:none}.control{border-right:0;border-bottom:1px solid var(--line)}.stage{grid-template-columns:1fr}.nav small{display:none}}
  </style>
</head>
<body><main>
  <nav class="nav"><div class="brand"><span class="tag">RED</span>TAG / INCIDENT COMMAND</div><small class="live">SYSTEM ONLINE</small></nav>
  <section class="hero">
    <div><div class="eyebrow">Background operations agent · safety first</div><h1>When the disk turns red, the agent acts once.</h1><p>Red Tag detects pressure, separates evidence from hypotheses, chooses the smallest reversible action, and proves recovery. Retries may repeat reasoning. They never repeat the operational action.</p></div>
    <aside class="proof"><div><b>Gemini 3.6 Flash</b>global Vertex AI endpoint</div><div><b>Google ADK 2.7</b>five specialist workflow</div><div><b>Cloud Run + Firestore</b>private worker, durable claims</div></aside>
  </section>
  <section class="console">
    <div class="bar"><span>JUDGE PROOF CONSOLE</span><span id="clock">READY</span></div>
    <div class="grid">
      <div class="control"><h2>Run the proof</h2><p>Create a background disk-pressure incident and watch the private worker reason, act through the safety boundary, verify closure, then reject a duplicate delivery.</p><button id="run">RUN CLOUD PIPELINE</button><div class="note">This button validates the cloud control plane and safe demo adapter. The Windows executor performs the measurable filesystem cleanup in the local-terminal demonstration.</div></div>
      <div class="trace"><h2>Evidence timeline</h2><div id="output" class="empty"><div><b>No incident selected</b>One click creates a real Firestore record.</div></div></div>
    </div>
  </section>
  <footer><span>PROJECT / red-tag-agentic-2026-0815</span><span>NO CHAT PROMPT · AUDIT EVERYTHING</span></footer>
</main>
<script>
const out=document.querySelector('#output'),btn=document.querySelector('#run'),clock=document.querySelector('#clock');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function safe(s){const d=document.createElement('div');d.textContent=String(s??'');return d.innerHTML}
function brief(s){return String(s??'').replace(/[#*`_|]/g,' ').replace(/\s+/g,' ').trim().slice(0,260)}
function render(i,replay){
  const stages=i.events.filter(e=>e.event_type==='agent_stage_completed');
  const rows=stages.map(e=>`<div class="stage"><strong>${safe(e.actor)}</strong><span>${safe(brief(e.data.summary))}<details><summary>VIEW FULL EVIDENCE</summary><pre>${safe(e.data.summary)}</pre></details></span></div>`).join('');
  const action=i.actions[0];
  out.className='';out.innerHTML=`<div class="status"><span class="pill">${safe(i.severity)}</span><span class="pill">${safe(i.status).toUpperCase()}</span><span>${safe(i.id)}</span></div>${rows||'<div class="stage"><strong>dispatch</strong><span>Private worker is processing the incident…</span></div>'}${action?`<div class="success">ACTION ${safe(action.action).toUpperCase()} / ${safe(action.status).toUpperCase()}<br>IDEMPOTENCY ${safe(action.idempotency_key)}</div>`:''}${replay?`<div class="success blocked">REPLAY ${safe(replay.outcome).toUpperCase()} / ACTION COUNT REMAINS ${i.actions.length}</div>`:''}`;
}
btn.onclick=async()=>{btn.disabled=true;btn.textContent='PIPELINE RUNNING…';clock.textContent='DISPATCHING';try{
  const created=await fetch('/v1/incidents',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({title:'Managed cache pressure detected',description:'Background threshold crossed: managed cache growth threatens terminal availability.',service:'windows-disk',severity:'SEV2',requested_action:'clear_cache',signals:{source:'judge-console',managed_cache_bytes:268435456,free_space_percent:4.8}})}).then(r=>{if(!r.ok)throw Error('create '+r.status);return r.json()});
  let current=created;for(let n=0;n<70;n++){current=await fetch('/v1/incidents/'+created.id).then(r=>r.json());render(current);clock.textContent=current.status.toUpperCase();if(['closed','failed','awaiting_approval'].includes(current.status))break;await sleep(2000)}
  if(current.status==='closed'){clock.textContent='REPLAYING';const replay=await fetch('/v1/demo/incidents/'+created.id+'/replay',{method:'POST'}).then(r=>r.json());current=await fetch('/v1/incidents/'+created.id).then(r=>r.json());render(current,replay);clock.textContent='PROOF COMPLETE'}
}catch(e){out.className='empty';out.innerHTML='<div><b>Pipeline error</b>'+safe(e.message)+'</div>';clock.textContent='ERROR'}finally{btn.disabled=false;btn.textContent='RUN AGAIN'}};
</script></body></html>"""
    )
