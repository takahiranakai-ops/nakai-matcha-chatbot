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
  "background_color": "#000000",
  "theme_color": "#000000",
  "orientation": "portrait",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ],
  "categories": ["food", "lifestyle"]
}"""

# ---- Service Worker ----
SW_JS = """
// v4: Self-unregistering service worker — clears all caches and removes itself
self.addEventListener('install',function(){self.skipWaiting()});
self.addEventListener('activate',function(e){
  e.waitUntil(
    caches.keys().then(function(ks){
      return Promise.all(ks.map(function(k){return caches.delete(k)}));
    }).then(function(){
      return self.registration.unregister();
    })
  );
  self.clients.claim();
});
self.addEventListener('fetch',function(e){
  e.respondWith(fetch(e.request));
});
"""

# ---- Main App HTML ----
APP_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000">
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
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@200;300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

:root{{
  --black:#000;
  --surface:#1C1C1E;
  --surface-glass:rgba(28,28,30,.72);
  --elevated:#2C2C2E;
  --elevated-glass:rgba(44,44,46,.52);
  --fill:#3A3A3C;
  --separator:rgba(84,84,88,.34);
  --separator-light:rgba(84,84,88,.18);
  --matcha:#7BA06D;
  --matcha-dim:rgba(123,160,109,.65);
  --matcha-bg:rgba(123,160,109,.1);
  --matcha-bg2:rgba(123,160,109,.06);
  --matcha-deep:#4A7A3E;
  --text-1:#F5F5F7;
  --text-2:#86868B;
  --text-3:#48484A;
  --ease:cubic-bezier(.25,1,.5,1);
  --ease-spring:cubic-bezier(.34,1.56,.64,1);
  --blur:saturate(180%) blur(20px);
}}

html,body{{
  height:100%;overflow:hidden;
  background:var(--black);color:var(--text-1);
  font-family:'Work Sans',-apple-system,BlinkMacSystemFont,sans-serif;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  font-feature-settings:'cv02','cv03','cv04','cv11';
}}

/* ===== App Shell ===== */
#nc-app{{display:flex;height:100vh;height:100dvh}}

/* ===== Brand Panel ===== */
.nc-brand{{
  width:380px;flex-shrink:0;
  background:var(--black);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:64px 48px;
  border-right:1px solid var(--separator-light);
  position:relative;
}}
.nc-brand__logo{{
  width:140px;height:auto;opacity:.8;
  margin-bottom:56px;
  animation:ncUp .7s var(--ease) both;
}}
.nc-brand__tagline{{
  font-weight:200;font-size:1.4rem;letter-spacing:.01em;
  line-height:1.7;text-align:center;
  color:var(--text-1);opacity:.6;
  margin-bottom:12px;
  animation:ncUp .7s .1s var(--ease) both;
}}
.nc-brand__sub{{
  font-weight:400;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--text-3);
  animation:ncUp .7s .18s var(--ease) both;
}}
.nc-brand__sep{{
  width:32px;height:1px;background:var(--separator-light);
  margin:40px 0;
  animation:ncUp .7s .25s var(--ease) both;
}}
.nc-brand__powered{{
  font-weight:300;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--text-3);opacity:.5;margin-bottom:36px;text-align:center;
  animation:ncUp .7s .32s var(--ease) both;
}}
.nc-brand__ctas{{
  display:flex;flex-direction:column;gap:10px;width:100%;max-width:220px;
  animation:ncUp .7s .38s var(--ease) both;
}}
.nc-cta{{
  display:flex;align-items:center;justify-content:center;
  font-family:inherit;font-size:.78rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;
  text-decoration:none;
  padding:13px 24px;border-radius:12px;
  cursor:pointer;transition:all .3s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-cta--primary{{
  background:var(--matcha);color:#fff;border:none;
}}
.nc-cta--primary:hover{{
  background:#8BB47C;transform:scale(1.02);
  box-shadow:0 4px 20px rgba(123,160,109,.2);
}}
.nc-cta--secondary{{
  background:transparent;color:var(--text-2);border:1px solid var(--separator);
}}
.nc-cta--secondary:hover{{
  background:var(--elevated);color:var(--text-1);border-color:var(--fill);
}}

/* ===== Chat Panel ===== */
.nc-chat{{
  flex:1;display:flex;flex-direction:column;
  background:var(--black);min-width:0;
}}

/* ===== Header ===== */
.nc-header{{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 24px;
  background:var(--surface-glass);
  -webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border-bottom:1px solid var(--separator-light);
  flex-shrink:0;z-index:10;
}}
.nc-header__left{{display:flex;align-items:center;gap:12px}}
.nc-header__logo-m{{height:18px;width:auto;opacity:.7;display:none}}
.nc-header__title{{
  font-weight:500;font-size:.82rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--text-2);
}}
.nc-header__badge{{
  display:inline-flex;align-items:center;gap:4px;
  background:var(--matcha-bg);
  border-radius:100px;padding:3px 10px 3px 7px;
  font-size:.65rem;font-weight:500;letter-spacing:.06em;
  color:var(--matcha);
}}
.nc-header__badge-dot{{
  width:5px;height:5px;border-radius:50%;
  background:var(--matcha);
  animation:ncPulse 3s ease-in-out infinite;
}}
@keyframes ncPulse{{
  0%,100%{{opacity:1}}50%{{opacity:.35}}
}}
.nc-header__right{{display:flex;align-items:center;gap:10px}}
.nc-lang{{
  background:var(--elevated);border:none;border-radius:8px;
  padding:6px 12px;color:var(--text-2);font-family:inherit;
  font-size:.7rem;font-weight:500;letter-spacing:.1em;
  cursor:pointer;transition:all .25s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-lang:hover{{background:var(--fill);color:var(--text-1)}}

/* ===== Messages ===== */
.nc-messages{{
  flex:1;overflow-y:auto;padding:24px 24px 16px;
  display:flex;flex-direction:column;gap:2px;
  scroll-behavior:smooth;
}}
.nc-messages::-webkit-scrollbar{{width:0;display:none}}

/* Banner */
.nc-banner{{
  display:flex;align-items:center;justify-content:center;gap:8px;
  padding:10px 16px;margin:0 auto 20px;
  background:var(--matcha-bg2);
  border-radius:12px;
  font-size:.72rem;font-weight:400;color:var(--text-2);
  letter-spacing:.02em;max-width:400px;
}}
.nc-banner__dot{{
  width:4px;height:4px;border-radius:50%;background:var(--matcha-dim);flex-shrink:0;
}}

/* Message base */
.nc-msg{{display:flex;flex-direction:column;animation:ncMsgIn .4s var(--ease) both}}
@keyframes ncMsgIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Bot */
.nc-msg--bot{{align-items:flex-start;padding-right:48px}}
.nc-msg--bot .nc-msg__bubble{{
  background:var(--surface);
  border-radius:20px 20px 20px 6px;
  padding:14px 18px;
  font-size:.9rem;font-weight:350;line-height:1.8;
  color:var(--text-1);letter-spacing:.01em;
}}
.nc-msg__bubble a{{
  color:var(--matcha);text-decoration:none;font-weight:400;
  transition:opacity .2s;
}}
.nc-msg__bubble a:hover{{opacity:.7}}
.nc-msg__bubble strong{{font-weight:500}}
.nc-msg__bubble ul,.nc-msg__bubble ol{{margin:8px 0;padding-left:20px}}
.nc-msg__bubble li{{margin:4px 0}}

/* User */
.nc-msg--user{{align-items:flex-end;padding-left:48px;margin-top:4px}}
.nc-msg--user .nc-msg__bubble{{
  background:var(--matcha);
  color:rgba(255,255,255,.95);
  border-radius:20px 20px 6px 20px;
  padding:12px 18px;
  font-size:.9rem;font-weight:400;line-height:1.72;
  letter-spacing:.01em;
}}

/* Spacing between sender switches */
.nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:12px}}

/* Meta & Sources */
.nc-msg__meta{{
  display:flex;align-items:center;gap:6px;
  margin-top:6px;padding-left:4px;
}}
.nc-msg__time{{font-size:.62rem;font-weight:400;color:var(--text-3);letter-spacing:.04em}}
.nc-msg__sources{{margin-top:8px;padding-left:4px;display:flex;flex-wrap:wrap;gap:6px}}
.nc-msg__source{{
  display:inline-flex;align-items:center;gap:4px;
  font-size:.7rem;color:var(--matcha);text-decoration:none;font-weight:400;
  background:var(--matcha-bg2);border-radius:8px;padding:4px 10px;
  transition:all .25s var(--ease);
}}
.nc-msg__source:hover{{background:var(--matcha-bg)}}

/* Typing */
.nc-typing .nc-msg__bubble{{
  display:flex;gap:5px;align-items:center;
  padding:16px 20px!important;min-height:44px;
}}
.nc-typing .nc-msg__bubble span{{
  width:5px;height:5px;background:var(--text-3);border-radius:50%;
  display:inline-block;animation:ncWave 1.4s ease-in-out infinite;
}}
.nc-typing .nc-msg__bubble span:nth-child(2){{animation-delay:.15s}}
.nc-typing .nc-msg__bubble span:nth-child(3){{animation-delay:.3s}}
@keyframes ncWave{{
  0%,60%,100%{{opacity:.15;transform:translateY(0)}}
  30%{{opacity:.6;transform:translateY(-3px)}}
}}
.nc-typing__label{{
  font-size:.65rem;font-weight:400;color:var(--text-3);
  letter-spacing:.03em;padding-left:4px;margin-top:4px;
}}

/* Quick Actions */
.nc-quick{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.nc-quick__btn{{
  font-family:inherit;font-size:.78rem;font-weight:400;
  color:var(--text-1);background:var(--surface);
  border:none;
  border-radius:14px;padding:10px 18px;cursor:pointer;
  letter-spacing:.01em;transition:all .25s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-quick__btn:hover{{
  background:var(--elevated);
  transform:translateY(-1px);
}}
.nc-quick__btn:active{{transform:scale(.97)}}

/* ===== Input Area ===== */
.nc-input-area{{
  padding:12px 24px 16px;
  flex-shrink:0;
}}
.nc-form{{
  display:flex;align-items:center;gap:8px;
  background:var(--surface);
  border:1px solid var(--separator-light);
  border-radius:24px;
  padding:4px 4px 4px 20px;
  transition:all .3s var(--ease);
}}
.nc-form:focus-within{{
  border-color:rgba(123,160,109,.25);
  background:var(--elevated);
}}
.nc-input{{
  flex:1;border:none;background:transparent;
  color:var(--text-1);font-family:inherit;
  font-size:.88rem;font-weight:350;letter-spacing:.01em;
  outline:none;padding:10px 0;
}}
.nc-input::placeholder{{color:var(--text-3);font-weight:300}}
.nc-send{{
  width:36px;height:36px;border-radius:50%;border:none;
  background:var(--matcha);
  color:rgba(255,255,255,.9);cursor:pointer;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
  transition:all .2s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-send:hover{{opacity:.85;transform:scale(1.05)}}
.nc-send:active{{transform:scale(.9)}}
.nc-send svg{{width:14px;height:14px}}

/* ===== Footer ===== */
.nc-footer{{
  display:flex;align-items:center;justify-content:center;gap:16px;
  padding:6px 24px max(10px,env(safe-area-inset-bottom));
  flex-shrink:0;
}}
.nc-footer__link{{
  font-size:.65rem;font-weight:400;letter-spacing:.1em;text-transform:uppercase;
  color:var(--text-3);text-decoration:none;
  transition:color .2s;
}}
.nc-footer__link:hover{{color:var(--text-2)}}
.nc-footer__sep{{
  width:1px;height:10px;background:var(--separator-light);
}}
.nc-footer__powered{{
  font-size:.6rem;font-weight:300;letter-spacing:.12em;text-transform:uppercase;
  color:var(--text-3);opacity:.5;
}}

/* ===== Animations ===== */
@keyframes ncUp{{
  from{{opacity:0;transform:translateY(10px)}}
  to{{opacity:1;transform:translateY(0)}}
}}

/* ===== Responsive ===== */
@media(max-width:1199px){{
  .nc-brand{{width:320px;padding:48px 36px}}
  .nc-brand__logo{{width:120px;margin-bottom:44px}}
  .nc-brand__tagline{{font-size:1.25rem}}
}}
@media(max-width:899px){{
  .nc-brand{{display:none}}
  .nc-header__logo-m{{display:block}}
  .nc-messages{{padding:20px 16px 12px}}
  .nc-msg--bot{{padding-right:24px}}
  .nc-msg--user{{padding-left:24px}}
  .nc-msg--bot .nc-msg__bubble,.nc-msg--user .nc-msg__bubble{{
    font-size:.88rem;padding:12px 16px;
  }}
  .nc-banner{{font-size:.68rem;padding:8px 14px;margin-bottom:16px}}
  .nc-quick{{gap:6px}}
  .nc-quick__btn{{font-size:.75rem;padding:9px 15px;border-radius:12px}}
  .nc-input-area{{padding:10px 16px 12px}}
  .nc-input{{font-size:16px}}
  .nc-header{{padding:12px 16px}}
  .nc-footer{{padding:4px 16px max(8px,env(safe-area-inset-bottom))}}
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
    <div class="nc-brand__sep"></div>
    <p class="nc-brand__powered">Powered by NAKAI</p>
    <div class="nc-brand__ctas">
      <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-cta nc-cta--primary">Shop NAKAI</a>
      <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-cta nc-cta--secondary">Wholesale Inquiry</a>
    </div>
  </aside>

  <!-- Chat Panel -->
  <main class="nc-chat">
    <header class="nc-header">
      <div class="nc-header__left">
        <img class="nc-header__logo-m" src="data:image/png;base64,{_LOGO_WHITE_B64}" alt="NAKAI" />
        <span class="nc-header__title" id="nc-title">Concierge</span>
        <span class="nc-header__badge">
          <span class="nc-header__badge-dot"></span>
          <span id="nc-status">Online</span>
        </span>
      </div>
      <div class="nc-header__right">
        <button class="nc-lang" id="nc-lang" aria-label="Toggle language">EN</button>
      </div>
    </header>

    <div class="nc-messages" id="nc-messages">
      <div class="nc-banner">
        <span class="nc-banner__dot"></span>
        <span id="nc-banner-text">AI-powered answers based on our matcha expertise</span>
      </div>
      <div class="nc-msg nc-msg--bot" id="nc-welcome">
        <div class="nc-msg__bubble" id="nc-greeting"></div>
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
      <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-footer__link" id="nc-footer-shop">Shop NAKAI</a>
      <span class="nc-footer__sep"></span>
      <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-footer__link" id="nc-footer-ws">Wholesale</a>
      <span class="nc-footer__sep"></span>
      <span class="nc-footer__powered">Powered by NAKAI</span>
    </div>
  </main>
</div>

<script>
(function(){{
  'use strict';
  var SHOP='https://nakaimatcha.com';
  var MAX_H=20;
  var history=[];
  var loading=false;

  var i18n={{
    en:{{
      greeting:"Welcome. I'm your AI Matcha Concierge — here to guide you through brewing, health benefits, product selection, and the art of Japanese tea. How can I help you today?",
      placeholder:'Ask about matcha...',
      typing:'Thinking...',
      banner:'AI-powered answers based on our matcha expertise',
      online:'Online',
      q1:'How to brew matcha',q1m:'How do I brew the perfect cup of matcha?',
      q2:'Health benefits',q2m:'What are the health benefits of matcha?',
      q3:'Matcha vs coffee',q3m:'How does matcha compare to coffee?',
      q4:'Recommend a product',q4m:'What matcha products do you recommend?',
      error:"Connection issue. Please try again in a moment.",
      offline:'Offline',
      shop:'Shop NAKAI',
      wholesale:'Wholesale',
    }},
    ja:{{
      greeting:'ようこそ。AI抹茶コンシェルジュです。点て方、健康効果、商品選びなど、抹茶に関するあらゆるご質問にお答えします。お気軽にどうぞ。',
      placeholder:'抹茶について質問する...',
      typing:'考え中...',
      banner:'AIが抹茶の専門知識に基づいて回答します',
      online:'オンライン',
      q1:'美味しい抹茶の点て方',q1m:'美味しい抹茶の点て方を教えてください',
      q2:'抹茶の健康効果',q2m:'抹茶の健康効果について教えてください',
      q3:'抹茶 vs コーヒー',q3m:'抹茶とコーヒーの違いを教えてください',
      q4:'おすすめ商品',q4m:'おすすめの抹茶商品を教えてください',
      error:'接続に問題が発生しました。もう一度お試しください。',
      offline:'オフライン',
      shop:'ショップ',
      wholesale:'卸売',
    }}
  }};

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
    $('nc-footer-shop').textContent=t('shop');
    $('nc-footer-ws').textContent=t('wholesale');
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
    if(!s)return'';
    return s
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\[(.*?)\]\(\/(.*?)\)/g,'<a href="'+SHOP+'/$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\[(.*?)\]\((https?:\/\/[^\)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/^- (.*?)$/gm,'<li>$1</li>')
      .replace(/((?:<li>.*?<\/li>\s*)+)/g,'<ul>$1</ul>')
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
      html+='<div class="nc-msg__bubble">'+content+'</div>';
      if(sources.length){{
        html+='<div class="nc-msg__sources">';
        sources.forEach(function(s){{
          var url=s.startsWith('/')?SHOP+s:s;
          var label=s.indexOf('/products/')>-1?(lang==='ja'?'商品を見る':'View product')
            :s.indexOf('/blogs/')>-1?(lang==='ja'?'記事を読む':'Read article')
            :(lang==='ja'?'詳細':'Learn more');
          html+='<a href="'+escapeHtml(url)+'" class="nc-msg__source" target="_blank" rel="noopener">'+label+'</a>';
        }});
        html+='</div>';
      }}
      var now=new Date();
      var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="nc-msg__meta"><span class="nc-msg__time">'+ts+'</span></div>';
    }}else{{
      html='<div class="nc-msg__bubble">'+content+'</div>';
    }}
    d.innerHTML=html;
    m.appendChild(d);
    scroll();
  }}

  function showTyping(){{
    var m=$('nc-messages');if(!m)return;
    var d=document.createElement('div');
    d.className='nc-msg nc-msg--bot nc-typing';
    d.innerHTML='<div class="nc-msg__bubble"><span></span><span></span><span></span></div><div class="nc-typing__label">'+t('typing')+'</div>';
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
    if('serviceWorker' in navigator){{
      navigator.serviceWorker.getRegistrations().then(function(regs){{
        regs.forEach(function(r){{r.unregister()}});
      }});
      caches.keys().then(function(ks){{ks.forEach(function(k){{caches.delete(k)}}) }});
    }}
    if(window.innerWidth>899)$('nc-input').focus();
  }}

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);
  else boot();
}})();
</script>
</body>
</html>"""


