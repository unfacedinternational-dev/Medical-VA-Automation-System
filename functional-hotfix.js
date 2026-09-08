(()=>{
const K='mva-production-workspace-v1';
const old='mva-demo-v1';
const sample=/P-100[1-5]|Maria Santos|Daniel Reyes|Sophia Cruz|Michael Garcia|Anna Rodriguez/;
const clean=()=>({patients:[],appointments:[],tasks:[],followups:[],billing:[],insurance:[],documents:[],messages:[],activity:[]});
let d=window.db;
if(!d||sample.test(JSON.stringify(d))){d=clean();window.db=d;localStorage.setItem(K,JSON.stringify(d));localStorage.removeItem(old);}
window.db=d;
const save=window.save||(()=>localStorage.setItem(K,JSON.stringify(window.db)));
window.save=save;
const go=v=>{window.view=v;window.render();document.querySelectorAll('.nav-item').forEach(x=>x.classList.toggle('active',x.dataset.view===v));};
const action=(el)=>{const a=el.dataset.action;if(!a)return; if(a.startsWith('view:'))go(a.slice(5)); if(a==='notify'){go('messages');} if(a==='clear'){if(confirm('Clear the entire workspace?')){window.db=clean();save();render();toast('Workspace cleared')}}};
document.addEventListener('click',e=>{const n=e.target.closest('[data-action]');if(n){e.preventDefault();action(n);return}const s=e.target.closest('.stat');if(s){const i=[...document.querySelectorAll('.stat')].indexOf(s);go(['patients','appointments','tasks','billing'][i]);}});
window.addEventListener('load',()=>{setTimeout(()=>{document.querySelectorAll('.stat').forEach(x=>{x.style.cursor='pointer';x.title='Open this section'});const note=document.querySelector('.demo-note b');if(note)note.textContent='Workspace ready';const small=document.querySelector('.demo-note small');if(small)small.textContent='Add your own records';const r=document.querySelector('#resetDemo');if(r){r.textContent='↺ Clear workspace';r.onclick=()=>{if(confirm('Clear the entire workspace?')){window.db=clean();save();window.render();toast('Workspace cleared')}}}window.render()},0)});
})();