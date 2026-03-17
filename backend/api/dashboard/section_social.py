"""Content & Social section — content generation, posting, blog, video scripts."""


def html() -> str:
    return """
<!-- Sub-Tabs -->
<div class="sub-tabs">
  <div class="sub-tab active" onclick="scSwitchTab('generate')">Generate</div>
  <div class="sub-tab" onclick="scSwitchTab('posts')">Post History</div>
  <div class="sub-tab" onclick="scSwitchTab('video')">Video Scripts</div>
</div>

<!-- Generate Tab -->
<div class="sub-panel active" id="sc-panel-generate">
  <div class="card mb-4">
    <div class="card-header"><h3 class="card-title"><i class="ti ti-bulb" style="margin-right:6px;color:#406546"></i> Today's Topic</h3></div>
    <div class="card-body" id="sc-today-topic">
      <div class="skeleton skeleton-chart" style="height:80px"></div>
    </div>
  </div>

  <div class="row mb-4">
    <div class="col-12">
      <div class="card">
        <div class="card-header"><h3 class="card-title">Generate & Post Content</h3></div>
        <div class="card-body">
          <p class="text-muted mb-3" style="font-size:.85rem">
            Generate AI-powered matcha content and post to social media platforms.
            The system uses a 365-day topic rotation with 230+ pre-written topics.
          </p>
          <div class="d-flex gap-2 flex-wrap mb-3">
            <button class="btn btn-primary btn-sm" onclick="scForcePost()" id="sc-post-all-btn">
              <i class="ti ti-send"></i> Post to All Platforms
            </button>
            <button class="btn btn-outline-primary btn-sm" onclick="scPreviewContent()">
              <i class="ti ti-eye"></i> Preview Today's Content
            </button>
          </div>
          <div class="row row-deck row-cards" id="sc-platform-status">
            <div class="col-sm-6 col-lg-3">
              <div class="card card-sm"><div class="card-body d-flex align-items-center gap-3">
                <div class="seg-icon" style="background:#1DA1F2;width:36px;height:36px;font-size:.9rem">X</div>
                <div><div style="font-weight:500;font-size:.85rem">Twitter / X</div><div class="text-muted" style="font-size:.75rem">Slot 1 &amp; 6 (09:00 &amp; 05:00 JST)</div></div>
              </div></div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card card-sm"><div class="card-body d-flex align-items-center gap-3">
                <div class="seg-icon" style="background:#E1306C;width:36px;height:36px;font-size:.9rem"><i class="ti ti-brand-threads" style="font-size:1rem"></i></div>
                <div><div style="font-weight:500;font-size:.85rem">Threads</div><div class="text-muted" style="font-size:.75rem">Slot 4 (21:00 JST)</div></div>
              </div></div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card card-sm"><div class="card-body d-flex align-items-center gap-3">
                <div class="seg-icon" style="background:#06C755;width:36px;height:36px;font-size:.9rem"><i class="ti ti-message-circle" style="font-size:1rem"></i></div>
                <div><div style="font-weight:500;font-size:.85rem">LINE</div><div class="text-muted" style="font-size:.75rem">Slot 6 (05:00 JST)</div></div>
              </div></div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card card-sm"><div class="card-body d-flex align-items-center gap-3">
                <div class="seg-icon" style="background:#FF4500;width:36px;height:36px;font-size:.9rem"><i class="ti ti-brand-reddit" style="font-size:1rem"></i></div>
                <div><div style="font-weight:500;font-size:.85rem">Reddit</div><div class="text-muted" style="font-size:.75rem">Slot 2 &amp; 5 (13:00 &amp; 01:00 JST)</div></div>
              </div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Preview area -->
  <div id="sc-preview-area" style="display:none">
    <div class="card mb-4">
      <div class="card-header">
        <h3 class="card-title">Generated Content Preview</h3>
        <button class="btn btn-outline-secondary btn-sm ms-auto" onclick="document.getElementById('sc-preview-area').style.display='none'">Close</button>
      </div>
      <div class="card-body" id="sc-preview-content"></div>
    </div>
  </div>

  <!-- Schedule Reference -->
  <div class="card">
    <div class="card-header"><h3 class="card-title"><i class="ti ti-clock" style="margin-right:6px;color:#406546"></i> Daily Auto-Post Schedule (6 Slots)</h3></div>
    <div class="table-responsive">
      <table class="table table-vcenter card-table">
        <thead><tr><th>Slot</th><th>Time (JST)</th><th>Platform</th><th>Type</th></tr></thead>
        <tbody>
          <tr><td><span class="badge bg-azure-lt">1</span></td><td>09:00</td><td><strong>Twitter / X</strong></td><td>Matcha tips & knowledge</td></tr>
          <tr><td><span class="badge bg-orange-lt">2</span></td><td>13:00</td><td><strong>Reddit</strong></td><td>Educational post</td></tr>
          <tr><td><span class="badge bg-green-lt">3</span></td><td>17:00</td><td><strong>Shopify Blog</strong></td><td>SEO-optimized article</td></tr>
          <tr><td><span class="badge bg-purple-lt">4</span></td><td>21:00</td><td><strong>Threads</strong></td><td>Conversational post</td></tr>
          <tr><td><span class="badge bg-red-lt">5</span></td><td>01:00</td><td><strong>Reddit</strong></td><td>Community engagement</td></tr>
          <tr><td><span class="badge bg-yellow-lt">6</span></td><td>05:00</td><td><strong>LINE + Twitter</strong></td><td>Morning tips</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- Post History Tab -->
<div class="sub-panel" id="sc-panel-posts">
  <div class="d-flex align-items-center gap-2 mb-3">
    <button class="btn btn-outline-secondary btn-sm" onclick="scLoadHistory()"><i class="ti ti-refresh"></i> Refresh</button>
    <span id="sc-history-count" class="text-muted" style="font-size:.85rem"></span>
  </div>
  <div id="sc-history-list">
    <div class="text-muted text-center py-4">Loading...</div>
  </div>
</div>

<!-- Video Scripts Tab -->
<div class="sub-panel" id="sc-panel-video">
  <div class="card mb-4">
    <div class="card-header"><h3 class="card-title">Generate Video Script</h3></div>
    <div class="card-body">
      <p class="text-muted mb-3" style="font-size:.85rem">
        AI generates a 30-60 second video script with trending topic research.
        Perfect for TikTok, Instagram Reels, or YouTube Shorts.
      </p>
      <div class="d-flex gap-2 align-items-end">
        <div style="flex:1">
          <label class="form-label">Topic (optional — leave blank for auto-topic)</label>
          <input type="text" class="form-control" id="sc-video-topic" placeholder="e.g., How to make the perfect matcha latte">
        </div>
        <button class="btn btn-primary btn-sm" onclick="scGenerateScript()" id="sc-gen-script-btn">
          <i class="ti ti-wand"></i> Generate
        </button>
      </div>
      <div id="sc-script-output" style="display:none;margin-top:16px"></div>
    </div>
  </div>

  <div class="d-flex align-items-center gap-2 mb-3">
    <h3 style="font-size:.95rem;font-weight:500;margin:0">Saved Scripts</h3>
    <button class="btn btn-outline-secondary btn-sm" onclick="scLoadScripts()"><i class="ti ti-refresh"></i></button>
    <span id="sc-scripts-count" class="text-muted" style="font-size:.85rem"></span>
  </div>
  <div id="sc-scripts-list">
    <div class="text-muted text-center py-4">Loading...</div>
  </div>
</div>

<script>
(function(){
  var PWD = sessionStorage.getItem('nakai-admin-pwd') || '';
  var H = {'Content-Type':'application/json','X-Admin-Password':PWD};

  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function $(id){return document.getElementById(id);}
  function timeAgo(ts){if(!ts)return'-';var df=(Date.now()-new Date(ts).getTime())/1000;if(df<60)return'just now';if(df<3600)return Math.floor(df/60)+'m ago';if(df<86400)return Math.floor(df/3600)+'h ago';return Math.floor(df/86400)+'d ago';}

  // ── Sub-Tabs ──
  var TAB_ORDER=['generate','posts','video'];
  window.scSwitchTab = function(name){
    document.querySelectorAll('#sec-social .sub-tab').forEach(function(t,i){t.classList.toggle('active',TAB_ORDER[i]===name)});
    document.querySelectorAll('#sec-social .sub-panel').forEach(function(p){p.classList.remove('active')});
    $('sc-panel-'+name).classList.add('active');
    if(name==='posts') scLoadHistory();
    if(name==='video') scLoadScripts();
  };

  // ── Today's Topic ──
  function scLoadToday(){
    $('sc-today-topic').innerHTML='<div class="d-flex align-items-center gap-2"><div class="spinner-border spinner-border-sm text-muted"></div><span class="text-muted">Loading today\'s topic...</span></div>';
    fetch('/api/tips/today',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var c=d.content||{};
      var topic=c.topic||'Today\'s matcha topic';
      var html='<div style="font-size:1rem;font-weight:500;color:#406546;margin-bottom:12px">'+esc(topic)+'</div>';
      if(c.twitter){
        html+='<div class="mb-2"><span class="badge bg-azure-lt">Twitter</span> <span style="font-size:.85rem">'+esc(c.twitter).substring(0,120)+'...</span></div>';
      }
      if(c.reddit){
        var reddit=c.reddit;
        var title=reddit.match&&reddit.match(/TITLE:\s*(.+?)(?:\n|BODY:)/)?RegExp.$1:reddit.substring(0,80);
        html+='<div class="mb-2"><span class="badge bg-orange-lt">Reddit</span> <span style="font-size:.85rem">'+esc(title)+'</span></div>';
      }
      if(c.threads){
        html+='<div class="mb-2"><span class="badge bg-purple-lt">Threads</span> <span style="font-size:.85rem">'+esc(c.threads).substring(0,120)+'...</span></div>';
      }
      $('sc-today-topic').innerHTML=html||'<p class="text-muted">No content generated yet</p>';
    })
    .catch(function(){
      $('sc-today-topic').innerHTML='<p class="text-muted">Could not load today\'s topic. Content is auto-generated daily.</p>';
    });
  }

  // ── Preview ──
  window.scPreviewContent = function(){
    $('sc-preview-area').style.display='block';
    $('sc-preview-content').innerHTML='<div class="d-flex align-items-center gap-2"><div class="spinner-border spinner-border-sm text-muted"></div><span class="text-muted">Generating preview (may take 10-20s)...</span></div>';
    fetch('/api/tips/today',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var c=d.content||{};
      var html='';
      var platforms={twitter:'Twitter / X',reddit:'Reddit',threads:'Threads',line:'LINE',blog:'Blog'};
      Object.keys(platforms).forEach(function(p){
        if(c[p]){
          html+='<div class="card mb-2"><div class="card-body">';
          html+='<h4 style="font-size:.85rem;font-weight:600;color:#406546;margin-bottom:8px">'+platforms[p]+'</h4>';
          html+='<pre style="white-space:pre-wrap;font-size:.82rem;color:#333;margin:0;font-family:inherit">'+esc(c[p])+'</pre>';
          html+='</div></div>';
        }
      });
      $('sc-preview-content').innerHTML=html||'<p class="text-muted">No content generated</p>';
    })
    .catch(function(){
      $('sc-preview-content').innerHTML='<p class="text-muted">Failed to generate preview</p>';
    });
  };

  // ── Force Post ──
  window.scForcePost = function(){
    if(!confirm('Post today\\'s content to ALL configured platforms now?'))return;
    var btn=$('sc-post-all-btn');
    btn.classList.add('btn-loading');btn.disabled=true;
    fetch('/api/tips/force-post',{method:'POST',headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      btn.classList.remove('btn-loading');btn.disabled=false;
      if(d.posted){
        var results=d.results||{};
        var summary=Object.keys(results).map(function(p){
          var r=results[p];
          return p+': '+(r.success?'OK':'Failed'+(r.error?' - '+r.error:''));
        }).join('\\n');
        alert('Posted!\\n\\n'+summary);
        scLoadHistory();
      }else{
        alert('Posting failed');
      }
    })
    .catch(function(){
      btn.classList.remove('btn-loading');btn.disabled=false;
      alert('Failed to post');
    });
  };

  // ── Post History ──
  window.scLoadHistory = function(){
    fetch('/api/tips/history',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var history=d.history||[];
      $('sc-history-count').textContent=history.length+' posts';
      var el=$('sc-history-list');
      if(!history.length){
        el.innerHTML='<div class="card"><div class="card-body text-center text-muted py-4">No posting history yet. Content is posted automatically via the 6-slot daily schedule.</div></div>';
        return;
      }
      var html='<div class="table-responsive"><table class="table table-vcenter table-hover card-table">';
      html+='<thead><tr><th>Date</th><th>Topic</th><th>Twitter</th><th>Reddit</th><th>Threads</th><th>LINE</th><th>Blog</th></tr></thead><tbody>';
      history.forEach(function(h){
        var date=h.posted_at?h.posted_at.substring(0,10):'—';
        function badge(st){
          if(!st||st==='skipped')return'<span class="badge bg-secondary-lt">—</span>';
          if(st==='success'||st==='ok'||st===true)return'<span class="badge bg-green-lt">OK</span>';
          return'<span class="badge bg-red-lt">Fail</span>';
        }
        html+='<tr>';
        html+='<td style="font-size:.78rem">'+date+'</td>';
        html+='<td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(h.topic||'—')+'</td>';
        html+='<td>'+badge(h.twitter_status||h.twitter)+'</td>';
        html+='<td>'+badge(h.reddit_status||h.reddit)+'</td>';
        html+='<td>'+badge(h.threads_status||h.threads)+'</td>';
        html+='<td>'+badge(h.line_status||h.line)+'</td>';
        html+='<td>'+badge(h.blog_status||h.blog)+'</td>';
        html+='</tr>';
      });
      html+='</tbody></table></div>';
      el.innerHTML=html;
    })
    .catch(function(){
      $('sc-history-list').innerHTML='<div class="card"><div class="card-body text-center text-muted">Could not load posting history (Supabase may not be configured)</div></div>';
    });
  };

  // ── Video Scripts ──
  window.scGenerateScript = function(){
    var topic=$('sc-video-topic').value.trim();
    var btn=$('sc-gen-script-btn');
    btn.classList.add('btn-loading');btn.disabled=true;
    $('sc-script-output').style.display='block';
    $('sc-script-output').innerHTML='<div class="d-flex align-items-center gap-2"><div class="spinner-border spinner-border-sm text-muted"></div><span class="text-muted">Researching trends and generating script (30-60s)...</span></div>';

    var body={};
    if(topic)body.topic=topic;
    fetch('/api/admin/video-scripts/generate',{method:'POST',headers:H,body:JSON.stringify(body)})
    .then(function(r){return r.json()})
    .then(function(d){
      btn.classList.remove('btn-loading');btn.disabled=false;
      if(d.script||d.topic){
        var s=d.script||d;
        $('sc-script-output').innerHTML=renderScript(s);
        scLoadScripts();
      }else{
        $('sc-script-output').innerHTML='<div class="alert alert-warning">Script generation not available. Check that ANTHROPIC_API_KEY is configured.</div>';
      }
    })
    .catch(function(){
      btn.classList.remove('btn-loading');btn.disabled=false;
      $('sc-script-output').innerHTML='<div class="alert alert-warning">Failed to generate script. The video script API endpoint may not be available.</div>';
    });
  };

  function renderScript(s){
    var tags=(s.hashtags||[]).join(' ');
    return '<div class="card"><div class="card-body">'
      +'<div class="d-flex justify-content-between align-items-center mb-3"><strong style="color:#406546;font-size:1rem">'+esc(s.topic||'Generated Script')+'</strong>'
      +'<span class="text-muted" style="font-size:.78rem">'+(s.estimated_duration||'30-60s')+'</span></div>'
      +'<div class="mb-2" style="font-size:.88rem"><span class="badge bg-green-lt me-2">Hook</span>'+esc(s.hook||'')+'</div>'
      +'<div class="mb-2" style="font-size:.88rem"><span class="badge bg-azure-lt me-2">Content</span>'+esc(s.content||'')+'</div>'
      +'<div class="mb-2" style="font-size:.88rem"><span class="badge bg-orange-lt me-2">CTA</span>'+esc(s.cta||'')+'</div>'
      +(s.visual_cues&&s.visual_cues.length?'<div class="mb-2" style="font-size:.82rem;color:#888"><strong>Visual cues:</strong> '+esc(s.visual_cues.join(' | '))+'</div>':'')
      +'<div style="font-size:.78rem;color:#888">'+esc(tags)+'</div>'
      +'</div></div>';
  }

  window.scLoadScripts = function(){
    fetch('/api/admin/video-scripts',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var scripts=d.scripts||[];
      $('sc-scripts-count').textContent=scripts.length+' scripts';
      var el=$('sc-scripts-list');
      if(!scripts.length){
        el.innerHTML='<div class="card"><div class="card-body text-center text-muted py-4">No video scripts yet. Click "Generate" above or scripts are auto-generated daily at 15:00 JST.</div></div>';
        return;
      }
      el.innerHTML=scripts.map(function(s){
        var dt=s.date||'';
        return '<div class="mb-2">'+renderScript(s)+'</div>';
      }).join('');
    })
    .catch(function(){
      $('sc-scripts-list').innerHTML='<div class="card"><div class="card-body text-center text-muted">Could not load scripts</div></div>';
    });
  };

  // ── Init ──
  var initialized=false;
  window.addEventListener('dashboard:section',function(e){
    if(e.detail==='social'&&!initialized){initialized=true;scLoadToday();}
  });
  if(document.getElementById('sec-social')&&document.getElementById('sec-social').style.display==='block'){
    scLoadToday();initialized=true;
  }
})();
</script>
"""
