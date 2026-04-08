"""Guide section — how to use the dashboard + system status."""


def html() -> str:
    return """
<div class="row mb-4">
  <div class="col-12">
    <h2 style="font-size:1.1rem;font-weight:400;color:#333;margin-bottom:4px">NAKAI Management Console Guide</h2>
    <p class="text-muted" style="font-size:.85rem">How to use the dashboard and check system status</p>
  </div>
</div>

<!-- System Status -->
<div class="card mb-4">
  <div class="card-header"><h3 class="card-title"><i class="ti ti-server" style="margin-right:6px;color:#406546"></i> System Status</h3></div>
  <div class="card-body" id="gu-system-status">
    <div class="skeleton skeleton-chart" style="height:100px"></div>
  </div>
</div>

<!-- Section Guide -->
<div class="row row-deck row-cards mb-4">

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('home')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#406546"><i class="ti ti-home" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">Home</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          Dashboard overview with KPIs from all systems. Quick access buttons for common tasks like running the B2B pipeline, syncing Shopify, and re-ingesting knowledge.
        </p>
      </div>
    </div>
  </div>

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('b2b')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#2c3e50"><i class="ti ti-users-group" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">B2B Sales Team</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          Manage wholesale leads for cafes, hotels, and restaurants. Import leads, discover new ones via Google Places, send automated outreach emails, and track conversions.
        </p>
        <div class="mt-2" style="font-size:.75rem;color:#406546">
          <strong>Flow:</strong> Discover &rarr; Import &rarr; Outreach &rarr; Track &rarr; Close
        </div>
      </div>
    </div>
  </div>

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('email')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#8e3b2e"><i class="ti ti-mail" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">Email Marketing</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          Create AI-designed email campaigns, manage newsletter schedules, and handle subscriber lists. Syncs with Shopify customer data automatically.
        </p>
        <div class="mt-2" style="font-size:.75rem;color:#406546">
          <strong>Flow:</strong> New Campaign &rarr; AI Design &rarr; Edit &rarr; Test &rarr; Send
        </div>
      </div>
    </div>
  </div>

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('social')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#FF4500"><i class="ti ti-brand-reddit" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">Content & Social</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          AI auto-posts to Twitter, Reddit, Threads, LINE, and Shopify Blog daily using a 6-slot schedule. Generate content manually, view posting history, and create video scripts.
        </p>
        <div class="mt-2" style="font-size:.75rem;color:#406546">
          <strong>Auto:</strong> 6 posts/day across 5 platforms
        </div>
      </div>
    </div>
  </div>

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('content')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#5856D6"><i class="ti ti-book" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">Content Management</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          Manage the knowledge base that powers the AI chatbot. Add articles, view chat history, manage brand content sources, and review video scripts.
        </p>
        <div class="mt-2" style="font-size:.75rem;color:#406546">
          <strong>Key:</strong> Add knowledge &rarr; Re-ingest &rarr; Chatbot learns
        </div>
      </div>
    </div>
  </div>

  <div class="col-md-6 col-lg-4">
    <div class="card" style="cursor:pointer" onclick="showSection('analytics')">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3 mb-2">
          <div class="seg-icon" style="background:#007AFF"><i class="ti ti-chart-bar" style="font-size:1rem"></i></div>
          <h3 class="card-title mb-0">Analytics</h3>
        </div>
        <p class="text-muted" style="font-size:.82rem;margin:0">
          Chat analytics (conversations, messages, sources). AI visibility tracking (citations, social mentions, SEO). Wholesale lead inquiries from the chatbot.
        </p>
        <div class="mt-2" style="font-size:.75rem;color:#406546">
          <strong>Tracks:</strong> Chat usage, AI citations, brand mentions
        </div>
      </div>
    </div>
  </div>

</div>

<!-- Automation Schedule -->
<div class="card mb-4">
  <div class="card-header"><h3 class="card-title"><i class="ti ti-clock" style="margin-right:6px;color:#406546"></i> Daily Automation Schedule</h3></div>
  <div class="table-responsive">
    <table class="table table-vcenter card-table">
      <thead><tr><th>Time (JST)</th><th>Task</th><th>Details</th></tr></thead>
      <tbody>
        <tr><td><strong>09:00</strong></td><td><span class="badge bg-azure-lt">Twitter</span></td><td>Matcha tip (280 chars, 3 hashtags)</td></tr>
        <tr><td><strong>13:00</strong></td><td><span class="badge bg-orange-lt">Reddit</span></td><td>Educational post (800-1500 words, rotates 5 subreddits)</td></tr>
        <tr><td><strong>15:00</strong></td><td><span class="badge bg-green-lt">Video Script</span></td><td>30-60s script with trending topic research</td></tr>
        <tr><td><strong>17:00</strong></td><td><span class="badge bg-green-lt">Blog</span></td><td>SEO-optimized article published to Shopify</td></tr>
        <tr><td><strong>21:00</strong></td><td><span class="badge bg-purple-lt">Threads</span></td><td>Conversational post (300-500 chars)</td></tr>
        <tr><td><strong>01:00</strong></td><td><span class="badge bg-red-lt">Reddit</span></td><td>Community engagement post</td></tr>
        <tr><td><strong>05:00</strong></td><td><span class="badge bg-yellow-lt">LINE + Twitter</span></td><td>Morning tips + actionable advice</td></tr>
        <tr style="border-top:2px solid #eee"><td><strong>Every 10min</strong></td><td><span class="badge bg-secondary-lt">Newsletter</span></td><td>Checks and sends scheduled newsletters</td></tr>
        <tr><td><strong>Daily 09:00</strong></td><td><span class="badge bg-secondary-lt">AI Monitor</span></td><td>Citation tracking + SEO ranking</td></tr>
        <tr><td><strong>Daily 23:00</strong></td><td><span class="badge bg-secondary-lt">B2B Pipeline</span></td><td>Automated outreach to new leads</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- API Key Setup -->
<div class="card">
  <div class="card-header"><h3 class="card-title"><i class="ti ti-key" style="margin-right:6px;color:#406546"></i> API Configuration Checklist</h3></div>
  <div class="card-body" id="gu-api-checklist">
    <div class="skeleton skeleton-chart" style="height:200px"></div>
  </div>
</div>

<script>
(function(){
  var H = {'Content-Type':'application/json'};

  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function $(id){return document.getElementById(id);}
  function dot(ok){return ok?'<span class="badge bg-green-lt"><i class="ti ti-check"></i> Connected</span>':'<span class="badge bg-secondary-lt"><i class="ti ti-x"></i> Not Set</span>';}

  function loadStatus(){
    // Check system status by calling various endpoints
    var checks = [
      {name:'Core API',endpoint:'/api/health',key:'status'},
      {name:'Supabase (Database)',endpoint:'/api/admin/analytics',key:'total_conversations'},
      {name:'B2B System',endpoint:'/api/b2b/stats',key:'total_leads'},
      {name:'Email System',endpoint:'/api/email/brand-assets',key:null},
    ];

    var results={};
    var done=0;
    var total=checks.length;

    checks.forEach(function(c){
      fetch(c.endpoint,{headers:H})
      .then(function(r){results[c.name]=r.ok;done++;if(done===total)renderStatus(results)})
      .catch(function(){results[c.name]=false;done++;if(done===total)renderStatus(results)});
    });
  }

  function renderStatus(results){
    var html='<div class="row">';
    Object.keys(results).forEach(function(name){
      var ok=results[name];
      html+='<div class="col-sm-6 col-lg-3 mb-2"><div class="d-flex align-items-center gap-2">'
        +'<div style="width:10px;height:10px;border-radius:50%;background:'+(ok?'#34C759':'#ccc')+'"></div>'
        +'<span style="font-size:.85rem">'+(ok?'<strong>'+name+'</strong>':'<span class="text-muted">'+name+'</span>')+'</span>'
        +'</div></div>';
    });
    html+='</div>';
    $('gu-system-status').innerHTML=html;
  }

  function loadChecklist(){
    // We can check API config by probing endpoints
    var apis = [
      {name:'Shopify Admin',desc:'Product data + customer sync',check:'/api/marketing/products'},
      {name:'Resend (Email)',desc:'Campaign + newsletter sending',check:'/api/email/brand-assets'},
      {name:'Anthropic (Claude)',desc:'AI content generation + email design',check:null},
      {name:'Reddit API',desc:'Reddit auto-posting (r/Matcha, r/tea, etc.)',check:null},
      {name:'Twitter / X API',desc:'Daily matcha tips posting',check:null},
      {name:'Threads API',desc:'Conversational matcha posts',check:null},
      {name:'LINE Channel',desc:'Morning tips + matcha advice',check:null},
      {name:'Google Places',desc:'B2B lead discovery',check:null},
      {name:'Hunter.io',desc:'Email verification for B2B leads',check:null},
      {name:'SERP API',desc:'AI citation + SEO monitoring',check:null},
    ];

    var html='<div class="table-responsive"><table class="table table-vcenter">';
    html+='<thead><tr><th>Service</th><th>Purpose</th><th>Status</th></tr></thead><tbody>';
    apis.forEach(function(a){
      // For APIs we can't probe, show "Check .env" note
      var status=a.check?'<span class="badge bg-azure-lt">Checking...</span>':'<span class="badge bg-secondary-lt">Set in .env</span>';
      html+='<tr id="api-row-'+a.name.replace(/[^a-zA-Z]/g,'')+'"><td><strong>'+esc(a.name)+'</strong></td><td class="text-muted" style="font-size:.82rem">'+esc(a.desc)+'</td><td>'+status+'</td></tr>';
    });
    html+='</tbody></table></div>';
    html+='<p class="text-muted mt-2" style="font-size:.78rem"><i class="ti ti-info-circle"></i> API keys are configured via environment variables on Render. Contact the admin to update settings.</p>';
    $('gu-api-checklist').innerHTML=html;

    // Probe checkable APIs
    apis.filter(function(a){return a.check}).forEach(function(a){
      var rowId='api-row-'+a.name.replace(/[^a-zA-Z]/g,'');
      fetch(a.check,{headers:H})
      .then(function(r){
        var row=document.getElementById(rowId);
        if(row){
          var td=row.querySelectorAll('td')[2];
          td.innerHTML=r.ok?'<span class="badge bg-green-lt"><i class="ti ti-check"></i> Connected</span>':'<span class="badge bg-red-lt"><i class="ti ti-x"></i> Error</span>';
        }
      })
      .catch(function(){
        var row=document.getElementById(rowId);
        if(row){var td=row.querySelectorAll('td')[2];td.innerHTML='<span class="badge bg-red-lt">Offline</span>';}
      });
    });
  }

  // ── Init ──
  var initialized=false;
  function init(){
    if(initialized)return;
    initialized=true;
    loadStatus();
    loadChecklist();
  }

  window.addEventListener('dashboard:section',function(e){
    if(e.detail==='guide')init();
  });
  if(document.getElementById('sec-guide')&&document.getElementById('sec-guide').style.display==='block'){
    init();
  }
})();
</script>
"""
