"""NAKAI Matcha Concierge — Standalone PWA Application.

Endpoints:
  GET /app           → Full HTML/CSS/JS PWA application
  GET /manifest.json → PWA manifest
  GET /sw.js         → Service worker
  GET /icon-192.png  → App icon
  GET /icon-512.png  → App icon
"""

import base64
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

pwa_router = APIRouter()

# Load logo assets at module import time
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_ICON_BYTES = (_REPO_ROOT / "logo-green-icon.png").read_bytes()
_LOGO_WHITE_B64 = base64.b64encode(
    (_REPO_ROOT / "nakai-logo-white.png").read_bytes()
).decode()
_ICON_B64 = base64.b64encode(_ICON_BYTES).decode()

# ---- PWA Manifest ----
MANIFEST_JSON = """{
  "name": "NAKAI Matcha Concierge",
  "short_name": "NAKAI",
  "description": "Your personal AI matcha expert",
  "start_url": "/app",
  "display": "standalone",
  "background_color": "#1A1F1A",
  "theme_color": "#3D6142",
  "orientation": "portrait",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ],
  "categories": ["food", "lifestyle"]
}"""

# ---- Service Worker ----
SW_JS = """
var CACHE='nakai-v1';
var SHELL=['/app'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(SHELL)}));
  self.skipWaiting();
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k!==CACHE}).map(function(k){return caches.delete(k)}));
  }));
  self.clients.claim();
});
self.addEventListener('fetch',function(e){
  var u=new URL(e.request.url);
  if(u.pathname.startsWith('/api/')){
    e.respondWith(fetch(e.request).catch(function(){
      return new Response(JSON.stringify({response:'You appear to be offline.',sources:[]}),
        {headers:{'Content-Type':'application/json'}});
    }));
    return;
  }
  e.respondWith(caches.match(e.request).then(function(r){
    return r||fetch(e.request).then(function(resp){
      var cl=resp.clone();
      caches.open(CACHE).then(function(c){c.put(e.request,cl)});
      return resp;
    });
  }));
});
"""

# ---- Main App HTML ----
APP_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#1A1F1A">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NAKAI">
<meta name="description" content="NAKAI Matcha Concierge — Your personal AI matcha expert">
<title>NAKAI Matcha Concierge</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/png" href="/icon-192.png">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg-deep:#1A1F1A;
  --bg-panel:#1E241E;
  --bg-surface:#232A23;
  --bg-elevated:#2A322A;
  --matcha:#7BA06D;
  --matcha-vivid:#8FB87C;
  --matcha-deep:#3D6142;
  --matcha-muted:rgba(123,160,109,.12);
  --sand:#C4AE96;
  --stone:#9E8471;
  --cream:#E8D9C5;
  --warm-white:#F5EDE1;
  --text-1:#E8E5DF;
  --text-2:#9A958C;
  --text-3:#635E56;
  --border:rgba(255,255,255,.06);
  --border-accent:rgba(123,160,109,.18);
  --ease:cubic-bezier(.22,1,.36,1);
  --ease-spring:cubic-bezier(.34,1.4,.64,1);
  --ease-out:cubic-bezier(.16,1,.3,1);
}}
html,body{{height:100%;overflow:hidden;background:var(--bg-deep);color:var(--text-1);font-family:'Work Sans',sans-serif}}

/* ===== App Shell ===== */
#nc-app{{display:flex;height:100vh;height:100dvh}}

/* ===== Brand Panel (desktop) ===== */
.nc-brand{{
  width:400px;flex-shrink:0;
  background:var(--bg-deep);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:60px 48px;
  border-right:1px solid var(--border);
  position:relative;overflow:hidden;
}}
.nc-brand::before{{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:radial-gradient(ellipse at 50% 80%,rgba(123,160,109,.04) 0%,transparent 70%);
  pointer-events:none;
}}
.nc-brand__logo{{
  width:160px;height:auto;opacity:.85;
  margin-bottom:48px;
  animation:ncFadeUp .8s var(--ease-out) both;
}}
.nc-brand__tagline{{
  font-weight:200;font-size:1.5rem;letter-spacing:.02em;
  line-height:1.6;text-align:center;
  color:var(--text-1);opacity:.7;
  margin-bottom:16px;
  animation:ncFadeUp .8s .15s var(--ease-out) both;
}}
.nc-brand__sub{{
  font-weight:300;font-size:.8rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--text-3);
  animation:ncFadeUp .8s .3s var(--ease-out) both;
}}
.nc-brand__line{{
  width:1px;height:48px;background:var(--border);
  margin:40px 0;
  animation:ncFadeUp .8s .45s var(--ease-out) both;
}}
.nc-brand__detail{{
  font-weight:300;font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;
  color:var(--text-3);opacity:.5;text-align:center;line-height:1.8;
  animation:ncFadeUp .8s .6s var(--ease-out) both;
}}
@keyframes ncFadeUp{{
  from{{opacity:0;transform:translateY(12px)}}
  to{{opacity:1;transform:translateY(0)}}
}}

