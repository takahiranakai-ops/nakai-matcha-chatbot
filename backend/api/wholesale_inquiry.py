"""NAKAI Wholesale Inquiry — Rich contact form for bulk orders (10 kg+)."""
import base64
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr

from services import supabase_client

logger = logging.getLogger(__name__)

inquiry_router = APIRouter()

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LOGO_WM_WHITE_B64 = base64.b64encode(
    (_REPO_ROOT / "nakai-logo-white.png").read_bytes()
).decode()
_LOGO_ICON_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-green-icon.png").read_bytes()
).decode()


class InquiryBody(BaseModel):
    company: str
    name: str
    email: str
    phone: str = ""
    country: str = ""
    quantity: str = ""
    use_case: str = ""
    message: str = ""
    language: str = "en"


INQUIRY_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#406546">
<title>Wholesale Inquiry — NAKAI Matcha</title>
<link rel="icon" type="image/png" href="/icon-192.png">
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --green:#406546;--cream:#F9F0E2;--white:#FFFFFF;
  --g90:rgba(64,101,70,.9);--g70:rgba(64,101,70,.7);--g50:rgba(64,101,70,.5);
  --g35:rgba(64,101,70,.35);--g20:rgba(64,101,70,.2);--g12:rgba(64,101,70,.12);
  --g06:rgba(64,101,70,.06);--g03:rgba(64,101,70,.03);
  --sans:'Work Sans',system-ui,sans-serif;
  --ease:cubic-bezier(.22,1,.36,1);
}}
html{{font-size:62.5%;scroll-behavior:smooth}}
body{{
  font-family:var(--sans);font-size:1.5rem;line-height:1.6;
  color:#1a1a1a;background:var(--cream);
  -webkit-font-smoothing:antialiased;min-height:100vh;min-height:100dvh;
}}

/* ── Hero ── */
.inq-hero{{
  background:var(--green);color:var(--white);
  padding:48px 24px 56px;text-align:center;position:relative;overflow:hidden;
}}
.inq-hero::after{{
  content:'';position:absolute;bottom:-1px;left:0;right:0;height:40px;
  background:var(--cream);border-radius:40px 40px 0 0;
}}
.inq-hero__logo{{width:48px;margin:0 auto 20px;opacity:.9}}
.inq-hero__title{{
  font-size:2.2rem;font-weight:600;letter-spacing:-.02em;margin-bottom:8px;
}}
.inq-hero__sub{{
  font-size:1.3rem;font-weight:300;opacity:.75;max-width:480px;margin:0 auto;
}}

/* ── Lang toggle ── */
.inq-lang{{position:absolute;top:16px;right:16px;display:flex;gap:4px}}
.inq-lang__btn{{
  background:rgba(255,255,255,.12);border:1.5px solid rgba(255,255,255,.2);
  color:rgba(255,255,255,.6);padding:6px 12px;border-radius:8px;
  font-family:var(--sans);font-size:1.1rem;font-weight:500;cursor:pointer;
  transition:all .2s;
}}
.inq-lang__btn.active{{background:rgba(255,255,255,.22);color:var(--white);border-color:rgba(255,255,255,.4)}}

/* ── Back link ── */
.inq-back{{
  position:absolute;top:16px;left:16px;color:rgba(255,255,255,.6);
  font-family:var(--sans);font-size:1.2rem;font-weight:400;
  text-decoration:none;display:flex;align-items:center;gap:6px;
  transition:color .2s;
}}
.inq-back:hover{{color:var(--white)}}
.inq-back svg{{width:16px;height:16px}}

/* ── Form card ── */
.inq-wrap{{
  max-width:680px;margin:-20px auto 48px;padding:0 20px;position:relative;z-index:1;
}}
.inq-card{{
  background:var(--white);border-radius:24px;padding:40px 36px;
  box-shadow:0 4px 24px rgba(0,0,0,.06),0 1px 3px rgba(0,0,0,.03);
}}
.inq-card__title{{
  font-size:1.5rem;font-weight:600;color:var(--green);margin-bottom:4px;
}}
.inq-card__sub{{
  font-size:1.2rem;font-weight:300;color:var(--g50);margin-bottom:32px;
}}

/* ── Grid ── */
.inq-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.inq-full{{grid-column:1/-1}}

