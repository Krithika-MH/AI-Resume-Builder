// ATS Checker JavaScript

document.getElementById('atsCheckForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await checkATSScore();
});

function updateFileName() {
    const fileInput = document.getElementById('resumeFile');
    const fileLabel = document.getElementById('fileLabel');
    
    if (fileInput.files.length > 0) {
        fileLabel.textContent = fileInput.files[0].name;
    } else {
        fileLabel.textContent = 'Click to upload or drag and drop';
    }
}

async function checkATSScore() {
    const btn = document.getElementById('checkBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    // Show loading state
    btn.disabled = true;
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    
    try {
        // Prepare form data
        const formData = new FormData();
        const fileInput = document.getElementById('resumeFile');
        
        if (!fileInput.files[0]) {
            throw new Error('Please upload a resume file');
        }
        
        formData.append('resume_file', fileInput.files[0]);
        formData.append('target_role', document.getElementById('targetRole').value);
        
        const jobDesc = document.getElementById('jobDescription').value;
        if (jobDesc) {
            formData.append('job_description', jobDesc);
        }
        
        // Call API
        const response = await fetch('/api/check-ats-score', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to check ATS score');
        }
        
        const atsScore = await response.json();
        
        // Display results
        displayResults(atsScore);
        
        // Show success message
        showNotification('ATS score calculated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to check ATS score', 'error');
    } finally {
        // Reset button state
        btn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
}

function displayResults(atsScore) {
    // Hide placeholder, show results
    document.getElementById('placeholder').classList.add('hidden');
    document.getElementById('resultsContainer').classList.remove('hidden');
    
    // Overall score
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreLevel = document.getElementById('scoreLevel');
    const scoreMessage = document.getElementById('scoreMessage');
    
    scoreValue.textContent = atsScore.overall_score;
    
    // Determine score level and color
    let level, message, circleClass;
    if (atsScore.overall_score >= 90) {
        level = 'Excellent';
        message = 'Your resume is highly optimized for ATS systems!';
        circleClass = 'score-excellent';
    } else if (atsScore.overall_score >= 75) {
        level = 'Good';
        message = 'Your resume is well-optimized with minor improvements possible.';
        circleClass = 'score-good';
    } else if (atsScore.overall_score >= 60) {
        level = 'Fair';
        message = 'Your resume meets basic ATS requirements but needs improvement.';
        circleClass = 'score-fair';
    } else {
        level = 'Needs Improvement';
        message = 'Your resume needs significant optimization for ATS systems.';
        circleClass = 'score-poor';
    }
    
    scoreLevel.textContent = level;
    scoreMessage.textContent = message;
    
    // Reset circle classes and add new one
    scoreCircle.className = 'score-circle flex items-center justify-center ' + circleClass;
    
    // Update breakdown bars
    updateScoreBar('skill', atsScore.skill_match);
    updateScoreBar('keyword', atsScore.keyword_relevance);
    updateScoreBar('role', atsScore.role_alignment);
    updateScoreBar('format', atsScore.formatting_score);
    updateScoreBar('section', atsScore.section_completeness);
    
    // Display missing keywords
    if (atsScore.missing_keywords && atsScore.missing_keywords.length > 0) {
        const missingSection = document.getElementById('missingKeywordsSection');
        const missingKeywords = document.getElementById('missingKeywords');
        
        missingSection.classList.remove('hidden');
        missingKeywords.innerHTML = '';
        
        atsScore.missing_keywords.forEach(keyword => {
            const badge = document.createElement('span');
            badge.className = 'px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm';
            badge.textContent = keyword;
            missingKeywords.appendChild(badge);
        });
    } else {
        document.getElementById('missingKeywordsSection').classList.add('hidden');
    }
    
    // Display suggestions
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    
    atsScore.suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.className = 'flex items-start';
        li.innerHTML = `
            <svg class="w-5 h-5 text-indigo-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
            <span>${suggestion}</span>
        `;
        suggestionsList.appendChild(li);
    });
}

function updateScoreBar(type, score) {
    document.getElementById(`${type}Score`).textContent = `${score}/100`;
    document.getElementById(`${type}Bar`).style.width = `${score}%`;
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

// Drag and drop functionality
const dropZone = document.querySelector('.border-dashed');
const fileInput = document.getElementById('resumeFile');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropZone.classList.add('border-indigo-500', 'bg-indigo-50');
}

function unhighlight(e) {
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        fileInput.files = files;
        updateFileName();
    }
}