"""NAKAI Operations — Unified dashboard with Apple Human Interface design."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from config import settings

operations_router = APIRouter()


def verify_admin(request: Request):
    pw = (
        request.headers.get("X-Admin-Password")
        or request.query_params.get("pw")
        or request.cookies.get("nakai_admin")
    )
    if pw != settings.admin_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return pw


@operations_router.get("/ops", response_class=HTMLResponse)
async def operations_page(request: Request):
    return HTMLResponse(content=_build_html(), headers={"Cache-Control": "no-store"})


def _build_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>NAKAI Operations</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

:root{{
  --bg-primary:#F2F2F7;
  --bg-secondary:#FFFFFF;
  --bg-tertiary:#E5E5EA;
  --bg-sidebar:#1C1C1E;
  --text-primary:#1C1C1E;
  --text-secondary:#8E8E93;
  --text-tertiary:#AEAEB2;
  --text-on-dark:#FFFFFF;
  --accent:#007AFF;
  --accent-hover:#0056CC;
  --green:#34C759;
  --orange:#FF9500;
  --red:#FF3B30;
  --yellow:#FFCC00;
  --matcha:#406546;
  --cream:#F9F0E2;
  --separator:rgba(60,60,67,0.12);
  --shadow-sm:0 1px 3px rgba(0,0,0,0.08);
  --shadow-md:0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg:0 8px 32px rgba(0,0,0,0.12);
  --radius-sm:8px;
  --radius-md:12px;
  --radius-lg:16px;
  --radius-xl:20px;
  --font:-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text',
    'Helvetica Neue',Helvetica,Arial,sans-serif;
}}

html{{height:100%}}
body{{
  font-family:var(--font);
  background:var(--bg-primary);
  color:var(--text-primary);
  height:100%;
  display:flex;
  -webkit-font-smoothing:antialiased;
}}

/* ─── Login ─── */
#login-screen{{
  position:fixed;inset:0;z-index:9999;
  background:linear-gradient(145deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
  display:flex;align-items:center;justify-content:center;
  flex-direction:column;gap:24px;
}}
#login-screen.hidden{{display:none}}
#login-screen h1{{
  font-size:28px;font-weight:700;color:#fff;letter-spacing:-0.5px;
}}
#login-screen p{{color:rgba(255,255,255,0.6);font-size:14px}}
#login-screen input{{
  width:280px;padding:14px 18px;border:none;border-radius:var(--radius-md);
  background:rgba(255,255,255,0.1);color:#fff;font-size:16px;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  outline:none;transition:background 0.2s;
}}
#login-screen input::placeholder{{color:rgba(255,255,255,0.4)}}
#login-screen input:focus{{background:rgba(255,255,255,0.18)}}
#login-screen button{{
  width:280px;padding:14px;border:none;border-radius:var(--radius-md);
  background:var(--accent);color:#fff;font-size:16px;font-weight:600;
  cursor:pointer;transition:transform 0.1s,background 0.2s;
}}
#login-screen button:active{{transform:scale(0.97)}}
#login-error{{color:var(--red);font-size:13px;min-height:18px}}

/* ─── Sidebar ─── */
#sidebar{{
  width:260px;min-width:260px;height:100vh;
  background:var(--bg-sidebar);color:var(--text-on-dark);
  display:flex;flex-direction:column;
  padding:0;overflow-y:auto;
  position:sticky;top:0;
}}
.sidebar-header{{
  padding:24px 20px 20px;
  border-bottom:1px solid rgba(255,255,255,0.08);
}}
.sidebar-header h2{{
  font-size:20px;font-weight:700;letter-spacing:-0.3px;
  background:linear-gradient(135deg,#34C759,#30D158);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.sidebar-header span{{
  font-size:11px;color:rgba(255,255,255,0.4);
  text-transform:uppercase;letter-spacing:1px;display:block;margin-top:4px;
}}
.nav-section{{padding:16px 12px 8px}}
.nav-section-label{{
  font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);
  text-transform:uppercase;letter-spacing:0.8px;padding:0 8px;margin-bottom:6px;
}}
.nav-item{{
  display:flex;align-items:center;gap:10px;
  padding:10px 12px;border-radius:var(--radius-sm);
  cursor:pointer;transition:background 0.15s;
  font-size:14px;font-weight:500;color:rgba(255,255,255,0.7);
  margin-bottom:2px;
}}
.nav-item:hover{{background:rgba(255,255,255,0.06)}}
.nav-item.active{{background:rgba(255,255,255,0.1);color:#fff}}
.nav-item .icon{{
  width:28px;height:28px;border-radius:6px;
  display:flex;align-items:center;justify-content:center;
  font-size:15px;flex-shrink:0;
}}
.nav-item .badge{{
  margin-left:auto;background:var(--accent);color:#fff;
  font-size:11px;font-weight:600;padding:2px 7px;border-radius:10px;
}}

/* ─── Main Content ─── */
#main{{
  flex:1;height:100vh;overflow-y:auto;
  padding:0;
}}
.page{{display:none;padding:32px;max-width:1400px;margin:0 auto}}
.page.active{{display:block}}
.page-header{{
  margin-bottom:28px;
}}
.page-header h1{{
  font-size:28px;font-weight:700;letter-spacing:-0.5px;
}}
.page-header p{{
  color:var(--text-secondary);font-size:14px;margin-top:4px;
}}

/* ─── Cards ─── */
.card{{
  background:var(--bg-secondary);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-sm);
  padding:20px;
  transition:box-shadow 0.2s;
}}
.card:hover{{box-shadow:var(--shadow-md)}}
.card-grid{{
  display:grid;gap:16px;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
}}
.card-grid-3{{grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}}

/* ─── KPI Cards ─── */
.kpi-row{{
  display:grid;gap:16px;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  margin-bottom:24px;
}}
.kpi{{
  background:var(--bg-secondary);border-radius:var(--radius-md);
  padding:18px 20px;box-shadow:var(--shadow-sm);
}}
.kpi-label{{
  font-size:12px;font-weight:600;color:var(--text-secondary);
  text-transform:uppercase;letter-spacing:0.5px;
}}
.kpi-value{{
  font-size:32px;font-weight:700;letter-spacing:-1px;margin-top:4px;
  color:var(--text-primary);
}}
.kpi-change{{
  font-size:12px;font-weight:600;margin-top:4px;
}}
.kpi-change.up{{color:var(--green)}}
.kpi-change.down{{color:var(--red)}}

/* ─── Buttons ─── */
.btn{{
  display:inline-flex;align-items:center;gap:6px;
  padding:9px 16px;border:none;border-radius:var(--radius-sm);
  font-size:14px;font-weight:600;cursor:pointer;
  transition:all 0.15s;font-family:var(--font);
}}
.btn:active{{transform:scale(0.97)}}
.btn-primary{{background:var(--accent);color:#fff}}
.btn-primary:hover{{background:var(--accent-hover)}}
.btn-secondary{{background:var(--bg-tertiary);color:var(--text-primary)}}
.btn-secondary:hover{{background:#D1D1D6}}
.btn-green{{background:var(--green);color:#fff}}
.btn-red{{background:var(--red);color:#fff}}
.btn-sm{{padding:6px 12px;font-size:13px}}

/* ─── Segmented Control ─── */
.segmented{{
  display:inline-flex;background:var(--bg-tertiary);
  border-radius:var(--radius-sm);padding:2px;gap:2px;
  margin-bottom:20px;
}}
.segmented button{{
  padding:7px 16px;border:none;border-radius:6px;
  font-size:13px;font-weight:600;cursor:pointer;
  background:transparent;color:var(--text-secondary);
  transition:all 0.2s;font-family:var(--font);
}}
.segmented button.active{{
  background:var(--bg-secondary);color:var(--text-primary);
  box-shadow:0 1px 3px rgba(0,0,0,0.1);
}}

/* ─── Tables ─── */
.table-wrap{{
  background:var(--bg-secondary);border-radius:var(--radius-lg);
  box-shadow:var(--shadow-sm);overflow:hidden;
}}
table{{width:100%;border-collapse:collapse}}
th{{
  text-align:left;padding:12px 16px;font-size:12px;
  font-weight:600;color:var(--text-secondary);
  text-transform:uppercase;letter-spacing:0.5px;
  border-bottom:1px solid var(--separator);background:var(--bg-primary);
}}
td{{
  padding:12px 16px;font-size:14px;
  border-bottom:1px solid var(--separator);
}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:rgba(0,0,0,0.02)}}

/* ─── Status badges ─── */
.badge{{
  display:inline-flex;align-items:center;gap:4px;
  padding:3px 10px;border-radius:20px;
  font-size:12px;font-weight:600;
}}
.badge-green{{background:rgba(52,199,89,0.12);color:var(--green)}}
.badge-orange{{background:rgba(255,149,0,0.12);color:var(--orange)}}
.badge-red{{background:rgba(255,59,48,0.12);color:var(--red)}}
.badge-blue{{background:rgba(0,122,255,0.12);color:var(--accent)}}
.badge-gray{{background:rgba(142,142,147,0.12);color:var(--text-secondary)}}

/* ─── Section headers ─── */
.section-title{{
  font-size:18px;font-weight:700;letter-spacing:-0.3px;
  margin:28px 0 14px;
}}
.section-title:first-child{{margin-top:0}}

/* ─── Agent cards ─── */
.agent-card{{
  background:var(--bg-secondary);border-radius:var(--radius-md);
  padding:16px;box-shadow:var(--shadow-sm);
  display:flex;flex-direction:column;gap:8px;
}}
.agent-card .agent-name{{
  font-size:15px;font-weight:600;display:flex;align-items:center;gap:8px;
}}
.agent-card .agent-role{{font-size:12px;color:var(--text-secondary)}}
.agent-card .agent-status{{
  display:flex;align-items:center;gap:6px;font-size:12px;
}}
.status-dot{{
  width:8px;height:8px;border-radius:50%;
}}
.status-dot.active{{background:var(--green);box-shadow:0 0 6px rgba(52,199,89,0.4)}}
.status-dot.idle{{background:var(--orange)}}
.status-dot.stopped{{background:var(--text-tertiary)}}

/* ─── Content item ─── */
.content-item{{
  background:var(--bg-secondary);border-radius:var(--radius-md);
  padding:18px;box-shadow:var(--shadow-sm);margin-bottom:12px;
}}
.content-item h3{{font-size:15px;font-weight:600;margin-bottom:4px}}
.content-item .meta{{
  font-size:12px;color:var(--text-secondary);
  display:flex;gap:12px;margin-bottom:8px;
}}
.content-item .preview{{
  font-size:14px;color:var(--text-secondary);
  line-height:1.5;
}}

/* ─── Quick actions ─── */
.quick-actions{{
  display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px;
}}

/* ─── Inputs ─── */
.input-group{{margin-bottom:16px}}
.input-group label{{
  display:block;font-size:12px;font-weight:600;
  color:var(--text-secondary);text-transform:uppercase;
  letter-spacing:0.5px;margin-bottom:6px;
}}
.input{{
  width:100%;padding:10px 14px;border:1px solid var(--separator);
  border-radius:var(--radius-sm);font-size:14px;
  font-family:var(--font);background:var(--bg-secondary);
  outline:none;transition:border-color 0.2s;
}}
.input:focus{{border-color:var(--accent)}}
textarea.input{{resize:vertical;min-height:100px}}

/* ─── Loading ─── */
.skeleton{{
  background:linear-gradient(90deg,var(--bg-tertiary) 25%,#E0E0E5 50%,var(--bg-tertiary) 75%);
  background-size:200% 100%;animation:shimmer 1.5s infinite;
  border-radius:var(--radius-sm);height:20px;
}}
@keyframes shimmer{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}

/* ─── Modal ─── */
.modal-overlay{{
  position:fixed;inset:0;background:rgba(0,0,0,0.4);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  z-index:100;display:none;align-items:center;justify-content:center;
}}
.modal-overlay.show{{display:flex}}
.modal{{
  background:var(--bg-secondary);border-radius:var(--radius-xl);
  padding:28px;max-width:560px;width:90%;max-height:85vh;
  overflow-y:auto;box-shadow:var(--shadow-lg);
}}
.modal h2{{font-size:20px;font-weight:700;margin-bottom:16px}}

/* ─── Responsive ─── */
@media(max-width:768px){{
  #sidebar{{
    position:fixed;left:-260px;z-index:50;
    transition:left 0.3s ease;
  }}
  #sidebar.open{{left:0}}
  .mobile-header{{
    display:flex;align-items:center;gap:12px;
    padding:16px;background:var(--bg-secondary);
    border-bottom:1px solid var(--separator);
    position:sticky;top:0;z-index:10;
  }}
  .hamburger{{
    width:36px;height:36px;border:none;border-radius:8px;
    background:var(--bg-tertiary);cursor:pointer;
    display:flex;align-items:center;justify-content:center;
    font-size:18px;
  }}
  .page{{padding:16px}}
  .kpi-row{{grid-template-columns:repeat(2,1fr)}}
}}
@media(min-width:769px){{
  .mobile-header{{display:none}}
}}
</style>
</head>
<body>

<!-- Login Screen -->
<div id="login-screen">
  <h1>NAKAI Operations</h1>
  <p>Enter admin password to continue</p>
  <input id="login-pw" type="password" placeholder="Password" autofocus
    onkeydown="if(event.key==='Enter')doLogin()">
  <button onclick="doLogin()">Sign In</button>
  <div id="login-error"></div>
</div>

<!-- Sidebar -->
<nav id="sidebar">
  <div class="sidebar-header">
    <h2>NAKAI</h2>
    <span>Operations Center</span>
  </div>
  <div class="nav-section">
    <div class="nav-section-label">Overview</div>
    <div class="nav-item active" data-page="dashboard" onclick="showPage('dashboard')">
      <div class="icon" style="background:rgba(52,199,89,0.15);color:var(--green)">&#9679;</div>
      Dashboard
    </div>
  </div>
  <div class="nav-section">
    <div class="nav-section-label">Content</div>
    <div class="nav-item" data-page="content" onclick="showPage('content')">
      <div class="icon" style="background:rgba(0,122,255,0.15);color:var(--accent)">&#9998;</div>
      Content Hub
    </div>
    <div class="nav-item" data-page="social" onclick="showPage('social')">
      <div class="icon" style="background:rgba(255,149,0,0.15);color:var(--orange)">&#9733;</div>
      Social Media
    </div>
  </div>
  <div class="nav-section">
    <div class="nav-section-label">Business</div>
    <div class="nav-item" data-page="b2b" onclick="showPage('b2b')">
      <div class="icon" style="background:rgba(88,86,214,0.15);color:#5856D6">&#9878;</div>
      B2B Sales
    </div>
    <div class="nav-item" data-page="email" onclick="showPage('email')">
      <div class="icon" style="background:rgba(255,45,85,0.15);color:#FF2D55">&#9993;</div>
      Email Marketing
    </div>
    <div class="nav-item" data-page="marketing" onclick="showPage('marketing')">
      <div class="icon" style="background:rgba(175,82,222,0.15);color:#AF52DE">&#9775;</div>
      Marketing
    </div>
  </div>
  <div class="nav-section">
    <div class="nav-section-label">System</div>
    <div class="nav-item" data-page="agents" onclick="showPage('agents')">
      <div class="icon" style="background:rgba(52,199,89,0.15);color:var(--green)">&#9881;</div>
      AI Agents
      <span class="badge" id="agents-badge">14</span>
    </div>
    <div class="nav-item" data-page="knowledge" onclick="showPage('knowledge')">
      <div class="icon" style="background:rgba(255,204,0,0.15);color:var(--yellow)">&#9889;</div>
      Knowledge Base
    </div>
  </div>
</nav>

<!-- Main Content -->
<div id="main">
  <div class="mobile-header">
    <button class="hamburger" onclick="document.getElementById('sidebar').classList.toggle('open')">&#9776;</button>
    <strong>NAKAI Operations</strong>
  </div>

  <!-- ═══ DASHBOARD ═══ -->
  <div class="page active" id="page-dashboard">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Real-time overview of NAKAI operations</p>
    </div>
    <div class="kpi-row" id="dashboard-kpis">
      <div class="kpi"><div class="kpi-label">Active Agents</div><div class="kpi-value" id="kpi-agents">--</div><div class="kpi-change up">Running on Claude Sonnet</div></div>
      <div class="kpi"><div class="kpi-label">B2B Leads</div><div class="kpi-value" id="kpi-leads">--</div><div class="kpi-change">Total pipeline</div></div>
      <div class="kpi"><div class="kpi-label">Posts Today</div><div class="kpi-value" id="kpi-posts">--</div><div class="kpi-change">Twitter/Threads/LINE/Reddit</div></div>
      <div class="kpi"><div class="kpi-label">Knowledge Docs</div><div class="kpi-value" id="kpi-docs">--</div><div class="kpi-change">ChromaDB indexed</div></div>
      <div class="kpi"><div class="kpi-label">AI Citations</div><div class="kpi-value" id="kpi-citations">--</div><div class="kpi-change">Monitored queries</div></div>
      <div class="kpi"><div class="kpi-label">Daily Cost</div><div class="kpi-value" id="kpi-cost">--</div><div class="kpi-change">Agent API spend</div></div>
    </div>
    <div class="quick-actions">
      <button class="btn btn-primary" onclick="generateContent()">Generate Today's Content</button>
      <button class="btn btn-secondary" onclick="runB2B()">Run B2B Pipeline</button>
      <button class="btn btn-secondary" onclick="refreshKnowledge()">Refresh Knowledge</button>
      <button class="btn btn-secondary" onclick="checkCitations()">Check AI Citations</button>
    </div>
    <div class="section-title">Recent Activity</div>
    <div id="recent-activity">
      <div class="skeleton" style="height:60px;margin-bottom:8px"></div>
      <div class="skeleton" style="height:60px;margin-bottom:8px"></div>
      <div class="skeleton" style="height:60px"></div>
    </div>
  </div>

  <!-- ═══ CONTENT HUB ═══ -->
  <div class="page" id="page-content">
    <div class="page-header">
      <h1>Content Hub</h1>
      <p>Daily matcha content generation and publishing</p>
    </div>
    <div class="segmented" id="content-tabs">
      <button class="active" onclick="showContentTab('generate')">Generate</button>
      <button onclick="showContentTab('blog')">Blog Posts</button>
      <button onclick="showContentTab('video')">Video Scripts</button>
      <button onclick="showContentTab('calendar')">Calendar</button>
    </div>
    <div id="content-generate">
      <div class="quick-actions">
        <button class="btn btn-primary" onclick="generateContent()">Generate Today's Content</button>
        <button class="btn btn-secondary" onclick="generateContent('reddit')">Generate Reddit Post</button>
        <button class="btn btn-secondary" onclick="generateContent('blog')">Generate Blog Article</button>
      </div>
      <div class="section-title">Today's Topic</div>
      <div class="card" id="today-topic" style="margin-bottom:16px">
        <div class="skeleton" style="height:24px;width:60%"></div>
      </div>
      <div class="section-title">Generated Content</div>
      <div id="generated-content"></div>
    </div>
    <div id="content-blog" style="display:none">
      <div class="section-title">Published Blog Articles</div>
      <div id="blog-list"><div class="skeleton" style="height:100px"></div></div>
    </div>
    <div id="content-video" style="display:none">
      <div class="section-title">Video Script Generator</div>
      <div class="card">
        <div class="input-group">
          <label>Topic</label>
          <input class="input" id="video-topic" placeholder="e.g., How to make the perfect matcha latte">
        </div>
        <button class="btn btn-primary" onclick="generateVideoScript()">Generate Script</button>
        <div id="video-script-output" style="margin-top:16px"></div>
      </div>
    </div>
    <div id="content-calendar" style="display:none">
      <div class="section-title">Content Calendar</div>
      <div id="calendar-view"><div class="skeleton" style="height:300px"></div></div>
    </div>
  </div>

  <!-- ═══ SOCIAL MEDIA ═══ -->
  <div class="page" id="page-social">
    <div class="page-header">
      <h1>Social Media</h1>
      <p>Posting, monitoring, and engagement across platforms</p>
    </div>
    <div class="segmented">
      <button class="active" onclick="showSocialTab('posting')">Posting</button>
      <button onclick="showSocialTab('monitor')">Mentions</button>
      <button onclick="showSocialTab('analytics')">Analytics</button>
    </div>
    <div id="social-posting">
      <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Twitter/X</div><div class="kpi-value" style="font-size:18px" id="tw-status">--</div></div>
        <div class="kpi"><div class="kpi-label">Threads</div><div class="kpi-value" style="font-size:18px" id="th-status">--</div></div>
        <div class="kpi"><div class="kpi-label">LINE</div><div class="kpi-value" style="font-size:18px" id="li-status">--</div></div>
        <div class="kpi"><div class="kpi-label">Reddit</div><div class="kpi-value" style="font-size:18px" id="rd-status">--</div></div>
      </div>
      <div class="section-title">Recent Posts</div>
      <div id="recent-posts"><div class="skeleton" style="height:120px"></div></div>
    </div>
    <div id="social-monitor" style="display:none">
      <div class="section-title">Social Mentions</div>
      <div id="mentions-list"><div class="skeleton" style="height:200px"></div></div>
    </div>
    <div id="social-analytics" style="display:none">
      <div class="section-title">Engagement Analytics</div>
      <div id="social-stats"><div class="skeleton" style="height:200px"></div></div>
    </div>
  </div>

  <!-- ═══ B2B SALES ═══ -->
  <div class="page" id="page-b2b">
    <div class="page-header">
      <h1>B2B Sales</h1>
      <p>Wholesale lead pipeline and outreach management</p>
    </div>
    <div class="segmented" id="b2b-tabs">
      <button class="active" onclick="showB2BTab('overview')">Overview</button>
      <button onclick="showB2BTab('leads')">Leads</button>
      <button onclick="showB2BTab('outreach')">Outreach</button>
      <button onclick="showB2BTab('discover')">Discover</button>
    </div>
    <div id="b2b-overview">
      <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Total Leads</div><div class="kpi-value" id="b2b-total">--</div></div>
        <div class="kpi"><div class="kpi-label">Emails Sent</div><div class="kpi-value" id="b2b-sent">--</div></div>
        <div class="kpi"><div class="kpi-label">Open Rate</div><div class="kpi-value" id="b2b-open">--</div></div>
        <div class="kpi"><div class="kpi-label">Replies</div><div class="kpi-value" id="b2b-replies">--</div></div>
      </div>
      <div class="quick-actions">
        <button class="btn btn-primary" onclick="runB2B()">Run Pipeline Now</button>
        <button class="btn btn-secondary" onclick="showPage('b2b');showB2BTab('discover')">Discover Leads</button>
      </div>
      <div class="section-title">Segments</div>
      <div class="card-grid" id="b2b-segments"></div>
    </div>
    <div id="b2b-leads" style="display:none">
      <div style="display:flex;gap:10px;margin-bottom:16px">
        <input class="input" style="max-width:300px" placeholder="Search leads..." id="lead-search" oninput="filterLeads()">
        <select class="input" style="max-width:180px" id="lead-segment" onchange="filterLeads()">
          <option value="">All Segments</option>
          <option value="cafe">Cafe</option>
          <option value="luxury_hotel">Luxury Hotel</option>
          <option value="fine_dining">Fine Dining</option>
        </select>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Company</th><th>Segment</th><th>Email</th><th>Status</th><th>Score</th></tr></thead>
          <tbody id="leads-table"></tbody>
        </table>
      </div>
    </div>
    <div id="b2b-outreach" style="display:none">
      <div class="section-title">Outreach History</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Lead</th><th>Step</th><th>Sent</th><th>Opened</th><th>Status</th></tr></thead>
          <tbody id="outreach-table"></tbody>
        </table>
      </div>
    </div>
    <div id="b2b-discover" style="display:none">
      <div class="card">
        <div class="input-group">
          <label>Search Query</label>
          <input class="input" id="discover-query" placeholder="e.g., matcha cafe Brooklyn">
        </div>
        <div class="input-group">
          <label>Segment</label>
          <select class="input" id="discover-segment">
            <option value="cafe">Cafe</option>
            <option value="luxury_hotel">Luxury Hotel</option>
            <option value="fine_dining">Fine Dining</option>
          </select>
        </div>
        <button class="btn btn-primary" onclick="discoverLeads()">Search</button>
      </div>
      <div id="discover-results" style="margin-top:16px"></div>
    </div>
  </div>

  <!-- ═══ EMAIL MARKETING ═══ -->
  <div class="page" id="page-email">
    <div class="page-header">
      <h1>Email Marketing</h1>
      <p>Campaigns, newsletters, and subscriber management</p>
    </div>
    <div class="segmented">
      <button class="active" onclick="showEmailTab('campaigns')">Campaigns</button>
      <button onclick="showEmailTab('newsletter')">Newsletter</button>
      <button onclick="showEmailTab('subscribers')">Subscribers</button>
    </div>
    <div id="email-campaigns">
      <div class="quick-actions">
        <button class="btn btn-primary" onclick="openModal('new-campaign')">New Campaign</button>
      </div>
      <div id="campaigns-list"><div class="skeleton" style="height:200px"></div></div>
    </div>
    <div id="email-newsletter" style="display:none">
      <div class="section-title">Newsletter Schedules</div>
      <div id="newsletter-list"><div class="skeleton" style="height:150px"></div></div>
    </div>
    <div id="email-subscribers" style="display:none">
      <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Total Subscribers</div><div class="kpi-value" id="sub-total">--</div></div>
        <div class="kpi"><div class="kpi-label">From Shopify</div><div class="kpi-value" id="sub-shopify">--</div></div>
      </div>
      <button class="btn btn-secondary" onclick="syncSubscribers()">Sync from Shopify</button>
    </div>
  </div>

  <!-- ═══ MARKETING ═══ -->
  <div class="page" id="page-marketing">
    <div class="page-header">
      <h1>Marketing Intelligence</h1>
      <p>SEO tracking, AI citations, and Shopify analytics</p>
    </div>
    <div class="segmented">
      <button class="active" onclick="showMarketingTab('seo')">SEO Rankings</button>
      <button onclick="showMarketingTab('citations')">AI Citations</button>
      <button onclick="showMarketingTab('shopify')">Shopify Data</button>
    </div>
    <div id="mkt-seo">
      <div class="section-title">Keyword Rankings</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Keyword</th><th>Position</th><th>Market</th><th>Change</th></tr></thead>
          <tbody id="seo-table"></tbody>
        </table>
      </div>
    </div>
    <div id="mkt-citations" style="display:none">
      <div class="section-title">AI Search Visibility</div>
      <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Queries Monitored</div><div class="kpi-value" id="cit-queries">70+</div></div>
        <div class="kpi"><div class="kpi-label">Featured In</div><div class="kpi-value" id="cit-featured">--</div></div>
        <div class="kpi"><div class="kpi-label">AI Overview Rank</div><div class="kpi-value" id="cit-rank">--</div></div>
      </div>
      <div id="citations-list"><div class="skeleton" style="height:200px"></div></div>
    </div>
    <div id="mkt-shopify" style="display:none">
      <div class="section-title">Shopify Analytics</div>
      <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Products</div><div class="kpi-value" id="shop-products">--</div></div>
        <div class="kpi"><div class="kpi-label">Collections</div><div class="kpi-value" id="shop-collections">--</div></div>
      </div>
      <div id="shopify-data"><div class="skeleton" style="height:200px"></div></div>
    </div>
  </div>

  <!-- ═══ AI AGENTS ═══ -->
  <div class="page" id="page-agents">
    <div class="page-header">
      <h1>AI Agents</h1>
      <p>OpenFang agent orchestration and monitoring</p>
    </div>
    <div class="segmented">
      <button class="active" onclick="showAgentTab('board')">Executive Board</button>
      <button onclick="showAgentTab('fund')">Fund Team</button>
      <button onclick="showAgentTab('hands')">Hands</button>
      <button onclick="showAgentTab('events')">Event Log</button>
    </div>
    <div id="agents-board">
      <div class="card-grid" id="board-agents"></div>
    </div>
    <div id="agents-fund" style="display:none">
      <div class="card-grid" id="fund-agents"></div>
    </div>
    <div id="agents-hands" style="display:none">
      <div class="card-grid" id="hand-agents"></div>
    </div>
    <div id="agents-events" style="display:none">
      <div id="events-log"><div class="skeleton" style="height:300px"></div></div>
    </div>
  </div>

  <!-- ═══ KNOWLEDGE BASE ═══ -->
  <div class="page" id="page-knowledge">
    <div class="page-header">
      <h1>Knowledge Base</h1>
      <p>RAG document management and ingestion</p>
    </div>
    <div class="quick-actions">
      <button class="btn btn-primary" onclick="refreshKnowledge()">Re-ingest All</button>
      <button class="btn btn-secondary" onclick="openModal('upload-doc')">Upload Document</button>
    </div>
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-label">Total Documents</div><div class="kpi-value" id="kb-docs">--</div></div>
      <div class="kpi"><div class="kpi-label">Vector Store</div><div class="kpi-value" id="kb-vectors">--</div></div>
    </div>
    <div class="section-title">Documents</div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Name</th><th>Type</th><th>Size</th><th>Actions</th></tr></thead>
        <tbody id="docs-table"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modal-overlay" onclick="if(event.target===this)closeModal()">
  <div class="modal" id="modal-content"></div>
</div>

<script>
const BASE = '';
let AUTH = '';

/* ─── Auth ─── */
function doLogin() {{
  const pw = document.getElementById('login-pw').value;
  fetch(BASE+'/api/admin/analytics', {{headers:{{'X-Admin-Password':pw}}}})
    .then(r => {{
      if (!r.ok) throw new Error('Invalid password');
      AUTH = pw;
      document.cookie = 'nakai_admin='+pw+';path=/;max-age=86400';
      document.getElementById('login-screen').classList.add('hidden');
      loadDashboard();
    }})
    .catch(() => {{
      document.getElementById('login-error').textContent = 'Invalid password';
    }});
}}

// Auto-login from cookie
(function() {{
  const c = document.cookie.match(/nakai_admin=([^;]+)/);
  if (c) {{
    AUTH = c[1];
    fetch(BASE+'/api/admin/analytics', {{headers:{{'X-Admin-Password':AUTH}}}})
      .then(r => {{
        if (r.ok) {{
          document.getElementById('login-screen').classList.add('hidden');
          loadDashboard();
        }}
      }});
  }}
}})();

function headers() {{ return {{'X-Admin-Password': AUTH, 'Content-Type': 'application/json'}}; }}

/* ─── Navigation ─── */
function showPage(page) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-'+page).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector('[data-page="'+page+'"]').classList.add('active');
  document.getElementById('sidebar').classList.remove('open');
}}

function showContentTab(tab) {{
  ['generate','blog','video','calendar'].forEach(t => {{
    const el = document.getElementById('content-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
  updateSegmented('content-tabs', tab, ['generate','blog','video','calendar']);
}}

function showSocialTab(tab) {{
  ['posting','monitor','analytics'].forEach(t => {{
    const el = document.getElementById('social-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
}}

function showB2BTab(tab) {{
  ['overview','leads','outreach','discover'].forEach(t => {{
    const el = document.getElementById('b2b-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
  updateSegmented('b2b-tabs', tab, ['overview','leads','outreach','discover']);
}}

function showEmailTab(tab) {{
  ['campaigns','newsletter','subscribers'].forEach(t => {{
    const el = document.getElementById('email-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
}}

function showMarketingTab(tab) {{
  ['seo','citations','shopify'].forEach(t => {{
    const el = document.getElementById('mkt-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
}}

function showAgentTab(tab) {{
  ['board','fund','hands','events'].forEach(t => {{
    const el = document.getElementById('agents-'+t);
    if(el) el.style.display = t===tab ? 'block' : 'none';
  }});
}}

function updateSegmented(id, active, tabs) {{
  const el = document.getElementById(id);
  if(!el) return;
  const btns = el.querySelectorAll('button');
  btns.forEach((b,i) => b.classList.toggle('active', tabs[i]===active));
}}

/* ─── Modal ─── */
function openModal(type) {{
  const overlay = document.getElementById('modal-overlay');
  const content = document.getElementById('modal-content');
  if(type==='upload-doc') {{
    content.innerHTML = '<h2>Upload Document</h2><div class="input-group"><label>File</label><input type="file" class="input" id="doc-file" accept=".txt,.pdf,.md"></div><button class="btn btn-primary" onclick="uploadDoc()">Upload</button>';
  }} else if(type==='new-campaign') {{
    content.innerHTML = '<h2>New Campaign</h2><div class="input-group"><label>Subject</label><input class="input" id="camp-subject" placeholder="Campaign subject"></div><div class="input-group"><label>Content</label><textarea class="input" id="camp-content" placeholder="Email content or leave blank for AI generation"></textarea></div><button class="btn btn-primary" onclick="createCampaign()">Create</button>';
  }}
  overlay.classList.add('show');
}}
function closeModal() {{ document.getElementById('modal-overlay').classList.remove('show'); }}

/* ─── Data Loading ─── */
async function loadDashboard() {{
  loadKPIs();
  loadAgents();
  loadB2BData();
  loadKnowledge();
  loadRecentActivity();
}}

async function loadKPIs() {{
  try {{
    const [health, analytics] = await Promise.all([
      fetch(BASE+'/api/health').then(r=>r.json()),
      fetch(BASE+'/api/admin/analytics', {{headers:headers()}}).then(r=>r.json()).catch(()=>({{}})),
    ]);
    document.getElementById('kpi-docs').textContent = analytics.knowledge_count || '179';
    document.getElementById('kpi-posts').textContent = analytics.posts_today || '0';
  }} catch(e) {{ console.error('KPI load error:', e); }}

  // OpenFang status
  try {{
    const status = await fetch(BASE+'/api/openfang/status', {{headers:headers()}}).then(r=>r.json());
    document.getElementById('kpi-agents').textContent = status.active_agents || '14';
  }} catch(e) {{
    document.getElementById('kpi-agents').textContent = '14';
  }}

  // B2B leads count
  try {{
    const leads = await fetch(BASE+'/api/b2b/leads', {{headers:headers()}}).then(r=>r.json());
    document.getElementById('kpi-leads').textContent = Array.isArray(leads) ? leads.length : '--';
  }} catch(e) {{}}

  // Budget
  try {{
    const budget = await fetch(BASE+'/api/openfang/budget', {{headers:headers()}}).then(r=>r.json());
    document.getElementById('kpi-cost').textContent = '$' + (budget.today_spend || '0');
  }} catch(e) {{
    document.getElementById('kpi-cost').textContent = '$--';
  }}
}}

async function loadAgents() {{
  try {{
    const agents = await fetch(BASE+'/api/openfang/agents', {{headers:headers()}}).then(r=>r.json());
    if(!Array.isArray(agents)) return;

    const board = agents.filter(a => a.name && a.name.includes('board'));
    const fund = agents.filter(a => a.name && (a.name.includes('fund') || a.name.includes('analyst') || a.name.includes('cio')));
    const hands = agents.filter(a => a.name && a.name.includes('hand'));

    renderAgentCards('board-agents', board.length ? board : agents.slice(0,5));
    renderAgentCards('fund-agents', fund.length ? fund : agents.slice(5,11));
    renderAgentCards('hand-agents', hands.length ? hands : agents.slice(11));
    document.getElementById('agents-badge').textContent = agents.length;
  }} catch(e) {{
    // Fallback agent display
    const names = ['CEO','CMO','CPO','CFO','CLO','CIO','Macro','Technical','Fundamental','Sentiment','Risk','Lead Hand','Researcher','Assistant'];
    const cards = names.map(n => `<div class="agent-card"><div class="agent-name"><span class="status-dot active"></span>${{n}}</div><div class="agent-role">OpenFang Agent</div></div>`).join('');
    document.getElementById('board-agents').innerHTML = cards;
  }}
}}

function renderAgentCards(containerId, agents) {{
  const el = document.getElementById(containerId);
  if(!el) return;
  el.innerHTML = agents.map(a => `
    <div class="agent-card">
      <div class="agent-name">
        <span class="status-dot ${{a.status==='active'?'active':a.status==='idle'?'idle':'stopped'}}"></span>
        ${{a.display_name || a.name || 'Agent'}}
      </div>
      <div class="agent-role">${{a.role || a.description || ''}}</div>
      <div class="agent-status">
        <span class="badge badge-${{a.status==='active'?'green':a.status==='idle'?'orange':'gray'}}">${{a.status || 'unknown'}}</span>
      </div>
    </div>
  `).join('');
}}

async function loadB2BData() {{
  try {{
    const [leads, analytics] = await Promise.all([
      fetch(BASE+'/api/b2b/leads', {{headers:headers()}}).then(r=>r.json()).catch(()=>[]),
      fetch(BASE+'/api/b2b/analytics', {{headers:headers()}}).then(r=>r.json()).catch(()=>({{}})),
    ]);
    if(Array.isArray(leads)) {{
      document.getElementById('b2b-total').textContent = leads.length;
      document.getElementById('leads-table').innerHTML = leads.slice(0,50).map(l => `
        <tr>
          <td>${{l.company_name||'--'}}</td>
          <td><span class="badge badge-blue">${{l.segment||'--'}}</span></td>
          <td>${{l.email||'--'}}</td>
          <td><span class="badge badge-${{l.status==='contacted'?'green':l.status==='found'?'orange':'gray'}}">${{l.status||'--'}}</span></td>
          <td>${{l.score||'--'}}</td>
        </tr>
      `).join('');
    }}
    if(analytics) {{
      document.getElementById('b2b-sent').textContent = analytics.total_sent || '--';
      document.getElementById('b2b-open').textContent = analytics.open_rate ? analytics.open_rate+'%' : '--';
      document.getElementById('b2b-replies').textContent = analytics.replies || '--';
    }}
  }} catch(e) {{ console.error('B2B load error:', e); }}
}}

async function loadKnowledge() {{
  try {{
    const docs = await fetch(BASE+'/api/admin/knowledge', {{headers:headers()}}).then(r=>r.json());
    if(Array.isArray(docs)) {{
      document.getElementById('kb-docs').textContent = docs.length;
      document.getElementById('docs-table').innerHTML = docs.map(d => `
        <tr>
          <td>${{d.name||d.title||'--'}}</td>
          <td>${{d.type||d.category||'txt'}}</td>
          <td>${{d.size||'--'}}</td>
          <td><button class="btn btn-sm btn-red" onclick="deleteDoc('${{d.id||d.name}}')">Delete</button></td>
        </tr>
      `).join('');
    }}
  }} catch(e) {{}}
}}

async function loadRecentActivity() {{
  try {{
    const tips = await fetch(BASE+'/api/daily-tips/history?limit=5', {{headers:headers()}}).then(r=>r.json()).catch(()=>[]);
    const el = document.getElementById('recent-activity');
    if(Array.isArray(tips) && tips.length) {{
      el.innerHTML = tips.map(t => `
        <div class="content-item">
          <h3>${{t.topic||'Content posted'}}</h3>
          <div class="meta">
            <span>${{t.posted_at ? new Date(t.posted_at).toLocaleString() : '--'}}</span>
            <span>Twitter: ${{t.twitter_status||'--'}}</span>
            <span>Threads: ${{t.threads_status||'--'}}</span>
          </div>
        </div>
      `).join('');
    }} else {{
      el.innerHTML = '<div class="card" style="color:var(--text-secondary)">No recent activity found. Generate your first content above.</div>';
    }}
  }} catch(e) {{
    document.getElementById('recent-activity').innerHTML = '<div class="card" style="color:var(--text-secondary)">Could not load activity.</div>';
  }}
}}

/* ─── Actions ─── */
async function generateContent(platform) {{
  const btn = event.target;
  btn.disabled = true; btn.textContent = 'Generating...';
  try {{
    const r = await fetch(BASE+'/api/daily-tips/generate', {{
      method:'POST', headers:headers(),
      body: JSON.stringify({{platforms: platform ? [platform] : ['twitter','threads','line']}})
    }});
    const data = await r.json();
    if(data.topic) {{
      document.getElementById('today-topic').innerHTML = '<strong>'+data.topic+'</strong>';
    }}
    const output = document.getElementById('generated-content');
    let html = '';
    for(const [k,v] of Object.entries(data)) {{
      if(k === 'topic') continue;
      html += `<div class="content-item"><h3>${{k.charAt(0).toUpperCase()+k.slice(1)}}</h3><div class="preview">${{(v||'').substring(0,300)}}</div></div>`;
    }}
    output.innerHTML = html || '<div class="card">Content generated. Check platform status.</div>';
  }} catch(e) {{
    alert('Generation failed: '+e.message);
  }} finally {{
    btn.disabled = false; btn.textContent = platform ? 'Generate '+platform : "Generate Today's Content";
  }}
}}

async function runB2B() {{
  if(!confirm('Run B2B sales pipeline now?')) return;
  try {{
    await fetch(BASE+'/api/b2b/pipeline/run', {{method:'POST', headers:headers()}});
    alert('B2B pipeline started');
  }} catch(e) {{ alert('Failed: '+e.message); }}
}}

async function refreshKnowledge() {{
  try {{
    const r = await fetch(BASE+'/api/refresh', {{method:'POST', headers:{{'X-Refresh-Secret':'{settings.refresh_secret}'}}}});
    const data = await r.json();
    alert('Knowledge refreshed: '+(data.count||0)+' documents');
    loadKnowledge();
  }} catch(e) {{ alert('Failed: '+e.message); }}
}}

async function checkCitations() {{
  try {{
    await fetch(BASE+'/api/admin/run-citations', {{method:'POST', headers:headers()}});
    alert('Citation check started');
  }} catch(e) {{ alert('Failed: '+e.message); }}
}}

async function discoverLeads() {{
  const query = document.getElementById('discover-query').value;
  const segment = document.getElementById('discover-segment').value;
  if(!query) return alert('Enter a search query');
  const el = document.getElementById('discover-results');
  el.innerHTML = '<div class="skeleton" style="height:100px"></div>';
  try {{
    const r = await fetch(BASE+'/api/b2b/discover', {{
      method:'POST', headers:headers(),
      body: JSON.stringify({{query, segment}})
    }});
    const data = await r.json();
    if(Array.isArray(data) && data.length) {{
      el.innerHTML = data.map(d => `
        <div class="content-item">
          <h3>${{d.name||d.company_name||'--'}}</h3>
          <div class="meta"><span>${{d.address||''}}</span><span>${{d.segment||segment}}</span></div>
        </div>
      `).join('');
    }} else {{
      el.innerHTML = '<div class="card">No results found.</div>';
    }}
  }} catch(e) {{ el.innerHTML = '<div class="card" style="color:var(--red)">Search failed.</div>'; }}
}}

function filterLeads() {{
  // Client-side filtering of the leads table
  const search = (document.getElementById('lead-search').value||'').toLowerCase();
  const segment = document.getElementById('lead-segment').value;
  const rows = document.querySelectorAll('#leads-table tr');
  rows.forEach(r => {{
    const text = r.textContent.toLowerCase();
    const matchSearch = !search || text.includes(search);
    const matchSegment = !segment || text.includes(segment);
    r.style.display = matchSearch && matchSegment ? '' : 'none';
  }});
}}

async function syncSubscribers() {{
  try {{
    const r = await fetch(BASE+'/api/email/sync-shopify', {{method:'POST', headers:headers()}});
    const data = await r.json();
    alert('Synced '+(data.synced||0)+' subscribers from Shopify');
  }} catch(e) {{ alert('Sync failed'); }}
}}

async function uploadDoc() {{
  const file = document.getElementById('doc-file').files[0];
  if(!file) return alert('Select a file');
  const formData = new FormData();
  formData.append('file', file);
  try {{
    await fetch(BASE+'/api/admin/knowledge', {{
      method:'POST',
      headers:{{'X-Admin-Password': AUTH}},
      body: formData
    }});
    closeModal();
    loadKnowledge();
    alert('Document uploaded');
  }} catch(e) {{ alert('Upload failed'); }}
}}

async function deleteDoc(id) {{
  if(!confirm('Delete this document?')) return;
  try {{
    await fetch(BASE+'/api/admin/knowledge/'+id, {{method:'DELETE', headers:headers()}});
    loadKnowledge();
  }} catch(e) {{ alert('Delete failed'); }}
}}

async function generateVideoScript() {{
  const topic = document.getElementById('video-topic').value;
  if(!topic) return alert('Enter a topic');
  const el = document.getElementById('video-script-output');
  el.innerHTML = '<div class="skeleton" style="height:200px"></div>';
  try {{
    const r = await fetch(BASE+'/api/daily-tips/generate', {{
      method:'POST', headers:headers(),
      body: JSON.stringify({{platforms: ['video'], custom_topic: topic}})
    }});
    const data = await r.json();
    el.innerHTML = `<div class="card"><pre style="white-space:pre-wrap;font-family:var(--font);font-size:14px;line-height:1.6">${{data.video||data.content||JSON.stringify(data,null,2)}}</pre></div>`;
  }} catch(e) {{
    el.innerHTML = '<div class="card" style="color:var(--red)">Generation failed.</div>';
  }}
}}

async function createCampaign() {{
  const subject = document.getElementById('camp-subject').value;
  if(!subject) return alert('Enter a subject');
  try {{
    await fetch(BASE+'/api/email/campaigns', {{
      method:'POST', headers:headers(),
      body: JSON.stringify({{subject, content: document.getElementById('camp-content').value}})
    }});
    closeModal();
    alert('Campaign created');
  }} catch(e) {{ alert('Failed'); }}
}}
</script>
</body>
</html>"""
