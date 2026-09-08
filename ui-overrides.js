/* VA CODES Medical VA UI overrides: NOTES + per-record edit/delete actions */
(function(){
  const style=document.createElement('style');
  style.textContent=`
    .notes-toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
    .notes-legend{display:flex;gap:8px;flex-wrap:wrap}
    .note-chip{display:inline-flex;align-items:center;border-radius:999px;padding:5px 10px;font-size:12px;font-weight:700;border:1px solid rgba(0,0,0,.06)}
    .note-row-joy{background:#fff1f6!important;border-left-color:#e9a8bd!important}
    .note-row-employer{background:#eef6ff!important;border-left-color:#a9c9ec!important}
    .note-row-shared{background:#fff0f1!important;border-left-color:#e5a5aa!important}
    tr.note-row-joy td, tr.note-row-employer td, tr.note-row-shared td{background:inherit!important}
    tr.note-row-joy td:first-child{border-left:4px solid #e9a8bd}
    tr.note-row-employer td:first-child{border-left:4px solid #a9c9ec}
    tr.note-row-shared td:first-child{border-left:4px solid #e5a5aa}
    .note-text{min-width:280px;max-width:520px;white-space:normal;line-height:1.5}
    .record-name{border:0;background:transparent;padding:0;text-align:left;font:inherit;font-weight:700;cursor:pointer;text-decoration:underline;text-decoration-color:transparent;text-underline-offset:3px}
    .record-name:hover{text-decoration-color:currentColor}
    .notes-card{overflow:hidden}
    .table-scroll{overflow-x:auto}
    .option-note{margin-top:0}
  `;
  document.head.appendChild(style);

  const noteTypes={
    joy:{label:'My Notes',from:'VA Joy',className:'note-row-joy'},
    employer:{label:'Employer Notes',from:'Employer',className:'note-row-employer'},
    shared:{label:'Shared Notes',from:'Both',className:'note-row-shared'}
  };

  function ensureNotes(){if(!Array.isArray(db.notes))db.notes=[];save()}
  function noteTypeBadge(type){const n=noteTypes[type]||noteTypes.shared;return `<span class="note-chip ${n.className}">${esc(n.label)}</span>`}

  function notes(){
    ensureNotes();
    return head('NOTES','Notes between VA Joy and the employer — personal or shared workspace notes.','＋ Add Note','add-note')+
      `<div class="notes-toolbar"><div class="notes-legend"><span class="note-chip note-row-joy">My Notes</span><span class="note-chip note-row-employer">Employer Notes</span><span class="note-chip note-row-shared">Shared Notes</span></div><select class="filter" id="noteFilter"><option value="all">All notes</option><option value="joy">My Notes</option><option value="employer">Employer Notes</option><option value="shared">Shared Notes</option></select></div>
      <div class="card notes-card"><div class="table-scroll">${table(['Date','From','Note','Patient / Record','Type','Action'],db.notes.map(n=>{const t=noteTypes[n.type]||noteTypes.shared;return `<tr class="${t.className}" data-note-row="${esc(n.id)}"><td>${esc(n.date||'')}</td><td><b>${esc(t.from)}</b></td><td class="note-text">${esc(n.text)}</td><td>${esc(n.patient||'—')}</td><td>${noteTypeBadge(n.type)}</td><td><button class="btn" data-note-menu="${esc(n.id)}">Options</button></td></tr>`}).join(''))}</div></div>`;
  }

  function addNote(existing){
    ensureNotes();
    const n=existing||{id:'N-'+Date.now(),type:'joy',text:'',patient:''};
    modal(existing?'Edit Note':'Add Note',`<div class="form-grid"><label class="field">Note type<select id="nType"><option value="joy" ${n.type==='joy'?'selected':''}>My Notes — VA Joy → Employer</option><option value="employer" ${n.type==='employer'?'selected':''}>Employer Notes — Employer → VA Joy</option><option value="shared" ${n.type==='shared'?'selected':''}>Shared Notes — visible to both</option></select></label><label class="field">Patient / record<select id="nPatient"><option value="">General note</option>${patients()}</select></label><label class="field full">Note<textarea id="nText" rows="7" placeholder="Write the note here..."></textarea></label></div>`,()=>{const text=$('#nText').value.trim();if(!text){toast('Note is required');return false}const item={id:n.id,type:$('#nType').value,text,patient:$('#nPatient').value||'',date:today()};if(existing){const i=db.notes.findIndex(x=>x.id===existing.id);if(i>-1)db.notes[i]=item;log('Note updated','Notes');toast('Note updated')}else{db.notes.unshift(item);log('Note added','Notes');toast('Note added')}save();render()},existing?'Update':'Save');
    if(n.patient)$('#nPatient').value=n.patient;
    $('#nText').value=n.text||'';
  }

  function noteOptions(noteId){
    const n=db.notes.find(x=>x.id===noteId);if(!n)return;
    modal('Note Options',`<p class="option-note"><b>${esc(noteTypes[n.type]?.label||'Note')}</b></p><p>${esc(n.text)}</p><p><b>Patient / record:</b> ${esc(n.patient||'General note')}</p>`,()=>{},'Close');
    const foot=$('#modalRoot .modal-foot');
    if(foot){const close=foot.querySelector('[data-close]');const edit=document.createElement('button');edit.className='btn primary';edit.textContent='Edit';edit.onclick=()=>{closeModal();addNote(n)};const del=document.createElement('button');del.className='btn danger';del.textContent='Delete';del.onclick=()=>{closeModal();deleteNote(noteId)};foot.insertBefore(del,close);foot.insertBefore(edit,close)}
  }
  function deleteNote(noteId){if(!db.notes.some(x=>x.id===noteId))return;if(!confirm('Delete this note?'))return;db.notes=db.notes.filter(x=>x.id!==noteId);log('Note deleted','Notes');save();render();toast('Note deleted')}

  function recordOptions(kind,recordId){
    const collection=db[kind];if(!Array.isArray(collection))return;const item=collection.find(x=>x.id===recordId);if(!item)return;
    const label={patients:'Patient',appointments:'Appointment',tasks:'Task',followups:'Follow-up',billing:'Billing record'}[kind]||'Record';
    const title=item.name||item.title||item.patient||item.claim||item.id||label;
    modal(`${label} Options`,`<p><b>${esc(title)}</b></p><p>Choose what to do with this record.</p>`,()=>{},'Close');
    const foot=$('#modalRoot .modal-foot');
    if(foot){const close=foot.querySelector('[data-close]');const edit=document.createElement('button');edit.className='btn primary';edit.textContent='Edit';edit.onclick=()=>{closeModal();editRecord(kind,recordId)};const del=document.createElement('button');del.className='btn danger';del.textContent='Delete';del.onclick=()=>{closeModal();deleteRecord(kind,recordId)};foot.insertBefore(del,close);foot.insertBefore(edit,close)}
  }

  function editRecord(kind,recordId){
    const item=db[kind]?.find(x=>x.id===recordId);if(!item)return;
    if(kind==='patients'){
      modal('Edit Patient',`<div class="form-grid"><label class="field">Patient name<input id="epName" value="${esc(item.name)}"></label><label class="field">Age<input id="epAge" type="number" value="${esc(item.age)}"></label><label class="field">Sex<select id="epSex"><option ${item.sex==='Female'?'selected':''}>Female</option><option ${item.sex==='Male'?'selected':''}>Male</option><option ${item.sex==='Other'?'selected':''}>Other</option><option ${item.sex==='Prefer not to say'?'selected':''}>Prefer not to say</option></select></label><label class="field">Status<select id="epStatus"><option ${item.status==='Active'?'selected':''}>Active</option><option ${item.status==='Follow-up'?'selected':''}>Follow-up</option><option ${item.status==='Pending'?'selected':''}>Pending</option></select></label></div>`,()=>{const name=$('#epName').value.trim();if(!name){toast('Patient name is required');return false}const old=item.name;item.name=name;item.age=$('#epAge').value;item.sex=$('#epSex').value;item.status=$('#epStatus').value;['appointments','tasks','followups','billing','insurance','documents','notes'].forEach(k=>{(db[k]||[]).forEach(x=>{if(x.patient===old)x.patient=name})});log('Patient updated: '+name,'Patients');save();render();toast('Patient updated')});
      return;
    }
    if(kind==='tasks'){
      modal('Edit Task',`<div class="form-grid"><label class="field">Task<input id="etTitle" value="${esc(item.title)}"></label><label class="field">Patient<select id="etPatient"><option value="${esc(item.patient||'')}">${esc(item.patient||'General')}</option>${patients()}</select></label><label class="field">Priority<select id="etPriority"><option ${item.priority==='High'?'selected':''}>High</option><option ${item.priority==='Medium'?'selected':''}>Medium</option><option ${item.priority==='Low'?'selected':''}>Low</option></select></label><label class="field">Status<select id="etStatus"><option ${item.status==='Open'?'selected':''}>Open</option><option ${item.status==='Completed'?'selected':''}>Completed</option></select></label></div>`,()=>{item.title=$('#etTitle').value.trim();if(!item.title){toast('Task title is required');return false}item.patient=$('#etPatient').value;item.priority=$('#etPriority').value;item.status=$('#etStatus').value;log('Task updated: '+item.title,'Tasks');save();render();toast('Task updated')});
      return;
    }
    toast('This record can be deleted from Options. Editing for this record type will be expanded next.');
  }

  function deleteRecord(kind,recordId){if(!db[kind])return;if(!confirm('Delete this record?'))return;const item=db[kind].find(x=>x.id===recordId);db[kind]=db[kind].filter(x=>x.id!==recordId);log((item?.name||item?.title||item?.patient||'Record')+' deleted',kind);save();render();toast('Record deleted')}

  const nav=document.querySelector('[data-view="messages"]');
  if(nav){nav.dataset.view='notes';nav.innerHTML='◇ <span>NOTES</span>'}
  views.notes=notes;

  function enhanceRecordNames(){
    const selectors=[['patients','[data-patient]'],['tasks','[data-complete-task]'],['appointments','[data-complete-appointment]'],['followups','[data-complete-followup]'],['billing','[data-paid]']];
    selectors.forEach(([kind,selector])=>document.querySelectorAll(selector).forEach(btn=>{const row=btn.closest('tr');if(!row)return;const cell=kind==='patients'?row.cells[1]:kind==='tasks'?row.cells[0]:row.cells[1];if(!cell||cell.querySelector('.record-name'))return;const recordId=btn.dataset.patient||btn.dataset.completeTask||btn.dataset.completeAppointment||btn.dataset.completeFollowup||btn.dataset.paid;const text=cell.textContent.trim();if(!recordId||!text)return;cell.innerHTML=`<button class="record-name" data-record-options="${esc(kind)}|${esc(recordId)}">${esc(text)}</button>`}));
  }
  const observer=new MutationObserver(()=>enhanceRecordNames());
  observer.observe($('#content'),{childList:true,subtree:true});
  enhanceRecordNames();

  function bindNoteFilter(){const f=$('#noteFilter');if(!f||f.dataset.bound)return;f.dataset.bound='1';f.addEventListener('change',()=>{const q=f.value;document.querySelectorAll('[data-note-row]').forEach(r=>r.style.display=q==='all'||r.classList.contains('note-row-'+q)?'':'none')})}

  document.addEventListener('click',e=>{
    const no=e.target.closest('[data-note-menu]');if(no){noteOptions(no.dataset.noteMenu);return}
    const ro=e.target.closest('[data-record-options]');if(ro){const [kind,recordId]=ro.dataset.recordOptions.split('|');recordOptions(kind,recordId);return}
    const add=e.target.closest('[data-action="add-note"]');if(add){e.preventDefault();addNote();return}
    if(view==='notes')setTimeout(bindNoteFilter,0);
  },true);

  render();
  bindNoteFilter();
})();
