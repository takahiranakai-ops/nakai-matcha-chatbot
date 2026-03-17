"""B2B Sales Team section — ported from b2b_page.py."""


def html() -> str:
    return """
<div class="d-flex align-items-center justify-content-between mb-3">
  <h2 style="font-size:1.1rem;font-weight:400;color:#333"><i class="ti ti-users-group" style="margin-right:6px;color:#406546"></i> B2B Virtual Sales Team</h2>
  <button class="btn btn-primary btn-sm" id="pipeline-btn" onclick="runPipeline()"><i class="ti ti-rocket"></i> Run Pipeline</button>
</div>

<ul class="nav nav-tabs" role="tablist">
  <li class="nav-item"><a class="nav-link active" href="#" data-tab="overview">Overview</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="leads">Leads</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="outreach">Outreach</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="analytics">Analytics</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="import">Import</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="discover">Discover</a></li>
  <li class="nav-item"><a class="nav-link" href="#" data-tab="settings">Settings</a></li>
</ul>

<!-- Overview -->
<div class="tab-pane active" id="panel-overview">
  <div class="row row-deck row-cards mb-3" id="seg-cards"></div>
  <div class="row row-deck row-cards mb-3" id="kpi-grid"></div>
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">Daily Activity (Last 30 Days)</h3></div>
    <div class="card-body" id="daily-chart"></div>
  </div>
  <div class="card">
    <div class="card-header"><h3 class="card-title">Recent Leads</h3></div>
    <div class="table-responsive">
      <table class="table table-vcenter table-hover card-table">
        <thead><tr><th>Name</th><th>City</th><th>Segment</th><th>Status</th><th>Added</th></tr></thead>
        <tbody id="recent-leads-body"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Leads -->
<div class="tab-pane" id="panel-leads">
  <div class="row g-2 align-items-center mb-3">
    <div class="col"><input type="text" id="lead-search" class="form-control" placeholder="Search leads..." oninput="debounceLoadLeads()"></div>
    <div class="col-auto">
      <select id="lead-segment" class="form-select" onchange="loadLeads()">
        <option value="">All Segments</option>
        <option value="cafe">Cafe</option>
        <option value="luxury_hotel">Luxury Hotel</option>
        <option value="fine_dining">Fine Dining</option>
      </select>
    </div>
    <div class="col-auto">
      <select id="lead-region" class="form-select" onchange="loadLeads()">
        <option value="">All Regions</option>
        <option value="us_west">US West</option><option value="us_east">US East</option>
        <option value="us_south">US South</option><option value="us_midwest">US Midwest</option>
        <option value="eu_uk">UK &amp; Ireland</option><option value="eu_central">EU Central</option>
        <option value="eu_nordic">EU Nordic</option><option value="eu_med">EU Mediterranean</option>
      </select>
    </div>
    <div class="col-auto">
      <select id="lead-status" class="form-select" onchange="loadLeads()">
        <option value="">All Status</option>
        <option value="new">New</option><option value="researched">Researched</option>
        <option value="contacted">Contacted</option><option value="replied">Replied</option>
        <option value="negotiating">Negotiating</option><option value="won">Won</option><option value="lost">Lost</option>
      </select>
    </div>
    <div class="col-auto"><button class="btn btn-outline-secondary btn-sm" id="export-btn" onclick="exportLeads()">Export Excel</button></div>
  </div>
  <div class="card">
    <div class="table-responsive">
      <table class="table table-vcenter table-hover card-table">
        <thead><tr><th>Name</th><th>City</th><th>Country</th><th>Segment</th><th>Status</th><th>Score</th><th>Site</th><th></th></tr></thead>
        <tbody id="leads-body"></tbody>
      </table>
    </div>
  </div>
  <div class="d-flex justify-content-center align-items-center gap-3 py-3">
    <button class="btn btn-outline-secondary btn-sm" onclick="loadLeads(leadsOffset-100)">Prev</button>
    <span id="leads-count" class="text-muted small"></span>
    <button class="btn btn-outline-secondary btn-sm" onclick="loadLeads(leadsOffset+100)">Next</button>
  </div>
</div>

<!-- Outreach -->
<div class="tab-pane" id="panel-outreach">
  <div class="card">
    <div class="card-header"><h3 class="card-title">Sent Emails</h3></div>
    <div class="table-responsive">
      <table class="table table-vcenter table-hover card-table">
        <thead><tr><th>Subject</th><th>Step</th><th>Status</th><th>Sent</th></tr></thead>
        <tbody id="outreach-body"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Analytics -->
<div class="tab-pane" id="panel-analytics">
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">Conversion Funnel</h3></div>
    <div class="card-body" id="funnel-chart"></div>
  </div>
  <div class="row row-deck row-cards mb-3">
    <div class="col-lg-6">
      <div class="card"><div class="card-header"><h3 class="card-title">Region Performance</h3></div><div class="card-body" id="region-chart"></div></div>
    </div>
    <div class="col-lg-6">
      <div class="card"><div class="card-header"><h3 class="card-title">Lead Score Distribution</h3></div><div class="card-body" id="score-chart"></div></div>
    </div>
  </div>
  <div class="card"><div class="card-header"><h3 class="card-title">High-Score Leads</h3></div><div class="card-body" id="quick-actions"></div></div>
</div>

<!-- Import -->
<div class="tab-pane" id="panel-import">
  <div class="drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
    <div style="font-size:2.5rem;opacity:.3;margin-bottom:16px;">+</div>
    <h3 style="font-size:1rem;font-weight:400;color:#555;margin-bottom:8px;">Drop Excel or CSV here</h3>
    <p class="text-muted small">.xlsx and .csv files supported</p>
  </div>
  <input type="file" id="file-input" accept=".xlsx,.csv" style="display:none" onchange="handleFile(this.files[0])">
  <div id="import-result" class="card" style="display:none"></div>
</div>

<!-- Discover -->
<div class="tab-pane" id="panel-discover">
  <div class="card">
    <div class="card-header"><h3 class="card-title">Discover New Leads</h3></div>
    <div class="card-body">
      <p class="text-muted mb-4">Search for leads by segment, region, and city.</p>
      <div class="row g-2 align-items-end mb-3">
        <div class="col-auto">
          <label class="form-label">Segment</label>
          <select id="disc-segment" class="form-select">
            <option value="cafe">Cafe</option>
            <option value="luxury_hotel">Luxury Hotel</option>
            <option value="fine_dining">Fine Dining</option>
          </select>
        </div>
        <div class="col-auto">
          <label class="form-label">Region</label>
          <select id="disc-region" class="form-select">
            <option value="">Select region</option>
            <option value="us_west">US West</option><option value="us_east">US East</option>
            <option value="us_south">US South</option><option value="us_midwest">US Midwest</option>
            <option value="eu_uk">UK &amp; Ireland</option><option value="eu_central">EU Central</option>
            <option value="eu_nordic">EU Nordic</option><option value="eu_med">EU Mediterranean</option>
          </select>
        </div>
        <div class="col"><label class="form-label">City (optional)</label><input type="text" id="disc-city" class="form-control" placeholder="e.g. New York, NY"></div>
        <div class="col-auto"><label class="form-label">&nbsp;</label><button class="btn btn-primary d-block" id="discover-btn" onclick="runDiscover()">Search</button></div>
      </div>
      <div id="disc-result" class="text-muted small"></div>
    </div>
  </div>
</div>

<!-- Settings -->
<div class="tab-pane" id="panel-settings">
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">Email Templates by Segment</h3></div>
    <div class="card-body">
      <p class="text-muted small mb-3">Edit 3-step outreach emails per segment. Variables: <code>{{cafe_name}}</code> <code>{{city}}</code> <code>{{location}}</code></p>
      <div class="d-flex gap-2 mb-3" id="seg-tabs">
        <button class="seg-tab active" onclick="switchSegment('cafe')"><i class="ti ti-coffee"></i> Cafe</button>
        <button class="seg-tab" onclick="switchSegment('luxury_hotel')"><i class="ti ti-building"></i> Luxury Hotel</button>
        <button class="seg-tab" onclick="switchSegment('fine_dining')"><i class="ti ti-tools-kitchen-2"></i> Fine Dining</button>
      </div>
      <div class="d-flex align-items-center gap-3 mb-3 p-2 rounded" style="background:#f8f8f6;">
        <span class="small fw-bold" id="seg-label">Cafe</span>
        <label class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" id="seg-enabled" onchange="toggleSegment()">
          <span class="form-check-label small" id="seg-enabled-label">Paused</span>
        </label>
      </div>
      <div class="btn-group mb-3" role="group">
        <button class="btn btn-sm btn-primary" id="tpl-btn-1" onclick="showTemplate(1)">Step 1: Initial</button>
        <button class="btn btn-sm btn-outline-secondary" id="tpl-btn-2" onclick="showTemplate(2)">Step 2: Follow-up</button>
        <button class="btn btn-sm btn-outline-secondary" id="tpl-btn-3" onclick="showTemplate(3)">Step 3: Final</button>
      </div>
      <div class="mb-3"><label class="form-label">Subject</label><input type="text" id="tpl-subject" class="form-control" placeholder="Subject template..."></div>
      <div class="mb-3"><label class="form-label">Body</label><textarea id="tpl-body" class="form-control" rows="12" placeholder="Email body template..."></textarea></div>
      <div class="d-flex align-items-center gap-3">
        <button class="btn btn-primary" id="save-tpl-btn" onclick="saveTemplate()">Save</button>
        <span id="tpl-msg" class="small" style="color:#406546;"></span>
      </div>
    </div>
  </div>
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">Test Send</h3></div>
    <div class="card-body">
      <div class="row g-2 align-items-end">
        <div class="col"><label class="form-label">Send to</label><input type="email" id="test-email" class="form-control" placeholder="your@email.com"></div>
        <div class="col-auto"><label class="form-label">Segment</label><select id="test-segment" class="form-select"><option value="cafe">Cafe</option><option value="luxury_hotel">Luxury Hotel</option><option value="fine_dining">Fine Dining</option></select></div>
        <div class="col-auto"><label class="form-label">Step</label><select id="test-step" class="form-select"><option value="1">Step 1</option><option value="2">Step 2</option><option value="3">Step 3</option></select></div>
        <div class="col-auto"><label class="form-label">&nbsp;</label><button class="btn btn-primary d-block" id="test-send-btn" onclick="sendTest()">Test Send</button></div>
      </div>
      <div id="test-msg" class="small mt-2"></div>
    </div>
  </div>
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">PDF Attachment</h3></div>
    <div class="card-body">
      <div id="pdf-status" class="mb-3"></div>
      <div class="d-flex align-items-center gap-2">
        <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('pdf-input').click()">Upload PDF</button>
        <button class="btn btn-sm btn-outline-danger" id="pdf-remove-btn" onclick="removePdf()" style="display:none;">Remove</button>
        <input type="file" id="pdf-input" accept=".pdf" style="display:none" onchange="uploadPdf(this.files[0])">
        <span id="pdf-msg" class="text-muted small"></span>
      </div>
    </div>
  </div>
  <div class="card mb-3">
    <div class="card-header"><h3 class="card-title">Resend Domain</h3></div>
    <div class="card-body">
      <button class="btn btn-outline-secondary btn-sm mb-3" id="resend-check-btn" onclick="checkResendDomain()">Check Status</button>
      <div id="resend-domain-status"></div>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><h3 class="card-title">Pipeline Config</h3></div>
    <div class="card-body">
      <div class="datagrid" style="max-width:500px;">
        <div class="datagrid-item"><div class="datagrid-title">Daily Send Limit</div><div class="datagrid-content" id="cfg-limit">-</div></div>
        <div class="datagrid-item"><div class="datagrid-title">From Email</div><div class="datagrid-content" id="cfg-from">-</div></div>
        <div class="datagrid-item"><div class="datagrid-title">Google Places API</div><div class="datagrid-content" id="cfg-gp">-</div></div>
        <div class="datagrid-item"><div class="datagrid-title">Resend API</div><div class="datagrid-content" id="cfg-resend">-</div></div>
      </div>
    </div>
  </div>
</div>

<!-- Lead Detail Modal -->
<div class="modal modal-blur fade" id="lead-modal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modal-title">Contacts</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body" id="modal-body"></div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/js/tabler.min.js"></script>
<script>
var API='/api/b2b',PWD=sessionStorage.getItem('nakai-admin-pwd')||sessionStorage.getItem('nakai_admin_pw')||'',leadsOffset=0,debounceTimer=null,currentStep=1,currentSegment='cafe';
var allTemplates={},segmentsData=[];
var BADGE_CLASS={'new':'bg-green-lt','researched':'bg-azure-lt','contacted':'bg-orange-lt','replied':'bg-purple-lt','negotiating':'bg-pink-lt','won':'bg-green-lt','lost':'bg-secondary-lt','sent':'bg-azure-lt','opened':'bg-orange-lt','clicked':'bg-purple-lt','bounced':'bg-red-lt','pending':'bg-secondary-lt','unsubscribed':'bg-secondary-lt'};
var STATUS_JA={new:'New',researched:'Researched',contacted:'Contacted',replied:'Replied',negotiating:'Negotiating',won:'Won',lost:'Lost',sent:'Sent',opened:'Opened',clicked:'Clicked',bounced:'Bounced',pending:'Pending',unsubscribed:'Unsubscribed'};
var REGION_JA={us_west:'US West',us_east:'US East',us_south:'US South',us_midwest:'US Midwest',eu_uk:'UK',eu_central:'EU Central',eu_nordic:'Nordic',eu_med:'Mediterranean'};
var SEG_JA={cafe:'Cafe',luxury_hotel:'Luxury Hotel',fine_dining:'Fine Dining'};
var SEG_ICON={cafe:'ti-coffee',luxury_hotel:'ti-building',fine_dining:'ti-tools-kitchen-2'};
var SEG_COLOR={cafe:'#406546',luxury_hotel:'#2c3e50',fine_dining:'#8e3b2e'};

var _dc={};
function cg(k){var e=_dc[k];if(!e)return null;if(Date.now()>e.x){delete _dc[k];return null;}return e.d;}
function cp(k,d,t){_dc[k]={d:d,x:Date.now()+(t||60000)};}
function ci(p){Object.keys(_dc).forEach(function(k){if(k.indexOf(p)===0)delete _dc[k];});}

function showSkel(id,type){
  var el=document.getElementById(id);if(!el)return;
  if(type==='kpi'){el.innerHTML=Array(6).fill(0).map(function(){return '<div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>';}).join('');}
  else if(type==='seg'){el.innerHTML=Array(3).fill(0).map(function(){return '<div class="col-md-4"><div class="skeleton skeleton-kpi"></div></div>';}).join('');}
  else if(type==='table'){el.innerHTML=Array(6).fill(0).map(function(){return '<tr><td colspan="8"><div class="skeleton skeleton-row"></div></td></tr>';}).join('');}
  else if(type==='chart'){el.innerHTML='<div class="skeleton skeleton-chart"></div>';}
}
function btnL(btn,on){if(!btn)return;if(on){btn.classList.add('btn-loading');btn.disabled=true;}else{btn.classList.remove('btn-loading');btn.disabled=false;}}
function hdr(){return{'X-Admin-Password':PWD,'Content-Type':'application/json'};}
function hdrF(){return{'X-Admin-Password':PWD};}

// Tabs
document.querySelectorAll('.nav-tabs .nav-link').forEach(function(tab){
  tab.addEventListener('click',function(e){
    e.preventDefault();var name=tab.dataset.tab;
    document.querySelectorAll('.nav-tabs .nav-link').forEach(function(t){t.classList.toggle('active',t===tab);});
    document.querySelectorAll('.tab-pane').forEach(function(p){p.classList.toggle('active',p.id==='panel-'+name);});
    if(name==='overview'){loadStats();loadSegmentCards();}if(name==='leads')loadLeads();if(name==='outreach')loadOutreach();
    if(name==='analytics')loadAnalytics();if(name==='settings')loadSettings();
  });
});

// Segments
function loadSegmentCards(){
  var c=cg('segments');if(c){renderSegCards(c);return;}
  showSkel('seg-cards','seg');
  fetch(API+'/segments',{headers:hdr()}).then(function(r){return r.json();})
    .then(function(d){segmentsData=d;cp('segments',d,30000);renderSegCards(d);})
    .catch(function(){document.getElementById('seg-cards').innerHTML='';});
}
function renderSegCards(segs){
  document.getElementById('seg-cards').innerHTML=segs.map(function(s){
    var co=SEG_COLOR[s.id]||'#406546';
    return '<div class="col-md-4"><div class="card seg-card"><div class="card-body d-flex align-items-center gap-3">'
      +'<div class="seg-icon" style="background:'+co+';"><i class="ti '+SEG_ICON[s.id]+'"></i></div>'
      +'<div class="flex-fill"><div class="fw-bold" style="font-size:.9rem;">'+esc(s.label)+'</div>'
      +'<div class="text-muted" style="font-size:.75rem;">'+s.leads+' leads &middot; '+s.sent+' sent &middot; '+s.open_rate+'% open</div></div>'
      +'<span class="badge '+(s.enabled?'bg-green-lt':'bg-secondary-lt')+'" style="font-size:.7rem;">'+(s.enabled?'Active':'Paused')+'</span>'
      +'</div></div></div>';
  }).join('');
}

// Overview
function loadStats(){
  var c=cg('stats');if(c){renderOverview(c);return;}
  showSkel('kpi-grid','kpi');showSkel('daily-chart','chart');showSkel('recent-leads-body','table');
  fetch(API+'/stats',{headers:hdr()}).then(function(r){if(!r.ok)throw new Error();return r.json();})
    .then(function(d){cp('stats',d,60000);renderOverview(d);})
    .catch(function(){document.getElementById('kpi-grid').innerHTML='<div class="col-12 text-center text-danger py-4">Failed to load</div>';});
}
function renderOverview(s){
  var grid=document.getElementById('kpi-grid');
  var ts=s.total_sent||0,rp=(s.outreach_by_status||{}).replied||0,ng=(s.leads_by_status||{}).negotiating||0,wn=(s.leads_by_status||{}).won||0,ct=(s.leads_by_status||{}).contacted||0;
  grid.innerHTML=
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">TOTAL LEADS</div><div class="kpi-value">'+(s.total_leads||0).toLocaleString()+'</div><div class="kpi-sub">'+Object.keys(s.leads_by_region||{}).length+' regions</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">CONTACTS</div><div class="kpi-value">'+(s.total_contacts||0).toLocaleString()+'</div><div class="kpi-sub">'+(s.verified_contacts||0)+' verified</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">EMAILS SENT</div><div class="kpi-value">'+ts.toLocaleString()+'</div><div class="kpi-sub">Open rate '+(s.open_rate||0)+'%</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">REPLY RATE</div><div class="kpi-value">'+(s.reply_rate||0)+'%</div><div class="kpi-sub">'+rp+' replies</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">WON DEALS</div><div class="kpi-value">'+wn+'</div><div class="kpi-sub">'+ng+' negotiating</div></div></div></div>'+
    '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">PIPELINE</div><div class="kpi-value">'+(ct+rp+ng)+'</div><div class="kpi-sub">Active leads</div></div></div></div>';
  var trend=s.daily_trend||[],chart=document.getElementById('daily-chart');
  if(!trend.length){chart.innerHTML='<div class="text-center text-muted py-4">No data yet</div>';} else {
    var mx=Math.max.apply(null,trend.map(function(d){return d.emails_sent||0;}).concat([1]));
    chart.innerHTML=trend.slice(-14).map(function(d){return '<div class="chart-bar-row"><div class="chart-bar-label">'+d.date.slice(5)+'</div><div class="chart-bar" style="width:'+(d.emails_sent||0)/mx*100+'%;background:#406546;"></div><div class="chart-bar" style="width:'+(d.opens||0)/mx*100+'%;background:#e67e22;"></div><div class="chart-bar-val">'+(d.emails_sent||0)+' sent / '+(d.opens||0)+' opened</div></div>';}).join('');
  }
  var tb=document.getElementById('recent-leads-body'),rl=s.recent_leads||[];
  if(!rl.length){tb.innerHTML='<tr><td colspan="5" class="text-center text-muted py-4">No leads yet</td></tr>';}
  else{tb.innerHTML=rl.map(function(l){return '<tr onclick="showLeadDetail(\''+l.id+'\')" style="cursor:pointer"><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.city||'')+'</td><td><span class="badge" style="background:'+(SEG_COLOR[l.cafe_type]||'#888')+';color:#fff;font-size:.65rem;">'+(SEG_JA[l.cafe_type]||l.cafe_type||'-')+'</span></td><td><span class="badge '+(BADGE_CLASS[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></td><td>'+timeAgo(l.created_at)+'</td></tr>';}).join('');}
}

// Leads
function debounceLoadLeads(){clearTimeout(debounceTimer);debounceTimer=setTimeout(function(){loadLeads();},300);}
function loadLeads(offset){
  leadsOffset=Math.max(0,offset||0);
  var s=document.getElementById('lead-search').value,r=document.getElementById('lead-region').value,st=document.getElementById('lead-status').value,sg=document.getElementById('lead-segment').value;
  var ck='leads_'+leadsOffset+'_'+s+'_'+r+'_'+st+'_'+sg,cc=cg(ck);if(cc){renderLeads(cc);return;}
  showSkel('leads-body','table');
  var url=API+'/leads?limit=100&offset='+leadsOffset;if(s)url+='&search='+encodeURIComponent(s);if(r)url+='&region='+r;if(st)url+='&status='+st;if(sg)url+='&segment='+sg;
  fetch(url,{headers:hdr()}).then(function(r){if(!r.ok)throw new Error();return r.json();})
    .then(function(d){cp(ck,d,30000);renderLeads(d);})
    .catch(function(){document.getElementById('leads-body').innerHTML='<tr><td colspan="8" class="text-center text-danger py-4">Failed to load</td></tr>';});
}
function renderLeads(data){
  var tb=document.getElementById('leads-body'),leads=data.leads||[];
  document.getElementById('leads-count').textContent=(leadsOffset+1)+'-'+(leadsOffset+leads.length)+' / '+(data.total||0);
  if(!leads.length){tb.innerHTML='<tr><td colspan="8"><div class="text-center text-muted py-5"><div style="font-size:3rem;opacity:.2;margin-bottom:16px;">&#9749;</div><h3 style="font-weight:400;margin-bottom:8px;">No leads found</h3></div></td></tr>';return;}
  tb.innerHTML=leads.map(function(l){return '<tr onclick="showLeadDetail(\''+l.id+'\')" style="cursor:pointer"><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.city||'')+'</td><td>'+esc(l.country||'')+'</td><td><span class="badge" style="background:'+(SEG_COLOR[l.cafe_type]||'#888')+';color:#fff;font-size:.65rem;">'+(SEG_JA[l.cafe_type]||l.cafe_type||'')+'</span></td><td><span class="badge '+(BADGE_CLASS[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></td><td>'+(l.lead_score||0)+'</td><td>'+(l.website?'<a href="'+esc(l.website)+'" target="_blank" style="color:#406546;">Open</a>':'-')+'</td><td><button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation();deleteLead(\''+l.id+'\')">Del</button></td></tr>';}).join('');
}
function deleteLead(id){if(!confirm('Delete this lead?'))return;ci('leads_');ci('segments');fetch(API+'/leads/'+id,{method:'DELETE',headers:hdr()}).then(function(){loadLeads(leadsOffset);});}
function exportLeads(){
  var btn=document.getElementById('export-btn');btnL(btn,true);
  var r=document.getElementById('lead-region').value,st=document.getElementById('lead-status').value;
  var url=API+'/export?';if(r)url+='region='+r+'&';if(st)url+='status='+st+'&';
  fetch(url,{headers:hdr()}).then(function(r){if(!r.ok)throw new Error();return r.blob();})
    .then(function(b){var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='NAKAI_B2B_Leads_'+new Date().toISOString().slice(0,10)+'.xlsx';a.click();URL.revokeObjectURL(a.href);btnL(btn,false);})
    .catch(function(e){alert('Export failed: '+e.message);btnL(btn,false);});
}
function showLeadDetail(id){
  fetch(API+'/leads/'+id+'/contacts',{headers:hdr()}).then(function(r){return r.json();}).then(function(c){
    document.getElementById('modal-title').textContent='Contacts';
    var b=document.getElementById('modal-body');
    if(!c.length){b.innerHTML='<p class="text-muted">No contacts yet.</p>';}
    else{b.innerHTML='<div class="table-responsive"><table class="table table-vcenter"><thead><tr><th>Email</th><th>Source</th><th>Verified</th></tr></thead><tbody>'+c.map(function(x){return '<tr><td>'+esc(x.email)+'</td><td>'+esc(x.source||'')+'</td><td>'+(x.verified?'Yes':'No')+'</td></tr>';}).join('')+'</tbody></table></div>';}
    var m=new bootstrap.Modal(document.getElementById('lead-modal'));m.show();
  });
}

// Outreach
function loadOutreach(){
  var c=cg('outreach');if(c){renderOutreach(c);return;}
  showSkel('outreach-body','table');
  fetch(API+'/outreach?limit=200',{headers:hdr()}).then(function(r){return r.json();}).then(function(d){cp('outreach',d,30000);renderOutreach(d);})
    .catch(function(){document.getElementById('outreach-body').innerHTML='<tr><td colspan="4" class="text-center text-danger py-4">Failed to load</td></tr>';});
}
function renderOutreach(data){
  var tb=document.getElementById('outreach-body');
  if(!data.length){tb.innerHTML='<tr><td colspan="4"><div class="text-center text-muted py-5"><div style="font-size:3rem;opacity:.2;margin-bottom:16px;">&#9993;</div><h3 style="font-weight:400;margin-bottom:8px;">No emails sent yet</h3></div></td></tr>';return;}
  tb.innerHTML=data.map(function(o){return '<tr><td>'+esc(o.subject||'(no subject)')+'</td><td>Step '+(o.sequence_step||1)+'</td><td><span class="badge '+(BADGE_CLASS[o.status]||'bg-secondary-lt')+'">'+(STATUS_JA[o.status]||o.status)+'</span></td><td>'+timeAgo(o.sent_at||o.created_at)+'</td></tr>';}).join('');
}

// Analytics
function loadAnalytics(){
  var c=cg('stats');if(c){renderAnalytics(c);return;}
  showSkel('funnel-chart','chart');showSkel('region-chart','chart');showSkel('score-chart','chart');
  fetch(API+'/stats',{headers:hdr()}).then(function(r){return r.json();}).then(function(d){cp('stats',d,60000);renderAnalytics(d);}).catch(function(){});
}
function renderAnalytics(s){
  var bs=s.leads_by_status||{},funnel=[
    {l:'Total Leads',c:s.total_leads||0,co:'#406546'},{l:'Contacts',c:s.total_contacts||0,co:'#5a8a62'},
    {l:'Emails Sent',c:s.total_sent||0,co:'#e67e22'},{l:'Opened',c:s.total_opens||0,co:'#d4760a'},
    {l:'Replied',c:(s.outreach_by_status||{}).replied||0,co:'#9b59b6'},
    {l:'Negotiating',c:bs.negotiating||0,co:'#e74c3c'},{l:'Won',c:bs.won||0,co:'#27ae60'}
  ];
  var mxF=Math.max.apply(null,funnel.map(function(f){return f.c;}).concat([1])),f0=funnel[0].c||1;
  document.getElementById('funnel-chart').innerHTML=funnel.map(function(f){
    return '<div class="chart-bar-row"><div class="chart-bar-label">'+f.l+'</div><div class="chart-bar" style="width:'+f.c/mxF*100+'%;background:'+f.co+';"></div><div class="chart-bar-val">'+f.c+' ('+(f.c/f0*100).toFixed(1)+'%)</div></div>';
  }).join('');
  var br=s.leads_by_region||{},mxR=Math.max.apply(null,Object.values(br).concat([1]));
  var rKeys=Object.keys(br).sort(function(a,b){return br[b]-br[a];});
  document.getElementById('region-chart').innerHTML=rKeys.length?rKeys.map(function(r){
    return '<div class="chart-bar-row"><div class="chart-bar-label">'+(REGION_JA[r]||r)+'</div><div class="chart-bar" style="width:'+br[r]/mxR*100+'%;background:#406546;"></div><div class="chart-bar-val">'+br[r]+'</div></div>';
  }).join(''):'<div class="text-muted text-center py-4">No data</div>';
  var dist=s.score_distribution||{},mxS=Math.max.apply(null,Object.values(dist).concat([1])),sColors={'0-20':'#e74c3c','21-40':'#e67e22','41-60':'#f1c40f','61-80':'#2ecc71','81-100':'#27ae60'};
  document.getElementById('score-chart').innerHTML=Object.keys(dist).length?Object.keys(dist).map(function(k){
    return '<div class="chart-bar-row"><div class="chart-bar-label">'+k+'</div><div class="chart-bar" style="width:'+dist[k]/mxS*100+'%;background:'+(sColors[k]||'#406546')+';"></div><div class="chart-bar-val">'+dist[k]+'</div></div>';
  }).join(''):'<div class="text-muted text-center py-4">No data</div>';
  var hv=s.high_value_leads||[],qa=document.getElementById('quick-actions');
  if(!hv.length){qa.innerHTML='<p class="text-muted">No high-score leads</p>';}
  else{qa.innerHTML='<div class="row g-2">'+hv.map(function(l){return '<div class="col-sm-6 col-lg-4"><div class="card card-sm"><div class="card-body d-flex align-items-center justify-content-between"><div><strong>'+esc(l.name)+'</strong><br><span class="text-muted small">'+esc(l.city||'')+' &middot; Score: '+(l.lead_score||0)+'</span></div><span class="badge '+(BADGE_CLASS[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></div></div></div>';}).join('')+'</div>';}
}

// Import
var dz=document.getElementById('drop-zone');
dz.addEventListener('dragover',function(e){e.preventDefault();dz.classList.add('drag-over');});
dz.addEventListener('dragleave',function(){dz.classList.remove('drag-over');});
dz.addEventListener('drop',function(e){e.preventDefault();dz.classList.remove('drag-over');if(e.dataTransfer.files.length)handleFile(e.dataTransfer.files[0]);});
function handleFile(file){
  if(!file)return;var fd=new FormData();fd.append('file',file);
  dz.innerHTML='<div style="font-size:2.5rem;opacity:.3;animation:spin 1s linear infinite;margin-bottom:16px;">&#8635;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">Importing...</h3>';
  fetch(API+'/import',{method:'POST',headers:hdrF(),body:fd}).then(function(r){return r.json();})
    .then(function(res){ci('leads_');ci('stats');ci('segments');dz.innerHTML='<div style="font-size:2.5rem;opacity:.3;margin-bottom:16px;">&#10003;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">Import Complete</h3>';var el=document.getElementById('import-result');el.style.display='block';el.innerHTML='<div class="card-body"><p><strong>'+(res.imported||0)+'</strong> imported / '+(res.skipped||0)+' skipped</p></div>';})
    .catch(function(){dz.innerHTML='<div style="font-size:2.5rem;color:#c0392b;margin-bottom:16px;">&#10007;</div><h3 style="font-size:1rem;font-weight:400;color:#555;">Import Failed</h3>';});
}

// Discover
function runDiscover(){
  var btn=document.getElementById('discover-btn');btnL(btn,true);
  var sg=document.getElementById('disc-segment').value,r=document.getElementById('disc-region').value,c=document.getElementById('disc-city').value,res=document.getElementById('disc-result');
  var url=API+'/discover?segment='+sg+'&';
  if(c)url+='city='+encodeURIComponent(c)+'&region='+(r||'us_west');
  else if(r)url+='region='+r;
  else{res.textContent='Enter a region or city name.';btnL(btn,false);return;}
  fetch(url,{method:'POST',headers:hdr()}).then(function(r){return r.json();})
    .then(function(d){res.textContent=d.error||((d.found||0)+' new '+(SEG_JA[sg]||'lead')+'s discovered!');if(d.found>0){ci('leads_');ci('stats');ci('segments');}btnL(btn,false);})
    .catch(function(){res.textContent='Search failed';btnL(btn,false);});
}

// Pipeline
function runPipeline(){
  if(!confirm('Run B2B pipeline now?'))return;
  var btn=document.getElementById('pipeline-btn');btnL(btn,true);
  fetch(API+'/pipeline/run',{method:'POST',headers:hdr()}).then(function(r){return r.json();})
    .then(function(){alert('Pipeline started.');ci('stats');ci('segments');btnL(btn,false);})
    .catch(function(){alert('Pipeline failed to start');btnL(btn,false);});
}

// Settings
function loadSettings(){
  Promise.all([
    fetch(API+'/stats',{headers:hdr()}).then(function(r){return r.json();}),
    fetch(API+'/sequences',{headers:hdr()}).then(function(r){return r.json();}),
    fetch(API+'/attachment',{headers:hdr()}).then(function(r){return r.json();}),
    fetch(API+'/segments',{headers:hdr()}).then(function(r){return r.json();})
  ]).then(function(res){
    var s=res[0];cp('stats',s,60000);
    document.getElementById('cfg-limit').textContent='333/day';
    document.getElementById('cfg-from').textContent='wholesale@nakaimatcha.com';
    document.getElementById('cfg-gp').textContent=s.total_leads>0?'Connected':'Not set';
    document.getElementById('cfg-resend').textContent=s.total_sent>0?'Connected':'Check env vars';
    allTemplates={};(res[1]||[]).forEach(function(t){var nm=t.name||'Default';if(!allTemplates[nm])allTemplates[nm]={};allTemplates[nm][t.step_number]=t;});
    segmentsData=res[3]||[];
    updateSegUI();showTemplate(currentStep);renderPdf(res[2]);
  }).catch(function(e){console.error('Settings load failed',e);});
}
function switchSegment(seg){
  currentSegment=seg;currentStep=1;
  document.querySelectorAll('#seg-tabs .seg-tab').forEach(function(b){b.classList.toggle('active',b.onclick.toString().indexOf(seg)>=0);});
  updateSegUI();showTemplate(1);
}
function updateSegUI(){
  document.getElementById('seg-label').textContent=SEG_JA[currentSegment]||currentSegment;
  var en=false;for(var i=0;i<segmentsData.length;i++){if(segmentsData[i].id===currentSegment){en=segmentsData[i].enabled;break;}}
  document.getElementById('seg-enabled').checked=en;
  document.getElementById('seg-enabled-label').textContent=en?'Active':'Paused';
}
function toggleSegment(){
  var btn=document.getElementById('seg-enabled');
  fetch(API+'/sequences/'+currentSegment+'/toggle',{method:'PUT',headers:hdr()})
    .then(function(r){return r.json();}).then(function(d){
      document.getElementById('seg-enabled-label').textContent=d.enabled?'Active':'Paused';btn.checked=d.enabled;
      for(var i=0;i<segmentsData.length;i++){if(segmentsData[i].id===currentSegment){segmentsData[i].enabled=d.enabled;break;}}ci('segments');
    }).catch(function(){btn.checked=!btn.checked;});
}
function showTemplate(step){
  currentStep=step;[1,2,3].forEach(function(s){var b=document.getElementById('tpl-btn-'+s);b.className=s===step?'btn btn-sm btn-primary':'btn btn-sm btn-outline-secondary';});
  var segTpls=allTemplates[currentSegment]||{};var t=segTpls[step]||{};
  document.getElementById('tpl-subject').value=t.subject_template||'';
  document.getElementById('tpl-body').value=t.body_template||'';
  document.getElementById('tpl-msg').textContent='';
}
function saveTemplate(){
  var btn=document.getElementById('save-tpl-btn');btnL(btn,true);
  var subj=document.getElementById('tpl-subject').value,body=document.getElementById('tpl-body').value;
  fetch(API+'/sequences/'+currentSegment+'/'+currentStep,{method:'PUT',headers:hdr(),body:JSON.stringify({subject_template:subj,body_template:body})})
    .then(function(r){return r.json();}).then(function(){
      document.getElementById('tpl-msg').textContent='Saved!';
      if(!allTemplates[currentSegment])allTemplates[currentSegment]={};
      if(!allTemplates[currentSegment][currentStep])allTemplates[currentSegment][currentStep]={};
      allTemplates[currentSegment][currentStep].subject_template=subj;
      allTemplates[currentSegment][currentStep].body_template=body;
      btnL(btn,false);setTimeout(function(){document.getElementById('tpl-msg').textContent='';},3000);
    }).catch(function(){document.getElementById('tpl-msg').textContent='Save failed';document.getElementById('tpl-msg').style.color='#c0392b';btnL(btn,false);});
}
function sendTest(){
  var btn=document.getElementById('test-send-btn');
  var email=document.getElementById('test-email').value,step=parseInt(document.getElementById('test-step').value),seg=document.getElementById('test-segment').value,msg=document.getElementById('test-msg');
  if(!email){msg.textContent='Enter an email address';msg.style.color='#c0392b';return;}
  btnL(btn,true);msg.textContent='Sending...';msg.style.color='#888';
  var names={cafe:'Sample Cafe',luxury_hotel:'The Grand Hotel',fine_dining:'Le Bistrot'};
  fetch(API+'/test-send',{method:'POST',headers:hdr(),body:JSON.stringify({to_email:email,step:step,cafe_name:names[seg]||'Sample',city:'Portland',cafe_type:seg})})
    .then(function(r){return r.json();}).then(function(d){
      if(d.ok){msg.textContent='Sent: '+d.subject+(d.note?' ('+d.note+')':'');msg.style.color='#406546';}
      else{msg.textContent='Failed: '+(d.error||d.detail||'unknown');msg.style.color='#c0392b';}
      btnL(btn,false);
    }).catch(function(e){msg.textContent='Failed: '+e.message;msg.style.color='#c0392b';btnL(btn,false);});
}
function renderPdf(data){
  var el=document.getElementById('pdf-status'),rm=document.getElementById('pdf-remove-btn');
  if(data.filename){el.innerHTML='<span class="small">Current: <strong>'+esc(data.filename)+'</strong></span>';rm.style.display='inline-block';}
  else{el.innerHTML='<span class="text-muted small">No attachment</span>';rm.style.display='none';}
}
function uploadPdf(file){
  if(!file)return;var msg=document.getElementById('pdf-msg');msg.textContent='Uploading...';
  var fd=new FormData();fd.append('file',file);
  fetch(API+'/attachment/upload',{method:'POST',headers:hdrF(),body:fd}).then(function(r){return r.json();})
    .then(function(d){if(d.ok){msg.textContent=d.filename+' ('+d.size_kb+'KB)';fetch(API+'/attachment',{headers:hdr()}).then(function(r){return r.json()}).then(renderPdf);}else{msg.textContent='Upload failed';msg.style.color='#c0392b';}})
    .catch(function(){msg.textContent='Upload failed';msg.style.color='#c0392b';});
}
function removePdf(){if(!confirm('Remove attachment?'))return;fetch(API+'/attachment',{method:'DELETE',headers:hdr()}).then(function(){fetch(API+'/attachment',{headers:hdr()}).then(function(r){return r.json()}).then(renderPdf);});document.getElementById('pdf-msg').textContent='';}

function checkResendDomain(){
  var btn=document.getElementById('resend-check-btn');btnL(btn,true);
  var el=document.getElementById('resend-domain-status');el.innerHTML='<p class="text-muted small">Checking...</p>';
  fetch(API+'/resend-domain',{headers:hdr()}).then(function(r){return r.json();}).then(function(data){
    btnL(btn,false);
    if(!data.ok){el.innerHTML='<p class="text-danger small">'+esc(data.error)+'</p>';return;}
    var sc=data.status==='verified'?'#406546':'#e67e22',st=data.status==='verified'?'Verified':'Not verified ('+data.status+')';
    var h='<p class="mb-3"><strong>'+esc(data.domain)+'</strong> &mdash; <span style="color:'+sc+';font-weight:600;">'+st+'</span></p>';
    if(data.status==='verified'){h+='<p style="color:#406546;" class="small">Domain verified. Ready to send.</p>';}
    el.innerHTML=h;
  }).catch(function(e){btnL(btn,false);el.innerHTML='<p class="text-danger small">Error: '+e.message+'</p>';});
}

function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):'';}
function timeAgo(ts){if(!ts)return'-';var d=new Date(ts),df=(Date.now()-d.getTime())/1000;if(df<60)return'just now';if(df<3600)return Math.floor(df/60)+'m ago';if(df<86400)return Math.floor(df/3600)+'h ago';if(df<2592000)return Math.floor(df/86400)+'d ago';return Math.floor(df/2592000)+'mo ago';}

// Auto-load
loadStats();loadSegmentCards();setTimeout(loadSettings,100);
</script>
"""
