(function () {
  'use strict';

  // ---- Configuration ----
  var CHAT_API_URL = 'https://nakai-matcha-chat.onrender.com/api';
  var SHOP_URL = 'https://nakaimatcha.com';
  var MAX_HISTORY = 20;
  var AI_STAR_SVG = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>';

  // ---- Known product name → handle mapping ----
  var PRODUCT_MAP = {
    'revi': '/products/revi-organic-matcha-20g-ss-grade-plus',
    'ikigai': '/products/ikigai-organic-matcha-40g-ss-grade',
    'exquisite matcha set': '/products/the-exquisite-matcha-set',
    'エクスキジット抹茶セット': '/products/the-exquisite-matcha-set',
    '抹茶セット': '/products/the-exquisite-matcha-set'
  };

  // ---- Session ID ----
  function getSessionId() {
    var key = 'nakai_session_id';
    var id = sessionStorage.getItem(key);
    if (!id) {
      id = typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : 'w-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem(key, id);
    }
    return id;
  }

  // ---- Streaming support check ----
  var supportsStream = typeof ReadableStream !== 'undefined'
    && typeof TextDecoder !== 'undefined'
    && typeof Response !== 'undefined'
    && typeof Response.prototype === 'object';

  // ---- Chat Widget Class ----
  function NakaiChat(opts) {
    this.containerId = opts.containerId || 'nakai-chat-widget';
    this.messagesId = opts.messagesId || 'nakai-chat-messages';
    this.formId = opts.formId || 'nakai-chat-form';
    this.inputId = opts.inputId || 'nakai-chat-input';
    this.isFullPage = opts.isFullPage || false;

    this.widget = document.getElementById(this.containerId);
    if (!this.widget) return;

    this.messagesContainer = document.getElementById(this.messagesId);
    this.form = document.getElementById(this.formId);
    this.input = document.getElementById(this.inputId);
    this.sendBtn = this.form ? this.form.querySelector('.nakai-chat__send') : null;

    this.history = [];
    this.isOpen = false;
    this.isLoading = false;
    this.language = this.widget.dataset.lang || 'en';
    this.sessionId = getSessionId();
    this.lastUserMessage = '';

    this.bindEvents();
    this.loadHistory();
  }

  NakaiChat.prototype.bindEvents = function () {
    var self = this;

    if (this.form) {
      this.form.addEventListener('submit', function (e) {
        e.preventDefault();
        self.sendMessage();
      });
    }

    // Quick action buttons
    this.widget.querySelectorAll('.nakai-chat__quick-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var msg = this.getAttribute('data-message') || this.textContent.trim();
        if (self.input) {
          self.input.value = msg;
          self.sendMessage();
        }
        var qa = this.closest('.nakai-chat__quick-actions');
        if (qa) qa.style.display = 'none';
      });
    });

    // Floating widget (toggle, close, ESC)
    if (!this.isFullPage) {
      var toggle = document.getElementById('nakai-chat-toggle');
      var closeBtn = document.getElementById('nakai-chat-close');

      if (toggle) {
        toggle.addEventListener('click', function () {
          self.isOpen ? self.closeChat() : self.openChat();
        });
      }
      if (closeBtn) {
        closeBtn.addEventListener('click', function () {
          self.closeChat();
        });
      }
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && self.isOpen) self.closeChat();
      });
    }
  };

  NakaiChat.prototype.openChat = function () {
    this.isOpen = true;
    this.widget.classList.add('nakai-chat--open');
    var panel = document.getElementById('nakai-chat-panel');
    if (panel) panel.setAttribute('aria-hidden', 'false');
    var toggle = document.getElementById('nakai-chat-toggle');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
    if (this.input && window.innerWidth > 749) {
      this.input.focus();
    }
  };

  NakaiChat.prototype.closeChat = function () {
    this.isOpen = false;
    this.widget.classList.remove('nakai-chat--open');
    var panel = document.getElementById('nakai-chat-panel');
    if (panel) panel.setAttribute('aria-hidden', 'true');
    var toggle = document.getElementById('nakai-chat-toggle');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  };

  // ---- Send Button Loading State ----
  NakaiChat.prototype.setSendLoading = function (on) {
    if (!this.sendBtn) return;
    if (on) {
      this.sendBtn.classList.add('nakai-chat__send--loading');
      this.sendBtn.disabled = true;
    } else {
      this.sendBtn.classList.remove('nakai-chat__send--loading');
      this.sendBtn.disabled = false;
    }
  };

  // ---- Error HTML with Retry ----
  NakaiChat.prototype.getErrorHtml = function () {
    var msg = this.language === 'ja'
      ? '接続に問題が発生しました。'
      : 'Sorry, I\'m having trouble connecting right now.';
    var retryLabel = this.language === 'ja' ? '再試行' : 'Retry';
    return '<div class="nakai-chat__error-content">'
      + '<span>' + msg + '</span>'
      + '<button class="nakai-chat__retry-btn" type="button">' + retryLabel + '</button>'
      + '</div>';
  };

  // ---- Main Send — SSE Streaming ----
  NakaiChat.prototype.sendMessage = function (overrideMsg) {
    var message = overrideMsg || (this.input ? this.input.value.trim() : '');
    if (!message || this.isLoading) return;

    if (this.input) this.input.value = '';
    this.lastUserMessage = message;
    this.addUserMessage(message);
    this.history.push({ role: 'user', content: message });
    this.showTyping();
    this.isLoading = true;
    this.setSendLoading(true);

    // Mock mode for local preview
    if (window.__NAKAI_MOCK) {
      this.mockStream(message);
      return;
    }

    var self = this;
    var useStream = supportsStream;

    if (useStream) {
      this.streamMessage(message);
    } else {
      this.legacyMessage(message);
    }
  };

  // ---- SSE Streaming via ReadableStream ----
  NakaiChat.prototype.streamMessage = function (message) {
    var self = this;

    fetch(CHAT_API_URL + '/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        history: this.history.slice(-MAX_HISTORY),
        language: this.language,
        session_id: this.sessionId,
        source: 'widget'
      })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('API error');
      self.removeTyping();

      // Create empty bot bubble
      var msgDiv = document.createElement('div');
      msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
      var row = document.createElement('div');
      row.className = 'nakai-chat__message-row';
      var avatar = document.createElement('div');
      avatar.className = 'nakai-chat__avatar';
      avatar.innerHTML = AI_STAR_SVG;
      var bubble = document.createElement('div');
      bubble.className = 'nakai-chat__message-content';
      row.appendChild(avatar);
      row.appendChild(bubble);
      msgDiv.appendChild(row);
      self.messagesContainer.appendChild(msgDiv);

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
              bubble.innerHTML = self.formatMarkdown(fullText);
              self.scrollToBottom();
            }
            else if (ev.type === 'done') {
              self.finishStreamMessage(msgDiv, bubble, fullText, ev.sources, ev.suggestions);
            }
            else if (ev.type === 'error') {
              bubble.innerHTML = self.getErrorHtml();
              self.bindRetry(msgDiv);
            }
          });

          read();
        }).catch(function () { finish(); });
      }

      function finish() {
        self.isLoading = false;
        self.setSendLoading(false);
        if (!fullText) {
          bubble.innerHTML = self.getErrorHtml();
          self.bindRetry(msgDiv);
        }
      }

      read();
    })
    .catch(function () {
      self.removeTyping();
      self.addBotError();
      self.isLoading = false;
      self.setSendLoading(false);
    });
  };

  // ---- Finish stream: sources, suggestions, timestamp ----
  NakaiChat.prototype.finishStreamMessage = function (msgDiv, bubble, fullText, sources, suggestions) {
    sources = sources || [];
    suggestions = suggestions || [];

    // Strip [SUGGESTIONS] block from visible text (handles **[SUGGESTIONS]** too)
    var sugM = fullText.match(/\*{0,2}\[SUGGESTIONS\]\*{0,2}/);
    if (sugM) {
      fullText = fullText.substring(0, sugM.index).trim();
    }

    // Strip [CHOICES] block from visible text and extract options (handles **[CHOICES]** too)
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
    var prodResult = this.extractProducts(fullText);
    fullText = prodResult.text;
    bubble.innerHTML = this.formatMarkdown(fullText);

    // Product carousel
    if (prodResult.handles.length > 0) {
      this.fetchAndRenderProducts(prodResult.handles, msgDiv);
    }

    // Choice buttons (Matcha Finder interactive options)
    if (choices.length > 0) {
      var choiceDiv = document.createElement('div');
      choiceDiv.className = 'nakai-chat__choices';
      var self2 = this;
      choices.forEach(function (text) {
        var btn = document.createElement('button');
        btn.className = 'nakai-chat__choice-btn';
        btn.type = 'button';
        btn.textContent = text;
        btn.addEventListener('click', function () {
          self2.sendMessage(text);
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
        var label = s.indexOf('/products/') > -1
          ? (this.language === 'ja' ? '商品を見る' : 'View product')
          : s.indexOf('/blogs/') > -1
            ? (this.language === 'ja' ? '記事を読む' : 'Read article')
            : (this.language === 'ja' ? '詳細' : 'Learn more');
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
    this.renderProductCards(sources, msgDiv, fullText);

    // Dynamic suggestions
    if (suggestions.length > 0) {
      var sugDiv = document.createElement('div');
      sugDiv.className = 'nakai-chat__suggestions';
      var self = this;
      suggestions.forEach(function (text) {
        var btn = document.createElement('button');
        btn.className = 'nakai-chat__suggestion-btn';
        btn.type = 'button';
        btn.innerHTML = '<span>' + self.escapeHtml(text) + '</span>';
        btn.addEventListener('click', function () {
          self.input.value = text;
          self.sendMessage();
          sugDiv.remove();
        });
        sugDiv.appendChild(btn);
      });
      msgDiv.appendChild(sugDiv);
    }

    // Timestamp + AI tag
    var now = new Date();
    var timeStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    var metaDiv = document.createElement('div');
    metaDiv.className = 'nakai-chat__message-meta';
    metaDiv.innerHTML =
      '<span class="nakai-chat__timestamp">' + timeStr + '</span>' +
      '<span class="nakai-chat__ai-tag">AI</span>';
    msgDiv.appendChild(metaDiv);

    this.history.push({ role: 'assistant', content: fullText });
    this.saveHistory();
    this.scrollToBottom();
    this.isLoading = false;
    this.setSendLoading(false);
  };

  // ---- Detect product mentions in text ----
  NakaiChat.prototype.detectProductsInText = function (text) {
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
  };

  // ---- Product Cards ----
  NakaiChat.prototype.renderProductCards = function (sources, parentDiv, textContent) {
    // Combine product URLs from sources + text mentions (deduplicated)
    var productPaths = [];
    var seen = {};

    // From RAG sources
    sources.forEach(function (s) {
      if (s.indexOf('/products/') > -1) {
        var path = s.startsWith('http') ? new URL(s).pathname : s;
        if (!seen[path]) { seen[path] = true; productPaths.push(path); }
      }
    });

    // From text mentions
    if (textContent) {
      var detected = this.detectProductsInText(textContent);
      detected.forEach(function (path) {
        if (!seen[path]) { seen[path] = true; productPaths.push(path); }
      });
    }

    if (productPaths.length === 0) return;

    var grid = document.createElement('div');
    grid.className = 'nakai-chat__product-grid';
    var self = this;
    var viewLabel = this.language === 'ja' ? '商品を見る' : 'View Product';

    productPaths.forEach(function (path) {
      var handle = path.split('/products/')[1];
      if (!handle) return;
      handle = handle.split('?')[0].split('#')[0];

      // Create placeholder card with shimmer
      var card = document.createElement('a');
      card.className = 'nakai-chat__product-card nakai-chat__product-card--loading';
      card.href = SHOP_URL + path;
      card.target = '_blank';
      card.rel = 'noopener';
      card.innerHTML =
        '<div class="nakai-chat__product-card-img"></div>' +
        '<div class="nakai-chat__product-card-body">' +
        '<div class="nakai-chat__product-card-title">Loading...</div>' +
        '<div class="nakai-chat__product-card-price">...</div>' +
        '<div class="nakai-chat__product-card-cta">' + viewLabel + '</div>' +
        '</div>';
      grid.appendChild(card);

      // Fetch product data
      self.fetchProductCard(handle, card);
    });

    parentDiv.appendChild(grid);
  };

  NakaiChat.prototype.fetchProductCard = function (handle, card) {
    var url = SHOP_URL + '/products/' + handle + '.json';
    fetch(url)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.product) return;
        var p = data.product;
        var imgSrc = p.image ? p.image.src : '';
        var price = p.variants && p.variants[0] ? p.variants[0].price : '';
        var currency = '$';

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
        if (priceEl && price) priceEl.textContent = currency + price;
      })
      .catch(function () {
        card.classList.remove('nakai-chat__product-card--loading');
      });
  };

  // ---- Extract [PRODUCT:handle] tags ----
  NakaiChat.prototype.extractProducts = function (text) {
    var re = /\[PRODUCT:([a-z0-9-]+)\]/gi; var handles = []; var m;
    while ((m = re.exec(text)) !== null) handles.push(m[1]);
    var cleaned = text.replace(/\[PRODUCT:[a-z0-9-]+\]/gi, '').trim();
    return { handles: handles, text: cleaned };
  };

  NakaiChat.prototype.fetchAndRenderProducts = function (handles, parentEl) {
    if (!handles.length) return;
    var self = this;
    var grid = document.createElement('div');
    grid.className = 'nakai-chat__product-grid';
    var lang = document.documentElement.lang || 'en';
    handles.forEach(function (handle) {
      var card = document.createElement('a');
      card.className = 'nakai-chat__product-card nakai-chat__product-card--loading';
      card.href = SHOP_URL + '/products/' + handle;
      card.target = '_blank'; card.rel = 'noopener';
      card.innerHTML = '<div class="nakai-chat__product-card-img"></div>'
        + '<div class="nakai-chat__product-card-body">'
        + '<div class="nakai-chat__product-card-title" style="height:2.6em;background:rgba(61,97,66,.04);border-radius:4px"></div>'
        + '</div>';
      grid.appendChild(card);
      self.fetchProductCard(handle, card);
    });
    parentEl.appendChild(grid);
    self.scrollToBottom();
  };

  // ---- Retry Binding ----
  NakaiChat.prototype.bindRetry = function (msgDiv) {
    var self = this;
    var btn = msgDiv.querySelector('.nakai-chat__retry-btn');
    if (btn) {
      btn.addEventListener('click', function () {
        msgDiv.remove();
        self.isLoading = false;
        self.setSendLoading(false);
        self.sendMessage(self.lastUserMessage);
      });
    }
  };

  // ---- Legacy (non-streaming) fallback ----
  NakaiChat.prototype.legacyMessage = function (message) {
    var self = this;
    fetch(CHAT_API_URL + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        history: this.history.slice(-MAX_HISTORY),
        language: this.language,
        session_id: this.sessionId,
        source: 'widget'
      })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('API error');
      return res.json();
    })
    .then(function (data) {
      self.removeTyping();
      self.addBotMessage(data.response, data.sources || [], data.suggestions || []);
      self.history.push({ role: 'assistant', content: data.response });
      self.saveHistory();
    })
    .catch(function () {
      self.removeTyping();
      self.addBotError();
    })
    .finally(function () {
      self.isLoading = false;
      self.setSendLoading(false);
    });
  };

  // ---- Mock Streaming for Preview ----
  NakaiChat.prototype.mockStream = function (message) {
    var self = this;
    var mockResponse = this.language === 'ja'
      ? 'NAKAI の抹茶は京都・宇治から直接仕入れています。石臼で丁寧に挽いた超微粉末で、鮮やかな緑色と豊かなうまみが特徴です。\n\n- **Revi オーガニック抹茶**: 日常使いに最適\n- **Ikigai オーガニック抹茶**: プレミアムグレード\n- **エクスキジット抹茶セット**: 限定ギフトセット'
      : 'NAKAI matcha is sourced directly from Uji, Kyoto. Our matcha is stone-ground using traditional techniques, producing an ultra-fine powder with vibrant green color and rich umami flavor.\n\n- **Revi Organic Matcha**: Perfect for daily use\n- **Ikigai Organic Matcha**: Premium ceremonial grade\n- **The Exquisite Matcha Set**: Limited edition gift set';

    var mockSources = ['/products/revi-organic-matcha-20g-ss-grade-plus', '/products/ikigai-organic-matcha-40g-ss-grade'];
    var mockSuggestions = this.language === 'ja'
      ? ['淹れ方のコツ', '配送について', '茶道とは？']
      : ['Brewing tips', 'Shipping info', 'What is tea ceremony?'];

    setTimeout(function () {
      self.removeTyping();

      var msgDiv = document.createElement('div');
      msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
      var row = document.createElement('div');
      row.className = 'nakai-chat__message-row';
      var avatar = document.createElement('div');
      avatar.className = 'nakai-chat__avatar';
      avatar.innerHTML = AI_STAR_SVG;
      var bubble = document.createElement('div');
      bubble.className = 'nakai-chat__message-content';
      row.appendChild(avatar);
      row.appendChild(bubble);
      msgDiv.appendChild(row);
      self.messagesContainer.appendChild(msgDiv);

      // Simulate token-by-token streaming
      var fullText = '';
      var chars = mockResponse.split('');
      var idx = 0;

      function tick() {
        if (idx >= chars.length) {
          self.finishStreamMessage(msgDiv, bubble, fullText, mockSources, mockSuggestions);
          return;
        }
        // Send ~3 chars per tick for speed
        var chunk = chars.slice(idx, idx + 3).join('');
        idx += 3;
        fullText += chunk;
        bubble.innerHTML = self.formatMarkdown(fullText);
        self.scrollToBottom();
        setTimeout(tick, 25);
      }

      tick();
    }, 600);
  };

  // ---- Message Helpers ----
  NakaiChat.prototype.addUserMessage = function (content) {
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--user';
    div.innerHTML = '<div class="nakai-chat__message-content">' + this.escapeHtml(content) + '</div>';
    this.messagesContainer.appendChild(div);
    this.scrollToBottom();
  };

  NakaiChat.prototype.addBotMessage = function (content, sources, suggestions) {
    sources = sources || [];
    suggestions = suggestions || [];

    var msgDiv = document.createElement('div');
    msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';

    var row = document.createElement('div');
    row.className = 'nakai-chat__message-row';
    row.innerHTML =
      '<div class="nakai-chat__avatar">' + AI_STAR_SVG + '</div>' +
      '<div class="nakai-chat__message-content">' + this.formatMarkdown(content) + '</div>';
    msgDiv.appendChild(row);

    var bubble = row.querySelector('.nakai-chat__message-content');
    this.messagesContainer.appendChild(msgDiv);
    this.finishStreamMessage(msgDiv, bubble, content, sources, suggestions);
  };

  NakaiChat.prototype.addBotError = function () {
    var msgDiv = document.createElement('div');
    msgDiv.className = 'nakai-chat__message nakai-chat__message--bot';
    var row = document.createElement('div');
    row.className = 'nakai-chat__message-row';
    row.innerHTML =
      '<div class="nakai-chat__avatar">' + AI_STAR_SVG + '</div>' +
      '<div class="nakai-chat__message-content">' + this.getErrorHtml() + '</div>';
    msgDiv.appendChild(row);
    this.messagesContainer.appendChild(msgDiv);
    this.bindRetry(msgDiv);
    this.scrollToBottom();
  };

  NakaiChat.prototype.showTyping = function () {
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--bot nakai-chat__typing-wrapper';

    var typingLabel = this.language === 'ja' ? 'AIが回答を作成中...' : 'AI is composing...';

    div.innerHTML =
      '<div class="nakai-chat__message-row">' +
      '<div class="nakai-chat__avatar">' + AI_STAR_SVG + '</div>' +
      '<div class="nakai-chat__typing-body">' +
      '<div class="nakai-chat__message-content nakai-chat__typing">' +
      '<span></span><span></span><span></span></div>' +
      '<span class="nakai-chat__typing-label">' + typingLabel + '</span>' +
      '</div></div>';
    this.messagesContainer.appendChild(div);
    this.scrollToBottom();
  };

  NakaiChat.prototype.removeTyping = function () {
    var typing = this.messagesContainer.querySelector('.nakai-chat__typing-wrapper');
    if (typing) typing.remove();
  };

  NakaiChat.prototype.scrollToBottom = function () {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  };

  // ---- Markdown — improved with lists, strips headers/rules ----
  NakaiChat.prototype.formatMarkdown = function (text) {
    if (!text) return '';
    return text
      // Convert markdown headers to bold (fallback if model outputs them)
      .replace(/^#{1,6}\s+(.*?)$/gm, '<strong>$1</strong>')
      // Strip horizontal rules (---, ***, ___)
      .replace(/^\s*-{3,}\s*$/gm, '')
      .replace(/^\s*\*{3,}\s*$/gm, '')
      .replace(/^\s*_{3,}\s*$/gm, '')
      // Strip table rows
      .replace(/^\|.*\|$/gm, '')
      // Bold (inline)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Relative links
      .replace(/\[(.*?)\]\(\/(.*?)\)/g, '<a href="' + SHOP_URL + '/$2" target="_blank" rel="noopener">$1</a>')
      // External links
      .replace(/\[(.*?)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      // Convert all bullet styles (*, +, -) and numbered lists to <li>
      .replace(/^\s*[*+-]\s+(.*?)$/gm, '<li>$1</li>')
      .replace(/^\d+\.\s+(.*?)$/gm, '<li>$1</li>')
      // Wrap consecutive <li> in <ul>
      .replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>')
      // Strip tab indentation
      .replace(/^\t+/gm, '')
      // Collapse all newlines to spaces (compact flow)
      .replace(/\n{2,}/g, ' ')
      .replace(/\n/g, ' ')
      .replace(/ {2,}/g, ' ')
      // Safety: collapse any stray br tags
      .replace(/(<br>){2,}/g, '<br>')
      .replace(/^(<br>| )+/, '')
      .replace(/(<br>| )+$/, '');
  };

  NakaiChat.prototype.escapeHtml = function (text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  };

  // ---- History ----
  NakaiChat.prototype.saveHistory = function () {
    try {
      sessionStorage.setItem(
        'nakai_chat_history',
        JSON.stringify(this.history.slice(-MAX_HISTORY))
      );
    } catch (e) { /* storage full */ }
  };

  NakaiChat.prototype.loadHistory = function () {
    try {
      var stored = sessionStorage.getItem('nakai_chat_history');
      if (stored) {
        this.history = JSON.parse(stored);
        var self = this;
        this.history.forEach(function (msg) {
          if (msg.role === 'user') {
            self.addUserMessage(msg.content);
          } else {
            // For restored messages, use simple rendering (no sources/suggestions)
            var div = document.createElement('div');
            div.className = 'nakai-chat__message nakai-chat__message--bot';
            div.innerHTML =
              '<div class="nakai-chat__message-row">' +
              '<div class="nakai-chat__avatar">' + AI_STAR_SVG + '</div>' +
              '<div class="nakai-chat__message-content">' + self.formatMarkdown(msg.content) + '</div>' +
              '</div>';
            self.messagesContainer.appendChild(div);
          }
        });
        this.scrollToBottom();
      }
    } catch (e) { /* corrupted */ }
  };

  // ---- Initialize ----
  function init() {
    if (document.getElementById('nakai-chat-widget')) {
      new NakaiChat({
        containerId: 'nakai-chat-widget',
        messagesId: 'nakai-chat-messages',
        formId: 'nakai-chat-form',
        inputId: 'nakai-chat-input',
        isFullPage: false
      });
    }

    if (document.getElementById('nakai-chatpage-container')) {
      new NakaiChat({
        containerId: 'nakai-chatpage-container',
        messagesId: 'nakai-chatpage-messages',
        formId: 'nakai-chatpage-form',
        inputId: 'nakai-chatpage-input',
        isFullPage: true
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
