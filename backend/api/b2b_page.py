"""B2B 営業ダッシュボード for NAKAI.

GET /b2b → Tabler Dashboard（6タブ）:
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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/css/tabler.min.css">
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600;700&family=Shippori+Mincho:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --tblr-primary:#406546;
  --tblr-primary-rgb:64,101,70;
  --tblr-font-sans-serif:'Work Sans','Shippori Mincho',system-ui,sans-serif;
  --tblr-body-bg:#f5f4f0;
}
body{font-family:var(--tblr-font-sans-serif)}
.navbar-brand-text{font-size:.7rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase}
.navbar-brand-sub{font-size:.75rem;opacity:.6;margin-left:12px}
.nav-tabs .nav-link{font-size:.82rem;font-weight:500;color:#888}
.nav-tabs .nav-link.active{color:#406546;border-bottom-color:#406546}
.kpi-value{font-size:1.8rem;font-weight:300;color:#406546}
.kpi-label{font-size:.72rem;font-weight:600;letter-spacing:.08em;color:#888;margin-bottom:4px}
.kpi-sub{font-size:.75rem;color:#888;margin-top:2px}
.drop-zone{border:2px dashed #d0d0d0;border-radius:16px;padding:64px 32px;text-align:center;cursor:pointer;transition:all .3s;background:#fff}
.drop-zone:hover,.drop-zone.drag-over{border-color:#406546;background:#f8fdf8}
.chart-bar-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.chart-bar-label{font-size:.7rem;color:#888;width:60px;text-align:right;flex-shrink:0}
.chart-bar{height:22px;border-radius:4px;transition:width .5s;min-width:2px}
.chart-bar-val{font-size:.7rem;color:#888;flex-shrink:0}
.tab-pane{display:none;padding:28px 0}
.tab-pane.active{display:block}
#login{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#F9F0E2}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
</style>
</head>
<body>

<!-- ログイン -->
<div id="login">
  <div class="card card-md" style="max-width:380px;width:90%;border-radius:20px;">
    <div class="card-body text-center py-5 px-4">
      <div class="kpi-label" style="font-size:.75rem;letter-spacing:.2em;margin-bottom:6px;">NAKAI</div>
      <h2 class="mb-4" style="font-size:1.05rem;font-weight:400;color:#555;">B2B 営業ダッシュボード</h2>
      <input type="password" id="pw" class="form-control mb-3" placeholder="管理者パスワード" onkeydown="if(event.key==='Enter')doLogin()">
      <button class="btn btn-primary w-100" onclick="doLogin()">ログイン</button>
      <div class="text-danger small mt-3" id="login-err" style="display:none;">パスワードが正しくありません</div>
    </div>
  </div>
</div>

<!-- アプリ -->
<div id="app" style="display:none;">
  <header class="navbar navbar-expand-sm navbar-dark" style="background:#406546;">
    <div class="container-xl">
      <div class="d-flex align-items-center">
        <span class="navbar-brand-text text-white">NAKAI B2B</span>
        <span class="navbar-brand-sub text-white">バーチャル営業チーム</span>
      </div>
      <div class="d-flex gap-2 ms-auto">
        <button class="btn btn-ghost-light btn-sm" onclick="runPipeline()">パイプライン実行</button>
        <button class="btn btn-ghost-light btn-sm" onclick="location.href='/admin'">管理画面</button>
      </div>
    </div>
  </header>

  <div class="container-xl">
    <ul class="nav nav-tabs mt-3" role="tablist">
      <li class="nav-item"><a class="nav-link active" href="#" data-tab="overview">概要</a></li>
      <li class="nav-item"><a class="nav-link" href="#" data-tab="leads">リード</a></li>
      <li class="nav-item"><a class="nav-link" href="#" data-tab="outreach">配信</a></li>
      <li class="nav-item"><a class="nav-link" href="#" data-tab="import">インポート</a></li>
      <li class="nav-item"><a class="nav-link" href="#" data-tab="discover">発見</a></li>
      <li class="nav-item"><a class="nav-link" href="#" data-tab="settings">設定</a></li>
    </ul>

    <!-- 概要 -->
    <div class="tab-pane active" id="panel-overview">
      <div class="row row-deck row-cards mb-3" id="kpi-grid"></div>
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">日次アクティビティ（直近30日間）</h3></div>
        <div class="card-body" id="daily-chart"></div>
      </div>
      <div class="card">
        <div class="card-header"><h3 class="card-title">最近追加されたカフェ</h3></div>
        <div class="table-responsive">
          <table class="table table-vcenter table-hover card-table">
            <thead><tr><th>店名</th><th>都市</th><th>地域</th><th>ステータス</th><th>追加日</th></tr></thead>
            <tbody id="recent-leads-body"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- リード -->
    <div class="tab-pane" id="panel-leads">
      <div class="row g-2 align-items-center mb-3">
        <div class="col"><input type="text" id="lead-search" class="form-control" placeholder="カフェを検索..." oninput="debounceLoadLeads()"></div>
        <div class="col-auto">
          <select id="lead-region" class="form-select" onchange="loadLeads()">
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
        </div>
        <div class="col-auto">
          <select id="lead-status" class="form-select" onchange="loadLeads()">
            <option value="">全ステータス</option>
            <option value="new">新規</option>
            <option value="researched">調査済</option>
            <option value="contacted">連絡済</option>
            <option value="replied">返信あり</option>
            <option value="negotiating">交渉中</option>
            <option value="won">成約</option>
            <option value="lost">失注</option>
          </select>
        </div>
        <div class="col-auto"><button class="btn btn-outline-secondary btn-sm" onclick="exportLeads()">Excel出力</button></div>
      </div>
      <div class="card">
        <div class="table-responsive">
          <table class="table table-vcenter table-hover card-table">
            <thead><tr><th>カフェ名</th><th>都市</th><th>国</th><th>業態</th><th>ステータス</th><th>スコア</th><th>サイト</th><th></th></tr></thead>
            <tbody id="leads-body"></tbody>
          </table>
        </div>
      </div>
      <div class="d-flex justify-content-center align-items-center gap-3 py-3">
        <button class="btn btn-outline-secondary btn-sm" onclick="loadLeads(leadsOffset-100)">前へ</button>
        <span id="leads-count" class="text-muted small"></span>
        <button class="btn btn-outline-secondary btn-sm" onclick="loadLeads(leadsOffset+100)">次へ</button>
      </div>
    </div>

    <!-- 配信 -->
    <div class="tab-pane" id="panel-outreach">
      <div class="card">
        <div class="card-header"><h3 class="card-title">送信済みメール</h3></div>
        <div class="table-responsive">
          <table class="table table-vcenter table-hover card-table">
            <thead><tr><th>件名</th><th>ステップ</th><th>ステータス</th><th>送信日時</th></tr></thead>
            <tbody id="outreach-body"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- インポート -->
    <div class="tab-pane" id="panel-import">
      <div class="drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
        <div style="font-size:2.5rem;opacity:.3;margin-bottom:16px;">+</div>
        <h3 style="font-size:1rem;font-weight:400;color:#555;margin-bottom:8px;">ExcelまたはCSVファイルをここにドロップ</h3>
        <p class="text-muted small">.xlsx と .csv ファイルに対応しています</p>
      </div>
      <input type="file" id="file-input" accept=".xlsx,.csv" style="display:none" onchange="handleFile(this.files[0])">
      <div id="import-result" class="card" style="display:none"></div>
    </div>

    <!-- 発見 -->
    <div class="tab-pane" id="panel-discover">
      <div class="card">
        <div class="card-header"><h3 class="card-title">新しいカフェを発見する</h3></div>
        <div class="card-body">
          <p class="text-muted mb-4">リージョンまたは都市を指定してカフェを検索します。パイプラインにより毎日自動的に新規カフェも発見されます。</p>
          <div class="row g-2 align-items-end mb-3">
            <div class="col-auto">
              <select id="disc-region" class="form-select">
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
            </div>
            <div class="col"><input type="text" id="disc-city" class="form-control" placeholder="または都市名を入力..."></div>
            <div class="col-auto"><button class="btn btn-primary" onclick="runDiscover()">検索</button></div>
          </div>
          <div id="disc-result" class="text-muted small"></div>
        </div>
      </div>
    </div>

    <!-- 設定 -->
    <div class="tab-pane" id="panel-settings">
      <!-- メールテンプレート編集 -->
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">メールテンプレート</h3></div>
        <div class="card-body">
          <p class="text-muted small mb-3">3段階の営業メールを自分で編集できます。変数: <code>{{cafe_name}}</code> <code>{{city}}</code> <code>{{cafe_type}}</code> <code>{{location}}</code></p>
          <div class="btn-group mb-3" role="group">
            <button class="btn btn-sm btn-primary" id="tpl-btn-1" onclick="showTemplate(1)">Step 1: 初回</button>
            <button class="btn btn-sm btn-outline-secondary" id="tpl-btn-2" onclick="showTemplate(2)">Step 2: フォロー</button>
            <button class="btn btn-sm btn-outline-secondary" id="tpl-btn-3" onclick="showTemplate(3)">Step 3: 最終</button>
          </div>
          <div id="tpl-editor">
            <div class="mb-3">
              <label class="form-label">件名</label>
              <input type="text" id="tpl-subject" class="form-control" placeholder="Premium organic matcha for {{cafe_name}}">
            </div>
            <div class="mb-3">
              <label class="form-label">本文</label>
              <textarea id="tpl-body" class="form-control" rows="12" placeholder="Hi {{cafe_name}} team,&#10;&#10;I'm Takahiro from NAKAI..."></textarea>
            </div>
            <div class="d-flex align-items-center gap-3">
              <button class="btn btn-primary" onclick="saveTemplate()">保存</button>
              <span id="tpl-msg" class="small" style="color:#406546;"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- テスト送信 -->
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">テスト送信</h3></div>
        <div class="card-body">
          <p class="text-muted small mb-3">テンプレートの確認用にテストメールを送信します。</p>
          <div class="row g-2 align-items-end">
            <div class="col">
              <label class="form-label">送信先メール</label>
              <input type="email" id="test-email" class="form-control" placeholder="your@email.com">
            </div>
            <div class="col-auto">
              <label class="form-label">ステップ</label>
              <select id="test-step" class="form-select">
                <option value="1">Step 1: 初回</option>
                <option value="2">Step 2: フォロー</option>
                <option value="3">Step 3: 最終</option>
              </select>
            </div>
            <div class="col-auto"><button class="btn btn-primary" onclick="sendTest()">テスト送信</button></div>
          </div>
          <div id="test-msg" class="small mt-2"></div>
        </div>
      </div>

      <!-- PDF添付 -->
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">PDF添付ファイル</h3></div>
        <div class="card-body">
          <p class="text-muted small mb-3">営業メールに添付するPDF（カタログ、価格表など）をアップロードできます。最大5MB。</p>
          <div id="pdf-status" class="mb-3"></div>
          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('pdf-input').click()">PDFをアップロード</button>
            <button class="btn btn-sm btn-outline-danger" id="pdf-remove-btn" onclick="removePdf()" style="display:none;">削除</button>
            <input type="file" id="pdf-input" accept=".pdf" style="display:none" onchange="uploadPdf(this.files[0])">
            <span id="pdf-msg" class="text-muted small"></span>
          </div>
        </div>
      </div>

      <!-- Resend ドメイン認証 -->
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">Resend ドメイン認証</h3></div>
        <div class="card-body">
          <p class="text-muted small mb-3">メール送信にはドメイン認証が必要です。以下の DNS レコードを Shopify のドメイン設定に追加してください。</p>
          <button class="btn btn-outline-secondary btn-sm mb-3" onclick="checkResendDomain()">認証状態を確認</button>
          <div id="resend-domain-status"></div>
        </div>
      </div>

      <!-- API接続状態 -->
      <div class="card">
        <div class="card-header"><h3 class="card-title">パイプライン設定</h3></div>
        <div class="card-body">
          <div class="datagrid" style="max-width:500px;">
            <div class="datagrid-item">
              <div class="datagrid-title">1日の送信上限</div>
              <div class="datagrid-content" id="cfg-limit">-</div>
            </div>
            <div class="datagrid-item">
              <div class="datagrid-title">送信元メール</div>
              <div class="datagrid-content" id="cfg-from">-</div>
            </div>
            <div class="datagrid-item">
              <div class="datagrid-title">Google Places API</div>
              <div class="datagrid-content" id="cfg-gp">-</div>
            </div>
            <div class="datagrid-item">
              <div class="datagrid-title">Resend API</div>
              <div class="datagrid-content" id="cfg-resend">-</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div><!-- /container-xl -->
</div><!-- /app -->

<!-- リード詳細モーダル -->
<div class="modal modal-blur fade" id="lead-modal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modal-title">連絡先一覧</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body" id="modal-body"></div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/js/tabler.min.js"></script>
<script>
var API = '/api/b2b';
var PWD = '';
var leadsOffset = 0;
var debounceTimer = null;

var BADGE_CLASS = {
  'new':'bg-green-lt','researched':'bg-azure-lt','contacted':'bg-orange-lt',
  'replied':'bg-purple-lt','negotiating':'bg-pink-lt','won':'bg-green-lt',
  'lost':'bg-secondary-lt','sent':'bg-azure-lt','opened':'bg-orange-lt',
  'clicked':'bg-purple-lt','bounced':'bg-red-lt','pending':'bg-secondary-lt',
  'unsubscribed':'bg-secondary-lt'
};
var STATUS_JA = {new:'新規',researched:'調査済',contacted:'連絡済',replied:'返信あり',negotiating:'交渉中',won:'成約',lost:'失注',sent:'送信済',opened:'開封',clicked:'クリック',bounced:'不達',pending:'未送信',unsubscribed:'配信停止'};
var REGION_JA = {us_west:'米国西部',us_east:'米国東部',us_south:'米国南部',us_midwest:'米国中西部',eu_uk:'英国',eu_central:'欧州中央',eu_nordic:'北欧',eu_med:'地中海'};
var TYPE_JA = {specialty:'スペシャルティ',chain:'チェーン',bakery:'ベーカリー',restaurant:'レストラン',hotel:'ホテル',bar:'バー'};

// ── ログイン ──
function enterApp(statsData){
  document.getElementById('login').style.display='none';
  document.getElementById('app').style.display='block';
  try{ renderOverview(statsData||{}); }catch(e){ console.error('renderOverview error',e); }
}

function doLogin(){
  PWD = document.getElementById('pw').value;
  if(!PWD){document.getElementById('login-err').style.display='block';return;}
  fetch(API+'/stats', {headers:{'X-Admin-Password':PWD}})
    .then(function(r){
      if(!r.ok) throw new Error('パスワードが正しくありません');
      sessionStorage.setItem('nakai_admin_pw', PWD);
      return r.json();
    })
    .then(function(data){enterApp(data);})
    .catch(function(e){
      document.getElementById('login-err').textContent=e.message||'ログインに失敗しました';
      document.getElementById('login-err').style.display='block';
    });
}

// Auto-login from /admin session
(function autoLogin(){
  var stored = sessionStorage.getItem('nakai_admin_pw');
  if(stored){
    PWD = stored;
    fetch(API+'/stats', {headers:{'X-Admin-Password':PWD}})
      .then(function(r){
        if(!r.ok) throw new Error();
        return r.json();
      })
      .then(function(data){enterApp(data);})
      .catch(function(){});
  }
})();

function headers(){return {'X-Admin-Password':PWD,'Content-Type':'application/json'};}
function headersFile(){return {'X-Admin-Password':PWD};}

// ── タブ ──
document.querySelectorAll('.nav-tabs .nav-link').forEach(function(tab){
  tab.addEventListener('click',function(e){
    e.preventDefault();
    var name = tab.dataset.tab;
    document.querySelectorAll('.nav-tabs .nav-link').forEach(function(t){t.classList.toggle('active',t===tab);});
    document.querySelectorAll('.tab-pane').forEach(function(p){p.classList.toggle('active',p.id==='panel-'+name);});
    if(name==='overview') loadStats();
    if(name==='leads') loadLeads();
    if(name==='outreach') loadOutreach();
    if(name==='settings') loadSettings();
  });
});

// ── 概要 ──
function loadStats(){
  fetch(API+'/stats',{headers:headers()}).then(function(r){return r.json();}).then(renderOverview);
}

function renderOverview(s){
  var grid = document.getElementById('kpi-grid');
  var totalSent = s.total_sent||0;
  var replied = (s.outreach_by_status||{}).replied||0;
  var negotiating = (s.leads_by_status||{}).negotiating||0;
  var won = (s.leads_by_status||{}).won||0;
  var contacted = (s.leads_by_status||{}).contacted||0;

  grid.innerHTML =
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">総リード数</div><div class="kpi-value">'+(s.total_leads||0).toLocaleString()+'</div><div class="kpi-sub">'+Object.keys(s.leads_by_region||{}).length+' リージョン</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">連絡先取得</div><div class="kpi-value">'+(s.total_contacts||0).toLocaleString()+'</div><div class="kpi-sub">'+(s.verified_contacts||0)+' 件検証済</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">メール送信数</div><div class="kpi-value">'+totalSent.toLocaleString()+'</div><div class="kpi-sub">開封率 '+(s.open_rate||0)+'%</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">返信率</div><div class="kpi-value">'+(s.reply_rate||0)+'%</div><div class="kpi-sub">'+replied+' 件の返信</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">成約数</div><div class="kpi-value">'+won+'</div><div class="kpi-sub">'+negotiating+' 件 交渉中</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">パイプライン</div><div class="kpi-value">'+(contacted+replied+negotiating)+'</div><div class="kpi-sub">アクティブリード</div></div></div></div>';

  // 日次チャート
  var trend = s.daily_trend||[];
  var chart = document.getElementById('daily-chart');
  if(!trend.length){chart.innerHTML='<div class="text-center text-muted py-4">データがまだありません。パイプラインを実行してください。</div>';return;}
  var maxSent = Math.max.apply(null,trend.map(function(d){return d.emails_sent||0;}).concat([1]));
  chart.innerHTML = trend.slice(-14).map(function(d){
    return '<div class="chart-bar-row"><div class="chart-bar-label">'+d.date.slice(5)+'</div><div class="chart-bar" style="width:'+(d.emails_sent||0)/maxSent*100+'%;background:#406546;"></div><div class="chart-bar" style="width:'+(d.opens||0)/maxSent*100+'%;background:#e67e22;"></div><div class="chart-bar-val">'+(d.emails_sent||0)+' 送信 / '+(d.opens||0)+' 開封</div></div>';
  }).join('');

  // 最近のリード
  var tbody = document.getElementById('recent-leads-body');
  var recentLeads = s.recent_leads||[];
  if(!recentLeads.length){
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">リードがまだありません</td></tr>';
  } else {
    tbody.innerHTML = recentLeads.map(function(l){
      return '<tr onclick="showLeadDetail(\\\''+l.id+'\\\')" style="cursor:pointer"><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.city||'')+'</td><td>'+(REGION_JA[l.region]||l.region||'-')+'</td><td><span class="badge '+(BADGE_CLASS[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></td><td>'+timeAgo(l.created_at)+'</td></tr>';
    }).join('');
  }
}

// ── リード ──
function debounceLoadLeads(){clearTimeout(debounceTimer);debounceTimer=setTimeout(function(){loadLeads();},300);}

function loadLeads(offset){
  leadsOffset = Math.max(0, offset||0);
  var search = document.getElementById('lead-search').value;
  var region = document.getElementById('lead-region').value;
  var status = document.getElementById('lead-status').value;
  var url = API+'/leads?limit=100&offset='+leadsOffset;
  if(search) url += '&search='+encodeURIComponent(search);
  if(region) url += '&region='+region;
  if(status) url += '&status='+status;

  fetch(url,{headers:headers()}).then(function(r){return r.json();}).then(function(data){
    var tbody = document.getElementById('leads-body');
    var leads = data.leads||[];
    document.getElementById('leads-count').textContent = (leadsOffset+1)+'-'+(leadsOffset+leads.length)+' / '+(data.total||0)+' 件';

    if(!leads.length){
      tbody.innerHTML = '<tr><td colspan="8"><div class="text-center text-muted py-5"><div style="font-size:3rem;opacity:.2;margin-bottom:16px;">&#9749;</div><h3 style="font-weight:400;margin-bottom:8px;">カフェが見つかりません</h3><p>ファイルをインポートするか、発見タブでカフェを検索してください。</p></div></td></tr>';
      return;
    }

    tbody.innerHTML = leads.map(function(l){
      return '<tr onclick="showLeadDetail(\\\''+l.id+'\\\')" style="cursor:pointer"><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.city||'')+'</td><td>'+esc(l.country||'')+'</td><td>'+(TYPE_JA[l.cafe_type]||l.cafe_type||'')+'</td><td><span class="badge '+(BADGE_CLASS[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></td><td>'+(l.lead_score||0)+'</td><td>'+(l.website?'<a href="'+esc(l.website)+'" target="_blank" style="color:#406546;">開く</a>':'-')+'</td><td><button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation();deleteLead(\\\''+l.id+'\\\')">削除</button></td></tr>';
    }).join('');
  });
}

function deleteLead(id){
  if(!confirm('このリードを削除しますか？')) return;
  fetch(API+'/leads/'+id,{method:'DELETE',headers:headers()}).then(function(){loadLeads(leadsOffset);});
}

function exportLeads(){
  var region = document.getElementById('lead-region').value;
  var status = document.getElementById('lead-status').value;
  var url = API+'/export?';
  if(region) url += 'region='+region+'&';
  if(status) url += 'status='+status+'&';
  fetch(url,{headers:headers()}).then(function(r){
    if(!r.ok) throw new Error('Export failed');
    return r.blob();
  }).then(function(blob){
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'NAKAI_B2B_Leads_'+new Date().toISOString().slice(0,10)+'.xlsx';
    a.click();
    URL.revokeObjectURL(a.href);
  }).catch(function(e){alert('エクスポートに失敗しました: '+e.message);});
}

function showLeadDetail(id){
  fetch(API+'/leads/'+id+'/contacts',{headers:headers()}).then(function(r){return r.json();}).then(function(contacts){
    document.getElementById('modal-title').textContent = '連絡先一覧';
    var body = document.getElementById('modal-body');
    if(!contacts.length){
      body.innerHTML='<p class="text-muted">連絡先がまだ見つかっていません。</p>';
    } else {
      body.innerHTML = '<div class="table-responsive"><table class="table table-vcenter"><thead><tr><th>メール</th><th>取得元</th><th>検証済</th></tr></thead><tbody>' +
        contacts.map(function(c){return '<tr><td>'+esc(c.email)+'</td><td>'+esc(c.source||'')+'</td><td>'+(c.verified?'はい':'いいえ')+'</td></tr>';}).join('') +
        '</tbody></table></div>';
    }
    var modal = new bootstrap.Modal(document.getElementById('lead-modal'));
    modal.show();
  });
}

// ── 配信 ──
function loadOutreach(){
  fetch(API+'/outreach?limit=200',{headers:headers()}).then(function(r){return r.json();}).then(function(data){
    var tbody = document.getElementById('outreach-body');
    if(!data.length){
      tbody.innerHTML='<tr><td colspan="4"><div class="text-center text-muted py-5"><div style="font-size:3rem;opacity:.2;margin-bottom:16px;">&#9993;</div><h3 style="font-weight:400;margin-bottom:8px;">まだメールを送信していません</h3><p>パイプラインを実行して営業メールを自動送信しましょう。</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = data.map(function(o){
      return '<tr><td>'+esc(o.subject||'（件名なし）')+'</td><td>ステップ '+(o.sequence_step||1)+'</td><td><span class="badge '+(BADGE_CLASS[o.status]||'bg-secondary-lt')+'">'+(STATUS_JA[o.status]||o.status)+'</span></td><td>'+timeAgo(o.sent_at||o.created_at)+'</td></tr>';
    }).join('');
  });
}

// ── インポート ──
var dz = document.getElementById('drop-zone');
dz.addEventListener('dragover',function(e){e.preventDefault();dz.classList.add('drag-over');});
dz.addEventListener('dragleave',function(){dz.classList.remove('drag-over');});
dz.addEventListener('drop',function(e){e.preventDefault();dz.classList.remove('drag-over');if(e.dataTransfer.files.length)handleFile(e.dataTransfer.files[0]);});

function handleFile(file){
  if(!file) return;
  var formData = new FormData();
  formData.append('file', file);
  dz.innerHTML = '<div style="font-size:2.5rem;opacity:.3;animation:spin 1s linear infinite;margin-bottom:16px;">&#8635;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">インポート中...</h3>';
  fetch(API+'/import',{method:'POST',headers:headersFile(),body:formData})
    .then(function(r){return r.json();})
    .then(function(res){
      dz.innerHTML = '<div style="font-size:2.5rem;opacity:.3;margin-bottom:16px;">&#10003;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">インポート完了</h3><p class="text-muted small">クリックして別のファイルをインポート</p>';
      var result = document.getElementById('import-result');
      result.style.display = 'block';
      result.innerHTML = '<div class="card-body"><p><strong>'+(res.imported||0)+'</strong> 件のカフェをインポートしました</p><p class="text-muted small">'+(res.skipped||0)+' 件スキップ</p>'+((res.errors||[]).length?'<p class="text-danger small mt-2">エラー: '+res.errors.slice(0,5).join(', ')+'</p>':'')+'</div>';
    })
    .catch(function(){
      dz.innerHTML = '<div style="font-size:2.5rem;color:#c0392b;margin-bottom:16px;">&#10007;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">インポート失敗</h3><p class="text-muted small">クリックして再試行</p>';
    });
}

// ── 発見 ──
function runDiscover(){
  var region = document.getElementById('disc-region').value;
  var city = document.getElementById('disc-city').value;
  var result = document.getElementById('disc-result');
  result.textContent = '検索中...';

  var url = API+'/discover?';
  if(city) url += 'city='+encodeURIComponent(city)+'&region='+(region||'us_west');
  else if(region) url += 'region='+region;
  else {result.textContent='リージョンを選択するか、都市名を入力してください。';return;}

  fetch(url,{method:'POST',headers:headers()})
    .then(function(r){return r.json();})
    .then(function(data){
      result.textContent = data.error || (data.found||0)+' 件の新しいカフェを発見しました！';
      if(data.found > 0) setTimeout(function(){loadLeads();},500);
    })
    .catch(function(){result.textContent='検索に失敗しました。Google Places APIキーを確認してください。';});
}

// ── パイプライン ──
function runPipeline(){
  if(!confirm('B2Bパイプラインを今すぐ実行しますか？')) return;
  fetch(API+'/pipeline/run',{method:'POST',headers:headers()})
    .then(function(r){return r.json();})
    .then(function(){alert('パイプラインを開始しました。数分後に結果を確認してください。');});
}

// ── 設定 ──
var currentStep = 1;
var templates = {};

function loadSettings(){
  fetch(API+'/stats',{headers:headers()}).then(function(r){return r.json();}).then(function(s){
    document.getElementById('cfg-limit').textContent = '333 通/日';
    document.getElementById('cfg-from').textContent = 'wholesale@nakaimatcha.com';
    document.getElementById('cfg-gp').textContent = s.total_leads > 0 ? '接続済' : '未設定';
    document.getElementById('cfg-resend').textContent = s.total_sent > 0 ? '接続済' : '環境変数を確認';
  });
  loadTemplates();
  loadPdfStatus();
}

function loadTemplates(){
  fetch(API+'/sequences',{headers:headers()}).then(function(r){return r.json();}).then(function(data){
    templates = {};
    (data||[]).forEach(function(s){ templates[s.step_number] = s; });
    showTemplate(currentStep);
  });
}

function showTemplate(step){
  currentStep = step;
  [1,2,3].forEach(function(s){
    var btn = document.getElementById('tpl-btn-'+s);
    if(s===step){btn.className='btn btn-sm btn-primary';}
    else{btn.className='btn btn-sm btn-outline-secondary';}
  });
  var tpl = templates[step] || {};
  document.getElementById('tpl-subject').value = tpl.subject_template || '';
  document.getElementById('tpl-body').value = tpl.body_template || '';
  document.getElementById('tpl-msg').textContent = '';
}

function saveTemplate(){
  var subject = document.getElementById('tpl-subject').value;
  var body = document.getElementById('tpl-body').value;
  fetch(API+'/sequences/'+currentStep,{
    method:'PUT',
    headers:headers(),
    body:JSON.stringify({subject_template:subject, body_template:body})
  }).then(function(r){return r.json();}).then(function(){
    document.getElementById('tpl-msg').textContent = '保存しました';
    if(templates[currentStep]) {
      templates[currentStep].subject_template = subject;
      templates[currentStep].body_template = body;
    }
    setTimeout(function(){document.getElementById('tpl-msg').textContent='';},3000);
  }).catch(function(){document.getElementById('tpl-msg').textContent='保存に失敗しました';document.getElementById('tpl-msg').style.color='#c0392b';});
}

function sendTest(){
  var email = document.getElementById('test-email').value;
  var step = parseInt(document.getElementById('test-step').value);
  var msg = document.getElementById('test-msg');
  if(!email){msg.textContent='メールアドレスを入力してください';msg.style.color='#c0392b';return;}
  msg.textContent='送信中...';msg.style.color='#888';
  fetch(API+'/test-send',{
    method:'POST',
    headers:headers(),
    body:JSON.stringify({to_email:email, step:step, cafe_name:'Sample Cafe', city:'Portland', cafe_type:'specialty'})
  }).then(function(r){return r.json();}).then(function(data){
    if(data.ok){msg.textContent='テスト送信しました: '+data.subject;msg.style.color='#406546';}
    else{msg.textContent='送信に失敗しました: '+(data.error||data.detail||'不明なエラー');msg.style.color='#c0392b';}
  }).catch(function(e){msg.textContent='送信に失敗しました: '+e.message;msg.style.color='#c0392b';});
}

function loadPdfStatus(){
  fetch(API+'/attachment',{headers:headers()}).then(function(r){return r.json();}).then(function(data){
    var el = document.getElementById('pdf-status');
    var rmBtn = document.getElementById('pdf-remove-btn');
    if(data.filename){
      el.innerHTML='<span class="small">現在の添付: <strong>'+esc(data.filename)+'</strong></span>';
      rmBtn.style.display='inline-block';
    } else {
      el.innerHTML='<span class="text-muted small">添付ファイルなし</span>';
      rmBtn.style.display='none';
    }
  });
}

function uploadPdf(file){
  if(!file) return;
  var msg = document.getElementById('pdf-msg');
  msg.textContent='アップロード中...';
  var formData = new FormData();
  formData.append('file', file);
  fetch(API+'/attachment/upload',{method:'POST',headers:headersFile(),body:formData})
    .then(function(r){return r.json();})
    .then(function(data){
      if(data.ok){msg.textContent=data.filename+' ('+data.size_kb+'KB)';loadPdfStatus();}
      else{msg.textContent='アップロード失敗';msg.style.color='#c0392b';}
    })
    .catch(function(){msg.textContent='アップロード失敗';msg.style.color='#c0392b';});
}

function removePdf(){
  if(!confirm('添付ファイルを削除しますか？')) return;
  fetch(API+'/attachment',{method:'DELETE',headers:headers()}).then(function(){loadPdfStatus();});
  document.getElementById('pdf-msg').textContent='';
}

// ── Resend ドメイン確認 ──
function checkResendDomain(){
  var el = document.getElementById('resend-domain-status');
  el.innerHTML='<p class="text-muted small">確認中...</p>';
  fetch(API+'/resend-domain',{headers:headers()}).then(function(r){return r.json();}).then(function(data){
    if(!data.ok){
      el.innerHTML='<p class="text-danger small">'+esc(data.error)+'</p>';
      return;
    }
    var statusColor = data.status==='verified'?'#406546':'#e67e22';
    var statusText = data.status==='verified'?'認証済み':'未認証 ('+data.status+')';
    var html = '<p class="mb-3"><strong>'+esc(data.domain)+'</strong> &mdash; <span style="color:'+statusColor+';font-weight:600;">'+statusText+'</span></p>';

    if(data.records && data.records.length>0 && data.status!=='verified'){
      html += '<p class="text-muted small mb-3">以下のレコードを <strong>Shopify &gt; Settings &gt; Domains &gt; nakaimatcha.com &gt; DNS settings &gt; Add custom record</strong> に追加してください：</p>';
      html += '<div class="table-responsive"><table class="table table-vcenter table-bordered small"><thead><tr><th>Type</th><th>Name (Shopifyに入力)</th><th>Value (コピー)</th><th>状態</th></tr></thead><tbody>';
      data.records.forEach(function(r){
        var name = (r.name||r.record||'').replace('.nakaimatcha.com','');
        var val = r.value||r.data||'';
        var recType = r.record_type||r.type||'';
        var recStatus = r.status==='verified'?'<span style="color:#406546;">OK</span>':'<span style="color:#e67e22;">未設定</span>';
        html += '<tr><td><strong>'+esc(recType)+'</strong></td>';
        html += '<td style="font-family:monospace;font-size:.75rem;word-break:break-all;">'+esc(name)+'</td>';
        html += '<td class="copy-val" style="font-family:monospace;font-size:.75rem;word-break:break-all;cursor:pointer;" data-val="'+esc(val)+'" title="クリックでコピー">'+esc(val)+'</td>';
        html += '<td class="text-center">'+recStatus+'</td></tr>';
      });
      html += '</tbody></table></div>';
      html += '<p class="text-muted" style="font-size:.78rem;">Value 列をクリックするとコピーできます。全レコードを Shopify に追加後、再度「認証状態を確認」を押してください。</p>';
    } else if(!data.records || data.records.length===0){
      html += '<p class="text-warning small">DNS レコードが取得できませんでした。Resend のドメインページを確認してください。</p>';
    } else if(data.status==='verified'){
      html += '<p style="color:#406546;" class="small">ドメイン認証完了。メール送信が可能です。</p>';
    }
    el.innerHTML = html;
    el.querySelectorAll('.copy-val').forEach(function(td){
      td.addEventListener('click',function(){
        navigator.clipboard.writeText(td.dataset.val);
        td.style.background='#e8f5e9';
        setTimeout(function(){td.style.background='';},1000);
      });
    });
  }).catch(function(e){el.innerHTML='<p class="text-danger small">エラー: '+e.message+'</p>';});
}

// ── ヘルパー ──
function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):'';}

function timeAgo(ts){
  if(!ts) return '-';
  var d = new Date(ts);
  var diff = (Date.now()-d.getTime())/1000;
  if(diff<60) return 'たった今';
  if(diff<3600) return Math.floor(diff/60)+'分前';
  if(diff<86400) return Math.floor(diff/3600)+'時間前';
  if(diff<2592000) return Math.floor(diff/86400)+'日前';
  return Math.floor(diff/2592000)+'ヶ月前';
}

// 初期化
setTimeout(loadSettings, 100);
</script>
</body>
</html>"""


@b2b_page_router.get("/b2b", response_class=HTMLResponse)
async def b2b_dashboard():
    return B2B_HTML
