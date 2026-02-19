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
_LOGO_WM_BLACK_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-wordmark-black.png").read_bytes()
).decode()
_LOGO_ICON_BLACK_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-black-icon.png").read_bytes()
).decode()
_ICON_B64 = base64.b64encode(_ICON_BYTES).decode()

# ---- PWA Manifest ----
MANIFEST_JSON = """{
  "name": "NAKAI Matcha Concierge",
  "short_name": "NAKAI",
  "description": "Your personal AI matcha expert",
  "start_url": "/app",
  "display": "standalone",
  "background_color": "#F9F0E2",
  "theme_color": "#406546",
  "orientation": "portrait",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ],
  "categories": ["food", "lifestyle"]
}"""

# ---- Service Worker ----
SW_JS = """
self.addEventListener('install',function(){self.skipWaiting()});
self.addEventListener('activate',function(e){
  e.waitUntil(
    caches.keys().then(function(ks){
      return Promise.all(ks.map(function(k){return caches.delete(k)}));
    }).then(function(){return self.registration.unregister()})
  );
  self.clients.claim();
});
self.addEventListener('fetch',function(e){e.respondWith(fetch(e.request))});
"""

# ---- Main App HTML ----
# Design: 3 colors — #406546 (green), #F9F0E2 (cream), #FFFFFF (white)
APP_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#406546">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NAKAI">
<meta name="description" content="NAKAI Matcha Concierge">
<title>NAKAI Matcha Concierge</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/png" href="/icon-192.png">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500&family=Work+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --green:#406546;--cream:#F9F0E2;--white:#FFFFFF;
  --g90:rgba(64,101,70,.9);--g60:rgba(64,101,70,.6);
  --g40:rgba(64,101,70,.4);--g20:rgba(64,101,70,.2);
  --g10:rgba(64,101,70,.1);--g05:rgba(64,101,70,.05);
  --ease:cubic-bezier(.25,1,.5,1);
}}
html,body{{height:100%;overflow:hidden;background:var(--cream);color:var(--green);font-family:'Work Sans',sans-serif;-webkit-font-smoothing:antialiased}}
html[lang="ja"]{{font-family:'Shippori Mincho','Work Sans',sans-serif}}
#nc-app{{display:flex;height:100vh;height:100dvh}}

/* Brand Panel (desktop) */
.nc-brand{{
  width:360px;flex-shrink:0;background:var(--green);
  display:flex;flex-direction:column;align-items:center;justify-content:center;padding:64px 48px;
}}
.nc-brand__logo{{width:120px;opacity:.85;margin-bottom:48px;animation:ncUp .6s var(--ease) both}}
.nc-brand__tagline{{font-weight:300;font-size:1.3rem;line-height:1.8;text-align:center;color:var(--cream);opacity:.7;margin-bottom:48px;animation:ncUp .6s .1s var(--ease) both}}
.nc-brand__ctas{{display:flex;flex-direction:column;gap:10px;width:100%;max-width:200px;animation:ncUp .6s .2s var(--ease) both}}
.nc-brand__cta{{
  display:block;text-align:center;font-family:inherit;font-size:.72rem;font-weight:500;
  letter-spacing:.12em;text-transform:uppercase;text-decoration:none;
  padding:13px 20px;border-radius:10px;cursor:pointer;transition:all .25s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-brand__cta--p{{background:rgba(249,240,226,.15);color:var(--cream);border:none}}
.nc-brand__cta--p:hover{{background:rgba(249,240,226,.25)}}
.nc-brand__cta--s{{background:transparent;color:rgba(249,240,226,.5);border:1px solid rgba(249,240,226,.15)}}
.nc-brand__cta--s:hover{{color:var(--cream);border-color:rgba(249,240,226,.3)}}

/* Main */
.nc-main{{flex:1;display:flex;flex-direction:column;min-width:0;position:relative;overflow:hidden}}

/* HOME */
.nc-home{{position:absolute;inset:0;display:flex;flex-direction:column;overflow-y:auto;-webkit-overflow-scrolling:touch;transition:opacity .3s var(--ease),transform .3s var(--ease);z-index:5}}
.nc-home.nc-hidden{{opacity:0;transform:translateX(-16px);pointer-events:none}}
.nc-home__top{{display:flex;justify-content:flex-end;padding:max(14px,env(safe-area-inset-top)) 20px 0;flex-shrink:0}}
.nc-home__scroll{{flex:1;display:flex;flex-direction:column;align-items:center;padding:max(24px,6vh) 24px 40px}}
.nc-home__logo{{width:140px;margin-bottom:10px;animation:ncUp .5s var(--ease) both}}
.nc-home__sub{{font-weight:400;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--g40);margin-bottom:max(36px,5vh);animation:ncUp .5s .06s var(--ease) both}}

/* Menu */
.nc-menu{{width:100%;max-width:400px;animation:ncUp .5s .12s var(--ease) both}}
.nc-menu__item{{
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 0;border-bottom:1px solid var(--g10);
  cursor:pointer;text-decoration:none;color:var(--green);
  transition:opacity .2s;-webkit-tap-highlight-color:transparent;
}}
.nc-menu__item:first-child{{border-top:1px solid var(--g10)}}
.nc-menu__item:active{{opacity:.5}}
.nc-menu__label{{font-size:.88rem;font-weight:400}}
.nc-menu__arrow{{font-size:.8rem;color:var(--g40);font-weight:300}}

/* Home CTA */
.nc-home__cta{{
  display:flex;align-items:center;justify-content:center;gap:8px;
  width:100%;max-width:400px;margin-top:max(28px,4vh);padding:16px 24px;
  background:var(--green);color:var(--cream);border:none;border-radius:12px;
  font-family:inherit;font-size:.82rem;font-weight:500;letter-spacing:.06em;
  cursor:pointer;transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent;
  animation:ncUp .5s .18s var(--ease) both;
}}
.nc-home__cta:active{{transform:scale(.97);opacity:.85}}

/* Home footer */
.nc-home__links{{display:flex;align-items:center;gap:20px;margin-top:24px;animation:ncUp .5s .24s var(--ease) both}}
.nc-home__link{{font-size:.68rem;font-weight:400;letter-spacing:.1em;text-transform:uppercase;color:var(--g40);text-decoration:none}}
.nc-home__link:active{{color:var(--green)}}
.nc-home__dot{{width:3px;height:3px;border-radius:50%;background:var(--g20)}}

/* Language toggle */
.nc-lang-toggle{{display:flex;background:var(--g05);border-radius:8px;overflow:hidden;border:1px solid var(--g10)}}
.nc-lang-btn{{
  font-family:'Work Sans',sans-serif;font-size:.68rem;font-weight:500;letter-spacing:.08em;
  padding:6px 14px;border:none;cursor:pointer;transition:all .2s var(--ease);
  -webkit-tap-highlight-color:transparent;background:transparent;color:var(--g40);
}}
.nc-lang-btn.active{{background:var(--green);color:var(--cream)}}

/* CHAT */
.nc-chat{{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .3s var(--ease),transform .3s var(--ease);z-index:4}}
.nc-chat.nc-hidden{{opacity:0;transform:translateX(16px);pointer-events:none}}

/* Header */
.nc-header{{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 20px;background:rgba(249,240,226,.85);
  -webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid var(--g10);flex-shrink:0;z-index:10;
}}
.nc-header__left{{display:flex;align-items:center;gap:10px}}
.nc-back{{display:none;background:none;border:none;color:var(--g60);font-size:1.3rem;cursor:pointer;padding:4px 8px 4px 0;-webkit-tap-highlight-color:transparent}}
.nc-back:active{{color:var(--green)}}
.nc-header__logo{{height:16px;opacity:.8;display:none}}
.nc-header__title{{font-weight:500;font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--g60)}}
.nc-header__dot{{width:6px;height:6px;border-radius:50%;background:var(--green);opacity:.6;animation:ncPulse 3s ease-in-out infinite}}
@keyframes ncPulse{{0%,100%{{opacity:.6}}50%{{opacity:.2}}}}

