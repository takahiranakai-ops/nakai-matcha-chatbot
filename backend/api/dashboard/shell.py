"""Dashboard shell — shared CSS, sidebar, login, navigation JS."""

SHELL_CSS = """
:root{
  --tblr-primary:#406546;
  --tblr-primary-rgb:64,101,70;
  --tblr-font-sans-serif:'Work Sans','Shippori Mincho',system-ui,sans-serif;
  --tblr-body-bg:#f8f7f4;
  --dash-sidebar:260px;
}
body{font-family:var(--tblr-font-sans-serif);background:var(--tblr-body-bg);margin:0}

/* Login */
#dash-login{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#F9F0E2}
.login-card{background:#fff;padding:48px 40px;border-radius:20px;box-shadow:0 8px 40px rgba(0,0,0,.08);text-align:center;max-width:380px;width:90%}
.login-card .brand{font-size:.7rem;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#888;margin-bottom:6px}
.login-card h2{font-size:1.05rem;font-weight:400;color:#555;margin-bottom:28px}
.login-card input{width:100%;padding:12px 16px;border:1px solid #ddd;border-radius:10px;font-size:1rem;outline:none;margin-bottom:14px;font-family:var(--tblr-font-sans-serif)}
.login-card input:focus{border-color:var(--tblr-primary)}
.login-card button{width:100%;padding:13px;background:var(--tblr-primary);color:#fff;border:none;border-radius:10px;font-size:.9rem;font-weight:500;cursor:pointer;font-family:var(--tblr-font-sans-serif);transition:opacity .15s}
.login-card button:hover{opacity:.9}
.login-card .err{color:#c0392b;font-size:.82rem;margin-top:8px;display:none}

/* Sidebar */
.dash-sidebar{position:fixed;top:0;left:0;bottom:0;width:var(--dash-sidebar);background:#fff;border-right:1px solid #e8e8e8;display:flex;flex-direction:column;z-index:50;transition:transform .25s ease}
.dash-sidebar .logo{padding:24px 20px 8px;border-bottom:1px solid #f0f0f0}
.dash-sidebar .logo .brand{font-size:.65rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#888}
.dash-sidebar .logo h1{font-size:.95rem;font-weight:500;color:#333;margin:4px 0 0}
.dash-sidebar nav{flex:1;padding:16px 12px;overflow-y:auto}
.dash-sidebar .nav-item{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;cursor:pointer;font-size:.85rem;font-weight:400;color:#555;transition:all .15s;margin-bottom:2px}
.dash-sidebar .nav-item:hover{background:rgba(64,101,70,.06);color:#333}
.dash-sidebar .nav-item.active{background:rgba(64,101,70,.1);color:var(--tblr-primary);font-weight:500}
.dash-sidebar .nav-item i{font-size:1.1rem;width:20px;text-align:center;flex-shrink:0}
.dash-sidebar .nav-sep{height:1px;background:#f0f0f0;margin:12px 14px}
.dash-sidebar .nav-link-ext{display:flex;align-items:center;gap:10px;padding:8px 14px;font-size:.78rem;color:#999;text-decoration:none;transition:color .15s}
.dash-sidebar .nav-link-ext:hover{color:var(--tblr-primary)}
.dash-sidebar .nav-link-ext i{font-size:.9rem;width:20px;text-align:center}

/* Main */
.dash-main{margin-left:var(--dash-sidebar);min-height:100vh;padding:0}
.dash-topbar{display:none;background:var(--tblr-primary);color:#fff;padding:10px 16px;position:sticky;top:0;z-index:40}
.dash-topbar button{background:none;border:none;color:#fff;font-size:1.3rem;cursor:pointer;padding:4px}
.dash-topbar .title{font-size:.8rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;margin-left:12px}
.dash-content{padding:24px;max-width:1400px}

/* Mobile */
.dash-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:45}
@media(max-width:900px){
  .dash-sidebar{transform:translateX(-100%)}
  .dash-sidebar.open{transform:translateX(0)}
  .dash-overlay.open{display:block}
  .dash-main{margin-left:0}
  .dash-topbar{display:flex;align-items:center}
}

/* Shared section styles */
.kpi-value{font-size:1.8rem;font-weight:300;color:#406546}
.kpi-label{font-size:.72rem;font-weight:600;letter-spacing:.08em;color:#888;margin-bottom:4px}
.kpi-sub{font-size:.75rem;color:#888;margin-top:2px}
.skeleton{background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.skeleton-kpi{height:100px;border-radius:12px}
.skeleton-row{height:42px;margin-bottom:4px;border-radius:4px}
.skeleton-chart{height:200px;border-radius:8px}
.btn-loading{position:relative;pointer-events:none;opacity:.7}
.btn-loading::after{content:'';display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite;margin-left:8px;vertical-align:middle}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
.chart-bar-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.chart-bar-label{font-size:.7rem;color:#888;width:80px;text-align:right;flex-shrink:0}
.chart-bar{height:22px;border-radius:4px;transition:width .5s;min-width:2px}
.chart-bar-val{font-size:.7rem;color:#888;flex-shrink:0}
.seg-card{border-radius:12px;cursor:default;transition:box-shadow .2s}
.seg-card:hover{box-shadow:0 4px 12px rgba(0,0,0,.08)}
.seg-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;color:#fff}
.drop-zone{border:2px dashed #d0d0d0;border-radius:16px;padding:64px 32px;text-align:center;cursor:pointer;transition:all .3s;background:#fff}
.drop-zone:hover,.drop-zone.drag-over{border-color:#406546;background:#f8fdf8}
.seg-tab{cursor:pointer;padding:6px 16px;border-radius:8px;font-size:.82rem;font-weight:500;border:1px solid #d0d0d0;background:#fff;color:#666;transition:all .2s}
.seg-tab.active{background:#406546;color:#fff;border-color:#406546}
.nav-tabs .nav-link{font-size:.82rem;font-weight:500;color:#888}
.nav-tabs .nav-link.active{color:#406546;border-bottom-color:#406546}
.tab-pane{display:none;padding:28px 0}
.tab-pane.active{display:block}

/* Email section styles */
.em-badge{padding:3px 10px;border-radius:12px;font-size:.72rem;font-weight:600}
.em-badge-draft{background:rgba(102,102,102,.12);color:#666}
.em-badge-generating{background:rgba(52,152,219,.12);color:#2980b9}
.em-badge-ready{background:rgba(46,204,113,.12);color:#27ae60}
.em-badge-sending{background:rgba(243,156,18,.12);color:#f39c12}
.em-badge-sent{background:rgba(64,101,70,.12);color:#406546}
.em-badge-failed{background:rgba(192,57,43,.12);color:#c0392b}
.em-badge-active{background:rgba(64,101,70,.12);color:#406546}
.em-badge-inactive{background:rgba(192,57,43,.12);color:#c0392b}
.editor-layout{display:grid;grid-template-columns:1fr 380px;gap:24px;margin-top:16px}
@media(max-width:900px){.editor-layout{grid-template-columns:1fr}}
.preview-frame{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden}
.preview-frame iframe{width:100%;min-height:600px;border:none}
.editor-panel{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.editor-panel h4{font-size:.9rem;font-weight:600;color:#406546;margin-bottom:16px}
.edit-block{margin-bottom:16px}
.edit-block label{display:block;font-size:.78rem;font-weight:500;color:#888;margin-bottom:4px;text-transform:capitalize}
.edit-block textarea,.edit-block input{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:.88rem;font-family:var(--tblr-font-sans-serif);resize:vertical;min-height:60px;outline:none}
.edit-block textarea:focus,.edit-block input:focus{border-color:#406546}
.schedule-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-bottom:24px}
.sched-card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
.sched-card h4{font-size:.95rem;font-weight:600;color:#333;margin-bottom:8px}
.sched-card .meta{font-size:.78rem;color:#888;line-height:1.6}
.toggle{position:relative;width:40px;height:22px;background:#ccc;border-radius:11px;cursor:pointer;transition:background .2s}
.toggle.on{background:#406546}
.toggle::after{content:'';position:absolute;top:2px;left:2px;width:18px;height:18px;background:#fff;border-radius:50%;transition:transform .2s}
.toggle.on::after{transform:translateX(18px)}
.day-checks{display:flex;gap:4px;margin:8px 0}
.day-check{width:28px;height:28px;border-radius:50%;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;font-size:.68rem;color:#888;cursor:pointer;font-family:var(--tblr-font-sans-serif)}
.day-check.sel{background:#406546;color:#fff;border-color:#406546}
.color-row{display:flex;gap:16px;flex-wrap:wrap}
.color-item{display:flex;align-items:center;gap:8px}
.color-item input[type=color]{width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0}
.photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:12px;margin-top:12px}
.photo-card{position:relative;border-radius:8px;overflow:hidden;aspect-ratio:1;background:#f5f5f5}
.photo-card img{width:100%;height:100%;object-fit:cover}
.photo-card .del-btn{position:absolute;top:4px;right:4px;background:rgba(0,0,0,.6);color:#fff;border:none;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:.7rem;display:flex;align-items:center;justify-content:center}

/* Admin section styles */
.ad-panel{display:none;padding:24px 0}
.ad-panel.active{display:block}
.msg-viewer{background:#fff;border-radius:8px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,.06);max-height:500px;overflow-y:auto}
.msg-item{padding:10px 14px;border-radius:12px;margin-bottom:8px;max-width:80%;font-size:.88rem;line-height:1.6;white-space:pre-wrap}
.msg-user{background:#406546;color:#fff;margin-left:auto;border-radius:12px 12px 4px 12px}
.msg-assistant{background:#f5f5f5;color:#333;border-radius:4px 12px 12px 12px}
.msg-meta{font-size:.7rem;color:#888;margin-top:4px}
.breakdown-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:.88rem}
.stat-card{background:#fff;padding:24px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.stat-card .label{font-size:.75rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:#888;margin-bottom:4px}
.stat-card .value{font-size:1.8rem;font-weight:600;color:#406546}
.ad-badge{padding:3px 8px;border-radius:4px;font-size:.72rem;font-weight:600}
.ad-badge-active{background:rgba(64,101,70,.1);color:#406546}
.ad-badge-inactive{background:rgba(192,57,43,.1);color:#c0392b}

/* Sub-tabs (email, content, analytics sections) */
.sub-tabs{display:flex;border-bottom:2px solid #eee;background:#fff;padding:0 4px;margin:-24px -24px 24px;border-radius:0}
.sub-tab{padding:12px 18px;font-size:.82rem;font-weight:500;color:#888;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s}
.sub-tab:hover{color:#555}
.sub-tab.active{color:#406546;border-bottom-color:#406546}
.sub-panel{display:none}
.sub-panel.active{display:block}

/* Email editor layout */
.em-editor-layout{display:grid;grid-template-columns:1fr 380px;gap:24px;margin-top:16px}
@media(max-width:900px){.em-editor-layout{grid-template-columns:1fr}}
.em-preview-frame{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden}
.em-editor-panel{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}

/* Section loading */
.section-loading{display:flex;align-items:center;justify-content:center;min-height:300px;color:#888;font-size:.9rem}
"""

