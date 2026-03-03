"""NAKAI Matcha Concierge — Standalone PWA Application.

Endpoints:
  GET /app           → Full HTML/CSS/JS PWA application
  GET /manifest.json → PWA manifest
  GET /sw.js         → Service worker
  GET /icon-192.png  → App icon
  GET /icon-512.png  → App icon
  GET /fonts/*.woff2 → Domaine Text web fonts
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
_LOGO_WM_WHITE_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-wordmark-white.png").read_bytes()
).decode()
_ICON_B64 = base64.b64encode(_ICON_BYTES).decode()

_FONT_FILES = {}

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
var CACHE_NAME='nakai-v2';
var PRECACHE=['/app','/manifest.json','/icon-192.png'];

self.addEventListener('install',function(e){
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(c){return c.addAll(PRECACHE)})
  );
  self.skipWaiting();
});

self.addEventListener('activate',function(e){
  e.waitUntil(
    caches.keys().then(function(ks){
      return Promise.all(ks.filter(function(k){return k!==CACHE_NAME}).map(function(k){return caches.delete(k)}));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET') return;
  e.respondWith(
    fetch(e.request).then(function(r){
      if(r&&r.status===200){
        var rc=r.clone();
        caches.open(CACHE_NAME).then(function(c){c.put(e.request,rc)});
      }
      return r;
    }).catch(function(){return caches.match(e.request)})
  );
});
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
<meta name="description" content="NAKAI's AI Matcha Concierge — discover premium organic matcha from Japan. Get personalized recommendations, brewing guides, and matcha expertise.">
<title>NAKAI Matcha Concierge — Premium Organic Matcha from Japan</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/png" href="/icon-192.png">
<link rel="apple-touch-icon" href="/icon-192.png">
<meta property="og:type" content="website">
<meta property="og:title" content="NAKAI Matcha Concierge">
<meta property="og:description" content="Your personal AI matcha expert. Discover NAKAI's numbered matcha collection — each with its own story, terroir, and character. From Kagoshima and Kyoto, Japan.">
<meta property="og:url" content="https://nakai-matcha-chat.onrender.com/app">
<meta property="og:site_name" content="NAKAI Matcha">
<meta property="og:image" content="https://nakaimatcha.com/cdn/shop/files/nakai-logo.png">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="ja_JP">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="NAKAI Matcha Concierge">
<meta name="twitter:description" content="Premium organic matcha from Kagoshima, Japan. AI-powered concierge for personalized recommendations.">
<meta name="twitter:image" content="https://nakaimatcha.com/cdn/shop/files/nakai-logo.png">
<link rel="canonical" href="https://nakai-matcha-chat.onrender.com/app">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "NAKAI Matcha Concierge",
  "description": "AI-powered matcha concierge for premium organic matcha from Japan",
  "url": "https://nakai-matcha-chat.onrender.com/app",
  "applicationCategory": "LifestyleApplication",
  "operatingSystem": "Any",
  "offers": {{
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }},
  "author": {{
    "@type": "Organization",
    "name": "NAKAI",
    "url": "https://nakaimatcha.com",
    "description": "Specialty organic matcha brand — grounded in nature, elevated in ritual",
    "foundingDate": "2024",
    "email": "info@s-natural.xyz",
    "brand": {{
      "@type": "Brand",
      "name": "NAKAI"
    }}
  }}
}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --green:#406546;--cream:#F9F0E2;--white:#FFFFFF;
  --g90:rgba(64,101,70,.9);--g70:rgba(64,101,70,.7);
  --g50:rgba(64,101,70,.5);--g35:rgba(64,101,70,.35);
  --g20:rgba(64,101,70,.2);--g12:rgba(64,101,70,.12);
  --g06:rgba(64,101,70,.06);--g03:rgba(64,101,70,.03);
  --sans:'Work Sans',sans-serif;
  --ease:cubic-bezier(.22,1,.36,1);--ease-spring:cubic-bezier(.175,.885,.32,1.275);
  --shadow-s:0 1px 2px rgba(64,101,70,.02),0 4px 12px rgba(64,101,70,.04);
  --shadow-m:0 2px 4px rgba(64,101,70,.03),0 10px 28px rgba(64,101,70,.06);
  --shadow-l:0 4px 8px rgba(64,101,70,.03),0 16px 48px rgba(64,101,70,.08);
}}
html,body{{height:100%;overflow:hidden;background:var(--cream);color:var(--green);font-family:var(--sans);-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}}
#nc-app{{display:flex;height:100vh;height:100dvh}}

/* Brand Panel (desktop) */
.nc-brand{{
  width:280px;flex-shrink:0;background:var(--green);
  display:flex;flex-direction:column;padding:32px 28px;position:relative;overflow:hidden;
}}
.nc-brand__top{{display:flex;flex-direction:column;align-items:flex-start;text-align:left;margin-bottom:0;gap:10px}}
.nc-brand__top-row{{display:flex;align-items:center;justify-content:space-between;width:100%}}
.nc-brand__logo{{height:14px;width:auto;opacity:.8;animation:ncFadeUp .8s var(--ease) both}}
.nc-brand__tagline{{font-family:var(--sans);font-weight:300;font-size:.68rem;line-height:1.6;text-align:left;color:var(--cream);opacity:.4;letter-spacing:.04em;animation:ncFadeUp .8s .12s var(--ease) both;margin-bottom:0}}
.nc-brand__nav{{display:flex;flex-direction:column;gap:2px;width:100%;margin-top:28px;animation:ncFadeUp .8s .2s var(--ease) both}}
.nc-brand__nav-item{{
  display:flex;align-items:center;gap:10px;font-family:var(--sans);font-size:.72rem;font-weight:400;
  color:rgba(249,240,226,.45);padding:10px 14px;border-radius:10px;cursor:pointer;
  transition:all .35s var(--ease);border:none;background:transparent;text-align:left;
  -webkit-tap-highlight-color:transparent;width:100%;
}}
.nc-brand__nav-item:hover{{color:var(--cream);background:rgba(249,240,226,.08)}}
.nc-brand__nav-item svg{{width:16px;height:16px;opacity:.5;flex-shrink:0}}
.nc-brand__nav-item:hover svg{{opacity:.8}}
.nc-brand__bottom{{margin-top:auto;padding-top:24px}}
.nc-brand__ctas{{display:flex;flex-direction:column;gap:8px;width:100%;animation:ncFadeUp .8s .3s var(--ease) both}}
.nc-brand__cta{{
  display:block;text-align:center;font-family:var(--sans);font-size:.64rem;font-weight:500;
  letter-spacing:.14em;text-transform:uppercase;text-decoration:none;
  padding:12px 16px;border-radius:10px;cursor:pointer;transition:all .5s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-brand__cta--p{{background:rgba(249,240,226,.12);color:var(--cream);border:none}}
.nc-brand__cta--p:hover{{background:rgba(249,240,226,.22)}}
.nc-brand__cta--s{{background:transparent;color:rgba(249,240,226,.4);border:1px solid rgba(249,240,226,.1)}}
.nc-brand__cta--s:hover{{color:var(--cream);border-color:rgba(249,240,226,.28)}}
.nc-brand__copy{{font-family:var(--sans);font-size:.58rem;color:rgba(249,240,226,.2);text-align:center;margin-top:20px;letter-spacing:.06em}}

/* Main */
.nc-main{{flex:1;display:flex;flex-direction:column;min-width:0;position:relative;overflow:hidden}}

/* HOME */
.nc-home{{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .5s var(--ease),transform .5s var(--ease),filter .5s var(--ease);z-index:5}}
.nc-home.nc-hidden{{opacity:0;transform:translateX(-20px);filter:blur(4px);pointer-events:none}}

/* Top Bar */
.nc-topbar{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:max(14px,env(safe-area-inset-top)) 24px 12px;transition:background .4s var(--ease)}}
.nc-topbar--scrolled{{background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}}
.nc-topbar__left{{display:flex;align-items:center;gap:8px}}
.nc-topbar__wordmark{{height:16px;width:auto;opacity:.5;transition:opacity .3s var(--ease);cursor:pointer}}
.nc-topbar__wordmark:hover{{opacity:.7}}
.nc-topbar__right{{display:flex;align-items:center;gap:8px}}

/* Scroll area */
.nc-home__scroll-area{{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;align-items:center}}

/* Hero */
.nc-hero{{width:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;min-height:min(340px,40vh);padding:0 28px 0;text-align:center;position:relative}}
.nc-hero__sub-wrap{{position:relative;display:inline-flex;align-items:center;gap:6px;animation:ncFadeUp .7s var(--ease) both}}
.nc-hero__sub{{font-family:var(--sans);font-weight:300;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--g35);margin-bottom:12px}}
.nc-hero__leaf{{position:absolute;right:-32px;top:-6px;width:22px;height:22px;pointer-events:none;animation:ncLeafSway 3.5s ease-in-out infinite;transform-origin:70% 90%}}
.nc-hero__leaf svg{{width:100%;height:100%}}
@keyframes ncLeafSway{{
  0%{{transform:rotate(-5deg) scale(1)}}
  25%{{transform:rotate(8deg) scale(1.03)}}
  50%{{transform:rotate(-3deg) scale(.98)}}
  75%{{transform:rotate(6deg) scale(1.02)}}
  100%{{transform:rotate(-5deg) scale(1)}}
}}
.nc-hero__greeting{{font-family:var(--sans);font-size:clamp(1.4rem,3.5vw,1.8rem);font-weight:300;color:var(--green);line-height:1.5;max-width:520px;margin-bottom:24px;animation:ncFadeUp .7s .08s var(--ease) both}}
.nc-hero__input-wrap{{width:100%;max-width:520px;animation:ncFadeUp .7s .16s var(--ease) both}}
.nc-hero__scroll-hint{{display:none}}

/* Home Input */
.nc-home__form{{display:flex;align-items:center;gap:8px;background:var(--white);border:none;border-radius:28px;padding:5px 5px 5px 22px;transition:box-shadow .5s var(--ease);box-shadow:var(--shadow-s)}}
.nc-home__form:focus-within{{box-shadow:var(--shadow-m)}}
.nc-home__input{{flex:1;border:none;background:transparent;color:var(--green);font-family:inherit;font-size:16px;font-weight:400;outline:none;padding:13px 0}}
.nc-home__input::placeholder{{color:var(--g35);font-weight:300}}

/* Topic pills */
.nc-topics{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;width:100%;max-width:580px;padding:0 28px;margin-top:16px;animation:ncFadeUp .7s .24s var(--ease) both}}
.nc-topics__pill{{
  font-family:var(--sans);font-size:.78rem;font-weight:400;color:var(--g50);
  background:var(--g03);border:none;border-radius:22px;
  padding:12px 22px;cursor:pointer;transition:all .35s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-topics__pill:hover{{color:var(--green);background:var(--g06)}}
.nc-topics__pill:active{{transform:scale(.96);transition-duration:.12s}}
.nc-topics__pill--primary{{color:var(--green);background:var(--g06);font-weight:500}}
.nc-topics__pill--primary:hover{{background:var(--g12)}}

/* Sections */
.nc-section{{width:100%;max-width:720px;padding:0 28px;margin-top:28px}}
.nc-section__title{{font-family:var(--sans);font-weight:400;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--g35);margin-bottom:20px;padding-left:4px}}

/* Product Cards v2 */
.nc-products-grid{{display:flex;gap:16px;overflow-x:auto;-webkit-overflow-scrolling:touch;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}}
.nc-products-grid::-webkit-scrollbar{{display:none}}
.nc-products-grid>.nc-pcard-v2{{min-width:260px;max-width:300px;flex-shrink:0;scroll-snap-align:start}}
.nc-pcard-v2{{background:var(--white);border:none;border-radius:20px;overflow:hidden;cursor:pointer;transition:all .5s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.nc-pcard-v2:hover{{box-shadow:var(--shadow-m)}}
.nc-pcard-v2:active{{transform:scale(.98);transition-duration:.12s}}
.nc-pcard-v2__visual{{width:100%;height:140px;position:relative;overflow:hidden}}
.nc-pcard-v2__blob{{position:absolute;width:100px;height:80px;bottom:-10px;right:20px;border-radius:60% 40% 50% 50%;background:rgba(255,255,255,.12)}}
.nc-pcard-v2__body{{padding:22px 24px 24px}}
.nc-pcard-v2__grade{{font-family:var(--sans);font-size:.58rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--g35);margin-bottom:8px}}
.nc-pcard-v2__name{{font-family:var(--sans);font-weight:400;font-size:1.2rem;color:var(--green);letter-spacing:.01em;line-height:1.3;transition:color .5s var(--ease)}}
.nc-pcard-v2:hover .nc-pcard-v2__name{{color:var(--g70)}}
.nc-pcard-v2__desc{{font-weight:300;font-size:.76rem;color:var(--g50);margin-top:8px;line-height:1.65}}
.nc-pcard-v2__footer{{display:flex;align-items:center;justify-content:space-between;margin-top:16px}}
.nc-pcard-v2__price{{font-weight:300;font-size:.72rem;color:var(--g35);letter-spacing:.04em}}
.nc-pcard-v2__cta{{font-family:var(--sans);font-size:.68rem;font-weight:400;color:var(--g35);transition:color .3s var(--ease)}}
.nc-pcard-v2:hover .nc-pcard-v2__cta{{color:var(--green)}}

/* Recipe Cards v2 */
.nc-recipes-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.nc-rcard-v2{{background:var(--white);border:none;border-radius:18px;padding:22px 20px;cursor:pointer;transition:all .5s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s);display:flex;flex-direction:column}}
.nc-rcard-v2:hover{{box-shadow:var(--shadow-m)}}
.nc-rcard-v2:active{{transform:scale(.97);transition-duration:.12s}}
.nc-rcard-v2__emoji{{font-size:1.6rem;margin-bottom:14px;line-height:1}}
.nc-rcard-v2__name{{font-family:var(--sans);font-weight:400;font-size:.95rem;color:var(--green);letter-spacing:.01em;line-height:1.3;transition:color .5s var(--ease)}}
.nc-rcard-v2:hover .nc-rcard-v2__name{{color:var(--g70)}}
.nc-rcard-v2__desc{{font-weight:300;font-size:.68rem;color:var(--g50);line-height:1.6;margin-top:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}

/* Invite section */
.nc-invite{{background:var(--g03);border-radius:24px;padding:36px 28px;text-align:center}}
.nc-invite__headline{{font-family:var(--sans);font-weight:300;font-size:1.15rem;color:var(--green);line-height:1.5;margin-bottom:12px}}
.nc-invite__body{{font-size:.8rem;font-weight:300;color:var(--g50);line-height:1.65;margin-bottom:24px}}
.nc-invite__btn{{
  font-family:var(--sans);font-size:.72rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;
  background:var(--green);color:var(--cream);border:none;border-radius:24px;
  padding:14px 28px;cursor:pointer;transition:all .35s var(--ease);
  -webkit-tap-highlight-color:transparent;
}}
.nc-invite__btn:hover{{opacity:.85}}
.nc-invite__btn:active{{transform:scale(.96);transition-duration:.12s}}
.nc-invite__btn:disabled{{background:var(--g12);color:var(--g35);cursor:default;transform:none}}
.nc-invite__counter{{font-size:.68rem;font-weight:300;color:var(--g35);margin-top:14px}}
.nc-invite__done{{font-family:var(--sans);font-weight:300;font-size:.85rem;color:var(--g35);line-height:1.6}}

/* Home footer */
.nc-home__links{{display:flex;align-items:center;gap:24px;margin-top:36px;margin-bottom:max(36px,env(safe-area-inset-bottom));animation:ncFadeUp .7s .4s var(--ease) both}}
.nc-home__link{{font-size:.64rem;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--g20);text-decoration:none;transition:color .4s var(--ease)}}
.nc-home__link:hover{{color:var(--g50)}}
.nc-home__dot{{width:3px;height:3px;border-radius:50%;background:var(--g12)}}

/* Language toggle — iOS segmented control */
.nc-lang-toggle{{display:flex;background:var(--g06);border-radius:9px;padding:2px;border:none;position:relative}}
.nc-lang-btn{{
  font-family:var(--sans);font-size:.66rem;font-weight:500;letter-spacing:.08em;
  padding:6px 14px;border:none;cursor:pointer;transition:all .35s var(--ease);
  -webkit-tap-highlight-color:transparent;background:transparent;color:var(--g35);
  border-radius:7px;position:relative;z-index:1;
}}
.nc-lang-btn.active{{background:var(--white);color:var(--green);box-shadow:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04)}}
.nc-brand .nc-lang-toggle{{background:rgba(249,240,226,.1)}}
.nc-brand .nc-lang-btn{{color:rgba(249,240,226,.35);font-size:.6rem;padding:5px 10px}}
.nc-brand .nc-lang-btn.active{{background:rgba(249,240,226,.18);color:var(--cream);box-shadow:none}}

/* Overlay backdrop */
.nc-overlay-bg{{position:fixed;inset:0;background:rgba(0,0,0,.3);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);opacity:0;pointer-events:none;transition:opacity .35s var(--ease);z-index:40}}
.nc-overlay-bg--active{{opacity:1;pointer-events:auto}}

/* Mobile drawer */
.nc-drawer-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.35);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);opacity:0;pointer-events:none;transition:opacity .3s var(--ease);z-index:50}}
.nc-drawer-overlay--open{{opacity:1;pointer-events:auto}}
.nc-drawer{{position:fixed;top:0;left:0;bottom:0;width:280px;max-width:80vw;background:var(--green);transform:translateX(-100%);transition:transform .35s var(--ease);z-index:51;display:flex;flex-direction:column;padding:0}}
.nc-drawer--open{{transform:translateX(0)}}
.nc-drawer__header{{display:flex;align-items:center;justify-content:space-between;padding:max(16px,env(safe-area-inset-top)) 20px 12px}}
.nc-drawer__close{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;color:var(--cream);opacity:.5;cursor:pointer;-webkit-tap-highlight-color:transparent}}
.nc-drawer__close:hover{{opacity:.8}}
.nc-drawer__lang{{}}
.nc-drawer .nc-lang-toggle{{background:rgba(249,240,226,.1)}}
.nc-drawer .nc-lang-btn{{color:rgba(249,240,226,.35);font-size:.6rem;padding:5px 10px}}
.nc-drawer .nc-lang-btn.active{{background:rgba(249,240,226,.18);color:var(--cream);box-shadow:none}}
.nc-drawer__nav{{display:flex;flex-direction:column;gap:2px;padding:8px 12px;flex:1}}
.nc-drawer__nav-item{{
  display:flex;align-items:center;gap:10px;font-family:var(--sans);font-size:.76rem;font-weight:400;
  color:rgba(249,240,226,.5);padding:12px 16px;border-radius:10px;cursor:pointer;
  transition:all .35s var(--ease);border:none;background:transparent;text-align:left;
  -webkit-tap-highlight-color:transparent;width:100%;
}}
.nc-drawer__nav-item:hover{{color:var(--cream);background:rgba(249,240,226,.08)}}
.nc-drawer__nav-item svg{{width:16px;height:16px;opacity:.5;flex-shrink:0}}
.nc-drawer__bottom{{padding:16px 20px max(16px,env(safe-area-inset-bottom));margin-top:auto}}
.nc-drawer__ctas{{display:flex;flex-direction:column;gap:8px}}
.nc-drawer__cta{{
  display:block;text-align:center;font-family:var(--sans);font-size:.64rem;font-weight:500;
  letter-spacing:.14em;text-transform:uppercase;text-decoration:none;
  padding:12px 16px;border-radius:10px;cursor:pointer;transition:all .5s var(--ease);
}}
.nc-drawer__cta--p{{background:rgba(249,240,226,.12);color:var(--cream);border:none}}
.nc-drawer__cta--p:hover{{background:rgba(249,240,226,.22)}}
.nc-drawer__cta--s{{background:transparent;color:rgba(249,240,226,.4);border:1px solid rgba(249,240,226,.1)}}
.nc-drawer__cta--s:hover{{color:var(--cream);border-color:rgba(249,240,226,.28)}}
.nc-hamburger{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;cursor:pointer;-webkit-tap-highlight-color:transparent;padding:0}}
.nc-hamburger svg{{width:20px;height:20px;color:var(--g50)}}

/* Invite sheet */
.nc-invite-sheet{{position:fixed;bottom:0;left:0;right:0;background:var(--white);border-radius:24px 24px 0 0;padding:28px 28px max(28px,env(safe-area-inset-bottom));transform:translateY(100%);transition:transform .4s var(--ease);z-index:41;text-align:center;max-height:70vh}}
.nc-invite-sheet--active{{transform:translateY(0)}}
.nc-invite-sheet__handle{{width:32px;height:4px;border-radius:2px;background:var(--g12);margin:0 auto 24px}}
.nc-invite-sheet__headline{{font-family:var(--sans);font-weight:300;font-size:1.15rem;color:var(--green);margin-bottom:12px}}
.nc-invite-sheet__body{{font-size:.82rem;font-weight:300;color:var(--g50);line-height:1.65;margin-bottom:28px;max-width:320px;margin-left:auto;margin-right:auto}}
.nc-invite-sheet__primary{{
  font-family:var(--sans);font-size:.72rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;
  background:var(--green);color:var(--cream);border:none;border-radius:24px;
  padding:14px 32px;cursor:pointer;transition:all .35s var(--ease);display:block;width:100%;max-width:280px;margin:0 auto;
  -webkit-tap-highlight-color:transparent;
}}
.nc-invite-sheet__primary:hover{{opacity:.85}}
.nc-invite-sheet__primary:active{{transform:scale(.96);transition-duration:.12s}}
.nc-invite-sheet__secondary{{display:block;font-family:var(--sans);font-size:.72rem;font-weight:300;color:var(--g35);background:none;border:none;cursor:pointer;margin:16px auto 0;transition:color .3s var(--ease);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--g12);-webkit-tap-highlight-color:transparent}}
.nc-invite-sheet__secondary:hover{{color:var(--green);text-decoration-color:var(--green)}}

/* Coupon overlay */
.nc-coupon-overlay{{position:fixed;inset:0;background:var(--cream);z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 28px;opacity:0;pointer-events:none;transition:opacity .4s var(--ease),transform .4s var(--ease);transform:scale(.96)}}
.nc-coupon-overlay--active{{opacity:1;pointer-events:auto;transform:scale(1)}}
.nc-coupon-overlay__mark{{width:36px;height:36px;opacity:.65;margin-bottom:32px}}
.nc-coupon-overlay__headline{{font-family:var(--sans);font-weight:300;font-size:1.3rem;color:var(--green);text-align:center;line-height:1.5;max-width:300px;margin-bottom:14px}}
.nc-coupon-overlay__body{{font-size:.82rem;font-weight:300;color:var(--g50);text-align:center;line-height:1.65;max-width:300px;margin-bottom:32px}}
.nc-coupon-overlay__card{{background:var(--white);border:2px dashed var(--g12);border-radius:16px;padding:28px 32px;text-align:center;width:100%;max-width:320px;margin-bottom:32px}}
.nc-coupon-overlay__code{{font-family:var(--sans);font-weight:500;font-size:1.2rem;letter-spacing:.2em;color:var(--green);margin-bottom:8px}}
.nc-coupon-overlay__discount{{font-size:.78rem;font-weight:300;color:var(--g50)}}
.nc-coupon-overlay__actions{{display:flex;gap:12px;margin-top:20px;justify-content:center}}
.nc-coupon-overlay__copy{{
  font-family:var(--sans);font-size:.72rem;font-weight:400;
  background:var(--g06);color:var(--green);border:none;border-radius:20px;
  padding:10px 20px;cursor:pointer;transition:all .35s var(--ease);-webkit-tap-highlight-color:transparent;
}}
.nc-coupon-overlay__copy:hover{{background:var(--g12)}}
.nc-coupon-overlay__shop{{
  font-family:var(--sans);font-size:.72rem;font-weight:500;
  background:var(--green);color:var(--cream);border:none;border-radius:20px;
  padding:10px 20px;cursor:pointer;transition:all .35s var(--ease);text-decoration:none;display:inline-block;-webkit-tap-highlight-color:transparent;
}}
.nc-coupon-overlay__shop:hover{{opacity:.85}}
.nc-coupon-overlay__dismiss{{font-family:var(--sans);font-size:.78rem;font-weight:300;color:var(--g35);background:none;border:none;cursor:pointer;transition:color .3s var(--ease);-webkit-tap-highlight-color:transparent}}
.nc-coupon-overlay__dismiss:hover{{color:var(--green)}}

/* Toast */
.nc-toast{{position:fixed;bottom:max(24px,env(safe-area-inset-bottom));left:50%;transform:translateX(-50%);background:var(--green);color:var(--cream);font-family:var(--sans);font-size:.76rem;font-weight:400;padding:12px 24px;border-radius:12px;z-index:60;animation:ncToastIn .35s var(--ease) both;pointer-events:none}}
.nc-toast--exit{{opacity:0;transition:opacity .3s var(--ease)}}
@keyframes ncToastIn{{from{{opacity:0;transform:translateX(-50%) translateY(16px)}}to{{opacity:1;transform:translateX(-50%) translateY(0)}}}}

/* CHAT */
.nc-chat{{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .5s var(--ease),transform .5s var(--ease),filter .5s var(--ease);z-index:4}}
.nc-chat.nc-hidden{{opacity:0;transform:translateX(20px);filter:blur(4px);pointer-events:none}}

/* Header */
.nc-header{{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 24px;background:rgba(249,240,226,.88);
  -webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px);
  border-bottom:none;flex-shrink:0;z-index:10;
}}
.nc-header__left{{display:flex;align-items:center;gap:12px}}
.nc-back{{display:none;background:none;border:none;color:var(--g50);cursor:pointer;padding:6px 10px 6px 0;-webkit-tap-highlight-color:transparent;transition:color .3s var(--ease)}}
.nc-back:hover{{color:var(--green)}}
.nc-header__logo{{height:16px;opacity:.75;display:none}}
.nc-header__title{{font-family:var(--sans);font-weight:400;font-size:.82rem;letter-spacing:.06em;text-transform:none;color:var(--g35)}}
.nc-header__dot{{width:6px;height:6px;border-radius:50%;background:var(--green);opacity:.5;animation:ncBreathe 4s ease-in-out infinite}}
@keyframes ncBreathe{{0%,100%{{opacity:.5;transform:scale(1)}}50%{{opacity:.2;transform:scale(.8)}}}}

/* Messages */
.nc-messages{{flex:1;overflow-y:auto;padding:24px 24px 16px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth;max-width:760px;width:100%;margin:0 auto}}
.nc-messages::-webkit-scrollbar{{width:0;display:none}}
.nc-banner{{text-align:center;padding:10px 16px;margin:0 auto 24px;font-family:var(--sans);font-size:.74rem;font-weight:300;color:var(--g20);letter-spacing:.03em}}
.nc-msg{{display:flex;flex-direction:column;animation:ncMsgIn .5s var(--ease) both}}
@keyframes ncMsgIn{{from{{opacity:0;transform:translateY(8px) scale(.98)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
.nc-msg--bot{{align-items:flex-start;padding-right:48px}}
.nc-msg--bot .nc-msg__bubble{{background:var(--white);border-radius:20px 20px 20px 6px;padding:14px 18px;font-size:.88rem;font-weight:400;line-height:1.55;color:var(--green);box-shadow:var(--shadow-s)}}
.nc-msg__bubble a{{color:var(--green);font-weight:500;text-decoration:underline;text-decoration-color:var(--g12);text-underline-offset:3px;transition:text-decoration-color .3s}}
.nc-msg__bubble a:hover{{text-decoration-color:var(--green)}}
.nc-msg__bubble strong{{font-weight:600}}
.nc-msg__bubble ul,.nc-msg__bubble ol{{margin:4px 0 2px;padding-left:18px;list-style:none}}
.nc-msg__bubble li{{margin:1px 0;position:relative;padding-left:2px}}
.nc-msg__bubble li::before{{content:'';position:absolute;left:-12px;top:.55em;width:4px;height:4px;border-radius:50%;background:var(--green);opacity:.45}}
.nc-msg--user{{align-items:flex-end;padding-left:48px;margin-top:4px}}
.nc-msg--user .nc-msg__bubble{{background:var(--green);color:var(--cream);border-radius:20px 20px 6px 20px;padding:14px 20px;font-size:.88rem;font-weight:400;line-height:1.7;box-shadow:0 2px 8px rgba(64,101,70,.15)}}
.nc-msg--bot+.nc-msg--user,.nc-msg--user+.nc-msg--bot{{margin-top:16px}}
.nc-msg__meta{{margin-top:6px;padding-left:2px}}
.nc-msg__time{{font-size:.58rem;color:var(--g20);letter-spacing:.03em}}
.nc-suggestions{{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}}
.nc-suggestion{{font-family:inherit;font-size:.76rem;font-weight:400;color:var(--green);background:var(--g03);border:none;border-radius:20px;padding:10px 16px;cursor:pointer;transition:all .4s var(--ease);text-align:left;line-height:1.4;-webkit-tap-highlight-color:transparent}}
.nc-suggestion:hover{{background:var(--g06)}}
.nc-suggestion:active{{background:var(--g12);transform:scale(.97);transition-duration:.12s}}
.nc-choices{{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}}
.nc-choice-btn{{font-family:inherit;font-size:.88rem;font-weight:500;color:var(--green);background:var(--cream);border:1.5px solid var(--green);border-radius:20px;padding:8px 18px;cursor:pointer;transition:all .25s var(--ease);-webkit-tap-highlight-color:transparent}}
.nc-choice-btn:hover{{background:var(--green);color:#fff}}
.nc-choice-btn--selected{{background:var(--green);color:#fff}}
.nc-choice-btn--disabled{{opacity:.45;pointer-events:none}}
.nc-product-carousel{{margin-top:12px;display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding:2px 0 6px;scrollbar-width:none}}
.nc-product-carousel::-webkit-scrollbar{{display:none}}
.nc-product-card{{flex:0 0 150px;scroll-snap-align:start;border-radius:14px;background:var(--white);box-shadow:var(--shadow-s);overflow:hidden;cursor:pointer;transition:all .3s var(--ease);text-decoration:none;color:inherit;display:block}}
.nc-product-card:hover{{box-shadow:var(--shadow-m);transform:translateY(-2px)}}
.nc-product-card__img{{width:100%;height:110px;object-fit:cover;background:linear-gradient(145deg,var(--g03),var(--g06));display:block}}
.nc-product-card__body{{padding:10px 12px}}
.nc-product-card__name{{font-size:.72rem;font-weight:500;color:var(--green);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.nc-product-card__price{{font-size:.68rem;font-weight:600;color:var(--g50);margin-top:4px}}
.nc-product-card__cta{{font-size:.62rem;font-weight:500;color:var(--green);margin-top:6px;letter-spacing:.04em}}
.nc-product-card--loading .nc-product-card__img{{background:linear-gradient(90deg,var(--g03) 25%,var(--g06) 50%,var(--g03) 75%);background-size:200% 100%;animation:ncShimmer 1.5s infinite}}
@keyframes ncShimmer{{from{{background-position:200% 0}}to{{background-position:-200% 0}}}}
.nc-msg__sources{{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}}
.nc-msg__source{{font-size:.68rem;color:var(--green);text-decoration:none;background:var(--g03);border:none;border-radius:10px;padding:8px 14px;transition:background .4s var(--ease);-webkit-tap-highlight-color:transparent}}
.nc-msg__source:hover{{background:var(--g06)}}
.nc-typing .nc-msg__bubble{{display:flex;gap:6px;align-items:center;padding:18px 22px!important;min-height:44px;box-shadow:var(--shadow-s)}}
.nc-typing .nc-msg__bubble span{{width:5px;height:5px;background:var(--g20);border-radius:50%;display:inline-block;animation:ncTypingBreath 1.8s ease-in-out infinite}}
.nc-typing .nc-msg__bubble span:nth-child(2){{animation-delay:.2s}}
.nc-typing .nc-msg__bubble span:nth-child(3){{animation-delay:.4s}}
@keyframes ncTypingBreath{{0%,60%,100%{{opacity:.15;transform:scale(.8)}}30%{{opacity:.6;transform:scale(1)}}}}
.nc-typing__label{{font-size:.6rem;color:var(--g20);padding-left:2px;margin-top:4px;font-style:italic}}
.nc-quick{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.nc-quick__btn{{font-family:inherit;font-size:.76rem;font-weight:400;color:var(--green);background:var(--white);border:none;border-radius:20px;padding:10px 18px;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:all .4s var(--ease);box-shadow:var(--shadow-s)}}
.nc-quick__btn:hover{{box-shadow:var(--shadow-m);transform:translateY(-1px)}}
.nc-quick__btn:active{{transform:scale(.96);transition-duration:.12s}}

/* Input */
.nc-input-area{{padding:12px 24px 16px;flex-shrink:0;max-width:760px;width:100%;margin:0 auto}}
.nc-form{{display:flex;align-items:center;gap:8px;background:var(--white);border:none;border-radius:28px;padding:5px 5px 5px 22px;transition:box-shadow .5s var(--ease);box-shadow:var(--shadow-s)}}
.nc-form:focus-within{{box-shadow:var(--shadow-m)}}
.nc-input{{flex:1;border:none;background:transparent;color:var(--green);font-family:inherit;font-size:.88rem;font-weight:400;outline:none;padding:11px 0}}
.nc-input::placeholder{{color:var(--g35);font-weight:300}}
.nc-send{{width:36px;height:36px;border-radius:50%;border:none;background:var(--green);color:var(--cream);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent;transition:all .4s var(--ease)}}
.nc-send:hover{{opacity:.85;transform:scale(1.04)}}
.nc-send:active{{transform:scale(.88);transition-duration:.1s}}
.nc-send svg{{width:13px;height:13px}}

/* Footer */
.nc-footer{{display:flex;align-items:center;justify-content:center;gap:16px;padding:4px 24px max(8px,env(safe-area-inset-bottom));flex-shrink:0}}
.nc-footer__link{{font-size:.58rem;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--g20);text-decoration:none;transition:color .4s var(--ease)}}
.nc-footer__link:hover{{color:var(--g50)}}
.nc-footer__dot{{width:2px;height:2px;border-radius:50%;background:var(--g12)}}

@keyframes ncFadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}

@media(min-width:900px){{.nc-topbar{{display:none}}.nc-drawer,.nc-drawer-overlay{{display:none}}.nc-products-grid{{flex-wrap:wrap;overflow-x:visible;scroll-snap-type:none}}.nc-products-grid>.nc-pcard-v2{{min-width:0;max-width:none;flex:1 1 calc(33.333% - 12px)}}.nc-pcard-v2__visual{{height:120px}}.nc-recipes-grid{{grid-template-columns:repeat(3,1fr)}}.nc-hero{{min-height:min(320px,38vh)}}.nc-invite-sheet{{max-width:420px;left:50%;right:auto;transform:translateX(-50%) translateY(100%)}}.nc-invite-sheet--active{{transform:translateX(-50%) translateY(0)}}.nc-invite{{max-width:720px;margin:0 auto}}.nc-msg--bot{{padding-right:80px}}.nc-msg--user{{padding-left:80px}}}}
@media(min-width:1400px){{.nc-section{{max-width:800px}}.nc-products-grid{{gap:20px}}.nc-messages{{max-width:840px}}.nc-input-area{{max-width:840px}}}}
@media(max-width:899px){{
  .nc-brand{{display:none}}
  #nc-app{{height:100vh;height:100dvh;height:-webkit-fill-available}}
  .nc-back{{display:block}}.nc-header__logo{{display:block}}
  .nc-header{{padding:max(12px,env(safe-area-inset-top)) 18px 12px}}
  .nc-messages{{padding:18px 18px 10px;-webkit-overflow-scrolling:touch}}
  .nc-msg--bot{{padding-right:20px}}.nc-msg--user{{padding-left:44px}}
  .nc-msg--bot .nc-msg__bubble{{padding:16px 18px}}
  .nc-quick{{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;scrollbar-width:none}}
  .nc-quick::-webkit-scrollbar{{display:none}}.nc-quick__btn{{white-space:nowrap;flex-shrink:0}}
  .nc-input-area{{padding:10px 16px 6px;background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);border-top:none}}
  .nc-form{{padding:4px 4px 4px 18px}}.nc-input{{font-size:16px;padding:12px 0;min-height:44px}}.nc-send{{width:38px;height:38px}}
  .nc-footer{{padding:4px 16px max(6px,env(safe-area-inset-bottom))}}
  .nc-hero{{padding:0 22px}}.nc-hero__input-wrap{{max-width:400px}}
  .nc-topics{{padding:0 22px}}.nc-section{{padding:0 22px}}
  .nc-invite-sheet{{padding:24px 22px max(24px,env(safe-area-inset-bottom))}}
}}
@media(max-width:430px){{
  .nc-messages{{padding:14px 12px 8px}}
  .nc-msg--bot .nc-msg__bubble,.nc-msg--user .nc-msg__bubble{{font-size:.86rem;padding:14px 16px}}
  .nc-input-area{{padding:8px 12px 4px}}.nc-send{{width:36px;height:36px}}
  .nc-footer{{padding:3px 12px max(4px,env(safe-area-inset-bottom))}}
  .nc-hero{{padding:0 18px}}.nc-hero__greeting{{font-size:1.45rem}}
  .nc-topics{{padding:0 18px;gap:8px}}.nc-topics__pill{{padding:10px 18px;font-size:.74rem}}
  .nc-section{{padding:0 18px;margin-top:max(32px,4vh)}}
  .nc-recipes-grid{{gap:10px}}.nc-rcard-v2{{padding:18px 16px}}
  .nc-pcard-v2__visual{{height:110px}}.nc-pcard-v2__body{{padding:18px 20px 20px}}
  .nc-invite{{padding:28px 22px}}
}}
</style>
</head>
<body>
<div id="nc-app">
  <aside class="nc-brand">
    <div class="nc-brand__top">
      <div class="nc-brand__top-row">
        <img class="nc-brand__logo" src="data:image/png;base64,{_LOGO_WM_WHITE_B64}" alt="NAKAI" />
        <div class="nc-lang-toggle" id="nc-lang-brand">
          <button class="nc-lang-btn active" data-lang="en">EN</button>
          <button class="nc-lang-btn" data-lang="ja">JA</button>
        </div>
      </div>
      <p class="nc-brand__tagline">Enriching the present.</p>
    </div>
    <nav class="nc-brand__nav">
      <button class="nc-brand__nav-item" id="nc-nav-home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg>Home</button>
      <button class="nc-brand__nav-item" id="nc-nav-find"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><span id="nc-nav-find-label">Find Your Matcha</span></button>
      <button class="nc-brand__nav-item" id="nc-nav-brew"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg><span id="nc-nav-brew-label">Barista Guide</span></button>
      <button class="nc-brand__nav-item" id="nc-nav-recipes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg><span id="nc-nav-recipes-label">Recipes</span></button>
      <button class="nc-brand__nav-item" id="nc-nav-faq"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg><span id="nc-nav-faq-label">About Matcha</span></button>
    </nav>
    <div class="nc-brand__bottom">
      <div class="nc-brand__ctas">
        <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-brand__cta nc-brand__cta--p">Shop NAKAI</a>
        <a href="/wholesale" class="nc-brand__cta nc-brand__cta--s">Wholesale</a>
      </div>
      <p class="nc-brand__copy">&copy; NAKAI Matcha</p>
    </div>
  </aside>
  <div class="nc-main">
    <!-- HOME -->
    <div class="nc-home" id="nc-home">
      <div class="nc-topbar" id="nc-topbar">
        <div class="nc-topbar__left">
          <button class="nc-hamburger" id="nc-hamburger" aria-label="Menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
          </button>
          <img class="nc-topbar__wordmark" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" id="nc-topbar-mark" />
        </div>
        <div class="nc-topbar__right">
          <div class="nc-lang-toggle" id="nc-lang-home">
            <button class="nc-lang-btn active" data-lang="en">EN</button>
            <button class="nc-lang-btn" data-lang="ja">JA</button>
          </div>
        </div>
      </div>
      <div class="nc-home__scroll-area" id="nc-home-scroll">
        <div class="nc-hero">
          <div class="nc-hero__sub-wrap">
            <p class="nc-hero__sub" id="nc-home-sub">Your private matcha concierge</p>
            <div class="nc-hero__leaf" aria-hidden="true"><svg viewBox="0 0 48 64" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 2C14 12 6 28 10 48c2 8 8 12 14 14" stroke="#8a8a6a" stroke-width="1.2" fill="none"/><path d="M24 2c10 10 18 26 14 46-2 8-8 12-14 14" stroke="#8a8a6a" stroke-width="1.2" fill="none"/><path d="M24 2v60" stroke="#c4a240" stroke-width="2.2" stroke-linecap="round"/><path d="M24 16c-5 3-9 8-11 14M24 26c-6 4-10 10-12 16M24 36c-4 3-7 8-9 12" stroke="#8a8a6a" stroke-width=".8" fill="none"/><path d="M24 16c5 3 9 8 11 14M24 26c6 4 10 10 12 16M24 36c4 3 7 8 9 12" stroke="#8a8a6a" stroke-width=".8" fill="none"/></svg></div>
          </div>
          <h1 class="nc-hero__greeting" id="nc-home-greeting">Shall we talk about matcha?</h1>
          <div class="nc-hero__input-wrap">
            <form class="nc-home__form" id="nc-home-form">
              <input type="text" class="nc-home__input" id="nc-home-input" autocomplete="off" maxlength="500" />
              <button type="submit" class="nc-send" aria-label="Send">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
              </button>
            </form>
          </div>
          <div class="nc-hero__scroll-hint" id="nc-scroll-hint">
            <svg width="16" height="10" viewBox="0 0 16 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 1l7 7 7-7"/></svg>
          </div>
        </div>
        <div class="nc-topics" id="nc-topics">
          <button class="nc-topics__pill nc-topics__pill--primary" id="nc-t-find">Find Your Matcha</button>
          <button class="nc-topics__pill" id="nc-t-brew">Barista Guide</button>
          <button class="nc-topics__pill" id="nc-t-product">Recipes</button>
          <button class="nc-topics__pill" id="nc-t-faq">About Matcha</button>
        </div>
        <div class="nc-section">
          <h2 class="nc-section__title" id="nc-sec-products">Our Matcha</h2>
          <div class="nc-products-grid" id="nc-product-cards"></div>
        </div>
        <div class="nc-section">
          <h2 class="nc-section__title" id="nc-sec-recipes">Recipes &amp; Guides</h2>
          <div class="nc-recipes-grid" id="nc-recipe-cards"></div>
        </div>
        <div class="nc-section">
          <div class="nc-invite" id="nc-invite"></div>
        </div>
        <div class="nc-home__links">
          <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-home__link" id="nc-h-shop">Shop</a>
          <span class="nc-home__dot"></span>
          <a href="mailto:info@s-natural.xyz?subject=Wholesale%20Inquiry" class="nc-home__link" id="nc-h-ws">Wholesale</a>
        </div>
      </div>
    </div>
    <!-- Overlays -->
    <div class="nc-drawer-overlay" id="nc-drawer-overlay"></div>
    <nav class="nc-drawer" id="nc-drawer">
      <div class="nc-drawer__header">
        <div class="nc-drawer__lang">
          <div class="nc-lang-toggle" id="nc-lang-drawer">
            <button class="nc-lang-btn active" data-lang="en">EN</button>
            <button class="nc-lang-btn" data-lang="ja">JA</button>
          </div>
        </div>
        <button class="nc-drawer__close" id="nc-drawer-close" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>
      </div>
      <div class="nc-drawer__nav">
        <button class="nc-drawer__nav-item" id="nc-dnav-home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg><span>Home</span></button>
        <button class="nc-drawer__nav-item" id="nc-dnav-find"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><span id="nc-dnav-find-label">Find Your Matcha</span></button>
        <button class="nc-drawer__nav-item" id="nc-dnav-brew"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg><span id="nc-dnav-brew-label">Barista Guide</span></button>
        <button class="nc-drawer__nav-item" id="nc-dnav-recipes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg><span id="nc-dnav-recipes-label">Recipes</span></button>
        <button class="nc-drawer__nav-item" id="nc-dnav-faq"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg><span id="nc-dnav-faq-label">About Matcha</span></button>
      </div>
      <div class="nc-drawer__bottom">
        <div class="nc-drawer__ctas">
          <a href="https://nakaimatcha.com/" target="_blank" rel="noopener" class="nc-drawer__cta nc-drawer__cta--p">Shop NAKAI</a>
          <a href="/wholesale" class="nc-drawer__cta nc-drawer__cta--s">Wholesale</a>
        </div>
      </div>
    </nav>
    <div class="nc-overlay-bg" id="nc-overlay-bg"></div>
    <div class="nc-invite-sheet" id="nc-invite-sheet">
      <div class="nc-invite-sheet__handle"></div>
      <h2 class="nc-invite-sheet__headline" id="nc-sheet-title">Share a matcha moment</h2>
      <p class="nc-invite-sheet__body" id="nc-sheet-body">Your friend will receive a special welcome coupon for NAKAI matcha.</p>
      <button class="nc-invite-sheet__primary" id="nc-sheet-share">Share invite link</button>
      <button class="nc-invite-sheet__secondary" id="nc-sheet-copy">or copy link manually</button>
    </div>
    <div class="nc-coupon-overlay" id="nc-coupon-overlay">
      <img class="nc-coupon-overlay__mark" src="data:image/png;base64,{_LOGO_ICON_BLACK_B64}" alt="NAKAI" />
      <h1 class="nc-coupon-overlay__headline" id="nc-coupon-title">A friend sent you a matcha moment</h1>
      <p class="nc-coupon-overlay__body" id="nc-coupon-body">Welcome to NAKAI. Enjoy a special gift on your first matcha order.</p>
      <div class="nc-coupon-overlay__card">
        <div class="nc-coupon-overlay__code" id="nc-coupon-code">MATCHA15</div>
        <div class="nc-coupon-overlay__discount" id="nc-coupon-discount">15% off your first order</div>
        <div class="nc-coupon-overlay__actions">
          <button class="nc-coupon-overlay__copy" id="nc-coupon-copy">Copy code</button>
          <a href="https://nakaimatcha.com" target="_blank" rel="noopener" class="nc-coupon-overlay__shop" id="nc-coupon-shop">Shop now</a>
        </div>
      </div>
      <button class="nc-coupon-overlay__dismiss" id="nc-coupon-dismiss">Explore the concierge</button>
    </div>
    <!-- CHAT -->
    <div class="nc-chat nc-hidden" id="nc-chat">
      <header class="nc-header">
        <div class="nc-header__left">
          <button class="nc-back" id="nc-back" aria-label="Back"><svg width="10" height="18" viewBox="0 0 10 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 1L1 9l8 8"/></svg></button>
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
        <a href="/wholesale" class="nc-footer__link" id="nc-f-ws">Wholesale</a>
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
  var SESSION_ID=(function(){{var id=localStorage.getItem('nakai_session_id');if(!id){{id=crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c){{var r=Math.random()*16|0;return(c==='x'?r:(r&0x3|0x8)).toString(16)}});localStorage.setItem('nakai_session_id',id)}}return id}})();

  var i18n={{
    en:{{
      greeting:"Hi there! I'm your matcha concierge. Whether you're new to matcha or a daily drinker, I'm here to help you find the perfect cup.",
      placeholder:'Ask about matcha...',
      typing:'Thinking...',
      banner:'AI-powered answers based on our matcha expertise',
      q1:'Find your matcha',q1m:"I'd like to find the right matcha for me. Can you help?",
      q2:'Make a matcha latte',q2m:'How do I make the perfect matcha latte at home?',
      q3:'Why NAKAI?',q3m:'What makes NAKAI matcha different from other matcha brands?',
      q4:'Health benefits',q4m:'What are the health benefits of drinking matcha daily?',
      error:"Connection issue. Please try again.",
      sub:'AI Matcha Concierge',homeGreeting:'What can I help you with?',
      findCta:'Find Your Matcha',
      mBrew:'Barista Guide',mProduct:'NAKAI Matcha Product Recipes',mFaq:'Learn about Matcha',
      hShop:'Shop',hWs:'Wholesale',
      brewMsg:'How do I brew the perfect cup of matcha? Please include water temperature, matcha-to-water ratio, and whisking technique.',
      productMsg:'Tell me about NAKAI matcha products. What grades do you offer and what makes each one special?',
      faqMsg:'What are the most common customer questions about matcha? Give me quick answers I can use as a barista.',
      findMsg:"I'd like to find the right matcha for me. Could you ask me a few questions to help narrow it down?",
      secProducts:'Our Matcha',secRecipes:'Recipes & Guides',
      pP22:'NIJYU-NI (22)',pP22Grade:'Ceremonial Reserved',pP22Desc:'Within the Flow, Everything Exists. Quiet, effortless depth.',pP22Price:'$48',pP22Msg:'Tell me about 二十二 (22) matcha. What makes it special and how should I prepare it?',
      pP18:'JU-HACHI (18)',pP18Grade:'Specialty Grade',pP18Desc:'Meditative stillness. Four-level roasting, weightless texture.',pP18Price:'$40',pP18Msg:'Tell me about 十八 (18) matcha. What is its unique four-level roasting process?',
      pP17:'JU-NANA (17)',pP17Grade:'Specialty Grade',pP17Desc:'Layered Umami, Lasting Stillness. Dual terroir, 500kg/year.',pP17Price:'$38',pP17Msg:'Tell me about 十七 (17) matcha. What makes the dual terroir special?',
      pP16:'JU-ROKU (16)',pP16Grade:'Specialty Grade',pP16Desc:'Veil of Mist, Infinite Echo. Elegant layers of flavor.',pP16Price:'$35',pP16Msg:'Tell me about 十六 (16) matcha. What is it best for and what makes it unique?',
      pP4:'SHI (4)',pP4Grade:'Specialty Grade',pP4Desc:'Breath of Earth, Living Strength. Chocolate, nuts, berries.',pP4Price:'$30',pP4Msg:'Tell me about 四 (4) matcha. What is its story and flavor profile?',
      pPBundle:'Discovery Bundle',pPBundleGrade:'Explore NAKAI',pPBundleDesc:'Your gateway to the world of specialty matcha.',pPBundlePrice:'',pPBundleMsg:'Tell me about the Discovery Bundle. What does it include and who is it for?',
      rUsucha:'Usucha',rUsuchaDesc:'Traditional thin tea, light and frothy',rUsuchaMsg:'How do I make usucha (thin matcha tea)? Give me step-by-step instructions.',
      rKoicha:'Koicha',rKoichaDesc:'Thick tea, intense and full-bodied',rKoichaMsg:'How do I make koicha (thick matcha tea)? Give me step-by-step instructions.',
      rLatte:'Matcha Latte',rLatteDesc:'Hot or iced, the perfect everyday drink',rLatteMsg:'How do I make the perfect matcha latte? Include hot and iced variations.',
      rIced:'Iced Matcha',rIcedDesc:'Refreshing, bright, and easy to make',rIcedMsg:'How do I make iced matcha? Step by step please.',
      rAffogato:'Affogato',rAffogatoDesc:'Matcha meets vanilla ice cream',rAffogatoMsg:'How do I make a matcha affogato?',
      rBarista:'Barista Tips',rBaristaDesc:'Water temp, whisking, milk pairing',rBaristaMsg:'What are the essential barista tips for working with matcha? Cover water temperature, whisking technique, and milk pairing.',
      heroSub:'Your private matcha concierge',heroGreeting:'Discover your perfect matcha',
      tFind:'Find Your Matcha',tBrew:'Barista Guide',tProduct:'Recipes',tFaq:'About Matcha',
      pAsk:'Ask about this',
      inviteHeadline:'Share matcha with someone you love',inviteBody:'Invite a close friend and they\u2019ll receive a special matcha gift.',
      inviteBtn:'Invite a friend',inviteAllUsed:'All invites shared',
      inviteDone:'You\u2019ve shared matcha with 3 friends',inviteDoneBody:'Thank you for spreading the matcha moment.',
      sheetTitle:'Share a matcha moment',sheetBody:'Your friend will receive a special welcome coupon for NAKAI matcha.',
      sheetShare:'Share invite link',sheetCopy:'or copy link manually',
      shareTitle:'A matcha moment from a friend',shareText:'I\u2019d love for you to try NAKAI Matcha. Here\u2019s a special welcome gift.',
      couponTitle:'A friend sent you a matcha moment',couponBody:'Welcome to NAKAI. Enjoy a special gift on your first matcha order.',
      couponCode:'MATCHA15',couponDiscount:'15% off your first order',
      couponCopy:'Copy code',couponCopied:'Copied!',couponShop:'Shop now',couponDismiss:'Explore the concierge',
      toastCopied:'Link copied to clipboard',
    }},
    ja:{{
      greeting:'こんにちは！抹茶コンシェルジュです。初めての方も毎日飲む方も、あなたにぴったりの一杯を一緒に見つけましょう。',
      placeholder:'抹茶について質問する...',
      typing:'考え中...',
      banner:'AIが抹茶の専門知識に基づいて回答します',
      q1:'自分に合う抹茶',q1m:'自分に合う抹茶を探しています。いくつか質問してもらえますか？',
      q2:'抹茶ラテの作り方',q2m:'自宅で美味しい抹茶ラテを作る方法を教えてください',
      q3:'NAKAIの特別さ',q3m:'NAKAIの抹茶は他の抹茶と何が違うのですか？',
      q4:'健康効果',q4m:'抹茶を毎日飲むとどんな健康効果がありますか？',
      error:'接続に問題が発生しました。もう一度お試しください。',
      sub:'AI 抹茶コンシェルジュ',homeGreeting:'何をお手伝いしましょうか？',
      findCta:'自分に合った抹茶を探す',
      mBrew:'バリスタガイド',mProduct:'NAKAI Matcha プロダクトレシピ',mFaq:'抹茶について学ぶ',
      hShop:'ショップ',hWs:'卸売',
      brewMsg:'美味しい抹茶の点て方を教えてください。水温、抹茶と水の割合、茶筅の使い方を含めてください。',
      productMsg:'NAKAIの抹茶商品について教えてください。どんなグレードがあり、それぞれの特徴は何ですか？',
      faqMsg:'抹茶に関するお客様からのよくある質問は何ですか？バリスタとして使える簡潔な回答をお願いします。',
      findMsg:'自分に合う抹茶を探しています。いくつか質問してもらえますか？',
      secProducts:'\u62b9\u8336\u30b3\u30ec\u30af\u30b7\u30e7\u30f3',secRecipes:'\u30ec\u30b7\u30d4 & \u30ac\u30a4\u30c9',
      pP22:'\u4e8c\u5341\u4e8c NIJYU-NI (22)',pP22Grade:'Ceremonial Reserved',pP22Desc:'\u6700\u9ad8\u5cf0\u3002\u9759\u304b\u3067\u529b\u307f\u306e\u306a\u3044\u6df1\u3055\u3002',pP22Price:'\u00a548',pP22Msg:'\u4e8c\u5341\u4e8c NIJYU-NI\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u4f55\u304c\u7279\u5225\u3067\u3001\u3069\u3046\u4f7f\u3046\u306e\u304c\u826f\u3044\u3067\u3059\u304b\uff1f',
      pP18:'\u5341\u516b JU-HACHI (18)',pP18Grade:'Specialty Grade',pP18Desc:'\u7791\u60f3\u7684\u306a\u9759\u3051\u3055\u30024\u6bb5\u968e\u706b\u5165\u308c\u3001\u7121\u91cd\u529b\u306e\u8cea\u611f\u3002',pP18Price:'\u00a540',pP18Msg:'\u5341\u516b JU-HACHI\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u72ec\u81ea\u306e4\u6bb5\u968e\u706b\u5165\u308c\u3068\u306f\uff1f',
      pP17:'\u5341\u4e03 JU-NANA (17)',pP17Grade:'Specialty Grade',pP17Desc:'\u5c64\u306a\u308b\u65e8\u5473\u3001\u7d9a\u304f\u9759\u3051\u3055\u3002\u5e74\u9593500kg\u9650\u5b9a\u3002',pP17Price:'\u00a538',pP17Msg:'\u5341\u4e03 JU-NANA\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u4e8c\u91cd\u30c6\u30ed\u30ef\u30fc\u30eb\u306e\u7279\u5fb4\u306f\uff1f',
      pP16:'\u5341\u516d JU-ROKU (16)',pP16Grade:'Specialty Grade',pP16Desc:'\u7dbf\u306e\u3088\u3046\u306b\u306a\u3081\u3089\u304b\u3002\u6e29\u5ea6\u3067\u8868\u60c5\u304c\u5909\u308f\u308b\u3002',pP16Price:'\u00a535',pP16Msg:'\u5341\u516d JU-ROKU\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u7279\u5fb4\u3068\u304a\u3059\u3059\u3081\u306e\u4f7f\u3044\u65b9\u306f\uff1f',
      pP4:'\u56db SHI (4)',pP4Grade:'Specialty Grade',pP4Desc:'\u5927\u5730\u306e\u606f\u5439\u3001\u751f\u304d\u308b\u529b\u3002\u30c1\u30e7\u30b3\u3001\u30ca\u30c3\u30c4\u3001\u30d9\u30ea\u30fc\u3002',pP4Price:'\u00a530',pP4Msg:'\u56db SHI\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u3069\u3093\u306a\u30b9\u30c8\u30fc\u30ea\u30fc\u3068\u5473\u308f\u3044\u3067\u3059\u304b\uff1f',
      pPBundle:'Discovery Bundle',pPBundleGrade:'3\u7a2e\u304a\u8a66\u3057\u30bb\u30c3\u30c8',pPBundleDesc:'NAKAI\u306e\u5473\u308f\u3044\u3092\u63a2\u6c42\u3002\u521d\u3081\u3066\u306e\u65b9\u306b\u6700\u9069\u3002',pPBundlePrice:'',pPBundleMsg:'Discovery Bundle\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u4f55\u304c\u542b\u307e\u308c\u3066\u3044\u3066\u3001\u8ab0\u5411\u3051\u3067\u3059\u304b\uff1f',
      rUsucha:'\u8584\u8336',rUsuchaDesc:'\u4f1d\u7d71\u7684\u306a\u8584\u8336\u3001\u8efd\u3084\u304b\u3067\u6ce1\u7acb\u3061\u8c4a\u304b',rUsuchaMsg:'\u8584\u8336\u306e\u70b9\u3066\u65b9\u3092\u30b9\u30c6\u30c3\u30d7\u30d0\u30a4\u30b9\u30c6\u30c3\u30d7\u3067\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      rKoicha:'\u6fc3\u8336',rKoichaDesc:'\u6fc3\u539a\u3067\u6df1\u3044\u5473\u308f\u3044\u306e\u4e00\u676f',rKoichaMsg:'\u6fc3\u8336\u306e\u70b9\u3066\u65b9\u3092\u30b9\u30c6\u30c3\u30d7\u30d0\u30a4\u30b9\u30c6\u30c3\u30d7\u3067\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      rLatte:'\u62b9\u8336\u30e9\u30c6',rLatteDesc:'\u30db\u30c3\u30c8\u3067\u3082\u30a2\u30a4\u30b9\u3067\u3082\u3002\u6bce\u65e5\u306e\u4e00\u676f\u306b',rLatteMsg:'\u7f8e\u5473\u3057\u3044\u62b9\u8336\u30e9\u30c6\u306e\u4f5c\u308a\u65b9\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u30db\u30c3\u30c8\u3068\u30a2\u30a4\u30b9\u306e\u4e21\u65b9\u3092\u304a\u9858\u3044\u3057\u307e\u3059\u3002',
      rIced:'\u30a2\u30a4\u30b9\u62b9\u8336',rIcedDesc:'\u723d\u3084\u304b\u3067\u4f5c\u308a\u3084\u3059\u3044',rIcedMsg:'\u30a2\u30a4\u30b9\u62b9\u8336\u306e\u4f5c\u308a\u65b9\u3092\u30b9\u30c6\u30c3\u30d7\u30d0\u30a4\u30b9\u30c6\u30c3\u30d7\u3067\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      rAffogato:'\u30a2\u30d5\u30a9\u30ac\u30fc\u30c8',rAffogatoDesc:'\u62b9\u8336\u3068\u30d0\u30cb\u30e9\u30a2\u30a4\u30b9\u306e\u30cf\u30fc\u30e2\u30cb\u30fc',rAffogatoMsg:'\u62b9\u8336\u30a2\u30d5\u30a9\u30ac\u30fc\u30c8\u306e\u4f5c\u308a\u65b9\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      rBarista:'\u30d0\u30ea\u30b9\u30bf Tips',rBaristaDesc:'\u6c34\u6e29\u3001\u8336\u7b45\u306e\u4f7f\u3044\u65b9\u3001\u30df\u30eb\u30af\u9078\u3073',rBaristaMsg:'\u62b9\u8336\u3092\u6271\u3046\u30d0\u30ea\u30b9\u30bf\u306e\u5fc5\u9808\u30c6\u30af\u30cb\u30c3\u30af\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u6c34\u6e29\u3001\u8336\u7b45\u306e\u4f7f\u3044\u65b9\u3001\u30df\u30eb\u30af\u306e\u76f8\u6027\u3092\u30ab\u30d0\u30fc\u3057\u3066\u304f\u3060\u3055\u3044\u3002',
      heroSub:'\u3042\u306a\u305f\u306e\u62b9\u8336\u30b3\u30f3\u30b7\u30a7\u30eb\u30b8\u30e5',heroGreeting:'\u3042\u306a\u305f\u306b\u3074\u3063\u305f\u308a\u306e\u62b9\u8336\u3092\u898b\u3064\u3051\u3088\u3046',
      tFind:'\u81ea\u5206\u306b\u5408\u3046\u62b9\u8336\u3092\u63a2\u3059',tBrew:'\u30d0\u30ea\u30b9\u30bf\u30ac\u30a4\u30c9',tProduct:'\u30ec\u30b7\u30d4',tFaq:'\u62b9\u8336\u306b\u3064\u3044\u3066',
      pAsk:'\u8a73\u3057\u304f\u805e\u304f',
      inviteHeadline:'\u5927\u5207\u306a\u4eba\u306b\u62b9\u8336\u3092\u8d08\u308d\u3046',inviteBody:'\u53cb\u4eba\u3092\u62db\u5f85\u3059\u308b\u3068\u3001\u7279\u5225\u306a\u62b9\u8336\u30ae\u30d5\u30c8\u304c\u5c4a\u304d\u307e\u3059\u3002',
      inviteBtn:'\u53cb\u4eba\u3092\u62db\u5f85\u3059\u308b',inviteAllUsed:'\u5168\u3066\u62db\u5f85\u6e08\u307f',
      inviteDone:'3\u4eba\u306e\u53cb\u4eba\u306b\u62b9\u8336\u3092\u30b7\u30a7\u30a2\u3057\u307e\u3057\u305f',inviteDoneBody:'\u62b9\u8336\u306e\u8f2a\u3092\u5e83\u3052\u3066\u304f\u308c\u3066\u3042\u308a\u304c\u3068\u3046\u3054\u3056\u3044\u307e\u3059\u3002',
      sheetTitle:'\u62b9\u8336\u306e\u3072\u3068\u3068\u304d\u3092\u30b7\u30a7\u30a2',sheetBody:'\u53cb\u4eba\u306bNAKAI\u62b9\u8336\u306e\u7279\u5225\u306a\u30a6\u30a7\u30eb\u30ab\u30e0\u30af\u30fc\u30dd\u30f3\u304c\u5c4a\u304d\u307e\u3059\u3002',
      sheetShare:'\u62db\u5f85\u30ea\u30f3\u30af\u3092\u30b7\u30a7\u30a2',sheetCopy:'\u307e\u305f\u306f\u30ea\u30f3\u30af\u3092\u30b3\u30d4\u30fc',
      shareTitle:'\u53cb\u4eba\u304b\u3089\u306e\u62b9\u8336\u30ae\u30d5\u30c8',shareText:'NAKAI\u62b9\u8336\u3092\u305c\u3072\u8a66\u3057\u3066\u307f\u3066\u304f\u3060\u3055\u3044\u3002\u7279\u5225\u306a\u30a6\u30a7\u30eb\u30ab\u30e0\u30ae\u30d5\u30c8\u3092\u304a\u9001\u308a\u3057\u307e\u3059\u3002',
      couponTitle:'\u53cb\u4eba\u304b\u3089\u62b9\u8336\u306e\u30ae\u30d5\u30c8\u304c\u5c4a\u304d\u307e\u3057\u305f',couponBody:'NAKAI\u3078\u3088\u3046\u3053\u305d\u3002\u521d\u56de\u6ce8\u6587\u306e\u7279\u5225\u30ae\u30d5\u30c8\u3092\u304a\u697d\u3057\u307f\u304f\u3060\u3055\u3044\u3002',
      couponCode:'MATCHA15',couponDiscount:'\u521d\u56de\u6ce8\u6587 15% \u30aa\u30d5',
      couponCopy:'\u30b3\u30fc\u30c9\u3092\u30b3\u30d4\u30fc',couponCopied:'\u30b3\u30d4\u30fc\u3057\u307e\u3057\u305f\uff01',couponShop:'\u30b7\u30e7\u30c3\u30d7\u3078',couponDismiss:'\u30b3\u30f3\u30b7\u30a7\u30eb\u30b8\u30e5\u3092\u898b\u308b',
      toastCopied:'\u30ea\u30f3\u30af\u3092\u30b3\u30d4\u30fc\u3057\u307e\u3057\u305f',
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
    $('nc-home-sub').textContent=t('heroSub');
    $('nc-home-greeting').textContent=t('heroGreeting');
    $('nc-home-input').placeholder=t('placeholder');
    $('nc-t-find').textContent=t('tFind');
    $('nc-t-brew').textContent=t('tBrew');
    $('nc-t-product').textContent=t('tProduct');
    $('nc-t-faq').textContent=t('tFaq');
    $('nc-h-shop').textContent=t('hShop');
    $('nc-h-ws').textContent=t('hWs');
    $('nc-f-shop').textContent=t('hShop');
    $('nc-f-ws').textContent=t('hWs');
    var nfl=$('nc-nav-find-label');if(nfl)nfl.textContent=t('tFind');
    var nbl=$('nc-nav-brew-label');if(nbl)nbl.textContent=t('tBrew');
    var nrl=$('nc-nav-recipes-label');if(nrl)nrl.textContent=t('tProduct');
    var nql=$('nc-nav-faq-label');if(nql)nql.textContent=t('tFaq');
    var dfl=$('nc-dnav-find-label');if(dfl)dfl.textContent=t('tFind');
    var dbl=$('nc-dnav-brew-label');if(dbl)dbl.textContent=t('tBrew');
    var drl=$('nc-dnav-recipes-label');if(drl)drl.textContent=t('tProduct');
    var dql=$('nc-dnav-faq-label');if(dql)dql.textContent=t('tFaq');
    buildQuickActions();
    buildProductCards();
    buildRecipeCards();
    var sp=$('nc-sec-products');if(sp)sp.textContent=t('secProducts');
    var sr=$('nc-sec-recipes');if(sr)sr.textContent=t('secRecipes');
    $('nc-sheet-title').textContent=t('sheetTitle');
    $('nc-sheet-body').textContent=t('sheetBody');
    $('nc-sheet-share').textContent=t('sheetShare');
    $('nc-sheet-copy').textContent=t('sheetCopy');
    $('nc-coupon-title').textContent=t('couponTitle');
    $('nc-coupon-body').textContent=t('couponBody');
    $('nc-coupon-code').textContent=t('couponCode');
    $('nc-coupon-discount').textContent=t('couponDiscount');
    $('nc-coupon-copy').textContent=t('couponCopy');
    $('nc-coupon-shop').textContent=t('couponShop');
    $('nc-coupon-dismiss').textContent=t('couponDismiss');
    if(typeof renderInviteSection==='function')renderInviteSection();
  }}

  function showHome(){{
    $('nc-home').classList.remove('nc-hidden');
    $('nc-chat').classList.add('nc-hidden');
    var tb=$('nc-topbar');if(tb)tb.style.display='';
  }}
  function showChat(autoMsg){{
    $('nc-home').classList.add('nc-hidden');
    $('nc-chat').classList.remove('nc-hidden');
    var tb=$('nc-topbar');if(tb)tb.style.display='none';
    if(autoMsg){{$('nc-input').value=autoMsg;setTimeout(function(){{sendMessage()}},200)}}
    if(window.innerWidth>899)$('nc-input').focus();
  }}

  var products=[
    {{id:'P22',gradient:'linear-gradient(170deg,rgba(64,101,70,.18),rgba(64,101,70,.06))',url:SHOP+'/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha'}},
    {{id:'P18',gradient:'linear-gradient(170deg,rgba(64,101,70,.14),rgba(64,101,70,.05))',url:SHOP+'/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha'}},
    {{id:'P17',gradient:'linear-gradient(170deg,rgba(64,101,70,.12),rgba(64,101,70,.04))',url:SHOP+'/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha'}},
    {{id:'P16',gradient:'linear-gradient(170deg,rgba(64,101,70,.10),rgba(64,101,70,.04))',url:SHOP+'/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha'}},
    {{id:'P4',gradient:'linear-gradient(170deg,rgba(64,101,70,.08),rgba(64,101,70,.03))',url:SHOP+'/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha'}},
    {{id:'PBundle',gradient:'linear-gradient(170deg,rgba(64,101,70,.13),rgba(64,101,70,.05))',url:SHOP+'/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB'}}
  ];
  var recipes=[
    {{id:'Usucha',icon:'\U0001F375'}},
    {{id:'Koicha',icon:'\U0001F343'}},
    {{id:'Latte',icon:'\u2615'}},
    {{id:'Iced',icon:'\U0001F9CA'}},
    {{id:'Affogato',icon:'\U0001F368'}},
    {{id:'Barista',icon:'\U0001F4A1'}}
  ];

  function buildProductCards(){{
    var c=$('nc-product-cards');if(!c)return;c.innerHTML='';
    products.forEach(function(p){{
      var k='p'+p.id;var card=document.createElement('div');card.className='nc-pcard-v2';
      card.innerHTML='<div class="nc-pcard-v2__visual" style="background:'+p.gradient+'"><div class="nc-pcard-v2__blob"></div></div><div class="nc-pcard-v2__body"><div class="nc-pcard-v2__grade">'+escapeHtml(t(k+'Grade'))+'</div><div class="nc-pcard-v2__name">'+escapeHtml(t(k))+'</div><div class="nc-pcard-v2__desc">'+escapeHtml(t(k+'Desc'))+'</div><div class="nc-pcard-v2__footer"><span class="nc-pcard-v2__price">'+escapeHtml(t(k+'Price'))+'</span><span class="nc-pcard-v2__cta">'+escapeHtml(t('pAsk'))+'</span></div></div>';
      card.addEventListener('click',function(){{showChat(t(k+'Msg'))}});
      c.appendChild(card);
    }});
  }}

  function buildRecipeCards(){{
    var c=$('nc-recipe-cards');if(!c)return;c.innerHTML='';
    recipes.forEach(function(r){{
      var k='r'+r.id;var card=document.createElement('div');card.className='nc-rcard-v2';
      card.innerHTML='<div class="nc-rcard-v2__emoji">'+r.icon+'</div><div class="nc-rcard-v2__name">'+escapeHtml(t(k))+'</div><div class="nc-rcard-v2__desc">'+escapeHtml(t(k+'Desc'))+'</div>';
      card.addEventListener('click',function(){{showChat(t(k+'Msg'))}});
      c.appendChild(card);
    }});
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
    s=escapeHtml(s);
    return s
      .replace(/^#{{1,6}}\s+(.*?)$/gm,'<strong>$1</strong>')
      .replace(/^\s*-{{3,}}\s*$/gm,'')
      .replace(/^\s*\*{{3,}}\s*$/gm,'')
      .replace(/^\s*_{{3,}}\s*$/gm,'')
      .replace(/^\|.*\|$/gm,'')
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\[(.*?)\]\(\/(.*?)\)/g,'<a href="'+SHOP+'/$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\[(.*?)\]\((https?:\/\/[^\)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/^\s*[*+-]\s+(.*?)$/gm,'<li>$1</li>')
      .replace(/^\d+\.\s+(.*?)$/gm,'<li>$1</li>')
      .replace(/((?:<li>.*?<\/li>\s*)+)/g,'<ul>$1</ul>')
      .replace(/^\\t+/gm,'')
      .replace(/\\n{{2,}}/g,' ')
      .replace(/\\n/g,' ')
      .replace(/ {{2,}}/g,' ')
      .replace(/(<br>){{2,}}/g,'<br>')
      .replace(/^(<br>| )+/,'')
      .replace(/(<br>| )+$/,'');
  }}
  function scroll(){{var m=$('nc-messages');if(m)m.scrollTop=m.scrollHeight}}

  function extractProducts(text){{
    var re=/\[PRODUCT:([a-z0-9-]+)\]/gi;var handles=[];var m;
    while((m=re.exec(text))!==null)handles.push(m[1]);
    var cleaned=text.replace(/\[PRODUCT:[a-z0-9-]+\]/gi,'').trim();
    return{{handles:handles,text:cleaned}};
  }}

  function fetchAndRenderProducts(handles,parentEl){{
    if(!handles.length)return;
    var carousel=document.createElement('div');carousel.className='nc-product-carousel';
    handles.forEach(function(handle){{
      var card=document.createElement('a');card.className='nc-product-card nc-product-card--loading';
      card.href=SHOP+'/products/'+handle;card.target='_blank';card.rel='noopener';
      card.innerHTML='<div class="nc-product-card__img"></div><div class="nc-product-card__body"><div class="nc-product-card__name" style="height:2.6em;background:var(--g03);border-radius:4px"></div></div>';
      carousel.appendChild(card);
      fetch('https://nakaimatcha.com/products/'+handle+'.json')
        .then(function(r){{if(!r.ok)throw new Error('err');return r.json()}})
        .then(function(data){{
          var p=data.product;
          var img=p.images&&p.images.length?p.images[0].src:'';
          var price=p.variants&&p.variants.length?p.variants[0].price:'';
          var currency='$';
          card.classList.remove('nc-product-card--loading');
          card.innerHTML=(img?'<img class="nc-product-card__img" src="'+escapeHtml(img)+'" alt="'+escapeHtml(p.title)+'" loading="lazy">':'<div class="nc-product-card__img"></div>')
            +'<div class="nc-product-card__body">'
            +'<div class="nc-product-card__name">'+escapeHtml(p.title)+'</div>'
            +(price?'<div class="nc-product-card__price">'+currency+escapeHtml(price)+'</div>':'')
            +'<div class="nc-product-card__cta">'+(lang==='ja'?'商品を見る →':'View Product →')+'</div>'
            +'</div>';
        }})
        .catch(function(){{card.classList.remove('nc-product-card--loading');var nm=card.querySelector('.nc-product-card__name');if(nm)nm.textContent=(lang==='ja'?'商品を見る':'View Product')}});
    }});
    parentEl.appendChild(carousel);
    scroll();
  }}

  function addMsg(role,text,sources,suggestions){{
    sources=sources||[];suggestions=suggestions||[];var m=$('nc-messages');if(!m)return;
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
      if(suggestions.length){{
        html+='<div class="nc-suggestions">';
        suggestions.forEach(function(s){{
          html+='<button class="nc-suggestion" type="button">'+escapeHtml(s)+'</button>';
        }});
        html+='</div>';
      }}
      var now=new Date();var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="nc-msg__meta"><span class="nc-msg__time">'+ts+'</span></div>';
    }}else{{html='<div class="nc-msg__bubble">'+content+'</div>'}}
    d.innerHTML=html;m.appendChild(d);
    d.querySelectorAll('.nc-suggestion').forEach(function(btn){{
      btn.addEventListener('click',function(){{
        var q=this.textContent;$('nc-input').value=q;sendMessage();
        var sc=d.querySelector('.nc-suggestions');if(sc)sc.remove();
      }});
    }});
    scroll();
  }}
  function showTyping(){{var m=$('nc-messages');if(!m)return;var d=document.createElement('div');d.className='nc-msg nc-msg--bot nc-typing';d.innerHTML='<div class="nc-msg__bubble"><span></span><span></span><span></span></div><div class="nc-typing__label">'+t('typing')+'</div>';m.appendChild(d);scroll()}}
  function removeTyping(){{var m=$('nc-messages');if(!m)return;var tw=m.querySelector('.nc-typing');if(tw)tw.remove()}}

  function sendMessage(){{
    var inp=$('nc-input');var msg=inp?inp.value.trim():'';
    if(!msg||loading)return;inp.value='';
    addMsg('user',msg);chatHistory.push({{role:'user',content:msg}});
    showTyping();loading=true;
    var abortCtrl=new AbortController();var streamTimeout=setTimeout(function(){{abortCtrl.abort()}},90000);
    fetch('/api/chat/stream',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg,history:chatHistory.slice(-MAX_H),language:lang,session_id:SESSION_ID,source:'pwa'}}),signal:abortCtrl.signal}})
    .then(function(r){{
      if(!r.ok)throw new Error('err');
      removeTyping();
      var m=$('nc-messages');var d=document.createElement('div');d.className='nc-msg nc-msg--bot';
      var bubble=document.createElement('div');bubble.className='nc-msg__bubble';
      d.appendChild(bubble);m.appendChild(d);
      var fullText='';
      var reader=r.body.getReader();var decoder=new TextDecoder();var buf='';
      function read(){{
        reader.read().then(function(result){{
          if(result.done)return finish();
          buf+=decoder.decode(result.value,{{stream:true}});
          var lines=buf.split('\\n');buf=lines.pop();
          lines.forEach(function(line){{
            if(!line.startsWith('data: '))return;
            try{{var ev=JSON.parse(line.slice(6))}}catch(e){{return}}
            if(ev.type==='text'){{fullText+=ev.content;bubble.innerHTML=formatMd(fullText);scroll()}}
            else if(ev.type==='done'){{
              var now=new Date();var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
              var meta='';
              if(ev.sources&&ev.sources.length){{
                meta+='<div class="nc-msg__sources">';
                ev.sources.forEach(function(s){{var url=s.startsWith('/')?SHOP+s:s;
                  var label=s.indexOf('/products/')>-1?(lang==='ja'?'商品を見る':'View product'):s.indexOf('/blogs/')>-1?(lang==='ja'?'記事を読む':'Read article'):(lang==='ja'?'詳細':'Learn more');
                  meta+='<a href="'+escapeHtml(url)+'" class="nc-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
                meta+='</div>';
              }}
              if(ev.suggestions&&ev.suggestions.length){{
                meta+='<div class="nc-suggestions">';
                ev.suggestions.forEach(function(s){{meta+='<button class="nc-suggestion" type="button">'+escapeHtml(s)+'</button>'}});
                meta+='</div>';
              }}
              meta+='<div class="nc-msg__meta"><span class="nc-msg__time">'+ts+'</span></div>';
              var metaEl=document.createElement('div');metaEl.innerHTML=meta;
              while(metaEl.firstChild)d.appendChild(metaEl.firstChild);
              d.querySelectorAll('.nc-suggestion').forEach(function(btn){{
                btn.addEventListener('click',function(){{var q=this.textContent;$('nc-input').value=q;sendMessage();var sc=d.querySelector('.nc-suggestions');if(sc)sc.remove()}});
              }});
              /* Clean [SUGGESTIONS] block from visible text (handles **[SUGGESTIONS]** too) */
              var raw=fullText;var sugM=raw.match(/\*{{0,2}}\[SUGGESTIONS\]\*{{0,2}}/);
              if(sugM){{fullText=raw.substring(0,sugM.index).trim()}}
              /* Clean [CHOICES] block and extract options (handles **[CHOICES]** too) */
              var choices=[];var choiceM=fullText.match(/\*{{0,2}}\[CHOICES\]\*{{0,2}}/);
              if(choiceM){{var choiceEnd=fullText.match(/\*{{0,2}}\[\/CHOICES\]\*{{0,2}}/);if(choiceEnd){{var choiceStr=fullText.substring(choiceM.index+choiceM[0].length,choiceEnd.index).trim();choices=choiceStr.split('|').map(function(c){{return c.trim()}}).filter(Boolean);fullText=fullText.substring(0,choiceM.index).trim()+fullText.substring(choiceEnd.index+choiceEnd[0].length).trim()}}}}
              /* Extract [PRODUCT:handle] tags */
              var prodResult=extractProducts(fullText);fullText=prodResult.text;
              bubble.innerHTML=formatMd(fullText);
              /* Render product carousel */
              if(prodResult.handles.length>0){{fetchAndRenderProducts(prodResult.handles,d)}}
              /* Render choice buttons */
              if(choices.length>0){{var choiceDiv=document.createElement('div');choiceDiv.className='nc-choices';choices.forEach(function(txt){{var btn=document.createElement('button');btn.className='nc-choice-btn';btn.type='button';btn.textContent=txt;btn.addEventListener('click',function(){{$('nc-input').value=txt;sendMessage();choiceDiv.querySelectorAll('.nc-choice-btn').forEach(function(b){{b.disabled=true;b.classList.add('nc-choice-btn--disabled')}});btn.classList.add('nc-choice-btn--selected')}});choiceDiv.appendChild(btn)}});d.appendChild(choiceDiv)}}
              chatHistory.push({{role:'assistant',content:fullText}});saveHistory();
              scroll();
            }}
            else if(ev.type==='error'){{bubble.innerHTML=formatMd(t('error'))}}
          }});
          read();
        }}).catch(function(){{finish()}});
      }}
      function finish(){{clearTimeout(streamTimeout);loading=false;if(!fullText){{bubble.innerHTML=formatMd(t('error'))}}}}
      read();
    }})
    .catch(function(){{removeTyping();addMsg('bot',t('error'));loading=false}});
  }}

  function saveHistory(){{try{{localStorage.setItem('nakai_app_history',JSON.stringify(chatHistory.slice(-MAX_H)))}}catch(e){{}}}}
  function loadHistory(){{try{{var s=localStorage.getItem('nakai_app_history');if(s){{chatHistory=JSON.parse(s);chatHistory.forEach(function(m){{addMsg(m.role==='assistant'?'bot':'user',m.content)}})}}}}catch(e){{}}}}

  /* --- Invite system --- */
  var MAX_INVITES=3;
  function getInviteData(){{
    try{{var s=localStorage.getItem('nakai_invites');if(s)return JSON.parse(s)}}catch(e){{}}
    return{{invites:[],maxInvites:MAX_INVITES}};
  }}
  function saveInviteData(d){{try{{localStorage.setItem('nakai_invites',JSON.stringify(d))}}catch(e){{}}}}
  function getRemainingInvites(){{var d=getInviteData();return d.maxInvites-d.invites.length}}
  function generateInviteCode(){{
    var chars='abcdefghijklmnopqrstuvwxyz0123456789';var code='';
    var arr=new Uint8Array(8);crypto.getRandomValues(arr);
    for(var i=0;i<8;i++)code+=chars[arr[i]%chars.length];
    return code;
  }}
  function createInvite(){{
    var d=getInviteData();if(d.invites.length>=d.maxInvites)return null;
    var code=generateInviteCode();
    d.invites.push({{code:code,created:new Date().toISOString(),shared:true}});
    saveInviteData(d);return window.location.origin+'/app?invite='+code;
  }}
  function renderInviteSection(){{
    var el=$('nc-invite');if(!el)return;
    var remaining=getRemainingInvites();
    if(remaining<=0){{
      el.innerHTML='<div class="nc-invite__done">'+escapeHtml(t('inviteDone'))+'</div><p class="nc-invite__body" style="margin-top:8px;margin-bottom:0">'+escapeHtml(t('inviteDoneBody'))+'</p>';
    }}else{{
      var counter=remaining+' / '+MAX_INVITES;
      el.innerHTML='<div class="nc-invite__headline">'+escapeHtml(t('inviteHeadline'))+'</div><p class="nc-invite__body">'+escapeHtml(t('inviteBody'))+'</p><button class="nc-invite__btn" id="nc-invite-btn">'+escapeHtml(t('inviteBtn'))+'</button><div class="nc-invite__counter">'+counter+'</div>';
      $('nc-invite-btn').addEventListener('click',openInviteSheet);
    }}
  }}
  function openInviteSheet(){{
    $('nc-overlay-bg').classList.add('nc-overlay-bg--active');
    $('nc-invite-sheet').classList.add('nc-invite-sheet--active');
  }}
  function closeInviteSheet(){{
    $('nc-overlay-bg').classList.remove('nc-overlay-bg--active');
    $('nc-invite-sheet').classList.remove('nc-invite-sheet--active');
  }}
  function shareInvite(copyOnly){{
    var url=createInvite();
    if(!url){{closeInviteSheet();renderInviteSection();return}}
    if(!copyOnly&&navigator.share){{
      navigator.share({{title:t('shareTitle'),text:t('shareText'),url:url}}).catch(function(){{}});
    }}else{{
      copyToClipboard(url);showToast(t('toastCopied'));
    }}
    closeInviteSheet();renderInviteSection();
  }}
  function copyToClipboard(text){{
    if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(text).catch(function(){{}})}}
    else{{var ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta)}}
  }}
  function showToast(msg){{
    var t=document.createElement('div');t.className='nc-toast';t.textContent=msg;
    document.body.appendChild(t);
    setTimeout(function(){{t.classList.add('nc-toast--exit');setTimeout(function(){{t.remove()}},300)}},2500);
  }}

  /* --- Coupon system (for invite recipients) --- */
  function checkInviteParam(){{
    var params=new URLSearchParams(window.location.search);
    var code=params.get('invite');
    if(code){{
      localStorage.setItem('nakai_invite_code',code);
      window.history.replaceState(null,'',window.location.pathname);
    }}
    if(localStorage.getItem('nakai_invite_code')&&!localStorage.getItem('nakai_coupon_dismissed')){{
      showCouponOverlay();
    }}
  }}
  function showCouponOverlay(){{
    $('nc-coupon-overlay').classList.add('nc-coupon-overlay--active');
  }}
  function dismissCoupon(){{
    localStorage.setItem('nakai_coupon_dismissed','1');
    $('nc-coupon-overlay').classList.remove('nc-coupon-overlay--active');
  }}
  function copyCouponCode(){{
    copyToClipboard(t('couponCode'));
    var btn=$('nc-coupon-copy');var orig=btn.textContent;
    btn.textContent=t('couponCopied');
    setTimeout(function(){{btn.textContent=orig}},2000);
  }}

  /* --- Topbar scroll --- */
  function initTopbarScroll(){{
    var scrollArea=$('nc-home-scroll');var topbar=$('nc-topbar');var hint=$('nc-scroll-hint');
    if(!scrollArea||!topbar)return;
    scrollArea.addEventListener('scroll',function(){{
      var y=scrollArea.scrollTop;
      if(y>40)topbar.classList.add('nc-topbar--scrolled');
      else topbar.classList.remove('nc-topbar--scrolled');
      if(hint){{if(y>80)hint.classList.add('nc-hidden-hint');else hint.classList.remove('nc-hidden-hint')}}
    }});
  }}

  function boot(){{
    try{{checkInviteParam()}}catch(e){{console.error('checkInviteParam error',e)}}
    try{{setLang(lang)}}catch(e){{console.error('setLang error',e)}}
    try{{renderInviteSection()}}catch(e){{console.error('renderInviteSection error',e)}}
    $('nc-form').addEventListener('submit',function(e){{e.preventDefault();sendMessage()}});
    $('nc-back').addEventListener('click',showHome);
    $('nc-home-form').addEventListener('submit',function(e){{e.preventDefault();var v=$('nc-home-input').value.trim();if(v)showChat(v)}});
    document.querySelectorAll('.nc-lang-btn').forEach(function(b){{
      b.addEventListener('click',function(){{setLang(this.getAttribute('data-lang'))}});
    }});
    $('nc-t-find').addEventListener('click',function(){{showChat(t('findMsg'))}});
    $('nc-t-brew').addEventListener('click',function(){{showChat(t('brewMsg'))}});
    $('nc-t-product').addEventListener('click',function(){{showChat(t('productMsg'))}});
    $('nc-t-faq').addEventListener('click',function(){{showChat(t('faqMsg'))}});
    /* Sidebar nav */
    var nh=$('nc-nav-home');if(nh)nh.addEventListener('click',showHome);
    var nf=$('nc-nav-find');if(nf)nf.addEventListener('click',function(){{showChat(t('findMsg'))}});
    var nb=$('nc-nav-brew');if(nb)nb.addEventListener('click',function(){{showChat(t('brewMsg'))}});
    var nr=$('nc-nav-recipes');if(nr)nr.addEventListener('click',function(){{showChat(t('productMsg'))}});
    var nq=$('nc-nav-faq');if(nq)nq.addEventListener('click',function(){{showChat(t('faqMsg'))}});
    $('nc-topbar-mark').addEventListener('click',function(){{var s=$('nc-home-scroll');if(s)s.scrollTo({{top:0,behavior:'smooth'}})}});
    initTopbarScroll();
    /* Drawer */
    var drawer=$('nc-drawer'),drawerOv=$('nc-drawer-overlay');
    function openDrawer(){{drawer.classList.add('nc-drawer--open');drawerOv.classList.add('nc-drawer-overlay--open');document.body.style.overflow='hidden'}}
    function closeDrawer(){{drawer.classList.remove('nc-drawer--open');drawerOv.classList.remove('nc-drawer-overlay--open');document.body.style.overflow=''}}
    var hb=$('nc-hamburger');if(hb)hb.addEventListener('click',openDrawer);
    $('nc-drawer-close').addEventListener('click',closeDrawer);
    drawerOv.addEventListener('click',closeDrawer);
    $('nc-dnav-home').addEventListener('click',function(){{closeDrawer();showHome()}});
    $('nc-dnav-find').addEventListener('click',function(){{closeDrawer();showChat(t('findMsg'))}});
    $('nc-dnav-brew').addEventListener('click',function(){{closeDrawer();showChat(t('brewMsg'))}});
    $('nc-dnav-recipes').addEventListener('click',function(){{closeDrawer();showChat(t('productMsg'))}});
    $('nc-dnav-faq').addEventListener('click',function(){{closeDrawer();showChat(t('faqMsg'))}});
    $('nc-overlay-bg').addEventListener('click',closeInviteSheet);
    $('nc-sheet-share').addEventListener('click',shareInvite);
    $('nc-sheet-copy').addEventListener('click',function(){{shareInvite(true)}});
    $('nc-coupon-copy').addEventListener('click',copyCouponCode);
    $('nc-coupon-dismiss').addEventListener('click',dismissCoupon);
    try{{loadHistory();if(chatHistory.length>0)showChat()}}catch(e){{console.error('loadHistory error',e)}}
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


@pwa_router.get("/fonts/{filename}")
async def serve_font(filename: str):
    data = _FONT_FILES.get(filename)
    if not data:
        return Response(status_code=404)
    return Response(
        content=data,
        media_type="font/woff2",
        headers={"Cache-Control": "public, max-age=31536000", "Access-Control-Allow-Origin": "*"},
    )
