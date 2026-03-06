"""Wholesale partner portal for NAKAI Matcha."""
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
<meta name="description" content="NAKAI Matcha Wholesale Partner Portal">
<title>NAKAI Wholesale</title>
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
}}
html,body{{height:100%;overflow:hidden;background:var(--cream);color:var(--green);font-family:var(--sans);-webkit-font-smoothing:antialiased}}

/* Login Gate */
#ws-login-gate{{display:flex;align-items:center;justify-content:center;min-height:100vh;background:var(--cream)}}
.ws-login-box{{background:var(--white);padding:48px;border-radius:16px;box-shadow:var(--shadow-m);text-align:center;max-width:360px;width:90%}}
.ws-login-box img{{width:40px;margin-bottom:16px;opacity:.7}}
.ws-login-box h2{{font-family:var(--sans);font-size:1.1rem;font-weight:500;color:var(--green);margin-bottom:24px;letter-spacing:.08em;text-transform:uppercase}}
.ws-login-box input{{width:100%;padding:12px 16px;border:1px solid #ddd;border-radius:8px;font-size:1rem;font-family:var(--sans);outline:none;margin-bottom:12px}}
.ws-login-box input:focus{{border-color:var(--green)}}
.ws-login-box button{{width:100%;padding:12px;background:var(--green);color:var(--white);border:none;border-radius:8px;font-size:.9rem;font-family:var(--sans);cursor:pointer;transition:opacity .3s}}
.ws-login-box button:hover{{opacity:.85}}
.ws-login-error{{color:#c0392b;font-size:.85rem;margin-top:8px;display:none}}

/* App shell */
#ws-app{{display:none;height:100vh;height:100dvh}}
#ws-app.ws-active{{display:flex}}

/* Brand sidebar (desktop) */
.ws-brand{{width:280px;flex-shrink:0;background:var(--green);display:flex;flex-direction:column;padding:32px 28px;overflow:hidden}}
.ws-brand__top{{display:flex;flex-direction:column;align-items:flex-start;gap:10px}}
.ws-brand__top-row{{display:flex;align-items:center;justify-content:space-between;width:100%}}
.ws-brand__logo{{height:14px;width:auto;opacity:.8}}
.ws-brand__tagline{{font-family:var(--sans);font-weight:300;font-size:.68rem;color:var(--cream);opacity:.4;letter-spacing:.04em}}
.ws-brand__nav{{display:flex;flex-direction:column;gap:2px;width:100%;margin-top:28px}}
.ws-brand__nav-item{{display:flex;align-items:center;gap:10px;font-family:var(--sans);font-size:.72rem;font-weight:400;color:rgba(249,240,226,.45);padding:10px 14px;border-radius:10px;cursor:pointer;transition:all .35s var(--ease);border:none;background:transparent;text-align:left;-webkit-tap-highlight-color:transparent;width:100%}}
.ws-brand__nav-item:hover{{color:var(--cream);background:rgba(249,240,226,.08)}}
.ws-brand__nav-item svg{{width:16px;height:16px;opacity:.5;flex-shrink:0}}
.ws-brand__nav-item:hover svg{{opacity:.8}}
.ws-brand__bottom{{margin-top:auto;padding-top:24px;display:flex;flex-direction:column;gap:8px}}
.ws-brand__contact{{display:block;text-align:center;font-family:var(--sans);font-size:.64rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;padding:12px 16px;border-radius:10px;cursor:pointer;transition:all .5s var(--ease);background:rgba(249,240,226,.12);color:var(--cream);border:none}}
.ws-brand__contact:hover{{background:rgba(249,240,226,.22)}}
.ws-brand__copy{{font-family:var(--sans);font-size:.58rem;color:rgba(249,240,226,.2);text-align:center;margin-top:20px;letter-spacing:.06em}}

/* Main area */
.ws-main{{flex:1;display:flex;flex-direction:column;min-width:0;position:relative;overflow:hidden}}

/* HOME */
.ws-home{{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .5s var(--ease),transform .5s var(--ease);z-index:5}}
.ws-home.ws-hidden{{opacity:0;transform:translateX(-20px);pointer-events:none}}

/* Topbar (mobile) */
.ws-topbar{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:max(14px,env(safe-area-inset-top)) 24px 12px;transition:background .4s var(--ease)}}
.ws-topbar--scrolled{{background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}}
.ws-topbar__left{{display:flex;align-items:center;gap:8px}}
.ws-topbar__wordmark{{height:16px;width:auto;opacity:.5;transition:opacity .3s;cursor:pointer}}
.ws-topbar__wordmark:hover{{opacity:.7}}
.ws-topbar__right{{display:flex;align-items:center;gap:8px}}
.ws-hamburger{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;cursor:pointer;-webkit-tap-highlight-color:transparent;padding:0}}
.ws-hamburger svg{{width:20px;height:20px;color:var(--g50)}}

/* Scroll area */
.ws-home__scroll{{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;align-items:center}}

/* Hero */
.ws-hero{{width:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;min-height:min(300px,36vh);padding:0 28px;text-align:center}}
.ws-hero__sub{{font-family:var(--sans);font-weight:300;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--g35);margin-bottom:12px;animation:wsFadeUp .7s var(--ease) both}}
.ws-hero__heading{{font-family:var(--sans);font-size:clamp(1.3rem,3.2vw,1.7rem);font-weight:300;color:var(--green);line-height:1.5;max-width:520px;margin-bottom:24px;animation:wsFadeUp .7s .08s var(--ease) both}}
.ws-hero__input-wrap{{width:100%;max-width:520px;animation:wsFadeUp .7s .16s var(--ease) both}}
.ws-hero__form{{display:flex;align-items:center;gap:8px;background:var(--white);border:none;border-radius:28px;padding:5px 5px 5px 22px;transition:box-shadow .5s var(--ease);box-shadow:var(--shadow-s)}}
.ws-hero__form:focus-within{{box-shadow:var(--shadow-m)}}
.ws-hero__input{{flex:1;border:none;background:transparent;color:var(--green);font-family:inherit;font-size:16px;font-weight:400;outline:none;padding:13px 0}}
.ws-hero__input::placeholder{{color:var(--g35);font-weight:300}}

/* Topic pills */
.ws-topics{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;width:100%;max-width:580px;padding:0 28px;margin-top:16px;animation:wsFadeUp .7s .24s var(--ease) both}}
.ws-topics__pill{{font-family:var(--sans);font-size:.78rem;font-weight:400;color:var(--g50);background:var(--g03);border:none;border-radius:22px;padding:12px 22px;cursor:pointer;transition:all .35s var(--ease);-webkit-tap-highlight-color:transparent}}
.ws-topics__pill:hover{{color:var(--green);background:var(--g06)}}
.ws-topics__pill:active{{transform:scale(.96);transition-duration:.12s}}

/* Sections */
.ws-section{{width:100%;max-width:720px;padding:0 28px;margin-top:28px}}
.ws-section__title{{font-family:var(--sans);font-weight:400;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--g35);margin-bottom:20px;padding-left:4px}}

/* Product cards */
.ws-products-grid{{display:flex;gap:16px;overflow-x:auto;-webkit-overflow-scrolling:touch;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}}
.ws-products-grid::-webkit-scrollbar{{display:none}}
.ws-products-grid>.ws-pcard{{min-width:260px;max-width:300px;flex-shrink:0;scroll-snap-align:start}}
.ws-pcard{{background:var(--white);border:none;border-radius:20px;overflow:hidden;cursor:pointer;transition:all .5s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.ws-pcard:hover{{box-shadow:var(--shadow-m)}}
.ws-pcard:active{{transform:scale(.98);transition-duration:.12s}}
.ws-pcard__visual{{width:100%;height:140px;position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.ws-pcard__num{{font-family:var(--sans);font-size:2.2rem;font-weight:300;color:rgba(64,101,70,.18);line-height:1}}
.ws-pcard__kanji{{font-size:1rem;color:rgba(64,101,70,.22);margin-top:2px}}
.ws-pcard__body{{padding:20px 22px 22px}}
.ws-pcard__grade{{font-family:var(--sans);font-size:.58rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--g35);margin-bottom:6px}}
.ws-pcard__origin{{font-family:var(--sans);font-size:.68rem;font-weight:400;color:var(--g50);margin-bottom:4px}}
.ws-pcard__cultivars{{font-family:var(--sans);font-size:.62rem;font-weight:300;color:var(--g35);margin-bottom:8px;line-height:1.5}}
.ws-pcard__desc{{font-weight:300;font-size:.76rem;color:var(--g50);line-height:1.65}}
.ws-pcard__footer{{display:flex;align-items:center;justify-content:space-between;margin-top:14px;flex-wrap:wrap;gap:6px}}
.ws-pcard__badges{{display:flex;gap:6px}}
.ws-pcard__badge{{font-family:var(--sans);font-size:.58rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;padding:4px 10px;border-radius:10px;background:var(--g03);color:var(--g50)}}
.ws-pcard__cta{{font-family:var(--sans);font-size:.68rem;font-weight:400;color:var(--g35);transition:color .3s var(--ease)}}
.ws-pcard:hover .ws-pcard__cta{{color:var(--green)}}

/* Tip cards */
.ws-tips-grid{{display:flex;gap:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}}
.ws-tips-grid::-webkit-scrollbar{{display:none}}
.ws-tip{{min-width:220px;max-width:260px;flex-shrink:0;scroll-snap-align:start;background:var(--white);border:none;border-radius:18px;padding:22px 20px;cursor:pointer;transition:all .5s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.ws-tip:hover{{box-shadow:var(--shadow-m)}}
.ws-tip:active{{transform:scale(.97);transition-duration:.12s}}
.ws-tip__icon{{font-size:1.6rem;margin-bottom:12px;line-height:1}}
.ws-tip__title{{font-family:var(--sans);font-weight:400;font-size:.9rem;color:var(--green);margin-bottom:6px}}
.ws-tip__body{{font-weight:300;font-size:.72rem;color:var(--g50);line-height:1.6}}

/* Cultivar cards */
.ws-cultivars-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.ws-cultivar{{background:var(--white);border:none;border-radius:16px;padding:18px 16px;cursor:default;box-shadow:var(--shadow-s)}}
.ws-cultivar__name{{font-family:var(--sans);font-weight:500;font-size:.82rem;color:var(--green);margin-bottom:2px}}
.ws-cultivar__kanji{{font-size:.68rem;color:var(--g35);margin-bottom:6px}}
.ws-cultivar__char{{font-weight:300;font-size:.68rem;color:var(--g50);line-height:1.5;margin-bottom:8px}}
.ws-cultivar__products{{display:flex;flex-wrap:wrap;gap:4px}}
.ws-cultivar__product-badge{{font-family:var(--sans);font-size:.56rem;font-weight:500;padding:3px 8px;border-radius:8px;background:var(--g03);color:var(--g50)}}

/* Menu cards */
.ws-menu-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.ws-menu-card{{background:var(--white);border:none;border-radius:18px;padding:22px 20px;cursor:pointer;transition:all .5s var(--ease);-webkit-tap-highlight-color:transparent;box-shadow:var(--shadow-s)}}
.ws-menu-card:hover{{box-shadow:var(--shadow-m)}}
.ws-menu-card:active{{transform:scale(.97);transition-duration:.12s}}
.ws-menu-card__icon{{font-size:1.6rem;margin-bottom:12px;line-height:1}}
.ws-menu-card__name{{font-family:var(--sans);font-weight:400;font-size:.9rem;color:var(--green);margin-bottom:4px}}
.ws-menu-card__specs{{font-family:var(--sans);font-size:.62rem;font-weight:500;letter-spacing:.06em;color:var(--g35);margin-bottom:6px}}
.ws-menu-card__desc{{font-weight:300;font-size:.68rem;color:var(--g50);line-height:1.5}}

/* Footer */
.ws-home__footer{{display:flex;align-items:center;gap:24px;margin-top:36px;margin-bottom:max(36px,env(safe-area-inset-bottom))}}
.ws-home__link{{font-size:.64rem;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--g20);text-decoration:none;transition:color .4s var(--ease)}}
.ws-home__link:hover{{color:var(--g50)}}
.ws-home__dot{{width:3px;height:3px;border-radius:50%;background:var(--g12)}}

/* Language toggle */
.ws-lang-toggle{{display:flex;background:var(--g06);border-radius:9px;padding:2px;border:none}}
.ws-lang-btn{{font-family:var(--sans);font-size:.66rem;font-weight:500;letter-spacing:.08em;padding:6px 14px;border:none;cursor:pointer;transition:all .35s var(--ease);-webkit-tap-highlight-color:transparent;background:transparent;color:var(--g35);border-radius:7px;position:relative;z-index:1}}
.ws-lang-btn.active{{background:var(--white);color:var(--green);box-shadow:var(--shadow-s)}}
.ws-brand .ws-lang-toggle{{background:rgba(249,240,226,.1)}}
.ws-brand .ws-lang-btn{{color:rgba(249,240,226,.35);font-size:.6rem;padding:5px 10px}}
.ws-brand .ws-lang-btn.active{{background:rgba(249,240,226,.18);color:var(--cream);box-shadow:none}}

/* Send button */
.ws-send{{width:36px;height:36px;border-radius:50%;border:none;background:var(--green);color:var(--cream);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent;transition:all .4s var(--ease)}}
.ws-send:hover{{opacity:.85;transform:scale(1.04)}}
.ws-send:active{{transform:scale(.88);transition-duration:.1s}}
.ws-send svg{{width:13px;height:13px}}

/* Drawer (mobile) */
.ws-drawer-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.35);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);opacity:0;pointer-events:none;transition:opacity .3s var(--ease);z-index:50}}
.ws-drawer-overlay--open{{opacity:1;pointer-events:auto}}
.ws-drawer{{position:fixed;top:0;left:0;bottom:0;width:280px;max-width:80vw;background:var(--green);transform:translateX(-100%);transition:transform .35s var(--ease);z-index:51;display:flex;flex-direction:column;padding:0}}
.ws-drawer--open{{transform:translateX(0)}}
.ws-drawer__header{{display:flex;align-items:center;justify-content:space-between;padding:max(16px,env(safe-area-inset-top)) 20px 12px}}
.ws-drawer__close{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;color:var(--cream);opacity:.5;cursor:pointer;-webkit-tap-highlight-color:transparent}}
.ws-drawer__close:hover{{opacity:.8}}
.ws-drawer .ws-lang-toggle{{background:rgba(249,240,226,.1)}}
.ws-drawer .ws-lang-btn{{color:rgba(249,240,226,.35);font-size:.6rem;padding:5px 10px}}
.ws-drawer .ws-lang-btn.active{{background:rgba(249,240,226,.18);color:var(--cream);box-shadow:none}}
.ws-drawer__nav{{display:flex;flex-direction:column;gap:2px;padding:8px 12px;flex:1}}
.ws-drawer__nav-item{{display:flex;align-items:center;gap:10px;font-family:var(--sans);font-size:.76rem;font-weight:400;color:rgba(249,240,226,.5);padding:12px 16px;border-radius:10px;cursor:pointer;transition:all .35s var(--ease);border:none;background:transparent;text-align:left;-webkit-tap-highlight-color:transparent;width:100%}}
.ws-drawer__nav-item:hover{{color:var(--cream);background:rgba(249,240,226,.08)}}
.ws-drawer__nav-item svg{{width:16px;height:16px;opacity:.5;flex-shrink:0}}
.ws-drawer__bottom{{padding:16px 20px max(16px,env(safe-area-inset-bottom));margin-top:auto;display:flex;flex-direction:column;gap:8px}}
.ws-drawer__contact{{display:block;text-align:center;font-family:var(--sans);font-size:.64rem;font-weight:400;letter-spacing:.08em;color:rgba(249,240,226,.4);text-decoration:none;padding:12px 16px;border-radius:10px;border:1px solid rgba(249,240,226,.1);transition:all .5s var(--ease)}}
.ws-drawer__contact:hover{{color:var(--cream);border-color:rgba(249,240,226,.28)}}

/* CHAT */
.ws-chat{{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .5s var(--ease),transform .5s var(--ease);z-index:4}}
.ws-chat.ws-hidden{{opacity:0;transform:translateX(20px);pointer-events:none}}
.ws-chat-header{{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px);flex-shrink:0;z-index:10}}
.ws-chat-header__left{{display:flex;align-items:center;gap:12px}}
.ws-back{{display:none;background:none;border:none;color:var(--g50);cursor:pointer;padding:6px 10px 6px 0;-webkit-tap-highlight-color:transparent;transition:color .3s var(--ease)}}
.ws-back:hover{{color:var(--green)}}
.ws-chat-header__logo{{height:16px;opacity:.75;display:none}}
.ws-chat-header__title{{font-family:var(--sans);font-weight:400;font-size:.82rem;letter-spacing:.06em;color:var(--g35)}}
.ws-chat-header__dot{{width:6px;height:6px;border-radius:50%;background:var(--green);opacity:.5;animation:wsBreathe 4s ease-in-out infinite}}
@keyframes wsBreathe{{0%,100%{{opacity:.5;transform:scale(1)}}50%{{opacity:.2;transform:scale(.8)}}}}

/* Messages */
.ws-messages{{flex:1;overflow-y:auto;padding:24px 24px 16px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth;max-width:760px;width:100%;margin:0 auto}}
.ws-messages::-webkit-scrollbar{{width:0;display:none}}
.ws-banner{{text-align:center;padding:10px 16px;margin:0 auto 24px;font-family:var(--sans);font-size:.74rem;font-weight:300;color:var(--g20);letter-spacing:.03em}}
.ws-msg{{display:flex;flex-direction:column;animation:wsMsgIn .5s var(--ease) both}}
@keyframes wsMsgIn{{from{{opacity:0;transform:translateY(8px) scale(.98)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
.ws-msg--bot{{align-items:flex-start;padding-right:48px}}
.ws-msg--bot .ws-msg__bubble{{background:var(--white);border-radius:20px 20px 20px 6px;padding:18px 22px;font-size:.88rem;font-weight:400;line-height:1.85;color:var(--green);box-shadow:var(--shadow-s)}}
.ws-msg__bubble a{{color:var(--green);font-weight:500;text-decoration:underline;text-decoration-color:var(--g12);text-underline-offset:3px;transition:text-decoration-color .3s}}
.ws-msg__bubble a:hover{{text-decoration-color:var(--green)}}
.ws-msg__bubble strong{{font-weight:600}}
.ws-msg__bubble ul,.ws-msg__bubble ol{{margin:10px 0;padding-left:20px}}
.ws-msg__bubble li{{margin:5px 0}}
.ws-msg--user{{align-items:flex-end;padding-left:48px;margin-top:4px}}
.ws-msg--user .ws-msg__bubble{{background:var(--green);color:var(--cream);border-radius:20px 20px 6px 20px;padding:14px 20px;font-size:.88rem;font-weight:400;line-height:1.7;box-shadow:0 2px 8px rgba(64,101,70,.15)}}
.ws-msg--bot+.ws-msg--user,.ws-msg--user+.ws-msg--bot{{margin-top:16px}}
.ws-msg__meta{{margin-top:6px;padding-left:2px}}
.ws-msg__time{{font-size:.58rem;color:var(--g20);letter-spacing:.03em}}
.ws-suggestions{{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}}
.ws-suggestion{{font-family:inherit;font-size:.76rem;font-weight:400;color:var(--green);background:var(--g03);border:none;border-radius:20px;padding:10px 16px;cursor:pointer;transition:all .4s var(--ease);text-align:left;line-height:1.4;-webkit-tap-highlight-color:transparent}}
.ws-suggestion:hover{{background:var(--g06)}}
.ws-suggestion:active{{background:var(--g12);transform:scale(.97);transition-duration:.12s}}
.ws-msg__sources{{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}}
.ws-msg__source{{font-size:.68rem;color:var(--green);text-decoration:none;background:var(--g03);border:none;border-radius:10px;padding:8px 14px;transition:background .4s var(--ease);-webkit-tap-highlight-color:transparent}}
.ws-msg__source:hover{{background:var(--g06)}}
.ws-typing .ws-msg__bubble{{display:flex;gap:6px;align-items:center;padding:18px 22px!important;min-height:44px;box-shadow:var(--shadow-s)}}
.ws-typing .ws-msg__bubble span{{width:5px;height:5px;background:var(--g20);border-radius:50%;display:inline-block;animation:wsTypingBreath 1.8s ease-in-out infinite}}
.ws-typing .ws-msg__bubble span:nth-child(2){{animation-delay:.2s}}
.ws-typing .ws-msg__bubble span:nth-child(3){{animation-delay:.4s}}
@keyframes wsTypingBreath{{0%,60%,100%{{opacity:.15;transform:scale(.8)}}30%{{opacity:.6;transform:scale(1)}}}}
.ws-typing__label{{font-size:.6rem;color:var(--g20);padding-left:2px;margin-top:4px;font-style:italic}}
.ws-quick{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.ws-quick__btn{{font-family:inherit;font-size:.76rem;font-weight:400;color:var(--green);background:var(--white);border:none;border-radius:20px;padding:10px 18px;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:all .4s var(--ease);box-shadow:var(--shadow-s)}}
.ws-quick__btn:hover{{box-shadow:var(--shadow-m);transform:translateY(-1px)}}
.ws-quick__btn:active{{transform:scale(.96);transition-duration:.12s}}

/* Chat input */
.ws-input-area{{padding:12px 24px 16px;flex-shrink:0;max-width:760px;width:100%;margin:0 auto}}
.ws-form{{display:flex;align-items:center;gap:8px;background:var(--white);border:none;border-radius:28px;padding:5px 5px 5px 22px;transition:box-shadow .5s var(--ease);box-shadow:var(--shadow-s)}}
.ws-form:focus-within{{box-shadow:var(--shadow-m)}}
.ws-input{{flex:1;border:none;background:transparent;color:var(--green);font-family:inherit;font-size:.88rem;font-weight:400;outline:none;padding:11px 0}}
.ws-input::placeholder{{color:var(--g35);font-weight:300}}

/* Chat footer */
.ws-chat-footer{{display:flex;align-items:center;justify-content:center;gap:16px;padding:4px 24px max(8px,env(safe-area-inset-bottom));flex-shrink:0}}
.ws-chat-footer__link{{font-size:.58rem;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--g20);text-decoration:none;transition:color .4s var(--ease)}}
.ws-chat-footer__link:hover{{color:var(--g50)}}
.ws-chat-footer__dot{{width:2px;height:2px;border-radius:50%;background:var(--g12)}}

@keyframes wsFadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Desktop */
@media(min-width:900px){{
  .ws-topbar{{display:none}}.ws-drawer,.ws-drawer-overlay{{display:none}}
  .ws-products-grid{{flex-wrap:wrap;overflow-x:visible;scroll-snap-type:none}}
  .ws-products-grid>.ws-pcard{{min-width:0;max-width:none;flex:1 1 calc(33.333% - 12px)}}
  .ws-cultivars-grid{{grid-template-columns:repeat(3,1fr)}}
  .ws-msg--bot{{padding-right:80px}}.ws-msg--user{{padding-left:80px}}
  .ws-hero{{min-height:min(280px,34vh)}}
}}
/* Mobile */
@media(max-width:899px){{
  .ws-brand{{display:none}}
  #ws-app{{height:100vh;height:100dvh}}
  .ws-back{{display:block}}.ws-chat-header__logo{{display:block}}
  .ws-chat-header{{padding:max(12px,env(safe-area-inset-top)) 18px 12px}}
  .ws-messages{{padding:18px 18px 10px;-webkit-overflow-scrolling:touch}}
  .ws-msg--bot{{padding-right:20px}}.ws-msg--user{{padding-left:44px}}
  .ws-msg--bot .ws-msg__bubble{{padding:16px 18px}}
  .ws-quick{{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;scrollbar-width:none}}
  .ws-quick::-webkit-scrollbar{{display:none}}.ws-quick__btn{{white-space:nowrap;flex-shrink:0}}
  .ws-input-area{{padding:10px 16px 6px;background:rgba(249,240,226,.88);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}}
  .ws-form{{padding:4px 4px 4px 18px}}.ws-input{{font-size:16px;padding:12px 0;min-height:44px}}.ws-send{{width:38px;height:38px}}
  .ws-chat-footer{{padding:4px 16px max(6px,env(safe-area-inset-bottom))}}
  .ws-hero{{padding:0 22px}}.ws-hero__input-wrap{{max-width:400px}}
  .ws-topics{{padding:0 22px}}.ws-section{{padding:0 22px}}
}}
@media(max-width:430px){{
  .ws-messages{{padding:14px 12px 8px}}
  .ws-msg--bot .ws-msg__bubble,.ws-msg--user .ws-msg__bubble{{font-size:.86rem;padding:14px 16px}}
  .ws-input-area{{padding:8px 12px 4px}}.ws-send{{width:36px;height:36px}}
  .ws-chat-footer{{padding:3px 12px max(4px,env(safe-area-inset-bottom))}}
  .ws-hero{{padding:0 18px}}.ws-hero__heading{{font-size:1.35rem}}
  .ws-topics{{padding:0 18px;gap:8px}}.ws-topics__pill{{padding:10px 18px;font-size:.74rem}}
  .ws-section{{padding:0 18px;margin-top:24px}}
  .ws-cultivars-grid{{gap:10px}}.ws-menu-grid{{gap:10px}}
}}
/* Gate */
.ws-gate{{display:flex;align-items:center;justify-content:center;min-height:100vh;min-height:100dvh;background:var(--cream);padding:24px}}
.ws-gate.ws-hidden{{display:none}}
.ws-gate__card{{background:var(--white);border-radius:24px;padding:48px 36px;max-width:420px;width:100%;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.06)}}
.ws-gate__logo{{width:80px;margin:0 auto 24px}}
.ws-gate__q{{font-family:var(--font);font-size:1.15rem;font-weight:600;color:var(--green);margin-bottom:8px}}
.ws-gate__sub{{font-family:var(--font);font-size:.88rem;color:rgba(64,101,70,.55);margin-bottom:32px}}
.ws-gate__btns{{display:flex;gap:12px;justify-content:center;margin-bottom:0}}
.ws-gate__btn{{flex:1;padding:14px 20px;border-radius:14px;font-family:var(--font);font-size:.92rem;font-weight:600;cursor:pointer;border:none;transition:all .3s ease}}
.ws-gate__btn--yes{{background:var(--green);color:var(--white)}}
.ws-gate__btn--yes:hover{{opacity:.88}}
.ws-gate__btn--no{{background:rgba(64,101,70,.08);color:var(--green)}}
.ws-gate__btn--no:hover{{background:rgba(64,101,70,.14)}}
.ws-gate__email{{display:none;margin-top:24px}}
.ws-gate__email.ws-gate__email--show{{display:block}}
.ws-gate__email-label{{font-family:var(--font);font-size:.85rem;color:rgba(64,101,70,.6);margin-bottom:10px;display:block}}
.ws-gate__email-wrap{{display:flex;gap:8px}}
.ws-gate__email-input{{flex:1;padding:12px 16px;border:1.5px solid rgba(64,101,70,.15);border-radius:12px;font-family:var(--font);font-size:.92rem;outline:none;transition:border-color .2s}}
.ws-gate__email-input:focus{{border-color:var(--green)}}
.ws-gate__email-submit{{padding:12px 24px;background:var(--green);color:var(--white);border:none;border-radius:12px;font-family:var(--font);font-size:.92rem;font-weight:600;cursor:pointer;transition:opacity .2s;white-space:nowrap}}
.ws-gate__email-submit:hover{{opacity:.88}}
.ws-gate__lang{{position:absolute;top:16px;right:16px}}
/* Inquiry Modal */
.ws-inquiry-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.4);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);z-index:100;opacity:0;pointer-events:none;transition:opacity .3s ease;display:flex;align-items:center;justify-content:center}}
.ws-inquiry-overlay--open{{opacity:1;pointer-events:auto}}
.ws-inquiry{{background:var(--white);border-radius:24px;padding:36px 32px;max-width:440px;width:calc(100% - 48px);box-shadow:0 8px 40px rgba(0,0,0,.12);transform:translateY(20px) scale(.97);transition:transform .35s ease;position:relative}}
.ws-inquiry-overlay--open .ws-inquiry{{transform:translateY(0) scale(1)}}
.ws-inquiry__close{{position:absolute;top:16px;right:16px;width:32px;height:32px;border:none;background:var(--g03);border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--g50);transition:background .2s}}
.ws-inquiry__close:hover{{background:var(--g06)}}
.ws-inquiry__title{{font-family:var(--sans);font-size:1.1rem;font-weight:600;color:var(--green);margin-bottom:24px;text-align:center}}
.ws-inquiry__tier{{border:1.5px solid var(--g06);border-radius:16px;padding:20px;margin-bottom:12px;transition:border-color .2s}}
.ws-inquiry__tier:last-child{{margin-bottom:0}}
.ws-inquiry__tier:hover{{border-color:var(--g12)}}
.ws-inquiry__tier-label{{font-family:var(--sans);font-size:.72rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--g35);margin-bottom:6px}}
.ws-inquiry__tier-range{{font-family:var(--sans);font-size:1rem;font-weight:600;color:var(--green);margin-bottom:4px}}
.ws-inquiry__tier-desc{{font-family:var(--sans);font-size:.82rem;font-weight:300;color:var(--g50);margin-bottom:14px;line-height:1.5}}
.ws-inquiry__tier-btn{{display:inline-block;font-family:var(--sans);font-size:.82rem;font-weight:600;text-decoration:none;padding:12px 28px;border-radius:12px;cursor:pointer;transition:opacity .2s;border:none}}
.ws-inquiry__tier-btn--shop{{background:var(--green);color:var(--white)}}
.ws-inquiry__tier-btn--shop:hover{{opacity:.88}}
.ws-inquiry__tier-btn--email{{background:rgba(64,101,70,.08);color:var(--green)}}
.ws-inquiry__tier-btn--email:hover{{background:rgba(64,101,70,.14)}}
</style>
</head>
<body>
<!-- GATE -->
<div id="ws-gate" class="ws-gate">
  <div class="ws-gate__lang">
    <div class="ws-lang-toggle" id="ws-lang-gate">
      <button class="ws-lang-btn active" data-lang="en">EN</button>
      <button class="ws-lang-btn" data-lang="ja">JA</button>
    </div>
  </div>
  <div class="ws-gate__card">
    <img class="ws-gate__logo" src="data:image/png;base64,{_LOGO_WM_WHITE_B64}" alt="NAKAI" />
    <p class="ws-gate__q" id="ws-gate-q">Are you a NAKAI wholesale partner?</p>
    <p class="ws-gate__sub" id="ws-gate-sub">Access our wholesale partner portal</p>
    <div class="ws-gate__btns">
      <button class="ws-gate__btn ws-gate__btn--yes" id="ws-gate-yes">Yes</button>
      <button class="ws-gate__btn ws-gate__btn--no" id="ws-gate-no">No, but I'm interested</button>
    </div>
    <div class="ws-gate__email" id="ws-gate-email">
      <label class="ws-gate__email-label" id="ws-gate-email-label">Enter your email to access the portal</label>
      <form class="ws-gate__email-wrap" id="ws-gate-email-form">
        <input type="email" class="ws-gate__email-input" id="ws-gate-email-input" placeholder="your@email.com" required />
        <button type="submit" class="ws-gate__email-submit" id="ws-gate-email-submit">Continue</button>
      </form>
    </div>
  </div>