SHELL_LOGIN = """
<div id="dash-login">
  <div class="login-card">
    <div class="brand">NAKAI</div>
    <h2>Management Console</h2>
    <input type="password" id="dash-pw" placeholder="Admin password" onkeydown="if(event.key==='Enter')dashLogin()">
    <button onclick="dashLogin()">Sign In</button>
    <div class="err" id="dash-err">Invalid password</div>
  </div>
</div>
"""

SHELL_SIDEBAR = """
<div class="dash-overlay" id="dash-overlay" onclick="closeSidebar()"></div>
<aside class="dash-sidebar" id="dash-sidebar">
  <div class="logo">
    <div class="brand">NAKAI</div>
    <h1>Management Console</h1>
  </div>
  <nav>
    <div class="nav-item active" data-sec="home" onclick="showSection('home')">
      <i class="ti ti-home"></i> Home
    </div>
    <div class="nav-item" data-sec="b2b" onclick="showSection('b2b')">
      <i class="ti ti-users-group"></i> B2B Sales Team
    </div>
    <div class="nav-item" data-sec="email" onclick="showSection('email')">
      <i class="ti ti-mail"></i> Email Marketing
    </div>
    <div class="nav-item" data-sec="content" onclick="showSection('content')">
      <i class="ti ti-book"></i> Content
    </div>
    <div class="nav-item" data-sec="analytics" onclick="showSection('analytics')">
      <i class="ti ti-chart-bar"></i> Analytics
    </div>
    <div class="nav-sep"></div>
    <a class="nav-link-ext" href="/app" target="_blank"><i class="ti ti-external-link"></i> Matcha Concierge</a>
    <a class="nav-link-ext" href="/admin"><i class="ti ti-settings"></i> Legacy Admin</a>
  </nav>
</aside>
"""

