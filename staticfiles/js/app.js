/**
 * INTERACTIVE CONCIERGE LOGIC (Progressive Disclosure)
 */
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const step2 = document.getElementById('step-2');
const step3 = document.getElementById('step-3');
const jdInput = document.getElementById('jdInput');
const analyzeBtn = document.getElementById('analyzeBtn');

// Drag and drop setup
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    if (dropzone) dropzone.addEventListener(eventName, e => { e.preventDefault(); e.stopPropagation(); }, false);
});

['dragenter', 'dragover'].forEach(eventName => {
    if (dropzone) dropzone.addEventListener(eventName, () => dropzone.classList.add('border-ios-blue', 'bg-ios-blue/5'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    if (dropzone) dropzone.addEventListener(eventName, () => dropzone.classList.remove('border-ios-blue', 'bg-ios-blue/5'), false);
});

if (dropzone) dropzone.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files));
if (fileInput) fileInput.addEventListener('change', function () { handleFiles(this.files); });

function handleFiles(files) {
    if (files.length > 0 && files[0].type === 'application/pdf') {
        // 1. Update UI for uploaded file
        fileNameDisplay.innerHTML = `<span class="text-ios-blue font-bold"><i class="ph ph-file-pdf"></i> ${files[0].name}</span>`;
        dropzone.classList.add('border-ios-blue');

        // 2. Reveal Step 2 (Job Description) smoothly
        setTimeout(() => {
            step2.classList.add('active', 'mt-4');
            // Scroll slightly down to keep it in focus
            step2.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);

    } else if (files.length > 0) {
        alert('Please upload a PDF file.');
    }
}

// Listen to JD input to reveal the Generate Button
if (jdInput) jdInput.addEventListener('input', function () {
    // Reveal button if they type at least 10 characters
    if (this.value.trim().length > 10 && !step3.classList.contains('active')) {
        step3.classList.add('active', 'mt-4');
        setTimeout(() => step3.scrollIntoView({ behavior: 'smooth', block: 'end' }), 100);
    }
});


/**
 * SYSTEM PROCESSING LOGIC
 */
async function startAnalysis() {
    const fileInput = document.getElementById('fileInput');
    const jdInput = document.getElementById('jdInput');
    if (!fileInput.files.length || jdInput.value.length < 10) return;

    const inputSection = document.getElementById('section-input');
    const loadingSection = document.getElementById('section-loading');
    const resultsSection = document.getElementById('section-results');

    // Hide input form fluidly
    inputSection.style.opacity = '0';

    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    formData.append('job_desc', jdInput.value);

    setTimeout(async () => {
        inputSection.style.display = 'none';

        // Show loading
        loadingSection.classList.remove('hidden');
        loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Simulate AI Processing steps
        const loadingBar = document.getElementById('loadingBar');
        const subText = document.getElementById('loadingSub');

        loadingBar.style.width = '0%';
        setTimeout(() => { loadingBar.style.width = '30%'; subText.innerText = "Processing PDF and executing Gemini neural vector analysis..."; }, 500);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.error) {
                alert("Analysis Failed: " + data.error);
                resetApp();
                return;
            }

            loadingBar.style.width = '100%';
            subText.innerText = "Done!";

            const quickFixes = data.analysis.quick_fix;
            if (Array.isArray(quickFixes) && quickFixes.length > 0) {
                document.getElementById('ai-quick-fix').innerHTML = quickFixes.map(fix => `<li class="mb-2 last:mb-0">${fix}</li>`).join('');
            } else {
                document.getElementById('ai-quick-fix').innerHTML = `<li>${quickFixes || "No specific recommendation generated."}</li>`;
            }

            document.getElementById('extracted-text-body').innerHTML = `<pre class="font-mono text-xs whitespace-pre-wrap">${data.resume_text.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
            document.getElementById('extracted-text-edit').value = data.resume_text;

            const kws = data.analysis.missing_keywords || [];
            document.getElementById('missing-keywords-list').innerHTML = kws.map(k => `<span class="px-3 py-1 bg-surface text-white rounded-full text-xs border border-ash/20 hover:border-ios-blue transition-colors cursor-default">${k}</span>`).join('');

            const gaps = data.analysis.critical_gaps || [];
            document.getElementById('critical-gaps-list').innerHTML = gaps.map(g => `<li class="flex items-start gap-3 bg-rose-500/10 p-3 rounded-lg border border-rose-500/20"><i class="ph ph-x-circle text-rose-400 mt-0.5 shrink-0 text-lg"></i><span class="text-sm text-ash font-light">${g}</span></li>`).join('');

            renderActionPlan(data.plan.interview_questions, data.plan.micro_project);

            // Reveal Results & Scroll to them
            setTimeout(() => {
                loadingSection.classList.add('hidden');
                resultsSection.classList.remove('hidden');
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

                animateScore(data.analysis.match_percentage || 0);
            }, 800);

        } catch (e) {
            alert("Analysis Server Error: " + e.message);
            resetApp();
        }

    }, 400); // Wait for fade out
}

function resetApp() {
    // Reset state
    fileInput.value = '';
    jdInput.value = '';
    fileNameDisplay.innerText = "Select your Resume (PDF)";
    dropzone.classList.remove('border-ios-blue');

    // Hide Steps
    step2.classList.remove('active', 'mt-4');
    step3.classList.remove('active', 'mt-4');

    // Toggle Sections
    document.getElementById('section-results').classList.add('hidden');
    const inputSection = document.getElementById('section-input');
    inputSection.style.display = 'block';
    setTimeout(() => inputSection.style.opacity = '1', 50);

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * ANIMATIONS & INTERACTIONS
 */
function animateScore(targetScore) {
    const circle = document.getElementById('scoreCircle');
    const text = document.getElementById('scoreText');

    const circumference = 251.2;
    const offset = circumference - (targetScore / 100) * circumference;

    circle.style.strokeDashoffset = circumference;
    text.innerText = "0%";

    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
        let current = 0;
        const timer = setInterval(() => {
            current += 1;
            text.innerText = current + "%";
            if (current >= targetScore) clearInterval(timer);
        }, 1500 / targetScore);
    }, 300);
}

/**
 * DYNAMIC DATA RENDERING (Accordions & Tasks)
 */
function renderActionPlan(questions, tasks) {
    const accContainer = document.getElementById('accordion-container');
    const taskContainer = document.getElementById('task-container');

    if (!questions || !questions.length) {
        accContainer.innerHTML = '<p class="text-ash font-light">No questions generated via Gemini API.</p>';
    } else {
        accContainer.innerHTML = questions.map((item) => `
            <div class="glass-card rounded-xl overflow-hidden accordion-item">
                <button class="w-full text-left p-4 flex justify-between items-center focus:outline-none hover:bg-white/5 transition-colors" onclick="toggleAccordion(this)">
                    <span class="text-sm font-medium text-white pr-4 leading-snug">${item.question || item.q}</span>
                    <i class="ph ph-caret-down text-ash transition-transform duration-300 flex-shrink-0"></i>
                </button>
                <div class="accordion-content px-4">
                    <div class="p-4 bg-surface/80 border border-white/5 rounded-lg text-sm text-ash font-light leading-relaxed">
                        <strong class="text-ios-blue block mb-2 font-semibold">Ideal Answer:</strong>
                        ${item.ideal_answer || item.a}
                    </div>
                </div>
            </div>
        `).join('');
    }

    if (!tasks || !tasks.length) {
        taskContainer.innerHTML = '<p class="text-ash font-light">No project generated via Gemini API.</p>';
    } else {
        taskContainer.innerHTML = tasks.map((task, idx) => `
            <div class="glass-card rounded-xl p-4 flex gap-4 cursor-pointer group hover:bg-surface/80 transition-colors" onclick="toggleTask(${idx}, this)">
                <div class="mt-1 flex-shrink-0 relative w-5 h-5 border-2 border-ash/30 rounded bg-surface flex items-center justify-center group-hover:border-ios-blue transition-colors task-checkbox">
                    <i class="ph ph-check text-ios-blue opacity-0 transition-opacity font-bold"></i>
                </div>
                <div>
                    <h4 class="text-white font-medium text-sm mb-1 group-hover:text-ios-blue transition-colors task-title">${task.title}</h4>
                    <p class="text-xs text-ash font-light leading-relaxed mb-3">${task.desc}</p>
                    <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(task.title + ' tutorial')}" target="_blank" onclick="event.stopPropagation()" class="inline-flex items-center gap-1.5 text-[10px] uppercase tracking-widest font-bold text-ios-blue hover:text-white transition-colors bg-ios-blue/10 hover:bg-ios-blue border border-ios-blue/20 hover:border-ios-blue rounded-md px-2.5 py-1.5 shadow-sm">
                         <i class="ph ph-youtube-logo text-sm leading-none"></i> Find Tutorial
                    </a>
                </div>
            </div>
        `).join('');
    }
}

function toggleAccordion(btn) {
    const item = btn.parentElement;
    const wasActive = item.classList.contains('active');
    document.querySelectorAll('.accordion-item').forEach(el => el.classList.remove('active'));
    if (!wasActive) item.classList.add('active');
}

function toggleTask(idx, element) {
    const checkbox = element.querySelector('.ph-check');
    const title = element.querySelector('.task-title');
    const box = element.querySelector('.task-checkbox');

    if (checkbox.classList.contains('opacity-0')) {
        // Mark complete
        checkbox.classList.remove('opacity-0');
        checkbox.classList.add('opacity-100');
        box.classList.add('border-ios-blue', 'bg-ios-blue/10');
        title.classList.add('line-through', 'text-ash/60');
        title.classList.remove('text-white');
    } else {
        // Mark incomplete
        checkbox.classList.add('opacity-0');
        checkbox.classList.remove('opacity-100');
        box.classList.remove('border-ios-blue', 'bg-ios-blue/10');
        title.classList.remove('line-through', 'text-ash/60');
        title.classList.add('text-white');
    }
}

/**
 * RESUME MODIFICATION LOGIC
 */
function toggleResumeEdit() {
    const body = document.getElementById('extracted-text-body');
    const editArea = document.getElementById('extracted-text-edit');
    const editBtn = document.getElementById('editResumeBtn');
    const downloadBtn = document.getElementById('downloadResumeBtn');

    if (editArea.classList.contains('hidden')) {
        // Entering edit mode
        body.classList.add('hidden');
        editArea.classList.remove('hidden');
        editArea.classList.add('block');
        downloadBtn.classList.remove('hidden');
        editBtn.innerHTML = '<i class="ph ph-check"></i> Save';
    } else {
        // Exiting edit mode
        editArea.classList.add('hidden');
        editArea.classList.remove('block');
        body.classList.remove('hidden');
        downloadBtn.classList.add('hidden');
        
        // Update the body with the new edited text safely
        const newText = editArea.value;
        body.innerHTML = `<pre class="font-mono text-xs whitespace-pre-wrap">${newText.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
        editBtn.innerHTML = '<i class="ph ph-pencil-simple"></i> Modify';
    }
}

function downloadResume() {
    const newText = document.getElementById('extracted-text-edit').value;
    
    // Create a temporary hidden container to format as PDF
    const printContainer = document.createElement('div');
    printContainer.style.padding = '40px';
    printContainer.style.background = '#ffffff';
    printContainer.style.color = '#000000';
    printContainer.style.fontFamily = 'Arial, sans-serif';
    printContainer.style.fontSize = '12px';
    printContainer.style.whiteSpace = 'pre-wrap';
    printContainer.style.lineHeight = '1.6';
    
    // Sanitize and append the user's text
    printContainer.innerText = newText;
    
    // Config for html2pdf
    const opt = {
        margin:       0.5,
        filename:     'RoleReadyAI_Updated_Resume.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    
    // Build and download the PDF
    html2pdf().set(opt).from(printContainer).save();
}
