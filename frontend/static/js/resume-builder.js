/* =========================================================
   resume-builder.js  –  Full multi-step form + preview logic
   ========================================================= */

// ── State ─────────────────────────────────────────────────
let currentStep  = 1;
let mode         = 'manual';   // 'manual' | 'upload'
let uploadedFile = null;
let currentResumeData = null;  // ResumeContent from last generation
let currentTemplate   = 'professional';

const techSkills = [];
const softSkills = [];
let expBlocks  = 0;
let eduBlocks  = 0;
let projBlocks = 0;

// ── Mode Toggle ───────────────────────────────────────────
function setMode(m) {
  mode = m;
  document.getElementById('manualForm').classList.toggle('hidden', m === 'upload');
  document.getElementById('uploadPanel').classList.toggle('hidden', m === 'manual');
  document.getElementById('btnManual').classList.toggle('border-indigo-600', m === 'manual');
  document.getElementById('btnManual').classList.toggle('text-indigo-600',   m === 'manual');
  document.getElementById('btnManual').classList.toggle('border-gray-300',   m !== 'manual');
  document.getElementById('btnManual').classList.toggle('text-gray-600',     m !== 'manual');
  document.getElementById('btnUpload').classList.toggle('border-indigo-600', m === 'upload');
  document.getElementById('btnUpload').classList.toggle('text-indigo-600',   m === 'upload');
  document.getElementById('btnUpload').classList.toggle('border-gray-300',   m !== 'upload');
  document.getElementById('btnUpload').classList.toggle('text-gray-600',     m !== 'upload');
}

// ── Upload handlers ───────────────────────────────────────
function handleUpload(input) {
  if (input.files[0]) {
    uploadedFile = input.files[0];
    document.getElementById('uploadLabel').textContent = '✅ ' + uploadedFile.name;
  }
}

async function generateFromUpload() {
  const name = document.getElementById('uFullName').value.trim();
  const phone = document.getElementById('uPhone').value.trim();
  const email = document.getElementById('uEmail').value.trim();
  const role  = document.getElementById('uTargetRole').value.trim();

  if (!uploadedFile) return toast('Please upload a resume file', 'error');
  if (!name)  return toast('Please enter your name', 'error');
  if (!phone) return toast('Please enter your phone number', 'error');
  if (!email) return toast('Please enter your email', 'error');
  if (!role)  return toast('Please enter the target job role', 'error');

  const tpl   = document.getElementById('uTemplate').value;
  const jd    = document.getElementById('uJobDesc').value.trim();
  currentTemplate = tpl;

  setUploadBtnLoading(true);

  const fd = new FormData();
  fd.append('full_name',  name);
  fd.append('phone',      phone);
  fd.append('email',      email);
  fd.append('target_role', role);
  fd.append('template',   tpl);
  if (jd) fd.append('job_description', jd);
  fd.append('existing_resume', uploadedFile);

  await callGenerateAPI(fd);
  setUploadBtnLoading(false);
}

function setUploadBtnLoading(on) {
  document.getElementById('uploadBtnTxt').classList.toggle('hidden', on);
  document.getElementById('uploadSpinner').classList.toggle('hidden', !on);
  document.getElementById('uploadGenBtn').disabled = on;
}