/* ── Field ── */
.inq-field{{display:flex;flex-direction:column;gap:6px}}
.inq-label{{
  font-size:1.1rem;font-weight:500;color:var(--g70);
  display:flex;align-items:center;gap:4px;
}}
.inq-label .req{{color:#c0392b;font-size:1.2rem}}
.inq-input,.inq-select,.inq-textarea{{
  width:100%;padding:14px 16px;border:1.5px solid var(--g12);border-radius:14px;
  font-family:var(--sans);font-size:1.4rem;color:#1a1a1a;
  background:var(--white);outline:none;transition:border-color .25s,box-shadow .25s;
  -webkit-appearance:none;appearance:none;
}}
.inq-input:focus,.inq-select:focus,.inq-textarea:focus{{
  border-color:var(--green);box-shadow:0 0 0 3px rgba(64,101,70,.08);
}}
.inq-input::placeholder,.inq-textarea::placeholder{{color:var(--g35)}}
.inq-select{{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' fill='none'%3E%3Cpath d='M1 1.5l5 5 5-5' stroke='%23406546' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 16px center;padding-right:40px;
}}
.inq-textarea{{resize:vertical;min-height:120px;line-height:1.5}}

/* ── Submit ── */
.inq-submit{{
  width:100%;padding:16px;border:none;border-radius:14px;
  background:var(--green);color:var(--white);
  font-family:var(--sans);font-size:1.4rem;font-weight:600;
  cursor:pointer;transition:opacity .2s,transform .15s;
  margin-top:8px;
}}
.inq-submit:hover{{opacity:.9}}
.inq-submit:active{{transform:scale(.985)}}
.inq-submit:disabled{{opacity:.5;cursor:not-allowed}}

/* ── Note ── */
.inq-note{{
  font-size:1.1rem;color:var(--g50);text-align:center;margin-top:16px;line-height:1.5;
}}
.inq-note a{{color:var(--green);text-decoration:underline;text-underline-offset:2px}}

/* ── Error ── */
.inq-error{{
  display:none;font-size:1.1rem;color:#c0392b;margin-top:4px;
}}
.inq-field.has-error .inq-input,
.inq-field.has-error .inq-select,
.inq-field.has-error .inq-textarea{{border-color:#c0392b}}
.inq-field.has-error .inq-error{{display:block}}

/* ── Success ── */
.inq-success{{
  display:none;text-align:center;padding:60px 20px;
}}
.inq-success.show{{display:block}}
.inq-form.hide{{display:none}}
.inq-success__check{{
  width:72px;height:72px;border-radius:50%;background:rgba(64,101,70,.08);
  display:flex;align-items:center;justify-content:center;margin:0 auto 24px;
  animation:scaleIn .5s var(--ease);
}}
@keyframes scaleIn{{from{{transform:scale(0);opacity:0}}to{{transform:scale(1);opacity:1}}}}
.inq-success__check svg{{width:36px;height:36px;color:var(--green)}}
.inq-success__title{{font-size:1.8rem;font-weight:600;color:var(--green);margin-bottom:8px}}
.inq-success__sub{{font-size:1.3rem;font-weight:300;color:var(--g50);margin-bottom:32px;max-width:400px;margin-left:auto;margin-right:auto}}
.inq-success__btn{{
  display:inline-block;padding:14px 32px;border-radius:14px;
  background:rgba(64,101,70,.08);color:var(--green);
  font-family:var(--sans);font-size:1.3rem;font-weight:600;
  text-decoration:none;transition:background .2s;
}}
.inq-success__btn:hover{{background:rgba(64,101,70,.14)}}

/* ── Footer ── */
.inq-footer{{
  text-align:center;padding:24px 20px 40px;
  font-size:1.1rem;color:var(--g35);
}}
.inq-footer a{{color:var(--g50);text-decoration:none}}
.inq-footer a:hover{{text-decoration:underline}}

/* ── Spinner ── */
.inq-spinner{{display:inline-block;width:18px;height:18px;border:2px solid rgba(255,255,255,.3);border-top-color:var(--white);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:8px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* ── Responsive ── */
@media(max-width:600px){{
  .inq-hero{{padding:36px 20px 48px}}
  .inq-hero__title{{font-size:1.9rem}}
  .inq-hero__sub{{font-size:1.2rem}}
  .inq-grid{{grid-template-columns:1fr}}
  .inq-card{{padding:28px 20px;border-radius:20px}}
  .inq-wrap{{padding:0 12px}}
}}
</style>
</head>
<body>

<!-- Hero -->
<div class="inq-hero">
  <a class="inq-back" href="/wholesale" id="inq-back">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
    <span id="inq-back-label">Back</span>
  </a>
  <div class="inq-lang">
    <button class="inq-lang__btn active" data-lang="en">EN</button>
    <button class="inq-lang__btn" data-lang="ja">JA</button>
  </div>
  <img class="inq-hero__logo" src="data:image/png;base64,{_LOGO_WM_WHITE_B64}" alt="NAKAI" />
  <h1 class="inq-hero__title" id="inq-title">Wholesale Partnership</h1>
  <p class="inq-hero__sub" id="inq-sub">Tell us about your business and we'll craft a custom proposal for you.</p>
</div>

<!-- Form -->
<div class="inq-wrap">
  <div class="inq-card">
    <h2 class="inq-card__title" id="inq-card-title">Inquiry Details</h2>
    <p class="inq-card__sub" id="inq-card-sub">Fields marked with * are required.</p>

    <form class="inq-form" id="inq-form" novalidate>
      <div class="inq-grid">

        <!-- Company -->
        <div class="inq-field inq-full" data-field="company">
          <label class="inq-label" id="inq-l-company">Company / Organization <span class="req">*</span></label>
          <input class="inq-input" type="text" name="company" id="inq-company" required autocomplete="organization" />
          <div class="inq-error" id="inq-e-company">Please enter your company name</div>
        </div>

        <!-- Name -->
        <div class="inq-field" data-field="name">
          <label class="inq-label" id="inq-l-name">Contact Name <span class="req">*</span></label>
          <input class="inq-input" type="text" name="name" id="inq-name" required autocomplete="name" />
          <div class="inq-error" id="inq-e-name">Please enter your name</div>
        </div>

        <!-- Email -->
        <div class="inq-field" data-field="email">
          <label class="inq-label" id="inq-l-email">Email <span class="req">*</span></label>
          <input class="inq-input" type="email" name="email" id="inq-email" required autocomplete="email" />
          <div class="inq-error" id="inq-e-email">Please enter a valid email</div>
        </div>

        <!-- Phone -->
        <div class="inq-field" data-field="phone">
          <label class="inq-label" id="inq-l-phone">Phone Number</label>
          <input class="inq-input" type="tel" name="phone" id="inq-phone" autocomplete="tel" />
        </div>

        <!-- Country -->
        <div class="inq-field" data-field="country">
          <label class="inq-label" id="inq-l-country">Country / Region</label>
          <select class="inq-select" name="country" id="inq-country">
            <option value="" id="inq-o-select">Select...</option>
            <option value="JP">Japan</option>
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="GB">United Kingdom</option>
            <option value="AU">Australia</option>
            <option value="DE">Germany</option>
            <option value="FR">France</option>
            <option value="SG">Singapore</option>
            <option value="HK">Hong Kong</option>
            <option value="TW">Taiwan</option>
            <option value="KR">South Korea</option>
            <option value="CN">China</option>
            <option value="TH">Thailand</option>
            <option value="AE">UAE</option>
            <option value="NL">Netherlands</option>
            <option value="IT">Italy</option>
            <option value="ES">Spain</option>
            <option value="SE">Sweden</option>
            <option value="CH">Switzerland</option>
            <option value="NZ">New Zealand</option>
            <option value="OTHER" id="inq-o-other">Other</option>
          </select>
        </div>

        <!-- Quantity -->
        <div class="inq-field" data-field="quantity">
          <label class="inq-label" id="inq-l-qty">Estimated Order (kg) <span class="req">*</span></label>
          <select class="inq-select" name="quantity" id="inq-quantity" required>
            <option value="" id="inq-o-qty-select">Select...</option>
            <option value="10-30">10 – 30 kg</option>
            <option value="30-100">30 – 100 kg</option>
            <option value="100-500">100 – 500 kg</option>
            <option value="500-1000">500 kg – 1 t</option>
            <option value="1000+">1 t+</option>
          </select>
          <div class="inq-error" id="inq-e-qty">Please select an estimated quantity</div>
        </div>

        <!-- Use case -->
        <div class="inq-field" data-field="use_case">
          <label class="inq-label" id="inq-l-use">Business Type</label>
          <select class="inq-select" name="use_case" id="inq-use">
            <option value="" id="inq-o-use-select">Select...</option>
            <option value="cafe" id="inq-o-cafe">Cafe / Coffee Shop</option>
            <option value="restaurant" id="inq-o-restaurant">Restaurant</option>
            <option value="hotel" id="inq-o-hotel">Hotel / Hospitality</option>
            <option value="retail" id="inq-o-retail">Retail Store</option>
            <option value="distributor" id="inq-o-distributor">Distributor / Importer</option>
            <option value="manufacturer" id="inq-o-manufacturer">Food / Beverage Manufacturer</option>
            <option value="other" id="inq-o-use-other">Other</option>
          </select>
        </div>

        <!-- Message -->
        <div class="inq-field inq-full" data-field="message">
          <label class="inq-label" id="inq-l-msg">Message</label>
          <textarea class="inq-textarea" name="message" id="inq-message" rows="4"></textarea>
        </div>

        <!-- Submit -->
        <div class="inq-full">
          <button class="inq-submit" type="submit" id="inq-btn">
            <span id="inq-btn-text">Send Inquiry</span>
          </button>
        </div>
      </div>
    </form>

    <!-- Success -->
    <div class="inq-success" id="inq-success">
      <div class="inq-success__check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <h3 class="inq-success__title" id="inq-s-title">Thank You!</h3>
      <p class="inq-success__sub" id="inq-s-sub">We've received your inquiry and will respond within 1–2 business days.</p>
      <a class="inq-success__btn" href="/wholesale" id="inq-s-btn">Back to Wholesale Portal</a>
    </div>

    <p class="inq-note" id="inq-note">
      Questions? Email us directly at <a href="mailto:info@s-natural.xyz">info@s-natural.xyz</a>
    </p>
  </div>
</div>

<div class="inq-footer">
  &copy; 2026 NAKAI Matcha &middot; <a href="https://nakaimatcha.com" target="_blank" rel="noopener">nakaimatcha.com</a>
</div>

<script>
(function(){{
  'use strict';
  function $(id){{return document.getElementById(id)}}

  var i18n={{
    en:{{
      title:'Wholesale Partnership',
      sub:'Tell us about your business and we\\'ll craft a custom proposal for you.',
      cardTitle:'Inquiry Details',
      cardSub:'Fields marked with * are required.',
      lCompany:'Company / Organization',lName:'Contact Name',lEmail:'Email',
      lPhone:'Phone Number',lCountry:'Country / Region',lQty:'Estimated Order (kg)',
      lUse:'Business Type',lMsg:'Message',
      eCompany:'Please enter your company name',eName:'Please enter your name',
      eEmail:'Please enter a valid email',eQty:'Please select an estimated quantity',
      btn:'Send Inquiry',btnSending:'Sending...',
      sTitle:'Thank You!',
      sSub:'We\\'ve received your inquiry and will respond within 1\\u20132 business days.',
      sBtn:'Back to Wholesale Portal',
      note:'Questions? Email us directly at <a href="mailto:info@s-natural.xyz">info@s-natural.xyz</a>',
      back:'Back',
      oSelect:'Select...',oOther:'Other',
      oCafe:'Cafe / Coffee Shop',oRestaurant:'Restaurant',oHotel:'Hotel / Hospitality',
      oRetail:'Retail Store',oDistributor:'Distributor / Importer',
      oManufacturer:'Food / Beverage Manufacturer',oUseOther:'Other',
      oQtySelect:'Select...'
    }},
    ja:{{
      title:'\u5378\u58f2\u30d1\u30fc\u30c8\u30ca\u30fc\u30b7\u30c3\u30d7',
      sub:'\u304a\u5ba2\u69d8\u306e\u30d3\u30b8\u30cd\u30b9\u306b\u3064\u3044\u3066\u304a\u805e\u304b\u305b\u304f\u3060\u3055\u3044\u3002\u5c02\u7528\u306e\u3054\u63d0\u6848\u3092\u304a\u4f5c\u308a\u3044\u305f\u3057\u307e\u3059\u3002',
      cardTitle:'\u304a\u554f\u3044\u5408\u308f\u305b\u5185\u5bb9',
      cardSub:'* \u306f\u5fc5\u9808\u9805\u76ee\u3067\u3059\u3002',
      lCompany:'\u4f1a\u793e\u540d / \u7d44\u7e54\u540d',lName:'\u62c5\u5f53\u8005\u540d',lEmail:'\u30e1\u30fc\u30eb',
      lPhone:'\u96fb\u8a71\u756a\u53f7',lCountry:'\u56fd / \u5730\u57df',lQty:'\u6ce8\u6587\u4e88\u5b9a\u91cf (kg)',
      lUse:'\u696d\u7a2e',lMsg:'\u30e1\u30c3\u30bb\u30fc\u30b8',
      eCompany:'\u4f1a\u793e\u540d\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044',eName:'\u304a\u540d\u524d\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044',
      eEmail:'\u6709\u52b9\u306a\u30e1\u30fc\u30eb\u30a2\u30c9\u30ec\u30b9\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044',eQty:'\u6ce8\u6587\u4e88\u5b9a\u91cf\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044',
      btn:'\u9001\u4fe1\u3059\u308b',btnSending:'\u9001\u4fe1\u4e2d...',
      sTitle:'\u3042\u308a\u304c\u3068\u3046\u3054\u3056\u3044\u307e\u3059\uff01',
      sSub:'\u304a\u554f\u3044\u5408\u308f\u305b\u3092\u53d7\u3051\u4ed8\u3051\u307e\u3057\u305f\u30021\\u301c2\u55b6\u696d\u65e5\u4ee5\u5185\u306b\u3054\u8fd4\u4fe1\u3044\u305f\u3057\u307e\u3059\u3002',
      sBtn:'\u5378\u58f2\u30dd\u30fc\u30bf\u30eb\u306b\u623b\u308b',
      note:'\u3054\u8cea\u554f\u306f\u304a\u6c17\u8efd\u306b <a href="mailto:info@s-natural.xyz">info@s-natural.xyz</a> \u307e\u3067',
      back:'\u623b\u308b',
      oSelect:'\u9078\u629e...',oOther:'\u305d\u306e\u4ed6',
      oCafe:'\u30ab\u30d5\u30a7 / \u30b3\u30fc\u30d2\u30fc\u30b7\u30e7\u30c3\u30d7',oRestaurant:'\u30ec\u30b9\u30c8\u30e9\u30f3',oHotel:'\u30db\u30c6\u30eb / \u63a5\u5ba2\u696d',
      oRetail:'\u5c0f\u58f2\u5e97',oDistributor:'\u5378\u58f2\u696d\u8005 / \u8f38\u5165\u696d\u8005',
      oManufacturer:'\u98df\u54c1 / \u98f2\u6599\u30e1\u30fc\u30ab\u30fc',oUseOther:'\u305d\u306e\u4ed6',
      oQtySelect:'\u9078\u629e...'
    }}
  }};

  var lang=(function(){{
    try{{var s=localStorage.getItem('nakai_ws_lang');if(s&&i18n[s])return s}}catch(e){{}}
    var n=(navigator.language||'en').substring(0,2);
    return i18n[n]?n:'en';
  }})();

  function t(k){{return(i18n[lang]||i18n.en)[k]||i18n.en[k]||''}}

  function setLang(l){{
    lang=l;try{{localStorage.setItem('nakai_ws_lang',l)}}catch(e){{}}
    document.documentElement.lang=l;
    document.querySelectorAll('.inq-lang__btn').forEach(function(b){{
      b.classList.toggle('active',b.getAttribute('data-lang')===l);
    }});
    $('inq-title').textContent=t('title');
    $('inq-sub').textContent=t('sub');
    $('inq-card-title').textContent=t('cardTitle');
    $('inq-card-sub').textContent=t('cardSub');
    $('inq-back-label').textContent=t('back');
    /* Labels */
    var labels=[['inq-l-company','lCompany'],['inq-l-name','lName'],['inq-l-email','lEmail'],
      ['inq-l-phone','lPhone'],['inq-l-country','lCountry'],['inq-l-qty','lQty'],
      ['inq-l-use','lUse'],['inq-l-msg','lMsg']];
    labels.forEach(function(p){{
      var el=$(p[0]);if(el){{
        var req=el.querySelector('.req');
        el.textContent=t(p[1]);
        if(req)el.appendChild(req);
      }}
    }});
    /* Errors */
    var errs=[['inq-e-company','eCompany'],['inq-e-name','eName'],['inq-e-email','eEmail'],['inq-e-qty','eQty']];
    errs.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    /* Button */
    $('inq-btn-text').textContent=t('btn');
    /* Select placeholders */
    var so=$('inq-o-select');if(so)so.textContent=t('oSelect');
    var qo=$('inq-o-qty-select');if(qo)qo.textContent=t('oQtySelect');
    var oo=$('inq-o-other');if(oo)oo.textContent=t('oOther');
    /* Use case options */
    var uOpts=[['inq-o-cafe','oCafe'],['inq-o-restaurant','oRestaurant'],['inq-o-hotel','oHotel'],
      ['inq-o-retail','oRetail'],['inq-o-distributor','oDistributor'],
      ['inq-o-manufacturer','oManufacturer'],['inq-o-use-other','oUseOther'],['inq-o-use-select','oSelect']];
    uOpts.forEach(function(p){{var el=$(p[0]);if(el)el.textContent=t(p[1])}});
    /* Success */
    $('inq-s-title').textContent=t('sTitle');
    $('inq-s-sub').textContent=t('sSub');
    $('inq-s-btn').textContent=t('sBtn');
    /* Note */
    $('inq-note').innerHTML=t('note');
  }}

  /* Validation */
  function validateField(name){{
    var field=document.querySelector('[data-field="'+name+'"]');
    var input=field.querySelector('input,select,textarea');
    var valid=true;
    if(name==='email'){{
      valid=/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(input.value.trim());
    }}else{{
      valid=input.value.trim().length>0;
    }}
    field.classList.toggle('has-error',!valid);
    return valid;
  }}

  /* Submit */
  var form=$('inq-form');
  form.addEventListener('submit',function(e){{
    e.preventDefault();
    var ok=true;
    ['company','name','email','quantity'].forEach(function(f){{
      if(!validateField(f))ok=false;
    }});
    if(!ok)return;

    var btn=$('inq-btn');
    btn.disabled=true;
    $('inq-btn-text').innerHTML='<span class="inq-spinner"></span>'+t('btnSending');

    var data={{
      company:$('inq-company').value.trim(),
      name:$('inq-name').value.trim(),
      email:$('inq-email').value.trim(),
      phone:$('inq-phone').value.trim(),
      country:$('inq-country').value,
      quantity:$('inq-quantity').value,
      use_case:$('inq-use').value,
      message:$('inq-message').value.trim(),
      language:lang
    }};

    fetch('/api/wholesale-inquiry',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify(data)
    }})
    .then(function(r){{
      if(!r.ok)throw new Error('Server error');
      return r.json();
    }})
    .then(function(){{
      form.classList.add('hide');
      $('inq-card-title').style.display='none';
      $('inq-card-sub').style.display='none';
      $('inq-success').classList.add('show');
      $('inq-note').style.display='none';
    }})
    .catch(function(){{
      btn.disabled=false;
      $('inq-btn-text').textContent=t('btn');
      alert(lang==='ja'?'\u9001\u4fe1\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002\u3082\u3046\u4e00\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002':'Something went wrong. Please try again.');
    }});
  }});

  /* Clear errors on input */
  document.querySelectorAll('.inq-input,.inq-select,.inq-textarea').forEach(function(el){{
    el.addEventListener('input',function(){{
      var f=this.closest('.inq-field');
      if(f)f.classList.remove('has-error');
    }});
  }});

  /* Lang toggle */
  document.querySelectorAll('.inq-lang__btn').forEach(function(b){{
    b.addEventListener('click',function(){{setLang(this.getAttribute('data-lang'))}});
  }});

  /* Init */
  try{{setLang(lang)}}catch(e){{console.error('setLang error',e)}}
}})();
</script>
</body>
</html>"""


@inquiry_router.get("/wholesale-inquiry")
async def serve_inquiry_page():
    return HTMLResponse(
        content=INQUIRY_HTML,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@inquiry_router.post("/api/wholesale-inquiry")
async def submit_inquiry(body: InquiryBody):
    """Store wholesale inquiry in Supabase and send notification email."""
    try:
        await supabase_client.create_wholesale_inquiry(
            company=body.company,
            name=body.name,
            email=body.email,
            phone=body.phone,
            country=body.country,
            quantity=body.quantity,
            use_case=body.use_case,
            message=body.message,
            language=body.language,
        )
    except Exception as e:
        logger.error(f"Failed to store inquiry: {e}")

    # Try to send notification email (non-blocking)
    try:
        from services.email_client import send_inquiry_notification
        await send_inquiry_notification(body)
    except Exception as e:
        logger.warning(f"Email notification skipped: {e}")

    return JSONResponse({"status": "ok"})
