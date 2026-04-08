"""AI Ops Chat section — natural language operations assistant."""


def html() -> str:
    return """
<style>
.ops-chat-wrap{display:flex;flex-direction:column;height:calc(100vh - 120px);min-height:400px}
.ops-messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.ops-msg{max-width:85%;padding:10px 14px;border-radius:12px;font-size:.88rem;line-height:1.5;word-wrap:break-word;white-space:pre-wrap}
.ops-msg.user{align-self:flex-end;background:#406546;color:#fff;border-bottom-right-radius:4px}
.ops-msg.assistant{align-self:flex-start;background:#f5f5f5;color:#333;border-bottom-left-radius:4px}
.ops-msg.tool{align-self:center;background:#fff;border:1px solid #e0e0e0;color:#888;font-size:.78rem;padding:6px 12px;border-radius:8px}
.ops-msg.tool i{margin-right:4px;color:#406546}
.ops-tool-pulse{animation:opsPulse 1.2s ease-in-out infinite}
@keyframes opsPulse{0%,100%{opacity:.6}50%{opacity:1}}
.ops-input-row{display:flex;gap:8px;padding:12px 16px;border-top:1px solid #eee;background:#fff}
.ops-input-row input{flex:1;border:1px solid #ddd;border-radius:8px;padding:10px 14px;font-size:.88rem;outline:none}
.ops-input-row input:focus{border-color:#406546}
.ops-input-row button{background:#406546;color:#fff;border:none;border-radius:8px;padding:10px 18px;font-size:.88rem;cursor:pointer;white-space:nowrap}
.ops-input-row button:disabled{opacity:.5;cursor:not-allowed}
.ops-chips{display:flex;gap:6px;padding:4px 16px 8px;flex-wrap:wrap}
.ops-chip{background:#f0f0f0;border:1px solid #ddd;border-radius:16px;padding:5px 12px;font-size:.76rem;cursor:pointer;transition:all .15s}
.ops-chip:hover{background:#406546;color:#fff;border-color:#406546}
.ops-welcome{text-align:center;padding:40px 20px;color:#888}
.ops-welcome h3{color:#333;font-weight:500;margin-bottom:8px}
.ops-welcome p{font-size:.85rem;max-width:400px;margin:0 auto 16px}
</style>

<div class="ops-chat-wrap">
  <div class="ops-messages" id="ops-messages">
    <div class="ops-welcome">
      <div style="font-size:2rem;margin-bottom:8px"><i class="ti ti-robot" style="color:#406546"></i></div>
      <h3>AI Operations Assistant</h3>
      <p>B2B、メール、SNS、分析など、ダッシュボードの操作を自然言語で指示できます。</p>
    </div>
  </div>
  <div class="ops-chips" id="ops-chips">
    <div class="ops-chip" onclick="opsQuick('B2Bの統計を見せて')">B2B Stats</div>
    <div class="ops-chip" onclick="opsQuick('メールキャンペーン一覧')">Campaigns</div>
    <div class="ops-chip" onclick="opsQuick('今日のSNSコンテンツをプレビュー')">Today\\'s Content</div>
    <div class="ops-chip" onclick="opsQuick('チャット分析を見せて')">Analytics</div>
    <div class="ops-chip" onclick="opsQuick('リサーチ結果を見せて')">Research</div>
    <div class="ops-chip" onclick="opsQuick('Shopifyの商品情報')">Shopify</div>
  </div>
  <div class="ops-input-row">
    <input type="text" id="ops-input" placeholder="指示を入力... (例: Portlandのリードを検索して)" onkeydown="if(event.key==='Enter')opsSend()">
    <button id="ops-send-btn" onclick="opsSend()"><i class="ti ti-send"></i> Send</button>
  </div>
</div>

<script>
(function(){
  var H = {'Content-Type':'application/json'};
  var opsHistory = [];
  var sending = false;

  function $(id){return document.getElementById(id);}
  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}

  function addMsg(cls, html){
    var el = document.createElement('div');
    el.className = 'ops-msg ' + cls;
    el.innerHTML = html;
    $('ops-messages').appendChild(el);
    $('ops-messages').scrollTop = $('ops-messages').scrollHeight;
    return el;
  }

  function setInput(enabled){
    sending = !enabled;
    $('ops-input').disabled = !enabled;
    $('ops-send-btn').disabled = !enabled;
  }

  window.opsQuick = function(text){
    $('ops-input').value = text;
    opsSend();
  };

  window.opsSend = async function(){
    if(sending) return;
    var input = $('ops-input');
    var msg = input.value.trim();
    if(!msg) return;
    input.value = '';

    // Clear welcome
    var welcome = $('ops-messages').querySelector('.ops-welcome');
    if(welcome) welcome.remove();

    addMsg('user', esc(msg));
    setInput(false);

    // Show thinking indicator
    var thinkEl = addMsg('tool', '<i class="ti ti-loader ops-tool-pulse"></i> Thinking...');

    try{
      var resp = await fetch('/api/ops/chat', {
        method: 'POST',
        headers: H,
        body: JSON.stringify({message: msg, history: opsHistory}),
      });

      if(!resp.ok){
        thinkEl.remove();
        addMsg('assistant', '<span style="color:#c0392b">Error: ' + resp.status + '</span>');
        setInput(true);
        return;
      }

      var data = await resp.json();
      thinkEl.remove();

      // Show tool events
      (data.events || []).forEach(function(ev){
        if(ev.type === 'tool_use'){
          addMsg('tool', '<i class="ti ti-tool"></i> ' + esc(ev.name));
        }
      });

      // Show response
      if(data.response){
        addMsg('assistant', formatResponse(data.response));
      }

      // Update history for next turn
      opsHistory = data.messages || [];

    } catch(e) {
      thinkEl.remove();
      addMsg('assistant', '<span style="color:#c0392b">Network error: ' + esc(e.message) + '</span>');
    }

    setInput(true);
    $('ops-input').focus();
  };

  function formatResponse(text){
    // Basic markdown: bold, code blocks, line breaks
    var s = esc(text);
    s = s.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
    s = s.replace(/`([^`]+)`/g, '<code style="background:#e8e8e8;padding:1px 4px;border-radius:3px;font-size:.82rem">$1</code>');
    s = s.replace(/\\n/g, '<br>');
    return s;
  }
})();
</script>
"""
