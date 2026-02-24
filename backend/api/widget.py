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
  var SHOP_URL = 'https://nakaimatcha.com';
  var MAX_HISTORY = 20;
  var STAR_SVG = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>';

  // Known product name → handle mapping
  var PRODUCT_MAP = {
    'revi': '/products/revi-organic-matcha-20g-ss-grade-plus',
    'ikigai': '/products/ikigai-organic-matcha-40g-ss-grade',
    'exquisite matcha set': '/products/the-exquisite-matcha-set',
    '\u30a8\u30af\u30b9\u30ad\u30b8\u30c3\u30c8\u62b9\u8336\u30bb\u30c3\u30c8': '/products/the-exquisite-matcha-set',
    '\u62b9\u8336\u30bb\u30c3\u30c8': '/products/the-exquisite-matcha-set'
  };

  // Detect language
  var PAGE_LANG = (document.documentElement.lang || 'en').substring(0, 2);

  // Session ID
  var SESSION_ID = (function () {
    var key = 'nakai_widget_session_id';
    var id;
    try { id = sessionStorage.getItem(key); } catch(e) {}
    if (!id) {
      id = typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : 'w-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
      try { sessionStorage.setItem(key, id); } catch(e) {}
    }
    return id;
  })();

  // Streaming support
  var supportsStream = typeof ReadableStream !== 'undefined'
    && typeof TextDecoder !== 'undefined';

  // i18n
  var i18n = {
    en: {
      greeting: "Hi there! I'm your matcha concierge. Whether you're new to matcha or a daily drinker, I'm here to help you find the perfect cup.",
      placeholder: 'Ask about matcha...',
      typing: 'AI is composing...',
      aiBanner: 'AI-powered answers based on our matcha expertise',
      q1: 'Find my matcha',
      q1msg: "I'd like to find the right matcha for me. Can you help?",
      q2: 'Make a matcha latte',
      q2msg: 'How do I make the perfect matcha latte at home?',
      q3: 'Why NAKAI?',
      q3msg: 'What makes NAKAI matcha different from other matcha brands?',
      q4: 'Health benefits',
      q4msg: 'What are the health benefits of drinking matcha daily?',
      error: "Sorry, I'm having trouble connecting right now.",
      errorRetry: 'Retry',
      online: 'Online',
      viewProduct: 'View product',
      readArticle: 'Read article',
      learnMore: 'Learn more',
    },
    ja: {
      greeting: 'こんにちは！抹茶コンシェルジュです。初めての方も毎日飲む方も、あなたにぴったりの一杯を一緒に見つけましょう。',
      placeholder: '抹茶について質問する...',
      typing: 'AIが回答を作成中...',
      aiBanner: 'AIが抹茶の専門知識に基づいて回答します',
      q1: '自分に合う抹茶',
      q1msg: '自分に合う抹茶を探しています。いくつか質問してもらえますか？',
      q2: '抹茶ラテの作り方',
      q2msg: '自宅で美味しい抹茶ラテを作る方法を教えてください',
      q3: 'NAKAIの特別さ',
      q3msg: 'NAKAIの抹茶は他の抹茶と何が違うのですか？',
      q4: '健康効果',
      q4msg: '抹茶を毎日飲むとどんな健康効果がありますか？',
      error: '接続に問題が発生しました。',
      errorRetry: '再試行',
      online: 'オンライン',
      viewProduct: '商品を見る',
      readArticle: '記事を読む',
      learnMore: '詳細',
    }
  };

  function t(key) {
    return (i18n[PAGE_LANG] || i18n.en)[key] || i18n.en[key];
  }

  function $(id) { return document.getElementById(id); }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function formatMarkdown(text) {
    if (!text) return '';
    text = escapeHtml(text);
    return text
      .replace(/^#{1,6}\s+(.*?)$/gm, '<strong>$1</strong>')
      .replace(/^\s*-{3,}\s*$/gm, '')
      .replace(/^\s*\*{3,}\s*$/gm, '')
      .replace(/^\s*_{3,}\s*$/gm, '')
      .replace(/^\|.*\|$/gm, '')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.*?)\]\(\/(.*?)\)/g, '<a href="' + SHOP_URL + '/$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\[(.*?)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/^\s*[*+-]\s+(.*?)$/gm, '<li>$1</li>')
      .replace(/^\d+\.\s+(.*?)$/gm, '<li>$1</li>')
      .replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>')
      .replace(/^\t+/gm, '')
      .replace(/\n{2,}/g, ' ')
      .replace(/\n/g, ' ')
      .replace(/ {2,}/g, ' ')
      .replace(/(<br>){2,}/g, '<br>')
      .replace(/^(<br>| )+/, '')
      .replace(/(<br>| )+$/, '');
  }

  function scrollToBottom() {
    var mc = $('nakai-chat-messages');
    if (mc) mc.scrollTop = mc.scrollHeight;
  }

  function extractProducts(text) {
    var re = /\[PRODUCT:([a-z0-9-]+)\]/gi; var handles = []; var m;
    while ((m = re.exec(text)) !== null) handles.push(m[1]);
    var cleaned = text.replace(/\[PRODUCT:[a-z0-9-]+\]/gi, '').trim();
    return { handles: handles, text: cleaned };
  }

  function fetchAndRenderProducts(handles, parentEl) {
    if (!handles.length) return;
    var carousel = document.createElement('div');
    carousel.className = 'nakai-chat__product-grid';
    handles.forEach(function(handle) {
      var card = document.createElement('a');
      card.className = 'nakai-chat__product-card';
      card.href = SHOP_URL + '/products/' + handle;
      card.target = '_blank'; card.rel = 'noopener';
      card.innerHTML = '<div class="nakai-chat__product-card-img" style="background:linear-gradient(90deg,rgba(61,97,66,.04) 25%,rgba(61,97,66,.08) 50%,rgba(61,97,66,.04) 75%);background-size:200% 100%;animation:nakaiShimmer 1.5s infinite"></div><div class="nakai-chat__product-card-body"><div class="nakai-chat__product-card-title" style="height:2.6em;background:rgba(61,97,66,.04);border-radius:4px"></div></div>';
      carousel.appendChild(card);
      fetch('https://nakaimatcha.com/products/' + handle + '.json')
        .then(function(r) { if (!r.ok) throw new Error('err'); return r.json(); })
        .then(function(data) {
          var p = data.product;
          var img = p.images && p.images.length ? p.images[0].src : '';
          var price = p.variants && p.variants.length ? p.variants[0].price : '';
          card.innerHTML = (img ? '<img class="nakai-chat__product-card-img" src="' + img + '" alt="' + escapeHtml(p.title) + '" loading="lazy">' : '<div class="nakai-chat__product-card-img"></div>')
            + '<div class="nakai-chat__product-card-body">'
            + '<div class="nakai-chat__product-card-title">' + escapeHtml(p.title) + '</div>'
            + (price ? '<div class="nakai-chat__product-card-price">$' + price + '</div>' : '')
            + '<div style="font-size:.7rem;font-weight:500;color:var(--nc-g1);margin-top:4px">' + (PAGE_LANG === 'ja' ? '商品を見る →' : 'View Product →') + '</div>'
            + '</div>';
        })
        .catch(function() { var t = card.querySelector('.nakai-chat__product-card-title'); if (t) t.textContent = PAGE_LANG === 'ja' ? '商品を見る' : 'View Product'; });
    });
    parentEl.appendChild(carousel);
    scrollToBottom();
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
      + '<button id="nakai-chat-toggle" class="nakai-chat__toggle" aria-label="Find My Matcha AI" aria-expanded="false">'
      +   '<div class="nakai-chat__toggle-body">'
      +     '<span class="nakai-chat__toggle-label">FIND MY MATCHA</span>'
      +     '<span class="nakai-chat__toggle-sep"></span>'
      +     '<span class="nakai-chat__toggle-ai">by AI</span>'
      +   '</div>'
      +   '<div class="nakai-chat__toggle-close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></div>'
      + '</button>'
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

  // ---- Chat State ----
  var history = [];
  var isOpen = false;
  var isLoading = false;
  var lastUserMessage = '';
  var sendBtn = null;

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

  // ---- Send Button Loading ----
  function setSendLoading(on) {
    if (!sendBtn) return;
    if (on) {
      sendBtn.classList.add('nakai-chat__send--loading');
      sendBtn.disabled = true;
    } else {
      sendBtn.classList.remove('nakai-chat__send--loading');
      sendBtn.disabled = false;
    }
  }

  // ---- Error HTML with Retry ----
  function getErrorHtml() {
    return '<div class="nakai-chat__error-content">'
      + '<span>' + t('error') + '</span>'
      + '<button class="nakai-chat__retry-btn" type="button">' + t('errorRetry') + '</button>'
      + '</div>';
  }

  function bindRetry(msgDiv) {
    var btn = msgDiv.querySelector('.nakai-chat__retry-btn');
    if (btn) {
      btn.addEventListener('click', function () {
        msgDiv.remove();
        isLoading = false;
        setSendLoading(false);
        sendMessage(lastUserMessage);
      });
    }
  }

  // ---- Message Helpers ----
  function addUserMessage(content) {
    var mc = $('nakai-chat-messages');
    if (!mc) return;
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--user';
    div.innerHTML = '<div class="nakai-chat__message-content">' + escapeHtml(content) + '</div>';
    mc.appendChild(div);
    scrollToBottom();
  }

  function addBotError() {
    var mc = $('nakai-chat-messages');
    if (!mc) return;
    var msgDiv = document.createElement('div');
    msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
    msgDiv.innerHTML =
      '<div class="nakai-chat__message-row">'
      + '<div class="nakai-chat__avatar">' + STAR_SVG + '</div>'
      + '<div class="nakai-chat__message-content">' + getErrorHtml() + '</div>'
      + '</div>';
    mc.appendChild(msgDiv);
    bindRetry(msgDiv);
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

  // ---- Finish stream: sources, suggestions, timestamp ----
  function finishStreamMessage(msgDiv, bubble, fullText, sources, suggestions) {
    sources = sources || [];
    suggestions = suggestions || [];

    // Strip [SUGGESTIONS] block (handles **[SUGGESTIONS]** too)
    var sugM = fullText.match(/\*{0,2}\[SUGGESTIONS\]\*{0,2}/);
    if (sugM) {
      fullText = fullText.substring(0, sugM.index).trim();
    }

    // Strip [CHOICES] block and extract options (handles **[CHOICES]** too)
    var choices = [];
    var choiceM = fullText.match(/\*{0,2}\[CHOICES\]\*{0,2}/);
    if (choiceM) {
      var choiceEnd = fullText.match(/\*{0,2}\[\/CHOICES\]\*{0,2}/);
      if (choiceEnd) {
        var choiceStr = fullText.substring(choiceM.index + choiceM[0].length, choiceEnd.index).trim();
        choices = choiceStr.split('|').map(function (c) { return c.trim(); }).filter(Boolean);
        fullText = fullText.substring(0, choiceM.index).trim() + fullText.substring(choiceEnd.index + choiceEnd[0].length).trim();
      }
    }

    // Extract [PRODUCT:handle] tags
    var prodResult = extractProducts(fullText);
    fullText = prodResult.text;
    bubble.innerHTML = formatMarkdown(fullText);

    // Product carousel
    if (prodResult.handles.length > 0) {
      fetchAndRenderProducts(prodResult.handles, msgDiv);
    }

    // Choice buttons
    if (choices.length > 0) {
      var choiceDiv = document.createElement('div');
      choiceDiv.className = 'nakai-chat__choices';
      choices.forEach(function (text) {
        var btn = document.createElement('button');
        btn.className = 'nakai-chat__choice-btn';
        btn.type = 'button';
        btn.textContent = text;
        btn.addEventListener('click', function () {
          inputEl.value = text;
          formEl.dispatchEvent(new Event('submit'));
          choiceDiv.querySelectorAll('.nakai-chat__choice-btn').forEach(function (b) {
            b.disabled = true;
            b.classList.add('nakai-chat__choice-btn--disabled');
          });
          btn.classList.add('nakai-chat__choice-btn--selected');
        });
        choiceDiv.appendChild(btn);
      });
      msgDiv.appendChild(choiceDiv);
    }

    // Source links
    if (sources.length > 0) {
      var srcDiv = document.createElement('div');
      srcDiv.className = 'nakai-chat__sources';
      for (var i = 0; i < sources.length; i++) {
        var s = sources[i];
        var url = s.startsWith('/') ? SHOP_URL + s : s;
        var label = s.indexOf('/products/') > -1 ? t('viewProduct')
          : s.indexOf('/blogs/') > -1 ? t('readArticle')
          : t('learnMore');
        var a = document.createElement('a');
        a.href = url;
        a.className = 'nakai-chat__source-link';
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = label;
        srcDiv.appendChild(a);
      }
      msgDiv.appendChild(srcDiv);
    }

    // Product cards from sources + text mentions
    renderProductCards(sources, msgDiv, fullText);

    // Dynamic suggestions
    if (suggestions.length > 0) {
      var sugDiv = document.createElement('div');
      sugDiv.className = 'nakai-chat__suggestions';
      suggestions.forEach(function (text) {
        var btn = document.createElement('button');
        btn.className = 'nakai-chat__suggestion-btn';
        btn.type = 'button';
        btn.innerHTML = '<span>' + escapeHtml(text) + '</span>';
        btn.addEventListener('click', function () {
          var inp = $('nakai-chat-input');
          if (inp) inp.value = text;
          sendMessage();
          sugDiv.remove();
        });
        sugDiv.appendChild(btn);
      });
      msgDiv.appendChild(sugDiv);
    }

    // Timestamp + AI tag
    var now = new Date();
    var ts = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    var metaDiv = document.createElement('div');
    metaDiv.className = 'nakai-chat__message-meta';
    metaDiv.innerHTML = '<span class="nakai-chat__timestamp">' + ts + '</span><span class="nakai-chat__ai-tag">AI</span>';
    msgDiv.appendChild(metaDiv);

    history.push({ role: 'assistant', content: fullText });
    saveHistory();
    scrollToBottom();
    isLoading = false;
    setSendLoading(false);
  }

  // ---- Detect product mentions in text ----
  function detectProductsInText(text) {
    var found = [];
    var lowerText = text.toLowerCase();
    var keys = Object.keys(PRODUCT_MAP);
    for (var i = 0; i < keys.length; i++) {
      if (lowerText.indexOf(keys[i]) > -1) {
        var path = PRODUCT_MAP[keys[i]];
        if (found.indexOf(path) === -1) found.push(path);
      }
    }
    return found;
  }

  // ---- Product Cards ----
  function renderProductCards(sources, parentDiv, textContent) {
    var productPaths = [];
    var seen = {};

    sources.forEach(function (s) {
      if (s.indexOf('/products/') > -1) {
        var path = s.startsWith('http') ? new URL(s).pathname : s;
        if (!seen[path]) { seen[path] = true; productPaths.push(path); }
      }
    });

    if (textContent) {
      var detected = detectProductsInText(textContent);
      detected.forEach(function (path) {
        if (!seen[path]) { seen[path] = true; productPaths.push(path); }
      });
    }

    if (productPaths.length === 0) return;

    var grid = document.createElement('div');
    grid.className = 'nakai-chat__product-grid';
    var viewLabel = PAGE_LANG === 'ja' ? '\u5546\u54c1\u3092\u898b\u308b' : 'View Product';

    productPaths.forEach(function (path) {
      var handle = path.split('/products/')[1];
      if (!handle) return;
      handle = handle.split('?')[0].split('#')[0];

      var card = document.createElement('a');
      card.className = 'nakai-chat__product-card nakai-chat__product-card--loading';
      card.href = SHOP_URL + path;
      card.target = '_blank';
      card.rel = 'noopener';
      card.innerHTML =
        '<div class="nakai-chat__product-card-img"></div>'
        + '<div class="nakai-chat__product-card-body">'
        + '<div class="nakai-chat__product-card-title">Loading...</div>'
        + '<div class="nakai-chat__product-card-price">...</div>'
        + '<div class="nakai-chat__product-card-cta">' + viewLabel + '</div>'
        + '</div>';
      grid.appendChild(card);

      fetchProductCard(handle, card);
    });

    parentDiv.appendChild(grid);
  }

  function fetchProductCard(handle, card) {
    var url = SHOP_URL + '/products/' + handle + '.json';
    fetch(url)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.product) return;
        var p = data.product;
        var imgSrc = p.image ? p.image.src : '';
        var price = p.variants && p.variants[0] ? p.variants[0].price : '';

        card.classList.remove('nakai-chat__product-card--loading');
        var imgEl = card.querySelector('.nakai-chat__product-card-img');
        if (imgEl && imgSrc) {
          var img = document.createElement('img');
          img.src = imgSrc;
          img.alt = p.title;
          img.className = 'nakai-chat__product-card-img';
          img.loading = 'lazy';
          imgEl.replaceWith(img);
        }
        var titleEl = card.querySelector('.nakai-chat__product-card-title');
        if (titleEl) titleEl.textContent = p.title;
        var priceEl = card.querySelector('.nakai-chat__product-card-price');
        if (priceEl && price) priceEl.textContent = '$' + price;
      })
      .catch(function () {
        card.classList.remove('nakai-chat__product-card--loading');
      });
  }

  // ---- Main Send ----
  function sendMessage(overrideMsg) {
    var inp = $('nakai-chat-input');
    var msg = overrideMsg || (inp ? inp.value.trim() : '');
    if (!msg || isLoading) return;
    if (inp) inp.value = '';
    lastUserMessage = msg;
    addUserMessage(msg);
    history.push({ role: 'user', content: msg });
    showTyping();
    isLoading = true;
    setSendLoading(true);

    if (supportsStream) {
      streamMessage(msg);
    } else {
      legacyMessage(msg);
    }
  }

  // ---- SSE Streaming ----
  var streamAbort = null;
  function streamMessage(message) {
    streamAbort = new AbortController();
    var streamTimeout = setTimeout(function () { streamAbort.abort(); }, 90000);
    fetch(API_BASE + '/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        history: history.slice(-MAX_HISTORY),
        language: PAGE_LANG,
        session_id: SESSION_ID,
        source: 'widget'
      }),
      signal: streamAbort.signal
    })
    .then(function (res) {
      if (!res.ok) throw new Error('API error');
      removeTyping();

      var mc = $('nakai-chat-messages');
      var msgDiv = document.createElement('div');
      msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
      var row = document.createElement('div');
      row.className = 'nakai-chat__message-row';
      var avatar = document.createElement('div');
      avatar.className = 'nakai-chat__avatar';
      avatar.innerHTML = STAR_SVG;
      var bubble = document.createElement('div');
      bubble.className = 'nakai-chat__message-content';
      row.appendChild(avatar);
      row.appendChild(bubble);
      msgDiv.appendChild(row);
      mc.appendChild(msgDiv);

      var fullText = '';
      var reader = res.body.getReader();
      var decoder = new TextDecoder();
      var buf = '';

      function read() {
        reader.read().then(function (result) {
          if (result.done) return finish();

          buf += decoder.decode(result.value, { stream: true });
          var lines = buf.split('\n');
          buf = lines.pop();

          lines.forEach(function (line) {
            if (!line.startsWith('data: ')) return;
            try { var ev = JSON.parse(line.slice(6)); } catch (e) { return; }

            if (ev.type === 'text') {
              fullText += ev.content;
              bubble.innerHTML = formatMarkdown(fullText);
              scrollToBottom();
            }
            else if (ev.type === 'done') {
              finishStreamMessage(msgDiv, bubble, fullText, ev.sources, ev.suggestions);
            }
            else if (ev.type === 'error') {
              bubble.innerHTML = getErrorHtml();
              bindRetry(msgDiv);
              isLoading = false;
              setSendLoading(false);
            }
          });

          read();
        }).catch(function () { finish(); });
      }

      function finish() {
        clearTimeout(streamTimeout);
        isLoading = false;
        setSendLoading(false);
        if (!fullText) {
          bubble.innerHTML = getErrorHtml();
          bindRetry(msgDiv);
        }
      }

      read();
    })
    .catch(function () {
      removeTyping();
      addBotError();
      isLoading = false;
      setSendLoading(false);
    });
  }

  // ---- Legacy (non-streaming) fallback ----
  function legacyMessage(message) {
    fetch(API_BASE + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        history: history.slice(-MAX_HISTORY),
        language: PAGE_LANG,
        session_id: SESSION_ID,
        source: 'widget'
      })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('API error');
      return res.json();
    })
    .then(function (data) {
      removeTyping();
      var mc = $('nakai-chat-messages');
      var msgDiv = document.createElement('div');
      msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
      var row = document.createElement('div');
      row.className = 'nakai-chat__message-row';
      row.innerHTML =
        '<div class="nakai-chat__avatar">' + STAR_SVG + '</div>'
        + '<div class="nakai-chat__message-content">' + formatMarkdown(data.response) + '</div>';
      msgDiv.appendChild(row);
      mc.appendChild(msgDiv);
      var bubble = row.querySelector('.nakai-chat__message-content');
      finishStreamMessage(msgDiv, bubble, data.response, data.sources || [], data.suggestions || []);
    })
    .catch(function () {
      removeTyping();
      addBotError();
      isLoading = false;
      setSendLoading(false);
    });
  }

  // ---- History ----
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
          if (msg.role === 'user') {
            addUserMessage(msg.content);
          } else {
            var mc = $('nakai-chat-messages');
            if (!mc) return;
            var div = document.createElement('div');
            div.className = 'nakai-chat__message nakai-chat__message--bot';
            div.innerHTML =
              '<div class="nakai-chat__message-row">'
              + '<div class="nakai-chat__avatar">' + STAR_SVG + '</div>'
              + '<div class="nakai-chat__message-content">' + formatMarkdown(msg.content) + '</div>'
              + '</div>';
            mc.appendChild(div);
          }
        });
        scrollToBottom();
      }
    } catch (e) { /* corrupted */ }
  }

  function bindEvents() {
    var form = $('nakai-chat-form');
    if (form) {
      sendBtn = form.querySelector('.nakai-chat__send');
      form.addEventListener('submit', function (e) { e.preventDefault(); sendMessage(); });
    }

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
.nakai-chat__toggle{height:44px;border-radius:var(--nc-rr);border:none;cursor:pointer;display:flex;align-items:center;gap:0;background:var(--nc-g1);color:rgba(255,255,255,.95);box-shadow:0 2px 12px rgba(61,97,66,.25),0 0 0 0 rgba(61,97,66,0);transition:all .4s var(--nc-e);position:relative;overflow:hidden;padding:0;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat:not(.nakai-chat--open) .nakai-chat__toggle{animation:nakaiGlow 3s ease-in-out infinite}
@keyframes nakaiGlow{0%,100%{box-shadow:0 2px 12px rgba(61,97,66,.25),0 0 0 0 rgba(126,214,126,0)}50%{box-shadow:0 2px 16px rgba(61,97,66,.35),0 0 0 4px rgba(126,214,126,.15)}}
.nakai-chat__toggle:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(61,97,66,.35),0 0 0 4px rgba(126,214,126,.18)}
.nakai-chat__toggle:active{transform:translateY(0) scale(.97);transition-duration:.1s}
.nakai-chat__toggle-body{display:flex;align-items:center;gap:0;padding:0 18px;height:100%;position:relative;z-index:1}
.nakai-chat__toggle-label{font-size:.82rem;font-weight:500;letter-spacing:.16em;text-transform:uppercase}
.nakai-chat__toggle-sep{width:1px;height:14px;background:rgba(255,255,255,.18);flex-shrink:0;margin:0 10px}
.nakai-chat__toggle-ai{font-size:.72rem;font-weight:400;letter-spacing:.1em;color:rgba(255,255,255,.6)}
.nakai-chat__toggle-close{display:none;width:44px;height:44px;align-items:center;justify-content:center}
.nakai-chat__toggle-close svg{width:14px;height:14px;stroke-width:2}
.nakai-chat--open .nakai-chat__toggle-body{display:none}
.nakai-chat--open .nakai-chat__toggle-close{display:flex}
.nakai-chat--open .nakai-chat__toggle{width:44px;padding:0}
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
.nakai-chat__ai-intro{display:flex;align-items:center;justify-content:center;gap:6px;padding:8px 14px;margin:0 0 14px;background:linear-gradient(135deg,rgba(61,97,66,.04),rgba(123,160,109,.04));border:1px solid var(--nc-ln);border-radius:12px;font-size:.88rem;font-weight:400;color:var(--nc-t2);letter-spacing:.02em;line-height:1.4}
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
.nakai-chat__message--bot .nakai-chat__message-content{background:var(--nc-s2);color:var(--nc-tx);border-radius:4px 20px 20px 20px;padding:12px 15px;font-size:1.05rem;font-weight:400;line-height:1.55;letter-spacing:.008em;word-wrap:break-word}
.nakai-chat__message--user .nakai-chat__message-content{background:linear-gradient(145deg,#4A7350,var(--nc-g1));color:rgba(255,255,255,.94);border-radius:20px 20px 4px 20px;padding:12px 15px;font-size:1.05rem;font-weight:400;line-height:1.65;letter-spacing:.008em;word-wrap:break-word;box-shadow:0 2px 12px rgba(61,97,66,.1),inset 0 1px 0 rgba(255,255,255,.06)}
.nakai-chat__message-content a{color:var(--nc-g3);text-decoration:none;font-weight:450;background:linear-gradient(to right,var(--nc-g2),var(--nc-g2)) no-repeat 0 100%/100% 1px;transition:all .3s var(--nc-e);padding-bottom:1px}
.nakai-chat__message-content a:hover{color:var(--nc-g1);background-size:100% 1.5px}
.nakai-chat__message--user .nakai-chat__message-content a{color:rgba(255,255,255,.88);background-image:linear-gradient(to right,rgba(255,255,255,.3),rgba(255,255,255,.3))}
.nakai-chat__message-content strong{font-weight:500}
.nakai-chat__message-content ul{margin:4px 0 2px;padding-left:18px;list-style:none}
.nakai-chat__message-content li{position:relative;padding-left:2px;margin-bottom:1px;line-height:1.5}
.nakai-chat__message-content li::before{content:'';position:absolute;left:-12px;top:.6em;width:4px;height:4px;border-radius:50%;background:var(--nc-g2);opacity:.6}
.nakai-chat__message--user .nakai-chat__message-content li::before{background:rgba(255,255,255,.5)}
.nakai-chat__message-meta{display:flex;align-items:center;gap:6px;margin-top:5px;padding:0 0 0 36px}
.nakai-chat__timestamp{font-size:.9rem;font-weight:350;color:var(--nc-t3);letter-spacing:.06em}
.nakai-chat__ai-tag{font-size:.8rem;font-weight:450;letter-spacing:.1em;text-transform:uppercase;color:var(--nc-g2);opacity:.6}
.nakai-chat__sources{margin-top:.6rem;display:flex;flex-wrap:wrap;gap:.4rem;padding-left:36px}
.nakai-chat__source-link{font-size:.88rem;color:var(--nc-g3);text-decoration:none;font-weight:450;background:linear-gradient(to right,var(--nc-g2),var(--nc-g2)) no-repeat 0 100%/100% 1px;opacity:.8;transition:all .3s var(--nc-e);padding-bottom:1px}
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
.nakai-chat__quick-btn{font-family:'Work Sans',sans-serif;font-size:.92rem;font-weight:400;color:var(--nc-g1);background:var(--nc-s1);border:1px solid var(--nc-ln2);border-radius:var(--nc-rr);padding:7px 14px;cursor:pointer;letter-spacing:.03em;transition:all .35s var(--nc-e);position:relative;overflow:hidden;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__quick-btn::before{content:'';position:absolute;inset:0;background:var(--nc-g1);border-radius:var(--nc-rr);transform:scaleX(0);transform-origin:left;transition:transform .35s var(--nc-e)}
.nakai-chat__quick-btn:hover{border-color:var(--nc-g1);color:rgba(255,255,255,.94);transform:translateY(-1px);box-shadow:0 4px 12px rgba(61,97,66,.12)}
.nakai-chat__quick-btn:hover::before{transform:scaleX(1)}
.nakai-chat__quick-btn span{position:relative;z-index:1}
.nakai-chat__input-area{padding:14px 20px 18px;background:var(--nc-s1);flex-shrink:0;position:relative}
.nakai-chat__input-area::before{content:'';position:absolute;top:0;left:22px;right:22px;height:1px;background:var(--nc-ln)}
.nakai-chat__form{display:flex;align-items:center;gap:8px;background:var(--nc-s0);border:1px solid var(--nc-ln);border-radius:var(--nc-rr);padding:5px 5px 5px 18px;transition:all .4s var(--nc-e)}
.nakai-chat__form:focus-within{border-color:rgba(123,160,109,.35);box-shadow:0 0 0 4px rgba(61,97,66,.04);background:var(--nc-s1)}
.nakai-chat__input{flex:1;border:none;background:transparent;color:var(--nc-tx);font-family:'Work Sans',sans-serif;font-size:1.05rem;font-weight:350;letter-spacing:.015em;outline:none;padding:6px 0}
.nakai-chat__input::placeholder{color:var(--nc-t3);font-weight:300;letter-spacing:.03em}
.nakai-chat__send{width:34px;height:34px;border-radius:var(--nc-rr);border:none;background:linear-gradient(145deg,#4A7350,var(--nc-g1));color:rgba(255,255,255,.88);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .3s var(--nc-e);position:relative;overflow:hidden;box-shadow:inset 0 1px 0 rgba(255,255,255,.08);touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__send::before{content:'';position:absolute;top:-10%;left:-10%;width:50%;height:50%;background:radial-gradient(circle,rgba(255,255,255,.2) 0%,transparent 70%);pointer-events:none}
.nakai-chat__send:hover{transform:scale(1.1);box-shadow:0 2px 8px rgba(61,97,66,.15),inset 0 1px 0 rgba(255,255,255,.08)}
.nakai-chat__send:active{transform:scale(.92)}
.nakai-chat__send:disabled{opacity:.5;cursor:not-allowed}
.nakai-chat__send svg{width:13px;height:13px;margin-left:1px}
.nakai-chat__send--loading svg{display:none}
.nakai-chat__send--loading::after{content:'';width:14px;height:14px;border:2px solid rgba(255,255,255,.25);border-top-color:rgba(255,255,255,.85);border-radius:50%;animation:nakaiSpin .6s linear infinite}
@keyframes nakaiSpin{to{transform:rotate(360deg)}}
.nakai-chat__footer{display:flex;align-items:center;justify-content:center;gap:5px;padding:2px 0 13px;background:var(--nc-s1)}
.nakai-chat__footer svg{width:9px;height:9px;color:var(--nc-t3);opacity:.3}
.nakai-chat__footer span{font-size:.85rem;font-weight:300;color:var(--nc-t3);letter-spacing:.12em;text-transform:uppercase;opacity:.3}
.nakai-chat__product-grid{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding:8px 0 4px 36px;margin-top:8px;scrollbar-width:none}
.nakai-chat__product-grid::-webkit-scrollbar{display:none}
.nakai-chat__product-card{flex:0 0 150px;scroll-snap-align:start;border-radius:14px;background:var(--nc-s1);border:1px solid var(--nc-ln2);overflow:hidden;text-decoration:none;color:var(--nc-tx);transition:all .35s var(--nc-e);display:flex;flex-direction:column}
.nakai-chat__product-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(61,97,66,.1);border-color:rgba(61,97,66,.15)}
.nakai-chat__product-card-img{width:100%;height:90px;object-fit:cover;background:linear-gradient(135deg,var(--nc-s0),rgba(61,97,66,.04))}
.nakai-chat__product-card-body{padding:10px;display:flex;flex-direction:column;gap:4px}
.nakai-chat__product-card-title{font-size:.82rem;font-weight:450;line-height:1.3;color:var(--nc-tx);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.nakai-chat__product-card-price{font-size:.78rem;font-weight:500;color:var(--nc-g1);letter-spacing:.02em}
.nakai-chat__product-card-cta{font-size:.7rem;font-weight:600;color:#fff;background:var(--nc-g1);border-radius:6px;padding:5px 0;text-align:center;margin-top:6px;letter-spacing:.03em;transition:background .2s ease}
.nakai-chat__product-card:hover .nakai-chat__product-card-cta{background:var(--nc-g3)}
.nakai-chat__product-card--loading .nakai-chat__product-card-cta{display:none}
.nakai-chat__product-card--loading .nakai-chat__product-card-img,.nakai-chat__product-card--loading .nakai-chat__product-card-title,.nakai-chat__product-card--loading .nakai-chat__product-card-price{background:linear-gradient(90deg,var(--nc-s0) 25%,var(--nc-ln) 50%,var(--nc-s0) 75%);background-size:200% 100%;animation:nakaiShimmer 1.5s infinite;border-radius:4px;color:transparent}
.nakai-chat__product-card--loading .nakai-chat__product-card-title{height:14px;width:80%}
.nakai-chat__product-card--loading .nakai-chat__product-card-price{height:12px;width:50%}
@keyframes nakaiShimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.nakai-chat__choices{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;padding-left:36px}
.nakai-chat__choice-btn{font-family:'Work Sans',sans-serif;font-size:.92rem;font-weight:500;color:var(--nc-g1);background:var(--nc-s1);border:1.5px solid var(--nc-g1);border-radius:var(--nc-rr);padding:8px 18px;cursor:pointer;letter-spacing:.02em;transition:all .25s var(--nc-e);position:relative;overflow:hidden}
.nakai-chat__choice-btn:hover{background:var(--nc-g1);color:#fff;transform:translateY(-1px);box-shadow:0 4px 14px rgba(61,97,66,.18)}
.nakai-chat__choice-btn--selected{background:var(--nc-g1);color:#fff;border-color:var(--nc-g1)}
.nakai-chat__choice-btn--disabled{opacity:.45;cursor:default;pointer-events:none}
.nakai-chat__choice-btn--disabled.nakai-chat__choice-btn--selected{opacity:1}
.nakai-chat__suggestions{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;padding-left:36px}
.nakai-chat__suggestion-btn{font-family:'Work Sans',sans-serif;font-size:.88rem;font-weight:400;color:var(--nc-g1);background:var(--nc-s1);border:1px solid var(--nc-ln2);border-radius:var(--nc-rr);padding:6px 13px;cursor:pointer;letter-spacing:.03em;transition:all .35s var(--nc-e);position:relative;overflow:hidden;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.nakai-chat__suggestion-btn::before{content:'';position:absolute;inset:0;background:var(--nc-g1);border-radius:var(--nc-rr);transform:scaleX(0);transform-origin:left;transition:transform .35s var(--nc-e)}
.nakai-chat__suggestion-btn:hover{border-color:var(--nc-g1);color:rgba(255,255,255,.94);transform:translateY(-1px);box-shadow:0 4px 12px rgba(61,97,66,.12)}
.nakai-chat__suggestion-btn:hover::before{transform:scaleX(1)}
.nakai-chat__suggestion-btn span{position:relative;z-index:1}
.nakai-chat__error-content{display:flex;flex-direction:column;gap:8px}
.nakai-chat__retry-btn{font-family:'Work Sans',sans-serif;font-size:.82rem;font-weight:450;color:var(--nc-g1);background:transparent;border:1px solid var(--nc-ln2);border-radius:var(--nc-rr);padding:5px 12px;cursor:pointer;align-self:flex-start;transition:all .3s var(--nc-e);touch-action:manipulation}
.nakai-chat__retry-btn:hover{background:var(--nc-g1);color:#fff;border-color:var(--nc-g1)}
[data-scheme="dark"] .nakai-chat{--nc-bg:#0C0E0C;--nc-s0:#131513;--nc-s1:#181B18;--nc-s2:rgba(123,160,109,.04);--nc-tx:#E4E5E0;--nc-t2:#7D807A;--nc-t3:#4E514A;--nc-ln:rgba(255,255,255,.04);--nc-ln2:rgba(255,255,255,.07);--nc-sh:0 0 0 .5px rgba(255,255,255,.03),0 24px 80px -16px rgba(0,0,0,.7);--nc-sh2:0 1px 4px rgba(0,0,0,.3)}
[data-scheme="dark"] .nakai-chat__toggle{background:var(--nc-g2);color:#0C0E0C;box-shadow:0 2px 12px rgba(123,160,109,.3),0 0 0 0 rgba(123,160,109,0)}
[data-scheme="dark"] .nakai-chat__toggle-ai{color:rgba(12,14,12,.5)}
[data-scheme="dark"] .nakai-chat__toggle-sep{background:rgba(0,0,0,.12)}
[data-scheme="dark"] .nakai-chat__header{background:linear-gradient(180deg,#1C201C,#151815);box-shadow:0 1px 0 rgba(255,255,255,.03)}
[data-scheme="dark"] .nakai-chat__header::before{background:rgba(255,255,255,.04)}
[data-scheme="dark"] .nakai-chat__ai-badge{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.05)}
[data-scheme="dark"] .nakai-chat__ai-intro{background:linear-gradient(135deg,rgba(123,160,109,.06),rgba(123,160,109,.03));border-color:var(--nc-ln)}
[data-scheme="dark"] .nakai-chat__avatar{background:linear-gradient(145deg,rgba(123,160,109,.1),rgba(123,160,109,.05));border-color:var(--nc-ln)}
[data-scheme="dark"] .nakai-chat__avatar svg{color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__message--user .nakai-chat__message-content{background:linear-gradient(145deg,#8FB87C,var(--nc-g2));color:#0C0E0C;box-shadow:0 2px 12px rgba(123,160,109,.08),inset 0 1px 0 rgba(255,255,255,.1)}
[data-scheme="dark"] .nakai-chat__send{background:linear-gradient(145deg,#8FB87C,var(--nc-g2));color:#0C0E0C}
[data-scheme="dark"] .nakai-chat__send--loading::after{border-color:rgba(12,14,12,.25);border-top-color:rgba(12,14,12,.85)}
[data-scheme="dark"] .nakai-chat__quick-btn{color:var(--nc-g2);border-color:rgba(123,160,109,.15)}
[data-scheme="dark"] .nakai-chat__quick-btn::before{background:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__quick-btn:hover{color:#0C0E0C;border-color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__choice-btn{color:var(--nc-g2);border-color:var(--nc-g2);background:transparent}
[data-scheme="dark"] .nakai-chat__choice-btn:hover,[data-scheme="dark"] .nakai-chat__choice-btn--selected{background:var(--nc-g2);color:#0C0E0C}
[data-scheme="dark"] .nakai-chat__suggestion-btn{color:var(--nc-g2);border-color:rgba(123,160,109,.15)}
[data-scheme="dark"] .nakai-chat__suggestion-btn::before{background:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__suggestion-btn:hover{color:#0C0E0C;border-color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__retry-btn{color:var(--nc-g2);border-color:rgba(123,160,109,.15)}
[data-scheme="dark"] .nakai-chat__retry-btn:hover{background:var(--nc-g2);color:#0C0E0C;border-color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__message-content a{color:var(--nc-g2);background-image:linear-gradient(to right,rgba(123,160,109,.35),rgba(123,160,109,.35))}
[data-scheme="dark"] .nakai-chat__source-link{color:var(--nc-g2);background-image:linear-gradient(to right,rgba(123,160,109,.35),rgba(123,160,109,.35))}
[data-scheme="dark"] .nakai-chat__message-content li::before{background:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__product-card{background:var(--nc-s0);border-color:var(--nc-ln2)}
[data-scheme="dark"] .nakai-chat__product-card:hover{box-shadow:0 6px 20px rgba(0,0,0,.3);border-color:rgba(123,160,109,.2)}
[data-scheme="dark"] .nakai-chat__product-card-price{color:var(--nc-g2)}
[data-scheme="dark"] .nakai-chat__product-card-cta{background:var(--nc-g2);color:#1a1a1a}
[data-scheme="dark"] .nakai-chat__header-dot{background:#7ED67E;box-shadow:0 0 8px rgba(126,214,126,.3)}
@media(prefers-reduced-motion:reduce){.nakai-chat__toggle,.nakai-chat__panel,.nakai-chat__message,.nakai-chat__quick-btn,.nakai-chat__quick-btn::before,.nakai-chat__suggestion-btn,.nakai-chat__suggestion-btn::before,.nakai-chat__send,.nakai-chat__retry-btn,.nakai-chat__product-card,.nakai-chat__form,.nakai-chat__header-close,.nakai-chat__message-content a,.nakai-chat__source-link{transition:none!important;animation:none!important}.nakai-chat__toggle-dot,.nakai-chat__header-dot,.nakai-chat__typing span{animation:none!important}.nakai-chat__typing span{opacity:.5}.nakai-chat:not(.nakai-chat--open) .nakai-chat__toggle{animation:none!important}.nakai-chat__messages{scroll-behavior:auto}}
@media screen and (max-width:749px){
  .nakai-chat{bottom:20px;right:16px}
  .nakai-chat__toggle-label{font-size:.78rem;letter-spacing:.14em}
  .nakai-chat__panel{position:fixed;top:0;left:0;right:0;bottom:0;width:100%;height:100%;max-height:-webkit-fill-available;border-radius:0;border:none;transform:translateY(100%);opacity:1}
  .nakai-chat--open .nakai-chat__panel{transform:translateY(0)}
  .nakai-chat--open .nakai-chat__toggle{display:none}
  .nakai-chat__messages{padding:16px}
  .nakai-chat__message--bot .nakai-chat__message-content,.nakai-chat__message--user .nakai-chat__message-content{font-size:1.05rem;line-height:1.55;padding:10px 14px}
  .nakai-chat__ai-intro{font-size:.85rem;padding:6px 10px;margin:0 0 10px}
  .nakai-chat__quick-actions{padding-left:36px;gap:5px}
  .nakai-chat__quick-btn{font-size:.88rem;padding:6px 12px}
  .nakai-chat__input-area{padding:10px 14px 14px}
  .nakai-chat__input{font-size:16px}
  .nakai-chat__header{padding:14px 16px}
  .nakai-chat__header-close{width:32px;height:32px}
  .nakai-chat__header-close svg{width:14px;height:14px}
  .nakai-chat__footer{padding:2px 0 max(10px,env(safe-area-inset-bottom))}
  .nakai-chat__product-grid{padding-left:36px;gap:8px}
  .nakai-chat__product-card{flex:0 0 135px}
  .nakai-chat__product-card-img{height:75px}
  .nakai-chat__suggestions{padding-left:36px;gap:5px}
  .nakai-chat__suggestion-btn{font-size:.84rem;padding:5px 11px}
}
.template-page-chat .nakai-chat{display:none}
`;

  // ---- Boot ----
  function boot() {
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
