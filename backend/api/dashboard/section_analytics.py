"""Analytics section — Chat analytics, AI visibility, Wholesale leads."""


def html() -> str:
    return """
<!-- Analytics Sub-Tabs -->
<div class="sub-tabs">
  <div class="sub-tab active" onclick="anSwitchTab('chat')">Chat Analytics</div>
  <div class="sub-tab" onclick="anSwitchTab('ai')">AI Visibility</div>
  <div class="sub-tab" onclick="anSwitchTab('leads')">Wholesale Leads</div>
</div>

<!-- Chat Analytics Panel -->
<div class="sub-panel active" id="an-panel-chat">
  <div class="row row-deck row-cards mb-4" id="an-stats-grid">
    <div class="col-sm-4"><div class="skeleton skeleton-kpi"></div></div>
    <div class="col-sm-4"><div class="skeleton skeleton-kpi"></div></div>
    <div class="col-sm-4"><div class="skeleton skeleton-kpi"></div></div>
  </div>
  <div class="row">
    <div class="col-lg-6">
      <div class="card">
        <div class="card-header"><h3 class="card-title">Daily Conversations (Last 7 Days)</h3></div>
        <div class="card-body">
          <div id="an-daily-chart" style="display:flex;align-items:flex-end;gap:8px;height:140px;padding:0 8px"></div>
        </div>
      </div>
    </div>
    <div class="col-lg-6">
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">By Source</h3></div>
        <div class="card-body" id="an-source-breakdown"></div>
      </div>
      <div class="card">
        <div class="card-header"><h3 class="card-title">By Language</h3></div>
        <div class="card-body" id="an-lang-breakdown"></div>
      </div>
    </div>
  </div>
</div>

<!-- AI Visibility Panel -->
<div class="sub-panel" id="an-panel-ai">
  <div class="row row-deck row-cards mb-4" id="an-ai-stats-grid">
    <div class="col-sm-3"><div class="skeleton skeleton-kpi"></div></div>
    <div class="col-sm-3"><div class="skeleton skeleton-kpi"></div></div>
    <div class="col-sm-3"><div class="skeleton skeleton-kpi"></div></div>
    <div class="col-sm-3"><div class="skeleton skeleton-kpi"></div></div>
  </div>
  <div class="card mb-4">
    <div class="card-header"><h3 class="card-title">Share of Model Trend (Last 30 Days)</h3></div>
    <div class="card-body">
      <div id="an-som-trend-chart" style="display:flex;align-items:flex-end;gap:8px;height:120px;padding:0 8px"></div>
      <p id="an-som-trend-empty" class="text-muted text-center" style="display:none;font-size:.85rem">No citation data yet. Data appears after the citation monitor runs.</p>
    </div>
  </div>
  <div class="row">
    <div class="col-lg-6">
      <div class="card mb-3">
        <div class="card-header"><h3 class="card-title">Top Cited Queries</h3></div>
        <div class="card-body" id="an-top-queries" style="max-height:220px;overflow-y:auto">
          <p class="text-muted" style="font-size:.85rem">Loading...</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><h3 class="card-title">Recent Social Mentions</h3></div>
        <div class="card-body" id="an-mentions" style="max-height:340px;overflow-y:auto">
          <p class="text-muted" style="font-size:.85rem">Loading...</p>
        </div>
      </div>
    </div>
    <div class="col-lg-6">
      <div class="card">
        <div class="card-header"><h3 class="card-title">Automation Status</h3></div>
        <div class="card-body" id="an-ai-jobs">
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>Citation Monitor (WS35)</span><span class="badge bg-green-lt">Daily 00:00</span></div>
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>Review Aggregator (WS37)</span><span class="badge bg-green-lt">Daily 01:00</span></div>
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>SEO Tracker (WS40)</span><span class="badge bg-green-lt">Daily 02:00</span></div>
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>Social Monitor (WS39)</span><span class="badge bg-green-lt">Every 6h</span></div>
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>Content Freshness (WS38)</span><span class="badge bg-green-lt">Weekly Wed</span></div>
          <div class="d-flex justify-content-between py-2" style="border-bottom:1px solid #f0f0f0"><span>Competitor Monitor (WS36)</span><span class="badge bg-green-lt">Weekly Mon</span></div>
          <div class="d-flex justify-content-between py-2"><span>Sitemap Ping (WS41)</span><span class="badge bg-green-lt">On Webhook</span></div>
          <p class="text-muted mt-2" style="font-size:.72rem">Requires SERP_API_KEY for WS35/WS40. Jobs run automatically when env vars are set.</p>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Wholesale Leads Panel -->
<div class="sub-panel" id="an-panel-leads">
  <div class="d-flex align-items-center gap-2 mb-3">
    <button class="btn btn-outline-secondary btn-sm" onclick="anLoadLeads()">Refresh</button>
    <span id="an-leads-count" class="text-muted" style="font-size:.85rem"></span>
  </div>
  <div class="table-responsive">
    <table class="table table-vcenter table-hover card-table">
      <thead><tr><th>Email</th><th>Session</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody id="an-leads-tbody"></tbody>
    </table>
  </div>
</div>

<script>
(function(){
  var H = {'Content-Type':'application/json'};

  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function $(id){return document.getElementById(id);}

  // ── Sub-Tabs ──
  var TAB_ORDER=['chat','ai','leads'];
  window.anSwitchTab = function(name){
    document.querySelectorAll('#sec-analytics .sub-tab').forEach(function(t,i){t.classList.toggle('active',TAB_ORDER[i]===name)});
    document.querySelectorAll('#sec-analytics .sub-panel').forEach(function(p){p.classList.remove('active')});
    $('an-panel-'+name).classList.add('active');
    if(name==='chat') anLoadAnalytics();
    if(name==='ai') anLoadAIStats();
    if(name==='leads') anLoadLeads();
  };

  // ── Chat Analytics ──
  window.anLoadAnalytics = function(){
    fetch('/api/admin/analytics',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var sg=$('an-stats-grid');
      var tc=d.total_conversations||0;var tm=d.total_messages||0;
      sg.innerHTML='<div class="col-sm-4"><div class="card card-sm"><div class="card-body"><div class="kpi-label">TOTAL CONVERSATIONS</div><div class="kpi-value">'+tc+'</div></div></div></div>'
        +'<div class="col-sm-4"><div class="card card-sm"><div class="card-body"><div class="kpi-label">TOTAL MESSAGES</div><div class="kpi-value">'+tm+'</div></div></div></div>'
        +'<div class="col-sm-4"><div class="card card-sm"><div class="card-body"><div class="kpi-label">AVG MSGS / CONV</div><div class="kpi-value">'+(tc?(tm/tc).toFixed(1):'0')+'</div></div></div></div>';

      var daily=d.daily_last_7||{};
      var chart=$('an-daily-chart');chart.innerHTML='';
      var vals=Object.values(daily);var maxV=vals.length?Math.max.apply(null,vals):1;
      Object.keys(daily).sort().forEach(function(day){
        var h=Math.max((daily[day]/maxV)*120,4);
        chart.innerHTML+='<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px">'
          +'<div style="font-size:.7rem;font-weight:600;color:#406546">'+daily[day]+'</div>'
          +'<div style="width:100%;max-width:40px;height:'+h+'px;background:#406546;border-radius:4px 4px 0 0"></div>'
          +'<div style="font-size:.65rem;color:#999">'+day.substring(5)+'</div></div>';
      });

      var sb=$('an-source-breakdown');sb.innerHTML='';
      var sources=d.by_source||{};
      Object.keys(sources).forEach(function(s){sb.innerHTML+='<div class="d-flex justify-content-between py-1" style="border-bottom:1px solid #f0f0f0"><span>'+esc(s)+'</span><strong>'+sources[s]+'</strong></div>'});

      var lb=$('an-lang-breakdown');lb.innerHTML='';
      var langs=d.by_language||{};
      Object.keys(langs).forEach(function(l){lb.innerHTML+='<div class="d-flex justify-content-between py-1" style="border-bottom:1px solid #f0f0f0"><span>'+esc(l)+'</span><strong>'+langs[l]+'</strong></div>'});
    })
    .catch(function(){});
  };

  // ── AI Visibility ──
  window.anLoadAIStats = function(){
    fetch('/api/admin/automation-stats',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var sg=$('an-ai-stats-grid');
      var som=d.share_of_model||0;
      var cit=d.citations||d.citations_count||0;
      var soc=d.social_mentions||d.social_mentions_count||0;
      var seo=d.seo_rankings||d.seo_rankings_count||0;
      sg.innerHTML='<div class="col-sm-3"><div class="card card-sm"><div class="card-body"><div class="kpi-label">SHARE OF MODEL</div><div class="kpi-value">'+som+'%</div></div></div></div>'
        +'<div class="col-sm-3"><div class="card card-sm"><div class="card-body"><div class="kpi-label">AI CITATIONS</div><div class="kpi-value">'+cit+'</div></div></div></div>'
        +'<div class="col-sm-3"><div class="card card-sm"><div class="card-body"><div class="kpi-label">SOCIAL MENTIONS</div><div class="kpi-value">'+soc+'</div></div></div></div>'
        +'<div class="col-sm-3"><div class="card card-sm"><div class="card-body"><div class="kpi-label">SEO RANKINGS</div><div class="kpi-value">'+seo+'</div></div></div></div>';

      var trend=d.citation_trend||[];
      var tChart=$('an-som-trend-chart');
      var tEmpty=$('an-som-trend-empty');
      tChart.innerHTML='';
      if(!trend.length){tEmpty.style.display='block'}
      else{
        tEmpty.style.display='none';
        var maxT=1;trend.forEach(function(t){if(t.total>maxT)maxT=t.total});
        trend.forEach(function(t){
          var h=Math.max((t.total/maxT)*100,4);
          var citH=t.total?Math.max((t.cited/maxT)*100,2):0;
          tChart.innerHTML+='<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px">'
            +'<div style="font-size:.65rem;font-weight:600;color:#406546">'+t.pct+'%</div>'
            +'<div style="position:relative;width:100%;max-width:40px;height:'+h+'px">'
            +'<div style="position:absolute;bottom:0;width:100%;height:'+h+'px;background:rgba(64,101,70,.15);border-radius:4px 4px 0 0"></div>'
            +'<div style="position:absolute;bottom:0;width:100%;height:'+citH+'px;background:#406546;border-radius:4px 4px 0 0"></div>'
            +'</div>'
            +'<div style="font-size:.65rem;color:#999">'+t.date.substring(5)+'</div></div>';
        });
      }

      var tq=$('an-top-queries');tq.innerHTML='';
      var topQ=d.top_cited_queries||[];
      if(!topQ.length){tq.innerHTML='<p class="text-muted" style="font-size:.85rem">No cited queries yet.</p>'}
      else{
        topQ.forEach(function(q){
          tq.innerHTML+='<div class="d-flex justify-content-between py-1" style="border-bottom:1px solid #f0f0f0"><span style="flex:1;font-size:.85rem">'+esc(q.query)+'</span><strong style="color:#406546">'+q.count+'x</strong></div>';
        });
      }

      var mc=$('an-mentions');mc.innerHTML='';
      var mentions=d.recent_mentions||[];
      if(!mentions.length){mc.innerHTML='<p class="text-muted" style="font-size:.85rem">No mentions yet. Data will appear after the social monitor runs.</p>';return}
      mentions.forEach(function(m){
        var plat=esc(m.platform||'reddit');
        var sub=m.subreddit?' r/'+esc(m.subreddit):'';
        var ts=m.timestamp?m.timestamp.substring(0,10):'';
        mc.innerHTML+='<div style="padding:8px 0;border-bottom:1px solid #f0f0f0">'
          +'<div style="font-size:.78rem;color:#999">'+plat+sub+' \u00b7 '+ts+'</div>'
          +'<div style="font-size:.88rem;margin-top:4px"><a href="'+esc(m.url||'#')+'" target="_blank" style="color:#406546">'+esc(m.title||'Mention')+'</a></div></div>';
      });
    })
    .catch(function(){
      $('an-ai-stats-grid').innerHTML='<div class="col-12"><div class="card card-sm"><div class="card-body text-center text-muted">Set SERP_API_KEY to enable AI citation tracking</div></div></div>';
    });
  };

  // ── Wholesale Leads ──
  window.anLoadLeads = function(){
    fetch('/api/admin/wholesale/leads',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var leads=d.leads||[];
      var tb=$('an-leads-tbody');tb.innerHTML='';
      $('an-leads-count').textContent=leads.length+' lead'+(leads.length!==1?'s':'');
      leads.forEach(function(l){
        var dt=l.created_at?l.created_at.substring(0,16).replace('T',' '):'\u2014';
        var sid=l.session_id?(l.session_id.substring(0,8)+'...'):'\u2014';
        var lid=esc(l.id);
        tb.innerHTML+='<tr><td>'+esc(l.email)+'</td><td style="font-size:.78rem">'+sid+'</td><td style="font-size:.78rem">'+dt+'</td>'
          +'<td><span class="badge bg-green-lt">'+esc(l.status||'new')+'</span></td>'
          +'<td><button class="btn btn-outline-danger btn-sm" onclick="anDeleteLead(\''+lid+'\')">Delete</button></td></tr>';
      });
    })
    .catch(function(){});
  };

  window.anDeleteLead = function(id){
    if(!confirm('Delete this lead permanently?'))return;
    fetch('/api/admin/wholesale/leads/'+id,{method:'DELETE',headers:H})
    .then(function(){anLoadLeads()});
  };

  // ── Init on section load ──
  var initialized = false;
  window.addEventListener('dashboard:section', function(e){
    if(e.detail === 'analytics' && !initialized){
      initialized = true;
      anLoadAnalytics();
    }
  });
  if(document.getElementById('sec-analytics') && document.getElementById('sec-analytics').style.display === 'block'){
    anLoadAnalytics();
    initialized = true;
  }
})();
</script>
"""
