"""Email marketing section — ported from email_page.py."""


def html() -> str:
    return """
<!-- Email Sub-Tabs -->
<div class="sub-tabs">
  <div class="sub-tab active" onclick="emSwitchTab('campaigns')">Campaigns</div>
  <div class="sub-tab" onclick="emSwitchTab('newsletter')">Newsletter</div>
  <div class="sub-tab" onclick="emSwitchTab('subscribers')">Subscribers</div>
  <div class="sub-tab" onclick="emSwitchTab('brand')">Brand Assets</div>
</div>

<!-- Campaigns Panel -->
<div class="sub-panel active" id="em-panel-campaigns">
  <div class="toolbar" style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap">
    <button class="btn btn-primary btn-sm" onclick="emShowNewCampaign()"><i class="ti ti-plus"></i> New Campaign</button>
  </div>
  <div id="em-campaigns-list"><div class="text-muted text-center py-4">Loading...</div></div>
  <!-- Campaign Editor (hidden by default) -->
  <div id="em-campaign-editor" style="display:none">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap">
      <button class="btn btn-outline-secondary btn-sm" onclick="emBackToCampaigns()">&larr; Back</button>
      <span id="em-editor-campaign-name" style="font-weight:500;font-size:.9rem"></span>
      <span id="em-editor-status-badge"></span>
    </div>
    <div style="max-width:500px;margin-bottom:16px">
      <label class="form-label">Subject Line</label>
      <input type="text" class="form-control" id="em-editor-subject" placeholder="Email subject...">
    </div>
    <div class="em-editor-layout">
      <div class="em-preview-frame">
        <iframe id="em-preview-iframe" style="width:100%;min-height:600px;border:none"></iframe>
      </div>
      <div class="em-editor-panel">
        <h4 style="font-size:.9rem;font-weight:600;color:#406546;margin-bottom:16px">Edit Text</h4>
        <div id="em-editable-blocks"></div>
        <h4 id="em-links-heading" style="display:none;margin-top:20px;font-size:.9rem;font-weight:600;color:#406546">Edit Links</h4>
        <div id="em-editable-links"></div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:20px">
          <button class="btn btn-primary btn-sm" onclick="emSaveCampaign()">Save</button>
          <button class="btn btn-outline-secondary btn-sm" onclick="emSendTest()">Send Test</button>
          <button class="btn btn-outline-secondary btn-sm" onclick="emRegenerateDesign()">Regenerate</button>
          <button class="btn btn-primary btn-sm" onclick="emSendCampaign()" id="em-send-btn">Send to All</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Newsletter Panel -->
<div class="sub-panel" id="em-panel-newsletter">
  <div class="toolbar" style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
    <button class="btn btn-primary btn-sm" onclick="emShowNewSchedule()"><i class="ti ti-plus"></i> New Schedule</button>
  </div>
  <div id="em-schedules-list"><div class="text-muted text-center py-4">Loading...</div></div>
  <!-- New Schedule Form -->
  <div id="em-schedule-form" style="display:none" class="card p-3 mt-3">
    <h4 style="font-size:.95rem;font-weight:600;color:#406546;margin-bottom:16px">New Newsletter Schedule</h4>
    <div class="mb-3"><label class="form-label">Name</label><input type="text" class="form-control" id="em-sched-name" placeholder="e.g. Weekly Matcha Recipe"></div>
    <div class="mb-3"><label class="form-label">Template</label>
      <select class="form-select" id="em-sched-template"><option value="">Loading...</option></select>
    </div>
    <div class="mb-3"><label class="form-label">Custom Prompt (optional)</label>
      <textarea class="form-control" id="em-sched-prompt" placeholder="Custom AI prompt for content generation..." rows="3"></textarea>
    </div>
    <div class="mb-3"><label class="form-label">Target Audience</label>
      <select class="form-select" id="em-sched-target">
        <option value="">All subscribers</option>
        <option value="retail">Retail customers</option>
        <option value="wholesale">Wholesale partners</option>
      </select>
    </div>
    <div class="mb-3"><label class="form-label">Language</label>
      <select class="form-select" id="em-sched-lang"><option value="en">English</option><option value="ja">Japanese</option></select>
    </div>
    <div class="mb-3"><label class="form-label">Days of Week</label>
      <div class="day-checks" id="em-sched-days">
        <div class="day-check" data-day="0" onclick="this.classList.toggle('sel')">Su</div>
        <div class="day-check sel" data-day="1" onclick="this.classList.toggle('sel')">Mo</div>
        <div class="day-check" data-day="2" onclick="this.classList.toggle('sel')">Tu</div>
        <div class="day-check" data-day="3" onclick="this.classList.toggle('sel')">We</div>
        <div class="day-check sel" data-day="4" onclick="this.classList.toggle('sel')">Th</div>
        <div class="day-check" data-day="5" onclick="this.classList.toggle('sel')">Fr</div>
        <div class="day-check" data-day="6" onclick="this.classList.toggle('sel')">Sa</div>
      </div>
    </div>
    <div class="mb-3"><label class="form-label">Send Time (UTC)</label><input type="time" class="form-control" id="em-sched-time" value="14:00" style="max-width:200px"></div>
    <div class="d-flex gap-2">
      <button class="btn btn-primary btn-sm" onclick="emCreateSchedule()">Create</button>
      <button class="btn btn-outline-secondary btn-sm" onclick="emHideScheduleForm()">Cancel</button>
    </div>
  </div>
</div>

<!-- Subscribers Panel -->
<div class="sub-panel" id="em-panel-subscribers">
  <div class="toolbar" style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap">
    <button class="btn btn-primary btn-sm" onclick="emShowAddSubscriber()"><i class="ti ti-plus"></i> Add Subscriber</button>
    <button class="btn btn-outline-secondary btn-sm" onclick="emShowImportCSV()">Import CSV</button>
    <button class="btn btn-outline-secondary btn-sm" onclick="emSyncShopify()">Sync Shopify</button>
    <select class="form-select form-select-sm" id="em-sub-tag-filter" onchange="emLoadSubscribers()" style="width:auto">
      <option value="">All Tags</option>
    </select>
  </div>
  <div id="em-subscribers-list"><div class="text-muted text-center py-4">Loading...</div></div>
</div>

<!-- Brand Assets Panel -->
<div class="sub-panel" id="em-panel-brand">
  <div class="row">
    <div class="col-lg-6">
      <div class="mb-3">
        <label class="form-label">Logo URL</label>
        <input type="text" class="form-control" id="em-brand-logo" placeholder="https://...">
        <div style="margin-top:8px"><img id="em-logo-preview" style="max-height:60px;display:none"></div>
      </div>
      <div class="mb-3">
        <label class="form-label">Colors</label>
        <div class="d-flex gap-3 flex-wrap">
          <div class="d-flex align-items-center gap-2"><input type="color" id="em-color-primary" value="#406546" style="width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0"><span class="text-muted" style="font-size:.82rem">Primary</span></div>
          <div class="d-flex align-items-center gap-2"><input type="color" id="em-color-secondary" value="#F9F0E2" style="width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0"><span class="text-muted" style="font-size:.82rem">Secondary</span></div>
          <div class="d-flex align-items-center gap-2"><input type="color" id="em-color-accent" value="#FFFFFF" style="width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0"><span class="text-muted" style="font-size:.82rem">Accent</span></div>
          <div class="d-flex align-items-center gap-2"><input type="color" id="em-color-text" value="#1a1a1a" style="width:40px;height:40px;border:none;border-radius:8px;cursor:pointer;padding:0"><span class="text-muted" style="font-size:.82rem">Text</span></div>
        </div>
      </div>
      <div class="mb-3"><label class="form-label">Font Family</label><input type="text" class="form-control" id="em-brand-font" value="Work Sans, Helvetica, Arial, sans-serif"></div>
      <div class="mb-3"><label class="form-label">Footer Text</label><input type="text" class="form-control" id="em-brand-footer" value="NAKAI Matcha | Kagoshima, Japan"></div>
      <button class="btn btn-primary btn-sm" onclick="emSaveBrandAssets()">Save Brand Settings</button>
    </div>
    <div class="col-lg-6">
      <div class="mb-3">
        <label class="form-label">Product Photos</label>
        <input type="file" class="form-control" id="em-photo-upload" accept="image/*" onchange="emUploadPhoto()">
      </div>
      <div class="photo-grid" id="em-photo-grid"></div>
    </div>
  </div>
</div>

<!-- Modals -->
<div class="modal modal-blur fade" id="em-modal-new-campaign" tabindex="-1">
<div class="modal-dialog modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title">New Campaign</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <div class="mb-3"><label class="form-label">Campaign Name</label><input type="text" class="form-control" id="em-new-camp-name" placeholder="e.g. Spring Collection Launch"></div>
    <div class="mb-3"><label class="form-label">Describe your email</label><textarea class="form-control" id="em-new-camp-desc" rows="3" placeholder="e.g. Product launch email with bright spring design"></textarea></div>
    <div class="mb-3"><label class="form-label">Target Language</label>
      <select class="form-select" id="em-new-camp-lang"><option value="en">English</option><option value="ja">Japanese</option></select>
    </div>
    <div class="mb-3">
      <label class="form-label">Campaign Photos (hero image)</label>
      <input type="file" class="form-control" id="em-new-camp-photos" accept="image/*" multiple>
      <div id="em-camp-photo-preview" style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"></div>
    </div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" id="em-gen-btn" onclick="emCreateCampaign()">Generate Design</button>
  </div>
</div></div>
</div>

<div class="modal modal-blur fade" id="em-modal-add-sub" tabindex="-1">
<div class="modal-dialog modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title">Add Subscriber</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control" id="em-new-sub-email" placeholder="email@example.com"></div>
    <div class="mb-3"><label class="form-label">Name</label><input type="text" class="form-control" id="em-new-sub-name" placeholder="John Doe"></div>
    <div class="mb-3"><label class="form-label">Tags (comma-separated)</label><input type="text" class="form-control" id="em-new-sub-tags" placeholder="newsletter, vip"></div>
    <div class="mb-3"><label class="form-label">Language</label>
      <select class="form-select" id="em-new-sub-lang"><option value="en">English</option><option value="ja">Japanese</option></select>
    </div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" onclick="emAddSubscriber()">Add</button>
  </div>
</div></div>
</div>

<div class="modal modal-blur fade" id="em-modal-csv" tabindex="-1">
<div class="modal-dialog modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title">Import Subscribers from CSV</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <p class="text-muted mb-3" style="font-size:.85rem">CSV columns: email, name, tags, language</p>
    <input type="file" class="form-control" id="em-csv-file" accept=".csv">
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" onclick="emImportCSV()">Import</button>
  </div>
</div></div>
</div>

<div class="modal modal-blur fade" id="em-modal-test" tabindex="-1">
<div class="modal-dialog modal-dialog-centered"><div class="modal-content">
  <div class="modal-header"><h5 class="modal-title">Send Test Email</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
  <div class="modal-body">
    <div class="mb-3"><label class="form-label">Send to</label><input type="email" class="form-control" id="em-test-email" placeholder="your@email.com"></div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
    <button type="button" class="btn btn-primary btn-sm" onclick="emDoSendTest()">Send</button>
  </div>
</div></div>
</div>

<script>
(function(){
  var H = {'Content-Type': 'application/json'};
  var currentCampaignId = null;
  var currentCampaign = null;
  var nlTemplates = {};

  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function $(id){return document.getElementById(id);}

  async function api(method, path, body){
    var opts = {method: method, headers: H};
    if(body) opts.body = JSON.stringify(body);
    var r = await fetch(path, opts);
    var data = r.ok ? await r.json() : null;
    return {ok: r.ok, status: r.status, data: data};
  }
  async function apiForm(method, path, formData){
    var r = await fetch(path, {method: method, body: formData, credentials: 'same-origin'});
    var data = r.ok ? await r.json() : null;
    return {ok: r.ok, data: data};
  }

  function emModal(id, show){
    var el = $(id);
    if(!el) return;
    if(typeof bootstrap !== 'undefined'){
      var m = bootstrap.Modal.getOrCreateInstance(el);
      show ? m.show() : m.hide();
    } else {
      el.style.display = show ? 'flex' : 'none';
      el.classList.toggle('show', show);
    }
  }

  // ── Sub-Tabs ──
  var TAB_ORDER = ['campaigns','newsletter','subscribers','brand'];
  window.emSwitchTab = function(name){
    document.querySelectorAll('#sec-email .sub-tab').forEach(function(t,i){t.classList.toggle('active', TAB_ORDER[i]===name)});
    document.querySelectorAll('#sec-email .sub-panel').forEach(function(p){p.classList.remove('active')});
    $('em-panel-'+name).classList.add('active');
    if(name==='campaigns') emBackToCampaigns();
    if(name==='newsletter') emLoadSchedules();
  };

  function loadAll(){emLoadCampaigns();emLoadSubscribers();emLoadBrandAssets();emLoadTemplates();}

  // ── Campaigns ──
  async function emLoadCampaigns(){
    var r = await api('GET','/api/email/campaigns');
    var el = $('em-campaigns-list');
    if(!r.ok||!r.data||r.data.length===0){
      el.innerHTML='<div class="text-center text-muted py-4"><p>No campaigns yet</p><button class="btn btn-primary btn-sm" onclick="emShowNewCampaign()">Create your first campaign</button></div>';
      return;
    }
    var html='<div class="table-responsive"><table class="table table-vcenter table-hover card-table"><thead><tr><th>Name</th><th>Status</th><th>Subject</th><th>Sent</th><th>Actions</th></tr></thead><tbody>';
    r.data.forEach(function(c){
      var stats=c.stats||{};
      var sentCount=stats.sent||0;
      html+='<tr><td><a href="#" onclick="emOpenCampaign(\''+c.id+'\');return false" style="color:#406546;text-decoration:none;font-weight:500">'+esc(c.name)+'</a></td>'
        +'<td><span class="badge bg-'+({draft:'secondary',generating:'azure',ready:'green',sending:'orange',sent:'green',failed:'red'}[c.status]||'secondary')+'-lt">'+c.status+'</span></td>'
        +'<td>'+esc(c.subject||'—')+'</td>'
        +'<td>'+(sentCount>0?sentCount:'—')+'</td>'
        +'<td><button class="btn btn-outline-danger btn-sm" onclick="emDeleteCampaign(\''+c.id+'\')">Delete</button></td></tr>';
    });
    html+='</tbody></table></div>';
    el.innerHTML=html;
  }

  window.emShowNewCampaign = function(){emModal('em-modal-new-campaign',true);};

  window.emCreateCampaign = async function(){
    var name=$('em-new-camp-name').value.trim();
    var desc=$('em-new-camp-desc').value.trim();
    var lang=$('em-new-camp-lang').value;
    if(!name||!desc){alert('Name and description are required');return;}
    var btn=$('em-gen-btn');
    btn.textContent='Uploading photos...';btn.disabled=true;
    var photoFiles=$('em-new-camp-photos').files;
    var photoUrls=[];
    for(var i=0;i<photoFiles.length;i++){
      var fd=new FormData();fd.append('file',photoFiles[i]);
      var up=await apiForm('POST','/api/email/campaign-photo',fd);
      if(up.ok&&up.data.url)photoUrls.push(up.data.url);
    }
    btn.textContent='Generating design...';
    var r=await api('POST','/api/email/campaigns',{name:name,description:desc,target_language:lang,campaign_photos:photoUrls});
    btn.textContent='Generate Design';btn.disabled=false;
    $('em-new-camp-photos').value='';
    $('em-camp-photo-preview').innerHTML='';
    emModal('em-modal-new-campaign',false);
    if(r.ok){emOpenCampaignData(r.data);}else{alert('Failed to create campaign');}
  };

  window.emOpenCampaign = async function(id){
    var r=await api('GET','/api/email/campaigns/'+id);
    if(r.ok)emOpenCampaignData(r.data);
  };

  function emOpenCampaignData(c){
    currentCampaignId=c.id;
    currentCampaign=c;
    $('em-campaigns-list').style.display='none';
    $('em-panel-campaigns').querySelector('.toolbar').style.display='none';
    $('em-campaign-editor').style.display='block';
    $('em-editor-campaign-name').textContent=c.name;
    $('em-editor-status-badge').innerHTML='<span class="badge bg-'+(({draft:'secondary',generating:'azure',ready:'green',sending:'orange',sent:'green',failed:'red'})[c.status]||'secondary')+'-lt">'+c.status+'</span>';
    $('em-editor-subject').value=c.subject||'';
    var iframe=$('em-preview-iframe');
    iframe.srcdoc=c.html_content||'<p style="padding:40px;color:#999;text-align:center">No content generated yet</p>';
    var blocks=c.editable_blocks||[];
    var textBlocks=blocks.filter(function(b){return b.type==='text'});
    var linkBlocks=blocks.filter(function(b){return b.type==='link'});
    var el=$('em-editable-blocks');
    if(textBlocks.length===0){
      el.innerHTML='<p class="text-muted" style="font-size:.85rem">No editable text blocks found</p>';
    }else{
      el.innerHTML=textBlocks.map(function(b){return '<div class="mb-3"><label class="form-label" style="text-transform:capitalize">'+b.name+'</label><textarea class="form-control" data-block="'+b.name+'" placeholder="'+esc(b.placeholder)+'" rows="2">'+esc(b.current_text)+'</textarea></div>'}).join('');
    }
    var linksEl=$('em-editable-links');
    var linksHeading=$('em-links-heading');
    if(linkBlocks.length>0){
      linksHeading.style.display='block';
      linksEl.innerHTML=linkBlocks.map(function(b){return '<div class="mb-3"><label class="form-label" style="text-transform:capitalize">'+b.name+'</label><input type="url" class="form-control" data-link="'+b.name+'" placeholder="'+esc(b.placeholder)+'" value="'+esc(b.current_url||'')+'"></div>'}).join('');
    }else{
      linksHeading.style.display='none';
      linksEl.innerHTML='';
    }
  }

  window.emBackToCampaigns = function(){
    currentCampaignId=null;currentCampaign=null;
    $('em-campaign-editor').style.display='none';
    $('em-campaigns-list').style.display='block';
    var tb=$('em-panel-campaigns').querySelector('.toolbar');
    if(tb)tb.style.display='flex';
    emLoadCampaigns();
  };

  window.emSaveCampaign = async function(){
    if(!currentCampaignId)return;
    var subject=$('em-editor-subject').value.trim();
    var edits={};
    document.querySelectorAll('#em-editable-blocks textarea').forEach(function(ta){edits[ta.dataset.block]=ta.value});
    var link_edits={};
    document.querySelectorAll('#em-editable-links input[data-link]').forEach(function(inp){if(inp.value.trim())link_edits[inp.dataset.link]=inp.value.trim()});
    var body={subject:subject,edits:edits};
    if(Object.keys(link_edits).length>0)body.link_edits=link_edits;
    var r=await api('PATCH','/api/email/campaigns/'+currentCampaignId,body);
    if(r.ok){emOpenCampaignData(r.data);alert('Saved!');}else{alert('Save failed');}
  };

  window.emSendTest = function(){emModal('em-modal-test',true);};
  window.emDoSendTest = async function(){
    var email=$('em-test-email').value.trim();
    if(!email){alert('Enter email');return;}
    var subject=$('em-editor-subject').value.trim();
    if(subject)await api('PATCH','/api/email/campaigns/'+currentCampaignId,{subject:subject});
    var r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/send-test',{email:email});
    emModal('em-modal-test',false);
    if(r.ok)alert('Test email sent!');else alert('Failed to send test');
  };

  window.emRegenerateDesign = async function(){
    if(!currentCampaignId)return;
    if(!confirm('This will regenerate the design. Continue?'))return;
    $('em-editor-status-badge').innerHTML='<span class="badge bg-azure-lt">generating...</span>';
    var r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/regenerate');
    if(r.ok)emOpenCampaignData(r.data);else alert('Regeneration failed');
  };

  window.emSendCampaign = async function(){
    if(!currentCampaignId)return;
    var subject=$('em-editor-subject').value.trim();
    if(!subject){alert('Subject is required before sending');return;}
    await api('PATCH','/api/email/campaigns/'+currentCampaignId,{subject:subject});
    if(!confirm('Send this campaign to ALL active subscribers?'))return;
    var r=await api('POST','/api/email/campaigns/'+currentCampaignId+'/send');
    if(r.ok){alert('Campaign is being sent!');emPollStatus(currentCampaignId);}
    else{alert('Failed: '+(r.data&&r.data.detail?r.data.detail:'unknown error'));}
  };

  async function emPollStatus(id){
    for(var i=0;i<30;i++){
      await new Promise(function(r){setTimeout(r,2000)});
      var r=await api('GET','/api/email/campaigns/'+id);
      if(r.ok&&r.data.status!=='sending'){
        if(currentCampaignId===id)emOpenCampaignData(r.data);
        return;
      }
    }
  }

  window.emDeleteCampaign = async function(id){
    if(!confirm('Delete this campaign?'))return;
    await api('DELETE','/api/email/campaigns/'+id);
    emLoadCampaigns();
  };

  // ── Subscribers ──
  window.emLoadSubscribers = async function(){
    var tag=$('em-sub-tag-filter').value;
    var r=await api('GET','/api/email/subscribers'+(tag?'?tag='+tag:''));
    var el=$('em-subscribers-list');
    if(!r.ok||!r.data||r.data.length===0){
      el.innerHTML='<div class="text-center text-muted py-4">No subscribers yet</div>';
      return;
    }
    var allTags=new Set();
    r.data.forEach(function(s){(s.tags||[]).forEach(function(t){allTags.add(t)})});
    var sel=$('em-sub-tag-filter');
    var currentVal=sel.value;
    sel.innerHTML='<option value="">All Tags</option>'+Array.from(allTags).sort().map(function(t){return '<option value="'+t+'"'+(t===currentVal?' selected':'')+'>'+t+'</option>'}).join('');
    var html='<div class="table-responsive"><table class="table table-vcenter table-hover card-table"><thead><tr><th>Email</th><th>Name</th><th>Tags</th><th>Lang</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
    r.data.forEach(function(s){
      var tags=(s.tags||[]).map(function(t){return '<span class="badge bg-green-lt" style="margin-right:4px">'+esc(t)+'</span>'}).join('');
      html+='<tr><td>'+esc(s.email)+'</td><td>'+esc(s.name||'—')+'</td><td>'+(tags||'—')+'</td><td>'+(s.language||'en')+'</td>'
        +'<td><span class="badge bg-'+(s.is_active?'green':'red')+'-lt">'+(s.is_active?'Active':'Unsubscribed')+'</span></td>'
        +'<td><button class="btn btn-outline-danger btn-sm" onclick="emDeleteSubscriber(\''+s.id+'\')">Delete</button></td></tr>';
    });
    html+='</tbody></table></div>';
    el.innerHTML=html;
  };

  window.emShowAddSubscriber = function(){emModal('em-modal-add-sub',true);};
  window.emAddSubscriber = async function(){
    var email=$('em-new-sub-email').value.trim();
    var name=$('em-new-sub-name').value.trim();
    var tagsStr=$('em-new-sub-tags').value.trim();
    var lang=$('em-new-sub-lang').value;
    if(!email){alert('Email is required');return;}
    var tags=tagsStr?tagsStr.split(',').map(function(t){return t.trim()}).filter(Boolean):[];
    var r=await api('POST','/api/email/subscribers',{email:email,name:name,tags:tags,language:lang});
    emModal('em-modal-add-sub',false);
    if(r.ok){emLoadSubscribers();}else{alert('Failed (may already exist)');}
  };

  window.emShowImportCSV = function(){emModal('em-modal-csv',true);};
  window.emImportCSV = async function(){
    var file=$('em-csv-file').files[0];
    if(!file){alert('Select a CSV file');return;}
    var fd=new FormData();fd.append('file',file);
    var r=await apiForm('POST','/api/email/subscribers/import',fd);
    emModal('em-modal-csv',false);
    if(r.ok){
      var msg='Imported: '+r.data.imported;
      if(r.data.errors&&r.data.errors.length)alert(msg+'\nErrors: '+r.data.errors.join(', '));
      else alert(msg);
      emLoadSubscribers();
    }else{alert('Import failed');}
  };

  window.emDeleteSubscriber = async function(id){
    if(!confirm('Delete this subscriber?'))return;
    await api('DELETE','/api/email/subscribers/'+id);
    emLoadSubscribers();
  };

  // ── Brand Assets ──
  window.emLoadBrandAssets = async function(){
    var r=await api('GET','/api/email/brand-assets');
    if(!r.ok)return;
    var a=r.data;
    $('em-brand-logo').value=a.logo_url||'';
    emUpdateLogoPreview();
    var c=a.colors||{};
    $('em-color-primary').value=c.primary||'#406546';
    $('em-color-secondary').value=c.secondary||'#F9F0E2';
    $('em-color-accent').value=c.accent||'#FFFFFF';
    $('em-color-text').value=c.text||'#1a1a1a';
    $('em-brand-font').value=a.font_family||'Work Sans, Helvetica, Arial, sans-serif';
    $('em-brand-footer').value=a.footer_text||'NAKAI Matcha | Kagoshima, Japan';
    emRenderPhotos(a.photos||[]);
  };

  function emUpdateLogoPreview(){
    var url=$('em-brand-logo').value;
    var img=$('em-logo-preview');
    if(url){img.src=url;img.style.display='block';}else{img.style.display='none';}
  }
  var logoInput=$('em-brand-logo');
  if(logoInput) logoInput.addEventListener('input', emUpdateLogoPreview);

  function emRenderPhotos(photos){
    var el=$('em-photo-grid');
    el.innerHTML=photos.map(function(p,i){return '<div class="photo-card"><img src="'+p.url+'" alt="'+esc(p.label||'')+'"><button class="del-btn" onclick="emDeletePhoto('+i+')">x</button></div>'}).join('');
  }

  window.emSaveBrandAssets = async function(){
    var data={
      logo_url:$('em-brand-logo').value.trim(),
      colors:{primary:$('em-color-primary').value,secondary:$('em-color-secondary').value,accent:$('em-color-accent').value,text:$('em-color-text').value},
      font_family:$('em-brand-font').value.trim(),
      footer_text:$('em-brand-footer').value.trim()
    };
    var r=await api('POST','/api/email/brand-assets',data);
    if(r.ok)alert('Saved!');else alert('Failed to save');
  };

  window.emUploadPhoto = async function(){
    var file=$('em-photo-upload').files[0];
    if(!file)return;
    var fd=new FormData();fd.append('file',file);fd.append('label',file.name);
    var r=await apiForm('POST','/api/email/brand-assets/photo',fd);
    if(r.ok){emLoadBrandAssets();$('em-photo-upload').value='';}
    else alert('Upload failed');
  };

  window.emDeletePhoto = async function(idx){
    if(!confirm('Delete this photo?'))return;
    await api('DELETE','/api/email/brand-assets/photo/'+idx);
    emLoadBrandAssets();
  };

  // ── Photo Preview ──
  var campPhotos=$('em-new-camp-photos');
  if(campPhotos) campPhotos.addEventListener('change',function(){
    var el=$('em-camp-photo-preview');el.innerHTML='';
    for(var i=0;i<this.files.length;i++){
      var url=URL.createObjectURL(this.files[i]);
      el.innerHTML+='<div style="width:60px;height:60px;border-radius:6px;overflow:hidden;background:#f5f5f5"><img src="'+url+'" style="width:100%;height:100%;object-fit:cover"></div>';
    }
  });

  // ── Shopify Sync ──
  window.emSyncShopify = async function(){
    if(!confirm('Sync marketing-consented customers from Shopify?'))return;
    var r=await api('POST','/api/email/subscribers/sync-shopify');
    if(r.ok){alert('Synced: '+r.data.synced+', Skipped: '+r.data.skipped+' ('+r.data.total_shopify+' total from Shopify)');emLoadSubscribers();}
    else{alert('Shopify sync failed');}
  };

  // ── Newsletter Templates & Schedules ──
  async function emLoadTemplates(){
    var r=await api('GET','/api/email/newsletter-templates');
    if(r.ok){
      nlTemplates=r.data;
      var sel=$('em-sched-template');
      sel.innerHTML='<option value="">(Custom prompt)</option>'+Object.entries(r.data).map(function(e){return '<option value="'+e[0]+'">'+esc(e[1].name_en)+' / '+esc(e[1].name_ja)+'</option>'}).join('');
    }
  }

  var DAY_NAMES=['Su','Mo','Tu','We','Th','Fr','Sa'];

  window.emShowNewSchedule = function(){$('em-schedule-form').style.display='block';};
  window.emHideScheduleForm = function(){$('em-schedule-form').style.display='none';};

  window.emCreateSchedule = async function(){
    var name=$('em-sched-name').value.trim();
    if(!name){alert('Name is required');return;}
    var template_key=$('em-sched-template').value;
    var custom_prompt=$('em-sched-prompt').value.trim();
    var target=$('em-sched-target').value;
    var target_tags=target?[target]:[];
    var target_language=$('em-sched-lang').value;
    var days_of_week=Array.from(document.querySelectorAll('#em-sched-days .day-check.sel')).map(function(e){return parseInt(e.dataset.day)});
    var send_time_utc=$('em-sched-time').value||'14:00';
    if(days_of_week.length===0){alert('Select at least one day');return;}
    var r=await api('POST','/api/email/schedules',{name:name,template_key:template_key,custom_prompt:custom_prompt,target_tags:target_tags,target_language:target_language,days_of_week:days_of_week,send_time_utc:send_time_utc,is_active:false});
    if(r.ok){emHideScheduleForm();emLoadSchedules();}else{alert('Failed to create schedule');}
  };

  window.emLoadSchedules = async function(){
    var r=await api('GET','/api/email/schedules');
    var el=$('em-schedules-list');
    if(!r.ok||!r.data||r.data.length===0){
      el.innerHTML='<div class="text-center text-muted py-4"><p>No newsletter schedules yet</p><button class="btn btn-primary btn-sm" onclick="emShowNewSchedule()">Create your first schedule</button></div>';
      return;
    }
    var html='<div class="schedule-grid">';
    r.data.forEach(function(s){
      var days=(s.days_of_week||[]).map(function(d){return DAY_NAMES[d]||d}).join(', ');
      var tpl=nlTemplates[s.template_key];
      var tplName=tpl?tpl.name_en:(s.custom_prompt?'Custom':'—');
      var tags=(s.target_tags||[]).join(', ')||'All';
      var lastSent=s.last_sent_at?new Date(s.last_sent_at).toLocaleDateString():'Never';
      var toggleCls=s.is_active?'toggle on':'toggle';
      html+='<div class="sched-card"><h4>'+esc(s.name)+'</h4>'
        +'<div class="meta">Template: '+esc(tplName)+'<br>Days: '+days+' at '+(s.send_time_utc||'14:00')+' UTC<br>Audience: '+esc(tags)+' | '+(s.target_language||'en')+'<br>Last sent: '+lastSent+'</div>'
        +'<div class="actions"><div class="'+toggleCls+'" onclick="emToggleSchedule(\''+s.id+'\','+(!s.is_active)+')"></div>'
        +'<span style="font-size:.78rem;color:#666">'+(s.is_active?'Active':'Paused')+'</span>'
        +'<button class="btn btn-outline-secondary btn-sm" onclick="emTriggerSchedule(\''+s.id+'\')">Send Now</button>'
        +'<button class="btn btn-outline-secondary btn-sm" onclick="emDeleteSchedule(\''+s.id+'\')">Delete</button></div></div>';
    });
    html+='</div>';
    el.innerHTML=html;
  };

  window.emToggleSchedule = async function(id,active){
    await api('PATCH','/api/email/schedules/'+id,{is_active:active});
    emLoadSchedules();
  };

  window.emTriggerSchedule = async function(id){
    if(!confirm('Send this newsletter now?'))return;
    var r=await api('POST','/api/email/schedules/'+id+'/trigger');
    if(r.ok)alert('Newsletter is being generated and sent!');
    else alert('Failed to trigger');
  };

  window.emDeleteSchedule = async function(id){
    if(!confirm('Delete this schedule?'))return;
    await api('DELETE','/api/email/schedules/'+id);
    emLoadSchedules();
  };

  // ── Init on section load ──
  var initialized = false;
  window.addEventListener('dashboard:section', function(e){
    if(e.detail === 'email' && !initialized){
      initialized = true;
      loadAll();
    }
  });
  // Auto-init if already visible
  if(document.getElementById('sec-email') && document.getElementById('sec-email').style.display === 'block'){
    loadAll();
    initialized = true;
  }
})();
</script>
"""
