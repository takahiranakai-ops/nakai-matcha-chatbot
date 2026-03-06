"""NAKAI Wholesale Inquiry — Minimalist contact form for bulk orders."""
import base64
import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from services import supabase_client

logger = logging.getLogger(__name__)

inquiry_router = APIRouter()

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LOGO_WM_BLACK_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-wordmark-black.png").read_bytes()
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
<meta name="theme-color" content="#FAFAF8">
<title>Wholesale — NAKAI</title>
<link rel="icon" type="image/png" href="/icon-192.png">
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --fg:#1d1d1f;--fg2:#6e6e73;--fg3:#aeaeb2;--border:#d2d2d7;
  --green:#406546;--bg:#fafaf8;--white:#fff;
  --sans:'Work Sans',-apple-system,system-ui,sans-serif;
}}
html{{font-size:62.5%}}
body{{
  font-family:var(--sans);font-size:1.5rem;line-height:1.5;
  color:var(--fg);background:var(--bg);
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
}}

/* ── Layout ── */
.page{{
  max-width:540px;margin:0 auto;
  padding:env(safe-area-inset-top,0) 24px 80px;
}}

/* ── Nav ── */
.nav{{
  display:flex;justify-content:space-between;align-items:center;
  padding:20px 0 0;
}}
.nav__back{{
  display:flex;align-items:center;gap:4px;
  color:var(--green);font-size:1.3rem;font-weight:500;
  text-decoration:none;transition:opacity .2s;
}}
.nav__back:hover{{opacity:.7}}
.nav__back svg{{width:14px;height:14px}}
.nav__lang{{
  font-size:1.1rem;color:var(--fg3);cursor:pointer;
  background:none;border:none;font-family:var(--sans);font-weight:400;
  transition:color .2s;
}}
.nav__lang:hover{{color:var(--fg2)}}

/* ── Header ── */
.header{{padding:56px 0 48px}}
.header__logo{{height:22px;opacity:.85;margin-bottom:32px}}
.header__title{{
  font-size:3.4rem;font-weight:600;letter-spacing:-.03em;
  line-height:1.1;color:var(--fg);margin-bottom:12px;
}}
.header__sub{{
  font-size:1.5rem;font-weight:300;color:var(--fg2);
  line-height:1.5;max-width:400px;
}}