/* ===== Chat Panel ===== */
.nc-chat{{
  flex:1;display:flex;flex-direction:column;
  background:var(--bg-panel);min-width:0;
}}

/* Header */
.nc-header{{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 24px;
  border-bottom:1px solid var(--border);
  flex-shrink:0;
}}
.nc-header__left{{display:flex;align-items:center;gap:12px}}
.nc-header__logo-m{{height:20px;width:auto;opacity:.7;display:none}}
.nc-header__title{{
  font-weight:300;font-size:.85rem;letter-spacing:.15em;text-transform:uppercase;
  color:var(--text-2);
}}
.nc-header__ai{{
  display:inline-flex;align-items:center;gap:3px;
  background:var(--matcha-muted);
  border:1px solid var(--border-accent);
  border-radius:999px;padding:2px 8px 2px 6px;
  font-size:.7rem;font-weight:400;letter-spacing:.08em;
  color:var(--matcha);
}}
.nc-header__ai svg{{width:8px;height:8px;opacity:.7}}
.nc-header__right{{display:flex;align-items:center;gap:12px}}
.nc-header__status{{
  display:flex;align-items:center;gap:5px;
  font-weight:300;font-size:.7rem;letter-spacing:.06em;color:var(--text-3);
}}
.nc-header__dot{{
  width:5px;height:5px;border-radius:50%;background:#7ED67E;
  box-shadow:0 0 6px rgba(126,214,126,.4);
  animation:ncPulse 3s ease-in-out infinite;
}}
@keyframes ncPulse{{
  0%,100%{{opacity:1;box-shadow:0 0 6px rgba(126,214,126,.4)}}
  50%{{opacity:.5;box-shadow:0 0 12px rgba(126,214,126,.15)}}
}}
.nc-lang{{
  background:none;border:1px solid var(--border);border-radius:999px;
  padding:4px 10px;color:var(--text-2);font-family:inherit;
  font-size:.7rem;font-weight:400;letter-spacing:.1em;
  cursor:pointer;transition:all .3s var(--ease);
}}
.nc-lang:hover{{border-color:var(--border-accent);color:var(--matcha)}}

/* Messages */
.nc-messages{{
  flex:1;overflow-y:auto;padding:28px 28px 16px;
  display:flex;flex-direction:column;gap:4px;
  scroll-behavior:smooth;
}}
.nc-messages::-webkit-scrollbar{{width:0}}

/* AI Banner */
.nc-banner{{
  display:flex;align-items:center;justify-content:center;gap:6px;
  padding:8px 14px;margin:0 0 20px;
  background:rgba(123,160,109,.04);
  border:1px solid var(--border-accent);
  border-radius:10px;
  font-size:.75rem;font-weight:300;color:var(--text-2);
  letter-spacing:.02em;
}}
.nc-banner svg{{width:12px;height:12px;color:var(--matcha);opacity:.5}}