/* Messages */
.nc-messages{{flex:1;overflow-y:auto;padding:20px 20px 12px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth}}
.nc-messages::-webkit-scrollbar{{width:0;display:none}}
.nc-banner{{text-align:center;padding:8px 16px;margin:0 auto 16px;font-size:.68rem;color:var(--g40);letter-spacing:.02em}}
.nc-msg{{display:flex;flex-direction:column;animation:ncMsgIn .35s var(--ease) both}}
@keyframes ncMsgIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
.nc-msg--bot{{align-items:flex-start;padding-right:48px}}
.nc-msg--bot .nc-msg__bubble{{background:var(--white);border-radius:18px 18px 18px 4px;padding:14px 18px;font-size:.88rem;font-weight:400;line-height:1.8;color:var(--green);box-shadow:0 1px 3px rgba(64,101,70,.05)}}
.nc-msg__bubble a{{color:var(--green);font-weight:500;text-decoration:underline;text-decoration-color:var(--g20);text-underline-offset:2px}}
.nc-msg__bubble a:hover{{text-decoration-color:var(--green)}}
.nc-msg__bubble strong{{font-weight:600}}
.nc-msg__bubble ul,.nc-msg__bubble ol{{margin:8px 0;padding-left:20px}}
.nc-msg__bubble li{{margin:4px 0}}
.nc-msg--user{{align-items:flex-end;padding-left:48px;margin-top:4px}}
.nc-msg--user .nc-msg__bubble{{background:var(--green);color:var(--cream);border-radius:18px 18px 4px 18px;padding:12px 18px;font-size:.88rem;font-weight:400;line-height:1.7}}
.nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:10px}}
.nc-msg__meta{{margin-top:4px;padding-left:2px}}
.nc-msg__time{{font-size:.6rem;color:var(--g40)}}
.nc-msg__sources{{margin-top:6px;display:flex;flex-wrap:wrap;gap:6px}}
.nc-msg__source{{font-size:.7rem;color:var(--green);text-decoration:none;background:var(--g05);border:1px solid var(--g10);border-radius:8px;padding:7px 12px;-webkit-tap-highlight-color:transparent}}
.nc-msg__source:active{{background:var(--g10)}}
.nc-typing .nc-msg__bubble{{display:flex;gap:5px;align-items:center;padding:16px 20px!important;min-height:40px}}
.nc-typing .nc-msg__bubble span{{width:4px;height:4px;background:var(--g20);border-radius:50%;display:inline-block;animation:ncWave 1.4s ease-in-out infinite}}
.nc-typing .nc-msg__bubble span:nth-child(2){{animation-delay:.15s}}
.nc-typing .nc-msg__bubble span:nth-child(3){{animation-delay:.3s}}
@keyframes ncWave{{0%,60%,100%{{opacity:.2;transform:translateY(0)}}30%{{opacity:.8;transform:translateY(-3px)}}}}
.nc-typing__label{{font-size:.62rem;color:var(--g40);padding-left:2px;margin-top:3px}}
.nc-quick{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}}
.nc-quick__btn{{font-family:inherit;font-size:.76rem;font-weight:400;color:var(--green);background:var(--white);border:1px solid var(--g10);border-radius:20px;padding:9px 16px;cursor:pointer;-webkit-tap-highlight-color:transparent}}
.nc-quick__btn:active{{background:var(--g05);transform:scale(.96)}}

/* Input */
.nc-input-area{{padding:10px 20px 14px;flex-shrink:0}}
.nc-form{{display:flex;align-items:center;gap:8px;background:var(--white);border:1px solid var(--g10);border-radius:24px;padding:4px 4px 4px 18px;transition:border-color .2s}}
.nc-form:focus-within{{border-color:var(--g20)}}
.nc-input{{flex:1;border:none;background:transparent;color:var(--green);font-family:inherit;font-size:.88rem;font-weight:400;outline:none;padding:10px 0}}
.nc-input::placeholder{{color:var(--g40);font-weight:300}}
.nc-send{{width:34px;height:34px;border-radius:50%;border:none;background:var(--green);color:var(--cream);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent}}
.nc-send:active{{transform:scale(.88)}}
.nc-send svg{{width:13px;height:13px}}

/* Footer */
.nc-footer{{display:flex;align-items:center;justify-content:center;gap:14px;padding:4px 20px max(8px,env(safe-area-inset-bottom));flex-shrink:0}}
.nc-footer__link{{font-size:.6rem;font-weight:400;letter-spacing:.1em;text-transform:uppercase;color:var(--g40);text-decoration:none}}
.nc-footer__link:active{{color:var(--green)}}
.nc-footer__dot{{width:2px;height:2px;border-radius:50%;background:var(--g20)}}

@keyframes ncUp{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}

@media(max-width:1199px){{.nc-brand{{width:300px;padding:48px 36px}}.nc-brand__logo{{width:100px;margin-bottom:40px}}.nc-brand__tagline{{font-size:1.15rem}}}}
@media(max-width:899px){{
  .nc-brand{{display:none}}
  #nc-app{{height:100vh;height:100dvh;height:-webkit-fill-available}}
  .nc-back{{display:block}}.nc-header__logo{{display:block}}
  .nc-header{{padding:max(12px,env(safe-area-inset-top)) 16px 10px}}
  .nc-messages{{padding:14px 14px 8px;-webkit-overflow-scrolling:touch}}
  .nc-msg--bot{{padding-right:16px}}.nc-msg--user{{padding-left:40px}}
  .nc-quick{{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;scrollbar-width:none}}
  .nc-quick::-webkit-scrollbar{{display:none}}.nc-quick__btn{{white-space:nowrap;flex-shrink:0}}
  .nc-input-area{{padding:8px 14px 4px;background:rgba(249,240,226,.9);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);border-top:1px solid var(--g05)}}
  .nc-form{{padding:3px 3px 3px 16px}}.nc-input{{font-size:16px;padding:12px 0;min-height:44px}}.nc-send{{width:36px;height:36px}}
  .nc-footer{{padding:3px 14px max(6px,env(safe-area-inset-bottom))}}
  .nc-home__scroll{{padding:max(16px,3vh) 20px 32px}}.nc-home__logo{{width:120px}}
}}
@media(max-width:430px){{
  .nc-messages{{padding:12px 10px 6px}}
  .nc-msg--bot .nc-msg__bubble,.nc-msg--user .nc-msg__bubble{{font-size:.86rem;padding:10px 14px}}
  .nc-input-area{{padding:6px 10px 2px}}.nc-send{{width:34px;height:34px}}
  .nc-footer{{padding:2px 10px max(4px,env(safe-area-inset-bottom))}}
  .nc-home__scroll{{padding:max(12px,2vh) 16px 24px}}.nc-home__logo{{width:110px}}
  .nc-menu__item{{padding:16px 0}}
}}
</style>
</head>
<body>
<div id="nc-app">
  <aside class="nc-brand">
    <img class="nc-brand__logo" src="data:image/png;base64,{_LOGO_WHITE_B64}" alt="NAKAI" />
    <p class="nc-brand__tagline">Grounded in nature,<br>elevated in ritual.</p>
    <div class="nc-brand__ctas">
      <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-brand__cta nc-brand__cta--p">Shop NAKAI</a>
      <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-brand__cta nc-brand__cta--s">Wholesale</a>
    </div>
  </aside>
  <div class="nc-main">
    <!-- HOME -->
    <div class="nc-home" id="nc-home">
      <div class="nc-home__top">
        <div class="nc-lang-toggle" id="nc-lang-home">
          <button class="nc-lang-btn active" data-lang="en">EN</button>
          <button class="nc-lang-btn" data-lang="ja">JA</button>
        </div>
      </div>
      <div class="nc-home__scroll">
        <img class="nc-home__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
        <p class="nc-home__sub" id="nc-home-sub">Matcha Concierge</p>
        <nav class="nc-menu">
          <div class="nc-menu__item" data-chat-msg="brew">
            <span class="nc-menu__label" id="nc-m-brew">Brewing Guide</span>
            <span class="nc-menu__arrow">&rsaquo;</span>
          </div>
          <div class="nc-menu__item" data-chat-msg="product">
            <span class="nc-menu__label" id="nc-m-product">Product Knowledge</span>
            <span class="nc-menu__arrow">&rsaquo;</span>
          </div>
          <div class="nc-menu__item" data-chat-msg="faq">
            <span class="nc-menu__label" id="nc-m-faq">Customer FAQ</span>
            <span class="nc-menu__arrow">&rsaquo;</span>
          </div>
        </nav>
        <button class="nc-home__cta" id="nc-start-chat">
          <span id="nc-start-label">Start Chat</span>
        </button>
        <div class="nc-home__links">
          <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-home__link" id="nc-h-shop">Shop</a>
          <span class="nc-home__dot"></span>
          <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-home__link" id="nc-h-ws">Wholesale</a>
        </div>
      </div>
    </div>
    <!-- CHAT -->
    <div class="nc-chat nc-hidden" id="nc-chat">
      <header class="nc-header">
        <div class="nc-header__left">
          <button class="nc-back" id="nc-back" aria-label="Back">&#8249;</button>
          <img class="nc-header__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
          <span class="nc-header__title" id="nc-title">Concierge</span>
          <span class="nc-header__dot"></span>
        </div>
        <div class="nc-header__right">
          <div class="nc-lang-toggle" id="nc-lang-chat">
            <button class="nc-lang-btn active" data-lang="en">EN</button>
            <button class="nc-lang-btn" data-lang="ja">JA</button>
          </div>
        </div>
      </header>
      <div class="nc-messages" id="nc-messages">
        <div class="nc-banner" id="nc-banner-text">AI-powered answers based on our matcha expertise</div>
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
        <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-footer__link" id="nc-f-shop">Shop</a>
        <span class="nc-footer__dot"></span>
        <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-footer__link" id="nc-f-ws">Wholesale</a>
      </div>
    </div>
  </div>
