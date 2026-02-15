// Resume Builder JavaScript
let currentResumeData = null;

document.getElementById('resumeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await generateResume();
});

async function generateResume() {
    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    // Show loading state
    btn.disabled = true;
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('full_name', document.getElementById('fullName').value);
        formData.append('phone', document.getElementById('phone').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('target_role', document.getElementById('targetRole').value);
        formData.append('template', document.getElementById('template').value);
        
        const jobDesc = document.getElementById('jobDescription').value;
        if (jobDesc) {
            formData.append('job_description', jobDesc);
        }
        
        const fileInput = document.getElementById('existingResume');
        if (fileInput.files[0]) {
            formData.append('existing_resume', fileInput.files[0]);
        }
        
        // Call API
        const response = await fetch('/api/generate-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate resume');
        }
        
        const data = await response.json();
        
        // Store resume data
        currentResumeData = data.resume_content;
        
        // Display resume
        displayResume(data.resume_content);
        
        // Display ATS score
        displayATSScore(data.ats_score);
        
        // Show success message
        showNotification('Resume generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to generate resume', 'error');
    } finally {
        // Reset button state
        btn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
}

function displayResume(resumeContent) {
    const preview = document.getElementById('resumePreview');
    
    let html = '';
    
    // Header
    html += `
        <div class="text-center mb-6">
            <h1 class="text-3xl font-bold text-gray-900 mb-2 editable" contenteditable="true" data-field="full_name">${resumeContent.full_name}</h1>
            <div class="text-gray-600 editable" contenteditable="true">
                ${resumeContent.contact.phone} | ${resumeContent.contact.email}
                ${resumeContent.contact.linkedin ? ' | ' + resumeContent.contact.linkedin : ''}
            </div>
        </div>
    `;
    
    // Professional Summary
    if (resumeContent.summary) {
        html += `
            <div class="mb-6">
                <div class="section-header">PROFESSIONAL SUMMARY</div>
                <p class="text-gray-700 editable" contenteditable="true" data-field="summary">${resumeContent.summary}</p>
            </div>
        `;
    }
    
    // Skills
    if (resumeContent.skills && resumeContent.skills.length > 0) {
        html += `
            <div class="mb-6">
                <div class="section-header">SKILLS</div>
                <div class="text-gray-700 editable" contenteditable="true" data-field="skills">${resumeContent.skills.join(' • ')}</div>
            </div>
        `;
    }
    
    // Experience
    if (resumeContent.experience && resumeContent.experience.length > 0) {
        html += `<div class="mb-6"><div class="section-header">PROFESSIONAL EXPERIENCE</div>`;
        resumeContent.experience.forEach((exp, idx) => {
            html += `
                <div class="mb-4">
                    <div class="font-bold text-gray-900 editable" contenteditable="true">${exp.title}</div>
                    <div class="text-gray-600 italic editable" contenteditable="true">${exp.company} | ${exp.duration}${exp.location ? ' | ' + exp.location : ''}</div>
                    <ul class="list-disc ml-5 mt-2 space-y-1">
            `;
            (exp.responsibilities || []).forEach(resp => {
                html += `<li class="text-gray-700 editable" contenteditable="true">${resp}</li>`;
            });
            html += `</ul></div>`;
        });
        html += `</div>`;
    }
    
    // Education
    if (resumeContent.education && resumeContent.education.length > 0) {
        html += `<div class="mb-6"><div class="section-header">EDUCATION</div>`;
        resumeContent.education.forEach(edu => {
            html += `
                <div class="mb-3">
                    <div class="font-bold text-gray-900 editable" contenteditable="true">${edu.degree}</div>
                    <div class="text-gray-600 italic editable" contenteditable="true">${edu.institution} | ${edu.year}${edu.gpa ? ' | GPA: ' + edu.gpa : ''}</div>
                </div>
            `;
        });
        html += `</div>`;
    }
    
    // Projects
    if (resumeContent.projects && resumeContent.projects.length > 0) {
        html += `<div class="mb-6"><div class="section-header">PROJECTS</div>`;
        resumeContent.projects.forEach(proj => {
            html += `
                <div class="mb-3">
                    <div class="font-bold text-gray-900 editable" contenteditable="true">${proj.name}</div>
                    ${proj.technologies ? `<div class="text-gray-600 italic text-sm editable" contenteditable="true">Technologies: ${proj.technologies}</div>` : ''}
                    <ul class="list-disc ml-5 mt-1">
                        ${proj.description ? `<li class="text-gray-700 editable" contenteditable="true">${proj.description}</li>` : ''}
                        ${proj.impact ? `<li class="text-gray-700 editable" contenteditable="true">${proj.impact}</li>` : ''}
                    </ul>
                </div>
            `;
        });
        html += `</div>`;
    }
    
    // Certifications
    if (resumeContent.certifications && resumeContent.certifications.length > 0) {
        html += `<div class="mb-6"><div class="section-header">CERTIFICATIONS</div><ul class="list-disc ml-5">`;
        resumeContent.certifications.forEach(cert => {
            html += `<li class="text-gray-700 editable" contenteditable="true">${cert}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Achievements
    if (resumeContent.achievements && resumeContent.achievements.length > 0) {
        html += `<div class="mb-6"><div class="section-header">ACHIEVEMENTS</div><ul class="list-disc ml-5">`;
        resumeContent.achievements.forEach(ach => {
            html += `<li class="text-gray-700 editable" contenteditable="true">${ach}</li>`;
        });
        html += `</ul></div>`;
    }
    
    preview.innerHTML = html;
}

function displayATSScore(atsScore) {
    const scoreDisplay = document.getElementById('atsScoreDisplay');
    scoreDisplay.classList.remove('hidden');
    
    document.getElementById('overallScore').textContent = atsScore.overall_score;
    
    document.getElementById('scoreBreakdown').innerHTML = `
        <div class="grid grid-cols-2 gap-2 text-xs">
            <div>Skill Match: ${atsScore.skill_match}/100</div>
            <div>Keywords: ${atsScore.keyword_relevance}/100</div>
            <div>Role Alignment: ${atsScore.role_alignment}/100</div>
            <div>Formatting: ${atsScore.formatting_score}/100</div>
        </div>
    `;
    
    let suggestionsHtml = '<div class="font-semibold mb-1">Suggestions:</div><ul class="list-disc ml-4 space-y-1">';
    atsScore.suggestions.forEach(suggestion => {
        suggestionsHtml += `<li>${suggestion}</li>`;
    });
    suggestionsHtml += '</ul>';
    
    document.getElementById('scoreSuggestions').innerHTML = suggestionsHtml;
}

async function downloadPDF() {
    if (!currentResumeData) {
        showNotification('Please generate a resume first', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('resume_data', JSON.stringify(currentResumeData));
        formData.append('template', document.getElementById('template').value);
        
        const response = await fetch('/api/download-pdf', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resume_${currentResumeData.full_name.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('PDF downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to download PDF', 'error');
    }
}

async function downloadDOCX() {
    if (!currentResumeData) {
        showNotification('Please generate a resume first', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('resume_data', JSON.stringify(currentResumeData));
        formData.append('template', document.getElementById('template').value);
        
        const response = await fetch('/api/download-docx', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate DOCX');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resume_${currentResumeData.full_name.replace(/\s+/g, '_')}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('DOCX downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to download DOCX', 'error');
    }
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} z-50`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}