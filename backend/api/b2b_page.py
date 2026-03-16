"""B2B 営業ダッシュボード for NAKAI.

GET /b2b → 綺麗でシンプルなダッシュボード（6タブ）:
  1. 概要 - KPI・日次チャート
  2. リード - カフェ一覧（検索・フィルター）
  3. 配信 - 送信メール・開封追跡
  4. インポート - Excel/CSV ドラッグ＆ドロップ
  5. 発見 - 新しいカフェの検索
  6. 設定 - パイプライン設定
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

b2b_page_router = APIRouter()

B2B_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAKAI B2B 営業管理</title>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600;700&family=Shippori+Mincho:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--green:#406546;--cream:#F9F0E2;--white:#FFFFFF;--red:#c0392b;--orange:#e67e22;--blue:#2980b9;--gray:#888;--light:#f8f8f8;--border:#eee;--font:'Work Sans','Shippori Mincho',system-ui,sans-serif;--radius:12px;--shadow:0 2px 16px rgba(0,0,0,.06)}
body{font-family:var(--font);background:#f5f4f0;color:#333;min-height:100vh}

/* ログイン */
#login{display:flex;align-items:center;justify-content:center;min-height:100vh;background:var(--cream)}
.login-box{background:var(--white);padding:56px 48px;border-radius:20px;box-shadow:var(--shadow);text-align:center;max-width:380px;width:90%}
.login-box .logo{font-size:.75rem;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--green);margin-bottom:6px}
.login-box h2{font-size:1.05rem;font-weight:400;color:#555;margin-bottom:32px}
.login-box input{width:100%;padding:14px 18px;border:1.5px solid #e0e0e0;border-radius:10px;font-size:.95rem;outline:none;font-family:var(--font);transition:border .2s}
.login-box input:focus{border-color:var(--green)}
.login-box button{width:100%;padding:14px;background:var(--green);color:var(--white);border:none;border-radius:10px;font-size:.9rem;font-weight:500;cursor:pointer;font-family:var(--font);margin-top:16px;transition:opacity .2s}
.login-box button:hover{opacity:.9}
.login-error{color:var(--red);font-size:.82rem;margin-top:12px;display:none}

/* アプリ */
#app{display:none}
.topbar{background:var(--green);color:var(--cream);padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:56px}
.topbar .brand{display:flex;align-items:center;gap:12px}
.topbar .brand span:first-child{font-size:.7rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase}
.topbar .brand span:last-child{font-size:.75rem;opacity:.6}
.topbar button{background:rgba(255,255,255,.12);color:var(--cream);border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-size:.78rem;font-family:var(--font)}
.topbar button:hover{background:rgba(255,255,255,.2)}

.tabs{display:flex;background:var(--white);border-bottom:1px solid var(--border);padding:0 32px;overflow-x:auto}
.tab{padding:16px 20px;font-size:.82rem;font-weight:500;color:var(--gray);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;white-space:nowrap;transition:color .2s}
.tab:hover{color:#555}
.tab.active{color:var(--green);border-bottom-color:var(--green)}

.panel{display:none;padding:28px 32px;max-width:1400px;margin:0 auto}
.panel.active{display:block}

/* KPIカード */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:28px}
.kpi{background:var(--white);border-radius:var(--radius);padding:24px;box-shadow:var(--shadow)}
.kpi .label{font-size:.72rem;font-weight:600;letter-spacing:.08em;color:var(--gray);margin-bottom:8px}
.kpi .value{font-size:1.8rem;font-weight:300;color:var(--green)}
.kpi .sub{font-size:.75rem;color:var(--gray);margin-top:4px}

/* テーブル */
.card{background:var(--white);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden;margin-bottom:20px}
.card-header{padding:20px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)}
.card-header h3{font-size:.9rem;font-weight:500;color:#333}
table{width:100%;border-collapse:collapse}
th{font-size:.7rem;font-weight:600;letter-spacing:.06em;color:var(--gray);padding:12px 16px;text-align:left;background:var(--light);border-bottom:1px solid var(--border)}
td{padding:14px 16px;font-size:.85rem;border-bottom:1px solid #f5f5f5;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover{background:#fafaf8}

/* ステータスバッジ */
.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:.7rem;font-weight:500;letter-spacing:.04em}
.badge-new{background:#e8f5e9;color:#2e7d32}
.badge-researched{background:#e3f2fd;color:#1565c0}
.badge-contacted{background:#fff3e0;color:#e65100}
.badge-replied{background:#f3e5f5;color:#7b1fa2}
.badge-negotiating{background:#fce4ec;color:#c62828}
.badge-won{background:#e8f5e9;color:#1b5e20;font-weight:600}
.badge-lost{background:#f5f5f5;color:#999}
.badge-sent{background:#e3f2fd;color:#1565c0}
.badge-opened{background:#fff3e0;color:#e65100}
.badge-clicked{background:#f3e5f5;color:#7b1fa2}
.badge-bounced{background:#ffebee;color:#c62828}

/* ボタン */
.btn{padding:10px 20px;border:none;border-radius:8px;font-size:.82rem;font-weight:500;cursor:pointer;font-family:var(--font);transition:opacity .2s}
.btn:hover{opacity:.85}
.btn-primary{background:var(--green);color:var(--white)}
.btn-secondary{background:#f0f0f0;color:#555}
.btn-sm{padding:6px 14px;font-size:.75rem;border-radius:6px}
.btn-danger{background:var(--red);color:var(--white)}

/* 検索バー */
.search-bar{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;align-items:center}
.search-bar input,.search-bar select{padding:10px 16px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;font-family:var(--font);outline:none;transition:border .2s}
.search-bar input:focus,.search-bar select:focus{border-color:var(--green)}
.search-bar input{flex:1;min-width:200px}

/* インポート ドロップゾーン */
.drop-zone{border:2px dashed #d0d0d0;border-radius:16px;padding:64px 32px;text-align:center;cursor:pointer;transition:all .3s;background:var(--white);margin-bottom:20px}
.drop-zone:hover,.drop-zone.drag-over{border-color:var(--green);background:#f8fdf8}
.drop-zone h3{font-size:1rem;font-weight:400;color:#555;margin-bottom:8px}
.drop-zone p{font-size:.82rem;color:var(--gray)}
.drop-zone .icon{font-size:2.5rem;margin-bottom:16px;opacity:.3}

/* チャート */
.chart-container{background:var(--white);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px;margin-bottom:20px}
.chart-container h3{font-size:.85rem;font-weight:500;color:#555;margin-bottom:16px}
.chart-bar-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.chart-bar-label{font-size:.7rem;color:var(--gray);width:60px;text-align:right;flex-shrink:0}
.chart-bar{height:22px;border-radius:4px;transition:width .5s;min-width:2px}
.chart-bar-val{font-size:.7rem;color:var(--gray);flex-shrink:0}

/* モーダル */
.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:100;align-items:center;justify-content:center}
.modal-overlay.show{display:flex}
.modal{background:var(--white);border-radius:16px;padding:32px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto;box-shadow:0 16px 48px rgba(0,0,0,.15)}
.modal h3{font-size:1rem;font-weight:500;margin-bottom:20px}
.modal .close{float:right;background:none;border:none;font-size:1.2rem;cursor:pointer;color:var(--gray)}

/* 空状態 */
.empty{text-align:center;padding:64px 32px;color:var(--gray)}
.empty .icon{font-size:3rem;opacity:.2;margin-bottom:16px}
.empty h3{font-size:1rem;font-weight:400;margin-bottom:8px;color:#555}
.empty p{font-size:.85rem}

/* レスポンシブ */
@media(max-width:768px){
  .topbar,.tabs,.panel{padding-left:16px;padding-right:16px}
  .kpi-grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .kpi .value{font-size:1.4rem}
  td,th{padding:10px 12px;font-size:.8rem}
}
</style>
</head>
<body>

<!-- ログイン -->
<div id="login">
  <div class="login-box">
    <div class="logo">NAKAI</div>
    <h2>B2B 営業ダッシュボード</h2>
    <input type="password" id="pw" placeholder="管理者パスワード" onkeydown="if(event.key==='Enter')doLogin()">
    <button onclick="doLogin()">ログイン</button>
    <div class="login-error" id="login-err">パスワードが正しくありません</div>
  </div>
</div>

<!-- アプリ -->
<div id="app">
  <div class="topbar">
    <div class="brand">
      <span>NAKAI B2B</span>
      <span>バーチャル営業チーム</span>
    </div>
    <div style="display:flex;gap:8px;">
      <button onclick="runPipeline()">パイプライン実行</button>
      <button onclick="location.href='/admin'">管理画面</button>
    </div>
  </div>

  <div class="tabs">
    <div class="tab active" data-tab="overview">概要</div>
    <div class="tab" data-tab="leads">リード</div>
    <div class="tab" data-tab="outreach">配信</div>
    <div class="tab" data-tab="import">インポート</div>
    <div class="tab" data-tab="discover">発見</div>
    <div class="tab" data-tab="settings">設定</div>
  </div>

  <!-- 概要 -->
  <div class="panel active" id="panel-overview">
    <div class="kpi-grid" id="kpi-grid"></div>
    <div class="chart-container">
      <h3>日次アクティビティ（直近30日間）</h3>
      <div id="daily-chart"></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>最近追加されたカフェ</h3></div>
      <table><thead><tr><th>店名</th><th>都市</th><th>地域</th><th>ステータス</th><th>追加日</th></tr></thead>
      <tbody id="recent-leads-body"></tbody></table>
    </div>
  </div>

  <!-- リード -->
  <div class="panel" id="panel-leads">
    <div class="search-bar">
      <input type="text" id="lead-search" placeholder="カフェを検索..." oninput="debounceLoadLeads()">
      <select id="lead-region" onchange="loadLeads()">
        <option value="">全リージョン</option>
        <option value="us_west">米国 西部</option>
        <option value="us_east">米国 東部</option>
        <option value="us_south">米国 南部</option>
        <option value="us_midwest">米国 中西部</option>
        <option value="eu_uk">英国・アイルランド</option>
        <option value="eu_central">欧州 中央</option>
        <option value="eu_nordic">欧州 北欧</option>
        <option value="eu_med">欧州 地中海</option>
      </select>
      <select id="lead-status" onchange="loadLeads()">
        <option value="">全ステータス</option>
        <option value="new">新規</option>
        <option value="researched">調査済</option>
        <option value="contacted">連絡済</option>
        <option value="replied">返信あり</option>
        <option value="negotiating">交渉中</option>
        <option value="won">成約</option>
        <option value="lost">失注</option>
      </select>
      <button class="btn btn-secondary btn-sm" onclick="exportLeads()" style="white-space:nowrap;">Excel出力</button>
    </div>
    <div class="card">
      <table><thead><tr><th>カフェ名</th><th>都市</th><th>国</th><th>業態</th><th>ステータス</th><th>スコア</th><th>サイト</th><th></th></tr></thead>
      <tbody id="leads-body"></tbody></table>
    </div>
    <div style="text-align:center;padding:12px;">
      <button class="btn btn-secondary btn-sm" onclick="loadLeads(leadsOffset-100)">前へ</button>
      <span id="leads-count" style="margin:0 16px;font-size:.82rem;color:var(--gray)"></span>
      <button class="btn btn-secondary btn-sm" onclick="loadLeads(leadsOffset+100)">次へ</button>
    </div>
  </div>

  <!-- 配信 -->
  <div class="panel" id="panel-outreach">
    <div class="card">
      <div class="card-header"><h3>送信済みメール</h3></div>
      <table><thead><tr><th>件名</th><th>ステップ</th><th>ステータス</th><th>送信日時</th></tr></thead>
      <tbody id="outreach-body"></tbody></table>
    </div>
  </div>

  <!-- インポート -->
  <div class="panel" id="panel-import">
    <div class="drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
      <div class="icon">+</div>
      <h3>ExcelまたはCSVファイルをここにドロップ</h3>
      <p>.xlsx と .csv ファイルに対応しています</p>
    </div>
    <input type="file" id="file-input" accept=".xlsx,.csv" style="display:none" onchange="handleFile(this.files[0])">
    <div id="import-result" class="card" style="display:none"></div>
  </div>

  <!-- 発見 -->
  <div class="panel" id="panel-discover">
    <div class="card" style="padding:32px;">
      <h3 style="font-size:.95rem;font-weight:500;margin-bottom:20px;">新しいカフェを発見する</h3>
      <p style="font-size:.85rem;color:var(--gray);margin-bottom:24px;">リージョンまたは都市を指定してカフェを検索します。パイプラインにより毎日自動的に新規カフェも発見されます。</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;">
        <select id="disc-region" style="padding:10px 16px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;">
          <option value="">リージョンを選択</option>
          <option value="us_west">米国 西部</option>
          <option value="us_east">米国 東部</option>
          <option value="us_south">米国 南部</option>
          <option value="us_midwest">米国 中西部</option>
          <option value="eu_uk">英国・アイルランド</option>
          <option value="eu_central">欧州 中央</option>
          <option value="eu_nordic">欧州 北欧</option>
          <option value="eu_med">欧州 地中海</option>
        </select>
        <input type="text" id="disc-city" placeholder="または都市名を入力..." style="padding:10px 16px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;flex:1;min-width:200px;">
        <button class="btn btn-primary" onclick="runDiscover()">検索</button>
      </div>
      <div id="disc-result" style="font-size:.85rem;color:var(--gray);"></div>
    </div>
  </div>

  <!-- 設定 -->
  <div class="panel" id="panel-settings">
    <!-- メールテンプレート編集 -->
    <div class="card" style="padding:32px;margin-bottom:20px;">
      <h3 style="font-size:.95rem;font-weight:500;margin-bottom:8px;">メールテンプレート</h3>
      <p style="font-size:.82rem;color:var(--gray);margin-bottom:20px;">3段階の営業メールを自分で編集できます。変数: <code>{{cafe_name}}</code> <code>{{city}}</code> <code>{{cafe_type}}</code> <code>{{location}}</code></p>
      <div style="display:flex;gap:8px;margin-bottom:20px;">
        <button class="btn btn-sm" id="tpl-btn-1" onclick="showTemplate(1)" style="background:var(--green);color:#fff;">Step 1: 初回</button>
        <button class="btn btn-sm btn-secondary" id="tpl-btn-2" onclick="showTemplate(2)">Step 2: フォロー</button>
        <button class="btn btn-sm btn-secondary" id="tpl-btn-3" onclick="showTemplate(3)">Step 3: 最終</button>
      </div>
      <div id="tpl-editor">
        <label style="font-size:.75rem;font-weight:600;color:var(--gray);display:block;margin-bottom:6px;">件名</label>
        <input type="text" id="tpl-subject" style="width:100%;padding:10px 14px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;margin-bottom:16px;outline:none;" placeholder="Premium organic matcha for {{cafe_name}}">
        <label style="font-size:.75rem;font-weight:600;color:var(--gray);display:block;margin-bottom:6px;">本文</label>
        <textarea id="tpl-body" rows="12" style="width:100%;padding:14px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;line-height:1.6;resize:vertical;outline:none;" placeholder="Hi {{cafe_name}} team,&#10;&#10;I'm Takahiro from NAKAI..."></textarea>
        <div style="display:flex;gap:10px;margin-top:14px;align-items:center;">
          <button class="btn btn-primary" onclick="saveTemplate()">保存</button>
          <span id="tpl-msg" style="font-size:.82rem;color:var(--green);"></span>
        </div>
      </div>
    </div>

    <!-- テスト送信 -->
    <div class="card" style="padding:32px;margin-bottom:20px;">
      <h3 style="font-size:.95rem;font-weight:500;margin-bottom:8px;">テスト送信</h3>
      <p style="font-size:.82rem;color:var(--gray);margin-bottom:20px;">テンプレートの確認用にテストメールを送信します。</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;">
        <div style="flex:1;min-width:200px;">
          <label style="font-size:.75rem;font-weight:600;color:var(--gray);display:block;margin-bottom:6px;">送信先メール</label>
          <input type="email" id="test-email" style="width:100%;padding:10px 14px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;outline:none;" placeholder="your@email.com">
        </div>
        <div>
          <label style="font-size:.75rem;font-weight:600;color:var(--gray);display:block;margin-bottom:6px;">ステップ</label>
          <select id="test-step" style="padding:10px 14px;border:1.5px solid #e0e0e0;border-radius:8px;font-family:var(--font);font-size:.85rem;">
            <option value="1">Step 1: 初回</option>
            <option value="2">Step 2: フォロー</option>
            <option value="3">Step 3: 最終</option>
          </select>
        </div>
        <button class="btn btn-primary" onclick="sendTest()">テスト送信</button>
      </div>
      <div id="test-msg" style="font-size:.82rem;margin-top:12px;"></div>
    </div>

    <!-- PDF添付 -->
    <div class="card" style="padding:32px;margin-bottom:20px;">
      <h3 style="font-size:.95rem;font-weight:500;margin-bottom:8px;">PDF添付ファイル</h3>
      <p style="font-size:.82rem;color:var(--gray);margin-bottom:20px;">営業メールに添付するPDF（カタログ、価格表など）をアップロードできます。最大5MB。</p>
      <div id="pdf-status" style="margin-bottom:16px;"></div>
      <div style="display:flex;gap:10px;align-items:center;">
        <button class="btn btn-secondary" onclick="document.getElementById('pdf-input').click()">PDFをアップロード</button>
        <button class="btn btn-sm btn-danger" id="pdf-remove-btn" onclick="removePdf()" style="display:none;">削除</button>
        <input type="file" id="pdf-input" accept=".pdf" style="display:none" onchange="uploadPdf(this.files[0])">
        <span id="pdf-msg" style="font-size:.82rem;color:var(--gray);"></span>
      </div>
    </div>

    <!-- API接続状態 -->
    <div class="card" style="padding:32px;">
      <h3 style="font-size:.95rem;font-weight:500;margin-bottom:20px;">パイプライン設定</h3>
      <div style="display:grid;gap:16px;max-width:500px;">
        <div>
          <label style="font-size:.75rem;font-weight:600;letter-spacing:.06em;color:var(--gray);display:block;margin-bottom:6px;">1日の送信上限</label>
          <div style="font-size:1.1rem;font-weight:300;" id="cfg-limit">-</div>
        </div>
        <div>
          <label style="font-size:.75rem;font-weight:600;letter-spacing:.06em;color:var(--gray);display:block;margin-bottom:6px;">送信元メール</label>
          <div style="font-size:.9rem;" id="cfg-from">-</div>
        </div>
        <div>
          <label style="font-size:.75rem;font-weight:600;letter-spacing:.06em;color:var(--gray);display:block;margin-bottom:6px;">Google Places API</label>
          <div style="font-size:.9rem;" id="cfg-gp">-</div>
        </div>
        <div>
          <label style="font-size:.75rem;font-weight:600;letter-spacing:.06em;color:var(--gray);display:block;margin-bottom:6px;">Resend API</label>
          <div style="font-size:.9rem;" id="cfg-resend">-</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- リード詳細モーダル -->
<div class="modal-overlay" id="lead-modal">
  <div class="modal">
    <button class="close" onclick="closeModal()">&times;</button>
    <h3 id="modal-title">連絡先一覧</h3>
    <div id="modal-body"></div>
  </div>
</div>

<script>
const API = '/api/b2b';
let PWD = '';
let leadsOffset = 0;
let debounceTimer = null;

// ── ログイン ──
function doLogin(){
  PWD = document.getElementById('pw').value;
  fetch(API+'/stats', {headers:{'X-Admin-Password':PWD}})
    .then(r=>{
      if(!r.ok) throw new Error();
      document.getElementById('login').style.display='none';
      document.getElementById('app').style.display='block';
      return r.json();
    })
    .then(renderOverview)
    .catch(()=>{document.getElementById('login-err').style.display='block'});
}

function headers(){return {'X-Admin-Password':PWD,'Content-Type':'application/json'}}
function headersFile(){return {'X-Admin-Password':PWD}}

// ── タブ ──
document.querySelectorAll('.tab').forEach(tab=>{
  tab.addEventListener('click',()=>{
    const name = tab.dataset.tab;
    document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t===tab));
    document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id==='panel-'+name));
    if(name==='overview') loadStats();
    if(name==='leads') loadLeads();
    if(name==='outreach') loadOutreach();
    if(name==='settings') loadSettings();
  });
});

// ── 概要 ──
function loadStats(){
  fetch(API+'/stats',{headers:headers()}).then(r=>r.json()).then(renderOverview);
}

const STATUS_JA = {new:'新規',researched:'調査済',contacted:'連絡済',replied:'返信あり',negotiating:'交渉中',won:'成約',lost:'失注',sent:'送信済',opened:'開封',clicked:'クリック',bounced:'不達',pending:'未送信',unsubscribed:'配信停止'};
const REGION_JA = {us_west:'米国西部',us_east:'米国東部',us_south:'米国南部',us_midwest:'米国中西部',eu_uk:'英国',eu_central:'欧州中央',eu_nordic:'北欧',eu_med:'地中海'};
const TYPE_JA = {specialty:'スペシャルティ',chain:'チェーン',bakery:'ベーカリー',restaurant:'レストラン',hotel:'ホテル',bar:'バー'};

function renderOverview(s){
  const grid = document.getElementById('kpi-grid');
  const totalSent = s.total_sent||0;
  const replied = (s.outreach_by_status||{}).replied||0;
  const negotiating = (s.leads_by_status||{}).negotiating||0;
  const won = (s.leads_by_status||{}).won||0;
  const contacted = (s.leads_by_status||{}).contacted||0;

  grid.innerHTML = `
    <div class="kpi"><div class="label">総リード数</div><div class="value">${(s.total_leads||0).toLocaleString()}</div><div class="sub">${Object.keys(s.leads_by_region||{}).length} リージョン</div></div>
    <div class="kpi"><div class="label">連絡先取得</div><div class="value">${(s.total_contacts||0).toLocaleString()}</div><div class="sub">${s.verified_contacts||0} 件検証済</div></div>
    <div class="kpi"><div class="label">メール送信数</div><div class="value">${totalSent.toLocaleString()}</div><div class="sub">開封率 ${s.open_rate||0}%</div></div>
    <div class="kpi"><div class="label">返信率</div><div class="value">${s.reply_rate||0}%</div><div class="sub">${replied} 件の返信</div></div>
    <div class="kpi"><div class="label">成約数</div><div class="value">${won}</div><div class="sub">${negotiating} 件 交渉中</div></div>
    <div class="kpi"><div class="label">パイプライン</div><div class="value">${contacted+replied+negotiating}</div><div class="sub">アクティブリード</div></div>
  `;

  // 日次チャート
  const trend = s.daily_trend||[];
  const chart = document.getElementById('daily-chart');
  if(!trend.length){chart.innerHTML='<div class="empty"><p>データがまだありません。パイプラインを実行してください。</p></div>';return;}
  const maxSent = Math.max(...trend.map(d=>d.emails_sent||0),1);
  chart.innerHTML = trend.slice(-14).map(d=>`
    <div class="chart-bar-row">
      <div class="chart-bar-label">${d.date.slice(5)}</div>
      <div class="chart-bar" style="width:${(d.emails_sent||0)/maxSent*100}%;background:var(--green);"></div>
      <div class="chart-bar" style="width:${(d.opens||0)/maxSent*100}%;background:var(--orange);"></div>
      <div class="chart-bar-val">${d.emails_sent||0} 送信 / ${d.opens||0} 開封</div>
    </div>
  `).join('');

  // 最近のリード
  const tbody = document.getElementById('recent-leads-body');
  tbody.innerHTML = (s.recent_leads||[]).map(l=>`
    <tr onclick="showLeadDetail('${l.id}')" style="cursor:pointer">
      <td><strong>${esc(l.name)}</strong></td>
      <td>${esc(l.city||'')}</td>
      <td>${REGION_JA[l.region]||l.region||'-'}</td>
      <td><span class="badge badge-${l.status}">${STATUS_JA[l.status]||l.status}</span></td>
      <td>${timeAgo(l.created_at)}</td>
    </tr>
  `).join('') || '<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--gray);">リードがまだありません</td></tr>';
}

// ── リード ──
function debounceLoadLeads(){clearTimeout(debounceTimer);debounceTimer=setTimeout(()=>loadLeads(),300);}

function loadLeads(offset){
  leadsOffset = Math.max(0, offset||0);
  const search = document.getElementById('lead-search').value;
  const region = document.getElementById('lead-region').value;
  const status = document.getElementById('lead-status').value;
  let url = `${API}/leads?limit=100&offset=${leadsOffset}`;
  if(search) url += `&search=${encodeURIComponent(search)}`;
  if(region) url += `&region=${region}`;
  if(status) url += `&status=${status}`;

  fetch(url,{headers:headers()}).then(r=>r.json()).then(data=>{
    const tbody = document.getElementById('leads-body');
    const leads = data.leads||[];
    document.getElementById('leads-count').textContent = `${leadsOffset+1}-${leadsOffset+leads.length} / ${data.total||0} 件`;

    if(!leads.length){
      tbody.innerHTML = '<tr><td colspan="8"><div class="empty"><div class="icon">&#9749;</div><h3>カフェが見つかりません</h3><p>ファイルをインポートするか、発見タブでカフェを検索してください。</p></div></td></tr>';
      return;
    }

    tbody.innerHTML = leads.map(l=>`
      <tr onclick="showLeadDetail('${l.id}')" style="cursor:pointer">
        <td><strong>${esc(l.name)}</strong></td>
        <td>${esc(l.city||'')}</td>
        <td>${esc(l.country||'')}</td>
        <td>${TYPE_JA[l.cafe_type]||l.cafe_type||''}</td>
        <td><span class="badge badge-${l.status}">${STATUS_JA[l.status]||l.status}</span></td>
        <td>${l.lead_score||0}</td>
        <td>${l.website?'<a href="'+esc(l.website)+'" target="_blank" style="color:var(--green);">開く</a>':'-'}</td>
        <td><button class="btn btn-sm btn-danger" onclick="event.stopPropagation();deleteLead('${l.id}')">削除</button></td>
      </tr>
    `).join('');
  });
}

function deleteLead(id){
  if(!confirm('このリードを削除しますか？')) return;
  fetch(`${API}/leads/${id}`,{method:'DELETE',headers:headers()}).then(()=>loadLeads(leadsOffset));
}

function exportLeads(){
  const region = document.getElementById('lead-region').value;
  const status = document.getElementById('lead-status').value;
  let url = `${API}/export?`;
  if(region) url += `region=${region}&`;
  if(status) url += `status=${status}&`;
  fetch(url,{headers:headers()}).then(r=>{
    if(!r.ok) throw new Error('Export failed');
    return r.blob();
  }).then(blob=>{
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `NAKAI_B2B_Leads_${new Date().toISOString().slice(0,10)}.xlsx`;
    a.click();
    URL.revokeObjectURL(a.href);
  }).catch(e=>alert('エクスポートに失敗しました: '+e.message));
}

function showLeadDetail(id){
  fetch(`${API}/leads/${id}/contacts`,{headers:headers()}).then(r=>r.json()).then(contacts=>{
    document.getElementById('modal-title').textContent = '連絡先一覧';
    const body = document.getElementById('modal-body');
    if(!contacts.length){body.innerHTML='<p style="color:var(--gray)">連絡先がまだ見つかっていません。</p>';} else {
      body.innerHTML = '<table><thead><tr><th>メール</th><th>取得元</th><th>検証済</th></tr></thead><tbody>' +
        contacts.map(c=>`<tr><td>${esc(c.email)}</td><td>${esc(c.source||'')}</td><td>${c.verified?'はい':'いいえ'}</td></tr>`).join('') +
        '</tbody></table>';
    }
    document.getElementById('lead-modal').classList.add('show');
  });
}

function closeModal(){document.getElementById('lead-modal').classList.remove('show');}

// ── 配信 ──
function loadOutreach(){
  fetch(`${API}/outreach?limit=200`,{headers:headers()}).then(r=>r.json()).then(data=>{
    const tbody = document.getElementById('outreach-body');
    if(!data.length){tbody.innerHTML='<tr><td colspan="4"><div class="empty"><div class="icon">&#9993;</div><h3>まだメールを送信していません</h3><p>パイプラインを実行して営業メールを自動送信しましょう。</p></div></td></tr>';return;}
    tbody.innerHTML = data.map(o=>`
      <tr>
        <td>${esc(o.subject||'（件名なし）')}</td>
        <td>ステップ ${o.sequence_step||1}</td>
        <td><span class="badge badge-${o.status}">${STATUS_JA[o.status]||o.status}</span></td>
        <td>${timeAgo(o.sent_at||o.created_at)}</td>
      </tr>
    `).join('');
  });
}

// ── インポート ──
const dz = document.getElementById('drop-zone');
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag-over');});
dz.addEventListener('dragleave',()=>dz.classList.remove('drag-over'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag-over');if(e.dataTransfer.files.length)handleFile(e.dataTransfer.files[0]);});

function handleFile(file){
  if(!file) return;
  const formData = new FormData();
  formData.append('file', file);
  dz.innerHTML = '<div class="icon" style="animation:spin 1s linear infinite">&#8635;</div><h3>インポート中...</h3>';
  fetch(`${API}/import`,{method:'POST',headers:headersFile(),body:formData})
    .then(r=>r.json())
    .then(res=>{
      dz.innerHTML = '<div class="icon">&#10003;</div><h3>インポート完了</h3><p>クリックして別のファイルをインポート</p>';
      const result = document.getElementById('import-result');
      result.style.display = 'block';
      result.innerHTML = `<div style="padding:24px;">
        <p style="font-size:.9rem;margin-bottom:8px;"><strong>${res.imported||0}</strong> 件のカフェをインポートしました</p>
        <p style="font-size:.85rem;color:var(--gray);">${res.skipped||0} 件スキップ</p>
        ${(res.errors||[]).length?'<p style="font-size:.82rem;color:var(--red);margin-top:8px;">エラー: '+res.errors.slice(0,5).join(', ')+'</p>':''}
      </div>`;
    })
    .catch(()=>{
      dz.innerHTML = '<div class="icon" style="color:var(--red)">&#10007;</div><h3>インポート失敗</h3><p>クリックして再試行</p>';
    });
}

// ── 発見 ──
function runDiscover(){
  const region = document.getElementById('disc-region').value;
  const city = document.getElementById('disc-city').value;
  const result = document.getElementById('disc-result');
  result.textContent = '検索中...';

  let url = `${API}/discover?`;
  if(city) url += `city=${encodeURIComponent(city)}&region=${region||'us_west'}`;
  else if(region) url += `region=${region}`;
  else {result.textContent='リージョンを選択するか、都市名を入力してください。';return;}

  fetch(url,{method:'POST',headers:headers()})
    .then(r=>r.json())
    .then(data=>{
      result.textContent = data.error || `${data.found||0} 件の新しいカフェを発見しました！`;
      if(data.found > 0) setTimeout(()=>loadLeads(),500);
    })
    .catch(()=>{result.textContent='検索に失敗しました。Google Places APIキーを確認してください。'});
}

// ── パイプライン ──
function runPipeline(){
  if(!confirm('B2Bパイプラインを今すぐ実行しますか？')) return;
  fetch(`${API}/pipeline/run`,{method:'POST',headers:headers()})
    .then(r=>r.json())
    .then(()=>alert('パイプラインを開始しました。数分後に結果を確認してください。'));
}

// ── 設定 ──
let currentStep = 1;
let templates = {};

function loadSettings(){
  fetch(API+'/stats',{headers:headers()}).then(r=>r.json()).then(s=>{
    document.getElementById('cfg-limit').textContent = '333 通/日';
    document.getElementById('cfg-from').textContent = 'wholesale@nakaimatcha.com';
    document.getElementById('cfg-gp').textContent = s.total_leads > 0 ? '接続済' : '未設定';
    document.getElementById('cfg-resend').textContent = s.total_sent > 0 ? '接続済' : '環境変数を確認';
  });
  loadTemplates();
  loadPdfStatus();
}

function loadTemplates(){
  fetch(API+'/sequences',{headers:headers()}).then(r=>r.json()).then(data=>{
    templates = {};
    (data||[]).forEach(s=>{ templates[s.step_number] = s; });
    showTemplate(currentStep);
  });
}

function showTemplate(step){
  currentStep = step;
  [1,2,3].forEach(s=>{
    const btn = document.getElementById('tpl-btn-'+s);
    if(s===step){btn.style.background='var(--green)';btn.style.color='#fff';btn.className='btn btn-sm';}
    else{btn.style.background='';btn.style.color='';btn.className='btn btn-sm btn-secondary';}
  });
  const tpl = templates[step] || {};
  document.getElementById('tpl-subject').value = tpl.subject_template || '';
  document.getElementById('tpl-body').value = tpl.body_template || '';
  document.getElementById('tpl-msg').textContent = '';
}

function saveTemplate(){
  const subject = document.getElementById('tpl-subject').value;
  const body = document.getElementById('tpl-body').value;
  fetch(API+'/sequences/'+currentStep,{
    method:'PUT',
    headers:headers(),
    body:JSON.stringify({subject_template:subject, body_template:body})
  }).then(r=>r.json()).then(()=>{
    document.getElementById('tpl-msg').textContent = '保存しました';
    if(templates[currentStep]) {
      templates[currentStep].subject_template = subject;
      templates[currentStep].body_template = body;
    }
    setTimeout(()=>{document.getElementById('tpl-msg').textContent='';},3000);
  }).catch(()=>{document.getElementById('tpl-msg').textContent='保存に失敗しました';document.getElementById('tpl-msg').style.color='var(--red)';});
}

function sendTest(){
  const email = document.getElementById('test-email').value;
  const step = parseInt(document.getElementById('test-step').value);
  const msg = document.getElementById('test-msg');
  if(!email){msg.textContent='メールアドレスを入力してください';msg.style.color='var(--red)';return;}
  msg.textContent='送信中...';msg.style.color='var(--gray)';
  fetch(API+'/test-send',{
    method:'POST',
    headers:headers(),
    body:JSON.stringify({to_email:email, step:step, cafe_name:'Sample Cafe', city:'Portland', cafe_type:'specialty'})
  }).then(r=>r.json()).then(data=>{
    if(data.ok){msg.textContent='テスト送信しました: '+data.subject;msg.style.color='var(--green)';}
    else{msg.textContent='送信に失敗しました';msg.style.color='var(--red)';}
  }).catch(()=>{msg.textContent='送信に失敗しました';msg.style.color='var(--red)';});
}

function loadPdfStatus(){
  fetch(API+'/attachment',{headers:headers()}).then(r=>r.json()).then(data=>{
    const el = document.getElementById('pdf-status');
    const rmBtn = document.getElementById('pdf-remove-btn');
    if(data.filename){
      el.innerHTML='<span style="font-size:.85rem;">現在の添付: <strong>'+esc(data.filename)+'</strong></span>';
      rmBtn.style.display='inline-block';
    } else {
      el.innerHTML='<span style="font-size:.85rem;color:var(--gray);">添付ファイルなし</span>';
      rmBtn.style.display='none';
    }
  });
}

function uploadPdf(file){
  if(!file) return;
  const msg = document.getElementById('pdf-msg');
  msg.textContent='アップロード中...';
  const formData = new FormData();
  formData.append('file', file);
  fetch(API+'/attachment/upload',{method:'POST',headers:headersFile(),body:formData})
    .then(r=>r.json())
    .then(data=>{
      if(data.ok){msg.textContent=data.filename+' ('+data.size_kb+'KB)';loadPdfStatus();}
      else{msg.textContent='アップロード失敗';msg.style.color='var(--red)';}
    })
    .catch(()=>{msg.textContent='アップロード失敗';msg.style.color='var(--red)';});
}

function removePdf(){
  if(!confirm('添付ファイルを削除しますか？')) return;
  fetch(API+'/attachment',{method:'DELETE',headers:headers()}).then(()=>loadPdfStatus());
  document.getElementById('pdf-msg').textContent='';
}

// ── ヘルパー ──
function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):'';}

function timeAgo(ts){
  if(!ts) return '-';
  const d = new Date(ts);
  const diff = (Date.now()-d.getTime())/1000;
  if(diff<60) return 'たった今';
  if(diff<3600) return Math.floor(diff/60)+'分前';
  if(diff<86400) return Math.floor(diff/3600)+'時間前';
  if(diff<2592000) return Math.floor(diff/86400)+'日前';
  return Math.floor(diff/2592000)+'ヶ月前';
}

// 初期化
setTimeout(loadSettings, 100);
</script>

<style>@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}</style>
</body>
</html>"""


@b2b_page_router.get("/b2b", response_class=HTMLResponse)
async def b2b_dashboard():
    return B2B_HTML
