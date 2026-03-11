"""Email Marketing dashboard for NAKAI.

GET /email → Password-gated email marketing UI with 3 tabs:
  1. Campaigns - Create, edit, preview, send emails
  2. Subscribers - Manage email list
  3. Brand Assets - Logo, colors, photos
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

email_page_router = APIRouter()

EMAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAKAI Email Marketing</title>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--green:#406546;--cream:#F9F0E2;--white:#FFFFFF;--red:#c0392b;--gray:#666;--light:#f5f5f5;--font:'Work Sans',system-ui,sans-serif}
body{font-family:var(--font);background:var(--cream);color:#333;min-height:100vh}

/* Login */
#login-gate{display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-box{background:var(--white);padding:48px;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;max-width:360px;width:90%}
.login-box h2{font-size:1rem;font-weight:500;color:var(--green);margin-bottom:8px;letter-spacing:.08em;text-transform:uppercase}
.login-box p{font-size:.85rem;color:var(--gray);margin-bottom:24px}
.login-box input{width:100%;padding:12px 16px;border:1px solid #ddd;border-radius:8px;font-size:1rem;outline:none;margin-bottom:12px;font-family:var(--font)}
.login-box input:focus{border-color:var(--green)}
.login-box button{width:100%;padding:12px;background:var(--green);color:var(--white);border:none;border-radius:8px;font-size:.9rem;cursor:pointer;font-family:var(--font)}
.login-error{color:var(--red);font-size:.85rem;margin-top:8px;display:none}

/* Dashboard */
#dashboard{display:none}
.topbar{background:var(--green);color:var(--cream);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}
.topbar h1{font-size:.9rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase}
.topbar button{background:rgba(255,255,255,.15);color:var(--cream);border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:.8rem;font-family:var(--font)}
.tabs{display:flex;border-bottom:2px solid #eee;background:var(--white);padding:0 24px}
.tab{padding:14px 20px;font-size:.85rem;font-weight:500;color:var(--gray);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;font-family:var(--font)}
.tab.active{color:var(--green);border-bottom-color:var(--green)}
.panel{display:none;padding:24px;max-width:1200px;margin:0 auto}
.panel.active{display:block}

/* Shared */
table{width:100%;border-collapse:collapse;background:var(--white);border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.06)}
th{background:var(--light);font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--gray);padding:12px 16px;text-align:left}
td{padding:12px 16px;border-top:1px solid #f0f0f0;font-size:.88rem;vertical-align:top}
.btn{padding:8px 16px;border:none;border-radius:8px;font-size:.85rem;font-weight:500;cursor:pointer;font-family:var(--font);transition:opacity .15s}
.btn:hover{opacity:.85}
.btn-green{background:var(--green);color:var(--white)}
.btn-red{background:var(--red);color:var(--white)}
.btn-outline{background:transparent;border:1px solid #ddd;color:#666}
.btn-sm{padding:5px 12px;font-size:.78rem}
.badge{padding:3px 10px;border-radius:12px;font-size:.72rem;font-weight:600}
.badge-draft{background:rgba(102,102,102,.12);color:var(--gray)}
.badge-generating{background:rgba(52,152,219,.12);color:#2980b9}
.badge-ready{background:rgba(46,204,113,.12);color:#27ae60}
.badge-sending{background:rgba(243,156,18,.12);color:#f39c12}
.badge-sent{background:rgba(64,101,70,.12);color:var(--green)}
.badge-failed{background:rgba(192,57,43,.12);color:var(--red)}
.badge-active{background:rgba(64,101,70,.12);color:var(--green)}
.badge-inactive{background:rgba(192,57,43,.12);color:var(--red)}

/* Modal */
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:100}
.modal-bg.show{display:flex}
.modal{background:var(--white);border-radius:16px;padding:32px;max-width:640px;width:92%;max-height:90vh;overflow-y:auto}
.modal h3{font-size:1.1rem;font-weight:600;color:var(--green);margin-bottom:20px}
.modal-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:24px}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:.8rem;font-weight:500;margin-bottom:6px;color:var(--gray)}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px 14px;border:1px solid #ddd;border-radius:8px;font-size:.9rem;font-family:var(--font);outline:none}
.form-group textarea{min-height:100px;resize:vertical}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:var(--green)}

/* Campaign Editor */
.editor-layout{display:grid;grid-template-columns:1fr 380px;gap:24px;margin-top:16px}
@media(max-width:900px){.editor-layout{grid-template-columns:1fr}}
.preview-frame{background:var(--white);border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden}
.preview-frame iframe{width:100%;min-height:600px;border:none}
.editor-panel{background:var(--white);border-radius:12px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.editor-panel h4{font-size:.9rem;font-weight:600;color:var(--green);margin-bottom:16px}
.edit-block{margin-bottom:16px}
.edit-block label{display:block;font-size:.78rem;font-weight:500;color:var(--gray);margin-bottom:4px;text-transform:capitalize}
.edit-block textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:.88rem;font-family:var(--font);resize:vertical;min-height:60px;outline:none}
.edit-block textarea:focus{border-color:var(--green)}
.editor-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}

/* Brand Assets */
.color-row{display:flex;gap:16px;flex-wrap:wrap}
.color-item{display:flex;align-items:center;gap:8px}
.color-item input[type=color]{width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0}
.color-item span{font-size:.82rem;color:var(--gray)}
.photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:12px;margin-top:12px}
.photo-card{position:relative;border-radius:8px;overflow:hidden;aspect-ratio:1;background:var(--light)}
.photo-card img{width:100%;height:100%;object-fit:cover}
.photo-card .del-btn{position:absolute;top:4px;right:4px;background:rgba(0,0,0,.6);color:#fff;border:none;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:.7rem;display:flex;align-items:center;justify-content:center}

/* Stats */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px}
.stat-card{background:var(--white);padding:20px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);text-align:center}
.stat-card .label{font-size:.72rem;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:var(--gray);margin-bottom:4px}
.stat-card .value{font-size:1.6rem;font-weight:600;color:var(--green)}

.toolbar{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.empty-state{text-align:center;padding:60px 20px;color:var(--gray)}
.empty-state p{font-size:.9rem;margin-bottom:16px}
.loading{text-align:center;padding:40px;color:var(--gray);font-size:.9rem}
</style>
</head>
<body>

<!-- Login Gate -->
<div id="login-gate">
<div class="login-box">
  <h2>NAKAI Email</h2>
  <p>Email marketing dashboard</p>
  <input type="password" id="pwd" placeholder="Admin password" onkeydown="if(event.key==='Enter')login()">
  <button onclick="login()">Sign In</button>
  <div class="login-error" id="login-err">Invalid password</div>
</div>
</div>

<!-- Dashboard -->
<div id="dashboard">
<div class="topbar">
  <h1>NAKAI Email Marketing</h1>
  <button onclick="logout()">Logout</button>
</div>
<div class="tabs">
  <div class="tab active" onclick="switchTab('campaigns')">Campaigns</div>
  <div class="tab" onclick="switchTab('subscribers')">Subscribers</div>
  <div class="tab" onclick="switchTab('brand')">Brand Assets</div>
</div>

<!-- Campaigns Panel -->
<div class="panel active" id="panel-campaigns">
  <div class="toolbar">
    <button class="btn btn-green" onclick="showNewCampaign()">+ New Campaign</button>
  </div>
  <div id="campaigns-list"><div class="loading">Loading...</div></div>
  <!-- Campaign Editor (hidden by default) -->
  <div id="campaign-editor" style="display:none">
    <div class="toolbar">
      <button class="btn btn-outline btn-sm" onclick="backToCampaigns()">&larr; Back</button>
      <span id="editor-campaign-name" style="font-weight:500;font-size:.9rem"></span>
      <span id="editor-status-badge"></span>
    </div>
    <div class="form-group" style="max-width:500px">
      <label>Subject Line</label>
      <input type="text" id="editor-subject" placeholder="Email subject...">
    </div>
    <div class="editor-layout">
      <div class="preview-frame">
        <iframe id="preview-iframe"></iframe>
      </div>
      <div class="editor-panel">
        <h4>Edit Text</h4>
        <div id="editable-blocks"></div>
        <div class="editor-actions">
          <button class="btn btn-green" onclick="saveCampaign()">Save</button>
          <button class="btn btn-outline" onclick="sendTest()">Send Test</button>
          <button class="btn btn-outline" onclick="regenerateDesign()">Regenerate</button>
          <button class="btn btn-green" onclick="sendCampaign()" id="send-btn">Send to All</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Subscribers Panel -->
<div class="panel" id="panel-subscribers">
  <div class="toolbar">
    <button class="btn btn-green" onclick="showAddSubscriber()">+ Add Subscriber</button>
    <button class="btn btn-outline" onclick="showImportCSV()">Import CSV</button>
    <select id="sub-tag-filter" onchange="loadSubscribers()">
      <option value="">All Tags</option>
    </select>
  </div>
  <div id="subscribers-list"><div class="loading">Loading...</div></div>
</div>

<!-- Brand Assets Panel -->
<div class="panel" id="panel-brand">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
    <div>
      <div class="form-group">
        <label>Logo URL</label>
        <input type="text" id="brand-logo" placeholder="https://...">
        <div style="margin-top:8px"><img id="logo-preview" style="max-height:60px;display:none"></div>
      </div>
      <div class="form-group">
        <label>Colors</label>
        <div class="color-row">
          <div class="color-item"><input type="color" id="color-primary" value="#406546"><span>Primary</span></div>
          <div class="color-item"><input type="color" id="color-secondary" value="#F9F0E2"><span>Secondary</span></div>
          <div class="color-item"><input type="color" id="color-accent" value="#FFFFFF"><span>Accent</span></div>
          <div class="color-item"><input type="color" id="color-text" value="#1a1a1a"><span>Text</span></div>
        </div>
      </div>
      <div class="form-group">
        <label>Font Family</label>
        <input type="text" id="brand-font" value="Work Sans, Helvetica, Arial, sans-serif">
      </div>
      <div class="form-group">
        <label>Footer Text</label>
        <input type="text" id="brand-footer" value="NAKAI Matcha | Kagoshima, Japan">
      </div>
      <button class="btn btn-green" onclick="saveBrandAssets()">Save Brand Settings</button>
    </div>
    <div>
      <div class="form-group">
        <label>Product Photos</label>
        <input type="file" id="photo-upload" accept="image/*" onchange="uploadPhoto()">
      </div>
      <div class="photo-grid" id="photo-grid"></div>
    </div>
  </div>
</div>
</div>

<!-- New Campaign Modal -->
<div class="modal-bg" id="modal-new-campaign">
<div class="modal">
  <h3>New Campaign</h3>
  <div class="form-group"><label>Campaign Name</label><input type="text" id="new-camp-name" placeholder="e.g. Spring Collection Launch"></div>
  <div class="form-group"><label>Describe your email</label><textarea id="new-camp-desc" placeholder="e.g. 新商品の発売お知らせメール。春らしい明るいデザインで、JU-NANA 17の写真を使いたい"></textarea></div>
  <div class="form-group"><label>Target Language</label>
    <select id="new-camp-lang"><option value="en">English</option><option value="ja">Japanese</option></select>
  </div>
  <div class="modal-actions">
    <button class="btn btn-outline" onclick="closeModal('modal-new-campaign')">Cancel</button>
    <button class="btn btn-green" id="gen-btn" onclick="createCampaign()">Generate Design</button>
  </div>
</div>
</div>

<!-- Add Subscriber Modal -->
<div class="modal-bg" id="modal-add-sub">
<div class="modal">
  <h3>Add Subscriber</h3>
  <div class="form-group"><label>Email</label><input type="email" id="new-sub-email" placeholder="email@example.com"></div>
  <div class="form-group"><label>Name</label><input type="text" id="new-sub-name" placeholder="John Doe"></div>
  <div class="form-group"><label>Tags (comma-separated)</label><input type="text" id="new-sub-tags" placeholder="newsletter, vip"></div>
  <div class="form-group"><label>Language</label>
    <select id="new-sub-lang"><option value="en">English</option><option value="ja">Japanese</option></select>
  </div>
  <div class="modal-actions">
    <button class="btn btn-outline" onclick="closeModal('modal-add-sub')">Cancel</button>
    <button class="btn btn-green" onclick="addSubscriber()">Add</button>
  </div>
</div>
</div>

<!-- CSV Import Modal -->
<div class="modal-bg" id="modal-csv">
<div class="modal">
  <h3>Import Subscribers from CSV</h3>
  <p style="font-size:.85rem;color:var(--gray);margin-bottom:16px">CSV columns: email, name, tags, language</p>
  <input type="file" id="csv-file" accept=".csv">
  <div class="modal-actions">
    <button class="btn btn-outline" onclick="closeModal('modal-csv')">Cancel</button>
    <button class="btn btn-green" onclick="importCSV()">Import</button>
  </div>
</div>
</div>

<!-- Send Test Modal -->
<div class="modal-bg" id="modal-test">
<div class="modal">
  <h3>Send Test Email</h3>
  <div class="form-group"><label>Send to</label><input type="email" id="test-email" placeholder="your@email.com"></div>
  <div class="modal-actions">
    <button class="btn btn-outline" onclick="closeModal('modal-test')">Cancel</button>
    <button class="btn btn-green" onclick="doSendTest()">Send</button>
  </div>
</div>
</div>

<script>
let PWD='';
let currentCampaignId=null;
let currentCampaign=null;

// ── Auth ──
function login(){
  PWD=document.getElementById('pwd').value;
  api('GET','/api/email/brand-assets').then(r=>{
    if(r.ok){document.getElementById('login-gate').style.display='none';document.getElementById('dashboard').style.display='block';loadAll();}
    else{document.getElementById('login-err').style.display='block';}
  });
}
function logout(){PWD='';location.reload();}

async function api(method,path,body){
  const opts={method,headers:{'X-Admin-Password':PWD,'Content-Type':'application/json'}};
  if(body)opts.body=JSON.stringify(body);
  const r=await fetch(path,opts);
  const data=r.ok?await r.json():null;
  return{ok:r.ok,status:r.status,data};
}
async function apiForm(method,path,formData){
  const r=await fetch(path,{method,headers:{'X-Admin-Password':PWD},body:formData});
  const data=r.ok?await r.json():null;
  return{ok:r.ok,data};
}

// ── Tabs ──
function switchTab(name){
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',['campaigns','subscribers','brand'][i]===name));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  if(name==='campaigns')backToCampaigns();
}

function loadAll(){loadCampaigns();loadSubscribers();loadBrandAssets();}

// ── Campaigns ──
async function loadCampaigns(){
  const r=await api('GET','/api/email/campaigns');
  const el=document.getElementById('campaigns-list');
  if(!r.ok||!r.data||r.data.length===0){
    el.innerHTML='<div class="empty-state"><p>No campaigns yet</p><button class="btn btn-green" onclick="showNewCampaign()">Create your first campaign</button></div>';
    return;
  }
  let html='<table><thead><tr><th>Name</th><th>Status</th><th>Subject</th><th>Sent</th><th>Actions</th></tr></thead><tbody>';
  for(const c of r.data){
    const stats=c.stats||{};
    const sentCount=stats.sent||0;
    html+=`<tr>
      <td><a href="#" onclick="openCampaign('${c.id}');return false" style="color:var(--green);text-decoration:none;font-weight:500">${esc(c.name)}</a></td>
      <td><span class="badge badge-${c.status}">${c.status}</span></td>
      <td>${esc(c.subject||'—')}</td>
      <td>${sentCount>0?sentCount:'—'}</td>
      <td><button class="btn btn-outline btn-sm" onclick="deleteCampaign('${c.id}')">Delete</button></td>
    </tr>`;
  }
  html+='</tbody></table>';
  el.innerHTML=html;
}

function showNewCampaign(){document.getElementById('modal-new-campaign').classList.add('show');}
function closeModal(id){document.getElementById(id).classList.remove('show');}

async function createCampaign(){
  const name=document.getElementById('new-camp-name').value.trim();
  const desc=document.getElementById('new-camp-desc').value.trim();
  const lang=document.getElementById('new-camp-lang').value;
  if(!name||!desc){alert('Name and description are required');return;}
  const btn=document.getElementById('gen-btn');
  btn.textContent='Generating...';btn.disabled=true;
  const r=await api('POST','/api/email/campaigns',{name,description:desc,target_language:lang});
  btn.textContent='Generate Design';btn.disabled=false;
  closeModal('modal-new-campaign');
  if(r.ok){openCampaignData(r.data);}else{alert('Failed to create campaign');}
}

async function openCampaign(id){
  const r=await api('GET','/api/email/campaigns/'+id);
  if(r.ok)openCampaignData(r.data);
}

function openCampaignData(c){
  currentCampaignId=c.id;
  currentCampaign=c;
  document.getElementById('campaigns-list').style.display='none';
  document.querySelector('#panel-campaigns .toolbar').style.display='none';
  document.getElementById('campaign-editor').style.display='block';
  document.getElementById('editor-campaign-name').textContent=c.name;
  document.getElementById('editor-status-badge').innerHTML=`<span class="badge badge-${c.status}">${c.status}</span>`;
  document.getElementById('editor-subject').value=c.subject||'';

  // Preview
  const iframe=document.getElementById('preview-iframe');
  iframe.srcdoc=c.html_content||'<p style="padding:40px;color:#999;text-align:center">No content generated yet</p>';

  // Editable blocks
  const blocks=c.editable_blocks||[];
  const el=document.getElementById('editable-blocks');
  if(blocks.length===0){
    el.innerHTML='<p style="color:var(--gray);font-size:.85rem">No editable text blocks found</p>';
  }else{
    el.innerHTML=blocks.map(b=>`<div class="edit-block">
      <label>${b.name}</label>
      <textarea data-block="${b.name}" placeholder="${esc(b.placeholder)}">${esc(b.current_text)}</textarea>
    </div>`).join('');
  }
}

function backToCampaigns(){
  currentCampaignId=null;currentCampaign=null;
  document.getElementById('campaign-editor').style.display='none';
  document.getElementById('campaigns-list').style.display='block';
  document.querySelector('#panel-campaigns .toolbar').style.display='flex';
  loadCampaigns();
}

async function saveCampaign(){
  if(!currentCampaignId)return;
  const subject=document.getElementById('editor-subject').value.trim();
  const edits={};
  document.querySelectorAll('#editable-blocks textarea').forEach(ta=>{
    edits[ta.dataset.block]=ta.value;
  });
  const r=await api('PATCH','/api/email/campaigns/'+currentCampaignId,{subject,edits});
  if(r.ok){openCampaignData(r.data);alert('Saved!');}else{alert('Save failed');}
}

function sendTest(){document.getElementById('modal-test').classList.add('show');}
async function doSendTest(){
  const email=document.getElementById('test-email').value.trim();
  if(!email){alert('Enter email');return;}
  // Ensure subject is saved first
  const subject=document.getElementById('editor-subject').value.trim();
  if(subject)await api('PATCH','/api/email/campaigns/'+currentCampaignId,{subject});
  const r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/send-test',{email});
  closeModal('modal-test');
  if(r.ok)alert('Test email sent!');else alert('Failed to send test');
}

async function regenerateDesign(){
  if(!currentCampaignId)return;
  if(!confirm('This will regenerate the design. Continue?'))return;
  document.getElementById('editor-status-badge').innerHTML='<span class="badge badge-generating">generating...</span>';
  const r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/regenerate');
  if(r.ok)openCampaignData(r.data);else alert('Regeneration failed');
}

async function sendCampaign(){
  if(!currentCampaignId)return;
  const subject=document.getElementById('editor-subject').value.trim();
  if(!subject){alert('Subject is required before sending');return;}
  // Save subject first
  await api('PATCH','/api/email/campaigns/'+currentCampaignId,{subject});
  if(!confirm('Send this campaign to ALL active subscribers?'))return;
  const r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/send');
  if(r.ok){
    alert('Campaign is being sent!');
    // Poll for completion
    pollCampaignStatus(currentCampaignId);
  }else{alert('Failed: '+(r.data?.detail||'unknown error'));}
}

async function pollCampaignStatus(id){
  for(let i=0;i<30;i++){
    await new Promise(r=>setTimeout(r,2000));
    const r=await api('GET','/api/email/campaigns/'+id);
    if(r.ok&&r.data.status!=='sending'){
      if(currentCampaignId===id)openCampaignData(r.data);
      return;
    }
  }
}

async function deleteCampaign(id){
  if(!confirm('Delete this campaign?'))return;
  await api('DELETE','/api/email/campaigns/'+id);
  loadCampaigns();
}

// ── Subscribers ──
async function loadSubscribers(){
  const tag=document.getElementById('sub-tag-filter').value;
  const r=await api('GET','/api/email/subscribers'+(tag?'?tag='+tag:''));
  const el=document.getElementById('subscribers-list');
  if(!r.ok||!r.data||r.data.length===0){
    el.innerHTML='<div class="empty-state"><p>No subscribers yet</p></div>';
    return;
  }
  // Collect all tags for filter
  const allTags=new Set();
  r.data.forEach(s=>(s.tags||[]).forEach(t=>allTags.add(t)));
  const sel=document.getElementById('sub-tag-filter');
  const currentVal=sel.value;
  sel.innerHTML='<option value="">All Tags</option>'+[...allTags].sort().map(t=>`<option value="${t}"${t===currentVal?' selected':''}>${t}</option>`).join('');

  let html='<table><thead><tr><th>Email</th><th>Name</th><th>Tags</th><th>Lang</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
  for(const s of r.data){
    const tags=(s.tags||[]).map(t=>`<span class="badge badge-active" style="margin-right:4px">${esc(t)}</span>`).join('');
    html+=`<tr>
      <td>${esc(s.email)}</td>
      <td>${esc(s.name||'—')}</td>
      <td>${tags||'—'}</td>
      <td>${s.language||'en'}</td>
      <td><span class="badge badge-${s.is_active?'active':'inactive'}">${s.is_active?'Active':'Unsubscribed'}</span></td>
      <td><button class="btn btn-outline btn-sm" onclick="deleteSubscriber('${s.id}')">Delete</button></td>
    </tr>`;
  }
  html+='</tbody></table>';
  el.innerHTML=html;
}

function showAddSubscriber(){document.getElementById('modal-add-sub').classList.add('show');}
async function addSubscriber(){
  const email=document.getElementById('new-sub-email').value.trim();
  const name=document.getElementById('new-sub-name').value.trim();
  const tagsStr=document.getElementById('new-sub-tags').value.trim();
  const lang=document.getElementById('new-sub-lang').value;
  if(!email){alert('Email is required');return;}
  const tags=tagsStr?tagsStr.split(',').map(t=>t.trim()).filter(Boolean):[];
  const r=await api('POST','/api/email/subscribers',{email,name,tags,language:lang});
  closeModal('modal-add-sub');
  if(r.ok){loadSubscribers();}else{alert('Failed (may already exist)');}
}

function showImportCSV(){document.getElementById('modal-csv').classList.add('show');}
async function importCSV(){
  const file=document.getElementById('csv-file').files[0];
  if(!file){alert('Select a CSV file');return;}
  const fd=new FormData();fd.append('file',file);
  const r=await apiForm('POST','/api/email/subscribers/import',fd);
  closeModal('modal-csv');
  if(r.ok){
    const msg=`Imported: ${r.data.imported}`;
    if(r.data.errors?.length)alert(msg+'\\nErrors: '+r.data.errors.join(', '));
    else alert(msg);
    loadSubscribers();
  }else{alert('Import failed');}
}

async function deleteSubscriber(id){
  if(!confirm('Delete this subscriber?'))return;
  await api('DELETE','/api/email/subscribers/'+id);
  loadSubscribers();
}

// ── Brand Assets ──
async function loadBrandAssets(){
  const r=await api('GET','/api/email/brand-assets');
  if(!r.ok)return;
  const a=r.data;
  document.getElementById('brand-logo').value=a.logo_url||'';
  updateLogoPreview();
  const c=a.colors||{};
  document.getElementById('color-primary').value=c.primary||'#406546';
  document.getElementById('color-secondary').value=c.secondary||'#F9F0E2';
  document.getElementById('color-accent').value=c.accent||'#FFFFFF';
  document.getElementById('color-text').value=c.text||'#1a1a1a';
  document.getElementById('brand-font').value=a.font_family||'Work Sans, Helvetica, Arial, sans-serif';
  document.getElementById('brand-footer').value=a.footer_text||'NAKAI Matcha | Kagoshima, Japan';
  renderPhotos(a.photos||[]);
}

function updateLogoPreview(){
  const url=document.getElementById('brand-logo').value;
  const img=document.getElementById('logo-preview');
  if(url){img.src=url;img.style.display='block';}else{img.style.display='none';}
}
document.getElementById('brand-logo').addEventListener('input',updateLogoPreview);

function renderPhotos(photos){
  const el=document.getElementById('photo-grid');
  el.innerHTML=photos.map((p,i)=>`<div class="photo-card">
    <img src="${p.url}" alt="${esc(p.label||'')}">
    <button class="del-btn" onclick="deletePhoto(${i})">x</button>
  </div>`).join('');
}

async function saveBrandAssets(){
  const data={
    logo_url:document.getElementById('brand-logo').value.trim(),
    colors:{
      primary:document.getElementById('color-primary').value,
      secondary:document.getElementById('color-secondary').value,
      accent:document.getElementById('color-accent').value,
      text:document.getElementById('color-text').value
    },
    font_family:document.getElementById('brand-font').value.trim(),
    footer_text:document.getElementById('brand-footer').value.trim()
  };
  const r=await api('POST','/api/email/brand-assets',data);
  if(r.ok)alert('Saved!');else alert('Failed to save');
}

async function uploadPhoto(){
  const file=document.getElementById('photo-upload').files[0];
  if(!file)return;
  const fd=new FormData();fd.append('file',file);fd.append('label',file.name);
  const r=await apiForm('POST','/api/email/brand-assets/photo',fd);
  if(r.ok){loadBrandAssets();document.getElementById('photo-upload').value='';}
  else alert('Upload failed');
}

async function deletePhoto(idx){
  if(!confirm('Delete this photo?'))return;
  await api('DELETE','/api/email/brand-assets/photo/'+idx);
  loadBrandAssets();
}

// ── Helpers ──
function esc(s){if(!s)return'';const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
</script>
</body>
</html>"""


@email_page_router.get("/email", response_class=HTMLResponse)
async def email_dashboard():
    return HTMLResponse(EMAIL_HTML)