/* ── Form ── */
.form__section{{margin-bottom:40px}}
.form__section-label{{
  font-size:1.1rem;font-weight:500;color:var(--fg3);
  text-transform:uppercase;letter-spacing:.08em;
  margin-bottom:16px;
}}
.form__row{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.form__row--full{{grid-template-columns:1fr}}

/* ── Field ── */
.field{{position:relative}}
.field__input,.field__select,.field__textarea{{
  width:100%;padding:14px 0 12px;
  border:none;border-bottom:1px solid var(--border);
  font-family:var(--sans);font-size:1.5rem;font-weight:400;
  color:var(--fg);background:transparent;outline:none;
  border-radius:0;-webkit-appearance:none;appearance:none;
  transition:border-color .3s;
}}
.field__input:focus,.field__select:focus,.field__textarea:focus{{
  border-bottom-color:var(--green);
}}
.field__input::placeholder,.field__textarea::placeholder{{color:var(--fg3);font-weight:300}}
.field__select{{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='none'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23aeaeb2' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 0 center;
  padding-right:24px;cursor:pointer;
}}
.field__select option{{font-family:var(--sans);font-size:1.4rem}}
.field__textarea{{resize:none;min-height:100px;line-height:1.5}}
.field__error{{
  display:none;font-size:1.1rem;color:#ff3b30;margin-top:6px;font-weight:400;
}}
.field.err .field__input,.field.err .field__select,.field.err .field__textarea{{border-bottom-color:#ff3b30}}
.field.err .field__error{{display:block}}

/* ── Submit ── */
.submit{{
  width:100%;padding:16px;margin-top:40px;
  background:var(--green);color:var(--white);border:none;border-radius:12px;
  font-family:var(--sans);font-size:1.5rem;font-weight:600;
  cursor:pointer;transition:transform .15s,opacity .2s;
}}
.submit:hover{{opacity:.88}}
.submit:active{{transform:scale(.98)}}
.submit:disabled{{opacity:.4;cursor:default;transform:none}}

/* ── Spinner ── */
.spin{{
  display:inline-block;width:16px;height:16px;
  border:2px solid rgba(255,255,255,.3);border-top-color:#fff;
  border-radius:50%;animation:spin .6s linear infinite;
  vertical-align:middle;margin-right:8px;
}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* ── Footer note ── */
.note{{
  text-align:center;margin-top:32px;
  font-size:1.2rem;font-weight:300;color:var(--fg3);
}}
.note a{{color:var(--fg2);text-decoration:none;border-bottom:1px solid var(--border);transition:border-color .2s}}
.note a:hover{{border-color:var(--fg2)}}

/* ── Success ── */
.success{{display:none;text-align:center;padding:80px 0 40px}}
.success.show{{display:block}}
.form.hide{{display:none}}
.success__icon{{
  width:64px;height:64px;border-radius:50%;
  background:rgba(64,101,70,.06);
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 28px;animation:pop .5s cubic-bezier(.22,1,.36,1);
}}
@keyframes pop{{from{{transform:scale(0);opacity:0}}to{{transform:scale(1);opacity:1}}}}
.success__icon svg{{width:28px;height:28px;color:var(--green)}}
.success__title{{font-size:2.4rem;font-weight:600;letter-spacing:-.02em;margin-bottom:8px}}
.success__sub{{font-size:1.4rem;font-weight:300;color:var(--fg2);margin-bottom:40px;line-height:1.5}}
.success__link{{
  color:var(--green);font-size:1.3rem;font-weight:500;text-decoration:none;
  transition:opacity .2s;
}}
.success__link:hover{{opacity:.7}}

/* ── Responsive ── */
@media(max-width:560px){{
  .page{{padding-left:20px;padding-right:20px}}
  .header{{padding:40px 0 36px}}
  .header__title{{font-size:2.8rem}}
  .form__row{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<div class="page">

  <!-- Nav -->
  <nav class="nav">
    <a class="nav__back" href="/wholesale">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
      <span id="nav-back">Back</span>
    </a>
    <button class="nav__lang" id="nav-lang" type="button">JA</button>
  </nav>

  <!-- Header -->
  <header class="header">
    <img class="header__logo" src="data:image/png;base64,{_LOGO_WM_BLACK_B64}" alt="NAKAI" />
    <h1 class="header__title" id="hd-title">Wholesale<br>Partnership.</h1>
    <p class="header__sub" id="hd-sub">Tell us about your business. We'll prepare a tailored proposal within two business days.</p>
  </header>

  <!-- Form -->
  <form class="form" id="form" novalidate>

    <div class="form__section">
      <div class="form__section-label" id="sec-about">About You</div>
      <div class="form__row">
        <div class="field" data-f="company">
          <input class="field__input" type="text" name="company" id="f-company" placeholder="Company" required autocomplete="organization" />
          <div class="field__error" id="e-company">Required</div>
        </div>
        <div class="field" data-f="name">
          <input class="field__input" type="text" name="name" id="f-name" placeholder="Your name" required autocomplete="name" />
          <div class="field__error" id="e-name">Required</div>
        </div>
      </div>
      <div class="form__row" style="margin-top:16px">
        <div class="field" data-f="email">
          <input class="field__input" type="email" name="email" id="f-email" placeholder="Email" required autocomplete="email" />
          <div class="field__error" id="e-email">Enter a valid email</div>
        </div>
        <div class="field" data-f="phone">
          <input class="field__input" type="tel" name="phone" id="f-phone" placeholder="Phone (optional)" autocomplete="tel" />
        </div>
      </div>
    </div>

    <div class="form__section">
      <div class="form__section-label" id="sec-order">Your Order</div>
      <div class="form__row">
        <div class="field" data-f="quantity">
          <select class="field__select" name="quantity" id="f-qty" required>
            <option value="">Estimated quantity</option>
            <option value="10-30">10 &ndash; 30 kg</option>
            <option value="30-100">30 &ndash; 100 kg</option>
            <option value="100-500">100 &ndash; 500 kg</option>
            <option value="500-1000">500 kg &ndash; 1 t</option>
            <option value="1000+">1 t +</option>
          </select>
          <div class="field__error" id="e-qty">Required</div>
        </div>
        <div class="field" data-f="use_case">
          <select class="field__select" name="use_case" id="f-use">
            <option value="">Business type (optional)</option>
            <option value="cafe">Caf&eacute; / Coffee Shop</option>
            <option value="restaurant">Restaurant</option>
            <option value="hotel">Hotel / Hospitality</option>
            <option value="retail">Retail</option>
            <option value="distributor">Distributor / Importer</option>
            <option value="manufacturer">F&amp;B Manufacturer</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
      <div class="form__row form__row--full" style="margin-top:16px">
        <div class="field" data-f="country">
          <select class="field__select" name="country" id="f-country">
            <option value="">Country (optional)</option>
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="GB">United Kingdom</option>
            <option value="AU">Australia</option>
            <option value="JP">Japan</option>
            <option value="SG">Singapore</option>
            <option value="HK">Hong Kong</option>
            <option value="TW">Taiwan</option>
            <option value="KR">South Korea</option>
            <option value="DE">Germany</option>
            <option value="FR">France</option>
            <option value="NL">Netherlands</option>
            <option value="CH">Switzerland</option>
            <option value="SE">Sweden</option>
            <option value="AE">UAE</option>
            <option value="TH">Thailand</option>
            <option value="NZ">New Zealand</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
      </div>
    </div>

    <div class="form__section">
      <div class="form__section-label" id="sec-msg">Message</div>
      <div class="form__row form__row--full">
        <div class="field" data-f="message">
          <textarea class="field__textarea" name="message" id="f-msg" placeholder="Tell us about your needs, preferred products, timeline&hellip;" rows="4"></textarea>
        </div>
      </div>
    </div>

    <button class="submit" type="submit" id="btn"><span id="btn-text">Submit Inquiry</span></button>
  </form>

  <!-- Success -->
  <div class="success" id="success">
    <div class="success__icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
    </div>
    <h2 class="success__title" id="s-title">Received.</h2>
    <p class="success__sub" id="s-sub">We'll get back to you within 1&ndash;2 business days.</p>
    <a class="success__link" href="/wholesale" id="s-link">&larr; Back to Wholesale Portal</a>
  </div>

  <p class="note" id="note">
    Prefer email? <a href="mailto:wholesale@nakaiinfo.com">wholesale@nakaiinfo.com</a>
  </p>

</div>
<script>
(function(){{
  'use strict';
  function $(id){{return document.getElementById(id)}}

  var lang='en';
  var ja={{
    title:'\\u5378\\u58f2\\u30d1\\u30fc\\u30c8\\u30ca\\u30fc\\u30b7\\u30c3\\u30d7\\u3002',
    sub:'\\u304a\\u5ba2\\u69d8\\u306e\\u30d3\\u30b8\\u30cd\\u30b9\\u3092\\u304a\\u805e\\u304b\\u305b\\u304f\\u3060\\u3055\\u3044\\u30022\\u55b6\\u696d\\u65e5\\u4ee5\\u5185\\u306b\\u3054\\u63d0\\u6848\\u3044\\u305f\\u3057\\u307e\\u3059\\u3002',
    secAbout:'\\u304a\\u5ba2\\u69d8\\u306b\\u3064\\u3044\\u3066',secOrder:'\\u3054\\u6ce8\\u6587',secMsg:'\\u30e1\\u30c3\\u30bb\\u30fc\\u30b8',
    btn:'\\u9001\\u4fe1\\u3059\\u308b',sending:'\\u9001\\u4fe1\\u4e2d\\u2026',
    sTitle:'\\u53d7\\u3051\\u4ed8\\u3051\\u307e\\u3057\\u305f\\u3002',
    sSub:'1\\u301c2\\u55b6\\u696d\\u65e5\\u4ee5\\u5185\\u306b\\u3054\\u9023\\u7d61\\u3044\\u305f\\u3057\\u307e\\u3059\\u3002',
    sLink:'\\u2190 \\u5378\\u58f2\\u30dd\\u30fc\\u30bf\\u30eb\\u306b\\u623b\\u308b',
    back:'\\u623b\\u308b',note:'\\u30e1\\u30fc\\u30eb\\u3067\\u306e\\u304a\\u554f\\u3044\\u5408\\u308f\\u305b\\u306f <a href="mailto:wholesale@nakaiinfo.com">wholesale@nakaiinfo.com</a>',
    phCompany:'\\u4f1a\\u793e\\u540d',phName:'\\u304a\\u540d\\u524d',phEmail:'\\u30e1\\u30fc\\u30eb',phPhone:'\\u96fb\\u8a71\\u756a\\u53f7\\uff08\\u4efb\\u610f\\uff09',
    phQty:'\\u6ce8\\u6587\\u4e88\\u5b9a\\u91cf',phUse:'\\u696d\\u7a2e\\uff08\\u4efb\\u610f\\uff09',phCountry:'\\u56fd\\uff08\\u4efb\\u610f\\uff09',
    phMsg:'\\u3054\\u5e0c\\u671b\\u306e\\u5546\\u54c1\\u3001\\u7d0d\\u671f\\u306a\\u3069\\u3092\\u304a\\u77e5\\u3089\\u305b\\u304f\\u3060\\u3055\\u3044\\u2026'
  }};
  var en={{
    title:'Wholesale<br>Partnership.',
    sub:'Tell us about your business. We\\u2019ll prepare a tailored proposal within two business days.',
    secAbout:'About You',secOrder:'Your Order',secMsg:'Message',
    btn:'Submit Inquiry',sending:'Sending\\u2026',
    sTitle:'Received.',
    sSub:'We\\u2019ll get back to you within 1\\u20132 business days.',
    sLink:'\\u2190 Back to Wholesale Portal',
    back:'Back',note:'Prefer email? <a href="mailto:wholesale@nakaiinfo.com">wholesale@nakaiinfo.com</a>',
    phCompany:'Company',phName:'Your name',phEmail:'Email',phPhone:'Phone (optional)',
    phQty:'Estimated quantity',phUse:'Business type (optional)',phCountry:'Country (optional)',
    phMsg:'Tell us about your needs, preferred products, timeline\\u2026'
  }};

  function t(k){{return(lang==='ja'?ja:en)[k]||en[k]||''}}

  function setLang(l){{
    lang=l;
    $('nav-lang').textContent=l==='en'?'JA':'EN';
    $('nav-back').textContent=t('back');
    $('hd-title').innerHTML=t('title');
    $('hd-sub').textContent=t('sub');
    $('sec-about').textContent=t('secAbout');
    $('sec-order').textContent=t('secOrder');
    $('sec-msg').textContent=t('secMsg');
    $('btn-text').textContent=t('btn');
    $('s-title').textContent=t('sTitle');
    $('s-sub').textContent=t('sSub');
    $('s-link').textContent=t('sLink');
    $('note').innerHTML=t('note');
    /* placeholders */
    $('f-company').placeholder=t('phCompany');
    $('f-name').placeholder=t('phName');
    $('f-email').placeholder=t('phEmail');
    $('f-phone').placeholder=t('phPhone');
    $('f-msg').placeholder=t('phMsg');
    /* select first options */
    $('f-qty').options[0].textContent=t('phQty');
    $('f-use').options[0].textContent=t('phUse');
    $('f-country').options[0].textContent=t('phCountry');
  }}

  /* Toggle language */
  $('nav-lang').addEventListener('click',function(){{setLang(lang==='en'?'ja':'en')}});

  /* Validate */
  function validate(name){{
    var el=document.querySelector('[data-f="'+name+'"]');
    var inp=el.querySelector('input,select,textarea');
    var ok=name==='email'?/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(inp.value.trim()):inp.value.trim().length>0;
    el.classList.toggle('err',!ok);return ok;
  }}

  /* Clear error on input */
  document.querySelectorAll('.field__input,.field__select,.field__textarea').forEach(function(el){{
    el.addEventListener('input',function(){{var p=this.closest('.field');if(p)p.classList.remove('err')}});
  }});

  /* Submit */
  $('form').addEventListener('submit',function(e){{
    e.preventDefault();
    var ok=true;
    ['company','name','email','quantity'].forEach(function(f){{if(!validate(f))ok=false}});
    if(!ok)return;
    var btn=$('btn');btn.disabled=true;
    $('btn-text').innerHTML='<span class="spin"></span>'+t('sending');

    fetch('/api/wholesale-inquiry',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{
        company:$('f-company').value.trim(),
        name:$('f-name').value.trim(),
        email:$('f-email').value.trim(),
        phone:$('f-phone').value.trim(),
        country:$('f-country').value,
        quantity:$('f-qty').value,
        use_case:$('f-use').value,
        message:$('f-msg').value.trim(),
        language:lang
      }})
    }})
    .then(function(r){{if(!r.ok)throw new Error();return r.json()}})
    .then(function(){{
      document.querySelector('.form').classList.add('hide');
      document.querySelector('.header').style.display='none';
      $('success').classList.add('show');
      $('note').style.display='none';
    }})
    .catch(function(){{
      btn.disabled=false;
      $('btn-text').textContent=t('btn');
      alert('Something went wrong. Please try again.');
    }});
  }});

  /* Init — default English */
  try{{setLang('en')}}catch(e){{}}
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
    stored = False
    emailed = False

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
        stored = True
    except Exception as e:
        logger.error(f"Failed to store inquiry: {e}")

    try:
        from services.email_client import send_inquiry_notification
        emailed = await send_inquiry_notification(body)
    except Exception as e:
        logger.warning(f"Email notification skipped: {e}")

    if not stored and not emailed:
        return JSONResponse({"status": "error"}, status_code=500)

    return JSONResponse({"status": "ok"})