</div>
<script>
(function(){{
  'use strict';
  var SHOP='https://nakaimatcha.com';
  var MAX_H=20;
  var chatHistory=[];
  var loading=false;

  var i18n={{
    en:{{
      greeting:"Welcome! I'm your AI Matcha Concierge. How can I help you today?",
      placeholder:'Ask about matcha...',
      typing:'Thinking...',
      banner:'AI-powered answers based on our matcha expertise',
      q1:'How to brew',q1m:'How do I brew the perfect cup of matcha?',
      q2:'Health benefits',q2m:'What are the health benefits of matcha?',
      q3:'Matcha vs coffee',q3m:'How does matcha compare to coffee?',
      q4:'Recommend',q4m:'What matcha products do you recommend?',
      error:"Connection issue. Please try again.",
      sub:'Matcha Concierge',startChat:'Start Chat',
      mBrew:'Brewing Guide',mProduct:'Product Knowledge',mFaq:'Customer FAQ',
      hShop:'Shop',hWs:'Wholesale',
      brewMsg:'How do I brew the perfect cup of matcha? Please include water temperature, matcha-to-water ratio, and whisking technique.',
      productMsg:'Tell me about NAKAI matcha products. What grades do you offer and what makes each one special?',
      faqMsg:'What are the most common customer questions about matcha? Give me quick answers I can use as a barista.',
    }},
    ja:{{
      greeting:'ようこそ！AI抹茶コンシェルジュです。何かお手伝いできることはありますか？',
      placeholder:'抹茶について質問する...',
      typing:'考え中...',
      banner:'AIが抹茶の専門知識に基づいて回答します',
      q1:'点て方',q1m:'美味しい抹茶の点て方を教えてください',
      q2:'健康効果',q2m:'抹茶の健康効果について教えてください',
      q3:'抹茶 vs コーヒー',q3m:'抹茶とコーヒーの違いを教えてください',
      q4:'おすすめ',q4m:'おすすめの抹茶商品を教えてください',
      error:'接続に問題が発生しました。もう一度お試しください。',
      sub:'抹茶コンシェルジュ',startChat:'チャットを始める',
      mBrew:'点て方ガイド',mProduct:'商品知識',mFaq:'お客様FAQ',
      hShop:'ショップ',hWs:'卸売',
      brewMsg:'美味しい抹茶の点て方を教えてください。水温、抹茶と水の割合、茶筅の使い方を含めてください。',
      productMsg:'NAKAIの抹茶商品について教えてください。どんなグレードがあり、それぞれの特徴は何ですか？',
      faqMsg:'抹茶に関するお客様からのよくある質問は何ですか？バリスタとして使える簡潔な回答をお願いします。',
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
    lang=l;localStorage.setItem('nakai_lang',l);
    document.documentElement.lang=l;
    document.querySelectorAll('.nc-lang-btn').forEach(function(b){{
      b.classList.toggle('active',b.getAttribute('data-lang')===l);
    }});
    $('nc-input').placeholder=t('placeholder');
    $('nc-banner-text').textContent=t('banner');
    $('nc-greeting').innerHTML=t('greeting');
    $('nc-home-sub').textContent=t('sub');
    $('nc-start-label').textContent=t('startChat');
    $('nc-m-brew').textContent=t('mBrew');
    $('nc-m-product').textContent=t('mProduct');
    $('nc-m-faq').textContent=t('mFaq');
    $('nc-h-shop').textContent=t('hShop');
    $('nc-h-ws').textContent=t('hWs');
    $('nc-f-shop').textContent=t('hShop');
    $('nc-f-ws').textContent=t('hWs');
    buildQuickActions();
  }}

  function showHome(){{
    $('nc-home').classList.remove('nc-hidden');
    $('nc-chat').classList.add('nc-hidden');
  }}
  function showChat(autoMsg){{
    $('nc-home').classList.add('nc-hidden');
    $('nc-chat').classList.remove('nc-hidden');
    if(autoMsg){{$('nc-input').value=autoMsg;setTimeout(function(){{sendMessage()}},200)}}
    if(window.innerWidth>899)$('nc-input').focus();
  }}

  function buildQuickActions(){{
    var qa=$('nc-quick');qa.innerHTML='';
    ['q1','q2','q3','q4'].forEach(function(k){{
      var b=document.createElement('button');b.className='nc-quick__btn';
      b.setAttribute('data-msg',t(k+'m'));b.textContent=t(k);
      b.addEventListener('click',function(){{$('nc-input').value=this.getAttribute('data-msg');sendMessage();qa.style.display='none'}});
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
    sources=sources||[];var m=$('nc-messages');if(!m)return;
    var d=document.createElement('div');d.className='nc-msg nc-msg--'+role;var html='';
    var content=role==='bot'?formatMd(text):escapeHtml(text);
    if(role==='bot'){{
      html+='<div class="nc-msg__bubble">'+content+'</div>';
      if(sources.length){{
        html+='<div class="nc-msg__sources">';
        sources.forEach(function(s){{var url=s.startsWith('/')?SHOP+s:s;
          var label=s.indexOf('/products/')>-1?(lang==='ja'?'商品を見る':'View product'):s.indexOf('/blogs/')>-1?(lang==='ja'?'記事を読む':'Read article'):(lang==='ja'?'詳細':'Learn more');
          html+='<a href="'+escapeHtml(url)+'" class="nc-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
        html+='</div>';
      }}
      var now=new Date();var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="nc-msg__meta"><span class="nc-msg__time">'+ts+'</span></div>';
    }}else{{html='<div class="nc-msg__bubble">'+content+'</div>'}}
    d.innerHTML=html;m.appendChild(d);scroll();
  }}
  function showTyping(){{var m=$('nc-messages');if(!m)return;var d=document.createElement('div');d.className='nc-msg nc-msg--bot nc-typing';d.innerHTML='<div class="nc-msg__bubble"><span></span><span></span><span></span></div><div class="nc-typing__label">'+t('typing')+'</div>';m.appendChild(d);scroll()}}
  function removeTyping(){{var m=$('nc-messages');if(!m)return;var tw=m.querySelector('.nc-typing');if(tw)tw.remove()}}

  function sendMessage(){{
    var inp=$('nc-input');var msg=inp?inp.value.trim():'';
    if(!msg||loading)return;inp.value='';
    addMsg('user',msg);chatHistory.push({{role:'user',content:msg}});
    showTyping();loading=true;
    fetch('/api/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg,history:chatHistory.slice(-MAX_H),language:lang}})}})
    .then(function(r){{if(!r.ok)throw new Error('err');return r.json()}})
    .then(function(d){{removeTyping();addMsg('bot',d.response,d.sources||[]);chatHistory.push({{role:'assistant',content:d.response}});saveHistory()}})
    .catch(function(){{removeTyping();addMsg('bot',t('error'))}})
    .finally(function(){{loading=false}});
  }}

  function saveHistory(){{try{{localStorage.setItem('nakai_app_history',JSON.stringify(chatHistory.slice(-MAX_H)))}}catch(e){{}}}}
  function loadHistory(){{try{{var s=localStorage.getItem('nakai_app_history');if(s){{chatHistory=JSON.parse(s);chatHistory.forEach(function(m){{addMsg(m.role==='assistant'?'bot':'user',m.content)}})}}}}catch(e){{}}}}

  function boot(){{
    setLang(lang);
    $('nc-form').addEventListener('submit',function(e){{e.preventDefault();sendMessage()}});
    $('nc-back').addEventListener('click',showHome);
    $('nc-start-chat').addEventListener('click',function(){{showChat()}});
    document.querySelectorAll('.nc-lang-btn').forEach(function(b){{
      b.addEventListener('click',function(){{setLang(this.getAttribute('data-lang'))}});
    }});
    document.querySelectorAll('.nc-menu__item[data-chat-msg]').forEach(function(c){{
      c.addEventListener('click',function(){{
        var key=this.getAttribute('data-chat-msg');
        var msg=t(key+'Msg');
        if(msg)showChat(msg);
      }});
    }});
    loadHistory();
    if(chatHistory.length>0)showChat();
    if('serviceWorker' in navigator){{
      navigator.serviceWorker.getRegistrations().then(function(regs){{regs.forEach(function(r){{r.unregister()}})}});
      caches.keys().then(function(ks){{ks.forEach(function(k){{caches.delete(k)}})}});
    }}
  }}

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);
  else boot();
}})();
</script>
</body>
</html>"""


@pwa_router.get("/test")
async def serve_test():
    """Minimal debug page."""
    return HTMLResponse(content="<h1>NAKAI Test</h1>", headers={"Cache-Control": "no-store"})


@pwa_router.get("/app")
async def serve_app():
    return HTMLResponse(
        content=APP_HTML,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@pwa_router.get("/manifest.json")
async def serve_manifest():
    return Response(content=MANIFEST_JSON, media_type="application/manifest+json", headers={"Cache-Control": "public, max-age=86400"})


@pwa_router.get("/sw.js")
async def serve_sw():
    return Response(content=SW_JS, media_type="application/javascript", headers={"Cache-Control": "public, max-age=0"})


@pwa_router.get("/icon-192.png")
async def serve_icon_192():
    return Response(content=_ICON_BYTES, media_type="image/png", headers={"Cache-Control": "public, max-age=604800"})


@pwa_router.get("/icon-512.png")
async def serve_icon_512():
    return Response(content=_ICON_BYTES, media_type="image/png", headers={"Cache-Control": "public, max-age=604800"})
