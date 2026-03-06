"""NAKAI × OpenFang Command Center — Ultra-futuristic agent management dashboard."""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from api.admin_routes import verify_admin
from config import settings

logger = logging.getLogger(__name__)

command_center_router = APIRouter(tags=["Command Center"])

_of_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _of_client
    if _of_client is None or _of_client.is_closed:
        _of_client = httpx.AsyncClient(
            base_url=settings.openfang_base_url,
            timeout=httpx.Timeout(15.0, connect=5.0),
        )
    return _of_client


async def _proxy(path: str, params: dict = None) -> dict:
    try:
        r = await _get_client().get(path, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        return {"error": "OpenFang unreachable", "status": "offline"}
    except httpx.HTTPStatusError as e:
        return {"error": f"OpenFang returned {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


# ── Proxy endpoints ──────────────────────────────────────────

@command_center_router.get("/api/openfang/status")
async def of_status(_: bool = Depends(verify_admin)):
    return await _proxy("/api/status")


@command_center_router.get("/api/openfang/agents")
async def of_agents(_: bool = Depends(verify_admin)):
    return await _proxy("/api/agents")


@command_center_router.get("/api/openfang/hands")
async def of_hands(_: bool = Depends(verify_admin)):
    return await _proxy("/api/hands")


@command_center_router.get("/api/openfang/skills")
async def of_skills(_: bool = Depends(verify_admin)):
    return await _proxy("/api/skills")


@command_center_router.get("/api/openfang/budget")
async def of_budget(_: bool = Depends(verify_admin)):
    return await _proxy("/api/budget")


@command_center_router.get("/api/openfang/budget/agents")
async def of_budget_agents(_: bool = Depends(verify_admin)):
    return await _proxy("/api/budget/agents")


@command_center_router.get("/api/openfang/events")
async def of_events(_: bool = Depends(verify_admin), limit: int = Query(30)):
    return await _proxy("/api/comms/events", {"limit": limit})


@command_center_router.get("/api/openfang/models")
async def of_models(_: bool = Depends(verify_admin)):
    return await _proxy("/api/models")


@command_center_router.get("/api/openfang/providers")
async def of_providers(_: bool = Depends(verify_admin)):
    return await _proxy("/api/providers")


# ── Dashboard HTML ───────────────────────────────────────────

_HAND_LABELS = {
    "lead": {"ja": "リード生成", "icon": "chart"},
    "collector": {"ja": "市場調査", "icon": "search"},
    "predictor": {"ja": "需要予測", "icon": "crystal"},
    "researcher": {"ja": "研究分析", "icon": "flask"},
    "twitter": {"ja": "権威構築", "icon": "bird"},
    "browser": {"ja": "ウェブ自動化", "icon": "globe"},
}

_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --cc-bg:#0a0f0b;--cc-s:#111a13;--cc-s2:#182219;
  --cc-b:rgba(64,101,70,.18);--cc-m:#406546;
  --cc-mg:rgba(64,101,70,.35);--cc-mb:#5a8a62;
  --cc-c:#F9F0E2;--cc-cd:rgba(249,240,226,.4);--cc-cd2:rgba(249,240,226,.12);
  --cc-r:#e74c3c;--cc-a:#f39c12;--cc-bl:#3498db;
  --cc-gl:rgba(17,26,19,.78);
  --cc-f:'Work Sans',sans-serif;
  --cc-mono:'SF Mono','Fira Code','Consolas',monospace;
  --ease:cubic-bezier(.22,1,.36,1);
}
html{font-size:16px}
body{background:var(--cc-bg);color:var(--cc-c);font-family:var(--cc-f);
  min-height:100vh;-webkit-font-smoothing:antialiased}
a{color:var(--cc-mb);text-decoration:none}
/* BG grid */
.cc-bg{position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(circle at 20% 30%,rgba(64,101,70,.05) 0%,transparent 50%),
    radial-gradient(circle at 80% 70%,rgba(64,101,70,.03) 0%,transparent 50%),
    linear-gradient(rgba(64,101,70,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(64,101,70,.025) 1px,transparent 1px);
  background-size:100% 100%,100% 100%,44px 44px,44px 44px;
  animation:ccGrid 25s linear infinite}
@keyframes ccGrid{from{background-position:0 0,0 0,0 0,0 0}to{background-position:0 0,0 0,44px 44px,44px 44px}}
/* Login */
.cc-login{position:fixed;inset:0;z-index:999;display:flex;align-items:center;
  justify-content:center;background:var(--cc-bg)}
.cc-login-box{background:var(--cc-gl);backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);border:1px solid var(--cc-b);
  border-radius:20px;padding:40px;max-width:380px;width:90%;text-align:center}
.cc-login-box h1{font-size:.88rem;font-weight:500;letter-spacing:.12em;
  text-transform:uppercase;margin-bottom:8px;color:var(--cc-mb)}
.cc-login-box p{font-size:.7rem;color:var(--cc-cd);margin-bottom:24px}
.cc-login-box input{width:100%;background:rgba(64,101,70,.08);border:1px solid var(--cc-b);
  border-radius:10px;padding:12px 16px;color:var(--cc-c);font-size:.78rem;
  font-family:var(--cc-f);outline:none;transition:border-color .3s}
.cc-login-box input:focus{border-color:var(--cc-m)}
.cc-login-box button{width:100%;margin-top:14px;background:var(--cc-m);border:none;
  border-radius:10px;padding:12px;color:#fff;font-size:.76rem;font-weight:500;
  font-family:var(--cc-f);cursor:pointer;letter-spacing:.06em;transition:all .3s var(--ease)}
.cc-login-box button:hover{background:var(--cc-mb);box-shadow:0 0 24px var(--cc-mg)}
.cc-login-err{color:var(--cc-r);font-size:.68rem;margin-top:10px;min-height:18px}
/* Header */
.cc-header{position:sticky;top:0;z-index:100;display:flex;align-items:center;
  justify-content:space-between;padding:14px 24px;
  background:rgba(17,26,19,.92);backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--cc-b);
  box-shadow:0 0 30px rgba(64,101,70,.06)}
.cc-hdr-left{display:flex;align-items:center;gap:14px}
.cc-hdr-logo{font-size:.82rem;font-weight:600;letter-spacing:.08em;color:var(--cc-c)}
.cc-hdr-logo span{color:var(--cc-mb)}
.cc-hdr-sub{font-size:.62rem;color:var(--cc-cd);letter-spacing:.15em}
.cc-hdr-badges{display:flex;gap:8px;align-items:center}
.cc-badge{display:inline-flex;align-items:center;gap:5px;
  background:rgba(64,101,70,.1);border:1px solid rgba(64,101,70,.15);
  border-radius:8px;padding:4px 10px;font-size:.6rem;color:var(--cc-cd);
  letter-spacing:.04em}
.cc-badge--live{border-color:rgba(74,222,128,.25);color:rgba(74,222,128,.9)}
.cc-badge--off{border-color:rgba(231,76,60,.25);color:rgba(231,76,60,.9)}
.cc-hdr-logout{background:none;border:1px solid var(--cc-b);border-radius:8px;
  padding:5px 12px;color:var(--cc-cd);font-size:.6rem;cursor:pointer;
  font-family:var(--cc-f);transition:all .3s}
.cc-hdr-logout:hover{border-color:var(--cc-r);color:var(--cc-r)}
/* Ticker */
.cc-ticker{overflow:hidden;white-space:nowrap;background:var(--cc-s);
  border-bottom:1px solid var(--cc-b);padding:5px 0;position:relative;z-index:50}
.cc-ticker-inner{display:inline-block;animation:ccTick 40s linear infinite;
  font-size:.58rem;color:var(--cc-cd);letter-spacing:.06em}
