// Interview Coach AI Chatbot Client

const API_BASE = '';

// State management
let state = {
    sessionId: null,
    role: null,
    company: null,
    experienceLevel: null,
    currentQuestion: null,
    messages: [],
    evaluations: [],
    questionCount: 0,
    isLoading: false,
};

// DOM Elements
const setupSection = document.getElementById('setup-section');
const loadingSection = document.getElementById('loading-section');
const chatSection = document.getElementById('chat-section');
const resultsSection = document.getElementById('results-section');
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const endInterviewBtn = document.getElementById('end-interview-btn');
const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');
const roleInput = document.getElementById('role-input');
const companyInput = document.getElementById('company-input');
const experienceInput = document.getElementById('experience-input');
const inputError = document.getElementById('input-error');

// Event Listeners
startBtn.addEventListener('click', startInterview);
sendBtn.addEventListener('click', sendMessage);
endInterviewBtn.addEventListener('click', endInterview);
restartBtn.addEventListener('click', restartInterview);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !state.isLoading) {
        e.preventDefault();
        sendMessage();
    }
});

// ==================== Main Functions ====================

async function startInterview() {
    const role = roleInput.value.trim();
    const company = companyInput.value.trim();
    const experienceLevel = experienceInput.value;

    if (!role) {
        alert('Please enter a job role');
        return;
    }

    try {
        setupSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');

        const response = await fetch(`${API_BASE}/api/chat/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                role: role,
                company: company,
                experience_level: experienceLevel
            })
        });

        if (!response.ok) {
            throw new Error('Failed to start interview');
        }

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            setupSection.classList.remove('hidden');
            loadingSection.classList.add('hidden');
            return;
        }

        // Store state
        state.sessionId = data.session_id;
        state.role = data.role_confirmed || role.toLowerCase();
        state.company = company;
        state.experienceLevel = experienceLevel;
        state.currentQuestion = data.question;
        state.messages = [];
        state.evaluations = [];
        state.questionCount = 0;

        // Initialize chat UI
        loadingSection.classList.add('hidden');
        chatSection.classList.remove('hidden');
        document.getElementById('session-role').textContent = capitalizeWords(state.role);
        document.getElementById('question-count').textContent = '0 / 5';
        document.getElementById('current-score').textContent = '--';

        // Display first question
        addMessage('assistant', data.question, null);
        messageInput.focus();

    } catch (error) {
        console.error('Start interview error:', error);
        alert('Error starting interview: ' + error.message);
        setupSection.classList.remove('hidden');
        loadingSection.classList.add('hidden');
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        inputError.classList.remove('hidden');
        setTimeout(() => inputError.classList.add('hidden'), 3000);
        return;
    }

    if (state.isLoading || !state.currentQuestion) {
        return;
    }

    // Add user message to UI
    addMessage('user', message, null);
    messageInput.value = '';
    inputError.classList.add('hidden');

    // Add typing indicator
    const typingId = addTypingIndicator();

    try {
        state.isLoading = true;
        const response = await fetch(`${API_BASE}/api/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                message: message,
                role: state.role,
                experience_level: state.experienceLevel,
                current_question: state.currentQuestion
            })
        });

        if (!response.ok) {
            throw new Error('Failed to process message');
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.error) {
            addMessage('assistant', 'Error: ' + data.error, null);
            state.isLoading = false;
            return;
        }

        // Store evaluation
        state.evaluations.push({
            technical_depth: data.technical_depth,
            relevance: data.relevance,
            confidence: data.confidence
        });

        // Display feedback and next question
        const feedbackText = `📊 Feedback: ${data.feedback}

🎯 Technical Depth: ${data.technical_depth}/10 | Relevance: ${data.relevance}/10 | Confidence: ${data.confidence}/10`;

        addMessage('assistant', feedbackText, null);

        state.questionCount++;
        updateQuestionCount();

        if (data.next_question && state.questionCount < 5) {
            state.currentQuestion = data.next_question;
            setTimeout(() => {
                addMessage('assistant', data.next_question, null);
                messageInput.focus();
            }, 500);
        } else if (state.questionCount >= 5) {
            // Auto-end interview after 5 questions
            setTimeout(() => {
                addMessage('assistant', 'Interview complete! Click "End Interview & See Results" to view your feedback.', null);
            }, 500);
        }

        state.isLoading = false;

    } catch (error) {
        console.error('Send message error:', error);
        removeTypingIndicator(typingId);
        addMessage('assistant', 'Error: Unable to process your answer. Please try again.', null);
        state.isLoading = false;
    }
}

async function endInterview() {
    if (state.questionCount === 0) {
        alert('Please answer at least one question before ending the interview');
        return;
    }

    try {
        chatSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        loadingSection.querySelector('p').textContent = 'Calculating your results...';

        const response = await fetch(`${API_BASE}/api/chat/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                evaluations: state.evaluations,
                role: state.role
            })
        });

        if (!response.ok) {
            throw new Error('Failed to evaluate interview');
        }

        const data = await response.json();

        // Display results
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Update score and label
        const score = data.overall_score;
        document.getElementById('final-score').textContent = score;
        document.getElementById('score-label').textContent = getScoreLabel(score);

        // Update metrics
        document.getElementById('metric-technical').textContent = data.avg_technical_depth.toFixed(1);
        document.getElementById('metric-relevance').textContent = data.avg_relevance.toFixed(1);
        document.getElementById('metric-confidence').textContent = data.avg_confidence.toFixed(1);

        // Update lists
        const strengthsList = document.getElementById('strengths-list');
        strengthsList.innerHTML = data.strengths
            .map(s => `<li class="flex items-start gap-2"><span class="text-accent mt-1">✓</span><span class="text-white">${s}</span></li>`)
            .join('');

        const improvementsList = document.getElementById('improvements-list');
        improvementsList.innerHTML = data.improvements
            .map(i => `<li class="flex items-start gap-2"><span class="text-ios-blue mt-1">→</span><span class="text-white">${i}</span></li>`)
            .join('');

    } catch (error) {
        console.error('End interview error:', error);
        alert('Error finalizing interview: ' + error.message);
        loadingSection.classList.add('hidden');
        chatSection.classList.remove('hidden');
    }
}

function restartInterview() {
    // Reset state
    state = {
        sessionId: null,
        role: null,
        company: null,
        experienceLevel: null,
        currentQuestion: null,
        messages: [],
        evaluations: [],
        questionCount: 0,
        isLoading: false,
    };

    // Clear UI
    messagesContainer.innerHTML = '';
    messageInput.value = '';

    // Show setup again
    resultsSection.classList.add('hidden');
    setupSection.classList.remove('hidden');
    roleInput.focus();
}

// ==================== UI Helper Functions ====================

function addMessage(role, content, evaluation) {
    const messageEl = document.createElement('div');
    messageEl.className = role === 'user'
        ? 'flex justify-end'
        : 'flex justify-start';

    const contentEl = document.createElement('div');
    contentEl.className = role === 'user'
        ? 'max-w-xs md:max-w-md bg-ios-blue/20 border border-ios-blue/50 rounded-2xl p-4 text-white'
        : 'max-w-xs md:max-w-md bg-accent/20 border border-accent/50 rounded-2xl p-4 text-white';

    // Format content (handle line breaks)
    const formattedContent = content.replace(/\n/g, '<br>');
    contentEl.innerHTML = formattedContent;

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);

    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    state.messages.push({ role, content, evaluation });
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageEl = document.createElement('div');
    messageEl.id = id;
    messageEl.className = 'flex justify-start';

    const contentEl = document.createElement('div');
    contentEl.className = 'max-w-xs md:max-w-md bg-accent/20 border border-accent/50 rounded-2xl p-4';
    contentEl.innerHTML = '<div class="flex gap-1"><span class="w-2 h-2 bg-accent rounded-full animate-bounce"></span><span class="w-2 h-2 bg-accent rounded-full animate-bounce" style="animation-delay: 0.1s"></span><span class="w-2 h-2 bg-accent rounded-full animate-bounce" style="animation-delay: 0.2s"></span></div>';

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) {
        el.remove();
    }
}

function updateQuestionCount() {
    document.getElementById('question-count').textContent = `${state.questionCount} / 5`;

    // Calculate current average score
    if (state.evaluations.length > 0) {
        const avg = state.evaluations.reduce((sum, e) => sum + (e.technical_depth + e.relevance + e.confidence) / 3, 0) / state.evaluations.length;
        const score = Math.round(avg * 10);
        document.getElementById('current-score').textContent = score;
    }
}

function getScoreLabel(score) {
    if (score >= 90) return 'Excellent!';
    if (score >= 80) return 'Very Good!';
    if (score >= 70) return 'Good Job!';
    if (score >= 60) return 'Decent Performance';
    if (score >= 50) return 'Keep Practicing';
    return 'Room for Improvement';
}

function capitalizeWords(str) {
    return str
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