</div>
<!-- INQUIRY MODAL -->
<div class="ws-inquiry-overlay" id="ws-inquiry-overlay">
  <div class="ws-inquiry">
    <button class="ws-inquiry__close" id="ws-inquiry-close">&times;</button>
    <h2 class="ws-inquiry__title" id="ws-inquiry-title">Wholesale Inquiry</h2>
    <div class="ws-inquiry__tier">
      <div class="ws-inquiry__tier-label" id="ws-inq-label1">SMALL ORDER</div>
      <div class="ws-inquiry__tier-range" id="ws-inq-range1">Under 10 kg</div>
      <div class="ws-inquiry__tier-desc" id="ws-inq-desc1">Purchase directly from our online store with fast shipping.</div>
      <a href="https://nakaimatcha.com" target="_blank" rel="noopener" class="ws-inquiry__tier-btn ws-inquiry__tier-btn--shop" id="ws-inq-btn1">Shop Now</a>
    </div>
    <div class="ws-inquiry__tier">
      <div class="ws-inquiry__tier-label" id="ws-inq-label2">BULK ORDER</div>
      <div class="ws-inquiry__tier-range" id="ws-inq-range2">10 kg &ndash; 100 t</div>
      <div class="ws-inquiry__tier-desc" id="ws-inq-desc2">Contact our team for custom pricing and logistics.</div>
      <a href="mailto:wholesale@nakaiinfo.com" class="ws-inquiry__tier-btn ws-inquiry__tier-btn--email" id="ws-inq-btn2">Email Us</a>
    </div>
  </div>
</div>
<!-- APP -->
<div id="ws-app" class="ws-hidden">
  <!-- Desktop sidebar -->
  <aside class="ws-brand">
    <div class="ws-brand__top">
      <div class="ws-brand__top-row">
        <img class="ws-brand__logo" src="data:image/png;base64,{_LOGO_WM_WHITE_B64}" alt="NAKAI" />
        <div class="ws-lang-toggle" id="ws-lang-brand">
          <button class="ws-lang-btn active" data-lang="en">EN</button>
          <button class="ws-lang-btn" data-lang="ja">JA</button>
        </div>
      </div>
      <p class="ws-brand__tagline">Wholesale Partner Portal</p>
    </div>
    <nav class="ws-brand__nav">
      <button class="ws-brand__nav-item" id="ws-nav-home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg><span id="ws-nav-home-label">Home</span></button>
      <button class="ws-brand__nav-item" id="ws-nav-products"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg><span id="ws-nav-products-label">Products</span></button>
      <button class="ws-brand__nav-item" id="ws-nav-barista"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg><span id="ws-nav-barista-label">Barista Guide</span></button>
      <button class="ws-brand__nav-item" id="ws-nav-cultivars"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c1.5 0 2-1 2-2v-1c0-.5.2-1 .6-1.4.4-.4.9-.6 1.4-.6h2c2.2 0 4-1.8 4-4 0-5-4.5-10-10-10z"/><circle cx="7.5" cy="11.5" r="1.5"/><circle cx="12" cy="7.5" r="1.5"/><circle cx="16.5" cy="11.5" r="1.5"/></svg><span id="ws-nav-cultivars-label">Cultivars</span></button>
      <button class="ws-brand__nav-item" id="ws-nav-chat"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg><span id="ws-nav-chat-label">Chat</span></button>
    </nav>
    <div class="ws-brand__bottom">
      <a href="/app" class="ws-brand__contact" id="ws-nav-consumer">Consumer App</a>
      <button class="ws-brand__contact" id="ws-nav-inquiry">Wholesale Inquiry</button>
      <p class="ws-brand__copy">&copy; NAKAI Matcha</p>
    </div>
  </aside>

  <div class="ws-main">
    <!-- HOME VIEW -->
    <div class="ws-home" id="ws-home">
      <div class="ws-topbar" id="ws-topbar">
        <div class="ws-topbar__left">
          <button class="ws-hamburger" id="ws-hamburger" aria-label="Menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
          </button>
          <img class="ws-topbar__wordmark" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" id="ws-topbar-mark" />
        </div>
        <div class="ws-topbar__right">
          <div class="ws-lang-toggle" id="ws-lang-home">
            <button class="ws-lang-btn active" data-lang="en">EN</button>
            <button class="ws-lang-btn" data-lang="ja">JA</button>
          </div>
        </div>
      </div>
      <div class="ws-home__scroll" id="ws-home-scroll">
        <div class="ws-hero">
          <p class="ws-hero__sub" id="ws-hero-sub">Wholesale Partner Portal</p>
          <h1 class="ws-hero__heading" id="ws-hero-heading">Specialty matcha for professionals</h1>
          <div class="ws-hero__input-wrap">
            <form class="ws-hero__form" id="ws-hero-form">
              <input type="text" class="ws-hero__input" id="ws-hero-input" autocomplete="off" maxlength="500" />
              <button type="submit" class="ws-send" aria-label="Send">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
              </button>
            </form>
          </div>
        </div>
        <div class="ws-topics" id="ws-topics">
          <button class="ws-topics__pill" id="ws-t-compare">Compare Products</button>
          <button class="ws-topics__pill" id="ws-t-latte">Latte Recipe</button>
          <button class="ws-topics__pill" id="ws-t-cultivar">Cultivar Guide</button>
          <button class="ws-topics__pill" id="ws-t-contact">Contact Us</button>
        </div>
        <div class="ws-section">
          <h2 class="ws-section__title" id="ws-sec-products">Product Lineup</h2>
          <div class="ws-products-grid" id="ws-product-cards"></div>
        </div>
        <div class="ws-section">
          <h2 class="ws-section__title" id="ws-sec-barista">Barista Guide</h2>
          <div class="ws-tips-grid" id="ws-tip-cards"></div>
        </div>
        <div class="ws-section">
          <h2 class="ws-section__title" id="ws-sec-cultivars">Cultivar Library</h2>
          <div class="ws-cultivars-grid" id="ws-cultivar-cards"></div>
        </div>
        <div class="ws-section">
          <h2 class="ws-section__title" id="ws-sec-menu">Menu Ideas</h2>
          <div class="ws-menu-grid" id="ws-menu-cards"></div>
        </div>
        <div class="ws-home__footer">
          <a href="/app" class="ws-home__link" id="ws-f-consumer">Consumer App</a>
          <span class="ws-home__dot"></span>
          <a href="#" class="ws-home__link" id="ws-f-inquiry">Wholesale Inquiry</a>
          <span class="ws-home__dot"></span>
          <a href="https://nakaimatcha.com" target="_blank" rel="noopener" class="ws-home__link">nakaimatcha.com</a>
        </div>
      </div>
    </div>

    <!-- Mobile drawer -->
    <div class="ws-drawer-overlay" id="ws-drawer-overlay"></div>
    <nav class="ws-drawer" id="ws-drawer">
      <div class="ws-drawer__header">
        <div class="ws-lang-toggle" id="ws-lang-drawer">
          <button class="ws-lang-btn active" data-lang="en">EN</button>
          <button class="ws-lang-btn" data-lang="ja">JA</button>
        </div>
        <button class="ws-drawer__close" id="ws-drawer-close" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>
      </div>
      <div class="ws-drawer__nav">
        <button class="ws-drawer__nav-item" id="ws-dnav-home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/></svg><span id="ws-dnav-home-label">Home</span></button>
        <button class="ws-drawer__nav-item" id="ws-dnav-products"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg><span id="ws-dnav-products-label">Products</span></button>
        <button class="ws-drawer__nav-item" id="ws-dnav-barista"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg><span id="ws-dnav-barista-label">Barista Guide</span></button>
        <button class="ws-drawer__nav-item" id="ws-dnav-cultivars"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c1.5 0 2-1 2-2v-1c0-.5.2-1 .6-1.4.4-.4.9-.6 1.4-.6h2c2.2 0 4-1.8 4-4 0-5-4.5-10-10-10z"/><circle cx="7.5" cy="11.5" r="1.5"/><circle cx="12" cy="7.5" r="1.5"/><circle cx="16.5" cy="11.5" r="1.5"/></svg><span id="ws-dnav-cultivars-label">Cultivars</span></button>
        <button class="ws-drawer__nav-item" id="ws-dnav-chat"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg><span id="ws-dnav-chat-label">Chat</span></button>
      </div>
      <div class="ws-drawer__bottom">
        <a href="/app" class="ws-drawer__contact" id="ws-dnav-consumer">Consumer App</a>
        <button class="ws-drawer__contact" id="ws-dnav-inquiry" style="cursor:pointer">Wholesale Inquiry</button>
      </div>
    </nav>

    <!-- CHAT VIEW -->
    <div class="ws-chat ws-hidden" id="ws-chat">
      <header class="ws-chat-header">
        <div class="ws-chat-header__left">
          <button class="ws-back" id="ws-back" aria-label="Back"><svg width="10" height="18" viewBox="0 0 10 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 1L1 9l8 8"/></svg></button>
          <img class="ws-chat-header__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
          <span class="ws-chat-header__title" id="ws-chat-title">Wholesale Specialist</span>
          <span class="ws-chat-header__dot"></span>
        </div>
        <div class="ws-chat-header__right">
          <div class="ws-lang-toggle" id="ws-lang-chat">
            <button class="ws-lang-btn active" data-lang="en">EN</button>
            <button class="ws-lang-btn" data-lang="ja">JA</button>
          </div>
        </div>
      </header>
      <div class="ws-messages" id="ws-messages">
        <div class="ws-banner" id="ws-banner-text">AI-powered answers for wholesale partners</div>
        <div class="ws-msg ws-msg--bot" id="ws-welcome">
          <div class="ws-msg__bubble" id="ws-greeting"></div>
          <div class="ws-quick" id="ws-quick"></div>
        </div>
      </div>
      <div class="ws-input-area">
        <form class="ws-form" id="ws-form">
          <input type="text" class="ws-input" id="ws-input" autocomplete="off" maxlength="500" />
          <button type="submit" class="ws-send" aria-label="Send">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg>
          </button>
        </form>
      </div>
      <div class="ws-chat-footer">
        <a href="/app" class="ws-chat-footer__link" id="ws-cf-consumer">Consumer App</a>
        <span class="ws-chat-footer__dot"></span>
        <a href="#" class="ws-chat-footer__link" id="ws-cf-inquiry">Inquiry</a>
        <span class="ws-chat-footer__dot"></span>
        <a href="https://nakaimatcha.com" target="_blank" rel="noopener" class="ws-chat-footer__link">Shop</a>
      </div>
    </div>
  </div>
</div>