.cc-ticker-inner span{margin-right:32px}
.cc-ticker-inner .cc-t-val{color:var(--cc-mb);font-weight:500}
@keyframes ccTick{from{transform:translateX(0)}to{transform:translateX(-50%)}}
/* Main */
.cc-main{position:relative;z-index:1;max-width:1440px;margin:0 auto;padding:20px}
/* Section titles */
.cc-sec-title{font-size:.62rem;font-weight:500;letter-spacing:.18em;
  text-transform:uppercase;color:var(--cc-cd);margin-bottom:14px;
  padding-left:2px;display:flex;align-items:center;gap:8px}
.cc-sec-title::before{content:'';width:3px;height:12px;background:var(--cc-m);
  border-radius:2px}
/* Agent grid */
.cc-agents{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px}
.cc-card{background:var(--cc-gl);backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px);border:1px solid var(--cc-b);
  border-radius:16px;padding:20px;position:relative;overflow:hidden;
  transition:all .45s var(--ease)}
.cc-card:hover{border-color:rgba(64,101,70,.35);
  box-shadow:0 0 28px rgba(64,101,70,.12);transform:translateY(-2px)}
.cc-card--active{border-color:rgba(64,101,70,.25)}
.cc-card--off{opacity:.5}
.cc-card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.cc-card-name{display:flex;align-items:center;gap:10px}
.cc-card-icon{width:36px;height:36px;border-radius:10px;display:flex;
  align-items:center;justify-content:center;font-size:1.1rem;
  background:rgba(64,101,70,.12);border:1px solid rgba(64,101,70,.15)}
.cc-card h3{font-size:.76rem;font-weight:500;color:var(--cc-c);line-height:1.2}
.cc-card h3 small{display:block;font-size:.56rem;font-weight:400;
  color:var(--cc-cd);margin-top:2px;letter-spacing:.06em}
/* Status dot */
.cc-dot{width:8px;height:8px;border-radius:50%;position:relative;flex-shrink:0}
.cc-dot--on{background:#4ade80;box-shadow:0 0 8px rgba(74,222,128,.5)}
.cc-dot--on::after{content:'';position:absolute;inset:-4px;border-radius:50%;
  border:1px solid rgba(74,222,128,.25);animation:ccPulse 2s ease-in-out infinite}
.cc-dot--off{background:var(--cc-r);box-shadow:0 0 6px rgba(231,76,60,.4)}
.cc-dot--idle{background:var(--cc-a);box-shadow:0 0 6px rgba(243,156,18,.3)}
@keyframes ccPulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(2);opacity:0}}
/* Card metrics */
.cc-card-metrics{display:flex;flex-direction:column;gap:6px}
.cc-metric{display:flex;justify-content:space-between;align-items:center;
  font-size:.6rem;color:var(--cc-cd)}
.cc-metric-val{color:var(--cc-mb);font-weight:500;font-variant-numeric:tabular-nums}
.cc-card-time{font-size:.54rem;color:var(--cc-cd2);margin-top:10px;
  text-align:right;letter-spacing:.04em}
/* Card glow line */
.cc-card::after{content:'';position:absolute;bottom:0;left:20px;right:20px;
  height:1px;background:linear-gradient(90deg,transparent,var(--cc-mg),transparent);
  opacity:0;transition:opacity .4s}
.cc-card:hover::after{opacity:1}
/* Panels row */
.cc-panels{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:28px}
/* Events */
.cc-events{background:var(--cc-s);border:1px solid var(--cc-b);border-radius:16px;
  padding:16px;max-height:340px;overflow-y:auto;position:relative;
  font-family:var(--cc-mono);font-size:.62rem;scrollbar-width:thin;
  scrollbar-color:rgba(64,101,70,.2) transparent}
.cc-events::-webkit-scrollbar{width:4px}
.cc-events::-webkit-scrollbar-thumb{background:rgba(64,101,70,.3);border-radius:2px}
.cc-events::after{content:'';position:absolute;inset:0;pointer-events:none;
  border-radius:16px;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(64,101,70,.015) 2px,rgba(64,101,70,.015) 4px)}
