"""Admin dashboard for NAKAI Matcha Chatbot.

GET /admin → Password-gated admin HTML with 3 tabs:
  1. Knowledge Base management
  2. Chat History browser
  3. Analytics dashboard
"""

import base64
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

admin_page_router = APIRouter()

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LOGO_B64 = base64.b64encode(
    (_REPO_ROOT / "logo-black-icon.png").read_bytes()
).decode()

ADMIN_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAKAI Admin</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--green:#406546;--cream:#F9F0E2;--white:#FFFFFF;--red:#c0392b;--gray:#666;--light:#f5f5f5}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--cream);color:#333;min-height:100vh}}
#login-gate{{display:flex;align-items:center;justify-content:center;min-height:100vh}}
.login-box{{background:var(--white);padding:48px;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;max-width:360px;width:90%}}
.login-box img{{width:40px;margin-bottom:16px;opacity:.7}}
.login-box h2{{font-size:1.1rem;font-weight:500;color:var(--green);margin-bottom:24px;letter-spacing:.08em;text-transform:uppercase}}
.login-box input{{width:100%;padding:12px 16px;border:1px solid #ddd;border-radius:8px;font-size:1rem;outline:none;margin-bottom:12px}}
.login-box input:focus{{border-color:var(--green)}}
.login-box button{{width:100%;padding:12px;background:var(--green);color:var(--white);border:none;border-radius:8px;font-size:.9rem;cursor:pointer}}
.login-error{{color:var(--red);font-size:.85rem;margin-top:8px;display:none}}
#dashboard{{display:none}}
.topbar{{background:var(--green);color:var(--cream);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}}
.topbar h1{{font-size:.9rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase}}
.topbar button{{background:rgba(255,255,255,.15);color:var(--cream);border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:.8rem}}
.tabs{{display:flex;border-bottom:2px solid #eee;background:var(--white);padding:0 24px}}
.tab{{padding:14px 20px;font-size:.85rem;font-weight:500;color:var(--gray);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px}}
.tab.active{{color:var(--green);border-bottom-color:var(--green)}}
.panel{{display:none;padding:24px;max-width:1200px;margin:0 auto}}
.panel.active{{display:block}}
table{{width:100%;border-collapse:collapse;background:var(--white);border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
th{{background:var(--light);font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--gray);padding:12px 16px;text-align:left}}
td{{padding:12px 16px;border-top:1px solid #f0f0f0;font-size:.88rem;vertical-align:top}}
.btn{{padding:6px 14px;border:none;border-radius:6px;font-size:.8rem;font-weight:500;cursor:pointer}}
.btn-green{{background:var(--green);color:var(--white)}}
.btn-red{{background:var(--red);color:var(--white)}}
.btn-outline{{background:transparent;border:1px solid #ddd;color:#666}}
.btn-outline:hover{{border-color:var(--green);color:var(--green)}}
.btn-sm{{padding:4px 10px;font-size:.75rem}}
.form-group{{margin-bottom:16px}}
.form-group label{{display:block;font-size:.8rem;font-weight:500;margin-bottom:4px;color:var(--gray)}}
.form-group input,.form-group select,.form-group textarea{{width:100%;padding:10px 14px;border:1px solid #ddd;border-radius:8px;font-size:.9rem;font-family:inherit;outline:none}}
.form-group textarea{{min-height:200px;resize:vertical}}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{{border-color:var(--green)}}
.modal-bg{{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:100}}
.modal-bg.show{{display:flex}}
.modal{{background:var(--white);border-radius:12px;padding:32px;max-width:600px;width:90%;max-height:90vh;overflow-y:auto}}
.modal h3{{font-size:1rem;font-weight:600;color:var(--green);margin-bottom:20px}}
.modal-actions{{display:flex;gap:8px;justify-content:flex-end;margin-top:20px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}}
.stat-card{{background:var(--white);padding:24px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.stat-card .label{{font-size:.75rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:var(--gray);margin-bottom:4px}}
.stat-card .value{{font-size:1.8rem;font-weight:600;color:var(--green)}}
.badge{{padding:3px 8px;border-radius:4px;font-size:.72rem;font-weight:600}}
.badge-active{{background:rgba(64,101,70,.1);color:var(--green)}}
.badge-inactive{{background:rgba(192,57,43,.1);color:var(--red)}}
.msg-viewer{{background:var(--white);border-radius:8px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,.06);max-height:500px;overflow-y:auto}}
.msg-item{{padding:10px 14px;border-radius:12px;margin-bottom:8px;max-width:80%;font-size:.88rem;line-height:1.6;white-space:pre-wrap}}
.msg-user{{background:var(--green);color:var(--white);margin-left:auto;border-radius:12px 12px 4px 12px}}
.msg-assistant{{background:var(--light);color:#333;border-radius:4px 12px 12px 12px}}
.msg-meta{{font-size:.7rem;color:var(--gray);margin-top:4px}}
.toolbar{{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}}
.toolbar select{{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:.85rem;outline:none}}
.bar-chart{{display:flex;align-items:flex-end;gap:8px;height:140px;padding:0 8px}}
.bar-col{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px}}
.bar-fill{{width:100%;max-width:40px;background:var(--green);border-radius:4px 4px 0 0;transition:height .3s}}
.bar-label{{font-size:.65rem;color:var(--gray)}}
.bar-value{{font-size:.7rem;font-weight:600;color:var(--green)}}
.breakdown-row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:.88rem}}
#upload-zone{{border:2px dashed #ddd;border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:border-color .2s}}
#upload-zone:hover,#upload-zone.drag-over{{border-color:var(--green);background:rgba(64,101,70,.03)}}
.upload-clear{{display:inline-block;margin-top:8px;padding:2px 10px;font-size:.75rem;border:1px solid #ddd;border-radius:4px;cursor:pointer;background:transparent;color:var(--gray)}}
.upload-clear:hover{{border-color:var(--red);color:var(--red)}}
</style>
</head>
<body>
<div id="login-gate">
  <div class="login-box">
    <img src="data:image/png;base64,{_LOGO_B64}" alt="NAKAI" />
    <h2>Admin Dashboard</h2>
    <form id="login-form">
      <input type="password" id="login-pw" placeholder="Enter admin password" autofocus />
      <button type="submit">Sign In</button>
    </form>
    <div class="login-error" id="login-error">Invalid password</div>
  </div>
</div>
<div id="dashboard">
  <div class="topbar">
    <h1>NAKAI Admin</h1>
    <div style="display:flex;gap:8px">
      <button onclick="reingest()">Re-ingest Knowledge</button>
      <button onclick="logout()">Logout</button>
    </div>
  </div>
  <div class="tabs">
    <div class="tab active" data-tab="knowledge">Knowledge Base</div>
    <div class="tab" data-tab="history">Chat History</div>
    <div class="tab" data-tab="analytics">Analytics</div>
  </div>
  <div class="panel active" id="panel-knowledge">
    <div class="toolbar">
      <button class="btn btn-green" onclick="openCreateArticle()">+ New Article</button>
      <select id="filter-lang" onchange="loadArticles()"><option value="">All Languages</option><option value="en">English</option><option value="ja">Japanese</option></select>
      <select id="filter-cat" onchange="loadArticles()"><option value="">All Categories</option><option value="general">General</option><option value="product">Product</option><option value="faq">FAQ</option><option value="brewing">Brewing</option><option value="science">Science</option><option value="shipping">Shipping</option><option value="recipe">Recipe</option></select>
    </div>
    <table><thead><tr><th>Title</th><th>Lang</th><th>Category</th><th>Status</th><th>Updated</th><th>Actions</th></tr></thead><tbody id="articles-tbody"></tbody></table>
  </div>
  <div class="panel" id="panel-history">
    <div class="toolbar">
      <select id="hist-source" onchange="loadConversations()"><option value="">All Sources</option><option value="pwa">PWA</option><option value="widget">Widget</option></select>
      <select id="hist-lang" onchange="loadConversations()"><option value="">All Languages</option><option value="en">English</option><option value="ja">Japanese</option></select>
      <button class="btn btn-outline" onclick="loadConversations()">Refresh</button>
    </div>
    <div style="display:flex;gap:20px;flex-wrap:wrap">
      <div style="flex:1;min-width:300px;max-width:500px">
        <table><thead><tr><th>Session</th><th>Src</th><th>Msgs</th><th>Last Activity</th></tr></thead><tbody id="convs-tbody"></tbody></table>
      </div>
      <div style="flex:1;min-width:300px">
        <div class="msg-viewer" id="msg-viewer"><p style="color:var(--gray);text-align:center;padding:40px">Select a conversation</p></div>
      </div>
    </div>
  </div>
  <div class="panel" id="panel-analytics">
    <div class="stats-grid" id="stats-grid"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div>
        <h3 style="font-size:.9rem;margin-bottom:12px;color:var(--green)">Daily Conversations (Last 7 Days)</h3>
        <div class="bar-chart" id="daily-chart"></div>
      </div>
      <div>
        <h3 style="font-size:.9rem;margin-bottom:12px;color:var(--green)">By Source</h3>
        <div id="source-breakdown"></div>
        <h3 style="font-size:.9rem;margin:16px 0 12px;color:var(--green)">By Language</h3>
        <div id="lang-breakdown"></div>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="article-modal">
  <div class="modal">
    <h3 id="modal-title">New Article</h3>
    <input type="hidden" id="edit-id" />
    <div class="form-group"><label>Title</label><input id="art-title" /></div>
    <div class="form-group"><label>Language</label><select id="art-lang"><option value="en">English</option><option value="ja">Japanese</option></select></div>
    <div class="form-group"><label>Category</label><select id="art-cat"><option value="general">General</option><option value="product">Product</option><option value="faq">FAQ</option><option value="brewing">Brewing</option><option value="science">Science</option><option value="shipping">Shipping</option><option value="recipe">Recipe</option></select></div>
    <div class="form-group" id="upload-group"><label>Upload File (.txt or .pdf)</label><div id="upload-zone"><input type="file" id="art-file" accept=".txt,.pdf" style="display:none" /><div id="upload-label" style="color:var(--gray);font-size:.85rem">Click to select a file or drag &amp; drop<br><span style="font-size:.75rem">.txt or .pdf (max 5 MB)</span></div><div id="upload-info" style="display:none;color:var(--green);font-size:.85rem"></div></div></div>
    <div class="form-group"><label>Content <span id="content-source" style="font-size:.75rem;color:var(--gray)"></span></label><textarea id="art-content"></textarea></div>
    <div class="modal-actions">
      <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
      <button class="btn btn-green" onclick="saveArticle()">Save</button>
    </div>
  </div>
</div>
<script>
(function(){{
  'use strict';
  var adminPw='';
  function hdrs(){{return{{'Content-Type':'application/json','X-Admin-Password':adminPw}}}}
  function esc(s){{if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML}}

  var selectedFile=null;
  var fileInput=document.getElementById('art-file');
  var uploadZone=document.getElementById('upload-zone');
  uploadZone.addEventListener('click',function(){{if(!selectedFile)fileInput.click()}});
  uploadZone.addEventListener('dragover',function(e){{e.preventDefault();uploadZone.classList.add('drag-over')}});
  uploadZone.addEventListener('dragleave',function(){{uploadZone.classList.remove('drag-over')}});
  uploadZone.addEventListener('drop',function(e){{e.preventDefault();uploadZone.classList.remove('drag-over');if(e.dataTransfer.files.length)handleFileSelect(e.dataTransfer.files[0])}});
  fileInput.addEventListener('change',function(){{if(fileInput.files.length)handleFileSelect(fileInput.files[0])}});
  function handleFileSelect(f){{
    var ext=f.name.split('.').pop().toLowerCase();
    if(ext!=='txt'&&ext!=='pdf'){{alert('Only .txt and .pdf files are supported');return}}
    if(f.size>5*1024*1024){{alert('File too large. Maximum size is 5 MB.');return}}
    selectedFile=f;
    document.getElementById('upload-label').style.display='none';
    var info=document.getElementById('upload-info');
    info.style.display='block';
    info.innerHTML=esc(f.name)+' ('+(f.size/1024).toFixed(1)+' KB)<br><button type="button" class="upload-clear" onclick="clearFile(event)">Remove</button>';
    document.getElementById('content-source').textContent='(will be replaced by file content)';
    var ti=document.getElementById('art-title');
    if(!ti.value.trim())ti.value=f.name.replace(/\.[^.]+$/,'').replace(/[_-]/g,' ');
  }}
  window.clearFile=function(e){{
    e.stopPropagation();selectedFile=null;fileInput.value='';
    document.getElementById('upload-label').style.display='block';
    document.getElementById('upload-info').style.display='none';
    document.getElementById('content-source').textContent='';
  }};

  document.getElementById('login-form').addEventListener('submit',function(e){{
    e.preventDefault();
    var pw=document.getElementById('login-pw').value;
    fetch('/api/admin/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{password:pw}})}})
    .then(function(r){{if(!r.ok)throw new Error();return r.json()}})
    .then(function(){{
      adminPw=pw;sessionStorage.setItem('nakai_admin_pw',pw);
      document.getElementById('login-gate').style.display='none';
      document.getElementById('dashboard').style.display='block';
      loadArticles();loadAnalytics();
    }})
    .catch(function(){{document.getElementById('login-error').style.display='block'}});
  }});

  var stored=sessionStorage.getItem('nakai_admin_pw');
  if(stored){{adminPw=stored;document.getElementById('login-gate').style.display='none';document.getElementById('dashboard').style.display='block';loadArticles();loadAnalytics()}}

  window.logout=function(){{sessionStorage.removeItem('nakai_admin_pw');location.reload()}};

  document.querySelectorAll('.tab').forEach(function(t){{
    t.addEventListener('click',function(){{
      document.querySelectorAll('.tab').forEach(function(x){{x.classList.remove('active')}});
      document.querySelectorAll('.panel').forEach(function(x){{x.classList.remove('active')}});
      t.classList.add('active');
      document.getElementById('panel-'+t.getAttribute('data-tab')).classList.add('active');
      if(t.getAttribute('data-tab')==='history')loadConversations();
      if(t.getAttribute('data-tab')==='analytics')loadAnalytics();
    }});
  }});

  window.loadArticles=function(){{
    var lang=document.getElementById('filter-lang').value;
    var cat=document.getElementById('filter-cat').value;
    var qs='?';if(lang)qs+='language='+lang+'&';if(cat)qs+='category='+cat;
    fetch('/api/admin/articles'+qs,{{headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(d){{
      var tb=document.getElementById('articles-tbody');tb.innerHTML='';
      (d.articles||[]).forEach(function(a){{
        var tr=document.createElement('tr');
        var st=a.is_active?'<span class="badge badge-active">Active</span>':'<span class="badge badge-inactive">Inactive</span>';
        var upd=a.updated_at?a.updated_at.substring(0,10):'—';
        tr.innerHTML='<td><strong>'+esc(a.title)+'</strong></td><td>'+esc(a.language)+'</td><td>'+esc(a.category)+'</td><td>'+st+'</td><td>'+upd+'</td>'
          +'<td><button class="btn btn-outline btn-sm" onclick="editArticle(\\''+a.id+'\\')">Edit</button> '
          +'<button class="btn btn-outline btn-sm" onclick="toggleArticle(\\''+a.id+'\\','+(!a.is_active)+')">'+(a.is_active?'Deactivate':'Activate')+'</button> '
          +'<button class="btn btn-red btn-sm" onclick="deleteArticle(\\''+a.id+'\\')">Delete</button></td>';
        tb.appendChild(tr);
      }});
    }});
  }};

  window.openCreateArticle=function(){{
    document.getElementById('modal-title').textContent='New Article';
    document.getElementById('edit-id').value='';
    document.getElementById('art-title').value='';
    document.getElementById('art-content').value='';
    document.getElementById('art-lang').value='en';
    document.getElementById('art-cat').value='general';
    selectedFile=null;fileInput.value='';
    document.getElementById('upload-label').style.display='block';
    document.getElementById('upload-info').style.display='none';
    document.getElementById('content-source').textContent='';
    document.getElementById('upload-group').style.display='block';
    document.getElementById('article-modal').classList.add('show');
  }};

  window.editArticle=function(id){{
    fetch('/api/admin/articles/'+id,{{headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(a){{
      document.getElementById('modal-title').textContent='Edit Article';
      document.getElementById('edit-id').value=id;
      document.getElementById('art-title').value=a.title||'';
      document.getElementById('art-content').value=a.content||'';
      document.getElementById('art-lang').value=a.language||'en';
      document.getElementById('art-cat').value=a.category||'general';
      document.getElementById('upload-group').style.display='none';
      document.getElementById('content-source').textContent='';
      selectedFile=null;
      document.getElementById('article-modal').classList.add('show');
    }});
  }};

  window.saveArticle=function(){{
    var id=document.getElementById('edit-id').value;
    if(!id&&selectedFile){{
      var fd=new FormData();
      fd.append('file',selectedFile);
      fd.append('title',document.getElementById('art-title').value);
      fd.append('language',document.getElementById('art-lang').value);
      fd.append('category',document.getElementById('art-cat').value);
      fetch('/api/admin/articles/upload',{{method:'POST',headers:{{'X-Admin-Password':adminPw}},body:fd}})
      .then(function(r){{if(!r.ok)return r.json().then(function(d){{throw new Error(d.detail||'Upload failed')}});return r.json()}})
      .then(function(){{closeModal();loadArticles()}})
      .catch(function(e){{alert('Upload failed: '+e.message)}});
    }}else{{
      var data={{title:document.getElementById('art-title').value,content:document.getElementById('art-content').value,language:document.getElementById('art-lang').value,category:document.getElementById('art-cat').value}};
      var url=id?'/api/admin/articles/'+id:'/api/admin/articles';
      var method=id?'PATCH':'POST';
      fetch(url,{{method:method,headers:hdrs(),body:JSON.stringify(data)}})
      .then(function(r){{if(!r.ok)throw new Error();return r.json()}})
      .then(function(){{closeModal();loadArticles()}})
      .catch(function(){{alert('Failed to save article')}});
    }}
  }};

  window.toggleArticle=function(id,newState){{
    fetch('/api/admin/articles/'+id,{{method:'PATCH',headers:hdrs(),body:JSON.stringify({{is_active:newState}})}})
    .then(function(){{loadArticles()}});
  }};

  window.deleteArticle=function(id){{
    if(!confirm('Delete this article permanently?'))return;
    fetch('/api/admin/articles/'+id,{{method:'DELETE',headers:hdrs()}})
    .then(function(){{loadArticles()}});
  }};

  window.closeModal=function(){{document.getElementById('article-modal').classList.remove('show')}};

  window.reingest=function(){{
    if(!confirm('Re-ingest all knowledge? This takes 1-2 minutes.'))return;
    fetch('/api/admin/reingest',{{method:'POST',headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(d){{alert('Re-ingestion '+d.status)}})
    .catch(function(){{alert('Failed to trigger re-ingestion')}});
  }};

  window.loadConversations=function(){{
    var src=document.getElementById('hist-source').value;
    var lng=document.getElementById('hist-lang').value;
    var qs='?limit=50';if(src)qs+='&source='+src;if(lng)qs+='&language='+lng;
    fetch('/api/admin/conversations'+qs,{{headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(d){{
      var tb=document.getElementById('convs-tbody');tb.innerHTML='';
      (d.conversations||[]).forEach(function(c){{
        var tr=document.createElement('tr');
        tr.style.cursor='pointer';
        tr.onclick=function(){{viewMessages(c.id)}};
        var last=c.last_message_at?c.last_message_at.substring(0,16).replace('T',' '):'—';
        tr.innerHTML='<td style="font-size:.78rem">'+esc(c.session_id.substring(0,8))+'...</td><td>'+esc(c.source)+'</td><td>'+c.message_count+'</td><td style="font-size:.78rem">'+last+'</td>';
        tb.appendChild(tr);
      }});
    }});
  }};

  window.viewMessages=function(convId){{
    fetch('/api/admin/conversations/'+convId+'/messages',{{headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(d){{
      var v=document.getElementById('msg-viewer');v.innerHTML='';
      (d.messages||[]).forEach(function(m){{
        var div=document.createElement('div');
        div.className='msg-item msg-'+m.role;
        var t=m.created_at?m.created_at.substring(11,16):'';
        var meta='<div class="msg-meta">'+t;
        if(m.response_time_ms)meta+=' ('+m.response_time_ms+'ms)';
        if(m.context_chunks)meta+=' | '+m.context_chunks+' chunks';
        meta+='</div>';
        div.innerHTML=esc(m.content)+meta;
        v.appendChild(div);
      }});
      v.scrollTop=v.scrollHeight;
    }});
  }};

  window.loadAnalytics=function(){{
    fetch('/api/admin/analytics',{{headers:hdrs()}})
    .then(function(r){{return r.json()}})
    .then(function(d){{
      var sg=document.getElementById('stats-grid');
      var tc=d.total_conversations||0;var tm=d.total_messages||0;
      sg.innerHTML='<div class="stat-card"><div class="label">Total Conversations</div><div class="value">'+tc+'</div></div>'
        +'<div class="stat-card"><div class="label">Total Messages</div><div class="value">'+tm+'</div></div>'
        +'<div class="stat-card"><div class="label">Avg Msgs / Conv</div><div class="value">'+(tc?(tm/tc).toFixed(1):'0')+'</div></div>';
      var daily=d.daily_last_7||{{}};
      var chart=document.getElementById('daily-chart');chart.innerHTML='';
      var vals=Object.values(daily);var maxV=Math.max.apply(null,vals.length?vals:[1]);
      Object.keys(daily).sort().forEach(function(day){{
        var col=document.createElement('div');col.className='bar-col';
        var h=Math.max((daily[day]/maxV)*120,4);
        col.innerHTML='<div class="bar-value">'+daily[day]+'</div><div class="bar-fill" style="height:'+h+'px"></div><div class="bar-label">'+day.substring(5)+'</div>';
        chart.appendChild(col);
      }});
      var sb=document.getElementById('source-breakdown');sb.innerHTML='';
      var sources=d.by_source||{{}};
      Object.keys(sources).forEach(function(s){{sb.innerHTML+='<div class="breakdown-row"><span>'+esc(s)+'</span><strong>'+sources[s]+'</strong></div>'}});
      var lb=document.getElementById('lang-breakdown');lb.innerHTML='';
      var langs=d.by_language||{{}};
      Object.keys(langs).forEach(function(l){{lb.innerHTML+='<div class="breakdown-row"><span>'+esc(l)+'</span><strong>'+langs[l]+'</strong></div>'}});
    }})
    .catch(function(){{}});
  }};
}})();
</script>
</body>
</html>"""


@admin_page_router.get("/admin")
async def serve_admin():
    return HTMLResponse(
        content=ADMIN_HTML,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )
