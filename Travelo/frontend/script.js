// script.js - Complete Version with Production Support
// Dynamically determine API base URL based on environment
const API_BASE = (() => {
    const hostname = window.location.hostname;
    
    // If on localhost/127.0.0.1, use localhost API
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('localhost')) {
        return 'http://localhost:5000/api';
    }
    
    // For production, use the same host with /api prefix
    const protocol = window.location.protocol;
    const host = window.location.host;
    return `${protocol}//${host}/api`;
})();

console.log(`API Base URL: ${API_BASE}`);

let currentToken = localStorage.getItem('token');

// ==================== AUTH HEADERS ====================
function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
    };
}

function isLoggedIn() {
    return !!localStorage.getItem('token');
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    currentToken = null;
    window.location.href = 'index.html';
}

// ==================== AUTH FUNCTIONS ====================
async function signup() {
    const username = document.getElementById('signup-username')?.value?.trim();
    const email = document.getElementById('signup-email')?.value?.trim();
    const password = document.getElementById('signup-password')?.value?.trim();

    if (!email || !password) {
        alert("Email aur Password zaruri hain");
        return;
    }

    if (password.length < 6) {
        alert("Password kam se kam 6 characters ka hona chahiye");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username || email.split('@')[0], email, password })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            currentToken = data.token;
            alert("Account ban gaya! Welcome! 🎉");
            window.location.href = 'dashboard.html';
        } else {
            alert(data.error || "Signup mein masla hai");
        }
    } catch (err) {
        console.error('Signup error:', err);
        alert("Backend se connection nahi ho raha. Kya server chal raha hai?");
    }
}

async function login() {
    const email = document.getElementById('login-email')?.value?.trim();
    const password = document.getElementById('login-password')?.value?.trim();

    if (!email || !password) {
        alert("Email aur Password dono zaruri hain");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            currentToken = data.token;

            alert("Login successful! Welcome back 🎉");
            window.location.href = 'dashboard.html';
        } else {
            alert(data.error || "Email ya Password galat hai");
        }
    } catch (err) {
        console.error('Login error:', err);
        alert("Server se connect nahi ho raha. Server chal raha hai kya?");
    }
}

// ==================== PREFERENCES FUNCTIONS ====================
async function getPreferences() {
    if (!isLoggedIn()) {
        alert("Login karo pehle");
        return null;
    }

    try {
        const res = await fetch(`${API_BASE}/preferences`, {
            headers: getAuthHeaders()
        });

        if (!res.ok) {
            console.error('Error fetching preferences:', res.status);
            return null;
        }

        const data = await res.json();
        return data;
    } catch (err) {
        console.error('Get preferences error:', err);
        return null;
    }
}

async function savePreferences() {
    if (!isLoggedIn()) {
        alert("Login karo pehle");
        return;
    }

    const preferredType = document.getElementById('pref-type')?.value || null;
    const maxBudget = parseInt(document.getElementById('pref-budget')?.value) || 100;
    const travelStyle = document.getElementById('pref-style')?.value || null;
    const region = document.getElementById('pref-region')?.value || null;

    try {
        const res = await fetch(`${API_BASE}/preferences`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                preferred_destination_type: preferredType,
                max_budget: maxBudget,
                travel_style: travelStyle,
                preferred_region: region
            })
        });

        const data = await res.json();

        if (res.ok) {
            alert("Preferences save ho gaye! 🎉");
            getRecommendations(); // Reload recommendations with new preferences
        } else {
            alert(data.error || "Preferences save nahi ho saki");
        }
    } catch (err) {
        console.error('Save preferences error:', err);
        alert("Server se connection problem");
    }
}

// ==================== RECOMMENDATIONS ====================
async function getRecommendations() {
    if (!isLoggedIn()) {
        alert("Recommendations dekhne ke liye login karo");
        return;
    }

    const container = document.getElementById('recommendations-container');
    if (container) {
        container.innerHTML = '<p style="text-align: center; padding: 20px;">Loading smart recommendations...</p>';
    }

    try {
        const res = await fetch(`${API_BASE}/recommendations`, {
            headers: getAuthHeaders()
        });

        const data = await res.json();

        if (!res.ok) {
            if (container) {
                container.innerHTML = `<p style="color:red; padding: 20px;">${data.error || 'Error loading recommendations'}</p>`;
            }
            return;
        }

        if (data.recommendations && Array.isArray(data.recommendations)) {
            renderRecommendations(data.recommendations, container);
        } else {
            if (container) {
                container.innerHTML = '<p style="color: orange; padding: 20px;">No recommendations available yet. Update your preferences!</p>';
            }
        }
    } catch (err) {
        console.error('Get recommendations error:', err);
        if (container) {
            container.innerHTML = '<p style="color: red; padding: 20px;">Recommendations load nahi ho rahi. Server check karo.</p>';
        }
    }
}

