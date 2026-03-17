"""Home section — unified KPI overview + quick actions."""


def html() -> str:
    return """
<div class="row row-deck row-cards mb-3" id="home-kpis">
  <div class="col-12">
    <div class="d-flex align-items-center justify-content-between mb-3">
      <h2 style="font-size:1.1rem;font-weight:400;color:#333">Overview</h2>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-secondary" onclick="homeRefresh()">Refresh</button>
      </div>
    </div>
  </div>
</div>

<!-- KPI Grid -->
<div class="row row-deck row-cards mb-4" id="home-kpi-grid">
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
  <div class="col-sm-6 col-lg-2"><div class="skeleton skeleton-kpi"></div></div>
</div>

<!-- Quick Actions -->
<div class="card mb-4">
  <div class="card-header"><h3 class="card-title">Quick Actions</h3></div>
  <div class="card-body">
    <div class="d-flex gap-2 flex-wrap">
      <button class="btn btn-primary btn-sm" onclick="homeRunPipeline()"><i class="ti ti-rocket"></i> Run B2B Pipeline</button>
      <button class="btn btn-outline-primary btn-sm" onclick="homeSyncShopify()"><i class="ti ti-refresh"></i> Sync Shopify</button>
      <button class="btn btn-outline-primary btn-sm" onclick="homeReingest()"><i class="ti ti-database"></i> Re-ingest Knowledge</button>
      <button class="btn btn-outline-secondary btn-sm" onclick="showSection('b2b')"><i class="ti ti-users-group"></i> Go to B2B</button>
      <button class="btn btn-outline-secondary btn-sm" onclick="showSection('email')"><i class="ti ti-mail"></i> Go to Email</button>
    </div>
  </div>
</div>

<!-- Two-column: B2B + Email Summary -->
<div class="row row-deck row-cards mb-4">
  <div class="col-lg-6">
    <div class="card">
      <div class="card-header">
        <h3 class="card-title"><i class="ti ti-users-group" style="margin-right:6px;color:#406546"></i> B2B Sales Pipeline</h3>
        <a class="ms-auto" href="#b2b" style="font-size:.78rem;color:#406546;text-decoration:none">View All &rarr;</a>
      </div>
      <div class="card-body" id="home-b2b-summary">
        <div class="skeleton skeleton-chart"></div>
      </div>
    </div>
  </div>
  <div class="col-lg-6">
    <div class="card">
      <div class="card-header">
        <h3 class="card-title"><i class="ti ti-mail" style="margin-right:6px;color:#406546"></i> Email Marketing</h3>
        <a class="ms-auto" href="#email" style="font-size:.78rem;color:#406546;text-decoration:none">View All &rarr;</a>
      </div>
      <div class="card-body" id="home-email-summary">
        <div class="skeleton skeleton-chart"></div>
      </div>
    </div>
  </div>
</div>

<!-- Recent Activity -->
<div class="card">
  <div class="card-header"><h3 class="card-title">Recent B2B Leads</h3></div>
  <div class="table-responsive">
    <table class="table table-vcenter table-hover card-table">
      <thead><tr><th>Name</th><th>City</th><th>Segment</th><th>Status</th><th>Added</th></tr></thead>
      <tbody id="home-recent-leads"></tbody>
    </table>
  </div>
</div>

<script>
(function(){
  var PWD = sessionStorage.getItem('nakai-admin-pwd') || sessionStorage.getItem('nakai_admin_pw') || '';
  var H = {'X-Admin-Password': PWD, 'Content-Type': 'application/json'};
  var SEG_JA = {cafe:'Cafe',luxury_hotel:'Luxury Hotel',fine_dining:'Fine Dining'};
  var SEG_COLOR = {cafe:'#406546',luxury_hotel:'#2c3e50',fine_dining:'#8e3b2e'};
  var STATUS_JA = {new:'New',researched:'Researched',contacted:'Contacted',replied:'Replied',negotiating:'Negotiating',won:'Won',lost:'Lost'};
  var BADGE = {'new':'bg-green-lt','researched':'bg-azure-lt','contacted':'bg-orange-lt','replied':'bg-purple-lt','negotiating':'bg-pink-lt','won':'bg-green-lt','lost':'bg-secondary-lt'};
  function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):'';}
  function timeAgo(ts){if(!ts)return'-';var df=(Date.now()-new Date(ts).getTime())/1000;if(df<60)return'just now';if(df<3600)return Math.floor(df/60)+'m ago';if(df<86400)return Math.floor(df/3600)+'h ago';return Math.floor(df/86400)+'d ago';}

  // Load B2B stats
  fetch('/api/b2b/stats', {headers: H})
    .then(function(r){return r.json()})
    .then(function(s){
      var ts=s.total_sent||0,rp=(s.outreach_by_status||{}).replied||0,ng=(s.leads_by_status||{}).negotiating||0,wn=(s.leads_by_status||{}).won||0,ct=(s.leads_by_status||{}).contacted||0;
      document.getElementById('home-kpi-grid').innerHTML=
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">TOTAL LEADS</div><div class="kpi-value">'+(s.total_leads||0).toLocaleString()+'</div><div class="kpi-sub">B2B pipeline</div></div></div></div>'+
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">CONTACTS</div><div class="kpi-value">'+(s.total_contacts||0).toLocaleString()+'</div><div class="kpi-sub">'+(s.verified_contacts||0)+' verified</div></div></div></div>'+
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">EMAILS SENT</div><div class="kpi-value">'+ts.toLocaleString()+'</div><div class="kpi-sub">Open rate '+(s.open_rate||0)+'%</div></div></div></div>'+
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">REPLY RATE</div><div class="kpi-value">'+(s.reply_rate||0)+'%</div><div class="kpi-sub">'+rp+' replies</div></div></div></div>'+
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">WON DEALS</div><div class="kpi-value">'+wn+'</div><div class="kpi-sub">'+ng+' negotiating</div></div></div></div>'+
        '<div class="col-sm-6 col-lg-2"><div class="card card-sm"><div class="card-body"><div class="kpi-label">PIPELINE</div><div class="kpi-value">'+(ct+rp+ng)+'</div><div class="kpi-sub">Active leads</div></div></div></div>';

      // B2B summary
      var bs = s.leads_by_status||{};
      var summary = '<div class="d-flex flex-wrap gap-3">';
      ['new','researched','contacted','replied','negotiating','won'].forEach(function(st){
        summary += '<div><span class="badge '+(BADGE[st]||'bg-secondary-lt')+'">'+STATUS_JA[st]+'</span> <strong>'+(bs[st]||0)+'</strong></div>';
      });
      summary += '</div>';
      if(s.daily_trend && s.daily_trend.length > 0){
        var trend = s.daily_trend.slice(-7);
        var mx = Math.max.apply(null, trend.map(function(d){return d.emails_sent||0}).concat([1]));
        summary += '<div style="margin-top:16px">';
        trend.forEach(function(d){
          summary += '<div class="chart-bar-row"><div class="chart-bar-label">'+d.date.slice(5)+'</div><div class="chart-bar" style="width:'+(d.emails_sent||0)/mx*100+'%;background:#406546;"></div><div class="chart-bar-val">'+(d.emails_sent||0)+' sent</div></div>';
        });
        summary += '</div>';
      }
      document.getElementById('home-b2b-summary').innerHTML = summary || '<p class="text-muted">No data yet</p>';

      // Recent leads
      var rl = s.recent_leads||[];
      var tb = document.getElementById('home-recent-leads');
      if(!rl.length){tb.innerHTML='<tr><td colspan="5" class="text-center text-muted py-4">No leads yet</td></tr>';}
      else{tb.innerHTML=rl.slice(0,8).map(function(l){
        return '<tr><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.city||'')+'</td><td><span class="badge" style="background:'+(SEG_COLOR[l.cafe_type]||'#888')+';color:#fff;font-size:.65rem;">'+(SEG_JA[l.cafe_type]||l.cafe_type||'-')+'</span></td><td><span class="badge '+(BADGE[l.status]||'bg-secondary-lt')+'">'+(STATUS_JA[l.status]||l.status)+'</span></td><td>'+timeAgo(l.created_at)+'</td></tr>';
      }).join('');}
    })
    .catch(function(){
      document.getElementById('home-kpi-grid').innerHTML='<div class="col-12"><div class="card card-sm"><div class="card-body text-center text-muted">Could not load B2B stats</div></div></div>';
    });

  // Load email summary
  fetch('/api/email/campaigns', {headers: H})
    .then(function(r){return r.json()})
    .then(function(camps){
      var html = '';
      if(!camps || camps.length === 0){
        html = '<p class="text-muted">No campaigns yet</p>';
      } else {
        html = '<div class="table-responsive"><table class="table table-vcenter table-sm"><thead><tr><th>Campaign</th><th>Status</th></tr></thead><tbody>';
        camps.slice(0,5).forEach(function(c){
          html += '<tr><td>'+esc(c.name)+'</td><td><span class="badge '+(c.status==='sent'?'bg-green-lt':'bg-azure-lt')+'">'+c.status+'</span></td></tr>';
        });
        html += '</tbody></table></div>';
      }
      document.getElementById('home-email-summary').innerHTML = html;
    })
    .catch(function(){
      document.getElementById('home-email-summary').innerHTML='<p class="text-muted">Could not load email data</p>';
    });

  // Quick actions
  window.homeRefresh = function(){ location.reload(); };
  window.homeRunPipeline = function(){
    if(!confirm('Run B2B pipeline now?'))return;
    fetch('/api/b2b/pipeline/run',{method:'POST',headers:H}).then(function(){alert('Pipeline started!');}).catch(function(){alert('Failed');});
  };
  window.homeSyncShopify = function(){
    if(!confirm('Sync Shopify customers?'))return;
    fetch('/api/email/subscribers/sync-shopify',{method:'POST',headers:H}).then(function(r){return r.json()}).then(function(d){alert('Synced: '+(d.synced||0)+', Skipped: '+(d.skipped||0));}).catch(function(){alert('Sync failed');});
  };
  window.homeReingest = function(){
    if(!confirm('Re-ingest all knowledge?'))return;
    fetch('/api/admin/reingest',{method:'POST',headers:H}).then(function(r){return r.json()}).then(function(d){alert('Re-ingestion '+d.status);}).catch(function(){alert('Failed');});
  };
})();
</script>
"""
