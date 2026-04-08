"""Barista education app for NAKAI Matcha."""
import base64
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

wholesale_router = APIRouter()

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LOGO_WM_WHITE_B64 = base64.b64encode((_REPO_ROOT / "logo-wordmark-white.png").read_bytes()).decode()
_LOGO_WM_BLACK_B64 = base64.b64encode((_REPO_ROOT / "logo-wordmark-black.png").read_bytes()).decode()
_LOGO_ICON_B64 = base64.b64encode((_REPO_ROOT / "logo-black-icon.png").read_bytes()).decode()

WS_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#406546">
<meta name="description" content="NAKAI Barista Hub - Matcha education for professionals">
<title>NAKAI Barista Hub</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --green:#406546;--cream:#F9F0E2;--white:#FFFFFF;
  --g90:rgba(64,101,70,.9);--g70:rgba(64,101,70,.7);
  --g50:rgba(64,101,70,.5);--g35:rgba(64,101,70,.35);
  --g20:rgba(64,101,70,.2);--g12:rgba(64,101,70,.12);
  --g06:rgba(64,101,70,.06);--g03:rgba(64,101,70,.03);
  --sans:'Work Sans',sans-serif;
  --ease:cubic-bezier(.22,1,.36,1);
  --shadow-s:0 1px 3px rgba(0,0,0,.04),0 1px 2px rgba(0,0,0,.03);
  --shadow-m:0 4px 12px rgba(0,0,0,.06),0 2px 4px rgba(0,0,0,.04);
  --nav-h:56px;
}}
html,body{{height:100%;overflow:hidden;background:var(--cream);color:var(--green);font-family:var(--sans);-webkit-font-smoothing:antialiased}}

/* App shell */
#bh-app{{display:flex;flex-direction:column;height:100vh;height:100dvh;position:relative}}

/* Tab content area */
.bh-tabs{{flex:1;overflow:hidden;position:relative}}
.bh-tab{{position:absolute;inset:0;overflow-y:auto;-webkit-overflow-scrolling:touch;opacity:0;pointer-events:none;transition:opacity .35s var(--ease)}}
.bh-tab.bh-active{{opacity:1;pointer-events:auto}}

/* Bottom nav */
.bh-nav{{display:flex;align-items:center;justify-content:space-around;height:var(--nav-h);padding-bottom:env(safe-area-inset-bottom);background:var(--white);border-top:1px solid rgba(64,101,70,.06);flex-shrink:0;position:relative;z-index:30}}
.bh-nav__item{{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 12px;border:none;background:none;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:color .3s var(--ease);color:var(--g35);position:relative}}
.bh-nav__item svg{{width:22px;height:22px}}
.bh-nav__item span{{font-family:var(--sans);font-size:.62rem;font-weight:500;letter-spacing:.02em}}
.bh-nav__item.bh-nav-active{{color:var(--green)}}
.bh-nav__item.bh-nav-active::before{{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:5px;height:5px;border-radius:50%;background:var(--green)}}

/* Header bar */
.bh-header{{display:flex;align-items:center;justify-content:space-between;padding:max(12px,env(safe-area-inset-top)) 20px 10px;flex-shrink:0;background:var(--cream);z-index:10}}
.bh-header__logo{{height:14px;opacity:.5}}
.bh-lang{{display:flex;background:var(--g06);border-radius:9px;padding:2px}}
.bh-lang__btn{{font-family:var(--sans);font-size:.64rem;font-weight:500;letter-spacing:.08em;padding:5px 12px;border:none;cursor:pointer;transition:all .3s var(--ease);-webkit-tap-highlight-color:transparent;background:transparent;color:var(--g35);border-radius:7px}}
.bh-lang__btn.active{{background:var(--white);color:var(--green);box-shadow:var(--shadow-s)}}

/* HOME TAB */
.bh-home{{padding:0 20px 32px;display:flex;flex-direction:column;align-items:center}}
.bh-hero{{text-align:center;padding:24px 0 20px;width:100%;max-width:480px}}
.bh-hero__sub{{font-size:.68rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--g35);margin-bottom:8px}}
.bh-hero__title{{font-size:1.3rem;font-weight:300;color:var(--green);line-height:1.45;margin-bottom:16px}}
.bh-hero__search{{display:flex;align-items:center;background:var(--white);border-radius:24px;padding:4px 4px 4px 18px;box-shadow:var(--shadow-s);transition:box-shadow .4s var(--ease)}}
.bh-hero__search:focus-within{{box-shadow:var(--shadow-m)}}
.bh-hero__input{{flex:1;border:none;background:none;font-family:var(--sans);font-size:16px;color:var(--green);outline:none;padding:10px 0}}
.bh-hero__input::placeholder{{color:var(--g35);font-weight:300}}
.bh-hero__send{{width:34px;height:34px;border-radius:50%;border:none;background:var(--green);color:var(--cream);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent;transition:all .3s var(--ease)}}
.bh-hero__send:active{{transform:scale(.9)}}
.bh-hero__send svg{{width:13px;height:13px}}

/* Quick actions */
.bh-quick{{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;max-width:480px;margin-bottom:24px}}
.bh-quick__btn{{background:var(--white);border:none;border-radius:16px;padding:18px 16px;cursor:pointer;text-align:left;transition:all .4s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.bh-quick__btn:hover{{box-shadow:var(--shadow-m)}}
.bh-quick__btn:active{{transform:scale(.97);transition-duration:.12s}}
.bh-quick__icon{{width:28px;height:28px;margin-bottom:8px;color:var(--green);opacity:.6}}
.bh-quick__label{{font-family:var(--sans);font-size:.82rem;font-weight:400;color:var(--green)}}

/* Section */
.bh-section{{width:100%;max-width:480px;margin-bottom:24px}}
.bh-section__title{{font-size:.72rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--g35);margin-bottom:14px;padding-left:2px}}

/* Product scroll */
.bh-pscroll{{display:flex;gap:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px;margin:0 -20px;padding-left:20px;padding-right:20px}}
.bh-pscroll::-webkit-scrollbar{{display:none}}
.bh-pcard{{min-width:220px;max-width:260px;flex-shrink:0;scroll-snap-align:start;background:var(--white);border-radius:18px;overflow:hidden;box-shadow:var(--shadow-s);cursor:pointer;transition:all .4s var(--ease);-webkit-tap-highlight-color:transparent}}
.bh-pcard:hover{{box-shadow:var(--shadow-m)}}
.bh-pcard:active{{transform:scale(.98);transition-duration:.1s}}
.bh-pcard__vis{{height:100px;display:flex;align-items:center;justify-content:center}}
.bh-pcard__num{{font-size:1.8rem;font-weight:300;color:rgba(64,101,70,.18)}}
.bh-pcard__body{{padding:14px 16px 16px}}
.bh-pcard__grade{{font-size:.56rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--g35);margin-bottom:4px}}
.bh-pcard__desc{{font-size:.74rem;font-weight:300;color:var(--g50);line-height:1.5;margin-bottom:8px}}
.bh-pcard__cta{{font-size:.66rem;color:var(--g35);transition:color .3s}}
.bh-pcard:hover .bh-pcard__cta{{color:var(--green)}}

.bh-order-link{{display:block;text-align:center;font-size:.72rem;font-weight:400;color:var(--g35);margin-top:20px;text-decoration:none;transition:color .3s}}
.bh-order-link:hover{{color:var(--green)}}

/* RECIPES + GUIDES GRID */
.bh-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:16px 20px 32px}}
.bh-card{{background:var(--white);border-radius:18px;padding:20px 16px;cursor:pointer;transition:all .4s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.bh-card:hover{{box-shadow:var(--shadow-m)}}
.bh-card:active{{transform:scale(.97);transition-duration:.1s}}
.bh-card__icon{{width:32px;height:32px;margin-bottom:10px;color:var(--green);opacity:.6}}
.bh-card__name{{font-family:var(--sans);font-size:.88rem;font-weight:400;color:var(--green);margin-bottom:4px}}
.bh-card__desc{{font-size:.7rem;font-weight:300;color:var(--g50);line-height:1.5}}

/* Detail panel */
.bh-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.3);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);z-index:40;opacity:0;pointer-events:none;transition:opacity .3s var(--ease)}}
.bh-overlay.bh-open{{opacity:1;pointer-events:auto}}
.bh-detail{{position:fixed;left:0;right:0;bottom:0;max-height:85vh;background:var(--white);border-radius:20px 20px 0 0;z-index:41;transform:translateY(100%);transition:transform .4s var(--ease);overflow-y:auto;-webkit-overflow-scrolling:touch;padding:0 24px max(24px,env(safe-area-inset-bottom))}}
.bh-detail.bh-open{{transform:translateY(0)}}
.bh-detail__handle{{display:flex;justify-content:center;padding:12px 0 8px;position:sticky;top:0;background:var(--white);z-index:1}}
.bh-detail__bar{{width:36px;height:4px;border-radius:2px;background:var(--g12)}}
.bh-detail__close{{position:absolute;top:12px;right:16px;width:30px;height:30px;border:none;background:var(--g06);border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--g50);font-size:1.1rem;transition:background .2s}}
.bh-detail__close:hover{{background:var(--g12)}}
.bh-detail__title{{font-size:1.15rem;font-weight:500;color:var(--green);margin-bottom:16px}}
.bh-detail__section{{margin-bottom:16px}}
.bh-detail__label{{font-size:.66rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--g35);margin-bottom:8px}}
.bh-detail__text{{font-size:.86rem;font-weight:300;color:var(--g70);line-height:1.75}}
.bh-detail__text li{{margin:4px 0;list-style-position:inside}}
.bh-detail__tip{{background:var(--g03);border-radius:12px;padding:14px 16px;margin-top:12px}}
.bh-detail__tip-label{{font-size:.64rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--green);margin-bottom:4px}}
.bh-detail__tip-text{{font-size:.82rem;font-weight:300;color:var(--g70);line-height:1.6}}
.bh-detail__product{{display:inline-block;font-size:.72rem;font-weight:500;color:var(--green);background:var(--g06);border-radius:10px;padding:6px 14px;margin-top:8px}}

