"""Unified dashboard — /dashboard route + AJAX section loader."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .shell import SHELL_CSS, SHELL_LOGIN, SHELL_SIDEBAR, SHELL_JS
from . import (
    section_home, section_b2b, section_email, section_content,
    section_analytics, section_social, section_guide,
)

dashboard_router = APIRouter()

SECTIONS = {
    "home": section_home,
    "b2b": section_b2b,
    "email": section_email,
    "social": section_social,
    "content": section_content,
    "analytics": section_analytics,
    "guide": section_guide,
}

DASHBOARD_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAKAI Management Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/css/tabler.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.31.0/dist/tabler-icons.min.css" rel="stylesheet">
<style>{SHELL_CSS}</style>
</head>
<body>

{SHELL_LOGIN}

<div id="dash-app" style="display:none">
  {SHELL_SIDEBAR}
  <div class="dash-main">
    <div class="dash-topbar" id="dash-topbar">
      <button onclick="openSidebar()"><i class="ti ti-menu-2"></i></button>
      <span class="title" id="dash-topbar-title">Home</span>
    </div>
    <div class="dash-content" id="dash-content">
      <!-- Sections loaded via AJAX -->
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/js/tabler.min.js"></script>
{SHELL_JS}
</body>
</html>"""


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(
        content=DASHBOARD_HTML,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@dashboard_router.get("/api/dashboard/section/{name}", response_class=HTMLResponse)
async def get_section(name: str, request: Request):
    # Check auth
    pw = request.headers.get("X-Admin-Password", "")
    from config import settings
    if pw != settings.admin_password:
        return HTMLResponse(
            content='<div class="section-loading" style="color:#c0392b">Unauthorized</div>',
            status_code=401,
        )

    mod = SECTIONS.get(name)
    if not mod:
        return HTMLResponse(
            content='<div class="section-loading" style="color:#c0392b">Section not found</div>',
            status_code=404,
        )

    return HTMLResponse(content=mod.html())