SHELL_JS = """
<script>
var DASH_PWD = '';
var currentSection = '';
var sectionLoaded = {};

function dashLogin() {
  var pw = document.getElementById('dash-pw').value;
  if (!pw) { document.getElementById('dash-err').style.display = 'block'; return; }
  fetch('/api/b2b/stats', {headers: {'X-Admin-Password': pw}})
    .then(function(r) {
      if (!r.ok) throw new Error();
      DASH_PWD = pw;
      sessionStorage.setItem('nakai-admin-pwd', pw);
      // Also set the old key for backward compat
      sessionStorage.setItem('nakai_admin_pw', pw);
      document.getElementById('dash-login').style.display = 'none';
      document.getElementById('dash-app').style.display = 'block';
      showSection(location.hash.replace('#','') || 'home');
    })
    .catch(function() {
      document.getElementById('dash-err').style.display = 'block';
    });
}

// Auto-login from session
(function() {
  var pw = sessionStorage.getItem('nakai-admin-pwd') || sessionStorage.getItem('nakai_admin_pw');
  if (pw) {
    DASH_PWD = pw;
    fetch('/api/b2b/stats', {headers: {'X-Admin-Password': pw}})
      .then(function(r) {
        if (!r.ok) throw new Error();
        document.getElementById('dash-login').style.display = 'none';
        document.getElementById('dash-app').style.display = 'block';
        showSection(location.hash.replace('#','') || 'home');
      })
      .catch(function() {});
  }
})();

function showSection(name) {
  if (!name) name = 'home';
  currentSection = name;
  location.hash = name;

  // Update sidebar active state
  document.querySelectorAll('.dash-sidebar .nav-item').forEach(function(el) {
    el.classList.toggle('active', el.dataset.sec === name);
  });

  // Update mobile topbar title
  var titles = {home:'Home',b2b:'B2B Sales Team',email:'Email Marketing',content:'Content',analytics:'Analytics'};
  var titleEl = document.getElementById('dash-topbar-title');
  if (titleEl) titleEl.textContent = titles[name] || name;

  // Hide all sections, show target
  document.querySelectorAll('.dash-section').forEach(function(s) { s.style.display = 'none'; });
  var el = document.getElementById('sec-' + name);
  if (el) {
    el.style.display = 'block';
    window.dispatchEvent(new CustomEvent('dashboard:section', {detail: name}));
    closeSidebar();
    return;
  }

  // Create and load section
  var container = document.createElement('div');
  container.id = 'sec-' + name;
  container.className = 'dash-section';
  container.innerHTML = '<div class="section-loading">Loading...</div>';
  document.getElementById('dash-content').appendChild(container);
  container.style.display = 'block';

  fetch('/api/dashboard/section/' + name, {
    headers: {'X-Admin-Password': DASH_PWD}
  })
    .then(function(r) { return r.text(); })
    .then(function(html) {
      container.innerHTML = html;
      // Execute script tags
      container.querySelectorAll('script').forEach(function(old) {
        var s = document.createElement('script');
        s.textContent = old.textContent;
        old.parentNode.replaceChild(s, old);
      });
    })
    .catch(function() {
      container.innerHTML = '<div class="section-loading" style="color:#c0392b">Failed to load section</div>';
    });

  closeSidebar();
}

function closeSidebar() {
  document.getElementById('dash-sidebar').classList.remove('open');
  document.getElementById('dash-overlay').classList.remove('open');
}
function openSidebar() {
  document.getElementById('dash-sidebar').classList.add('open');
  document.getElementById('dash-overlay').classList.add('open');
}

// Hash navigation
window.addEventListener('hashchange', function() {
  var sec = location.hash.replace('#','');
  if (sec && sec !== currentSection) showSection(sec);
});
</script>
"""
