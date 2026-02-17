(function () {
  'use strict';

  // ---- Configuration ----
  var CHAT_API_URL = 'https://nakai-matcha-chat.onrender.com/api';
  var MAX_HISTORY = 20;
  var AI_STAR_SVG = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l1.545 4.755h5.005l-4.047 2.94 1.545 4.755L8 10.51l-4.048 2.94 1.545-4.755L1.45 5.755h5.005L8 1z"/></svg>';

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

    this.history = [];
    this.isOpen = false;
    this.isLoading = false;
    this.language = this.widget.dataset.lang || 'en';

    this.bindEvents();
    this.loadHistory();
  }

  NakaiChat.prototype.bindEvents = function () {
    var self = this;

    // Form submission
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
        // Hide quick actions after click
        var qa = this.closest('.nakai-chat__quick-actions');
        if (qa) qa.style.display = 'none';
      });
    });

    // Floating widget specific (toggle, close, ESC)
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
    if (this.input) this.input.focus();
  };

  NakaiChat.prototype.closeChat = function () {
    this.isOpen = false;
    this.widget.classList.remove('nakai-chat--open');
    var panel = document.getElementById('nakai-chat-panel');
    if (panel) panel.setAttribute('aria-hidden', 'true');
    var toggle = document.getElementById('nakai-chat-toggle');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  };

  NakaiChat.prototype.sendMessage = function () {
    var message = this.input ? this.input.value.trim() : '';
    if (!message || this.isLoading) return;

    this.input.value = '';
    this.addMessage('user', message);
    this.history.push({ role: 'user', content: message });
    this.showTyping();
    this.isLoading = true;

    var self = this;
    fetch(CHAT_API_URL + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        history: this.history.slice(-MAX_HISTORY),
        language: this.language,
      }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('API error');
        return res.json();
      })
      .then(function (data) {
        self.removeTyping();
        self.addMessage('bot', data.response, data.sources || []);
        self.history.push({ role: 'assistant', content: data.response });
        self.saveHistory();
      })
      .catch(function () {
        self.removeTyping();
        self.addMessage(
          'bot',
          'Sorry, I\'m having trouble connecting right now. Please try again or visit our <a href="/pages/contact">Contact page</a>.'
        );
      })
      .finally(function () {
        self.isLoading = false;
      });
  };

  NakaiChat.prototype.addMessage = function (role, content, sources) {
    sources = sources || [];
    var div = document.createElement('div');
    div.className = 'nakai-chat__message nakai-chat__message--' + role;

    var contentHtml = role === 'bot' ? this.formatMarkdown(content) : this.escapeHtml(content);

    if (role === 'bot') {
      // Bot message with avatar row
      var html =
        '<div class="nakai-chat__message-row">' +
        '<div class="nakai-chat__avatar">' + AI_STAR_SVG + '</div>' +
        '<div class="nakai-chat__message-content">' + contentHtml + '</div>' +
        '</div>';

      // Sources
      if (sources.length > 0) {
        html += '<div class="nakai-chat__sources">';
        for (var i = 0; i < sources.length; i++) {
          html +=
            '<a href="' +
            this.escapeHtml(sources[i]) +
            '" class="nakai-chat__source-link">View product</a>';
        }
        html += '</div>';
      }

      // Meta row with timestamp + AI tag
      var now = new Date();
      var timeStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
      html += '<div class="nakai-chat__message-meta">' +
        '<span class="nakai-chat__timestamp">' + timeStr + '</span>' +
        '<span class="nakai-chat__ai-tag">AI</span>' +
        '</div>';

      div.innerHTML = html;
    } else {
      // User message (no avatar)
      div.innerHTML = '<div class="nakai-chat__message-content">' + contentHtml + '</div>';
    }

    this.messagesContainer.appendChild(div);
    this.scrollToBottom();
  };

  NakaiChat.prototype.showTyping = function () {
    var div = document.createElement('div');
    div.className =
      'nakai-chat__message nakai-chat__message--bot nakai-chat__typing-wrapper';

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
    var typing = this.messagesContainer.querySelector(
      '.nakai-chat__typing-wrapper'
    );
    if (typing) typing.remove();
  };

  NakaiChat.prototype.scrollToBottom = function () {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  };

  NakaiChat.prototype.formatMarkdown = function (text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
      .replace(/\n/g, '<br>');
  };

  NakaiChat.prototype.escapeHtml = function (text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  };

  NakaiChat.prototype.saveHistory = function () {
    try {
      sessionStorage.setItem(
        'nakai_chat_history',
        JSON.stringify(this.history.slice(-MAX_HISTORY))
      );
    } catch (e) {
      /* storage full */
    }
  };

  NakaiChat.prototype.loadHistory = function () {
    try {
      var stored = sessionStorage.getItem('nakai_chat_history');
      if (stored) {
        this.history = JSON.parse(stored);
        var self = this;
        this.history.forEach(function (msg) {
          self.addMessage(
            msg.role === 'assistant' ? 'bot' : 'user',
            msg.content
          );
        });
      }
    } catch (e) {
      /* corrupted */
    }
  };

  // ---- Initialize ----
  function init() {
    // Floating widget (all pages except dedicated chat page)
    if (document.getElementById('nakai-chat-widget')) {
      new NakaiChat({
        containerId: 'nakai-chat-widget',
        messagesId: 'nakai-chat-messages',
        formId: 'nakai-chat-form',
        inputId: 'nakai-chat-input',
        isFullPage: false,
      });
    }

    // Dedicated chat page
    if (document.getElementById('nakai-chatpage-container')) {
      new NakaiChat({
        containerId: 'nakai-chatpage-container',
        messagesId: 'nakai-chatpage-messages',
        formId: 'nakai-chatpage-form',
        inputId: 'nakai-chatpage-input',
        isFullPage: true,
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
