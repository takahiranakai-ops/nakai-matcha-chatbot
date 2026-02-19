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
<meta name="theme-color" content="#406546">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NAKAI">
<meta name="description" content="NAKAI Matcha Concierge — Your personal AI matcha expert">
<title>NAKAI Matcha Concierge</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/png" href="/icon-192.png">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600&family=Work+Sans:wght@200;300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#F9F0E2;--bg-warm:#F8F8E3;--surface:#FFFFFF;
  --green-deep:#406546;--green:#81A370;--green-light:rgba(129,163,112,.12);--green-lighter:rgba(129,163,112,.06);
  --beige:#ECDDC7;--beige-light:rgba(236,221,199,.4);
  --brown:#9E8471;--brown-light:rgba(158,132,113,.5);
  --red:#F5361E;
  --text-1:#406546;--text-2:#9E8471;--text-3:#C4B5A5;
  --separator:rgba(158,132,113,.18);--separator-light:rgba(158,132,113,.1);
  --ease:cubic-bezier(.25,1,.5,1);--ease-spring:cubic-bezier(.34,1.56,.64,1);
  --shadow-sm:0 1px 3px rgba(64,101,70,.06);
  --shadow-md:0 4px 16px rgba(64,101,70,.08);
  --shadow-lg:0 8px 32px rgba(64,101,70,.1);
}}
html,body{{
  height:100%;overflow:hidden;background:var(--bg);color:var(--text-1);
  font-family:'Work Sans',-apple-system,BlinkMacSystemFont,sans-serif;
  -webkit-font-smoothing:antialiased;
}}
#nc-app{{display:flex;height:100vh;height:100dvh}}

/* ===== Brand Panel (desktop) ===== */
.nc-brand{{
  width:380px;flex-shrink:0;background:var(--green-deep);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:64px 48px;
}}
.nc-brand__logo{{width:140px;opacity:.9;margin-bottom:56px;animation:ncUp .7s var(--ease) both}}
.nc-brand__tagline{{font-weight:200;font-size:1.4rem;line-height:1.7;text-align:center;color:rgba(249,240,226,.85);margin-bottom:12px;animation:ncUp .7s .1s var(--ease) both}}
.nc-brand__sub{{font-weight:400;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:rgba(249,240,226,.4);animation:ncUp .7s .18s var(--ease) both}}
.nc-brand__sep{{width:32px;height:1px;background:rgba(249,240,226,.15);margin:40px 0;animation:ncUp .7s .25s var(--ease) both}}
.nc-brand__powered{{font-weight:300;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:rgba(249,240,226,.3);margin-bottom:36px;animation:ncUp .7s .32s var(--ease) both}}
.nc-brand__ctas{{display:flex;flex-direction:column;gap:10px;width:100%;max-width:220px;animation:ncUp .7s .38s var(--ease) both}}