<script>
(function(){{
  'use strict';
  var MAX_H=20;
  var chatHistory=[];
  var loading=false;
  var SESSION_ID=(function(){{var id=localStorage.getItem('nakai_ws_session_id');if(!id){{id=crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c){{var r=Math.random()*16|0;return(c==='x'?r:(r&0x3|0x8)).toString(16)}});localStorage.setItem('nakai_ws_session_id',id)}}return id}})();

  var i18n={{
    en:{{
      greeting:"Welcome! I'm your wholesale matcha specialist. How can I help your business today?",
      placeholder:'Ask about products, recipes, cultivars...',
      typing:'Thinking...',
      banner:'AI-powered answers for wholesale partners',
      chatTitle:'Wholesale Specialist',
      q1:'Compare products',q1m:'Compare the NAKAI wholesale matcha products. What are the key differences in grade, origin, and recommended use?',
      q2:'Latte recipe',q2m:'What is the ideal matcha latte recipe for a cafe setting? Include dosing, temperature, and milk recommendations.',
      q3:'Storage guide',q3m:'What are the best practices for storing matcha in a commercial kitchen environment?',
      q4:'Order inquiry',q4m:'I would like to place a wholesale order. What are the available formats and minimum order quantities?',
      error:"Connection issue. Please try again.",
      heroSub:'Wholesale Partner Portal',heroHeading:'Specialty matcha for professionals',
      tCompare:'Compare Products',tLatte:'Latte Recipe',tCultivar:'Cultivar Guide',tInquiry:'Wholesale Inquiry',
      inquiryTitle:'Wholesale Inquiry',inqLabel1:'SMALL ORDER',inqRange1:'Under 10 kg',inqDesc1:'Purchase directly from our online store with fast shipping.',inqBtn1:'Shop Now',inqLabel2:'BULK ORDER',inqRange2:'10 kg \u2013 100 t',inqDesc2:'Contact our team for custom pricing and logistics.',inqBtn2:'Email Us',
      compareMsg:'Compare the NAKAI wholesale matcha products. What are the key differences in grade, origin, and recommended use?',
      latteMsg:'What is the ideal matcha latte recipe for a cafe setting? Include dosing, temperature, and milk recommendations.',
      cultivarMsg:'Tell me about the different matcha cultivars used in NAKAI products. How do they differ in flavor profile?',
      contactMsg:'I would like to get in touch about a wholesale partnership. What information do you need from me?',
      secProducts:'Product Lineup',secBarista:'Barista Guide',secCultivars:'Cultivar Library',secMenu:'Menu Ideas',
      navHome:'Home',navProducts:'Products',navBarista:'Barista Guide',navCultivars:'Cultivars',navChat:'Chat',
      pAsk:'Ask about this',
      /* Products */
      p111name:'111',p111grade:'Organic Ceremonial Reserve',p111origin:'Kagoshima',p111milling:'Micro-Milled',
      p111cultivars:'Saemidori, Yutakamidori, Asanoka, Yabukita',
      p111desc:'4-cultivar micro-milled blend. Creamy body, layered umami.',
      p111msg:'Tell me about NAKAI 111 matcha. What makes it special for a cafe or restaurant setting?',
      p101name:'101',p101grade:'Organic Specialty',p101origin:'Kirishima',p101milling:'Stone-Milled',
      p101cultivars:'Asahi, Kirari 31, Saemidori',
      p101desc:'Single origin from Kirishima. Vivid umami, elegant finish.',
      p101msg:'Tell me about NAKAI 101 matcha. How does the Kirishima single origin compare to blends?',
      p102name:'102',p102grade:'Organic Specialty',p102origin:'Kagoshima \u00d7 Uji',p102milling:'Stone-Milled',
      p102cultivars:'Okumidori, Saemidori, Gokou',
      p102desc:'Cross-region blend. Balanced sweetness, 500kg annual limit.',
      p102msg:'Tell me about NAKAI 102 matcha. Why is it limited to 500kg annually?',
      p103name:'103',p103grade:'Organic Specialty',p103origin:'Kagoshima',p103milling:'Stone-Milled',
      p103cultivars:'Okumidori, Saemidori',
      p103desc:'Bold umami forward. Full body, deep green.',
      p103msg:'Tell me about NAKAI 103 matcha. What kind of drinks does it work best in?',
      p211name:'211',p211grade:'Ceremonial',p211origin:'Yame',p211milling:'Stone-Milled',
      p211cultivars:'Yabukita, Saemidori, Okumidori',
      p211desc:'Yame single origin. Clean, classic profile.',
      p211msg:'Tell me about NAKAI 211 matcha. How does the Yame origin affect the flavor?',
      p212name:'212',p212grade:'Ceremonial',p212origin:'Blend',p212milling:'Stone-Milled',
      p212cultivars:'Saemidori, Gokou, Yabukita',
      p212desc:'Latte-optimized. 1st + 2nd harvest for milk pairing.',
      p212msg:'Tell me about NAKAI 212 matcha. Why is it optimized for lattes?',
      /* Tips */
      tip1title:'Dosing & Sifting',tip1body:'2-3g per shot. Always sift for smooth extraction.',
      tip1msg:'What is the proper dosing and sifting technique for matcha in a professional setting?',
      tip2title:'Milk Pairing',tip2body:'Oat for sweetness, whole for body, almond for nuttiness.',
      tip2msg:'What milk types pair best with matcha for lattes? Compare oat, whole, almond, and soy.',
      tip3title:'Storage',tip3body:'Nitrogen-flush sealed. Freeze unopened, refrigerate once open.',
      tip3msg:'How should I store matcha in a commercial kitchen? What about nitrogen-flush packaging?',
      tip4title:'Temperature',tip4body:'70-80\u00b0C for specialty, never boiling. Affects umami extraction.',
      tip4msg:'What is the ideal water temperature for different grades of matcha?',
      tip5title:'Troubleshooting',tip5body:'Bitterness? Lower temp. Clumps? Sift more. Dull color? Check freshness.',
      tip5msg:'I am having issues with my matcha drinks. Help me troubleshoot bitterness, clumping, and dull color.',
      /* Cultivars */
      cv1name:'Saemidori',cv1kanji:'\u3055\u3048\u307f\u3069\u308a',cv1char:'Sweet, balanced, mild umami',
      cv2name:'Asahi',cv2kanji:'\u3042\u3055\u3072',cv2char:'Rich umami, full body, traditional',
      cv3name:'Okumidori',cv3kanji:'\u304a\u304f\u307f\u3069\u308a',cv3char:'Deep green, clean finish',
      cv4name:'Yutakamidori',cv4kanji:'\u3086\u305f\u304b\u307f\u3069\u308a',cv4char:'Vibrant color, fresh aroma',
      cv5name:'Yabukita',cv5kanji:'\u3084\u3076\u304d\u305f',cv5char:'Classic, robust, reliable',
      cv6name:'Kirari 31',cv6kanji:'\u304d\u3089\u308a31',cv6char:'New cultivar, bright, delicate',
      cv7name:'Gokou',cv7kanji:'\u3054\u3053\u3046',cv7char:'Rich aroma, creamy, Uji specialty',
      /* Menu */
      menu1name:'Matcha Shot',menu1specs:'2g \u00b7 60ml \u00b7 75\u00b0C',menu1desc:'Pure foundation for every matcha drink',
      menu1msg:'How do I make the perfect matcha shot for cafe service?',
      menu2name:'Matcha Latte',menu2specs:'3g \u00b7 60ml \u00b7 200ml milk',menu2desc:'Hot or iced, the cafe bestseller',
      menu2msg:'Give me the ideal matcha latte recipe for a cafe menu.',
      menu3name:'Matcha Americano',menu3specs:'2g \u00b7 60ml \u00b7 150ml water',menu3desc:'Light, refreshing, easy to customize',
      menu3msg:'How do I make a matcha americano? What variations can I offer?',
      menu4name:'Signature Cocktail',menu4specs:'3g \u00b7 various',menu4desc:'Creative matcha-based beverages',
      menu4msg:'What are some creative matcha cocktail or mocktail recipes for a bar or restaurant?',
      gateQ:'Are you a NAKAI wholesale partner?',gateSub:'Access our wholesale partner portal',
      gateYes:'Yes',gateNo:"No, but I'm interested",
      gateEmailLabel:'Enter your email to access the portal',gateSubmit:'Continue',
      consumerApp:'Consumer App',
    }},
    ja:{{
      greeting:'\u3088\u3046\u3053\u305d\uff01\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u62b9\u8336\u30b9\u30da\u30b7\u30e3\u30ea\u30b9\u30c8\u3067\u3059\u3002\u30d3\u30b8\u30cd\u30b9\u306e\u304a\u624b\u4f1d\u3044\u3092\u3044\u305f\u3057\u307e\u3059\u3002',
      placeholder:'\u5546\u54c1\u3001\u30ec\u30b7\u30d4\u3001\u54c1\u7a2e\u306b\u3064\u3044\u3066\u8cea\u554f...',
      typing:'\u8003\u3048\u4e2d...',
      banner:'AI\u304c\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30d1\u30fc\u30c8\u30ca\u30fc\u5411\u3051\u306b\u56de\u7b54\u3057\u307e\u3059',
      chatTitle:'\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30b9\u30da\u30b7\u30e3\u30ea\u30b9\u30c8',
      q1:'\u5546\u54c1\u6bd4\u8f03',q1m:'NAKAI\u306e\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u62b9\u8336\u5546\u54c1\u3092\u6bd4\u8f03\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u30b0\u30ec\u30fc\u30c9\u3001\u7523\u5730\u3001\u63a8\u5968\u7528\u9014\u306e\u4e3b\u306a\u9055\u3044\u306f\uff1f',
      q2:'\u30e9\u30c6\u30ec\u30b7\u30d4',q2m:'\u30ab\u30d5\u30a7\u3067\u306e\u7406\u60f3\u7684\u306a\u62b9\u8336\u30e9\u30c6\u30ec\u30b7\u30d4\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u5206\u91cf\u3001\u6e29\u5ea6\u3001\u30df\u30eb\u30af\u306e\u63a8\u5968\u3092\u542b\u3081\u3066\u3002',
      q3:'\u4fdd\u5b58\u30ac\u30a4\u30c9',q3m:'\u5546\u696d\u7528\u30ad\u30c3\u30c1\u30f3\u3067\u306e\u62b9\u8336\u4fdd\u5b58\u306e\u30d9\u30b9\u30c8\u30d7\u30e9\u30af\u30c6\u30a3\u30b9\u306f\uff1f',
      q4:'\u6ce8\u6587\u306b\u3064\u3044\u3066',q4m:'\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u6ce8\u6587\u3092\u3057\u305f\u3044\u3067\u3059\u3002\u5229\u7528\u53ef\u80fd\u306a\u30d5\u30a9\u30fc\u30de\u30c3\u30c8\u3068\u6700\u4f4e\u6ce8\u6587\u6570\u91cf\u306f\uff1f',
      error:'\u63a5\u7d9a\u306b\u554f\u984c\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002\u3082\u3046\u4e00\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002',
      heroSub:'\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30d1\u30fc\u30c8\u30ca\u30fc\u30dd\u30fc\u30bf\u30eb',heroHeading:'\u30d7\u30ed\u30d5\u30a7\u30c3\u30b7\u30e7\u30ca\u30eb\u306e\u305f\u3081\u306e\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3\u62b9\u8336',
      tCompare:'\u5546\u54c1\u6bd4\u8f03',tLatte:'\u30e9\u30c6\u30ec\u30b7\u30d4',tCultivar:'\u54c1\u7a2e\u30ac\u30a4\u30c9',tInquiry:'\u304a\u554f\u3044\u5408\u308f\u305b',
      inquiryTitle:'\u304a\u554f\u3044\u5408\u308f\u305b',inqLabel1:'\u5c11\u91cf\u6ce8\u6587',inqRange1:'10 kg \u672a\u6e80',inqDesc1:'\u30aa\u30f3\u30e9\u30a4\u30f3\u30b9\u30c8\u30a2\u304b\u3089\u76f4\u63a5\u8cfc\u5165\u3044\u305f\u3060\u3051\u307e\u3059\u3002',inqBtn1:'\u30b7\u30e7\u30c3\u30d7\u3078',inqLabel2:'\u5927\u53e3\u6ce8\u6587',inqRange2:'10 kg \u2013 100 t',inqDesc2:'\u4fa1\u683c\u3068\u7269\u6d41\u306b\u3064\u3044\u3066\u304a\u554f\u3044\u5408\u308f\u305b\u304f\u3060\u3055\u3044\u3002',inqBtn2:'\u30e1\u30fc\u30eb\u3059\u308b',
      compareMsg:'NAKAI\u306e\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u62b9\u8336\u5546\u54c1\u3092\u6bd4\u8f03\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u30b0\u30ec\u30fc\u30c9\u3001\u7523\u5730\u3001\u63a8\u5968\u7528\u9014\u306e\u4e3b\u306a\u9055\u3044\u306f\uff1f',
      latteMsg:'\u30ab\u30d5\u30a7\u3067\u306e\u7406\u60f3\u7684\u306a\u62b9\u8336\u30e9\u30c6\u30ec\u30b7\u30d4\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u5206\u91cf\u3001\u6e29\u5ea6\u3001\u30df\u30eb\u30af\u306e\u63a8\u5968\u3092\u542b\u3081\u3066\u3002',
      cultivarMsg:'NAKAI\u88fd\u54c1\u306b\u4f7f\u308f\u308c\u3066\u3044\u308b\u62b9\u8336\u306e\u54c1\u7a2e\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u98a8\u5473\u30d7\u30ed\u30d5\u30a1\u30a4\u30eb\u306e\u9055\u3044\u306f\uff1f',
      contactMsg:'\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30d1\u30fc\u30c8\u30ca\u30fc\u30b7\u30c3\u30d7\u306b\u3064\u3044\u3066\u554f\u3044\u5408\u308f\u305b\u305f\u3044\u3067\u3059\u3002\u3069\u306e\u3088\u3046\u306a\u60c5\u5831\u304c\u5fc5\u8981\u3067\u3059\u304b\uff1f',
      secProducts:'\u5546\u54c1\u30e9\u30a4\u30f3\u30ca\u30c3\u30d7',secBarista:'\u30d0\u30ea\u30b9\u30bf\u30ac\u30a4\u30c9',secCultivars:'\u54c1\u7a2e\u30e9\u30a4\u30d6\u30e9\u30ea',secMenu:'\u30e1\u30cb\u30e5\u30fc\u30a2\u30a4\u30c7\u30a2',
      navHome:'\u30db\u30fc\u30e0',navProducts:'\u5546\u54c1',navBarista:'\u30d0\u30ea\u30b9\u30bf\u30ac\u30a4\u30c9',navCultivars:'\u54c1\u7a2e',navChat:'\u30c1\u30e3\u30c3\u30c8',
      pAsk:'\u8a73\u3057\u304f\u805e\u304f',
      /* Products */
      p111name:'111',p111grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb\u30fb\u30ea\u30b6\u30fc\u30d6',p111origin:'\u9e7f\u5150\u5cf6',p111milling:'\u30de\u30a4\u30af\u30ed\u30df\u30eb',
      p111cultivars:'\u3055\u3048\u307f\u3069\u308a, \u3086\u305f\u304b\u307f\u3069\u308a, \u3042\u3055\u306e\u304b, \u3084\u3076\u304d\u305f',
      p111desc:'4\u54c1\u7a2e\u30de\u30a4\u30af\u30ed\u30df\u30eb\u30d6\u30ec\u30f3\u30c9\u3002\u30af\u30ea\u30fc\u30df\u30fc\u306a\u30dc\u30c7\u30a3\u3001\u5c64\u72b6\u306e\u3046\u307e\u307f\u3002',
      p111msg:'NAKAI 111\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u30ab\u30d5\u30a7\u3084\u30ec\u30b9\u30c8\u30e9\u30f3\u3067\u306e\u4f7f\u3044\u65b9\u306f\uff1f',
      p101name:'101',p101grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p101origin:'\u9727\u5cf6',p101milling:'\u77f3\u81fc\u631d\u304d',
      p101cultivars:'\u3042\u3055\u3072, \u304d\u3089\u308a31, \u3055\u3048\u307f\u3069\u308a',
      p101desc:'\u9727\u5cf6\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3002\u9bae\u3084\u304b\u306a\u3046\u307e\u307f\u3001\u30a8\u30ec\u30ac\u30f3\u30c8\u306a\u5f8c\u5473\u3002',
      p101msg:'NAKAI 101\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u9727\u5cf6\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3068\u30d6\u30ec\u30f3\u30c9\u306e\u9055\u3044\u306f\uff1f',
      p102name:'102',p102grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p102origin:'\u9e7f\u5150\u5cf6\u00d7\u5b87\u6cbb',p102milling:'\u77f3\u81fc\u631d\u304d',
      p102cultivars:'\u304a\u304f\u307f\u3069\u308a, \u3055\u3048\u307f\u3069\u308a, \u3054\u3053\u3046',
      p102desc:'\u7523\u5730\u6a2a\u65ad\u30d6\u30ec\u30f3\u30c9\u3002\u30d0\u30e9\u30f3\u30b9\u306e\u826f\u3044\u7518\u307f\u3002\u5e74\u9593500kg\u9650\u5b9a\u3002',
      p102msg:'NAKAI 102\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u306a\u305c\u5e74\u9593500kg\u9650\u5b9a\u306a\u306e\u3067\u3059\u304b\uff1f',
      p103name:'103',p103grade:'\u30aa\u30fc\u30ac\u30cb\u30c3\u30af\u30fb\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3',p103origin:'\u9e7f\u5150\u5cf6',p103milling:'\u77f3\u81fc\u631d\u304d',
      p103cultivars:'\u304a\u304f\u307f\u3069\u308a, \u3055\u3048\u307f\u3069\u308a',
      p103desc:'\u529b\u5f37\u3044\u3046\u307e\u307f\u3002\u30d5\u30eb\u30dc\u30c7\u30a3\u3001\u6df1\u3044\u7dd1\u3002',
      p103msg:'NAKAI 103\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u3069\u306e\u3088\u3046\u306a\u30c9\u30ea\u30f3\u30af\u306b\u6700\u9069\u3067\u3059\u304b\uff1f',
      p211name:'211',p211grade:'\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb',p211origin:'\u516b\u5973',p211milling:'\u77f3\u81fc\u631d\u304d',
      p211cultivars:'\u3084\u3076\u304d\u305f, \u3055\u3048\u307f\u3069\u308a, \u304a\u304f\u307f\u3069\u308a',
      p211desc:'\u516b\u5973\u30b7\u30f3\u30b0\u30eb\u30aa\u30ea\u30b8\u30f3\u3002\u30af\u30ea\u30fc\u30f3\u3067\u30af\u30e9\u30b7\u30c3\u30af\u306a\u30d7\u30ed\u30d5\u30a1\u30a4\u30eb\u3002',
      p211msg:'NAKAI 211\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u516b\u5973\u7523\u5730\u306e\u5473\u308f\u3044\u306e\u7279\u5fb4\u306f\uff1f',
      p212name:'212',p212grade:'\u30bb\u30ec\u30e2\u30cb\u30a2\u30eb',p212origin:'\u30d6\u30ec\u30f3\u30c9',p212milling:'\u77f3\u81fc\u631d\u304d',
      p212cultivars:'\u3055\u3048\u307f\u3069\u308a, \u3054\u3053\u3046, \u3084\u3076\u304d\u305f',
      p212desc:'\u30e9\u30c6\u7279\u5316\u30021\u756a\u8336+2\u756a\u8336\u306e\u30df\u30eb\u30af\u30da\u30a2\u30ea\u30f3\u30b0\u3002',
      p212msg:'NAKAI 212\u62b9\u8336\u306b\u3064\u3044\u3066\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002\u306a\u305c\u30e9\u30c6\u306b\u6700\u9069\u306a\u306e\u3067\u3059\u304b\uff1f',
      /* Tips */
      tip1title:'\u8a08\u91cf\u3068\u3075\u308b\u3044',tip1body:'1\u30b7\u30e7\u30c3\u30c8\u3042\u305f\u308a2\u301c3g\u3002\u30c0\u30de\u89e3\u6d88\u306e\u305f\u3081\u5fc5\u305a\u3075\u308b\u3046\u3002',
      tip1msg:'\u30d7\u30ed\u306e\u73fe\u5834\u3067\u306e\u6b63\u3057\u3044\u62b9\u8336\u306e\u8a08\u91cf\u3068\u3075\u308b\u3044\u306e\u30c6\u30af\u30cb\u30c3\u30af\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      tip2title:'\u30df\u30eb\u30af\u30da\u30a2\u30ea\u30f3\u30b0',tip2body:'\u30aa\u30fc\u30c4\u306f\u7518\u307f\u3001\u5168\u4e73\u306f\u30dc\u30c7\u30a3\u3001\u30a2\u30fc\u30e2\u30f3\u30c9\u306f\u30ca\u30c3\u30c6\u30a3\u3002',
      tip2msg:'\u62b9\u8336\u30e9\u30c6\u306b\u6700\u9069\u306a\u30df\u30eb\u30af\u306f\uff1f\u30aa\u30fc\u30c4\u3001\u5168\u4e73\u3001\u30a2\u30fc\u30e2\u30f3\u30c9\u3001\u8c46\u4e73\u3092\u6bd4\u8f03\u3057\u3066\u304f\u3060\u3055\u3044\u3002',
      tip3title:'\u4fdd\u5b58\u65b9\u6cd5',tip3body:'\u7a92\u7d20\u5145\u586b\u5bc6\u5c01\u3002\u672a\u958b\u5c01\u306f\u51b7\u51cd\u3001\u958b\u5c01\u5f8c\u306f\u51b7\u8535\u3002',
      tip3msg:'\u5546\u696d\u7528\u30ad\u30c3\u30c1\u30f3\u3067\u306e\u62b9\u8336\u4fdd\u5b58\u306e\u30d9\u30b9\u30c8\u30d7\u30e9\u30af\u30c6\u30a3\u30b9\u306f\uff1f\u7a92\u7d20\u5145\u586b\u30d1\u30c3\u30b1\u30fc\u30b8\u306b\u3064\u3044\u3066\u3082\u3002',
      tip4title:'\u6c34\u6e29\u7ba1\u7406',tip4body:'\u30b9\u30da\u30b7\u30e3\u30eb\u30c6\u30a3\u306f70\u301c80\u00b0C\u3002\u6cb8\u9a30\u6c34\u306f\u53b3\u7981\u3002\u3046\u307e\u307f\u62bd\u51fa\u306b\u5f71\u97ff\u3002',
      tip4msg:'\u62b9\u8336\u306e\u30b0\u30ec\u30fc\u30c9\u5225\u306e\u7406\u60f3\u7684\u306a\u6c34\u6e29\u306f\uff1f',
      tip5title:'\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0',tip5body:'\u82e6\u5473\u2192\u6e29\u5ea6\u3092\u4e0b\u3052\u308b\u3002\u30c0\u30de\u2192\u3075\u308b\u3046\u3002\u8272\u892a\u305b\u2192\u9bae\u5ea6\u78ba\u8a8d\u3002',
      tip5msg:'\u62b9\u8336\u30c9\u30ea\u30f3\u30af\u306e\u554f\u984c\u304c\u3042\u308a\u307e\u3059\u3002\u82e6\u5473\u3001\u30c0\u30de\u3001\u8272\u892a\u305b\u306e\u30c8\u30e9\u30d6\u30eb\u30b7\u30e5\u30fc\u30c6\u30a3\u30f3\u30b0\u3092\u304a\u9858\u3044\u3057\u307e\u3059\u3002',
      /* Cultivars */
      cv1name:'\u3055\u3048\u307f\u3069\u308a',cv1kanji:'\u3055\u3048\u307f\u3069\u308a',cv1char:'\u7518\u307f\u3001\u30d0\u30e9\u30f3\u30b9\u3001\u7a4f\u3084\u304b\u306a\u3046\u307e\u307f',
      cv2name:'\u3042\u3055\u3072',cv2kanji:'\u3042\u3055\u3072',cv2char:'\u8c4a\u304b\u306a\u3046\u307e\u307f\u3001\u30d5\u30eb\u30dc\u30c7\u30a3\u3001\u4f1d\u7d71\u7684',
      cv3name:'\u304a\u304f\u307f\u3069\u308a',cv3kanji:'\u304a\u304f\u307f\u3069\u308a',cv3char:'\u6df1\u3044\u7dd1\u3001\u30af\u30ea\u30a2\u306a\u5f8c\u5473',
      cv4name:'\u3086\u305f\u304b\u307f\u3069\u308a',cv4kanji:'\u3086\u305f\u304b\u307f\u3069\u308a',cv4char:'\u9bae\u3084\u304b\u306a\u8272\u3001\u723d\u3084\u304b\u306a\u9999\u308a',
      cv5name:'\u3084\u3076\u304d\u305f',cv5kanji:'\u3084\u3076\u304d\u305f',cv5char:'\u5b9a\u756a\u3001\u529b\u5f37\u3044\u3001\u5b89\u5b9a\u3057\u305f\u54c1\u8cea',
      cv6name:'\u304d\u3089\u308a31',cv6kanji:'\u304d\u3089\u308a31',cv6char:'\u65b0\u54c1\u7a2e\u3001\u660e\u308b\u3044\u3001\u7e4a\u7d30',
      cv7name:'\u3054\u3053\u3046',cv7kanji:'\u3054\u3053\u3046',cv7char:'\u8c4a\u304b\u306a\u9999\u308a\u3001\u30af\u30ea\u30fc\u30df\u30fc\u3001\u5b87\u6cbb\u7279\u7523',
      /* Menu */
      menu1name:'\u62b9\u8336\u30b7\u30e7\u30c3\u30c8',menu1specs:'2g \u00b7 60ml \u00b7 75\u00b0C',menu1desc:'\u3059\u3079\u3066\u306e\u62b9\u8336\u30c9\u30ea\u30f3\u30af\u306e\u57fa\u672c',
      menu1msg:'\u30ab\u30d5\u30a7\u30b5\u30fc\u30d3\u30b9\u306e\u305f\u3081\u306e\u5b8c\u74a7\u306a\u62b9\u8336\u30b7\u30e7\u30c3\u30c8\u306e\u4f5c\u308a\u65b9\u306f\uff1f',
      menu2name:'\u62b9\u8336\u30e9\u30c6',menu2specs:'3g \u00b7 60ml \u00b7 200ml milk',menu2desc:'\u30db\u30c3\u30c8\u3067\u3082\u30a2\u30a4\u30b9\u3067\u3082\u3002\u30ab\u30d5\u30a7\u306e\u4eba\u6c17No.1',
      menu2msg:'\u30ab\u30d5\u30a7\u30e1\u30cb\u30e5\u30fc\u306b\u6700\u9069\u306a\u62b9\u8336\u30e9\u30c6\u306e\u30ec\u30b7\u30d4\u3092\u6559\u3048\u3066\u304f\u3060\u3055\u3044\u3002',
      menu3name:'\u62b9\u8336\u30a2\u30e1\u30ea\u30ab\u30fc\u30ce',menu3specs:'2g \u00b7 60ml \u00b7 150ml water',menu3desc:'\u8efd\u304f\u3066\u723d\u3084\u304b\u3001\u30ab\u30b9\u30bf\u30de\u30a4\u30ba\u81ea\u5728',
      menu3msg:'\u62b9\u8336\u30a2\u30e1\u30ea\u30ab\u30fc\u30ce\u306e\u4f5c\u308a\u65b9\u306f\uff1f\u3069\u306e\u3088\u3046\u306a\u30d0\u30ea\u30a8\u30fc\u30b7\u30e7\u30f3\u304c\u3042\u308a\u307e\u3059\u304b\uff1f',
      menu4name:'\u30b7\u30b0\u30cd\u30c1\u30e3\u30fc\u30ab\u30af\u30c6\u30eb',menu4specs:'3g \u00b7 various',menu4desc:'\u5275\u4f5c\u62b9\u8336\u30c9\u30ea\u30f3\u30af',
      menu4msg:'\u30d0\u30fc\u3084\u30ec\u30b9\u30c8\u30e9\u30f3\u5411\u3051\u306e\u5275\u4f5c\u62b9\u8336\u30ab\u30af\u30c6\u30eb\u30fb\u30e2\u30af\u30c6\u30eb\u306e\u30ec\u30b7\u30d4\u306f\uff1f',
      gateQ:'NAKAI\u306e\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30d1\u30fc\u30c8\u30ca\u30fc\u3067\u3059\u304b\uff1f',gateSub:'\u30db\u30fc\u30eb\u30bb\u30fc\u30eb\u30d1\u30fc\u30c8\u30ca\u30fc\u30dd\u30fc\u30bf\u30eb\u3078\u30a2\u30af\u30bb\u30b9',
      gateYes:'\u306f\u3044',gateNo:'\u3044\u3044\u3048\u3001\u3067\u3082\u8208\u5473\u304c\u3042\u308a\u307e\u3059',
      gateEmailLabel:'\u30e1\u30fc\u30eb\u30a2\u30c9\u30ec\u30b9\u3092\u5165\u529b\u3057\u3066\u30dd\u30fc\u30bf\u30eb\u306b\u30a2\u30af\u30bb\u30b9',gateSubmit:'\u7d9a\u3051\u308b',
      consumerApp:'\u6d88\u8cbb\u8005\u5411\u3051\u30a2\u30d7\u30ea',
    }}
  }};

  var lang=(function(){{
    var s=localStorage.getItem('nakai_ws_lang');
    if(s&&i18n[s])return s;
    var n=(navigator.language||'en').substring(0,2);
    return i18n[n]?n:'en';
  }})();

  function t(k){{return(i18n[lang]||i18n.en)[k]||i18n.en[k]||''}}
  function $(id){{return document.getElementById(id)}}

  /* Products data */
  var products=[
    {{num:'111',kanji:'\u767e\u5341\u4e00',k:'p111',formats:['straight','latte'],accent:'linear-gradient(170deg,rgba(196,162,64,.15),rgba(196,162,64,.05))'}},
    {{num:'101',kanji:'\u767e\u4e00',k:'p101',formats:['straight'],accent:'linear-gradient(170deg,rgba(64,101,70,.18),rgba(64,101,70,.06))'}},
    {{num:'102',kanji:'\u767e\u4e8c',k:'p102',formats:['straight','latte'],accent:'linear-gradient(170deg,rgba(64,101,70,.16),rgba(64,101,70,.05))'}},
    {{num:'103',kanji:'\u767e\u4e09',k:'p103',formats:['straight','latte'],accent:'linear-gradient(170deg,rgba(64,101,70,.14),rgba(64,101,70,.05))'}},
    {{num:'211',kanji:'\u4e8c\u767e\u5341\u4e00',k:'p211',formats:['straight'],accent:'linear-gradient(170deg,rgba(64,101,70,.10),rgba(64,101,70,.04))'}},
    {{num:'212',kanji:'\u4e8c\u767e\u5341\u4e8c',k:'p212',formats:['latte'],accent:'linear-gradient(170deg,rgba(64,101,70,.10),rgba(64,101,70,.04))'}}
  ];

  var tips=[
    {{icon:'\u2696\ufe0f',k:'tip1'}},
    {{icon:'\U0001f95b',k:'tip2'}},
    {{icon:'\u2744\ufe0f',k:'tip3'}},
    {{icon:'\U0001f321\ufe0f',k:'tip4'}},
    {{icon:'\U0001f527',k:'tip5'}}
  ];

  var cultivars=[
    {{k:'cv1',products:['111','101','102','103','211','212']}},
    {{k:'cv2',products:['101']}},
    {{k:'cv3',products:['102','103','211']}},
    {{k:'cv4',products:['111']}},
    {{k:'cv5',products:['111','211','212']}},
    {{k:'cv6',products:['101']}},
    {{k:'cv7',products:['102','212']}}
  ];

  var menuItems=[
    {{icon:'\U0001f375',k:'menu1'}},
    {{icon:'\U0001f95b',k:'menu2'}},
    {{icon:'\U0001f4a7',k:'menu3'}},
    {{icon:'\U0001f378',k:'menu4'}}
  ];

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

  function setLang(l){{
    lang=l;localStorage.setItem('nakai_ws_lang',l);
    document.documentElement.lang=l;
    document.querySelectorAll('.ws-lang-btn').forEach(function(b){{
      b.classList.toggle('active',b.getAttribute('data-lang')===l);
    }});
    $('ws-input').placeholder=t('placeholder');
    $('ws-banner-text').textContent=t('banner');
    $('ws-greeting').innerHTML=t('greeting');
    $('ws-hero-sub').textContent=t('heroSub');
    $('ws-hero-heading').textContent=t('heroHeading');
    $('ws-hero-input').placeholder=t('placeholder');
    $('ws-chat-title').textContent=t('chatTitle');
    $('ws-t-compare').textContent=t('tCompare');
    $('ws-t-latte').textContent=t('tLatte');
    $('ws-t-cultivar').textContent=t('tCultivar');
    $('ws-t-contact').textContent=t('tInquiry');
    /* Inquiry modal */
    var iq=[['ws-inquiry-title','inquiryTitle'],['ws-inq-label1','inqLabel1'],['ws-inq-range1','inqRange1'],['ws-inq-desc1','inqDesc1'],['ws-inq-btn1','inqBtn1'],['ws-inq-label2','inqLabel2'],['ws-inq-range2','inqRange2'],['ws-inq-desc2','inqDesc2'],['ws-inq-btn2','inqBtn2']];
    iq.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    var il=[['ws-nav-inquiry','tInquiry'],['ws-dnav-inquiry','tInquiry'],['ws-f-inquiry','tInquiry'],['ws-cf-inquiry','tInquiry']];
    il.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    $('ws-sec-products').textContent=t('secProducts');
    $('ws-sec-barista').textContent=t('secBarista');
    $('ws-sec-cultivars').textContent=t('secCultivars');
    $('ws-sec-menu').textContent=t('secMenu');
    /* Gate */
    var gq=$('ws-gate-q');if(gq)gq.textContent=t('gateQ');
    var gs=$('ws-gate-sub');if(gs)gs.textContent=t('gateSub');
    var gy=$('ws-gate-yes');if(gy)gy.textContent=t('gateYes');
    var gn=$('ws-gate-no');if(gn)gn.textContent=t('gateNo');
    var gl=$('ws-gate-email-label');if(gl)gl.textContent=t('gateEmailLabel');
    var ge=$('ws-gate-email-submit');if(ge)ge.textContent=t('gateSubmit');
    /* Consumer app links */
    var ca=[['ws-nav-consumer','consumerApp'],['ws-dnav-consumer','consumerApp'],['ws-f-consumer','consumerApp'],['ws-cf-consumer','consumerApp']];
    ca.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    /* Nav labels */
    var ids=[['ws-nav-home-label','navHome'],['ws-nav-products-label','navProducts'],['ws-nav-barista-label','navBarista'],['ws-nav-cultivars-label','navCultivars'],['ws-nav-chat-label','navChat'],['ws-dnav-home-label','navHome'],['ws-dnav-products-label','navProducts'],['ws-dnav-barista-label','navBarista'],['ws-dnav-cultivars-label','navCultivars'],['ws-dnav-chat-label','navChat']];
    ids.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    buildProductCards();
    buildTipCards();
    buildCultivarCards();
    buildMenuCards();
    buildQuickActions();
  }}

  function showHome(){{
    $('ws-home').classList.remove('ws-hidden');
    $('ws-chat').classList.add('ws-hidden');
    var tb=$('ws-topbar');if(tb)tb.style.display='';
  }}
  function showChat(autoMsg){{
    $('ws-home').classList.add('ws-hidden');
    $('ws-chat').classList.remove('ws-hidden');
    var tb=$('ws-topbar');if(tb)tb.style.display='none';
    if(autoMsg){{$('ws-input').value=autoMsg;setTimeout(function(){{sendMessage()}},200)}}
    if(window.innerWidth>899)$('ws-input').focus();
  }}

  function scrollToSection(id){{
    var el=document.getElementById(id);
    var scr=$('ws-home-scroll');
    if(el&&scr){{
      var top=el.offsetTop-80;
      scr.scrollTo({{top:top,behavior:'smooth'}});
    }}
  }}

  function buildProductCards(){{
    var c=$('ws-product-cards');if(!c)return;c.innerHTML='';
    products.forEach(function(p){{
      var card=document.createElement('div');card.className='ws-pcard';
      card.innerHTML='<div class="ws-pcard__visual" style="background:'+p.accent+'">'
        +'<div class="ws-pcard__num">'+escapeHtml(p.num)+'</div>'
        +'<div class="ws-pcard__kanji">'+escapeHtml(p.kanji)+'</div>'
        +'</div><div class="ws-pcard__body">'
        +'<div class="ws-pcard__grade">'+escapeHtml(t(p.k+'grade'))+'</div>'
        +'<div class="ws-pcard__origin">'+escapeHtml(t(p.k+'origin'))+' \u00b7 '+escapeHtml(t(p.k+'milling'))+'</div>'
        +'<div class="ws-pcard__cultivars">'+escapeHtml(t(p.k+'cultivars'))+'</div>'
        +'<div class="ws-pcard__desc">'+escapeHtml(t(p.k+'desc'))+'</div>'
        +'<div class="ws-pcard__footer"><div class="ws-pcard__badges">'
        +p.formats.map(function(f){{return'<span class="ws-pcard__badge">'+escapeHtml(f)+'</span>'}}).join('')
        +'</div><span class="ws-pcard__cta">'+escapeHtml(t('pAsk'))+'</span></div>'
        +'</div>';
      card.addEventListener('click',function(){{showChat(t(p.k+'msg'))}});
      c.appendChild(card);
    }});
  }}

  function buildTipCards(){{
    var c=$('ws-tip-cards');if(!c)return;c.innerHTML='';
    tips.forEach(function(tip){{
      var card=document.createElement('div');card.className='ws-tip';
      card.innerHTML='<div class="ws-tip__icon">'+tip.icon+'</div>'
        +'<div class="ws-tip__title">'+escapeHtml(t(tip.k+'title'))+'</div>'
        +'<div class="ws-tip__body">'+escapeHtml(t(tip.k+'body'))+'</div>';
      card.addEventListener('click',function(){{showChat(t(tip.k+'msg'))}});
      c.appendChild(card);
    }});
  }}

  function buildCultivarCards(){{
    var c=$('ws-cultivar-cards');if(!c)return;c.innerHTML='';
    cultivars.forEach(function(cv){{
      var card=document.createElement('div');card.className='ws-cultivar';
      card.innerHTML='<div class="ws-cultivar__name">'+escapeHtml(t(cv.k+'name'))+'</div>'
        +'<div class="ws-cultivar__kanji">'+escapeHtml(t(cv.k+'kanji'))+'</div>'
        +'<div class="ws-cultivar__char">'+escapeHtml(t(cv.k+'char'))+'</div>'
        +'<div class="ws-cultivar__products">'
        +cv.products.map(function(p){{return'<span class="ws-cultivar__product-badge">'+escapeHtml(p)+'</span>'}}).join('')
        +'</div>';
      c.appendChild(card);
    }});
  }}

  function buildMenuCards(){{
    var c=$('ws-menu-cards');if(!c)return;c.innerHTML='';
    menuItems.forEach(function(m){{
      var card=document.createElement('div');card.className='ws-menu-card';
      card.innerHTML='<div class="ws-menu-card__icon">'+m.icon+'</div>'
        +'<div class="ws-menu-card__name">'+escapeHtml(t(m.k+'name'))+'</div>'
        +'<div class="ws-menu-card__specs">'+escapeHtml(t(m.k+'specs'))+'</div>'
        +'<div class="ws-menu-card__desc">'+escapeHtml(t(m.k+'desc'))+'</div>';
      card.addEventListener('click',function(){{showChat(t(m.k+'msg'))}});
      c.appendChild(card);
    }});
  }}

  function buildQuickActions(){{
    var qa=$('ws-quick');if(!qa)return;qa.innerHTML='';
    ['q1','q2','q3','q4'].forEach(function(k){{
      var b=document.createElement('button');b.className='ws-quick__btn';
      b.setAttribute('data-msg',t(k+'m'));b.textContent=t(k);
      b.addEventListener('click',function(){{$('ws-input').value=this.getAttribute('data-msg');sendMessage();qa.style.display='none'}});
      qa.appendChild(b);
    }});
  }}

  function scroll(){{var m=$('ws-messages');if(m)m.scrollTop=m.scrollHeight}}

  function addMsg(role,text,sources,suggestions){{
    sources=sources||[];suggestions=suggestions||[];var m=$('ws-messages');if(!m)return;
    var d=document.createElement('div');d.className='ws-msg ws-msg--'+role;var html='';
    var content=role==='bot'?formatMd(text):escapeHtml(text);
    if(role==='bot'){{
      html+='<div class="ws-msg__bubble">'+content+'</div>';
      if(sources.length){{
        html+='<div class="ws-msg__sources">';
        sources.forEach(function(s){{var url=s.startsWith('http')?s:s;
          var label=lang==='ja'?'\u8a73\u7d30':'Learn more';
          html+='<a href="'+escapeHtml(url)+'" class="ws-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
        html+='</div>';
      }}
      if(suggestions.length){{
        html+='<div class="ws-suggestions">';
        suggestions.forEach(function(s){{
          html+='<button class="ws-suggestion" type="button">'+escapeHtml(s)+'</button>';
        }});
        html+='</div>';
      }}
      var now=new Date();var ts=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
      html+='<div class="ws-msg__meta"><span class="ws-msg__time">'+ts+'</span></div>';
    }}else{{html='<div class="ws-msg__bubble">'+content+'</div>'}}
    d.innerHTML=html;m.appendChild(d);
    d.querySelectorAll('.ws-suggestion').forEach(function(btn){{
      btn.addEventListener('click',function(){{
        var q=this.textContent;$('ws-input').value=q;sendMessage();
        var sc=d.querySelector('.ws-suggestions');if(sc)sc.remove();
      }});
    }});
    scroll();
  }}

  function showTyping(){{var m=$('ws-messages');if(!m)return;var d=document.createElement('div');d.className='ws-msg ws-msg--bot ws-typing';d.innerHTML='<div class="ws-msg__bubble"><span></span><span></span><span></span></div><div class="ws-typing__label">'+t('typing')+'</div>';m.appendChild(d);scroll()}}
  function removeTyping(){{var m=$('ws-messages');if(!m)return;var tw=m.querySelector('.ws-typing');if(tw)tw.remove()}}

  function sendMessage(){{
    var inp=$('ws-input');var msg=inp?inp.value.trim():'';
    if(!msg||loading)return;inp.value='';
    addMsg('user',msg);chatHistory.push({{role:'user',content:msg}});
    showTyping();loading=true;
    var abortCtrl=new AbortController();var streamTimeout=setTimeout(function(){{abortCtrl.abort()}},90000);
    fetch('/api/chat/stream',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg,history:chatHistory.slice(-MAX_H),language:lang,session_id:SESSION_ID,source:'wholesale'}}),signal:abortCtrl.signal}})
    .then(function(r){{
      if(!r.ok)throw new Error('err');
      removeTyping();
      var m=$('ws-messages');var d=document.createElement('div');d.className='ws-msg ws-msg--bot';
      var bubble=document.createElement('div');bubble.className='ws-msg__bubble';
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
                meta+='<div class="ws-msg__sources">';
                ev.sources.forEach(function(s){{var url=s.startsWith('http')?s:s;
                  var label=lang==='ja'?'\u8a73\u7d30':'Learn more';
                  meta+='<a href="'+escapeHtml(url)+'" class="ws-msg__source" target="_blank" rel="noopener">'+label+'</a>'}});
                meta+='</div>';
              }}
              if(ev.suggestions&&ev.suggestions.length){{
                meta+='<div class="ws-suggestions">';
                ev.suggestions.forEach(function(s){{meta+='<button class="ws-suggestion" type="button">'+escapeHtml(s)+'</button>'}});
                meta+='</div>';
              }}
              meta+='<div class="ws-msg__meta"><span class="ws-msg__time">'+ts+'</span></div>';
              var metaEl=document.createElement('div');metaEl.innerHTML=meta;
              while(metaEl.firstChild)d.appendChild(metaEl.firstChild);
              d.querySelectorAll('.ws-suggestion').forEach(function(btn){{
                btn.addEventListener('click',function(){{var q=this.textContent;$('ws-input').value=q;sendMessage();var sc=d.querySelector('.ws-suggestions');if(sc)sc.remove()}});
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

  function saveHistory(){{try{{localStorage.setItem('nakai_ws_history',JSON.stringify(chatHistory.slice(-MAX_H)))}}catch(e){{}}}}
  function loadHistory(){{try{{var s=localStorage.getItem('nakai_ws_history');if(s){{chatHistory=JSON.parse(s);chatHistory.forEach(function(m){{addMsg(m.role==='assistant'?'bot':'user',m.content)}})}}}}catch(e){{}}}}

  /* Topbar scroll */
  function initTopbarScroll(){{
    var scrollArea=$('ws-home-scroll');var topbar=$('ws-topbar');
    if(!scrollArea||!topbar)return;
    scrollArea.addEventListener('scroll',function(){{
      if(scrollArea.scrollTop>40)topbar.classList.add('ws-topbar--scrolled');
      else topbar.classList.remove('ws-topbar--scrolled');
    }});
  }}

  function enterApp(){{
    $('ws-gate').classList.add('ws-hidden');
    $('ws-app').classList.remove('ws-hidden');
    $('ws-app').classList.add('ws-active');
    try{{initApp()}}catch(e){{console.error('initApp error',e)}}
  }}

  function initLogin(){{
    /* Gate: check if already verified */
    if(sessionStorage.getItem('ws_partner_verified')){{
      enterApp();
      return;
    }}
    /* Attach button handlers FIRST (before setLang which may fail) */
    $('ws-gate-yes').addEventListener('click',function(){{
      sessionStorage.setItem('ws_partner_verified','yes');
      enterApp();
    }});
    $('ws-gate-no').addEventListener('click',function(){{
      $('ws-gate-email').classList.add('ws-gate__email--show');
      $('ws-gate-email-input').focus();
    }});
    $('ws-gate-email-form').addEventListener('submit',function(e){{
      e.preventDefault();
      var email=$('ws-gate-email-input').value.trim();
      if(!email)return;
      sessionStorage.setItem('ws_partner_verified','interested');
      sessionStorage.setItem('ws_lead_email',email);
      fetch('/api/admin/wholesale/leads',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email,session_id:SESSION_ID}})}}).catch(function(){{}});
      enterApp();
    }});
    /* Now safe to set language (won't block buttons if it throws) */
    try{{setLang(lang)}}catch(e){{console.error('setLang error',e)}}
  }}

  function initApp(){{
    try{{setLang(lang)}}catch(e){{console.error('initApp setLang error',e)}}
    try{{loadHistory()}}catch(e){{console.error('loadHistory error',e)}}
    /* Forms */
    $('ws-form').addEventListener('submit',function(e){{e.preventDefault();sendMessage()}});
    $('ws-back').addEventListener('click',showHome);
    $('ws-hero-form').addEventListener('submit',function(e){{e.preventDefault();var v=$('ws-hero-input').value.trim();if(v)showChat(v)}});
    /* Lang buttons */
    document.querySelectorAll('.ws-lang-btn').forEach(function(b){{
      b.addEventListener('click',function(){{setLang(this.getAttribute('data-lang'))}});
    }});
    /* Topic pills */
    $('ws-t-compare').addEventListener('click',function(){{showChat(t('compareMsg'))}});
    $('ws-t-latte').addEventListener('click',function(){{showChat(t('latteMsg'))}});
    $('ws-t-cultivar').addEventListener('click',function(){{showChat(t('cultivarMsg'))}});
    $('ws-t-contact').addEventListener('click',function(){{openInquiry()}});
    /* Inquiry modal */
    function openInquiry(){{$('ws-inquiry-overlay').classList.add('ws-inquiry-overlay--open')}}
    function closeInquiry(){{$('ws-inquiry-overlay').classList.remove('ws-inquiry-overlay--open')}}
    $('ws-inquiry-close').addEventListener('click',closeInquiry);
    $('ws-inquiry-overlay').addEventListener('click',function(e){{if(e.target===this)closeInquiry()}});
    var ni=$('ws-nav-inquiry');if(ni)ni.addEventListener('click',openInquiry);
    var fi=$('ws-f-inquiry');if(fi)fi.addEventListener('click',function(e){{e.preventDefault();openInquiry()}});
    var ci=$('ws-cf-inquiry');if(ci)ci.addEventListener('click',function(e){{e.preventDefault();openInquiry()}});
    /* Sidebar nav */
    var sn=$('ws-nav-home');if(sn)sn.addEventListener('click',showHome);
    var sp=$('ws-nav-products');if(sp)sp.addEventListener('click',function(){{showHome();setTimeout(function(){{scrollToSection('ws-sec-products')}},100)}});
    var sb=$('ws-nav-barista');if(sb)sb.addEventListener('click',function(){{showHome();setTimeout(function(){{scrollToSection('ws-sec-barista')}},100)}});
    var sc=$('ws-nav-cultivars');if(sc)sc.addEventListener('click',function(){{showHome();setTimeout(function(){{scrollToSection('ws-sec-cultivars')}},100)}});
    var sch=$('ws-nav-chat');if(sch)sch.addEventListener('click',function(){{showChat()}});
    $('ws-topbar-mark').addEventListener('click',function(){{var s=$('ws-home-scroll');if(s)s.scrollTo({{top:0,behavior:'smooth'}})}});
    initTopbarScroll();
    /* Drawer */
    var drawer=$('ws-drawer'),drawerOv=$('ws-drawer-overlay');
    function openDrawer(){{drawer.classList.add('ws-drawer--open');drawerOv.classList.add('ws-drawer-overlay--open');document.body.style.overflow='hidden'}}
    function closeDrawer(){{drawer.classList.remove('ws-drawer--open');drawerOv.classList.remove('ws-drawer-overlay--open');document.body.style.overflow=''}}
    var hb=$('ws-hamburger');if(hb)hb.addEventListener('click',openDrawer);
    $('ws-drawer-close').addEventListener('click',closeDrawer);
    drawerOv.addEventListener('click',closeDrawer);
    $('ws-dnav-home').addEventListener('click',function(){{closeDrawer();showHome()}});
    $('ws-dnav-products').addEventListener('click',function(){{closeDrawer();showHome();setTimeout(function(){{scrollToSection('ws-sec-products')}},100)}});
    $('ws-dnav-barista').addEventListener('click',function(){{closeDrawer();showHome();setTimeout(function(){{scrollToSection('ws-sec-barista')}},100)}});
    $('ws-dnav-cultivars').addEventListener('click',function(){{closeDrawer();showHome();setTimeout(function(){{scrollToSection('ws-sec-cultivars')}},100)}});
    $('ws-dnav-chat').addEventListener('click',function(){{closeDrawer();showChat()}});
    var di=$('ws-dnav-inquiry');if(di)di.addEventListener('click',function(){{closeDrawer();openInquiry()}});
    if(chatHistory.length>0)showChat();
  }}

  function boot(){{
    initLogin();
  }}

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);
  else boot();
}})();
</script>
</body>
</html>"""


@wholesale_router.get("/wholesale")
async def serve_wholesale():
    return HTMLResponse(content=WS_HTML, headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