// ── Step Navigation ───────────────────────────────────────
function nextStep(from) {
  if (from === 1 && !validateStep1()) return;
  if (from === 2 && expBlocks === 0)   addExperienceBlock();  // Auto-add one block
  if (from === 3 && eduBlocks  === 0)  addEducationBlock();
  if (from === 4 && projBlocks === 0)  addProjectBlock();

  document.getElementById('step' + from).classList.remove('active');
  document.getElementById('step' + (from + 1)).classList.add('active');

  markStepDone(from);
  markStepActive(from + 1);
  currentStep = from + 1;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevStep(current) {
  document.getElementById('step' + current).classList.remove('active');
  document.getElementById('step' + (current - 1)).classList.add('active');
  markStepActive(current - 1);
  currentStep = current - 1;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function markStepDone(n) {
  const d = document.getElementById('sd_' + n);
  d.className = 'step-dot done';
  d.textContent = '✓';
  if (document.getElementById('sl_' + n))
    document.getElementById('sl_' + n).className = 'text-sm font-medium text-indigo-600';
}

function markStepActive(n) {
  const d = document.getElementById('sd_' + n);
  d.className = 'step-dot active';
  if (document.getElementById('sl_' + n))
    document.getElementById('sl_' + n).className = 'text-sm font-medium text-indigo-600';
}

function validateStep1() {
  const name  = document.getElementById('s1_name').value.trim();
  const role  = document.getElementById('s1_role').value.trim();
  const phone = document.getElementById('s1_phone').value.trim();
  const email = document.getElementById('s1_email').value.trim();
  if (!name)  { toast('Please enter your full name', 'error');  return false; }
  if (!role)  { toast('Please enter the target job role', 'error'); return false; }
  if (!phone) { toast('Please enter your phone number', 'error'); return false; }
  if (!email || !email.includes('@')) { toast('Please enter a valid email', 'error'); return false; }
  return true;
}

// ── Skill chips ───────────────────────────────────────────
function addSkill(e, type) {
  if (e.key !== 'Enter' && e.key !== ',') return;
  e.preventDefault();
  const input = document.getElementById(type + 'SkillInput');
  const val   = input.value.replace(',', '').trim();
  if (!val) return;
  const arr  = type === 'tech' ? techSkills : softSkills;
  const cont = document.getElementById(type + 'SkillsContainer');
  if (arr.includes(val)) { input.value = ''; return; }
  arr.push(val);

  const chip = document.createElement('span');
  chip.className = 'skill-chip';
  chip.innerHTML = `${val}<button onclick="removeSkill(this,'${type}','${val}')" title="Remove">×</button>`;
  cont.appendChild(chip);
  input.value = '';
}

function removeSkill(btn, type, val) {
  const arr  = type === 'tech' ? techSkills : softSkills;
  const idx  = arr.indexOf(val);
  if (idx > -1) arr.splice(idx, 1);
  btn.closest('.skill-chip').remove();
}

// ── Dynamic blocks ────────────────────────────────────────
function addExperienceBlock() {
  expBlocks++;
  const id = expBlocks;
  const html = `
  <div class="border border-gray-200 rounded-xl p-5 relative" id="expBlock_${id}">
    <button onclick="removeBlock('expBlock_${id}')" class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-lg">✕</button>
    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Job Title *</label>
        <input type="text" id="exp_${id}_title" placeholder="e.g. Software Engineer"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Company Name *</label>
        <input type="text" id="exp_${id}_company" placeholder="e.g. Infosys, Google, Startup Inc."
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Duration *</label>
        <input type="text" id="exp_${id}_duration" placeholder="e.g. Jun 2022 – Present"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Location</label>
        <input type="text" id="exp_${id}_location" placeholder="e.g. Bangalore, India / Remote"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-xs font-semibold text-gray-600 mb-1">
          Key Responsibilities / Achievements *
          <span class="text-gray-400 font-normal">(one per line – AI will polish the wording)</span>
        </label>
        <textarea id="exp_${id}_resp" rows="4"
          placeholder="Built REST APIs for 50K+ daily users&#10;Led a team of 4 to migrate legacy codebase&#10;Reduced deployment time by 40% via CI/CD"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400"></textarea>
      </div>
    </div>
  </div>`;
  document.getElementById('experienceBlocks').insertAdjacentHTML('beforeend', html);
}

function addEducationBlock() {
  eduBlocks++;
  const id = eduBlocks;
  const html = `
  <div class="border border-gray-200 rounded-xl p-5 relative" id="eduBlock_${id}">
    <button onclick="removeBlock('eduBlock_${id}')" class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-lg">✕</button>
    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Degree / Course *</label>
        <input type="text" id="edu_${id}_degree" placeholder="e.g. B.Tech in Computer Science"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Institution Name *</label>
        <input type="text" id="edu_${id}_inst" placeholder="e.g. IIT Madras, VIT"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Year of Completion</label>
        <input type="text" id="edu_${id}_year" placeholder="e.g. 2024"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">GPA / CGPA / Percentage</label>
        <input type="text" id="edu_${id}_gpa" placeholder="e.g. 8.5 / 10 or 85%"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
    </div>
  </div>`;
  document.getElementById('educationBlocks').insertAdjacentHTML('beforeend', html);
}

function addProjectBlock() {
  projBlocks++;
  const id = projBlocks;
  const html = `
  <div class="border border-gray-200 rounded-xl p-5 relative" id="projBlock_${id}">
    <button onclick="removeBlock('projBlock_${id}')" class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-lg">✕</button>
    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Project Name *</label>
        <input type="text" id="proj_${id}_name" placeholder="e.g. Smart Expense Tracker"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-gray-600 mb-1">Technologies Used</label>
        <input type="text" id="proj_${id}_tech" placeholder="e.g. React, Node.js, MongoDB"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-xs font-semibold text-gray-600 mb-1">Description</label>
        <textarea id="proj_${id}_desc" rows="2"
          placeholder="What the project does and what problem it solves…"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400"></textarea>
      </div>
      <div class="md:col-span-2">
        <label class="block text-xs font-semibold text-gray-600 mb-1">Outcome / Impact</label>
        <input type="text" id="proj_${id}_impact" placeholder="e.g. Deployed to 200+ users; reduced budget waste by 30%"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400" />
      </div>
    </div>
  </div>`;
  document.getElementById('projectBlocks').insertAdjacentHTML('beforeend', html);
}

function removeBlock(id) {
  document.getElementById(id)?.remove();
}

// ── Collect all form data ─────────────────────────────────
function collectFormData() {
  const data = {
    full_name:   document.getElementById('s1_name').value.trim(),
    phone:       document.getElementById('s1_phone').value.trim(),
    email:       document.getElementById('s1_email').value.trim(),
    target_role: document.getElementById('s1_role').value.trim(),
    linkedin:    document.getElementById('s1_linkedin').value.trim(),
    github:      document.getElementById('s1_github').value.trim(),
    summary:     document.getElementById('s1_summary').value.trim(),
    job_description: document.getElementById('s1_jd').value.trim(),
    template:    document.getElementById('s1_template').value,

    tech_skills: [...techSkills],
    soft_skills: [...softSkills],

    experience:  [],
    education:   [],
    projects:    [],

    certifications: (document.getElementById('s5_certs').value || '')
      .split('\n').map(s => s.trim()).filter(Boolean),
    achievements: (document.getElementById('s5_achievements').value || '')
      .split('\n').map(s => s.trim()).filter(Boolean),
  };

  // Experience
  for (let i = 1; i <= expBlocks; i++) {
    const el = document.getElementById('expBlock_' + i);
    if (!el) continue;
    const title = (document.getElementById(`exp_${i}_title`)?.value || '').trim();
    const company = (document.getElementById(`exp_${i}_company`)?.value || '').trim();
    if (!title && !company) continue;
    data.experience.push({
      title:    title,
      company:  company,
      duration: (document.getElementById(`exp_${i}_duration`)?.value || '').trim(),
      location: (document.getElementById(`exp_${i}_location`)?.value || '').trim(),
      responsibilities: (document.getElementById(`exp_${i}_resp`)?.value || '')
        .split('\n').map(s => s.trim()).filter(Boolean),
    });
  }

  // Education
  for (let i = 1; i <= eduBlocks; i++) {
    const el = document.getElementById('eduBlock_' + i);
    if (!el) continue;
    const degree = (document.getElementById(`edu_${i}_degree`)?.value || '').trim();
    const inst   = (document.getElementById(`edu_${i}_inst`)?.value || '').trim();
    if (!degree && !inst) continue;
    data.education.push({
      degree:      degree,
      institution: inst,
      year:        (document.getElementById(`edu_${i}_year`)?.value || '').trim(),
      gpa:         (document.getElementById(`edu_${i}_gpa`)?.value  || '').trim(),
    });
  }

  // Projects
  for (let i = 1; i <= projBlocks; i++) {
    const el = document.getElementById('projBlock_' + i);
    if (!el) continue;
    const name = (document.getElementById(`proj_${i}_name`)?.value || '').trim();
    if (!name) continue;
    data.projects.push({
      name:         name,
      technologies: (document.getElementById(`proj_${i}_tech`)?.value   || '').trim(),
      description:  (document.getElementById(`proj_${i}_desc`)?.value   || '').trim(),
      impact:       (document.getElementById(`proj_${i}_impact`)?.value || '').trim(),
    });
  }

  return data;
}

// ── Generate resume (manual) ──────────────────────────────
async function generateResume() {
  const data = collectFormData();

  // Build FormData to send to API
  const fd = new FormData();
  fd.append('full_name',      data.full_name);
  fd.append('phone',          data.phone);
  fd.append('email',          data.email);
  fd.append('target_role',    data.target_role);
  fd.append('template',       data.template);
  if (data.job_description)  fd.append('job_description', data.job_description);

  // Pass all real user data as JSON so backend can use it
  fd.append('user_data', JSON.stringify(data));

  currentTemplate = data.template;

  setGenLoading(true);
  await callGenerateAPI(fd);
  setGenLoading(false);
}

function setGenLoading(on) {
  document.getElementById('genBtnTxt').classList.toggle('hidden', on);
  document.getElementById('genSpinner').classList.toggle('hidden', !on);
  document.getElementById('genBtn').disabled = on;
}

// ── Common API call ───────────────────────────────────────
async function callGenerateAPI(fd) {
  try {
    const resp = await fetch('/api/generate-resume', { method: 'POST', body: fd });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Server error' }));
      throw new Error(err.detail || 'Failed to generate resume');
    }
    const result = await resp.json();
    currentResumeData = result.resume_content;
    renderResume(result.resume_content);
    renderATS(result.ats_score);
    document.getElementById('resultPanel').classList.remove('hidden');
    document.getElementById('manualForm').classList.add('hidden');
    document.getElementById('uploadPanel').classList.add('hidden');
    document.querySelector('.flex.items-center.justify-center.gap-2.mb-8')?.classList.add('hidden');
    document.getElementById('resultPanel').scrollIntoView({ behavior: 'smooth' });
    toast('Resume generated successfully!', 'success');
  } catch (e) {
    toast(e.message || 'Error generating resume', 'error');
    console.error(e);
  }
}

// ── Font Picker ───────────────────────────────────────────
function setFont(fontName) {
  document.getElementById('resumePreview').style.fontFamily = fontName + ', sans-serif';
  document.querySelectorAll('.font-btn').forEach(b => {
    b.classList.toggle('active', b.textContent.trim() === fontName);
  });
}

// ── Render resume preview ─────────────────────────────────
function renderResume(rc) {
  const el = document.getElementById('resumePreview');
  let h = '';

  // Header
  h += `<div class="r-name" contenteditable="true">${esc(rc.full_name)}</div>`;
  const cp = [];
  if (rc.contact?.phone)    cp.push(esc(rc.contact.phone));
  if (rc.contact?.email)    cp.push(esc(rc.contact.email));
  if (rc.contact?.linkedin) cp.push(esc(rc.contact.linkedin));
  if (rc.contact?.github)   cp.push(esc(rc.contact.github));
  h += `<div class="r-contact" contenteditable="true">${cp.join(' &nbsp;|&nbsp; ')}</div>`;

  // Summary
  if (rc.summary) {
    h += sec('PROFESSIONAL SUMMARY');
    h += `<p class="text-sm leading-relaxed text-gray-700" style="font-size:12px" contenteditable="true">${esc(rc.summary)}</p>`;
  }

  // Skills
  if (rc.skills?.length) {
    h += sec('SKILLS');
    h += `<p class="r-skills" contenteditable="true">${rc.skills.map(esc).join(' &bull; ')}</p>`;
  }

  // Experience
  if (rc.experience?.length) {
    h += sec('PROFESSIONAL EXPERIENCE');
    rc.experience.forEach(exp => {
      h += `<div class="r-job-title" contenteditable="true">${esc(exp.title)}</div>`;
      const sub = [exp.company, exp.duration, exp.location].filter(Boolean).map(esc).join(' &nbsp;|&nbsp; ');
      h += `<div class="r-sub" contenteditable="true">${sub}</div>`;
      (exp.responsibilities || []).forEach(r => {
        h += `<div class="r-bullet" contenteditable="true">${esc(r)}</div>`;
      });
      h += '<div style="margin-bottom:8px"></div>';
    });
  }

  // Education
  if (rc.education?.length) {
    h += sec('EDUCATION');
    rc.education.forEach(edu => {
      h += `<div class="r-job-title" contenteditable="true">${esc(edu.degree)}</div>`;
      const sub = [edu.institution, edu.year, edu.gpa ? 'GPA: ' + edu.gpa : ''].filter(Boolean).map(esc).join(' &nbsp;|&nbsp; ');
      h += `<div class="r-sub" contenteditable="true">${sub}</div>`;
    });
  }

  // Projects
  if (rc.projects?.length) {
    h += sec('PROJECTS');
    rc.projects.forEach(p => {
      h += `<div class="r-job-title" contenteditable="true">${esc(p.name)}</div>`;
      if (p.technologies) h += `<div class="r-sub" contenteditable="true">Technologies: ${esc(p.technologies)}</div>`;
      if (p.description)  h += `<div class="r-bullet" contenteditable="true">${esc(p.description)}</div>`;
      if (p.impact)       h += `<div class="r-bullet" contenteditable="true">${esc(p.impact)}</div>`;
      h += '<div style="margin-bottom:8px"></div>';
    });
  }

  // Certifications — always render if array has any items
  const certs = rc.certifications || [];
  if (certs.length > 0) {
    h += sec('CERTIFICATIONS');
    certs.forEach(c => { if (c && c.trim()) h += `<div class="r-bullet" contenteditable="true">${esc(c)}</div>`; });
  }

  // Achievements — always render if array has any items
  const achs = rc.achievements || [];
  if (achs.length > 0) {
    h += sec('ACHIEVEMENTS');
    achs.forEach(a => { if (a && a.trim()) h += `<div class="r-bullet" contenteditable="true">${esc(a)}</div>`; });
  }

  el.innerHTML = h;
}

function sec(t) {
  return `<div class="r-section-title">${t}</div>`;
}

function esc(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Render ATS banner ─────────────────────────────────────
function renderATS(ats) {
  document.getElementById('atsNum').textContent   = ats.overall_score;
  document.getElementById('b_skill').textContent  = ats.skill_match + '/100';
  document.getElementById('b_kw').textContent     = ats.keyword_relevance + '/100';
  document.getElementById('b_role').textContent   = ats.role_alignment + '/100';
  document.getElementById('b_fmt').textContent    = ats.formatting_score + '/100';
  document.getElementById('b_sec').textContent    = ats.section_completeness + '/100';

  const ul = document.getElementById('atsSuggestions');
  ul.innerHTML = '';
  (ats.suggestions || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    ul.appendChild(li);
  });

  const score = ats.overall_score;
  const banner = document.getElementById('atsBanner');
  banner.className = 'rounded-xl p-5 mb-6 border flex flex-wrap gap-6 items-center ';
  if (score >= 85) banner.className += 'bg-green-50 border-green-300';
  else if (score >= 70) banner.className += 'bg-blue-50 border-blue-300';
  else if (score >= 55) banner.className += 'bg-yellow-50 border-yellow-300';
  else banner.className += 'bg-red-50 border-red-300';
}

// ── Downloads ─────────────────────────────────────────────
async function downloadPDF() {
  if (!currentResumeData) return toast('Generate a resume first', 'error');
  await downloadFile('/api/download-pdf', currentTemplate, 'pdf');
}
async function downloadDOCX() {
  if (!currentResumeData) return toast('Generate a resume first', 'error');
  await downloadFile('/api/download-docx', currentTemplate, 'docx');
}

async function downloadFile(url, tpl, ext) {
  try {
    const fd = new FormData();
    fd.append('resume_data', JSON.stringify(currentResumeData));
    fd.append('template', tpl);
    const resp = await fetch(url, { method: 'POST', body: fd });
    if (!resp.ok) throw new Error('Download failed');
    const blob = await resp.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `resume_${(currentResumeData.full_name || 'resume').replace(/\s+/g,'_')}.${ext}`;
    document.body.appendChild(a); a.click();
    URL.revokeObjectURL(a.href);
    document.body.removeChild(a);
    toast(`${ext.toUpperCase()} downloaded!`, 'success');
  } catch (e) {
    toast('Download failed: ' + e.message, 'error');
  }
}

// ── Toast ─────────────────────────────────────────────────
function toast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `fixed top-4 right-4 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-[100] ${type === 'success' ? 'bg-green-500' : 'bg-red-600'}`;
  t.classList.remove('hidden');
  setTimeout(() => t.classList.add('hidden'), 3500);
}

// ── Init: add first blocks automatically ──────────────────
document.addEventListener('DOMContentLoaded', () => {
  setMode('manual');
  addExperienceBlock();
  addEducationBlock();
  addProjectBlock();
});