/* ===== Shared CTA Button ===== */
.nc-cta{{
  display:flex;align-items:center;justify-content:center;gap:8px;
  font-family:inherit;font-size:.78rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;
  text-decoration:none;padding:13px 24px;border-radius:12px;cursor:pointer;
  transition:all .3s var(--ease);-webkit-tap-highlight-color:transparent;
}}
.nc-cta--primary{{background:var(--green);color:#fff;border:none}}
.nc-cta--primary:hover{{background:#8BB47C;transform:scale(1.02);box-shadow:0 4px 20px rgba(129,163,112,.25)}}
.nc-cta--primary:active{{transform:scale(.96)}}
.nc-cta--secondary{{background:transparent;color:var(--text-2);border:1px solid var(--beige)}}
.nc-cta--secondary:hover{{background:var(--beige-light);color:var(--text-1)}}
.nc-cta--secondary:active{{transform:scale(.96)}}
.nc-cta--brand-secondary{{background:transparent;color:rgba(249,240,226,.7);border:1px solid rgba(249,240,226,.2)}}
.nc-cta--brand-secondary:hover{{background:rgba(249,240,226,.1);color:rgba(249,240,226,.9)}}

/* ===== Main Content (right side) ===== */
.nc-main{{flex:1;display:flex;flex-direction:column;background:var(--bg);min-width:0;position:relative;overflow:hidden}}

/* ===== HOME VIEW ===== */
.nc-home{{
  position:absolute;inset:0;display:flex;flex-direction:column;
  overflow-y:auto;-webkit-overflow-scrolling:touch;
  transition:opacity .35s var(--ease),transform .35s var(--ease);
  z-index:5;
}}
.nc-home.nc-hidden{{opacity:0;transform:translateX(-20px);pointer-events:none}}
.nc-home__scroll{{
  flex:1;display:flex;flex-direction:column;align-items:center;
  padding:max(60px,10vh) 24px 40px;
}}
.nc-home__symbol{{width:56px;opacity:.7;margin-bottom:20px;animation:ncUp .6s var(--ease) both}}
.nc-home__logo{{width:160px;opacity:.9;margin-bottom:8px;animation:ncUp .6s .06s var(--ease) both}}
.nc-home__title{{
  font-weight:300;font-size:1rem;letter-spacing:.14em;text-transform:uppercase;text-align:center;
  color:var(--text-2);margin-bottom:40px;animation:ncUp .6s .12s var(--ease) both;
}}

/* Cards Grid */
.nc-cards{{
  display:grid;grid-template-columns:1fr 1fr;gap:12px;
  width:100%;max-width:400px;margin-bottom:32px;
  animation:ncUp .6s .18s var(--ease) both;
}}
.nc-card{{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:10px;padding:24px 16px;border-radius:16px;
  background:var(--surface);border:1px solid var(--separator-light);
  cursor:pointer;text-decoration:none;color:var(--text-1);
  transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent;
  box-shadow:var(--shadow-sm);
}}
.nc-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow-md);border-color:var(--green-light)}}
.nc-card:active{{transform:scale(.97)}}
.nc-card__icon{{
  width:48px;height:48px;border-radius:14px;
  display:flex;align-items:center;justify-content:center;font-size:1.4rem;
}}
.nc-card__icon--brew{{background:rgba(64,101,70,.08)}}
.nc-card__icon--product{{background:rgba(129,163,112,.1)}}
.nc-card__icon--faq{{background:rgba(158,132,113,.1)}}
.nc-card__icon--shop{{background:rgba(236,221,199,.5)}}
.nc-card__label{{font-size:.78rem;font-weight:500;letter-spacing:.02em;text-align:center;color:var(--text-1)}}
.nc-card__desc{{font-size:.62rem;color:var(--text-2);text-align:center;line-height:1.5}}

/* Home CTAs */
.nc-home__ctas{{
  display:flex;flex-direction:column;gap:10px;width:100%;max-width:400px;
  animation:ncUp .6s .24s var(--ease) both;
}}
.nc-home__cta-main{{padding:16px 24px;border-radius:14px;font-size:.82rem}}
.nc-home__footer{{
  display:flex;flex-direction:column;align-items:center;gap:16px;
  margin-top:32px;animation:ncUp .6s .3s var(--ease) both;
}}
.nc-home__powered{{font-size:.55rem;font-weight:300;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3);opacity:.6}}

/* ===== CHAT VIEW ===== */
.nc-chat{{
  position:absolute;inset:0;display:flex;flex-direction:column;
  transition:opacity .35s var(--ease),transform .35s var(--ease);
  z-index:4;background:var(--bg-warm);
}}
.nc-chat.nc-hidden{{opacity:0;transform:translateX(20px);pointer-events:none}}

