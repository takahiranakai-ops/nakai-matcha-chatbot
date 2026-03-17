"""Content management section — Knowledge Base + Chat History from admin_page.py."""


def html() -> str:
    return """
<!-- Content Sub-Tabs -->
<div class="sub-tabs">
  <div class="sub-tab active" onclick="ctSwitchTab('knowledge')">Knowledge Base</div>
  <div class="sub-tab" onclick="ctSwitchTab('history')">Chat History</div>
  <div class="sub-tab" onclick="ctSwitchTab('sources')">Content Sources</div>
  <div class="sub-tab" onclick="ctSwitchTab('scripts')">Video Scripts</div>
</div>

<!-- Knowledge Base Panel -->
<div class="sub-panel active" id="ct-panel-knowledge">
  <div class="d-flex align-items-center gap-2 mb-3 flex-wrap">
    <button class="btn btn-primary btn-sm" onclick="ctOpenCreateArticle()"><i class="ti ti-plus"></i> New Article</button>
    <button class="btn btn-outline-secondary btn-sm" onclick="ctReingest()"><i class="ti ti-database"></i> Re-ingest</button>
    <select class="form-select form-select-sm" id="ct-filter-lang" onchange="ctLoadArticles()" style="width:auto">
      <option value="">All Languages</option><option value="en">English</option><option value="ja">Japanese</option>
    </select>
    <select class="form-select form-select-sm" id="ct-filter-cat" onchange="ctLoadArticles()" style="width:auto">
      <option value="">All Categories</option><option value="general">General</option><option value="product">Product</option><option value="faq">FAQ</option><option value="brewing">Brewing</option><option value="science">Science</option><option value="shipping">Shipping</option><option value="recipe">Recipe</option>
    </select>
  </div>
  <div class="table-responsive">
    <table class="table table-vcenter table-hover card-table">
      <thead><tr><th>Title</th><th>Lang</th><th>Category</th><th>Status</th><th>Updated</th><th>Actions</th></tr></thead>
      <tbody id="ct-articles-tbody"></tbody>
    </table>
  </div>
</div>

<!-- Chat History Panel -->
<div class="sub-panel" id="ct-panel-history">
  <div class="d-flex align-items-center gap-2 mb-3 flex-wrap">
    <select class="form-select form-select-sm" id="ct-hist-source" onchange="ctLoadConversations()" style="width:auto">
      <option value="">All Sources</option><option value="pwa">PWA</option><option value="widget">Widget</option>
    </select>
    <select class="form-select form-select-sm" id="ct-hist-lang" onchange="ctLoadConversations()" style="width:auto">
      <option value="">All Languages</option><option value="en">English</option><option value="ja">Japanese</option>
    </select>
    <button class="btn btn-outline-secondary btn-sm" onclick="ctLoadConversations()">Refresh</button>
  </div>
  <div class="row">
    <div class="col-lg-5">
      <div class="table-responsive">
        <table class="table table-vcenter table-hover card-table">
          <thead><tr><th>Session</th><th>Src</th><th>Msgs</th><th>Last Activity</th></tr></thead>
          <tbody id="ct-convs-tbody"></tbody>
        </table>
      </div>
    </div>
    <div class="col-lg-7">
      <div class="card" id="ct-msg-viewer" style="min-height:300px;max-height:500px;overflow-y:auto">
        <div class="card-body text-center text-muted py-5">Select a conversation</div>
      </div>
    </div>
  </div>
</div>

<!-- Content Sources Panel -->
<div class="sub-panel" id="ct-panel-sources">
  <div class="d-flex align-items-center gap-2 mb-3">
    <button class="btn btn-primary btn-sm" onclick="ctOpenCreateSource()"><i class="ti ti-plus"></i> New Source</button>
    <button class="btn btn-outline-secondary btn-sm" onclick="ctLoadContentSources()">Refresh</button>
  </div>
  <div class="table-responsive">
    <table class="table table-vcenter table-hover card-table">
      <thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Priority</th><th>Actions</th></tr></thead>
      <tbody id="ct-sources-tbody"></tbody>
    </table>
  </div>
</div>

<!-- Video Scripts Panel -->
<div class="sub-panel" id="ct-panel-scripts">
  <div class="d-flex align-items-center gap-2 mb-3">
    <button class="btn btn-outline-secondary btn-sm" onclick="ctLoadVideoScripts()">Refresh</button>
    <span id="ct-scripts-count" class="text-muted" style="font-size:.85rem"></span>
  </div>
  <div id="ct-scripts-list"></div>
</div>

<!-- Article Modal -->
<div class="modal modal-blur fade" id="ct-article-modal" tabindex="-1">
<div class="modal-dialog modal-lg modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title" id="ct-modal-title">New Article</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <input type="hidden" id="ct-edit-id">
    <div class="mb-3"><label class="form-label">Title</label><input type="text" class="form-control" id="ct-art-title"></div>
    <div class="row mb-3">
      <div class="col-6"><label class="form-label">Language</label><select class="form-select" id="ct-art-lang"><option value="en">English</option><option value="ja">Japanese</option></select></div>
      <div class="col-6"><label class="form-label">Category</label><select class="form-select" id="ct-art-cat"><option value="general">General</option><option value="product">Product</option><option value="faq">FAQ</option><option value="brewing">Brewing</option><option value="science">Science</option><option value="shipping">Shipping</option><option value="recipe">Recipe</option></select></div>
    </div>
    <div class="mb-3" id="ct-upload-group">
      <label class="form-label">Upload File (.txt or .pdf)</label>
      <div id="ct-upload-zone" style="border:2px dashed #ddd;border-radius:8px;padding:20px;text-align:center;cursor:pointer">
        <input type="file" id="ct-art-file" accept=".txt,.pdf" style="display:none">
        <div id="ct-upload-label" class="text-muted" style="font-size:.85rem">Click to select a file or drag &amp; drop<br><span style="font-size:.75rem">.txt or .pdf (max 5 MB)</span></div>
        <div id="ct-upload-info" style="display:none;color:#406546;font-size:.85rem"></div>
      </div>
    </div>
    <div class="mb-3"><label class="form-label">Content <span id="ct-content-source" class="text-muted" style="font-size:.75rem"></span></label><textarea class="form-control" id="ct-art-content" rows="8"></textarea></div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" onclick="ctSaveArticle()">Save</button>
  </div>
</div></div>
</div>

<!-- Content Source Modal -->
<div class="modal modal-blur fade" id="ct-source-modal" tabindex="-1">
<div class="modal-dialog modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title" id="ct-source-modal-title">New Content Source</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <input type="hidden" id="ct-source-edit-id">
    <div class="mb-3"><label class="form-label">Type</label>
      <select class="form-select" id="ct-src-type">
        <option value="key_message">Key Message</option><option value="product_narrative">Product Narrative</option><option value="seasonal_theme">Seasonal Theme</option><option value="brand_voice">Brand Voice</option><option value="custom">Custom</option>
      </select>
    </div>
    <div class="mb-3"><label class="form-label">Title</label><input type="text" class="form-control" id="ct-src-title"></div>
    <div class="mb-3"><label class="form-label">Content</label><textarea class="form-control" id="ct-src-content" rows="5"></textarea></div>
    <div class="mb-3"><label class="form-label">Priority (0=low, higher=more important)</label><input type="number" class="form-control" id="ct-src-priority" value="0" min="0" max="100" style="max-width:120px"></div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" onclick="ctSaveSource()">Save</button>
  </div>
</div></div>
</div>

<script>
(function(){
  var PWD = sessionStorage.getItem('nakai-admin-pwd') || '';
  var H = {'Content-Type':'application/json','X-Admin-Password':PWD};
  var selectedFile = null;

  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function $(id){return document.getElementById(id);}

  function ctModal(id, show){
    var el=$(id);if(!el)return;
    if(typeof bootstrap!=='undefined'){var m=bootstrap.Modal.getOrCreateInstance(el);show?m.show():m.hide();}
    else{el.style.display=show?'flex':'none';el.classList.toggle('show',show);}
  }

  // ── Sub-Tabs ──
  var TAB_ORDER=['knowledge','history','sources','scripts'];
  window.ctSwitchTab = function(name){
    document.querySelectorAll('#sec-content .sub-tab').forEach(function(t,i){t.classList.toggle('active',TAB_ORDER[i]===name)});
    document.querySelectorAll('#sec-content .sub-panel').forEach(function(p){p.classList.remove('active')});
    $('ct-panel-'+name).classList.add('active');
    if(name==='history') ctLoadConversations();
    if(name==='sources') ctLoadContentSources();
    if(name==='scripts') ctLoadVideoScripts();
  };

  // ── Knowledge Base ──
  window.ctLoadArticles = function(){
    var lang=$('ct-filter-lang').value;
    var cat=$('ct-filter-cat').value;
    var qs='?';if(lang)qs+='language='+lang+'&';if(cat)qs+='category='+cat;
    fetch('/api/admin/articles'+qs,{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var tb=$('ct-articles-tbody');tb.innerHTML='';
      (d.articles||[]).forEach(function(a){
        var st=a.is_active?'<span class="badge bg-green-lt">Active</span>':'<span class="badge bg-secondary-lt">Inactive</span>';
        var upd=a.updated_at?a.updated_at.substring(0,10):'—';
        var aid=esc(a.id);
        tb.innerHTML+='<tr><td><strong>'+esc(a.title)+'</strong></td><td>'+esc(a.language)+'</td><td>'+esc(a.category)+'</td><td>'+st+'</td><td>'+upd+'</td>'
          +'<td><button class="btn btn-outline-secondary btn-sm" onclick="ctEditArticle(\''+aid+'\')">Edit</button> '
          +'<button class="btn btn-outline-secondary btn-sm" onclick="ctToggleArticle(\''+aid+'\','+(!a.is_active)+')">'+(a.is_active?'Off':'On')+'</button> '
          +'<button class="btn btn-outline-danger btn-sm" onclick="ctDeleteArticle(\''+aid+'\')">Del</button></td></tr>';
      });
    });
  };

  window.ctOpenCreateArticle = function(){
    $('ct-modal-title').textContent='New Article';
    $('ct-edit-id').value='';
    $('ct-art-title').value='';
    $('ct-art-content').value='';
    $('ct-art-lang').value='en';
    $('ct-art-cat').value='general';
    selectedFile=null;
    var fi=$('ct-art-file');if(fi)fi.value='';
    $('ct-upload-label').style.display='block';
    $('ct-upload-info').style.display='none';
    $('ct-content-source').textContent='';
    $('ct-upload-group').style.display='block';
    ctModal('ct-article-modal',true);
  };

  window.ctEditArticle = function(id){
    fetch('/api/admin/articles/'+id,{headers:H})
    .then(function(r){return r.json()})
    .then(function(a){
      $('ct-modal-title').textContent='Edit Article';
      $('ct-edit-id').value=id;
      $('ct-art-title').value=a.title||'';
      $('ct-art-content').value=a.content||'';
      $('ct-art-lang').value=a.language||'en';
      $('ct-art-cat').value=a.category||'general';
      $('ct-upload-group').style.display='none';
      $('ct-content-source').textContent='';
      selectedFile=null;
      ctModal('ct-article-modal',true);
    });
  };

  window.ctSaveArticle = function(){
    var id=$('ct-edit-id').value;
    if(!id && selectedFile){
      var fd=new FormData();
      fd.append('file',selectedFile);
      fd.append('title',$('ct-art-title').value);
      fd.append('language',$('ct-art-lang').value);
      fd.append('category',$('ct-art-cat').value);
      fetch('/api/admin/articles/upload',{method:'POST',headers:{'X-Admin-Password':PWD},body:fd})
      .then(function(r){if(!r.ok)return r.json().then(function(d){throw new Error(d.detail||'Upload failed')});return r.json()})
      .then(function(){ctModal('ct-article-modal',false);ctLoadArticles()})
      .catch(function(e){alert('Upload failed: '+e.message)});
    } else {
      var data={title:$('ct-art-title').value,content:$('ct-art-content').value,language:$('ct-art-lang').value,category:$('ct-art-cat').value};
      var url=id?'/api/admin/articles/'+id:'/api/admin/articles';
      var method=id?'PATCH':'POST';
      fetch(url,{method:method,headers:H,body:JSON.stringify(data)})
      .then(function(r){if(!r.ok)throw new Error();return r.json()})
      .then(function(){ctModal('ct-article-modal',false);ctLoadArticles()})
      .catch(function(){alert('Failed to save article')});
    }
  };

  window.ctToggleArticle = function(id,newState){
    fetch('/api/admin/articles/'+id,{method:'PATCH',headers:H,body:JSON.stringify({is_active:newState})})
    .then(function(){ctLoadArticles()});
  };

  window.ctDeleteArticle = function(id){
    if(!confirm('Delete this article permanently?'))return;
    fetch('/api/admin/articles/'+id,{method:'DELETE',headers:H})
    .then(function(){ctLoadArticles()});
  };

  window.ctReingest = function(){
    if(!confirm('Re-ingest all knowledge? This takes 1-2 minutes.'))return;
    fetch('/api/admin/reingest',{method:'POST',headers:H})
    .then(function(r){return r.json()})
    .then(function(d){alert('Re-ingestion '+d.status)})
    .catch(function(){alert('Failed to trigger re-ingestion')});
  };

  // ── File Upload ──
  var uploadZone=$('ct-upload-zone');
  var fileInput=$('ct-art-file');
  if(uploadZone){
    uploadZone.addEventListener('click',function(){if(!selectedFile && fileInput)fileInput.click()});
    uploadZone.addEventListener('dragover',function(e){e.preventDefault();uploadZone.style.borderColor='#406546'});
    uploadZone.addEventListener('dragleave',function(){uploadZone.style.borderColor='#ddd'});
    uploadZone.addEventListener('drop',function(e){e.preventDefault();uploadZone.style.borderColor='#ddd';if(e.dataTransfer.files.length)handleFileSelect(e.dataTransfer.files[0])});
  }
  if(fileInput) fileInput.addEventListener('change',function(){if(fileInput.files.length)handleFileSelect(fileInput.files[0])});

  function handleFileSelect(f){
    var ext=f.name.split('.').pop().toLowerCase();
    if(ext!=='txt'&&ext!=='pdf'){alert('Only .txt and .pdf files are supported');return}
    if(f.size>5*1024*1024){alert('File too large. Maximum size is 5 MB.');return}
    selectedFile=f;
    $('ct-upload-label').style.display='none';
    var info=$('ct-upload-info');
    info.style.display='block';
    info.innerHTML=esc(f.name)+' ('+(f.size/1024).toFixed(1)+' KB) <button type="button" class="btn btn-outline-secondary btn-sm ms-2" onclick="ctClearFile(event)" style="font-size:.7rem">Remove</button>';
    $('ct-content-source').textContent='(will be replaced by file content)';
    var ti=$('ct-art-title');
    if(ti&&!ti.value.trim())ti.value=f.name.replace(/\.[^.]+$/,'').replace(/[_-]/g,' ');
  }

  window.ctClearFile = function(e){
    e.stopPropagation();selectedFile=null;if(fileInput)fileInput.value='';
    $('ct-upload-label').style.display='block';
    $('ct-upload-info').style.display='none';
    $('ct-content-source').textContent='';
  };

  // ── Chat History ──
  window.ctLoadConversations = function(){
    var src=$('ct-hist-source').value;
    var lng=$('ct-hist-lang').value;
    var qs='?limit=50';if(src)qs+='&source='+src;if(lng)qs+='&language='+lng;
    fetch('/api/admin/conversations'+qs,{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var tb=$('ct-convs-tbody');tb.innerHTML='';
      (d.conversations||[]).forEach(function(c){
        var last=c.last_message_at?c.last_message_at.substring(0,16).replace('T',' '):'—';
        tb.innerHTML+='<tr style="cursor:pointer" onclick="ctViewMessages(\''+c.id+'\')"><td style="font-size:.78rem">'+esc(c.session_id.substring(0,8))+'...</td><td>'+esc(c.source)+'</td><td>'+c.message_count+'</td><td style="font-size:.78rem">'+last+'</td></tr>';
      });
    });
  };

  window.ctViewMessages = function(convId){
    fetch('/api/admin/conversations/'+convId+'/messages',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var v=$('ct-msg-viewer');
      var html='<div class="card-body">';
      (d.messages||[]).forEach(function(m){
        var cls=m.role==='user'?'msg-user':'msg-assistant';
        var t=m.created_at?m.created_at.substring(11,16):'';
        var meta='<div style="font-size:.7rem;color:#999;margin-top:4px">'+t;
        if(m.response_time_ms)meta+=' ('+m.response_time_ms+'ms)';
        if(m.context_chunks)meta+=' | '+m.context_chunks+' chunks';
        meta+='</div>';
        html+='<div class="msg-item '+cls+'">'+esc(m.content)+meta+'</div>';
      });
      html+='</div>';
      v.innerHTML=html;
      v.scrollTop=v.scrollHeight;
    });
  };

  // ── Content Sources ──
  var TYPE_LABELS={key_message:'Key Message',product_narrative:'Product Narrative',seasonal_theme:'Seasonal Theme',brand_voice:'Brand Voice',custom:'Custom'};

  window.ctLoadContentSources = function(){
    fetch('/api/admin/content-sources',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var tb=$('ct-sources-tbody');tb.innerHTML='';
      (d.sources||[]).forEach(function(s){
        var st=s.is_active?'<span class="badge bg-green-lt">Active</span>':'<span class="badge bg-secondary-lt">Inactive</span>';
        var sid=esc(s.id);
        var typeLabel=TYPE_LABELS[s.type]||s.type;
        tb.innerHTML+='<tr><td><strong>'+esc(s.title)+'</strong><div style="font-size:.78rem;color:#999;margin-top:4px">'+esc((s.content||'').substring(0,80))+(s.content&&s.content.length>80?'...':'')+'</div></td>'
          +'<td>'+esc(typeLabel)+'</td><td>'+st+'</td><td>'+s.priority+'</td>'
          +'<td><button class="btn btn-outline-secondary btn-sm" onclick="ctEditSource(\''+sid+'\')">Edit</button> '
          +'<button class="btn btn-outline-secondary btn-sm" onclick="ctToggleSource(\''+sid+'\','+(!s.is_active)+')">'+(s.is_active?'Off':'On')+'</button> '
          +'<button class="btn btn-outline-danger btn-sm" onclick="ctDeleteSource(\''+sid+'\')">Del</button></td></tr>';
      });
    });
  };

  window.ctOpenCreateSource = function(){
    $('ct-source-modal-title').textContent='New Content Source';
    $('ct-source-edit-id').value='';
    $('ct-src-type').value='key_message';
    $('ct-src-title').value='';
    $('ct-src-content').value='';
    $('ct-src-priority').value='0';
    ctModal('ct-source-modal',true);
  };

  window.ctEditSource = function(id){
    fetch('/api/admin/content-sources',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var s=(d.sources||[]).find(function(x){return x.id===id});
      if(!s)return;
      $('ct-source-modal-title').textContent='Edit Content Source';
      $('ct-source-edit-id').value=id;
      $('ct-src-type').value=s.type||'custom';
      $('ct-src-title').value=s.title||'';
      $('ct-src-content').value=s.content||'';
      $('ct-src-priority').value=s.priority||0;
      ctModal('ct-source-modal',true);
    });
  };

  window.ctSaveSource = function(){
    var id=$('ct-source-edit-id').value;
    var data={type:$('ct-src-type').value,title:$('ct-src-title').value,content:$('ct-src-content').value,priority:parseInt($('ct-src-priority').value)||0};
    var url=id?'/api/admin/content-sources/'+id:'/api/admin/content-sources';
    var method=id?'PATCH':'POST';
    fetch(url,{method:method,headers:H,body:JSON.stringify(data)})
    .then(function(r){if(!r.ok)throw new Error();return r.json()})
    .then(function(){ctModal('ct-source-modal',false);ctLoadContentSources()})
    .catch(function(){alert('Failed to save content source')});
  };

  window.ctToggleSource = function(id,newState){
    fetch('/api/admin/content-sources/'+id,{method:'PATCH',headers:H,body:JSON.stringify({is_active:newState})})
    .then(function(){ctLoadContentSources()});
  };

  window.ctDeleteSource = function(id){
    if(!confirm('Delete this content source?'))return;
    fetch('/api/admin/content-sources/'+id,{method:'DELETE',headers:H})
    .then(function(){ctLoadContentSources()});
  };

  // ── Video Scripts ──
  window.ctLoadVideoScripts = function(){
    fetch('/api/admin/video-scripts',{headers:H})
    .then(function(r){return r.json()})
    .then(function(d){
      var scripts=d.scripts||[];
      $('ct-scripts-count').textContent=scripts.length+' script'+(scripts.length!==1?'s':'');
      var list=$('ct-scripts-list');list.innerHTML='';
      if(!scripts.length){list.innerHTML='<div class="card"><div class="card-body text-muted text-center">No video scripts yet. Scripts are generated daily at 06:00 UTC.</div></div>';return}
      scripts.forEach(function(s){
        var dt=s.date||'';
        var tags=(s.hashtags||[]).join(' ');
        list.innerHTML+='<div class="card mb-2"><div class="card-body">'
          +'<div class="d-flex justify-content-between align-items-center mb-2"><strong style="color:#406546">'+esc(s.topic||'Untitled')+'</strong><span class="text-muted" style="font-size:.78rem">'+esc(dt)+' · '+(s.estimated_duration||'')+'</span></div>'
          +'<div style="font-size:.85rem;margin-bottom:6px"><b>Hook:</b> '+esc(s.hook||'')+'</div>'
          +'<div style="font-size:.85rem;margin-bottom:6px"><b>Content:</b> '+esc(s.content||'')+'</div>'
          +'<div style="font-size:.85rem;margin-bottom:6px"><b>CTA:</b> '+esc(s.cta||'')+'</div>'
          +'<div style="font-size:.78rem;color:#999">'+esc(tags)+'</div>'
          +'</div></div>';
      });
    })
    .catch(function(){});
  };

  // ── Init on section load ──
  var initialized = false;
  window.addEventListener('dashboard:section', function(e){
    if(e.detail === 'content' && !initialized){
      initialized = true;
      ctLoadArticles();
    }
  });
  if(document.getElementById('sec-content') && document.getElementById('sec-content').style.display === 'block'){
    ctLoadArticles();
    initialized = true;
  }
})();
</script>
"""