/* CHAT TAB */
.bh-chat-wrap{{display:flex;flex-direction:column;height:100%}}
.bh-chat-header{{display:flex;align-items:center;gap:10px;padding:max(12px,env(safe-area-inset-top)) 20px 10px;background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);flex-shrink:0;z-index:10}}
.bh-chat-header__title{{font-size:.82rem;font-weight:400;letter-spacing:.04em;color:var(--g35)}}
.bh-chat-header__dot{{width:6px;height:6px;border-radius:50%;background:var(--green);opacity:.5;animation:bhBreathe 4s ease-in-out infinite}}
@keyframes bhBreathe{{0%,100%{{opacity:.5;transform:scale(1)}}50%{{opacity:.2;transform:scale(.8)}}}}
.bh-messages{{flex:1;overflow-y:auto;padding:16px 20px 8px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth}}
.bh-messages::-webkit-scrollbar{{width:0;display:none}}
.bh-banner{{text-align:center;padding:8px 12px;font-size:.72rem;font-weight:300;color:var(--g20);letter-spacing:.02em;margin-bottom:16px}}
.bh-msg{{display:flex;flex-direction:column;animation:bhMsgIn .45s var(--ease) both}}
@keyframes bhMsgIn{{from{{opacity:0;transform:translateY(6px) scale(.98)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
.bh-msg--bot{{align-items:flex-start;padding-right:36px}}
.bh-msg--bot .bh-msg__bubble{{background:var(--white);border-radius:18px 18px 18px 6px;padding:14px 18px;font-size:.86rem;font-weight:400;line-height:1.8;color:var(--green);box-shadow:var(--shadow-s)}}
.bh-msg__bubble a{{color:var(--green);font-weight:500;text-decoration:underline;text-decoration-color:var(--g12);text-underline-offset:3px;transition:text-decoration-color .3s}}
.bh-msg__bubble a:hover{{text-decoration-color:var(--green)}}
.bh-msg__bubble strong{{font-weight:600}}
.bh-msg__bubble ul,.bh-msg__bubble ol{{margin:8px 0;padding-left:18px}}
.bh-msg__bubble li{{margin:4px 0}}
.bh-msg--user{{align-items:flex-end;padding-left:36px;margin-top:4px}}
.bh-msg--user .bh-msg__bubble{{background:var(--green);color:var(--cream);border-radius:18px 18px 6px 18px;padding:12px 18px;font-size:.86rem;font-weight:400;line-height:1.65;box-shadow:0 2px 8px rgba(64,101,70,.15)}}
.bh-msg--bot+.bh-msg--user,.bh-msg--user+.bh-msg--bot{{margin-top:14px}}
.bh-msg__meta{{margin-top:4px;padding-left:2px}}
.bh-msg__time{{font-size:.56rem;color:var(--g20)}}
.bh-suggestions{{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}}
.bh-suggestion{{font-family:var(--sans);font-size:.74rem;font-weight:400;color:var(--green);background:var(--g03);border:none;border-radius:18px;padding:8px 14px;cursor:pointer;transition:all .3s var(--ease);text-align:left;line-height:1.4;-webkit-tap-highlight-color:transparent}}
.bh-suggestion:hover{{background:var(--g06)}}
.bh-suggestion:active{{transform:scale(.97)}}
.bh-msg__sources{{margin-top:6px;display:flex;flex-wrap:wrap;gap:4px}}
.bh-msg__source{{font-size:.66rem;color:var(--green);text-decoration:none;background:var(--g03);border:none;border-radius:10px;padding:6px 12px;transition:background .3s;-webkit-tap-highlight-color:transparent}}
.bh-msg__source:hover{{background:var(--g06)}}
.bh-typing .bh-msg__bubble{{display:flex;gap:5px;align-items:center;padding:14px 18px!important;min-height:40px}}
.bh-typing .bh-msg__bubble span{{width:5px;height:5px;background:var(--g20);border-radius:50%;display:inline-block;animation:bhTypeDot 1.8s ease-in-out infinite}}
.bh-typing .bh-msg__bubble span:nth-child(2){{animation-delay:.2s}}
.bh-typing .bh-msg__bubble span:nth-child(3){{animation-delay:.4s}}
@keyframes bhTypeDot{{0%,60%,100%{{opacity:.15;transform:scale(.8)}}30%{{opacity:.6;transform:scale(1)}}}}
.bh-typing__label{{font-size:.58rem;color:var(--g20);padding-left:2px;margin-top:3px;font-style:italic}}
.bh-quick-actions{{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}}
.bh-qa-btn{{font-family:var(--sans);font-size:.74rem;font-weight:400;color:var(--green);background:var(--white);border:none;border-radius:18px;padding:8px 16px;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:all .3s var(--ease);box-shadow:var(--shadow-s)}}
.bh-qa-btn:hover{{box-shadow:var(--shadow-m)}}
.bh-qa-btn:active{{transform:scale(.96)}}
.bh-input-area{{padding:10px 20px 8px;flex-shrink:0;background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}}
.bh-form{{display:flex;align-items:center;gap:8px;background:var(--white);border-radius:24px;padding:4px 4px 4px 18px;box-shadow:var(--shadow-s);transition:box-shadow .4s var(--ease)}}
.bh-form:focus-within{{box-shadow:var(--shadow-m)}}
.bh-input{{flex:1;border:none;background:none;font-family:var(--sans);font-size:16px;color:var(--green);outline:none;padding:10px 0;min-height:44px}}
.bh-input::placeholder{{color:var(--g35);font-weight:300}}
.bh-send{{width:36px;height:36px;border-radius:50%;border:none;background:var(--green);color:var(--cream);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent;transition:all .3s var(--ease)}}
.bh-send:hover{{opacity:.85}}
.bh-send:active{{transform:scale(.88);transition-duration:.1s}}
.bh-send svg{{width:13px;height:13px}}

/* Animations */
@keyframes bhFadeUp{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Desktop */
@media(min-width:600px){{
  .bh-grid{{max-width:540px;margin:0 auto}}
  .bh-home{{max-width:540px;margin:0 auto}}
  .bh-messages{{max-width:640px;margin:0 auto;width:100%}}
  .bh-input-area{{max-width:640px;margin:0 auto;width:100%}}
  .bh-detail{{max-width:500px;left:50%;right:auto;transform:translateX(-50%) translateY(100%)}}
  .bh-detail.bh-open{{transform:translateX(-50%) translateY(0)}}
  .bh-nav{{max-width:420px;margin:0 auto;border-radius:20px 20px 0 0}}
}}
</style>
</head>
<body>
<div id="bh-app">
  <!-- Header -->
  <div class="bh-header">
    <img class="bh-header__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
    <div class="bh-lang" id="bh-lang">
      <button class="bh-lang__btn active" data-lang="en">EN</button>
      <button class="bh-lang__btn" data-lang="ja">JA</button>
    </div>
  </div>

  <!-- Tab content -->
  <div class="bh-tabs">
    <!-- HOME -->
    <div class="bh-tab bh-active" id="bh-tab-home">
      <div class="bh-home">
        <div class="bh-hero">
          <p class="bh-hero__sub" id="bh-hero-sub">NAKAI Barista Hub</p>
          <h1 class="bh-hero__title" id="bh-hero-title">Everything you need behind the bar</h1>
          <form class="bh-hero__search" id="bh-hero-form">
            <input type="text" class="bh-hero__input" id="bh-hero-input" autocomplete="off" maxlength="500" />
            <button type="submit" class="bh-hero__send" aria-label="Search">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
            </button>
          </form>
        </div>
        <div class="bh-quick" id="bh-quick-grid"></div>
        <div class="bh-section">
          <h2 class="bh-section__title" id="bh-sec-products">Products</h2>
          <div class="bh-pscroll" id="bh-product-scroll"></div>
        </div>
        <a href="mailto:wholesale@nakaiinfo.com?subject=Order%20Inquiry" class="bh-order-link" id="bh-order-link">Need to order? Contact wholesale@nakaiinfo.com &rarr;</a>
      </div>
    </div>

    <!-- RECIPES -->
    <div class="bh-tab" id="bh-tab-recipes">
      <div class="bh-grid" id="bh-recipe-grid"></div>
    </div>

    <!-- GUIDES -->
    <div class="bh-tab" id="bh-tab-guides">
      <div class="bh-grid" id="bh-guide-grid"></div>
    </div>

    <!-- CHAT -->
    <div class="bh-tab" id="bh-tab-chat">
      <div class="bh-chat-wrap">
        <div class="bh-chat-header">
          <span class="bh-chat-header__title" id="bh-chat-title">Matcha Assistant</span>
          <span class="bh-chat-header__dot"></span>
        </div>
        <div class="bh-messages" id="bh-messages">
          <div class="bh-banner" id="bh-banner"></div>
          <div class="bh-msg bh-msg--bot" id="bh-welcome">
            <div class="bh-msg__bubble" id="bh-greeting"></div>
            <div class="bh-quick-actions" id="bh-chat-quick"></div>
          </div>
        </div>
        <div class="bh-input-area">
          <form class="bh-form" id="bh-form">
            <input type="text" class="bh-input" id="bh-input" autocomplete="off" maxlength="500" />
            <button type="submit" class="bh-send" aria-label="Send">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom nav -->
  <nav class="bh-nav" id="bh-nav">
    <button class="bh-nav__item bh-nav-active" data-tab="home">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg>
      <span id="bh-nav-home">Home</span>
    </button>
    <button class="bh-nav__item" data-tab="recipes">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
      <span id="bh-nav-recipes">Recipes</span>
    </button>
    <button class="bh-nav__item" data-tab="guides">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
      <span id="bh-nav-guides">Guides</span>
    </button>
    <button class="bh-nav__item" data-tab="chat">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
      <span id="bh-nav-chat">Chat</span>
    </button>
  </nav>

  <!-- Detail panel -->
  <div class="bh-overlay" id="bh-overlay"></div>
  <div class="bh-detail" id="bh-detail">
    <div class="bh-detail__handle"><div class="bh-detail__bar"></div></div>
    <button class="bh-detail__close" id="bh-detail-close">&times;</button>
    <div id="bh-detail-content"></div>
  </div>
</div>

<script>
(function(){{
  'use strict';
  var MAX_H=20,chatHistory=[],loading=false;
  var SESSION_ID=(function(){{var id=localStorage.getItem('nakai_bh_session');if(!id){{id=crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c){{var r=Math.random()*16|0;return(c==='x'?r:(r&0x3|0x8)).toString(16)}});localStorage.setItem('nakai_bh_session',id)}}return id}})();

  /* ── i18n ── */
  var i18n={{
    en:{{
      heroSub:'NAKAI Barista Hub',heroTitle:'Everything you need behind the bar',
      placeholder:'Ask about matcha...',typing:'Thinking...',
      banner:'Your matcha assistant for recipes, troubleshooting, and more',
      chatTitle:'Matcha Assistant',
      greeting:"I'm your matcha assistant. Ask me anything \u2014 recipes, troubleshooting, products, techniques.",
      cq1:'Compare products',cq1m:'Compare the NAKAI matcha products. What are the key differences and best use cases?',
      cq2:'Latte recipe',cq2m:'What is the ideal matcha latte recipe for a cafe? Include dosing, temperature, and milk recommendations.',
      cq3:'Storage guide',cq3m:'What are the best practices for storing matcha in a commercial kitchen?',
      cq4:'Troubleshoot',cq4m:'I am having issues with my matcha drinks. Help me troubleshoot bitterness, clumping, and color fading.',
      error:'Connection issue. Please try again.',
      navHome:'Home',navRecipes:'Recipes',navGuides:'Guides',navChat:'Chat',
      secProducts:'Products',
      pAsk:'Ask about this',
      qaLatte:'Latte Recipe',qaTrouble:'Troubleshoot',qaCompare:'Compare Products',qaAsk:'Ask AI',
      qaLatteAction:'recipes',qaTroubleAction:'guides',qaCompareAction:'chat:Compare the NAKAI matcha products and their best use cases',qaAskAction:'chat',
      orderLink:'Need to order? Contact wholesale@nakaiinfo.com \u2192',
      /* Product data */
      p111grade:'Organic Ceremonial Reserve',p111origin:'Kagoshima',p111desc:'4-cultivar micro-milled. Creamy body, layered umami.',
      p111msg:'Tell me about NAKAI 111 matcha. What makes it special for a cafe?',
      p101grade:'Organic Specialty',p101origin:'Kirishima',p101desc:'Single origin. Vivid umami, elegant finish.',
      p101msg:'Tell me about NAKAI 101 matcha from Kirishima.',
      p102grade:'Organic Specialty',p102origin:'Kagoshima \u00d7 Uji',p102desc:'Cross-region blend. Balanced sweetness, 500kg limit.',
      p102msg:'Tell me about NAKAI 102 matcha. Why is it limited?',
      p103grade:'Organic Specialty',p103origin:'Kagoshima',p103desc:'Bold umami forward. Full body, deep green.',
      p103msg:'Tell me about NAKAI 103. Best drinks for it?',
      p211grade:'Ceremonial',p211origin:'Yame',p211desc:'Single origin. Clean, classic profile.',
      p211msg:'Tell me about NAKAI 211 from Yame.',
      p212grade:'Ceremonial',p212origin:'Blend',p212desc:'Latte-optimized. 1st+2nd harvest for milk pairing.',
      p212msg:'Tell me about NAKAI 212. Why is it best for lattes?',
      /* Recipes */
      r1name:'Hot Matcha Latte',r1desc:'The cafe classic',
      r1ingredients:'2-3g matcha, 30ml water (75\u00b0C), 240ml steamed oat milk',
      r1steps:'1. Sift matcha into bowl or pitcher\\n2. Add 30ml of 75\u00b0C water\\n3. Whisk vigorously until smooth and frothy\\n4. Steam 240ml oat milk\\n5. Pour matcha into cup, add steamed milk\\n6. Optional: latte art on top',
      r1tip:'Always sift matcha before each use to prevent clumps.',
      r1product:'Recommended: NAKAI 212 or 111',
      r2name:'Iced Matcha Latte',r2desc:'Refreshing iced version',
      r2ingredients:'3g matcha, 30ml water (75\u00b0C), ice, 240ml cold milk',
      r2steps:'1. Sift 3g matcha into bowl\\n2. Add 30ml of 75\u00b0C water\\n3. Whisk until smooth\\n4. Fill glass with ice\\n5. Pour in 240ml cold milk\\n6. Pour matcha over the milk',
      r2tip:'Use slightly more matcha for iced drinks \u2014 the ice dilutes flavor.',
      r2product:'Recommended: NAKAI 212 or 103',
      r3name:'Matcha Espresso Tonic',r3desc:'Fizzy and layered',
      r3ingredients:'2g matcha, 20ml water (75\u00b0C), tonic water, ice',
      r3steps:'1. Sift 2g matcha into a small bowl\\n2. Add 20ml of 75\u00b0C water\\n3. Whisk until smooth\\n4. Fill glass with ice and tonic water\\n5. Slowly pour matcha over the back of a spoon for layered effect',
      r3tip:'Pour very slowly for a beautiful two-tone layered look.',
      r3product:'Recommended: NAKAI 101 or 103',
      r4name:'Dirty Matcha',r4desc:'Matcha meets espresso',
      r4ingredients:'2g matcha, 30ml water (75\u00b0C), 1 espresso shot',
      r4steps:'1. Sift 2g matcha\\n2. Add 30ml of 75\u00b0C water and whisk\\n3. Pour matcha into cup\\n4. Pull a single espresso shot\\n5. Pour espresso slowly over the matcha',
      r4tip:'The espresso should float on top \u2014 pour gently over a spoon.',
      r4product:'Recommended: NAKAI 211 or 212',
      r5name:'Matcha Concentrate',r5desc:'Batch prep for rush hour',
      r5ingredients:'10g matcha, 150ml water (75\u00b0C)',
      r5steps:'1. Sift 10g matcha into a large bowl\\n2. Add 150ml of 75\u00b0C water\\n3. Whisk vigorously until fully dissolved\\n4. Transfer to squeeze bottle\\n5. Refrigerate\\n6. Use 30ml per drink',
      r5tip:'Good for up to 4 hours refrigerated. Shake before each use.',
      r5product:'Recommended: NAKAI 212 or 103',
      r6name:'Ceremonial Service',r6desc:'Traditional preparation',
      r6ingredients:'2g matcha, 70ml water (70\u00b0C), chawan (tea bowl)',
      r6steps:'1. Sift 2g matcha into chawan\\n2. Add 70ml of 70\u00b0C water\\n3. Whisk in M-pattern for 15 seconds\\n4. Lift whisk and create foam\\n5. Serve immediately',
      r6tip:'Use slightly cooler water (70\u00b0C) for ceremonial grade to bring out sweetness.',
      r6product:'Recommended: NAKAI 111 or 101',
      /* Guides */
      g1name:'Troubleshooting',g1desc:'Fix common issues',
      g1content:'<strong>Bitter?</strong> Lower water temperature to 75\u00b0C. Never use boiling water.\\n\\n<strong>Clumpy?</strong> Sift matcha before every use. Use a fine-mesh strainer.\\n\\n<strong>Weak in latte?</strong> Increase dose to 2.5\u20133g per serving.\\n\\n<strong>Color fading?</strong> Oxidation \u2014 seal container tightly, use within 2 weeks of opening.\\n\\n<strong>Inconsistent?</strong> Pre-sift daily portions into airtight containers. Mark water temperature on your kettle.',
      g2name:'Storage Guide',g2desc:'Keep matcha fresh',
      g2content:'<strong>Sealed, dark, cool</strong> \u2014 the three rules of matcha storage.\\n\\n<strong>Unopened:</strong> Refrigerate. Good for 6+ months.\\n\\n<strong>Once opened:</strong> Transfer to an airtight container. Keep at room temperature (not fridge \u2014 condensation risk). Use within 2\u20134 weeks.\\n\\n<strong>Never freeze once opened</strong> \u2014 moisture will degrade quality.\\n\\n<strong>Away from:</strong> Direct sunlight, strong odors, heat sources.',
      g3name:'Milk Pairing',g3desc:'Choose the right milk',
      g3content:'<strong>Oat milk:</strong> Best for lattes. Natural sweetness complements matcha umami. Froths well.\\n\\n<strong>Whole milk:</strong> Richest foam and mouthfeel. Classic choice.\\n\\n<strong>Almond milk:</strong> Best for iced drinks. Lighter body, nutty notes.\\n\\n<strong>Coconut milk:</strong> Great for iced and blended drinks. Tropical notes.\\n\\n<strong>Soy milk:</strong> Watch temperature \u2014 can curdle above 65\u00b0C. Good protein foam.',
      g4name:'Product Comparison',g4desc:'Find your matcha',
      g4content:'<strong>111</strong> \u2014 Organic Ceremonial Reserve. Best for: straight drinking, premium lattes. Micro-milled, creamy.\\n\\n<strong>101</strong> \u2014 Organic Specialty, Kirishima. Best for: ceremonial service, straight. Vivid umami.\\n\\n<strong>102</strong> \u2014 Organic Specialty, cross-region. Best for: versatile menu use. Balanced sweetness. Limited 500kg/year.\\n\\n<strong>103</strong> \u2014 Organic Specialty, Kagoshima. Best for: bold lattes, iced drinks. Umami-forward.\\n\\n<strong>211</strong> \u2014 Ceremonial, Yame. Best for: clean-tasting lattes, straight. Classic.\\n\\n<strong>212</strong> \u2014 Ceremonial, Blend. Best for: high-volume lattes. Optimized for milk.',
      g5name:'Cultivar Library',g5desc:'Know your tea plants',
      g5content:'<strong>Saemidori:</strong> Sweet cream notes, mild umami. Elegant and approachable.\\n\\n<strong>Okumidori:</strong> Deep umami, clean finish. Rich green color.\\n\\n<strong>Asanoka:</strong> Fruity, bright character. Unique flavor profile.\\n\\n<strong>Yabukita:</strong> Classic Japanese cultivar. Robust, reliable structure.\\n\\n<strong>Gokou:</strong> Rich aroma, creamy body. Uji specialty cultivar.',
      g6name:'Speed & Efficiency',g6desc:'Tips for rush hour',
      g6content:'<strong>Pre-sift portions:</strong> Sift daily matcha amounts into small airtight containers each morning.\\n\\n<strong>Hot water station:</strong> Keep a dedicated kettle at 75\u201380\u00b0C. Mark the target temperature clearly.\\n\\n<strong>Electric frother backup:</strong> Keep a milk frother for quick single servings when the bar is slammed.\\n\\n<strong>Matcha concentrate:</strong> Mix 10g + 150ml water, refrigerate. Use 30ml per drink. Lasts 4 hours.\\n\\n<strong>Station layout:</strong> Matcha, sifter, whisk, and scale within arm\u2019s reach.',
    }},
    ja:{{
      heroSub:'NAKAI \u30d0\u30ea\u30b9\u30bf\u30cf\u30d6',heroTitle:'\u30d0\u30fc\u306e\u5f8c\u308d\u3067\u5fc5\u8981\u306a\u3059\u3079\u3066',
      placeholder:'\u62b9\u8336\u306b\u3064\u3044\u3066\u8cea\u554f...',typing:'\u8003\u3048\u4e2d...',
      banner:'\u30ec\u30b7\u30d4\u3001\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0\u306a\u3069\u3001\u62b9\u8336\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8',
      chatTitle:'\u62b9\u8336\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8',
      greeting:'\u62b9\u8336\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8\u3067\u3059\u3002\u30ec\u30b7\u30d4\u3001\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0\u3001\u5546\u54c1\u3001\u6280\u8853\u306a\u3069\u4f55\u3067\u3082\u304a\u805e\u304d\u304f\u3060\u3055\u3044\u3002',
      cq1:'\u5546\u54c1\u6bd4\u8f03',cq1m:'NAKAI\u306e\u62b9\u8336\u5546\u54c1\u3092\u6bd4\u8f03\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u4e3b\u306a\u9055\u3044\u3068\u6700\u9069\u306a\u7528\u9014\u306f\uff1f',
      cq2:'\u30e9\u30c6\u30ec\u30b7\u30d4',cq2m:'\u30ab\u30d5\u30a7\u3067\u306e\u7406\u60f3\u7684\u306a\u62b9\u8336\u30e9\u30c6\u30ec\u30b7\u30d4\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      cq3:'\u4fdd\u5b58\u30ac\u30a4\u30c9',cq3m:'\u5546\u696d\u7528\u30ad\u30c3\u30c1\u30f3\u3067\u306e\u62b9\u8336\u4fdd\u5b58\u306e\u30d9\u30b9\u30c8\u30d7\u30e9\u30af\u30c6\u30a3\u30b9\u306f\uff1f',
      cq4:'\u30c8\u30e9\u30d6\u30eb\u89e3\u6c7a',cq4m:'\u62b9\u8336\u30c9\u30ea\u30f3\u30af\u306e\u554f\u984c\u304c\u3042\u308a\u307e\u3059\u3002\u82e6\u5473\u3001\u30c0\u30de\u3001\u8272\u892a\u305b\u306e\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0\u3092\u304a\u9858\u3044\u3057\u307e\u3059\u3002',
      error:'\u63a5\u7d9a\u306b\u554f\u984c\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002\u3082\u3046\u4e00\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002',
      navHome:'\u30db\u30fc\u30e0',navRecipes:'\u30ec\u30b7\u30d4',navGuides:'\u30ac\u30a4\u30c9',navChat:'\u30c1\u30e3\u30c3\u30c8',
      secProducts:'\u5546\u54c1',
      pAsk:'\u8a73\u3057\u304f\u805e\u304f',
      qaLatte:'\u30e9\u30c6\u30ec\u30b7\u30d4',qaTrouble:'\u30c8\u30e9\u30d6\u30eb\u89e3\u6c7a',qaCompare:'\u5546\u54c1\u6bd4\u8f03',qaAsk:'AI\u306b\u805e\u304f',
      qaLatteAction:'recipes',qaTroubleAction:'guides',qaCompareAction:'chat:NAKAI\u306e\u62b9\u8336\u5546\u54c1\u3092\u6bd4\u8f03\u3057\u3066\u304f\u3060\u3055\u3044',qaAskAction:'chat',
      orderLink:'\u6ce8\u6587\u306f wholesale@nakaiinfo.com \u3078 \u2192',
      p111grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb\u30fb\u30ea\u30b6\u30fc\u30d6',p111origin:'\u9e7f\u5150\u5cf6',p111desc:'4\u54c1\u7a2e\u30de\u30a4\u30af\u30ed\u30df\u30eb\u3002\u30af\u30ea\u30fc\u30df\u30fc\u306a\u3046\u307e\u307f\u3002',
      p111msg:'NAKAI 111\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      p101grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p101origin:'\u9727\u5cf6',p101desc:'\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3002\u9bae\u3084\u304b\u306a\u3046\u307e\u307f\u3002',
      p101msg:'NAKAI 101\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      p102grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p102origin:'\u9e7f\u5150\u5cf6\u00d7\u5b87\u6cbb',p102desc:'\u7523\u5730\u6a2a\u65ad\u30d6\u30ec\u30f3\u30c9\u3002\u30d0\u30e9\u30f3\u30b9\u306e\u826f\u3044\u7518\u307f\u3002',
      p102msg:'NAKAI 102\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      p103grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p103origin:'\u9e7f\u5150\u5cf6',p103desc:'\u529b\u5f37\u3044\u3046\u307e\u307f\u3002\u30d5\u30eb\u30dc\u30c7\u30a3\u3002',
      p103msg:'NAKAI 103\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      p211grade:'\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb',p211origin:'\u516b\u5973',p211desc:'\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3002\u30af\u30ea\u30fc\u30f3\u306a\u5473\u308f\u3044\u3002',
      p211msg:'NAKAI 211\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      p212grade:'\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb',p212origin:'\u30d6\u30ec\u30f3\u30c9',p212desc:'\u30e9\u30c6\u7279\u5316\u30021\u756a\u8336+2\u756a\u8336\u3002',
      p212msg:'NAKAI 212\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      r1name:'\u30db\u30c3\u30c8\u62b9\u8336\u30e9\u30c6',r1desc:'\u30ab\u30d5\u30a7\u306e\u5b9a\u756a',
      r1ingredients:'2-3g \u62b9\u8336\u300130ml \u304a\u6e6f(75\u00b0C)\u3001240ml \u30b9\u30c1\u30fc\u30e0\u30aa\u30fc\u30c4\u30df\u30eb\u30af',
      r1steps:'1. \u62b9\u8336\u3092\u3075\u308b\u3046\\n2. 75\u00b0C\u306e\u304a\u6e6f30ml\u3092\u52a0\u3048\u308b\\n3. \u3057\u3063\u304b\u308a\u6ce1\u7acb\u3064\u307e\u3067\u6df7\u305c\u308b\\n4. \u30aa\u30fc\u30c4\u30df\u30eb\u30af240ml\u3092\u30b9\u30c1\u30fc\u30e0\\n5. \u62b9\u8336\u3092\u30ab\u30c3\u30d7\u306b\u6ce8\u304e\u3001\u30df\u30eb\u30af\u3092\u52a0\u3048\u308b',
      r1tip:'\u6bce\u56de\u3075\u308b\u3063\u3066\u304b\u3089\u4f7f\u3046\u3068\u30c0\u30de\u9632\u6b62\u3002',r1product:'\u63a8\u5968: NAKAI 212 \u307e\u305f\u306f 111',
      r2name:'\u30a2\u30a4\u30b9\u62b9\u8336\u30e9\u30c6',r2desc:'\u723d\u3084\u304b\u306a\u30a2\u30a4\u30b9\u7248',
      r2ingredients:'3g \u62b9\u8336\u300130ml \u304a\u6e6f(75\u00b0C)\u3001\u6c37\u3001240ml \u51b7\u305f\u3044\u30df\u30eb\u30af',
      r2steps:'1. 3g\u306e\u62b9\u8336\u3092\u3075\u308b\u3046\\n2. 75\u00b0C\u306e\u304a\u6e6f30ml\u3092\u52a0\u3048\u308b\\n3. \u6ed1\u3089\u304b\u306b\u306a\u308b\u307e\u3067\u6df7\u305c\u308b\\n4. \u30b0\u30e9\u30b9\u306b\u6c37\u3092\u5165\u308c\u308b\\n5. \u51b7\u305f\u3044\u30df\u30eb\u30af240ml\u3092\u6ce8\u3050\\n6. \u62b9\u8336\u3092\u4e0a\u304b\u3089\u6ce8\u3050',
      r2tip:'\u30a2\u30a4\u30b9\u30c9\u30ea\u30f3\u30af\u306f\u62b9\u8336\u3092\u5c11\u3057\u591a\u3081\u306b\u3002',r2product:'\u63a8\u5968: NAKAI 212 \u307e\u305f\u306f 103',
      r3name:'\u62b9\u8336\u30a8\u30b9\u30d7\u30ec\u30c3\u30bd\u30c8\u30cb\u30c3\u30af',r3desc:'\u70ad\u9178\u3067\u723d\u3084\u304b',
      r3ingredients:'2g \u62b9\u8336\u300120ml \u304a\u6e6f(75\u00b0C)\u3001\u30c8\u30cb\u30c3\u30af\u30a6\u30a9\u30fc\u30bf\u30fc\u3001\u6c37',
      r3steps:'1. 2g\u306e\u62b9\u8336\u3092\u3075\u308b\u3046\\n2. 75\u00b0C\u306e\u304a\u6e6f20ml\u3092\u52a0\u3048\u308b\\n3. \u6ed1\u3089\u304b\u306b\u6df7\u305c\u308b\\n4. \u30b0\u30e9\u30b9\u306b\u6c37\u3068\u30c8\u30cb\u30c3\u30af\u3092\u5165\u308c\u308b\\n5. \u30b9\u30d7\u30fc\u30f3\u306e\u80cc\u3067\u3086\u3063\u304f\u308a\u62b9\u8336\u3092\u6ce8\u3050',
      r3tip:'\u3086\u3063\u304f\u308a\u6ce8\u3050\u3068\u7f8e\u3057\u3044\u30ec\u30a4\u30e4\u30fc\u306b\u3002',r3product:'\u63a8\u5968: NAKAI 101 \u307e\u305f\u306f 103',
      r4name:'\u30c0\u30fc\u30c6\u30a3\u30de\u30c3\u30c1\u30e3',r4desc:'\u62b9\u8336\u00d7\u30a8\u30b9\u30d7\u30ec\u30c3\u30bd',
      r4ingredients:'2g \u62b9\u8336\u300130ml \u304a\u6e6f(75\u00b0C)\u3001\u30a8\u30b9\u30d7\u30ec\u30c3\u30bd1\u30b7\u30e7\u30c3\u30c8',
      r4steps:'1. 2g\u306e\u62b9\u8336\u3092\u3075\u308b\u3046\\n2. 75\u00b0C\u306e\u304a\u6e6f30ml\u3092\u52a0\u3048\u3066\u6df7\u305c\u308b\\n3. \u62b9\u8336\u3092\u30ab\u30c3\u30d7\u306b\u6ce8\u3050\\n4. \u30a8\u30b9\u30d7\u30ec\u30c3\u30bd\u3092\u62bd\u51fa\\n5. \u30a8\u30b9\u30d7\u30ec\u30c3\u30bd\u3092\u3086\u3063\u304f\u308a\u4e0a\u304b\u3089\u6ce8\u3050',
      r4tip:'\u30a8\u30b9\u30d7\u30ec\u30c3\u30bd\u304c\u4e0a\u306b\u6d6e\u304f\u3088\u3046\u306b\u3002',r4product:'\u63a8\u5968: NAKAI 211 \u307e\u305f\u306f 212',
      r5name:'\u62b9\u8336\u30b3\u30f3\u30bb\u30f3\u30c8\u30ec\u30fc\u30c8',r5desc:'\u30e9\u30c3\u30b7\u30e5\u6642\u306e\u4e8b\u524d\u6e96\u5099',
      r5ingredients:'10g \u62b9\u8336\u3001150ml \u304a\u6e6f(75\u00b0C)',
      r5steps:'1. 10g\u306e\u62b9\u8336\u3092\u3075\u308b\u3046\\n2. 75\u00b0C\u306e\u304a\u6e6f150ml\u3092\u52a0\u3048\u308b\\n3. \u3057\u3063\u304b\u308a\u6df7\u305c\u308b\\n4. \u30dc\u30c8\u30eb\u306b\u79fb\u3057\u3066\u51b7\u8535\\n5. 1\u676f\u3042\u305f\u308a30ml\u4f7f\u7528',
      r5tip:'\u51b7\u8535\u30674\u6642\u9593\u4ee5\u5185\u3002\u4f7f\u7528\u524d\u306b\u632f\u308b\u3002',r5product:'\u63a8\u5968: NAKAI 212 \u307e\u305f\u306f 103',
      r6name:'\u8336\u9053\u30b5\u30fc\u30d3\u30b9',r6desc:'\u4f1d\u7d71\u7684\u306a\u70b9\u3066\u65b9',
      r6ingredients:'2g \u62b9\u8336\u300170ml \u304a\u6e6f(70\u00b0C)\u3001\u8336\u7897',
      r6steps:'1. 2g\u306e\u62b9\u8336\u3092\u8336\u7897\u306b\u3075\u308b\u3046\\n2. 70\u00b0C\u306e\u304a\u6e6f70ml\u3092\u52a0\u3048\u308b\\n3. M\u5b57\u306b15\u79d2\u9593\u8336\u7b45\u3067\u70b9\u3066\u308b\\n4. \u6ce1\u3092\u7acb\u3066\u308b\\n5. \u3059\u3050\u306b\u63d0\u4f9b',
      r6tip:'70\u00b0C\u306e\u4f4e\u3081\u306e\u6e29\u5ea6\u3067\u7518\u307f\u3092\u5f15\u304d\u51fa\u3059\u3002',r6product:'\u63a8\u5968: NAKAI 111 \u307e\u305f\u306f 101',
      g1name:'\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0',g1desc:'\u3088\u304f\u3042\u308b\u554f\u984c\u306e\u89e3\u6c7a',
      g1content:'<strong>\u82e6\u3044\uff1f</strong> \u6c34\u6e29\u309275\u00b0C\u306b\u4e0b\u3052\u308b\u3002\u6cb8\u9a30\u6c34\u306f\u4f7f\u308f\u306a\u3044\u3002\\n\\n<strong>\u30c0\u30de\u304c\u3042\u308b\uff1f</strong> \u6bce\u56de\u3075\u308b\u3063\u3066\u304b\u3089\u4f7f\u3046\u3002\\n\\n<strong>\u30e9\u30c6\u3067\u8584\u3044\uff1f</strong> 2.5\u301c3g\u306b\u5897\u3084\u3059\u3002\\n\\n<strong>\u8272\u304c\u8910\u305b\u308b\uff1f</strong> \u9178\u5316\u3002\u5bc6\u5c01\u3057\u30012\u9031\u9593\u4ee5\u5185\u306b\u4f7f\u3046\u3002\\n\\n<strong>\u4e0d\u5b89\u5b9a\uff1f</strong> \u6bce\u65e5\u306e\u5206\u91cf\u3092\u4e8b\u524d\u306b\u3075\u308b\u3063\u3066\u304a\u304f\u3002',
      g2name:'\u4fdd\u5b58\u30ac\u30a4\u30c9',g2desc:'\u62b9\u8336\u3092\u65b0\u9bae\u306b\u4fdd\u3064',
      g2content:'<strong>\u5bc6\u5c01\u30fb\u907f\u5149\u30fb\u4f4e\u6e29</strong> \u2014 \u4fdd\u5b58\u306e3\u539f\u5247\u3002\\n\\n<strong>\u672a\u958b\u5c01:</strong> \u51b7\u8535\u4fdd\u5b58\u30026\u30f6\u6708\u4ee5\u4e0a\u3002\\n\\n<strong>\u958b\u5c01\u5f8c:</strong> \u5bc6\u5c01\u5bb9\u5668\u306b\u79fb\u3059\u3002\u5e38\u6e29\u4fdd\u5b58\u30022\u301c4\u9031\u9593\u4ee5\u5185\u306b\u4f7f\u3046\u3002\\n\\n<strong>\u958b\u5c01\u5f8c\u306e\u51b7\u51cd\u306fNG</strong> \u2014 \u6c34\u5206\u3067\u54c1\u8cea\u304c\u4f4e\u4e0b\u3002',
      g3name:'\u30df\u30eb\u30af\u30da\u30a2\u30ea\u30f3\u30b0',g3desc:'\u6700\u9069\u306a\u30df\u30eb\u30af\u9078\u3073',
      g3content:'<strong>\u30aa\u30fc\u30c4\u30df\u30eb\u30af:</strong> \u30e9\u30c6\u306b\u6700\u9069\u3002\u5929\u7136\u306e\u7518\u307f\u304c\u62b9\u8336\u3068\u76f8\u6027\u25ce\u3002\\n\\n<strong>\u5168\u4e73:</strong> \u6700\u3082\u30ea\u30c3\u30c1\u306a\u6ce1\u3002\u5b9a\u756a\u3002\\n\\n<strong>\u30a2\u30fc\u30e2\u30f3\u30c9:</strong> \u30a2\u30a4\u30b9\u5411\u304d\u3002\\n\\n<strong>\u30b3\u30b3\u30ca\u30c3\u30c4:</strong> \u30a2\u30a4\u30b9\u30fb\u30d6\u30ec\u30f3\u30c9\u5411\u304d\u3002\\n\\n<strong>\u8c46\u4e73:</strong> 65\u00b0C\u4ee5\u4e0a\u3067\u56fa\u307e\u308b\u3053\u3068\u304c\u3042\u308b\u306e\u3067\u6ce8\u610f\u3002',
      g4name:'\u5546\u54c1\u6bd4\u8f03',g4desc:'\u6700\u9069\u306a\u62b9\u8336\u3092\u898b\u3064\u3051\u308b',
      g4content:'<strong>111</strong> \u2014 \u30bb\u30ec\u30e2\u30cb\u30a2\u30eb\u30ea\u30b6\u30fc\u30d6\u3002\u30b9\u30c8\u30ec\u30fc\u30c8\u3001\u30d7\u30ec\u30df\u30a2\u30e0\u30e9\u30c6\u306b\u3002\\n\\n<strong>101</strong> \u2014 \u9727\u5cf6\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3002\u8336\u9053\u3001\u30b9\u30c8\u30ec\u30fc\u30c8\u306b\u3002\\n\\n<strong>102</strong> \u2014 \u7523\u5730\u6a2a\u65ad\u3002\u4e07\u80fd\u578b\u3002\u5e74\u9593500kg\u9650\u5b9a\u3002\\n\\n<strong>103</strong> \u2014 \u9e7f\u5150\u5cf6\u3002\u6fc3\u3044\u30e9\u30c6\u3001\u30a2\u30a4\u30b9\u306b\u3002\\n\\n<strong>211</strong> \u2014 \u516b\u5973\u3002\u30af\u30ea\u30fc\u30f3\u306a\u30e9\u30c6\u3001\u30b9\u30c8\u30ec\u30fc\u30c8\u306b\u3002\\n\\n<strong>212</strong> \u2014 \u30e9\u30c6\u7279\u5316\u3002\u5927\u91cf\u63d0\u4f9b\u5411\u304d\u3002',
      g5name:'\u54c1\u7a2e\u30e9\u30a4\u30d6\u30e9\u30ea',g5desc:'\u8336\u306e\u54c1\u7a2e\u3092\u77e5\u308b',
      g5content:'<strong>\u3055\u3048\u307f\u3069\u308a:</strong> \u7518\u3044\u30af\u30ea\u30fc\u30e0\u3001\u7a4f\u3084\u304b\u306a\u3046\u307e\u307f\u3002\\n\\n<strong>\u304a\u304f\u307f\u3069\u308a:</strong> \u6df1\u3044\u3046\u307e\u307f\u3001\u30af\u30ea\u30a2\u306a\u5f8c\u5473\u3002\\n\\n<strong>\u3042\u3055\u306e\u304b:</strong> \u30d5\u30eb\u30fc\u30c6\u30a3\u3067\u660e\u308b\u3044\u3002\\n\\n<strong>\u3084\u3076\u304d\u305f:</strong> \u5b9a\u756a\u3002\u529b\u5f37\u3044\u69cb\u9020\u3002\\n\\n<strong>\u3054\u3053\u3046:</strong> \u8c4a\u304b\u306a\u9999\u308a\u3001\u30af\u30ea\u30fc\u30df\u30fc\u3002\u5b87\u6cbb\u7279\u7523\u3002',
      g6name:'\u30b9\u30d4\u30fc\u30c9\u30fb\u52b9\u7387',g6desc:'\u30e9\u30c3\u30b7\u30e5\u6642\u306e\u30b3\u30c4',
      g6content:'<strong>\u4e8b\u524d\u306b\u3075\u308b\u3046:</strong> \u6bce\u671d\u3001\u305d\u306e\u65e5\u306e\u5206\u91cf\u3092\u5c0f\u5206\u3051\u3057\u3066\u304a\u304f\u3002\\n\\n<strong>\u304a\u6e6f\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3:</strong> 75\u301c80\u00b0C\u306b\u8a2d\u5b9a\u3057\u305f\u5c02\u7528\u30b1\u30c8\u30eb\u3092\u7f6e\u304f\u3002\\n\\n<strong>\u96fb\u52d5\u30d5\u30ed\u30b5\u30fc:</strong> \u5fd9\u3057\u3044\u6642\u306e\u30d0\u30c3\u30af\u30a2\u30c3\u30d7\u306b\u3002\\n\\n<strong>\u30b3\u30f3\u30bb\u30f3\u30c8\u30ec\u30fc\u30c8:</strong> 10g+150ml\u3067\u4f5c\u308a\u7f6e\u304d\u30021\u676f30ml\u30024\u6642\u9593\u6709\u52b9\u3002',
    }}
  }};

  var lang=(function(){{var s=localStorage.getItem('nakai_bh_lang');if(s&&i18n[s])return s;var n=(navigator.language||'en').substring(0,2);return i18n[n]?n:'en'}})();
  function t(k){{return(i18n[lang]||i18n.en)[k]||i18n.en[k]||''}}
  function $(id){{return document.getElementById(id)}}
  function escapeHtml(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}

  function formatMd(s){{
    if(!s)return'';
    s=escapeHtml(s);
    return s
      .replace(/^#{{1,6}}\s+(.*?)$/gm,'<strong>$1</strong>')
      .replace(/^\s*-{{3,}}\s*$/gm,'').replace(/^\s*\*{{3,}}\s*$/gm,'').replace(/^\s*_{{3,}}\s*$/gm,'')
      .replace(/^\|.*\|$/gm,'')
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\[(.*?)\]\((https?:\/\/[^\)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/^\s*[*+-]\s+(.*?)$/gm,'<li>$1</li>')
      .replace(/^\d+\.\s+(.*?)$/gm,'<li>$1</li>')
      .replace(/((?:<li>.*?<\/li>\s*)+)/g,'<ul>$1</ul>')
      .replace(/^\\t+/gm,'').replace(/\\n{{2,}}/g,' ').replace(/\\n/g,' ')
      .replace(/ {{2,}}/g,' ').replace(/(<br>){{2,}}/g,'<br>')
      .replace(/^(<br>| )+/,'').replace(/(<br>| )+$/,'');
  }}

  /* ── SVG icons for cards ── */
  var ICONS={{
    latte:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>',
    iced:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M12 2v4"/><path d="M16 2v4"/><rect x="5" y="6" width="14" height="16" rx="3"/><path d="M5 10h14"/></svg>',
    tonic:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2l2 4h4l2-4"/><path d="M10 6v0a8 8 0 00-4 7v5a4 4 0 004 4h4a4 4 0 004-4v-5a8 8 0 00-4-7v0"/></svg>',
    dirty:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>',
    concentrate:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v4a2 2 0 01-2 2H6a2 2 0 00-2 2v8a4 4 0 004 4h8a4 4 0 004-4v-8a2 2 0 00-2-2h-2a2 2 0 01-2-2V2"/></svg>',
    ceremonial:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2z"/><path d="M2 12h20"/></svg>',
    troubleshoot:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>',
    storage:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>',
    milk:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2h8l2 4v14a2 2 0 01-2 2H8a2 2 0 01-2-2V6l2-4z"/><path d="M6 6h12"/></svg>',
    compare:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    cultivar:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c4-4 8-7.5 8-12a8 8 0 10-16 0c0 4.5 4 8 8 12z"/><path d="M12 6v10"/><path d="M8 10c2-1 4 1 4 1s2-2 4-1"/></svg>',
    speed:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    home:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg>',
    chat:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>',
  }};

  /* ── Data ── */
  var products=[
    {{num:'111',k:'p111',accent:'linear-gradient(170deg,rgba(196,162,64,.15),rgba(196,162,64,.05))'}},
    {{num:'101',k:'p101',accent:'linear-gradient(170deg,rgba(64,101,70,.18),rgba(64,101,70,.06))'}},
    {{num:'102',k:'p102',accent:'linear-gradient(170deg,rgba(64,101,70,.16),rgba(64,101,70,.05))'}},
    {{num:'103',k:'p103',accent:'linear-gradient(170deg,rgba(64,101,70,.14),rgba(64,101,70,.05))'}},
    {{num:'211',k:'p211',accent:'linear-gradient(170deg,rgba(64,101,70,.10),rgba(64,101,70,.04))'}},
    {{num:'212',k:'p212',accent:'linear-gradient(170deg,rgba(64,101,70,.10),rgba(64,101,70,.04))'}}
  ];
  var recipes=[
    {{k:'r1',icon:'latte'}},{{k:'r2',icon:'iced'}},{{k:'r3',icon:'tonic'}},
    {{k:'r4',icon:'dirty'}},{{k:'r5',icon:'concentrate'}},{{k:'r6',icon:'ceremonial'}}
  ];
  var guides=[
    {{k:'g1',icon:'troubleshoot'}},{{k:'g2',icon:'storage'}},{{k:'g3',icon:'milk'}},
    {{k:'g4',icon:'compare'}},{{k:'g5',icon:'cultivar'}},{{k:'g6',icon:'speed'}}
  ];
  var quickActions=[
    {{label:'qaLatte',icon:'latte',action:'qaLatteAction'}},
    {{label:'qaTrouble',icon:'troubleshoot',action:'qaTroubleAction'}},
    {{label:'qaCompare',icon:'compare',action:'qaCompareAction'}},
    {{label:'qaAsk',icon:'chat',action:'qaAskAction'}}
  ];

  /* ── Tab navigation ── */
  var currentTab='home';
  function switchTab(name){{
    currentTab=name;
    document.querySelectorAll('.bh-tab').forEach(function(el){{el.classList.remove('bh-active')}});
    document.querySelectorAll('.bh-nav__item').forEach(function(el){{el.classList.remove('bh-nav-active')}});
    var tab=$('bh-tab-'+name);if(tab)tab.classList.add('bh-active');
    var nav=document.querySelector('.bh-nav__item[data-tab="'+name+'"]');if(nav)nav.classList.add('bh-nav-active');
    if(name==='chat'){{var inp=$('bh-input');if(inp&&window.innerWidth>600)inp.focus()}}
  }}

  /* ── Detail panel ── */
  function openDetail(html){{
    $('bh-detail-content').innerHTML=html;
    $('bh-overlay').classList.add('bh-open');
    $('bh-detail').classList.add('bh-open');
  }}
  function closeDetail(){{
    $('bh-overlay').classList.remove('bh-open');
    $('bh-detail').classList.remove('bh-open');
  }}

  /* ── Build UI ── */
  function buildQuickGrid(){{
    var g=$('bh-quick-grid');if(!g)return;g.innerHTML='';
    quickActions.forEach(function(qa){{
      var b=document.createElement('button');b.className='bh-quick__btn';
      b.innerHTML='<div class="bh-quick__icon">'+ICONS[qa.icon]+'</div><div class="bh-quick__label">'+escapeHtml(t(qa.label))+'</div>';
      b.addEventListener('click',function(){{
        var action=t(qa.action);
        if(action.indexOf('chat:')=== 0){{switchTab('chat');var msg=action.slice(5);$('bh-input').value=msg;setTimeout(sendMessage,200)}}
        else if(action==='chat'){{switchTab('chat')}}
        else{{switchTab(action)}}
      }});
      g.appendChild(b);
    }});
  }}

  function buildProductScroll(){{
    var c=$('bh-product-scroll');if(!c)return;c.innerHTML='';
    products.forEach(function(p){{
      var card=document.createElement('div');card.className='bh-pcard';
      card.innerHTML='<div class="bh-pcard__vis" style="background:'+p.accent+'">'
        +'<div class="bh-pcard__num">'+escapeHtml(p.num)+'</div></div>'
        +'<div class="bh-pcard__body">'
        +'<div class="bh-pcard__grade">'+escapeHtml(t(p.k+'grade'))+' \u00b7 '+escapeHtml(t(p.k+'origin'))+'</div>'
        +'<div class="bh-pcard__desc">'+escapeHtml(t(p.k+'desc'))+'</div>'
        +'<div class="bh-pcard__cta">'+escapeHtml(t('pAsk'))+'</div>'
        +'</div>';
      card.addEventListener('click',function(){{switchTab('chat');$('bh-input').value=t(p.k+'msg');setTimeout(sendMessage,200)}});
      c.appendChild(card);
    }});
  }}

  function buildRecipeGrid(){{
    var g=$('bh-recipe-grid');if(!g)return;g.innerHTML='';
    recipes.forEach(function(r){{
      var card=document.createElement('div');card.className='bh-card';
      card.innerHTML='<div class="bh-card__icon">'+ICONS[r.icon]+'</div>'
        +'<div class="bh-card__name">'+escapeHtml(t(r.k+'name'))+'</div>'
        +'<div class="bh-card__desc">'+escapeHtml(t(r.k+'desc'))+'</div>';
      card.addEventListener('click',function(){{
        var html='<h2 class="bh-detail__title">'+escapeHtml(t(r.k+'name'))+'</h2>'
          +'<div class="bh-detail__section"><div class="bh-detail__label">'+escapeHtml(lang==='ja'?'\u6750\u6599':'Ingredients')+'</div>'
          +'<div class="bh-detail__text">'+escapeHtml(t(r.k+'ingredients'))+'</div></div>'
          +'<div class="bh-detail__section"><div class="bh-detail__label">'+escapeHtml(lang==='ja'?'\u624b\u9806':'Steps')+'</div>'
          +'<div class="bh-detail__text">'+t(r.k+'steps').split('\\n').map(function(l){{return escapeHtml(l)}}).join('<br>')+'</div></div>'
          +'<div class="bh-detail__tip"><div class="bh-detail__tip-label">'+escapeHtml(lang==='ja'?'\u30d7\u30ed\u306e\u30b3\u30c4':'Pro Tip')+'</div>'
          +'<div class="bh-detail__tip-text">'+escapeHtml(t(r.k+'tip'))+'</div></div>'
          +'<div class="bh-detail__product">'+escapeHtml(t(r.k+'product'))+'</div>';
        openDetail(html);
      }});
      g.appendChild(card);
    }});
  }}

  function buildGuideGrid(){{
    var g=$('bh-guide-grid');if(!g)return;g.innerHTML='';
    guides.forEach(function(gd){{
      var card=document.createElement('div');card.className='bh-card';
      card.innerHTML='<div class="bh-card__icon">'+ICONS[gd.icon]+'</div>'
        +'<div class="bh-card__name">'+escapeHtml(t(gd.k+'name'))+'</div>'
        +'<div class="bh-card__desc">'+escapeHtml(t(gd.k+'desc'))+'</div>';
      card.addEventListener('click',function(){{
        var raw=t(gd.k+'content');
        var html='<h2 class="bh-detail__title">'+escapeHtml(t(gd.k+'name'))+'</h2>'
          +'<div class="bh-detail__text">'+raw.split('\\n\\n').map(function(p){{return'<p style="margin-bottom:12px">'+p+'</p>'}}).join('')+'</div>';
        openDetail(html);
      }});
      g.appendChild(card);
    }});
  }}

  function buildChatQuick(){{
    var c=$('bh-chat-quick');if(!c)return;c.innerHTML='';
    [['cq1','cq1m'],['cq2','cq2m'],['cq3','cq3m'],['cq4','cq4m']].forEach(function(pair){{
      var b=document.createElement('button');b.className='bh-qa-btn';
      b.textContent=t(pair[0]);
      b.setAttribute('data-msg',t(pair[1]));
      b.addEventListener('click',function(){{$('bh-input').value=this.getAttribute('data-msg');sendMessage();c.style.display='none'}});
      c.appendChild(b);
    }});
  }}

  /* ── Language ── */
  function setLang(l){{
    lang=l;localStorage.setItem('nakai_bh_lang',l);
    document.documentElement.lang=l;
    document.querySelectorAll('.bh-lang__btn').forEach(function(b){{b.classList.toggle('active',b.getAttribute('data-lang')===l)}});
    $('bh-hero-sub').textContent=t('heroSub');
    $('bh-hero-title').textContent=t('heroTitle');
    $('bh-hero-input').placeholder=t('placeholder');
    $('bh-input').placeholder=t('placeholder');
    $('bh-banner').textContent=t('banner');
    $('bh-greeting').innerHTML=t('greeting');
    $('bh-chat-title').textContent=t('chatTitle');
    $('bh-sec-products').textContent=t('secProducts');
    $('bh-order-link').textContent=t('orderLink');
    $('bh-nav-home').textContent=t('navHome');
    $('bh-nav-recipes').textContent=t('navRecipes');
    $('bh-nav-guides').textContent=t('navGuides');
    $('bh-nav-chat').textContent=t('navChat');
    buildQuickGrid();buildProductScroll();buildRecipeGrid();buildGuideGrid();buildChatQuick();
  }}

  /* ── Chat ── */
  function scroll(){{var m=$('bh-messages');if(m)m.scrollTop=m.scrollHeight}}

  function addMsg(role,text,sources,suggestions){{
    sources=sources||[];suggestions=suggestions||[];
    var m=$('bh-messages');if(!m)return;
    var d=document.createElement('div');d.className='bh-msg bh-msg--'+role;var html='';
    var content=role==='bot'?formatMd(text):escapeHtml(text);
    if(role==='bot'){{
      html+='<div class="bh-msg__bubble">'+content+'</div>';
      if(sources.length){{
        html+='<div class="bh-msg__sources">';
        sources.forEach(function(s){{var label=lang==='ja'?'\u8a73\u7d30':'Learn more';
          html+='<a href="'+escapeHtml(s)+'" class="bh-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
        html+='</div>';
      }}
      if(suggestions.length){{
        html+='<div class="bh-suggestions">';
        suggestions.forEach(function(s){{html+='<button class="bh-suggestion" type="button">'+escapeHtml(s)+'</button>'}});
        html+='</div>';
      }}
      var now=new Date();var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="bh-msg__meta"><span class="bh-msg__time">'+ts+'</span></div>';
    }}else{{html='<div class="bh-msg__bubble">'+content+'</div>'}}
    d.innerHTML=html;m.appendChild(d);
    d.querySelectorAll('.bh-suggestion').forEach(function(btn){{
      btn.addEventListener('click',function(){{
        $('bh-input').value=this.textContent;sendMessage();
        var sc=d.querySelector('.bh-suggestions');if(sc)sc.remove();
      }});
    }});
    scroll();
  }}

  function showTyping(){{var m=$('bh-messages');if(!m)return;var d=document.createElement('div');d.className='bh-msg bh-msg--bot bh-typing';d.innerHTML='<div class="bh-msg__bubble"><span></span><span></span><span></span></div><div class="bh-typing__label">'+t('typing')+'</div>';m.appendChild(d);scroll()}}
  function removeTyping(){{var m=$('bh-messages');if(!m)return;var tw=m.querySelector('.bh-typing');if(tw)tw.remove()}}

  function sendMessage(){{
    var inp=$('bh-input');var msg=inp?inp.value.trim():'';
    if(!msg||loading)return;inp.value='';
    addMsg('user',msg);chatHistory.push({{role:'user',content:msg}});
    showTyping();loading=true;
    var abortCtrl=new AbortController();var streamTimeout=setTimeout(function(){{abortCtrl.abort()}},90000);
    fetch('/api/chat/stream',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg,history:chatHistory.slice(-MAX_H),language:lang,session_id:SESSION_ID,source:'wholesale'}}),signal:abortCtrl.signal}})
    .then(function(r){{
      if(!r.ok)throw new Error('err');
      removeTyping();
      var m=$('bh-messages');var d=document.createElement('div');d.className='bh-msg bh-msg--bot';
      var bubble=document.createElement('div');bubble.className='bh-msg__bubble';
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
                meta+='<div class="bh-msg__sources">';
                ev.sources.forEach(function(s){{var label=lang==='ja'?'\u8a73\u7d30':'Learn more';
                  meta+='<a href="'+escapeHtml(s)+'" class="bh-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
                meta+='</div>';
              }}
              if(ev.suggestions&&ev.suggestions.length){{
                meta+='<div class="bh-suggestions">';
                ev.suggestions.forEach(function(s){{meta+='<button class="bh-suggestion" type="button">'+escapeHtml(s)+'</button>'}});
                meta+='</div>';
              }}
              meta+='<div class="bh-msg__meta"><span class="bh-msg__time">'+ts+'</span></div>';
              var metaEl=document.createElement('div');metaEl.innerHTML=meta;
              while(metaEl.firstChild)d.appendChild(metaEl.firstChild);
              d.querySelectorAll('.bh-suggestion').forEach(function(btn){{
                btn.addEventListener('click',function(){{$('bh-input').value=this.textContent;sendMessage();var sc=d.querySelector('.bh-suggestions');if(sc)sc.remove()}});
              }});
              var raw=fullText;var si=raw.indexOf('[SUGGESTIONS]');
              if(si>-1){{fullText=raw.substring(0,si).trim();bubble.innerHTML=formatMd(fullText)}}
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
    .catch(function(){{clearTimeout(streamTimeout);removeTyping();addMsg('bot',t('error'));loading=false}});
  }}

  function saveHistory(){{try{{localStorage.setItem('nakai_bh_history',JSON.stringify(chatHistory.slice(-MAX_H)))}}catch(e){{}}}}
  function loadHistory(){{try{{var s=localStorage.getItem('nakai_bh_history');if(s){{chatHistory=JSON.parse(s);chatHistory.forEach(function(m){{addMsg(m.role==='assistant'?'bot':'user',m.content)}})}}}}catch(e){{}}}}

  /* ── Init ── */
  function init(){{
    setLang(lang);
    loadHistory();

    /* Nav */
    document.querySelectorAll('.bh-nav__item').forEach(function(btn){{
      btn.addEventListener('click',function(){{switchTab(this.getAttribute('data-tab'))}});
    }});

    /* Lang */
    document.querySelectorAll('.bh-lang__btn').forEach(function(b){{
      b.addEventListener('click',function(){{setLang(this.getAttribute('data-lang'))}});
    }});

    /* Chat form */
    $('bh-form').addEventListener('submit',function(e){{e.preventDefault();sendMessage()}});

    /* Hero search */
    $('bh-hero-form').addEventListener('submit',function(e){{
      e.preventDefault();
      var v=$('bh-hero-input').value.trim();
      if(v){{switchTab('chat');$('bh-input').value=v;setTimeout(sendMessage,200)}}
    }});

    /* Detail panel close */
    $('bh-detail-close').addEventListener('click',closeDetail);
    $('bh-overlay').addEventListener('click',closeDetail);

    /* Restore chat tab if history exists */
    if(chatHistory.length>0)switchTab('chat');
  }}

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
  else init();
}})();
</script>
</body>
</html>"""


@wholesale_router.get("/wholesale")
async def serve_wholesale() -> HTMLResponse:
    return HTMLResponse(
        content=WS_HTML,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        },
    )
