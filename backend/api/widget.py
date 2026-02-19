"""Self-contained chat widget served from the backend.

Shopify only needs ONE script tag:
  <script src="https://nakai-matcha-chat.onrender.com/widget.js" defer></script>

This endpoint injects the full HTML, CSS, and JS into the page.
"""

from fastapi import APIRouter
from fastapi.responses import Response

widget_router = APIRouter()

WIDGET_JS = r"""
(function () {
  'use strict';

  // ---- Configuration ----
  var API_BASE = (document.currentScript && document.currentScript.src)
    ? document.currentScript.src.replace('/widget.js', '/api')
    : 'https://nakai-matcha-chat.onrender.com/api';
  var MAX_HISTORY = 20;
  var STAR_SVG = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>';

  // Detect language
  var PAGE_LANG = (document.documentElement.lang || 'en').substring(0, 2);

  // i18n
  var i18n = {
    en: {
      greeting: "Welcome to NAKAI! I'm your AI Matcha Concierge. Ask me anything — from brewing tips and health benefits to finding your perfect matcha.",
      placeholder: 'Ask about our matcha...',
      typing: 'AI is composing...',
      aiBanner: 'AI-powered answers based on our product knowledge',
      q1: 'Help me find the right matcha',
      q1msg: 'Help me find the perfect matcha for my needs',
      q2: 'Shipping & returns',
      q2msg: 'What are your shipping and return policies?',
      q3: 'Matcha health benefits',
      q3msg: 'What are the health benefits of matcha?',
      q4: 'How to prepare matcha',
      q4msg: 'How do I prepare matcha properly?',
      error: 'I\'m sorry, I\'m having a brief connection issue. Please try again in a moment, or visit our <a href="/pages/contact">Contact page</a> for assistance.',
      online: 'Online',
    },
    ja: {
      greeting: 'NAKAIへようこそ！AI抹茶コンシェルジュです。点て方や健康効果、あなたにぴったりの抹茶探しまで、何でもお気軽にお尋ねください。',
      placeholder: '抹茶について質問する...',
      typing: 'AIが回答を作成中...',
      aiBanner: 'AI が商品知識に基づいて回答します',
      q1: '自分に合う抹茶を探す',
      q1msg: '自分に合った抹茶を見つけたいです',
      q2: '配送・返品について',
      q2msg: '配送と返品のポリシーを教えてください',
      q3: '抹茶の健康効果',
      q3msg: '抹茶の健康効果について教えてください',
      q4: '抹茶の点て方',
      q4msg: '美味しい抹茶の点て方を教えてください',
      error: '申し訳ございません。接続に問題が発生しました。しばらくしてからもう一度お試しいただくか、<a href="/pages/contact">お問い合わせページ</a>からご連絡ください。',
      online: 'オンライン',
    }
  };

  function t(key) {
    return (i18n[PAGE_LANG] || i18n.en)[key] || i18n.en[key];
  }

  // ---- Inject CSS ----
  function injectStyles() {
    if (document.getElementById('nakai-chat-styles')) return;
    var style = document.createElement('style');
    style.id = 'nakai-chat-styles';
    style.textContent = WIDGET_CSS;
    document.head.appendChild(style);
  }

  // ---- Inject HTML ----
  function injectHTML() {
    if (document.getElementById('nakai-chat-widget')) return;
    var wrap = document.createElement('div');
    wrap.innerHTML = WIDGET_HTML();
    document.body.appendChild(wrap.firstElementChild);
  }

  function WIDGET_HTML() {
    return '<div id="nakai-chat-widget" class="nakai-chat">'
      // FAB Toggle
      + '<button id="nakai-chat-toggle" class="nakai-chat__toggle" aria-label="NAKAI Concierge AI" aria-expanded="false">'
      +   '<div class="nakai-chat__toggle-body">'
      +     '<span class="nakai-chat__toggle-dot"></span>'
      +     '<svg class="nakai-chat__toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>'
      +     '<div class="nakai-chat__toggle-text">'
      +       '<span class="nakai-chat__toggle-label">Nakai Concierge</span>'
      +       '<span class="nakai-chat__toggle-sep"></span>'
      +       '<span class="nakai-chat__toggle-ai">' + STAR_SVG + ' AI</span>'
      +     '</div>'
      +   '</div>'
      +   '<div class="nakai-chat__toggle-close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></div>'
      + '</button>'
      // Panel
      + '<div id="nakai-chat-panel" class="nakai-chat__panel" aria-hidden="true">'
      +   '<div class="nakai-chat__header">'
      +     '<div class="nakai-chat__header-left">'
      +       '<div class="nakai-chat__header-info">'
      +         '<span class="nakai-chat__header-title">NAKAI Concierge <span class="nakai-chat__ai-badge">' + STAR_SVG + ' AI</span></span>'
      +         '<div class="nakai-chat__header-status"><span class="nakai-chat__header-dot"></span><span class="nakai-chat__header-subtitle">' + t('online') + '</span></div>'
      +       '</div>'
      +     '</div>'
      +     '<button id="nakai-chat-close" class="nakai-chat__header-close" aria-label="Close chat"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></button>'
      +   '</div>'
      +   '<div id="nakai-chat-messages" class="nakai-chat__messages">'
      +     '<div class="nakai-chat__ai-intro">' + STAR_SVG + '<span>' + t('aiBanner') + '</span></div>'
      +     '<div class="nakai-chat__message nakai-chat__message--bot">'
      +       '<div class="nakai-chat__message-row"><div class="nakai-chat__avatar">' + STAR_SVG + '</div><div class="nakai-chat__message-content">' + t('greeting') + '</div></div>'
      +       '<div class="nakai-chat__quick-actions">'
      +         '<button class="nakai-chat__quick-btn" data-message="' + t('q1msg') + '"><span>' + t('q1') + '</span></button>'
      +         '<button class="nakai-chat__quick-btn" data-message="' + t('q2msg') + '"><span>' + t('q2') + '</span></button>'
      +         '<button class="nakai-chat__quick-btn" data-message="' + t('q3msg') + '"><span>' + t('q3') + '</span></button>'
      +         '<button class="nakai-chat__quick-btn" data-message="' + t('q4msg') + '"><span>' + t('q4') + '</span></button>'
      +       '</div>'
      +     '</div>'
      +   '</div>'
      +   '<div class="nakai-chat__input-area">'
      +     '<form id="nakai-chat-form" class="nakai-chat__form">'
      +       '<input type="text" id="nakai-chat-input" class="nakai-chat__input" placeholder="' + t('placeholder') + '" autocomplete="off" maxlength="500" />'
      +       '<button type="submit" class="nakai-chat__send" aria-label="Send"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z"/></svg></button>'
      +     '</form>'
      +   '</div>'
      +   '<div class="nakai-chat__footer">' + STAR_SVG + '<span>AI by NAKAI</span></div>'
      + '</div>'
    + '</div>';
  }

  // ---- Chat Logic ----
  var history = [];
  var isOpen = false;
  var isLoading = false;
  var SESSION_ID = (function(){
    var key = 'nakai_widget_session_id';
    var id = localStorage.getItem(key);
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID()
         : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
             var r = Math.random() * 16 | 0;
             return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
           });
      localStorage.setItem(key, id);
    }
    return id;
  })();

  function $(id) { return document.getElementById(id); }

  function openChat() {
    isOpen = true;
    var w = $('nakai-chat-widget');
    if (w) w.classList.add('nakai-chat--open');
    var p = $('nakai-chat-panel');
    if (p) p.setAttribute('aria-hidden', 'false');
    var tog = $('nakai-chat-toggle');
    if (tog) tog.setAttribute('aria-expanded', 'true');
    if (window.innerWidth > 749) {
      var inp = $('nakai-chat-input');
      if (inp) inp.focus();
    }
  }

  function closeChat() {
    isOpen = false;
    var w = $('nakai-chat-widget');
    if (w) w.classList.remove('nakai-chat--open');
    var p = $('nakai-chat-panel');
    if (p) p.setAttribute('aria-hidden', 'true');
    var tog = $('nakai-chat-toggle');
    if (tog) tog.setAttribute('aria-expanded', 'false');
  }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function formatMarkdown(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\n/g, '<br>');
  }

  function scrollToBottom() {
    var mc = $('nakai-chat-messages');
    if (mc) mc.scrollTop = mc.scrollHeight;
  }

  function addMessage(role, content, sources) {
    sources = sources || [];
    var mc = $('nakai-chat-messages');
    if (!mc) return;
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--' + role;

    var html = '';
    var contentHtml = role === 'bot' ? formatMarkdown(content) : escapeHtml(content);

    if (role === 'bot') {
      html += '<div class="nakai-chat__message-row">'
        + '<div class="nakai-chat__avatar">' + STAR_SVG + '</div>'
        + '<div class="nakai-chat__message-content">' + contentHtml + '</div>'
        + '</div>';
      if (sources.length > 0) {
        html += '<div class="nakai-chat__sources">';
        for (var i = 0; i < sources.length; i++) {
          var label = sources[i].indexOf('/products/') > -1 ? (PAGE_LANG === 'ja' ? '商品を見る' : 'View product')
            : sources[i].indexOf('/blogs/') > -1 ? (PAGE_LANG === 'ja' ? '記事を読む' : 'Read article')
            : (PAGE_LANG === 'ja' ? '詳細を見る' : 'Learn more');
          html += '<a href="' + escapeHtml(sources[i]) + '" class="nakai-chat__source-link">' + label + '</a>';
        }
        html += '</div>';
      }
      var now = new Date();
      var ts = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
      html += '<div class="nakai-chat__message-meta"><span class="nakai-chat__timestamp">' + ts + '</span><span class="nakai-chat__ai-tag">AI</span></div>';
    } else {
      html = '<div class="nakai-chat__message-content">' + contentHtml + '</div>';
    }
    div.innerHTML = html;
    mc.appendChild(div);
    scrollToBottom();
  }

  function showTyping() {
    var mc = $('nakai-chat-messages');
    if (!mc) return;
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--bot nakai-chat__typing-wrapper';
    div.innerHTML = '<div class="nakai-chat__message-row">'
      + '<div class="nakai-chat__avatar">' + STAR_SVG + '</div>'
      + '<div class="nakai-chat__typing-body">'
      + '<div class="nakai-chat__message-content nakai-chat__typing"><span></span><span></span><span></span></div>'
      + '<span class="nakai-chat__typing-label">' + t('typing') + '</span>'
      + '</div></div>';
    mc.appendChild(div);
    scrollToBottom();
  }

  function removeTyping() {
    var mc = $('nakai-chat-messages');
    if (!mc) return;
    var tw = mc.querySelector('.nakai-chat__typing-wrapper');
    if (tw) tw.remove();
  }

  function sendMessage() {
    var inp = $('nakai-chat-input');
    var msg = inp ? inp.value.trim() : '';
    if (!msg || isLoading) return;
    inp.value = '';
    addMessage('user', msg);
    history.push({ role: 'user', content: msg });
    showTyping();
    isLoading = true;

    fetch(API_BASE + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg,
        history: history.slice(-MAX_HISTORY),
        language: PAGE_LANG,
        session_id: SESSION_ID,
        source: 'widget',
      }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('API error');
        return res.json();
      })
      .then(function (data) {
        removeTyping();
        addMessage('bot', data.response, data.sources || []);
        history.push({ role: 'assistant', content: data.response });
        saveHistory();
      })
      .catch(function () {
        removeTyping();
        addMessage('bot', t('error'));
      })
      .finally(function () {
        isLoading = false;
      });
  }

  function saveHistory() {
    try {
      sessionStorage.setItem('nakai_chat_history', JSON.stringify(history.slice(-MAX_HISTORY)));
    } catch (e) { /* full */ }
  }

  function loadHistory() {
    try {
      var stored = sessionStorage.getItem('nakai_chat_history');
      if (stored) {
        history = JSON.parse(stored);
        history.forEach(function (msg) {
          addMessage(msg.role === 'assistant' ? 'bot' : 'user', msg.content);
        });
      }
    } catch (e) { /* corrupted */ }
  }

  function bindEvents() {
    var form = $('nakai-chat-form');
    if (form) form.addEventListener('submit', function (e) { e.preventDefault(); sendMessage(); });

    var toggle = $('nakai-chat-toggle');
    if (toggle) toggle.addEventListener('click', function () { isOpen ? closeChat() : openChat(); });

    var closeBtn = $('nakai-chat-close');
    if (closeBtn) closeBtn.addEventListener('click', closeChat);

    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && isOpen) closeChat(); });

    var widget = $('nakai-chat-widget');
    if (widget) {
      widget.querySelectorAll('.nakai-chat__quick-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var msg = this.getAttribute('data-message') || this.textContent.trim();
          var inp = $('nakai-chat-input');
          if (inp) { inp.value = msg; sendMessage(); }
          var qa = this.closest('.nakai-chat__quick-actions');
          if (qa) qa.style.display = 'none';
        });
      });
    }
  }

  // ---- CSS (embedded) ----
  var WIDGET_CSS = `
.nakai-chat{--nc-g1:#3D6142;--nc-g2:#7BA06D;--nc-g3:#5B8A52;--nc-tp:#9E8471;--nc-sd:#ECDDC7;--nc-pm:#F5EDE1;--nc-bg:#FFF;--nc-s0:#FAFAF6;--nc-s1:#FFF;--nc-s2:rgba(61,97,66,.028);--nc-tx:#161614;--nc-t2:#7A766D;--nc-t3:#B0AAA0;--nc-ln:rgba(61,97,66,.07);--nc-ln2:rgba(61,97,66,.12);--nc-sh:0 0 0 .5px rgba(0,0,0,.03),0 24px 80px -16px rgba(61,97,66,.13),0 8px 24px -12px rgba(0,0,0,.05);--nc-sh2:0 0 0 .5px rgba(0,0,0,.02),0 1px 4px rgba(61,97,66,.04);--nc-rr:9999px;--nc-e:cubic-bezier(.22,1,.36,1);--nc-es:cubic-bezier(.34,1.4,.64,1);--nc-eo:cubic-bezier(.16,1,.3,1);position:fixed;bottom:32px;right:32px;z-index:9990;font-family:'Work Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
.nakai-chat *,.nakai-chat *::before,.nakai-chat *::after{box-sizing:border-box;margin:0;padding:0}
.nakai-chat__toggle{height:48px;border-radius:var(--nc-rr);border:none;cursor:pointer;display:flex;align-items:center;gap:0;background:linear-gradient(145deg,#4A7350 0%,var(--nc-g1) 50%,#325238 100%);color:rgba(255,255,255,.92);box-shadow:var(--nc-sh),inset 0 1px 0 rgba(255,255,255,.1);transition:all .5s var(--nc-es);position:relative;overflow:hidden;padding:0;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__toggle::before{content:'';position:absolute;top:-30%;left:-10%;width:50%;height:60%;background:radial-gradient(circle,rgba(255,255,255,.15) 0%,transparent 70%);pointer-events:none}
.nakai-chat__toggle::after{content:'';position:absolute;inset:0;border-radius:var(--nc-rr);box-shadow:inset 0 -2px 4px rgba(0,0,0,.08);pointer-events:none}
.nakai-chat:not(.nakai-chat--open) .nakai-chat__toggle{animation:nakaiBreathe 4s ease-in-out infinite}
@keyframes nakaiBreathe{0%,100%{box-shadow:0 0 0 .5px rgba(0,0,0,.03),0 24px 80px -16px rgba(61,97,66,.13),0 8px 24px -12px rgba(0,0,0,.05),inset 0 1px 0 rgba(255,255,255,.1)}50%{box-shadow:0 0 0 .5px rgba(0,0,0,.03),0 28px 88px -16px rgba(61,97,66,.18),0 10px 28px -12px rgba(0,0,0,.07),inset 0 1px 0 rgba(255,255,255,.1)}}
.nakai-chat__toggle:hover{transform:translateY(-2px);box-shadow:0 0 0 .5px rgba(0,0,0,.03),0 28px 88px -12px rgba(61,97,66,.22),0 12px 32px -8px rgba(0,0,0,.08),inset 0 1px 0 rgba(255,255,255,.1)}
.nakai-chat__toggle:active{transform:translateY(0) scale(.97);transition-duration:.12s}
.nakai-chat__toggle-body{display:flex;align-items:center;gap:12px;padding:0 20px 0 16px;height:100%;position:relative;z-index:1}
.nakai-chat__toggle-icon{width:20px;height:20px;flex-shrink:0;opacity:.85;filter:drop-shadow(0 1px 2px rgba(0,0,0,.1))}
.nakai-chat__toggle-text{display:flex;align-items:center;gap:8px;line-height:1;white-space:nowrap}
.nakai-chat__toggle-label{font-size:1.05rem;font-weight:400;letter-spacing:.14em;text-transform:uppercase;opacity:.88}
.nakai-chat__toggle-sep{width:1px;height:16px;background:rgba(255,255,255,.12);flex-shrink:0}
.nakai-chat__toggle-ai{display:inline-flex;align-items:center;gap:3px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.08);border-radius:var(--nc-rr);padding:3px 8px 3px 6px;font-size:.9rem;font-weight:450;letter-spacing:.08em;color:rgba(255,255,255,.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.nakai-chat__toggle-ai svg{width:9px;height:9px;opacity:.8}
.nakai-chat__toggle-dot{width:5px;height:5px;border-radius:var(--nc-rr);background:#7ED67E;box-shadow:0 0 6px rgba(126,214,126,.5);flex-shrink:0;animation:nakaiPulse 3s ease-in-out infinite}
.nakai-chat__toggle-close{display:none;width:48px;height:48px;align-items:center;justify-content:center}
.nakai-chat__toggle-close svg{width:14px;height:14px;stroke-width:2}
.nakai-chat--open .nakai-chat__toggle-body{display:none}
.nakai-chat--open .nakai-chat__toggle-close{display:flex}
.nakai-chat--open .nakai-chat__toggle{width:48px;padding:0}
.nakai-chat__panel{position:absolute;bottom:calc(48px + 16px);right:0;width:380px;height:620px;background:var(--nc-s1);border:1px solid var(--nc-ln);border-radius:28px;box-shadow:var(--nc-sh);display:flex;flex-direction:column;overflow:hidden;opacity:0;transform:translateY(12px) scale(.92);pointer-events:none;transition:opacity .45s var(--nc-eo),transform .55s var(--nc-es)}
.nakai-chat--open .nakai-chat__panel{opacity:1;transform:translateY(0) scale(1);pointer-events:auto}
.nakai-chat__header{display:flex;align-items:center;justify-content:space-between;padding:18px 22px;background:linear-gradient(180deg,#436E48 0%,var(--nc-g1) 100%);color:rgba(255,255,255,.92);flex-shrink:0;position:relative;box-shadow:0 1px 0 rgba(0,0,0,.06)}
.nakai-chat__header::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:rgba(255,255,255,.08)}
.nakai-chat__header-left{display:flex;align-items:center;gap:12px}
.nakai-chat__header-info{display:flex;flex-direction:column;gap:3px}
.nakai-chat__header-title{display:flex;align-items:center;gap:6px;font-weight:400;font-size:1.1rem;letter-spacing:.1em;text-transform:uppercase;line-height:1;opacity:.88}
.nakai-chat__ai-badge{display:inline-flex;align-items:center;gap:3px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.08);border-radius:var(--nc-rr);padding:2px 7px 2px 5px;font-size:.85rem;font-weight:450;letter-spacing:.08em;color:rgba(255,255,255,.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.nakai-chat__ai-badge svg{width:9px;height:9px;opacity:.8}
.nakai-chat__header-status{display:flex;align-items:center;gap:5px}
.nakai-chat__header-dot{width:5px;height:5px;border-radius:var(--nc-rr);background:#7ED67E;box-shadow:0 0 6px rgba(126,214,126,.4);animation:nakaiPulse 3s ease-in-out infinite}
@keyframes nakaiPulse{0%,100%{opacity:1;box-shadow:0 0 6px rgba(126,214,126,.4)}50%{opacity:.65;box-shadow:0 0 12px rgba(126,214,126,.15)}}
.nakai-chat__header-subtitle{font-weight:300;font-size:.9rem;color:rgba(255,255,255,.35);letter-spacing:.06em;line-height:1}
.nakai-chat__header-close{width:24px;height:24px;border-radius:var(--nc-rr);background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.05);color:rgba(255,255,255,.4);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .3s var(--nc-e)}
.nakai-chat__header-close:hover{background:rgba(255,255,255,.1);color:rgba(255,255,255,.8);border-color:rgba(255,255,255,.08)}
.nakai-chat__header-close svg{width:11px;height:11px;stroke-width:2.5}
.nakai-chat__messages{flex:1;overflow-y:auto;padding:20px 22px;display:flex;flex-direction:column;gap:2px;scroll-behavior:smooth;background:var(--nc-s1)}
.nakai-chat__messages::-webkit-scrollbar{width:0}
.nakai-chat__ai-intro{display:flex;align-items:center;justify-content:center;gap:6px;padding:8px 14px;margin:0 0 14px;background:linear-gradient(135deg,rgba(61,97,66,.04),rgba(123,160,109,.04));border:1px solid var(--nc-ln);border-radius:12px;font-size:1.05rem;font-weight:400;color:var(--nc-t2);letter-spacing:.02em;line-height:1.4}
.nakai-chat__ai-intro svg{width:14px;height:14px;color:var(--nc-g2);flex-shrink:0;opacity:.7}
.nakai-chat__message{display:flex;flex-direction:column;animation:nakaiMsgIn .3s var(--nc-eo) both}
@keyframes nakaiMsgIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.nakai-chat__message--bot{align-items:flex-start;padding-right:40px}
.nakai-chat__message--user{align-items:flex-end;padding-left:40px;margin-top:6px}
.nakai-chat__message--bot+.nakai-chat__message--bot{margin-top:2px}
.nakai-chat__message--user+.nakai-chat__message--user{margin-top:2px}
.nakai-chat__message--bot+.nakai-chat__message--user,.nakai-chat__message--user+.nakai-chat__message--bot{margin-top:14px}
.nakai-chat__message--bot .nakai-chat__message-row{display:flex;align-items:flex-start;gap:10px}
.nakai-chat__avatar{width:26px;height:26px;border-radius:10px;flex-shrink:0;margin-top:1px;background:linear-gradient(145deg,rgba(61,97,66,.08),rgba(123,160,109,.06));border:1px solid var(--nc-ln);display:flex;align-items:center;justify-content:center}
.nakai-chat__avatar svg{width:12px;height:12px;color:var(--nc-g2);opacity:.75}
.nakai-chat__message--bot .nakai-chat__message-content{background:var(--nc-s2);color:var(--nc-tx);border-radius:4px 20px 20px 20px;padding:13px 16px;font-size:1.35rem;font-weight:400;line-height:1.72;letter-spacing:.008em;word-wrap:break-word}
.nakai-chat__message--user .nakai-chat__message-content{background:linear-gradient(145deg,#4A7350,var(--nc-g1));color:rgba(255,255,255,.94);border-radius:20px 20px 4px 20px;padding:13px 16px;font-size:1.35rem;font-weight:400;line-height:1.72;letter-spacing:.008em;word-wrap:break-word;box-shadow:0 2px 12px rgba(61,97,66,.1),inset 0 1px 0 rgba(255,255,255,.06)}
.nakai-chat__message-content a{color:var(--nc-g3);text-decoration:none;font-weight:450;background:linear-gradient(to right,var(--nc-g2),var(--nc-g2)) no-repeat 0 100%/100% 1px;transition:all .3s var(--nc-e);padding-bottom:1px}
.nakai-chat__message-content a:hover{color:var(--nc-g1);background-size:100% 1.5px}
.nakai-chat__message--user .nakai-chat__message-content a{color:rgba(255,255,255,.88);background-image:linear-gradient(to right,rgba(255,255,255,.3),rgba(255,255,255,.3))}
.nakai-chat__message-content strong{font-weight:500}
.nakai-chat__message-meta{display:flex;align-items:center;gap:6px;margin-top:5px;padding:0 0 0 36px}
.nakai-chat__timestamp{font-size:.9rem;font-weight:350;color:var(--nc-t3);letter-spacing:.06em}
.nakai-chat__ai-tag{font-size:.8rem;font-weight:450;letter-spacing:.1em;text-transform:uppercase;color:var(--nc-g2);opacity:.6}
.nakai-chat__sources{margin-top:.6rem;display:flex;flex-wrap:wrap;gap:.4rem}
.nakai-chat__source-link{font-size:1.1rem;color:var(--nc-g3);text-decoration:none;font-weight:450;background:linear-gradient(to right,var(--nc-g2),var(--nc-g2)) no-repeat 0 100%/100% 1px;opacity:.8;transition:all .3s var(--nc-e);padding-bottom:1px}
.nakai-chat__source-link:hover{opacity:1;background-size:100% 1.5px}
.nakai-chat__typing-wrapper .nakai-chat__message-row{display:flex;align-items:flex-start;gap:10px}
.nakai-chat__typing-body{display:flex;flex-direction:column;gap:6px}
.nakai-chat__typing{display:flex;gap:6px;align-items:center;height:12px;padding:14px 18px!important}
.nakai-chat__typing span{width:4px;height:4px;background:var(--nc-g2);border-radius:var(--nc-rr);display:inline-block;animation:nakaiWave 1.6s ease-in-out infinite}
.nakai-chat__typing span:nth-child(2){animation-delay:.15s}
.nakai-chat__typing span:nth-child(3){animation-delay:.3s}
@keyframes nakaiWave{0%,60%,100%{opacity:.15;transform:translateY(0)}30%{opacity:.8;transform:translateY(-4px)}}
.nakai-chat__typing-label{font-size:.95rem;font-weight:350;color:var(--nc-t3);letter-spacing:.04em;padding-left:2px;animation:nakaiTypeIn .4s var(--nc-eo) both}
@keyframes nakaiTypeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.nakai-chat__quick-actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;padding-left:36px}
.nakai-chat__quick-btn{font-family:'Work Sans',sans-serif;font-size:1.1rem;font-weight:400;color:var(--nc-g1);background:var(--nc-s1);border:1px solid var(--nc-ln2);border-radius:var(--nc-rr);padding:7px 14px;cursor:pointer;letter-spacing:.03em;transition:all .35s var(--nc-e);position:relative;overflow:hidden;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__quick-btn::before{content:'';position:absolute;inset:0;background:var(--nc-g1);border-radius:var(--nc-rr);transform:scaleX(0);transform-origin:left;transition:transform .35s var(--nc-e)}
.nakai-chat__quick-btn:hover{border-color:var(--nc-g1);color:rgba(255,255,255,.94);transform:translateY(-1px);box-shadow:0 4px 12px rgba(61,97,66,.12)}
.nakai-chat__quick-btn:hover::before{transform:scaleX(1)}
.nakai-chat__quick-btn span{position:relative;z-index:1}
.nakai-chat__input-area{padding:14px 20px 18px;background:var(--nc-s1);flex-shrink:0;position:relative}
.nakai-chat__input-area::before{content:'';position:absolute;top:0;left:22px;right:22px;height:1px;background:var(--nc-ln)}
.nakai-chat__form{display:flex;align-items:center;gap:8px;background:var(--nc-s0);border:1px solid var(--nc-ln);border-radius:var(--nc-rr);padding:5px 5px 5px 18px;transition:all .4s var(--nc-e)}
.nakai-chat__form:focus-within{border-color:rgba(123,160,109,.35);box-shadow:0 0 0 4px rgba(61,97,66,.04);background:var(--nc-s1)}
.nakai-chat__input{flex:1;border:none;background:transparent;color:var(--nc-tx);font-family:'Work Sans',sans-serif;font-size:1.3rem;font-weight:350;letter-spacing:.015em;outline:none;padding:6px 0}
.nakai-chat__input::placeholder{color:var(--nc-t3);font-weight:300;letter-spacing:.03em}
.nakai-chat__send{width:34px;height:34px;border-radius:var(--nc-rr);border:none;background:linear-gradient(145deg,#4A7350,var(--nc-g1));color:rgba(255,255,255,.88);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .3s var(--nc-e);position:relative;overflow:hidden;box-shadow:inset 0 1px 0 rgba(255,255,255,.08);touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__send::before{content:'';position:absolute;top:-10%;left:-10%;width:50%;height:50%;background:radial-gradient(circle,rgba(255,255,255,.2) 0%,transparent 70%);pointer-events:none}
.nakai-chat__send:hover{transform:scale(1.1);box-shadow:0 2px 8px rgba(61,97,66,.15),inset 0 1px 0 rgba(255,255,255,.08)}
.nakai-chat__send:active{transform:scale(.92)}
.nakai-chat__send:disabled{opacity:.5;cursor:not-allowed}
.nakai-chat__send svg{width:13px;height:13px;margin-left:1px}
.nakai-chat__footer{display:flex;align-items:center;justify-content:center;gap:5px;padding:2px 0 13px;background:var(--nc-s1)}
.nakai-chat__footer svg{width:9px;height:9px;color:var(--nc-t3);opacity:.3}
.nakai-chat__footer span{font-size:.85rem;font-weight:300;color:var(--nc-t3);letter-spacing:.12em;text-transform:uppercase;opacity:.3}
[data-scheme="dark"] .nakai-chat{--nc-bg:#0C0E0C;--nc-s0:#131513;--nc-s1:#181B18;--nc-s2:rgba(123,160,109,.04);--nc-tx:#E4E5E0;--nc-t2:#7D807A;--nc-t3:#4E514A;--nc-ln:rgba(255,255,255,.04);--nc-ln2:rgba(255,255,255,.07);--nc-sh:0 0 0 .5px rgba(255,255,255,.03),0 24px 80px -16px rgba(0,0,0,.7);--nc-sh2:0 1px 4px rgba(0,0,0,.3)}
[data-scheme="dark"] .nakai-chat__toggle{background:linear-gradient(145deg,#8FB87C,var(--nc-g2),#6A9960);color:#0C0E0C;box-shadow:var(--nc-sh),inset 0 1px 0 rgba(255,255,255,.12)}
[data-scheme="dark"] .nakai-chat__toggle-ai{background:rgba(0,0,0,.15);border-color:rgba(0,0,0,.1);color:rgba(12,14,12,.65)}
[data-scheme="dark"] .nakai-chat__toggle-sep{background:rgba(0,0,0,.1)}
[data-scheme="dark"] .nakai-chat__toggle-dot{background:#2D5A2D;box-shadow:0 0 6px rgba(45,90,45,.4)}
[data-scheme="dark"] .nakai-chat__header{background:linear-gradient(180deg,#1C201C,#151815);box-shadow:0 1px 0 rgba(255,255,255,.03)}
[data-scheme="dark"] .nakai-chat__header::before{background:rgba(255,255,255,.04)}
[data-scheme="dark"] .nakai-chat__ai-badge{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.05)}
[data-scheme="dark"] .nakai-chat__ai-intro{background:linear-gradient(135deg,rgba(123,160,109,.06),rgba(123,160,109,.03));border-color:var(--nc-ln)}
[data-scheme="dark"] .nakai-chat__avatar{background:linear-gradient(145deg,rgba(123,160,109,.1),rgba(123,160,109,.05));border-color:var(--nc-ln)}
[data-scheme="dark"] .nakai-chat__avatar svg{color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__message--user .nakai-chat__message-content{background:linear-gradient(145deg,#8FB87C,var(--nc-g2));color:#0C0E0C;box-shadow:0 2px 12px rgba(123,160,109,.08),inset 0 1px 0 rgba(255,255,255,.1)}
[data-scheme="dark"] .nakai-chat__send{background:linear-gradient(145deg,#8FB87C,var(--nc-g2));color:#0C0E0C}
[data-scheme="dark"] .nakai-chat__quick-btn{color:var(--nc-g2);border-color:rgba(123,160,109,.15)}
[data-scheme="dark"] .nakai-chat__quick-btn::before{background:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__quick-btn:hover{color:#0C0E0C;border-color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__message-content a{color:var(--nc-g2);background-image:linear-gradient(to right,rgba(123,160,109,.35),rgba(123,160,109,.35))}
[data-scheme="dark"] .nakai-chat__source-link{color:var(--nc-g2);background-image:linear-gradient(to right,rgba(123,160,109,.35),rgba(123,160,109,.35))}
[data-scheme="dark"] .nakai-chat__header-dot{background:#7ED67E;box-shadow:0 0 8px rgba(126,214,126,.3)}
@media screen and (max-width:749px){
  .nakai-chat{bottom:20px;right:16px}
  .nakai-chat__toggle-label{font-size:.95rem;letter-spacing:.12em}
  .nakai-chat__panel{position:fixed;top:0;left:0;right:0;bottom:0;width:100%;height:100%;max-height:-webkit-fill-available;border-radius:0;border:none;transform:translateY(100%);opacity:1}
  .nakai-chat--open .nakai-chat__panel{transform:translateY(0)}
  .nakai-chat--open .nakai-chat__toggle{display:none}
  .nakai-chat__messages{padding:16px}
  .nakai-chat__message--bot .nakai-chat__message-content,.nakai-chat__message--user .nakai-chat__message-content{font-size:1.05rem;line-height:1.6;padding:10px 14px}
  .nakai-chat__ai-intro{font-size:.9rem;padding:6px 10px;margin:0 0 10px}
  .nakai-chat__quick-actions{padding-left:36px;gap:5px}
  .nakai-chat__quick-btn{font-size:.95rem;padding:6px 12px}
  .nakai-chat__input-area{padding:10px 14px 14px}
  .nakai-chat__input{font-size:16px}
  .nakai-chat__header{padding:14px 16px}
  .nakai-chat__header-close{width:32px;height:32px}
  .nakai-chat__header-close svg{width:14px;height:14px}
  .nakai-chat__footer{padding:2px 0 max(10px,env(safe-area-inset-bottom))}
}
.template-page-chat .nakai-chat{display:none}
`;

  // ---- Boot ----
  function boot() {
    // Don't load on the dedicated chat page
    if (document.body.classList.contains('template-page-chat')) return;
    injectStyles();
    injectHTML();
    bindEvents();
    loadHistory();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
"""


@widget_router.get("/widget.js")
async def serve_widget():
    """Serve the self-contained chat widget JavaScript."""
    return Response(
        content=WIDGET_JS,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=300",
            "Access-Control-Allow-Origin": "*",
        },
    )