.cc-ev{display:flex;gap:10px;padding:5px 0;border-bottom:1px solid rgba(64,101,70,.06);
  animation:ccEvIn .3s var(--ease) both}
@keyframes ccEvIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:translateX(0)}}
.cc-ev-time{color:var(--cc-cd2);white-space:nowrap;min-width:52px}
.cc-ev-src{background:rgba(64,101,70,.12);color:var(--cc-mb);padding:1px 6px;
  border-radius:4px;font-size:.54rem;white-space:nowrap}
.cc-ev-msg{color:var(--cc-cd);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cc-ev--error .cc-ev-msg{color:var(--cc-r)}
.cc-ev--success .cc-ev-msg{color:#4ade80}
/* Stats */
.cc-stats{display:flex;flex-direction:column;gap:14px}
.cc-gauge-row{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.cc-gauge{display:flex;flex-direction:column;align-items:center;gap:6px}
.cc-gauge svg{width:90px;height:90px;filter:drop-shadow(0 0 6px var(--cc-mg))}
.cc-gauge-bg{fill:none;stroke:rgba(64,101,70,.12);stroke-width:6}
.cc-gauge-fill{fill:none;stroke:var(--cc-m);stroke-width:6;stroke-linecap:round;
  transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset 1s var(--ease)}
.cc-gauge-text{font-size:.58rem;color:var(--cc-cd);text-anchor:middle;dominant-baseline:central;
  fill:var(--cc-c);font-weight:500;font-family:var(--cc-f)}
.cc-gauge-label{font-size:.54rem;color:var(--cc-cd);letter-spacing:.06em}
/* Stat cards */
.cc-stat-cards{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.cc-stat{background:rgba(64,101,70,.06);border:1px solid var(--cc-b);
  border-radius:10px;padding:12px 14px;text-align:center}
.cc-stat-val{font-size:1.1rem;font-weight:600;color:var(--cc-mb);
  font-variant-numeric:tabular-nums}
.cc-stat-lbl{font-size:.52rem;color:var(--cc-cd);letter-spacing:.08em;
  text-transform:uppercase;margin-top:2px}
/* Skills & actions row */
.cc-bottom{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cc-skills{display:flex;flex-direction:column;gap:8px}
.cc-skill{display:flex;align-items:center;gap:10px;
  background:rgba(64,101,70,.06);border:1px solid var(--cc-b);
  border-radius:10px;padding:10px 14px}
.cc-skill-name{font-size:.68rem;font-weight:500;color:var(--cc-c);flex:1}
.cc-skill-desc{font-size:.52rem;color:var(--cc-cd)}
.cc-skill-badge{font-size:.54rem;background:rgba(64,101,70,.15);
  color:var(--cc-mb);padding:2px 8px;border-radius:6px;white-space:nowrap}
/* Actions */
.cc-actions{display:flex;flex-direction:column;gap:8px}
.cc-act{background:rgba(64,101,70,.08);border:1px solid rgba(64,101,70,.18);
  border-radius:10px;padding:12px 16px;color:var(--cc-c);font-size:.68rem;
  font-weight:500;font-family:var(--cc-f);cursor:pointer;letter-spacing:.04em;
  text-align:left;transition:all .35s var(--ease);display:flex;
  align-items:center;gap:10px}
.cc-act:hover{background:rgba(64,101,70,.18);border-color:rgba(64,101,70,.35);
  box-shadow:0 0 18px rgba(64,101,70,.12)}
.cc-act-icon{font-size:.9rem}
.cc-act small{font-size:.52rem;color:var(--cc-cd);margin-left:auto}
/* Offline banner */
.cc-offline{background:rgba(231,76,60,.08);border:1px solid rgba(231,76,60,.2);
  border-radius:10px;padding:10px 16px;text-align:center;font-size:.66rem;
  color:var(--cc-r);margin-bottom:16px;display:none;
  animation:ccBlink 2s ease-in-out infinite}
@keyframes ccBlink{0%,100%{opacity:1}50%{opacity:.5}}
/* Responsive */
@media(max-width:1023px){
  .cc-agents{grid-template-columns:repeat(2,1fr)}
  .cc-panels,.cc-bottom{grid-template-columns:1fr}
}
@media(max-width:639px){
  .cc-agents{grid-template-columns:1fr}
  .cc-header{padding:10px 16px;flex-wrap:wrap;gap:8px}
  .cc-hdr-badges{display:none}
  .cc-main{padding:14px}
  .cc-stat-cards{grid-template-columns:1fr 1fr}
  .cc-gauge-row{gap:10px}
  .cc-gauge svg{width:70px;height:70px}
}
"""

_JS = """
(function(){
'use strict';
var pw='',PT=8000,timer=null,polling=false,seenEvts=new Set();

function hd(){return{'Content-Type':'application/json','X-Admin-Password':pw}}

// Login
var loginEl=document.getElementById('cc-login');
var dashEl=document.getElementById('cc-dash');
var pwIn=document.getElementById('cc-pw');
var errEl=document.getElementById('cc-err');

function tryLogin(){
  var v=pwIn.value.trim();if(!v)return;
  fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({password:v})})
  .then(function(r){if(!r.ok)throw new Error('bad');return r.json()})
  .then(function(){pw=v;sessionStorage.setItem('cc_pw',v);showDash()})
  .catch(function(){errEl.textContent='Invalid password'});
}
pwIn.addEventListener('keydown',function(e){if(e.key==='Enter')tryLogin()});
document.getElementById('cc-login-btn').addEventListener('click',tryLogin);

var saved=sessionStorage.getItem('cc_pw');
if(saved){pw=saved;showDash()}

function showDash(){loginEl.style.display='none';dashEl.style.display='block';startPoll()}
function doLogout(){sessionStorage.removeItem('cc_pw');location.reload()}
document.getElementById('cc-logout').addEventListener('click',doLogout);

// Polling
function F(u){return fetch(u,{headers:hd()}).then(function(r){return r.json()}).catch(function(){return{error:'fetch failed'}})}

function startPoll(){pollAll();timer=setInterval(pollAll,PT);loadSkills()}
function pollAll(){
  if(polling)return;polling=true;
  Promise.all([F('/api/openfang/status'),F('/api/openfang/agents'),
    F('/api/openfang/events?limit=40'),F('/api/openfang/budget')])
  .then(function(d){
    var offline=!!d[0].error;
    document.getElementById('cc-offline-bar').style.display=offline?'block':'none';
    if(!offline){renderHeader(d[0]);renderAgents(d[1]);renderEvents(d[2]);renderBudget(d[3])}
    else{renderOffline()}
  }).finally(function(){polling=false});
}

// Header
function renderHeader(s){
  document.getElementById('hdr-agents').textContent=s.agent_count||0;
  document.getElementById('hdr-model').textContent=(s.default_model||'unknown').split('/').pop();
  document.getElementById('hdr-version').textContent='v'+(s.version||'?');
  var up=s.uptime_seconds||0;
  var h=Math.floor(up/3600),m=Math.floor((up%3600)/60);
  document.getElementById('hdr-uptime').textContent=h+'h '+m+'m';
  var b=document.getElementById('hdr-status-badge');
  b.className='cc-badge cc-badge--live';b.querySelector('span').textContent='ONLINE';
}

// Agents
var HAND_META={lead:{icon:'&#x1F4CA;',ja:'\\u30EA\\u30FC\\u30C9\\u751F\\u6210'},
  collector:{icon:'&#x1F50D;',ja:'\\u5E02\\u5834\\u8ABF\\u67FB'},
  predictor:{icon:'&#x1F52E;',ja:'\\u9700\\u8981\\u4E88\\u6E2C'},
  researcher:{icon:'&#x1F9EA;',ja:'\\u7814\\u7A76\\u5206\\u6790'},
  twitter:{icon:'&#x1D54F;',ja:'\\u6A29\\u5A01\\u69CB\\u7BC9'},
  browser:{icon:'&#x1F310;',ja:'\\u30A6\\u30A7\\u30D6\\u81EA\\u52D5\\u5316'}};

function renderAgents(agents){
  if(!Array.isArray(agents))return;
  var el=document.getElementById('agent-grid');
  var html='';
  agents.forEach(function(a){
    var hand=a.name.replace('-hand','');
    var meta=HAND_META[hand]||{icon:'&#x2699;',ja:hand};
    var isOn=a.state==='Running';
    var dotCls=isOn?'cc-dot--on':'cc-dot--off';
    var cardCls=isOn?'cc-card cc-card--active':'cc-card cc-card--off';
    html+='<div class="'+cardCls+'">'
      +'<div class="cc-card-top">'
      +'<div class="cc-card-name">'
      +'<div class="cc-card-icon">'+meta.icon+'</div>'
      +'<h3>'+capitalize(hand)+' Hand<small>'+meta.ja+'</small></h3>'
      +'</div>'
      +'<div class="cc-dot '+dotCls+'"></div>'
      +'</div>'
      +'<div class="cc-card-metrics">'
      +'<div class="cc-metric"><span>Status</span><span class="cc-metric-val">'+(isOn?'Active':'Stopped')+'</span></div>'
      +'<div class="cc-metric"><span>Model</span><span class="cc-metric-val">'+(a.model||'default').split('/').pop()+'</span></div>'
      +'</div>'
      +'<div class="cc-card-time">'+relTime(a.last_activity||a.created_at)+'</div>'
      +'</div>';
  });
  el.innerHTML=html;
}

// Events
function renderEvents(data){
  var events=Array.isArray(data)?data:(data.events||[]);
  var el=document.getElementById('event-log');
  var newHtml='';
  events.forEach(function(ev){
    if(seenEvts.has(ev.id))return;
    seenEvts.add(ev.id);
    var cls='cc-ev';
    if(ev.detail&&ev.detail.match(/error|fail/i))cls+=' cc-ev--error';
    else if(ev.detail&&ev.detail.match(/success|complete/i))cls+=' cc-ev--success';
    var src=ev.source_agent_name||ev.source||'system';
    var time=formatTime(ev.timestamp);
    newHtml+='<div class="'+cls+'">'
      +'<span class="cc-ev-time">'+time+'</span>'
      +'<span class="cc-ev-src">'+src+'</span>'
      +'<span class="cc-ev-msg">'+(ev.detail||ev.kind||'')+'</span>'
      +'</div>';
  });
  if(newHtml)el.innerHTML=newHtml+el.innerHTML;
  // trim
  while(el.children.length>60)el.removeChild(el.lastChild);
}

// Budget
function renderBudget(b){
  if(b.error)return;
  var ds=b.daily_spend_usd||b.today_cost_usd||0;
  var dl=b.daily_limit_usd||1;
  var pct=Math.min(ds/dl*100,100);
  setGauge('gauge-spend',pct);
  document.getElementById('stat-spend').textContent='$'+ds.toFixed(3);
}

function setGauge(id,pct){
  var c=document.getElementById(id);if(!c)return;
  var r=38,circ=2*Math.PI*r;
  c.style.strokeDasharray=circ;
  c.style.strokeDashoffset=circ*(1-pct/100);
}

// Skills (once)
function loadSkills(){
  F('/api/openfang/skills').then(function(data){
    var skills=Array.isArray(data)?data:(data.skills||[]);
    var el=document.getElementById('skills-list');
    if(!skills.length){el.innerHTML='<div class="cc-skill"><span class="cc-skill-name" style="color:var(--cc-cd)">No skills installed</span></div>';return}
    var html='';
    skills.forEach(function(s){
      var tc=0;if(s.tools&&s.tools.provided)tc=s.tools.provided.length;
      else if(s.tools_count)tc=s.tools_count;
      html+='<div class="cc-skill">'
        +'<span class="cc-skill-name">'+s.name+'</span>'
        +'<span class="cc-skill-badge">'+tc+' tools</span>'
        +'</div>';
    });
    el.innerHTML=html;
  });
}

// Offline
function renderOffline(){
  var b=document.getElementById('hdr-status-badge');
  b.className='cc-badge cc-badge--off';b.querySelector('span').textContent='OFFLINE';
}

// Helpers
function capitalize(s){return s.charAt(0).toUpperCase()+s.slice(1)}
function relTime(iso){
  if(!iso)return'---';
  var ms=Date.now()-new Date(iso).getTime();
  var s=Math.floor(ms/1000);if(s<60)return s+'s ago';
  var m=Math.floor(s/60);if(m<60)return m+'m ago';
  var h=Math.floor(m/60);if(h<24)return h+'h ago';
  return Math.floor(h/24)+'d ago';
}
function formatTime(iso){
  if(!iso)return'--:--';
  var d=new Date(iso);
  return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0')+':'+String(d.getSeconds()).padStart(2,'0');
}
})();
"""


_HTML = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>NAKAI Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{_CSS}</style>
</head>
<body>
<div class="cc-bg"></div>

<!-- Login Gate -->
<div id="cc-login" class="cc-login">
  <div class="cc-login-box">
    <h1>NAKAI &times; OpenFang</h1>
    <p>指令センター &mdash; Command Center</p>
    <input id="cc-pw" type="password" placeholder="Admin password" autocomplete="off">
    <button id="cc-login-btn">ACCESS</button>
    <div id="cc-err" class="cc-login-err"></div>
  </div>
</div>

<!-- Dashboard -->
<div id="cc-dash" style="display:none">

<!-- Header -->
<header class="cc-header">
  <div class="cc-hdr-left">
    <div class="cc-hdr-logo">NAKAI <span>&times; OpenFang</span></div>
    <div class="cc-hdr-sub">指令センター</div>
  </div>
  <div class="cc-hdr-badges">
    <div id="hdr-status-badge" class="cc-badge cc-badge--live">
      <div class="cc-dot cc-dot--on" style="width:6px;height:6px"></div>
      <span>ONLINE</span>
    </div>
    <div class="cc-badge">UPTIME <span id="hdr-uptime" class="cc-t-val">--</span></div>
    <div class="cc-badge">AGENTS <span id="hdr-agents" class="cc-t-val">0</span></div>
    <div class="cc-badge">MODEL <span id="hdr-model" class="cc-t-val">--</span></div>
    <div class="cc-badge"><span id="hdr-version">v--</span></div>
  </div>
  <button id="cc-logout" class="cc-hdr-logout">LOGOUT</button>
</header>

<!-- Ticker -->
<div class="cc-ticker">
  <div class="cc-ticker-inner" id="ticker">
    <span>NAKAI MATCHA</span>
    <span>Kagoshima, Japan</span>
    <span>6 Autonomous Agents</span>
    <span>JAS Organic + USDA Organic</span>
    <span>Lead Generation &bull; Market Intelligence &bull; Demand Forecast &bull; Authority Building</span>
    <span>Powered by Claude (Anthropic)</span>
    <span>NAKAI MATCHA</span>
    <span>Kagoshima, Japan</span>
    <span>6 Autonomous Agents</span>
    <span>JAS Organic + USDA Organic</span>
    <span>Lead Generation &bull; Market Intelligence &bull; Demand Forecast &bull; Authority Building</span>
    <span>Powered by Claude (Anthropic)</span>
  </div>
</div>

<main class="cc-main">

<!-- Offline banner -->
<div id="cc-offline-bar" class="cc-offline">
  OpenFang connection lost &mdash; retrying every 8 seconds...
</div>

<!-- Agent Grid -->
<div class="cc-sec-title">ACTIVE AGENTS</div>
<div class="cc-agents" id="agent-grid">
  <div class="cc-card"><div class="cc-card-metrics" style="text-align:center;padding:30px 0;color:var(--cc-cd);font-size:.66rem">Loading agents...</div></div>
</div>

<!-- Panels: Events + Stats -->
<div class="cc-panels">
  <div>
    <div class="cc-sec-title">EVENT TIMELINE</div>
    <div class="cc-events" id="event-log">
      <div class="cc-ev"><span class="cc-ev-time">--:--</span><span class="cc-ev-src">system</span><span class="cc-ev-msg">Waiting for events...</span></div>
    </div>
  </div>
  <div>
    <div class="cc-sec-title">SYSTEM STATS</div>
    <div class="cc-stats">
      <div class="cc-gauge-row">
        <div class="cc-gauge">
          <svg viewBox="0 0 80 80">
            <circle class="cc-gauge-bg" cx="40" cy="40" r="38"/>
            <circle id="gauge-spend" class="cc-gauge-fill" cx="40" cy="40" r="38"
              stroke-dasharray="238.76" stroke-dashoffset="238.76"/>
            <text class="cc-gauge-text" x="40" y="38" font-size="10" id="stat-spend">$0</text>
            <text class="cc-gauge-text" x="40" y="50" font-size="7" fill="rgba(249,240,226,.4)">today</text>
          </svg>
          <div class="cc-gauge-label">API SPEND</div>
        </div>
        <div class="cc-gauge">
          <svg viewBox="0 0 80 80">
            <circle class="cc-gauge-bg" cx="40" cy="40" r="38"/>
            <circle id="gauge-agents" class="cc-gauge-fill" cx="40" cy="40" r="38"
              stroke-dasharray="238.76" stroke-dashoffset="0"/>
            <text class="cc-gauge-text" x="40" y="40" font-size="16" id="stat-agents-num">6</text>
          </svg>
          <div class="cc-gauge-label">AGENTS</div>
        </div>
      </div>
      <div class="cc-stat-cards">
        <div class="cc-stat"><div class="cc-stat-val" id="stat-models">--</div><div class="cc-stat-lbl">Models</div></div>
        <div class="cc-stat"><div class="cc-stat-val" id="stat-skills">3</div><div class="cc-stat-lbl">Skills</div></div>
        <div class="cc-stat"><div class="cc-stat-val" id="stat-tools">10</div><div class="cc-stat-lbl">Tools</div></div>
        <div class="cc-stat"><div class="cc-stat-val" id="stat-events">0</div><div class="cc-stat-lbl">Events</div></div>
      </div>
    </div>
  </div>
</div>

<!-- Bottom: Skills + Actions -->
<div class="cc-bottom">
  <div>
    <div class="cc-sec-title">INSTALLED SKILLS</div>
    <div class="cc-skills" id="skills-list">
      <div class="cc-skill"><span class="cc-skill-name" style="color:var(--cc-cd)">Loading...</span></div>
    </div>
  </div>
  <div>
    <div class="cc-sec-title">QUICK ACTIONS</div>
    <div class="cc-actions">
      <button class="cc-act" onclick="alert('Lead scan triggered (demo)')">
        <span class="cc-act-icon">&#x1F4CA;</span>Run Lead Scan<small>Lead Hand</small>
      </button>
      <button class="cc-act" onclick="alert('Research report triggered (demo)')">
        <span class="cc-act-icon">&#x1F9EA;</span>Generate Research Report<small>Researcher</small>
      </button>
      <button class="cc-act" onclick="alert('Competitor check triggered (demo)')">
        <span class="cc-act-icon">&#x1F50D;</span>Check Competitors<small>Collector</small>
      </button>
      <button class="cc-act" onclick="alert('Feed refresh triggered (demo)')">
        <span class="cc-act-icon">&#x1F310;</span>Refresh Feeds<small>Browser</small>
      </button>
    </div>
  </div>
</div>

</main>
</div>

<script>{_JS}</script>
</body>
</html>"""


@command_center_router.get("/command-center", response_class=HTMLResponse)
async def serve_command_center():
    return HTMLResponse(
        content=_HTML,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )
