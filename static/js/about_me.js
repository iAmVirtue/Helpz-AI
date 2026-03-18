/**
 * 1. DATA LAYER (Separation of Concerns)
 * Keeps the HTML clean and makes future updates extremely easy.
 */
const portfolioData = {
    skills: [
        { category: "Languages", items: ["C++", "Python", "Java"] },
        { category: "Web Tech", items: ["HTML5", "CSS3", "JavaScript"] },
        { category: "Tools & DB", items: ["MySQL", "Machine Learning", "VS Code"] }
    ],
    otherProjects: [
        {
            title: "JARVIS Desktop Assistant",
            desc: "AI-based Python assistant for app control, web search, and voice interaction.",
            icon: "ph-microphone-stage"
        },
        {
            title: "Chatbot Ticketing System",
            desc: "Customer query handler generating tickets stored in MySQL.",
            icon: "ph-ticket"
        },
        {
            title: "Hangman Interactive",
            desc: "Python-based word-guessing game with score tracking.",
            icon: "ph-game-controller"
        }
    ],
    experience: [
        {
            title: "Event Organizer",
            role: "Algohour, Hack-Rush & More",
            desc: "Led end-to-end execution of major technical events engaging over 500+ participants."
        },
        {
            title: "ACPC Club Member",
            role: "2024 - Present",
            desc: "Actively contributed to coding sessions, hackathons, and SIH selection rounds."
        },
        {
            title: "Community Volunteer",
            role: "Hamara Sankalp",
            desc: "Contributed 70+ hours tutoring underprivileged students and organizing donation drives."
        }
    ]
};

/**
 * 2. RENDER ENGINE
 * Dynamically generates UI components based on the data layer.
 */

// Render Skills
const skillsContainer = document.getElementById('skills-container');
if (skillsContainer) {
    portfolioData.skills.forEach(skillGroup => {
        const groupHtml = `
            <div>
                <h4 class="text-xs font-bold text-ash/70 uppercase tracking-widest mb-2">${skillGroup.category}</h4>
                <div class="flex flex-wrap gap-2">
                    ${skillGroup.items.map(item => `
                        <span class="px-3 py-1.5 bg-surface rounded-lg text-sm text-gray-200 border border-white/5 hover:border-ios-blue/50 hover:bg-ios-blue/10 transition-colors cursor-default">${item}</span>
                    `).join('')}
                </div>
            </div>
        `;
        skillsContainer.insertAdjacentHTML('beforeend', groupHtml);
    });
}

// Render Other Projects
const projectsContainer = document.getElementById('projects-container');
if (projectsContainer) {
    portfolioData.otherProjects.forEach(proj => {
        const projHtml = `
            <div class="group cursor-pointer p-4 -mx-4 rounded-xl hover:bg-white/5 transition-colors flex gap-4 items-start">
                <div class="w-10 h-10 rounded-lg bg-surface flex items-center justify-center shrink-0 border border-white/5 group-hover:border-ios-blue/30 transition-colors">
                    <i class="ph ${proj.icon} text-xl text-ash group-hover:text-ios-blue transition-colors"></i>
                </div>
                <div>
                    <h4 class="text-white font-medium text-sm mb-1 group-hover:text-ios-blue transition-colors">${proj.title}</h4>
                    <p class="text-ash text-xs leading-relaxed">${proj.desc}</p>
                </div>
            </div>
        `;
        projectsContainer.insertAdjacentHTML('beforeend', projHtml);
    });
}

// Render Experience
const expContainer = document.getElementById('experience-container');
if (expContainer) {
    portfolioData.experience.forEach(exp => {
        const expHtml = `
            <div class="relative pl-6 border-l border-white/10">
                <div class="absolute w-3 h-3 bg-darkbg border-2 border-ios-blue rounded-full -left-[7px] top-1"></div>
                <h4 class="text-white font-bold text-base mb-1">${exp.title}</h4>
                <span class="block text-xs text-accent font-medium mb-2">${exp.role}</span>
                <p class="text-ash text-sm font-light leading-relaxed">${exp.desc}</p>
            </div>
        `;
        expContainer.insertAdjacentHTML('beforeend', expHtml);
    });
}

/**
 * 3. INTERACTION & ANIMATION LOGIC
 */

// Mouse Spotlight Effect for Bento Cards
document.querySelectorAll('.bento-card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Scroll Reveal Animation (Intersection Observer)
const revealElements = document.querySelectorAll('.reveal');

const revealOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
};

const revealOnScroll = new IntersectionObserver(function (entries, observer) {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;

        // Add staggered delay based on horizontal position (optional polish)
        entry.target.classList.add('active');
        observer.unobserve(entry.target); // Only animate once
    });
}, revealOptions);

revealElements.forEach(el => revealOnScroll.observe(el));