/* Message shared */
.nc-msg{{display:flex;flex-direction:column;animation:ncMsgIn .35s var(--ease-out) both}}
@keyframes ncMsgIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Bot message */
.nc-msg--bot{{align-items:flex-start;padding-right:60px}}
.nc-msg--bot .nc-msg__row{{display:flex;align-items:flex-start;gap:12px}}
.nc-msg__avatar{{
  width:28px;height:28px;border-radius:8px;flex-shrink:0;margin-top:2px;
  background:rgba(123,160,109,.06);border:1px solid var(--border-accent);
  display:flex;align-items:center;justify-content:center;
}}
.nc-msg__avatar svg{{width:12px;height:12px;color:var(--matcha);opacity:.6}}
.nc-msg--bot .nc-msg__body{{
  padding:14px 18px;
  border-left:2px solid rgba(123,160,109,.15);
  font-size:.9rem;font-weight:350;line-height:1.75;
  color:var(--text-1);letter-spacing:.008em;
}}
.nc-msg__body a{{
  color:var(--matcha);text-decoration:none;font-weight:400;
  border-bottom:1px solid rgba(123,160,109,.25);
  transition:all .3s var(--ease);
}}
.nc-msg__body a:hover{{border-color:var(--matcha)}}
.nc-msg__body strong{{font-weight:500}}

/* User message */
.nc-msg--user{{align-items:flex-end;padding-left:60px;margin-top:8px}}
.nc-msg--user .nc-msg__body{{
  background:linear-gradient(145deg,var(--matcha-deep),#2E4A33);
  color:rgba(255,255,255,.92);
  border-radius:20px 20px 4px 20px;
  padding:12px 18px;
  font-size:.9rem;font-weight:400;line-height:1.72;
  letter-spacing:.008em;
  box-shadow:0 2px 12px rgba(61,97,66,.15);
}}

/* Message spacing */
.nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:16px}}

/* Meta */
.nc-msg__meta{{
  display:flex;align-items:center;gap:6px;
  margin-top:4px;padding-left:40px;
}}
.nc-msg__time{{font-size:.65rem;font-weight:300;color:var(--text-3);letter-spacing:.06em}}
.nc-msg__tag{{font-size:.6rem;font-weight:400;letter-spacing:.1em;text-transform:uppercase;color:var(--matcha);opacity:.4}}

/* Sources */
.nc-msg__sources{{margin-top:8px;padding-left:40px;display:flex;flex-wrap:wrap;gap:6px}}
.nc-msg__source{{
  font-size:.75rem;color:var(--matcha);text-decoration:none;font-weight:400;
  border-bottom:1px solid rgba(123,160,109,.2);
  opacity:.6;transition:all .3s var(--ease);
}}
.nc-msg__source:hover{{opacity:1}}

/* Typing */
.nc-typing .nc-msg__body{{display:flex;gap:5px;align-items:center;height:12px;padding:14px 18px!important;border-left:2px solid rgba(123,160,109,.15)}}
.nc-typing .nc-msg__body span{{
  width:4px;height:4px;background:var(--matcha);border-radius:50%;
  display:inline-block;animation:ncWave 1.6s ease-in-out infinite;
}}
.nc-typing .nc-msg__body span:nth-child(2){{animation-delay:.15s}}
.nc-typing .nc-msg__body span:nth-child(3){{animation-delay:.3s}}
@keyframes ncWave{{
  0%,60%,100%{{opacity:.12;transform:translateY(0)}}
  30%{{opacity:.7;transform:translateY(-4px)}}
}}
.nc-typing__label{{
  font-size:.7rem;font-weight:300;color:var(--text-3);
  letter-spacing:.04em;padding-left:40px;margin-top:4px;
}}

/* Quick actions */
.nc-quick{{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;padding-left:40px}}
.nc-quick__btn{{
  font-family:inherit;font-size:.78rem;font-weight:400;
  color:var(--matcha);background:transparent;
  border:1px solid var(--border-accent);
  border-radius:999px;padding:7px 16px;cursor:pointer;
  letter-spacing:.02em;transition:all .35s var(--ease);
  touch-action:manipulation;-webkit-tap-highlight-color:transparent;
}}
.nc-quick__btn:hover{{
  background:var(--matcha-deep);color:rgba(255,255,255,.9);
  border-color:var(--matcha-deep);
  transform:translateY(-1px);
  box-shadow:0 4px 12px rgba(61,97,66,.2);
}}

