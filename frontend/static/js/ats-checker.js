/* ats-checker.js */
let uploadedFile = null;

function handleFileSelect(input) {
  if (input.files[0]) {
    uploadedFile = input.files[0];
    document.getElementById('fileLabel').textContent = '✅ ' + uploadedFile.name;
    document.getElementById('dropZone').style.borderColor = '#2E7D52';
  }
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('drag');
  const f = e.dataTransfer.files[0];
  if (f && (f.name.endsWith('.pdf') || f.name.endsWith('.docx'))) {
    uploadedFile = f;
    document.getElementById('fileLabel').textContent = '✅ ' + f.name;
  } else {
    showToast('Please upload a PDF or DOCX file', 'error');
  }
}

async function checkATS() {
  if (!uploadedFile)   return showToast('Please upload a resume file', 'error');
  const role = document.getElementById('targetRole').value.trim();
  if (!role) return showToast('Please enter the target job role', 'error');

  setLoading(true);
  try {
    const fd = new FormData();
    fd.append('resume_file', uploadedFile);
    fd.append('target_role', role);
    const jd = document.getElementById('jobDescription').value.trim();
    if (jd) fd.append('job_description', jd);

    const resp = await fetch('/api/check-ats-score', { method:'POST', body:fd });
    if (!resp.ok) { const e = await resp.json(); throw new Error(e.detail || 'Error'); }
    const data = await resp.json();
    renderResults(data);
  } catch(e) {
    showToast(e.message, 'error');
  }
  setLoading(false);
}

function renderResults(d) {
  document.getElementById('placeholder').classList.add('hidden');
  document.getElementById('results').classList.remove('hidden');

  const score = d.overall_score;
  // Ring animation
  const circ = 2 * Math.PI * 68;
  const offset = circ - (score / 100) * circ;
  const arc = document.getElementById('ringArc');
  setTimeout(() => { arc.style.strokeDashoffset = offset; }, 100);

  // Color
  let color, label, msg;
  if      (score >= 85) { color='#059669'; label='🟢 Excellent – FAANG Ready';      msg='Your resume is highly optimized. It should pass most ATS systems including FAANG-level filters.'; }
  else if (score >= 70) { color='#2563EB'; label='🔵 Good – Competitive';            msg='Well optimized. A few targeted improvements will push you into the top tier.'; }
  else if (score >= 55) { color='#D97706'; label='🟡 Fair – Needs Work';             msg='Meets basic requirements but will be filtered out by FAANG ATS. Follow the suggestions below.'; }
  else                  { color='#DC2626'; label='🔴 Poor – High Risk of Rejection'; msg='Significant optimization needed before applying to competitive roles.'; }

  arc.setAttribute('stroke', color);
  document.getElementById('scoreNum').textContent = score;
  document.getElementById('scoreNum').style.color = color;
  document.getElementById('scoreLabel').textContent = label;
  document.getElementById('scoreLabel').style.color = color;
  document.getElementById('scoreMsg').textContent = msg;

  // Bars
  const components = [
    { label:'Skill Match',          val:d.skill_match,        color:'#6366F1' },
    { label:'Keyword Density',      val:d.keyword_relevance,  color:'#2563EB' },
    { label:'Role Alignment',       val:d.role_alignment,     color:'#2E7D52' },
    { label:'Formatting Score',     val:d.formatting_score,   color:'#10B981' },
    { label:'Section Completeness', val:d.section_completeness,color:'#F59E0B'},
    { label:'Action Verb Usage',    val:d.action_verb_score || d.role_alignment, color:'#EC4899' },
    { label:'Quantified Impact',    val:d.quantified_score   || Math.min(d.role_alignment+5,100), color:'#8B5CF6' },
    { label:'FAANG Compliance',     val:d.faang_compliance   || Math.round((score+d.formatting_score)/2), color:'#EF4444' },
  ];
  const barsEl = document.getElementById('bars');
  barsEl.innerHTML = '';
  components.forEach(c => {
    barsEl.innerHTML += `
      <div>
        <div class="flex justify-between text-xs mb-1">
          <span class="font-medium text-gray-700">${c.label}</span>
          <span class="font-bold" style="color:${c.color}">${c.val}/100</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:${c.val}%;background:${c.color}"></div></div>
      </div>`;
  });

  // Missing keywords
  if (d.missing_keywords?.length) {
    document.getElementById('kwSection').classList.remove('hidden');
    document.getElementById('kwChips').innerHTML = d.missing_keywords.map(k => `<span class="kw-chip">${k}</span>`).join('');
  }

  // AI suggestions
  const sugEl = document.getElementById('suggestions');
  sugEl.innerHTML = '';
  (d.suggestions || []).forEach(s => {
    sugEl.innerHTML += `<div class="sug-card text-sm text-gray-800">${s}</div>`;
  });
}

function setLoading(on) {
  document.getElementById('btnTxt').classList.toggle('hidden', on);
  document.getElementById('btnSpin').classList.toggle('hidden', !on);
  document.getElementById('checkBtn').disabled = on;
}

function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `fixed top-4 right-4 px-5 py-3 rounded-xl shadow-lg text-white text-sm font-medium z-[100] ${type==='success'?'bg-green-600':'bg-red-600'}`;
  t.classList.remove('hidden');
  setTimeout(() => t.classList.add('hidden'), 3500);
}