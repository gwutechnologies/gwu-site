// ── LOADER ──────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('hidden');
  }, 2000);
});

// ── CUSTOM CURSOR ─────────────────────────────────────────────────────────────
const cursor = document.getElementById('cursor');
const follower = document.getElementById('cursorFollower');
if (cursor && follower) {
  let mouseX = 0, mouseY = 0, followerX = 0, followerY = 0;
  document.addEventListener('mousemove', e => {
    mouseX = e.clientX; mouseY = e.clientY;
    cursor.style.left = mouseX + 'px'; cursor.style.top = mouseY + 'px';
  });
  (function animateFollower() {
    followerX += (mouseX - followerX) * 0.12;
    followerY += (mouseY - followerY) * 0.12;
    follower.style.left = followerX + 'px'; follower.style.top = followerY + 'px';
    requestAnimationFrame(animateFollower);
  })();
  document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
    el.addEventListener('mouseenter', () => {
      cursor.style.transform = 'translate(-50%,-50%) scale(2.5)';
      cursor.style.background = 'rgba(255,154,0,0.5)';
      follower.style.opacity = '0';
    });
    el.addEventListener('mouseleave', () => {
      cursor.style.transform = 'translate(-50%,-50%) scale(1)';
      cursor.style.background = '#FF9A00';
      follower.style.opacity = '0.5';
    });
  });
}

// ── NAVBAR SCROLL ─────────────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 80);
  });
}

// ── SCROLL REVEAL ─────────────────────────────────────────────────────────────
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  revealEls.forEach(el => observer.observe(el));
}

// ── SMOOTH SCROLL NAV ─────────────────────────────────────────────────────────
document.querySelectorAll('a[href^="/#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    const id = href.split('#')[1];
    if (window.location.pathname === '/' || window.location.pathname === '') {
      e.preventDefault();
      const target = document.getElementById(id);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href === '#' || href.startsWith('/#')) return;
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// ── CONTACT FORM ──────────────────────────────────────────────────────────────
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    const successEl = document.getElementById('form-success');
    const errorEl = document.getElementById('form-error');
    successEl.style.display = 'none';
    errorEl.style.display = 'none';
    btn.disabled = true;
    btn.innerHTML = '<span style="display:inline-block;animation:spin 0.8s linear infinite;border:2px solid white;border-top-color:transparent;width:16px;height:16px;border-radius:50%"></span> Sending...';

    const data = {};
    new FormData(this).forEach((v, k) => data[k] = v);

    try {
      const res = await fetch('/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const result = await res.json();
      if (result.success) {
        successEl.textContent = result.message;
        successEl.style.display = 'block';
        this.reset();
        successEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        errorEl.textContent = result.error || 'Something went wrong. Please try again.';
        errorEl.style.display = 'block';
      }
    } catch (err) {
      errorEl.textContent = 'Network error. Please check your connection and try again.';
      errorEl.style.display = 'block';
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Send Message <span>→</span>';
    }
  });
}

// ── VIEWPORT-GATED ANIMATIONS (pause offscreen for perf) ────────────────────────
const animEls = document.querySelectorAll('.js-anim');
if (animEls.length && 'IntersectionObserver' in window) {
  const animObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => e.target.classList.toggle('anim-run', e.isIntersecting));
  }, { threshold: 0.2 });
  animEls.forEach(el => animObserver.observe(el));
}

// ── INSPECTION SCENE COUNTERS ──────────────────────────────────────────────────
// Counts are driven by the badge animations themselves (one 'animationiteration'
// per part pass), so the tally always matches what's visibly happening on the belt.
const statInspected = document.getElementById('statInspected');
const statOk = document.getElementById('statOk');
const statNok = document.getElementById('statNok');
if (statInspected && statOk && statNok) {
  let inspected = 0, ok = 0, nok = 0;
  document.querySelectorAll('.belt-track .part-badge').forEach(badge => {
    badge.addEventListener('animationiteration', () => {
      inspected++;
      if (badge.classList.contains('badge-ok')) ok++; else nok++;
      statInspected.textContent = inspected;
      statOk.textContent = ok;
      statNok.textContent = nok;
    });
  });
}

// ── SPIN KEYFRAME ─────────────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = '@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}';
document.head.appendChild(style);