function renderRecommendations(recommendations, container) {
    if (!container || !Array.isArray(recommendations)) return;

    if (recommendations.length === 0) {
        container.innerHTML = '<p style="color: orange; padding: 20px;">Koi recommendations nahi. Apne preferences update karo!</p>';
        return;
    }

    let html = '';
    recommendations.forEach(dest => {
        const name = dest.name || 'Unknown';
        const type = dest.type || 'Adventure';
        const style = dest.style || 'Moderate';
        const description = dest.description || 'Beautiful destination';
        const cost = dest.avg_cost_per_day || '0';
        const matchScore = dest.match_score || '0';
        
        html += `
            <article class="dest-card">
                <div class="dest-img-container">
                    <div class="dest-badge"><i class="fa-solid fa-star"></i> ${matchScore}% Match</div>
                    <img src="https://source.unsplash.com/featured/?${name.toLowerCase().replace(/\s+/g, ',')}" 
                         alt="${name}"
                         onerror="this.src='https://via.placeholder.com/300x200?text=${name}'">
                </div>
                <div class="dest-content">
                    <h3>${name}</h3>
                    <div class="dest-tags">
                        <span class="tag">${type}</span>
                        <span class="tag">${style}</span>
                    </div>
                    <p>${description}</p>
                    <div class="dest-footer">
                        <span class="dest-price">~$${cost}/day</span>
                    </div>
                </div>
            </article>
        `;
    });
    container.innerHTML = html;
}

// ==================== UI LOGIC (Drawer, Scroll, Header etc.) ====================
document.addEventListener('DOMContentLoaded', () => {
    // Update footer year
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) yearSpan.textContent = new Date().getFullYear();

    // Update header with user info if logged in
    if (isLoggedIn()) {
        const username = localStorage.getItem('username') || 'User';
        const userGreeting = document.getElementById('user-greeting');
        if (userGreeting) {
            userGreeting.textContent = `Welcome, ${username}!`;
        }
    }

    // ---------- RIGHT DRAWER LOGIC ----------
    const menuBtn = document.getElementById('menuToggleBtn');
    const drawer = document.getElementById('sideDrawer');
    const overlay = document.getElementById('drawerOverlay');
    const closeBtn = document.getElementById('closeDrawerBtn');
    const drawerLinks = document.querySelectorAll('.drawer-nav a');

    function openDrawer() {
        if (!drawer) return;
        drawer.classList.add('active');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        if (menuBtn) {
            menuBtn.setAttribute('aria-expanded', 'true');
            const icon = menuBtn.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-xmark';
        }
    }

    function closeDrawer() {
        if (!drawer) return;
        drawer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
        if (menuBtn) {
            menuBtn.setAttribute('aria-expanded', 'false');
            const icon = menuBtn.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-bars';
        }
    }

    if (menuBtn) menuBtn.addEventListener('click', openDrawer);
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (overlay) overlay.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawer && drawer.classList.contains('active')) closeDrawer();
    });

    // Close drawer when any navigation link is clicked
    drawerLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetEl = document.querySelector(targetId);
                if (targetEl) {
                    e.preventDefault();
                    closeDrawer();
                    targetEl.scrollIntoView({ behavior: 'smooth' });
                } else {
                    closeDrawer();
                }
            } else {
                closeDrawer();
            }
        });
    });

    // ---------- STICKY HEADER & BACK TO TOP ----------
    const header = document.getElementById('header');
    const backTopBtn = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        if (header) {
            if (window.scrollY > 20) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
        }
        if (backTopBtn) {
            if (window.scrollY > 500) backTopBtn.classList.add('visible');
            else backTopBtn.classList.remove('visible');
        }
    });

    if (backTopBtn) {
        backTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ---------- SMOOTH SCROLL FOR ALL ANCHOR LINKS ----------
    const allAnchors = document.querySelectorAll('a[href^="#"]');
    allAnchors.forEach(anchor => {
        if (anchor.closest('.drawer-nav')) return;
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === "#" || targetId === "") return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({ behavior: 'smooth' });
                if (drawer && drawer.classList.contains('active')) closeDrawer();
            }
        });
    });

    // Auto load recommendations on dashboard page
    if ((window.location.pathname.includes('dashboard') || window.location.pathname.includes('index')) && isLoggedIn()) {
        setTimeout(getRecommendations, 1500);
    }
});