@pwa_router.get("/test")
async def serve_test():
    """Minimal debug chat page — no service worker, no cache."""
    test_html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAKAI Chat Test</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;background:#000;color:#f5f5f7;height:100vh;display:flex;flex-direction:column}
#log{flex:1;overflow-y:auto;padding:16px;font-size:14px;line-height:1.8}
.msg{margin:8px 0;padding:10px 14px;border-radius:16px;max-width:80%}
.bot{background:#1c1c1e;align-self:flex-start}
.user{background:#7BA06D;align-self:flex-end;margin-left:auto}
#log{display:flex;flex-direction:column}
form{display:flex;gap:8px;padding:12px 16px;border-top:1px solid #333}
input{flex:1;background:#1c1c1e;border:none;color:#fff;padding:12px 16px;border-radius:20px;font-size:16px;outline:none}
button{background:#7BA06D;color:#fff;border:none;padding:12px 20px;border-radius:20px;font-size:14px;cursor:pointer}
#debug{background:#1a1a1a;color:#86868b;padding:8px 16px;font-size:11px;max-height:80px;overflow-y:auto;border-top:1px solid #222}
</style>
</head>
<body>
<div style="padding:12px 16px;border-bottom:1px solid #333;font-size:13px;color:#86868b">
  NAKAI Chat Debug — <span id="status">checking...</span>
</div>
<div id="log">
  <div class="msg bot">テスト用チャットページです。メッセージを入力してください。</div>
</div>
<form id="f">
  <input id="i" placeholder="メッセージを入力..." autocomplete="off">
  <button type="submit">送信</button>
</form>
<div id="debug"></div>
<script>
var debug=document.getElementById('debug');
function log(s){debug.textContent+=new Date().toLocaleTimeString()+' '+s+'\\n';debug.scrollTop=debug.scrollHeight;}

// Health check
log('Checking API...');
fetch('/api/health').then(function(r){return r.json()}).then(function(d){
  document.getElementById('status').textContent='OK - '+d.model+' ('+d.documents+' docs)';
  document.getElementById('status').style.color='#7BA06D';
  log('Health OK: '+JSON.stringify(d));
}).catch(function(e){
  document.getElementById('status').textContent='ERROR: '+e.message;
  document.getElementById('status').style.color='red';
  log('Health ERROR: '+e.message);
});

// Chat
var loading=false;
document.getElementById('f').addEventListener('submit',function(e){
  e.preventDefault();
  var inp=document.getElementById('i');
  var msg=inp.value.trim();
  if(!msg||loading)return;
  inp.value='';
  var logEl=document.getElementById('log');
  var ud=document.createElement('div');ud.className='msg user';ud.textContent=msg;logEl.appendChild(ud);
  logEl.scrollTop=logEl.scrollHeight;
  log('Sending: '+msg);
  loading=true;
  fetch('/api/chat',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:msg,history:[],language:'ja'})
  }).then(function(r){
    log('Response status: '+r.status);
    if(!r.ok)throw new Error('HTTP '+r.status);
    return r.json();
  }).then(function(d){
    log('Response OK: '+d.response.substring(0,50)+'...');
    var bd=document.createElement('div');bd.className='msg bot';bd.textContent=d.response;logEl.appendChild(bd);
    logEl.scrollTop=logEl.scrollHeight;
  }).catch(function(e){
    log('ERROR: '+e.message);
    var ed=document.createElement('div');ed.className='msg bot';ed.style.color='red';ed.textContent='Error: '+e.message;logEl.appendChild(ed);
    logEl.scrollTop=logEl.scrollHeight;
  }).finally(function(){loading=false});
});
log('Page loaded');
</script>
</body>
</html>"""
    return HTMLResponse(content=test_html, headers={"Cache-Control": "no-store"})


@pwa_router.get("/app")
async def serve_app():
    return HTMLResponse(
        content=APP_HTML,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
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