/* Input area */
.nc-input-area{{
  padding:16px 24px 20px;
  border-top:1px solid var(--border);
  flex-shrink:0;
}}
.nc-form{{
  display:flex;align-items:center;gap:8px;
  background:var(--bg-surface);
  border:1px solid var(--border);
  border-radius:999px;
  padding:5px 5px 5px 20px;
  transition:all .4s var(--ease);
}}
.nc-form:focus-within{{
  border-color:var(--border-accent);
  box-shadow:0 0 0 3px rgba(123,160,109,.06);
  background:var(--bg-elevated);
}}
.nc-input{{
  flex:1;border:none;background:transparent;
  color:var(--text-1);font-family:inherit;
  font-size:.88rem;font-weight:350;letter-spacing:.015em;
  outline:none;padding:8px 0;
}}
.nc-input::placeholder{{color:var(--text-3);font-weight:300;letter-spacing:.03em}}
.nc-send{{
  width:36px;height:36px;border-radius:50%;border:none;
  background:linear-gradient(145deg,var(--matcha),var(--matcha-deep));
  color:rgba(255,255,255,.85);cursor:pointer;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
  transition:all .3s var(--ease);
  touch-action:manipulation;-webkit-tap-highlight-color:transparent;
}}
.nc-send:hover{{transform:scale(1.08);box-shadow:0 2px 10px rgba(123,160,109,.25)}}
.nc-send:active{{transform:scale(.92)}}
.nc-send svg{{width:14px;height:14px;margin-left:1px}}

/* Footer */
.nc-footer{{
  display:flex;align-items:center;justify-content:center;gap:5px;
  padding:2px 0 max(12px,env(safe-area-inset-bottom));
}}
.nc-footer svg{{width:8px;height:8px;color:var(--text-3);opacity:.2}}
.nc-footer span{{font-size:.65rem;font-weight:300;color:var(--text-3);letter-spacing:.14em;text-transform:uppercase;opacity:.2}}

/* ===== Responsive ===== */
@media(max-width:1199px){{
  .nc-brand{{width:340px;padding:48px 36px}}
  .nc-brand__logo{{width:140px;margin-bottom:40px}}
  .nc-brand__tagline{{font-size:1.35rem}}
}}
@media(max-width:899px){{
  .nc-brand{{display:none}}
  .nc-header__logo-m{{display:block}}
  .nc-messages{{padding:20px 16px 12px}}
  .nc-msg--bot{{padding-right:32px}}
  .nc-msg--user{{padding-left:32px}}
  .nc-msg--bot .nc-msg__body,.nc-msg--user .nc-msg__body{{font-size:.88rem;padding:11px 15px}}
  .nc-banner{{font-size:.72rem;padding:6px 10px;margin-bottom:14px}}
  .nc-quick{{padding-left:40px;gap:5px}}
  .nc-quick__btn{{font-size:.75rem;padding:6px 13px}}
  .nc-input-area{{padding:12px 16px 16px}}
  .nc-input{{font-size:16px}}
  .nc-header{{padding:14px 16px}}
  .nc-footer{{padding:2px 0 max(10px,env(safe-area-inset-bottom))}}
}}
</style>
</head>
<body>
<div id="nc-app">
  <!-- Brand Panel (desktop) -->
  <aside class="nc-brand">
    <img class="nc-brand__logo" src="data:image/png;base64,{_LOGO_WHITE_B64}" alt="NAKAI" />
    <p class="nc-brand__tagline">Grounded in nature,<br>elevated in ritual.</p>
    <p class="nc-brand__sub">AI Matcha Concierge</p>
    <div class="nc-brand__line"></div>
    <p class="nc-brand__detail">Organic Matcha<br>Uji, Kyoto</p>
  </aside>

  <!-- Chat Panel -->
  <main class="nc-chat">
    <header class="nc-header">
      <div class="nc-header__left">
        <img class="nc-header__logo-m" src="data:image/png;base64,{_LOGO_WHITE_B64}" alt="NAKAI" />
        <span class="nc-header__title" id="nc-title">Concierge</span>
        <span class="nc-header__ai">
          <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>
          AI
        </span>
      </div>
      <div class="nc-header__right">
        <div class="nc-header__status">
          <span class="nc-header__dot"></span>
          <span id="nc-status">Online</span>
        </div>
        <button class="nc-lang" id="nc-lang" aria-label="Toggle language">EN</button>
      </div>
    </header>

    <div class="nc-messages" id="nc-messages">
      <div class="nc-banner">
        <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>
        <span id="nc-banner-text">AI-powered answers based on our matcha expertise</span>
      </div>
      <div class="nc-msg nc-msg--bot" id="nc-welcome">
        <div class="nc-msg__row">
          <div class="nc-msg__avatar"><svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg></div>
          <div class="nc-msg__body" id="nc-greeting"></div>
        </div>
        <div class="nc-quick" id="nc-quick"></div>
      </div>
    </div>

    <div class="nc-input-area">
      <form class="nc-form" id="nc-form">
        <input type="text" class="nc-input" id="nc-input" autocomplete="off" maxlength="500" />
        <button type="submit" class="nc-send" aria-label="Send">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
        </button>
      </form>
    </div>
    <div class="nc-footer">
      <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>
      <span>AI by NAKAI</span>
    </div>
  </main>