/* Header */
.nc-header{{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 24px;background:rgba(255,255,255,.8);
  -webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid var(--separator-light);flex-shrink:0;z-index:10;
}}
.nc-header__left{{display:flex;align-items:center;gap:10px}}
.nc-back{{
  display:none;background:none;border:none;color:var(--text-2);
  font-size:1.2rem;cursor:pointer;padding:4px 8px 4px 0;
  -webkit-tap-highlight-color:transparent;transition:color .2s;
}}
.nc-back:active{{color:var(--text-1)}}
.nc-header__logo-m{{height:18px;opacity:.85;display:none}}
.nc-header__title{{font-weight:500;font-size:.82rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text-2)}}
.nc-header__badge{{
  display:inline-flex;align-items:center;gap:4px;background:var(--green-light);
  border-radius:100px;padding:3px 10px 3px 7px;font-size:.65rem;font-weight:500;
  letter-spacing:.06em;color:var(--green-deep);
}}
.nc-header__badge-dot{{width:5px;height:5px;border-radius:50%;background:var(--green);animation:ncPulse 3s ease-in-out infinite}}
@keyframes ncPulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.nc-header__right{{display:flex;align-items:center;gap:10px}}
.nc-lang{{
  background:var(--green-lighter);border:none;border-radius:8px;padding:6px 12px;
  color:var(--green-deep);font-family:inherit;font-size:.7rem;font-weight:500;letter-spacing:.1em;
  cursor:pointer;transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent;
}}
.nc-lang:hover{{background:var(--green-light);color:var(--green-deep)}}

/* Messages */
.nc-messages{{flex:1;overflow-y:auto;padding:24px 24px 16px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth}}
.nc-messages::-webkit-scrollbar{{width:0;display:none}}
.nc-banner{{display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;margin:0 auto 20px;background:var(--green-lighter);border-radius:12px;font-size:.72rem;color:var(--text-2);max-width:400px}}
.nc-banner__dot{{width:4px;height:4px;border-radius:50%;background:var(--green)}}
.nc-msg{{display:flex;flex-direction:column;animation:ncMsgIn .4s var(--ease) both}}
@keyframes ncMsgIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.nc-msg--bot{{align-items:flex-start;padding-right:48px;position:relative;padding-left:40px}}
.nc-msg--bot::before{{
  content:'';position:absolute;left:0;top:0;width:28px;height:28px;border-radius:50%;
  background:var(--green-deep);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F9F0E2'%3E%3Cpath d='M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.71c.59.35 1.27.71 2.06.71 2.02 0 4.5-1.98 4.69-4.34C14.65 14.39 17 12.5 17 8z' opacity='.9'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:center;background-size:16px;
}}
.nc-msg--bot .nc-msg__bubble{{background:var(--surface);border:1px solid var(--separator-light);border-radius:20px 20px 20px 6px;padding:14px 18px;font-size:.9rem;font-weight:350;line-height:1.8;color:var(--text-1);box-shadow:var(--shadow-sm)}}
.nc-msg__bubble a{{color:var(--green);text-decoration:none;font-weight:500;transition:opacity .2s}}
.nc-msg__bubble a:hover{{opacity:.7}}
.nc-msg__bubble strong{{font-weight:600;color:var(--green-deep)}}
.nc-msg__bubble ul,.nc-msg__bubble ol{{margin:8px 0;padding-left:20px}}
.nc-msg__bubble li{{margin:4px 0}}
.nc-msg--user{{align-items:flex-end;padding-left:48px;margin-top:4px}}
.nc-msg--user .nc-msg__bubble{{background:var(--green-deep);color:rgba(249,240,226,.95);border-radius:20px 20px 6px 20px;padding:12px 18px;font-size:.9rem;font-weight:400;line-height:1.72;box-shadow:var(--shadow-md)}}
.nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:12px}}
.nc-msg__meta{{display:flex;align-items:center;gap:6px;margin-top:6px;padding-left:4px}}
.nc-msg__time{{font-size:.62rem;color:var(--text-3)}}
.nc-msg__sources{{margin-top:8px;padding-left:4px;display:flex;flex-wrap:wrap;gap:6px}}
.nc-msg__source{{display:inline-flex;align-items:center;gap:4px;font-size:.72rem;color:var(--green-deep);text-decoration:none;background:var(--green-lighter);border:1px solid var(--green-light);border-radius:10px;padding:8px 14px;min-height:36px;transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent}}
.nc-msg__source:hover{{background:var(--green-light)}}
.nc-msg__source:active{{transform:scale(.95)}}
.nc-typing .nc-msg__bubble{{display:flex;gap:5px;align-items:center;padding:16px 20px!important;min-height:44px}}
.nc-typing .nc-msg__bubble span{{width:5px;height:5px;background:var(--beige);border-radius:50%;display:inline-block;animation:ncWave 1.4s ease-in-out infinite}}
.nc-typing .nc-msg__bubble span:nth-child(2){{animation-delay:.15s}}
.nc-typing .nc-msg__bubble span:nth-child(3){{animation-delay:.3s}}
@keyframes ncWave{{0%,60%,100%{{opacity:.3;transform:translateY(0)}}30%{{opacity:1;transform:translateY(-3px)}}}}
.nc-typing__label{{font-size:.65rem;color:var(--text-3);padding-left:4px;margin-top:4px}}
.nc-quick{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.nc-quick__btn{{font-family:inherit;font-size:.78rem;font-weight:400;color:var(--text-1);background:var(--surface);border:1px solid var(--separator);border-radius:14px;padding:10px 18px;cursor:pointer;transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-sm)}}
.nc-quick__btn:hover{{background:var(--green-lighter);border-color:var(--green-light);transform:translateY(-1px)}}
.nc-quick__btn:active{{transform:scale(.95)}}

/* Input */
.nc-input-area{{padding:12px 24px 16px;flex-shrink:0}}
.nc-form{{display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--separator);border-radius:24px;padding:4px 4px 4px 20px;transition:all .3s var(--ease);box-shadow:var(--shadow-sm)}}
.nc-form:focus-within{{border-color:var(--green-light);box-shadow:0 0 0 3px rgba(129,163,112,.1)}}
.nc-input{{flex:1;border:none;background:transparent;color:var(--text-1);font-family:inherit;font-size:.88rem;font-weight:350;outline:none;padding:10px 0}}
.nc-input::placeholder{{color:var(--text-3);font-weight:300}}
.nc-send{{width:36px;height:36px;border-radius:50%;border:none;background:var(--green-deep);color:rgba(249,240,226,.9);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .2s var(--ease);-webkit-tap-highlight-color:transparent}}
.nc-send:hover{{opacity:.85;transform:scale(1.05)}}
.nc-send:active{{transform:scale(.9)}}
.nc-send svg{{width:14px;height:14px}}

/* Chat Footer */
.nc-footer{{display:flex;align-items:center;justify-content:center;gap:16px;padding:6px 24px max(10px,env(safe-area-inset-bottom));flex-shrink:0;background:var(--bg-warm)}}
.nc-footer__link{{font-size:.65rem;font-weight:400;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);text-decoration:none;transition:color .2s}}
.nc-footer__link:hover{{color:var(--text-2)}}
.nc-footer__sep{{width:1px;height:10px;background:var(--separator-light)}}
.nc-footer__powered{{font-size:.6rem;font-weight:300;letter-spacing:.12em;text-transform:uppercase;color:var(--text-3);opacity:.5}}

/* Animations */
@keyframes ncUp{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}

/* ===== Responsive ===== */
@media(max-width:1199px){{
  .nc-brand{{width:320px;padding:48px 36px}}
  .nc-brand__logo{{width:120px;margin-bottom:44px}}
  .nc-brand__tagline{{font-size:1.25rem}}
}}
@media(max-width:899px){{
  .nc-brand{{display:none}}
  #nc-app{{height:100vh;height:100dvh;height:-webkit-fill-available}}
  .nc-back{{display:block}}
  .nc-header__logo-m{{display:block}}
  .nc-header{{padding:max(12px,env(safe-area-inset-top)) 16px 10px;background:rgba(249,240,226,.9);-webkit-backdrop-filter:saturate(180%) blur(24px);backdrop-filter:saturate(180%) blur(24px);border-bottom:1px solid var(--separator-light)}}
  .nc-header__title{{font-size:.72rem;letter-spacing:.12em}}
  .nc-header__badge{{font-size:.6rem;padding:2px 8px 2px 5px}}
  .nc-header__badge-dot{{width:4px;height:4px}}
  .nc-lang{{padding:5px 10px;font-size:.65rem;border-radius:6px}}
  .nc-lang:active{{transform:scale(.92)}}
  .nc-messages{{padding:16px 14px 8px;-webkit-overflow-scrolling:touch}}
  .nc-msg--bot{{padding-right:16px;padding-left:36px}}
  .nc-msg--bot::before{{width:24px;height:24px;background-size:13px}}
  .nc-msg--user{{padding-left:40px}}
  .nc-msg--bot .nc-msg__bubble{{font-size:.92rem;padding:12px 16px;line-height:1.75;border-radius:22px 22px 22px 6px}}
  .nc-msg--user .nc-msg__bubble{{font-size:.92rem;padding:12px 16px;line-height:1.7;border-radius:22px 22px 6px 22px}}
  .nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:10px}}
  .nc-banner{{font-size:.66rem;padding:7px 12px;margin-bottom:14px;border-radius:10px}}
  .nc-quick{{display:flex;flex-wrap:nowrap;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:2px 0 6px;margin-top:14px;scrollbar-width:none}}
  .nc-quick::-webkit-scrollbar{{display:none}}
  .nc-quick__btn{{font-size:.8rem;padding:10px 18px;border-radius:20px;white-space:nowrap;flex-shrink:0}}
  .nc-input-area{{padding:8px 14px 4px;background:rgba(248,248,227,.85);-webkit-backdrop-filter:saturate(150%) blur(20px);backdrop-filter:saturate(150%) blur(20px);border-top:1px solid var(--separator-light)}}
  .nc-form{{padding:4px 4px 4px 18px;border-radius:22px}}
  .nc-input{{font-size:16px;padding:12px 0;min-height:44px}}
  .nc-send{{width:38px;height:38px;transition:all .15s var(--ease)}}
  .nc-send:active{{transform:scale(.85)}}
  .nc-footer{{padding:4px 16px max(6px,env(safe-area-inset-bottom));gap:12px}}
  .nc-footer__link{{font-size:.58rem}}
  .nc-footer__powered{{font-size:.52rem;opacity:.3}}
  .nc-home__scroll{{padding:max(40px,8vh) 20px 32px}}
  .nc-home__symbol{{width:48px;margin-bottom:16px}}
  .nc-home__logo{{width:130px}}
  .nc-home__title{{font-size:.88rem}}
  .nc-cards{{max-width:100%;gap:10px}}
  .nc-card{{padding:20px 14px;border-radius:14px}}
}}
@media(max-width:430px){{
  .nc-messages{{padding:14px 10px 8px}}
  .nc-msg--bot{{padding-right:10px;padding-left:32px}}
  .nc-msg--bot::before{{width:22px;height:22px;background-size:12px}}
  .nc-msg--user{{padding-left:32px}}
  .nc-msg--bot .nc-msg__bubble,.nc-msg--user .nc-msg__bubble{{font-size:.88rem;padding:10px 14px}}
  .nc-input-area{{padding:6px 10px 2px}}
  .nc-form{{padding:3px 3px 3px 14px;border-radius:20px}}
  .nc-send{{width:34px;height:34px}}
  .nc-send svg{{width:13px;height:13px}}
  .nc-footer{{padding:2px 12px max(4px,env(safe-area-inset-bottom));gap:10px}}
  .nc-home__scroll{{padding:max(32px,6vh) 16px 24px}}
  .nc-cards{{gap:8px}}
  .nc-card{{padding:18px 12px;gap:8px}}
  .nc-card__icon{{width:40px;height:40px;font-size:1.2rem}}
  .nc-card__label{{font-size:.74rem}}
}}
@media(hover:none){{
  .nc-card:hover,.nc-cta--primary:hover,.nc-cta--secondary:hover,.nc-quick__btn:hover{{transform:none;box-shadow:var(--shadow-sm)}}
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
      <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-cta nc-cta--brand-secondary">Wholesale Inquiry</a>
    </div>
  </aside>

  <!-- Main Content -->
  <div class="nc-main">

    <!-- HOME VIEW -->
    <div class="nc-home" id="nc-home">
      <div class="nc-home__scroll">
        <img class="nc-home__symbol" src="data:image/png;base64,{_LOGO_ICON_BLACK_B64}" alt="" />
        <img class="nc-home__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
        <h1 class="nc-home__title" id="nc-home-title">AI Matcha Concierge</h1>

        <div class="nc-cards">
          <div class="nc-card" data-chat-msg="brew">
            <div class="nc-card__icon nc-card__icon--brew">&#127861;</div>
            <span class="nc-card__label" id="nc-card-brew">Brewing Guide</span>
            <span class="nc-card__desc" id="nc-card-brew-d">Temperature, ratio, technique</span>
          </div>
          <div class="nc-card" data-chat-msg="product">
            <div class="nc-card__icon nc-card__icon--product">&#128230;</div>
            <span class="nc-card__label" id="nc-card-product">Product Knowledge</span>
            <span class="nc-card__desc" id="nc-card-product-d">Grades, origins, tasting notes</span>
          </div>
          <div class="nc-card" data-chat-msg="faq">
            <div class="nc-card__icon nc-card__icon--faq">&#128172;</div>
            <span class="nc-card__label" id="nc-card-faq">Customer FAQ</span>
            <span class="nc-card__desc" id="nc-card-faq-d">Common questions, quick answers</span>
          </div>
          <a class="nc-card" href="https://nakaimatcha.com/" target="_blank" rel="noopener">
            <div class="nc-card__icon nc-card__icon--shop">&#128722;</div>
            <span class="nc-card__label" id="nc-card-shop">Shop NAKAI</span>
            <span class="nc-card__desc" id="nc-card-shop-d">Browse our matcha collection</span>
          </a>
        </div>

        <div class="nc-home__ctas">
          <button class="nc-cta nc-cta--primary nc-home__cta-main" id="nc-start-chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M4.913 2.658c2.075-.27 4.19-.408 6.337-.408 2.147 0 4.262.139 6.337.408 1.922.25 3.291 1.861 3.405 3.727a4.403 4.403 0 0 0-1.032-.211 50.89 50.89 0 0 0-8.42 0c-2.358.196-4.04 2.19-4.04 4.434v4.286a4.47 4.47 0 0 0 2.433 3.984L7.28 21.53A.75.75 0 0 1 6 20.97v-1.95a48.276 48.276 0 0 1-1.087-.128C2.905 18.636 1.5 17.09 1.5 15.27V5.658c0-1.81 1.406-3.346 3.413-3Z"/><path d="M15.75 7.5c-1.376 0-2.739.057-4.086.169C10.124 7.797 9 9.103 9 10.609v4.285c0 1.507 1.128 2.814 2.67 2.94 1.243.102 2.5.157 3.768.165l2.782 2.781a.75.75 0 0 0 1.28-.53v-2.39l.33-.026c1.542-.125 2.67-1.433 2.67-2.94v-4.286c0-1.505-1.125-2.811-2.664-2.94A49.392 49.392 0 0 0 15.75 7.5Z"/></svg>
            <span id="nc-start-label">Start Chat</span>
          </button>
          <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-cta nc-cta--secondary" id="nc-ws-btn">
            <span id="nc-ws-label">Wholesale Inquiry</span>
          </a>
        </div>

        <div class="nc-home__footer">
          <span class="nc-home__powered">Powered by NAKAI</span>
        </div>
      </div>
    </div>

    <!-- CHAT VIEW -->
    <div class="nc-chat nc-hidden" id="nc-chat">
      <header class="nc-header">
        <div class="nc-header__left">
          <button class="nc-back" id="nc-back" aria-label="Back">&#8249;</button>
          <img class="nc-header__logo-m" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
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
  var currentView='home';

  var i18n={{
    en:{{
      greeting:"Welcome! I'm your AI Matcha Concierge. How can I help you today?",
      placeholder:'Ask about matcha...',
      typing:'Thinking...',
      banner:'AI-powered answers based on our matcha expertise',
      online:'Online',
      q1:'How to brew matcha',q1m:'How do I brew the perfect cup of matcha?',
      q2:'Health benefits',q2m:'What are the health benefits of matcha?',
      q3:'Matcha vs coffee',q3m:'How does matcha compare to coffee?',
      q4:'Recommend a product',q4m:'What matcha products do you recommend?',
      error:"Connection issue. Please try again in a moment.",
      shop:'Shop NAKAI',wholesale:'Wholesale',
      homeTitle:'AI Matcha Concierge',
      startChat:'Start Chat',wsLabel:'Wholesale Inquiry',
      cardBrew:'Brewing Guide',cardBrewD:'Temperature, ratio, technique',
      cardProduct:'Product Knowledge',cardProductD:'Grades, origins, tasting notes',
      cardFaq:'Customer FAQ',cardFaqD:'Common questions, quick answers',
      cardShop:'Shop NAKAI',cardShopD:'Browse our matcha collection',
      brewMsg:'How do I brew the perfect cup of matcha? Please include water temperature, matcha-to-water ratio, and whisking technique.',
      productMsg:'Tell me about NAKAI matcha products. What grades do you offer and what makes each one special?',
      faqMsg:'What are the most common customer questions about matcha? Give me quick answers I can use as a barista.',
    }},
    ja:{{
      greeting:'ようこそ！AI抹茶コンシェルジュです。何かお手伝いできることはありますか？',
      placeholder:'抹茶について質問する...',
      typing:'考え中...',
      banner:'AIが抹茶の専門知識に基づいて回答します',
      online:'オンライン',
      q1:'美味しい抹茶の点て方',q1m:'美味しい抹茶の点て方を教えてください',
      q2:'抹茶の健康効果',q2m:'抹茶の健康効果について教えてください',
      q3:'抹茶 vs コーヒー',q3m:'抹茶とコーヒーの違いを教えてください',
      q4:'おすすめ商品',q4m:'おすすめの抹茶商品を教えてください',
      error:'接続に問題が発生しました。もう一度お試しください。',
      shop:'ショップ',wholesale:'卸売',
      homeTitle:'AI 抹茶コンシェルジュ',
      startChat:'チャットを始める',wsLabel:'卸売のお問い合わせ',
      cardBrew:'点て方ガイド',cardBrewD:'水温・分量・点て方のコツ',
      cardProduct:'商品知識',cardProductD:'グレード・産地・味わい',
      cardFaq:'お客様FAQ',cardFaqD:'よくある質問と回答',
      cardShop:'Shop NAKAI',cardShopD:'抹茶コレクションを見る',
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

  /* ---- View switching ---- */
  function showHome(){{
    currentView='home';
    $('nc-home').classList.remove('nc-hidden');
    $('nc-chat').classList.add('nc-hidden');
  }}
  function showChat(autoMsg){{
    currentView='chat';
    $('nc-home').classList.add('nc-hidden');
    $('nc-chat').classList.remove('nc-hidden');
    if(autoMsg){{
      $('nc-input').value=autoMsg;
      setTimeout(function(){{sendMessage()}},200);
    }}
    if(window.innerWidth>899)$('nc-input').focus();
  }}

  /* ---- Language ---- */
  function setLang(l){{
    lang=l;localStorage.setItem('nakai_lang',l);
    document.documentElement.lang=l;
    $('nc-lang').textContent=l.toUpperCase();
    $('nc-input').placeholder=t('placeholder');
    $('nc-banner-text').textContent=t('banner');
    $('nc-status').textContent=t('online');
    $('nc-greeting').innerHTML=t('greeting');
    $('nc-footer-shop').textContent=t('shop');
    $('nc-footer-ws').textContent=t('wholesale');
    $('nc-home-title').textContent=t('homeTitle');
    $('nc-start-label').textContent=t('startChat');
    $('nc-ws-label').textContent=t('wsLabel');
    $('nc-card-brew').textContent=t('cardBrew');
    $('nc-card-brew-d').textContent=t('cardBrewD');
    $('nc-card-product').textContent=t('cardProduct');
    $('nc-card-product-d').textContent=t('cardProductD');
    $('nc-card-faq').textContent=t('cardFaq');
    $('nc-card-faq-d').textContent=t('cardFaqD');
    $('nc-card-shop').textContent=t('cardShop');
    $('nc-card-shop-d').textContent=t('cardShopD');
    buildQuickActions();
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
    $('nc-lang').addEventListener('click',function(){{setLang(lang==='en'?'ja':'en')}});
    $('nc-back').addEventListener('click',showHome);
    $('nc-start-chat').addEventListener('click',function(){{showChat()}});

    /* Card click handlers */
    var cards=document.querySelectorAll('.nc-card[data-chat-msg]');
    cards.forEach(function(c){{
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
