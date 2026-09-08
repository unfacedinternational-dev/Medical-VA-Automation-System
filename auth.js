const AUTH_KEY='mva-authenticated-role';
const SHARED_PASSWORD='2026';
const appEl=document.getElementById('app');
const modalEl=document.getElementById('modalRoot');

function showLanding(){
  appEl.classList.add('auth-hidden');
  document.body.classList.add('auth-page');
  appEl.insertAdjacentHTML('beforebegin',`<main id="authLanding" class="auth-landing">
    <div class="auth-collage" aria-hidden="true">
      <div class="auth-photo photo-equipment"></div><div class="auth-photo photo-doctor"></div><div class="auth-photo photo-mask"></div><div class="auth-photo photo-team"></div>
    </div>
    <section class="auth-hero">
      <div class="auth-brand"><div class="auth-mark">M</div><div><b>MEDICAL VA</b><span>AUTOMATION SYSTEM</span></div></div>
      <div class="auth-badge">PRIVATE INTERNAL WORKSPACE</div>
      <h1>Welcome to the<br><strong>Medical VA Automation System</strong></h1>
      <p class="auth-lead">A practical workflow system designed to organize medical virtual assistant operations, reduce repetitive administrative work, and keep important tasks moving from appointment to completion.</p>
      <div class="auth-personal"><span>AUTHORIZED USERS</span><strong>VA Joy N. &amp; Employer</strong><p>This is a private internal workspace intended only for Joy and her employer.</p></div>
      <div class="auth-actions"><button class="auth-primary" id="howItWorks">How this system works <span>→</span></button></div>
      <div class="auth-access">
        <div class="access-card"><div class="access-icon">VA</div><div><h2>VA Joy</h2><p>Enter the shared authorized password to access the workspace.</p></div><button class="auth-secondary" id="joyLogin">Enter as VA</button></div>
        <div class="access-card"><div class="access-icon">EM</div><div><h2>Employer</h2><p>Enter the same shared authorized password to access the workspace.</p></div><button class="auth-secondary" id="employerLogin">Enter as Employer</button></div>
      </div>
      <p class="auth-note">This workspace uses one shared password for the two authorized users. For production use with real patient information, server-side authentication and secure healthcare-compliant storage should be enabled.</p>
    </section>
  </main>`);
  document.getElementById('howItWorks').onclick=showHow;
  document.getElementById('joyLogin').onclick=showSharedLogin;
  document.getElementById('employerLogin').onclick=showSharedLogin;
}

function closeAuth(){modalEl.innerHTML=''}
function showHow(){
  modalEl.innerHTML=`<div class="modal-backdrop auth-modal-backdrop"><div class="modal auth-info-modal"><div class="modal-head"><h3>How the Medical VA Automation System works</h3><button class="icon-btn" data-auth-close>×</button></div><div class="modal-body auth-info">
    <p>This system connects the routine administrative steps of a medical VA workflow into one organized workspace.</p>
    <div class="info-block"><b>1. Patients</b><span>Create and maintain patient records so appointments, tasks, billing, insurance, and documents can stay connected.</span></div>
    <div class="info-block"><b>2. Appointments</b><span>Schedule visits and track their status. Completing an appointment can trigger the next operational steps.</span></div>
    <div class="info-block"><b>3. Automated workflow</b><span>Appointment completed → billing record → insurance check → task creation → staff notification → claim/payment tracking → reporting.</span></div>
    <div class="info-block"><b>4. Tasks & follow-ups</b><span>Turn required actions into visible work items so important follow-ups are not dependent on memory or scattered notes.</span></div>
    <div class="info-block"><b>5. Billing & insurance</b><span>Track claims, payment status, eligibility checks, and related follow-up work from one place.</span></div>
    <div class="info-block"><b>6. Documents & files</b><span>Organize files alongside the patient and operational records that need them.</span></div>
    <div class="info-columns"><div><h4>How it helps the VA</h4><ul><li>Less repetitive manual tracking</li><li>Clear priorities and work queues</li><li>Fewer missed follow-ups</li><li>Centralized operational records</li><li>Clear visibility of completed work</li></ul></div><div><h4>How it helps the employer</h4><ul><li>Visibility into workflow status</li><li>Consistent administrative processes</li><li>Easier monitoring of claims and tasks</li><li>Centralized operational information</li><li>Better reporting and accountability</li></ul></div></div>
    <div class="info-note"><b>Security:</b> The shared-password login is suitable for the current private workspace prototype. Do not enter real patient/PHI data until secure server-side authentication, access control, encrypted storage, and an appropriate healthcare-compliant backend are implemented.</div>
  </div><div class="modal-foot"><button class="btn primary" data-auth-close>Got it</button></div></div></div>`;
  modalEl.querySelectorAll('[data-auth-close]').forEach(x=>x.onclick=closeAuth);
}

function showSharedLogin(){
  modalEl.innerHTML=`<div class="modal-backdrop auth-modal-backdrop"><div class="modal"><div class="modal-head"><h3>Authorized access</h3><button class="icon-btn" data-auth-close>×</button></div><div class="modal-body"><div class="auth-form"><label class="field"><span>Shared password</span><input id="authPassword" type="password" autocomplete="current-password" placeholder="Enter password"></label><p class="auth-error"></p></div></div><div class="modal-foot"><button class="btn" data-auth-close>Cancel</button><button class="btn primary" id="submitShared">Enter workspace</button></div></div></div>`;
  modalEl.querySelectorAll('[data-auth-close]').forEach(x=>x.onclick=closeAuth);
  document.getElementById('submitShared').onclick=()=>{
    const password=document.getElementById('authPassword').value;
    if(password===SHARED_PASSWORD) authenticate('authorized');
    else document.querySelector('.auth-error').textContent='Access denied. Incorrect password.';
  };
  document.getElementById('authPassword').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('submitShared').click()});
}
function authenticate(role){sessionStorage.setItem(AUTH_KEY,role);document.getElementById('authLanding')?.remove();document.body.classList.remove('auth-page');appEl.classList.remove('auth-hidden');closeAuth()}
if(!sessionStorage.getItem(AUTH_KEY)) showLanding(); else appEl.classList.remove('auth-hidden');
