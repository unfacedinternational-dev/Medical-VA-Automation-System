/* Reliable patient-name click handler and profile renderer. */
(function(){
  function e(s){return String(s??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]))}
  function list(k,name){return Array.isArray(db[k])?(db[k]||[]).filter(x=>x.patient===name):[]}
  function rows(items,cols){return items.length?items.map(x=>`<tr>${cols.map(c=>`<td>${e(typeof c==='function'?c(x):(x[c]??'—'))}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${cols.length}" class="profile-empty">No records yet</td></tr>`}
  function profile(id){
    const p=(db.patients||[]).find(x=>x.id===id); if(!p)return;
    const ins=list('insurance',p.name), bills=list('billing',p.name), apps=list('appointments',p.name), docs=list('documents',p.name), tasks=list('tasks',p.name), follows=list('followups',p.name), notes=list('notes',p.name);
    const total=bills.reduce((s,x)=>s+Number(x.amount||0),0), paid=bills.filter(x=>/paid/i.test(x.status||'')).reduce((s,x)=>s+Number(x.amount||0),0);
    const table=(h,r)=>`<div class="table-scroll"><table class="profile-table"><thead><tr>${h.map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${r}</tbody></table></div>`;
    const body=`<div class="patient-profile">
      <div class="patient-profile-card"><h4>Patient Information</h4><div class="patient-profile-grid"><p><strong>Full Name</strong><br>${e(p.name)}</p><p><strong>Age</strong><br>${e(p.age||'—')}</p><p><strong>Gender</strong><br>${e(p.sex||'—')}</p><p><strong>Status</strong><br>${e(p.status||'—')}</p></div></div>
      <div class="patient-profile-grid">
        <div class="patient-profile-card"><h4>Insurance</h4>${table(['Provider','Member / Policy','Group','Status'],rows(ins,[x=>x.provider,x=>x.memberId||x.memberID,x=>x.group,x=>x.status]))}<button class="btn primary" data-profile-add-insurance="${e(p.id)}">＋ Add / Update Insurance</button></div>
        <div class="patient-profile-card"><h4>Billing</h4><p><strong>Total billed:</strong> ₱${total.toLocaleString()} &nbsp; <strong>Paid:</strong> ₱${paid.toLocaleString()}</p>${table(['Claim / Invoice','Amount','Status'],rows(bills,[x=>x.claim,x=>`₱${Number(x.amount||0).toLocaleString()}`,x=>x.status]))}<button class="btn primary" data-profile-add-billing="${e(p.id)}">＋ Add Billing</button></div>
      </div>
      <div class="patient-profile-card"><h4>Appointments</h4>${table(['Date','Time','Type','Provider','Status'],rows(apps,[x=>x.date,x=>x.time,x=>x.type,x=>x.provider,x=>x.status]))}<button class="btn primary" data-profile-add-appointment="${e(p.id)}">＋ Add Appointment</button></div>
      <div class="patient-profile-card patient-profile-wide"><h4>Documents & Files</h4><div class="profile-drop">Add PDF, document, image, or other file<input id="fixedProfileFiles" type="file" multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,image/*"></div>${docs.map(d=>`<div class="profile-doc"><div><b>${e(d.name)}</b><br><small>${e(d.type||'File')} · ${e(d.date||'')}</small></div><div><button class="btn" data-fixed-view-doc="${e(d.id)}">View</button><button class="btn danger" data-fixed-delete-doc="${e(d.id)}">Delete</button></div></div>`).join('')||'<div class="profile-empty">No files attached to this patient.</div>'}</div>
      <div class="patient-profile-grid"><div class="patient-profile-card"><h4>Tasks</h4>${table(['Task','Priority','Status'],rows(tasks,[x=>x.title,x=>x.priority,x=>x.status]))}</div><div class="patient-profile-card"><h4>Follow-ups</h4>${table(['Due','Reason','Status'],rows(follows,[x=>x.due,x=>x.reason,x=>x.status]))}</div></div>
      <div class="patient-profile-card"><h4>Notes</h4>${notes.map(n=>`<p><strong>${e(n.date||'')}</strong> · ${e(n.type||'shared')}<br>${e(n.text)}</p>`).join('')||'<div class="profile-empty">No notes linked to this patient.</div>'}</div>
    </div>`;
    modal(`Patient Record — ${e(p.name)}`,body,()=>{},'Close');
    const m=document.querySelector('#modalRoot .modal');if(m)m.style.width='min(1050px,96vw)';
    const input=document.getElementById('fixedProfileFiles');if(input)input.onchange=()=>{Array.from(input.files||[]).forEach(file=>{const r=new FileReader();r.onload=()=>{db.documents=db.documents||[];db.documents.push({id:'DOC-'+Date.now()+'-'+Math.random().toString(36).slice(2,7),name:file.name,type:file.type||'File',patient:p.name,date:new Date().toISOString().slice(0,10),owner:'VA Joy',size:file.size,dataUrl:r.result});save();toast(file.name+' attached');profile(p.id)};r.readAsDataURL(file)})};
  }
  document.addEventListener('click',function(ev){
    const btn=ev.target.closest('.patient-name-link[data-patient]');
    if(!btn)return;
    ev.preventDefault();ev.stopImmediatePropagation();
    profile(btn.dataset.patient);
  },true);
  window.openPatientProfile=profile;
})();