</div>

<script>
(function(){{
  'use strict';
  var STAR='<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>';
  var MAX_H=20;
  var history=[];
  var loading=false;

  // i18n
  var i18n={{
    en:{{
      greeting:"Welcome. I'm your AI Matcha Concierge — here to guide you through brewing, health benefits, product selection, and the art of Japanese tea. Ask me anything.",
      placeholder:'Ask about matcha...',
      typing:'Composing...',
      banner:'AI-powered answers based on our matcha expertise',
      online:'Online',
      q1:'How to brew the perfect matcha',q1m:'How do I brew the perfect cup of matcha?',
      q2:'Matcha health benefits',q2m:'What are the health benefits of matcha?',
      q3:'Matcha vs coffee',q3m:'How does matcha compare to coffee?',
      q4:'Product recommendations',q4m:'What matcha products do you recommend?',
      error:"I'm having a brief connection issue. Please try again in a moment.",
      offline:'Offline',
    }},
    ja:{{
      greeting:'ようこそ。AI抹茶コンシェルジュです。点て方、健康効果、商品選び、日本茶の文化まで、抹茶に関するあらゆるご質問にお答えします。お気軽にどうぞ。',
      placeholder:'抹茶について質問する...',
      typing:'回答を作成中...',
      banner:'AI が抹茶の専門知識に基づいて回答します',
      online:'オンライン',
      q1:'美味しい抹茶の点て方',q1m:'美味しい抹茶の点て方を教えてください',
      q2:'抹茶の健康効果',q2m:'抹茶の健康効果について教えてください',
      q3:'抹茶 vs コーヒー',q3m:'抹茶とコーヒーの違いを教えてください',
      q4:'おすすめの商品',q4m:'おすすめの抹茶商品を教えてください',
      error:'接続に問題が発生しました。しばらくしてからもう一度お試しください。',
      offline:'オフライン',
    }}
  }};

  // Language
  var lang=(function(){{
    var s=localStorage.getItem('nakai_lang');
    if(s&&i18n[s])return s;
    var n=(navigator.language||'en').substring(0,2);
    return i18n[n]?n:'en';
  }})();

  function t(k){{return(i18n[lang]||i18n.en)[k]||i18n.en[k]}}
  function $(id){{return document.getElementById(id)}}

  function setLang(l){{
    lang=l;
    localStorage.setItem('nakai_lang',l);
    document.documentElement.lang=l;
    $('nc-lang').textContent=l.toUpperCase();
    $('nc-input').placeholder=t('placeholder');
    $('nc-banner-text').textContent=t('banner');
    $('nc-status').textContent=t('online');
    $('nc-greeting').innerHTML=t('greeting');
    buildQuickActions();
  }}

  function buildQuickActions(){{
    var qa=$('nc-quick');
    qa.innerHTML='';
    ['q1','q2','q3','q4'].forEach(function(k){{
      var b=document.createElement('button');
      b.className='nc-quick__btn';
      b.setAttribute('data-msg',t(k+'m'));
      b.textContent=t(k);
      b.addEventListener('click',function(){{
        $('nc-input').value=this.getAttribute('data-msg');
        sendMessage();
        qa.style.display='none';
      }});
      qa.appendChild(b);
    }});
  }}

  function escapeHtml(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}
  function formatMd(s){{
    return s
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\[(.*?)\]\((.*?)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\\n/g,'<br>');
  }}
  function scroll(){{var m=$('nc-messages');if(m)m.scrollTop=m.scrollHeight}}

  function addMsg(role,text,sources){{
    sources=sources||[];
    var m=$('nc-messages');if(!m)return;
    var d=document.createElement('div');
    d.className='nc-msg nc-msg--'+role;
    var html='';
    var content=role==='bot'?formatMd(text):escapeHtml(text);
    if(role==='bot'){{
      html+='<div class="nc-msg__row"><div class="nc-msg__avatar">'+STAR+'</div><div class="nc-msg__body">'+content+'</div></div>';
      if(sources.length){{
        html+='<div class="nc-msg__sources">';
        sources.forEach(function(s){{
          var label=s.indexOf('/products/')>-1?(lang==='ja'?'商品を見る':'View product')
            :s.indexOf('/blogs/')>-1?(lang==='ja'?'記事を読む':'Read article')
            :(lang==='ja'?'詳細':'Learn more');
          html+='<a href="'+escapeHtml(s)+'" class="nc-msg__source" target="_blank">'+label+'</a>';
        }});
        html+='</div>';
      }}
      var now=new Date();
      var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="nc-msg__meta"><span class="nc-msg__time">'+ts+'</span><span class="nc-msg__tag">AI</span></div>';
    }}else{{
      html='<div class="nc-msg__body">'+content+'</div>';
    }}
    d.innerHTML=html;
    m.appendChild(d);
    scroll();
  }}

  function showTyping(){{
    var m=$('nc-messages');if(!m)return;
    var d=document.createElement('div');
    d.className='nc-msg nc-msg--bot nc-typing';
    d.innerHTML='<div class="nc-msg__row"><div class="nc-msg__avatar">'+STAR+'</div><div class="nc-msg__body"><span></span><span></span><span></span></div></div><div class="nc-typing__label">'+t('typing')+'</div>';
    m.appendChild(d);
    scroll();
  }}

  function removeTyping(){{
    var m=$('nc-messages');if(!m)return;
    var tw=m.querySelector('.nc-typing');
    if(tw)tw.remove();
  }}

  function sendMessage(){{
    var inp=$('nc-input');
    var msg=inp?inp.value.trim():'';
    if(!msg||loading)return;
    inp.value='';
    addMsg('user',msg);
    history.push({{role:'user',content:msg}});
    showTyping();
    loading=true;
    fetch('/api/chat',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{message:msg,history:history.slice(-MAX_H),language:lang}})
    }})
    .then(function(r){{if(!r.ok)throw new Error('err');return r.json()}})
    .then(function(d){{
      removeTyping();
      addMsg('bot',d.response,d.sources||[]);
      history.push({{role:'assistant',content:d.response}});
      saveHistory();
    }})
    .catch(function(){{removeTyping();addMsg('bot',t('error'))}})
    .finally(function(){{loading=false}});
  }}

  function saveHistory(){{try{{localStorage.setItem('nakai_app_history',JSON.stringify(history.slice(-MAX_H)))}}catch(e){{}}}}
  function loadHistory(){{
    try{{
      var s=localStorage.getItem('nakai_app_history');
      if(s){{
        history=JSON.parse(s);
        history.forEach(function(m){{addMsg(m.role==='assistant'?'bot':'user',m.content)}});
      }}
    }}catch(e){{}}
  }}

  function boot(){{
    setLang(lang);
    $('nc-form').addEventListener('submit',function(e){{e.preventDefault();sendMessage()}});
    $('nc-lang').addEventListener('click',function(){{setLang(lang==='en'?'ja':'en')}});
    loadHistory();
    if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js');
    if(window.innerWidth>899)$('nc-input').focus();
  }}

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);
  else boot();
}})();
</script>
</body>
</html>"""


@pwa_router.get("/app")
async def serve_app():
    return HTMLResponse(
        content=APP_HTML,
        headers={"Cache-Control": "public, max-age=300"},
    )


@pwa_router.get("/manifest.json")
async def serve_manifest():
    return Response(
        content=MANIFEST_JSON,
        media_type="application/manifest+json",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@pwa_router.get("/sw.js")
async def serve_sw():
    return Response(
        content=SW_JS,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=0"},
    )


@pwa_router.get("/icon-192.png")
async def serve_icon_192():
    return Response(
        content=_ICON_BYTES,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=604800"},
    )


@pwa_router.get("/icon-512.png")
async def serve_icon_512():
    return Response(
        content=_ICON_BYTES,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=604800"},
    )
