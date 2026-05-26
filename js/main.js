/**
 * Fabric Arcade - Main JavaScript
 * Gaming-inspired interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    initScrollEffects();
    initTypingEffect();
    initParticles();
});

/**
 * Game Filters
 */
function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const gameCards = document.querySelectorAll('.game-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;

            // Filter cards with animation
            gameCards.forEach(card => {
                const workloads = card.dataset.workloads;
                
                if (filter === 'all' || workloads.includes(filter)) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.5s ease';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Scroll Effects
 */
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    const sections = document.querySelectorAll('section');

    // Navbar background on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(10, 10, 26, 0.98)';
        } else {
            navbar.style.background = 'rgba(10, 10, 26, 0.9)';
        }
    });

    // Intersection Observer for section animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Typing Effect for Terminal
 */
function initTypingEffect() {
    const terminal = document.querySelector('.terminal-body');
    if (!terminal) return;

    // Add blinking cursor
    const cursor = document.createElement('span');
    cursor.className = 'cursor';
    cursor.textContent = '█';
    cursor.style.animation = 'blink 1s infinite';
    terminal.appendChild(cursor);
}

/**
 * Particle Background (optional, lightweight)
 */
function initParticles() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    // Create floating particles
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 2}px;
            height: ${Math.random() * 4 + 2}px;
            background: rgba(0, 212, 255, ${Math.random() * 0.5 + 0.2});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${Math.random() * 10 + 10}s infinite linear;
            pointer-events: none;
        `;
        hero.appendChild(particle);
    }
}

/**
 * Smooth Scroll for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Add CSS animations
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
    }
    
    section {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    section.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .cursor {
        color: var(--accent);
        margin-left: 4px;
    }
`;
document.head.appendChild(style);

/**
 * Easter Egg: Konami Code
 */
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let konamiIndex = 0;

document.addEventListener('keydown', (e) => {
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            activateEasterEgg();
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
});

function activateEasterEgg() {
    document.body.style.animation = 'rainbow 2s linear';
    setTimeout(() => {
        document.body.style.animation = '';
        alert('🎮 KONAMI CODE ACTIVATED!\n\nYou found the secret! Check out our bonus games...');
    }, 2000);
    
    const rainbowStyle = document.createElement('style');
    rainbowStyle.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
    `;
    document.head.appendChild(rainbowStyle);
}

console.log(`
🎮 FABRIC ARCADE 🎮
==================
Welcome, developer!
Try the Konami Code for a surprise...
↑ ↑ ↓ ↓ ← → ← → B A
`);
