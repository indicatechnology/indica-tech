// =========================================================
// INDICA TECH — v2
// =========================================================

// Mobile nav
const nav = document.querySelector('.nav');
const menuBtn = document.querySelector('.menu-btn');
if (menuBtn) menuBtn.addEventListener('click', () => nav.classList.toggle('open'));
document.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));

// Smooth anchors with offset
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href');
    if (id.length < 2) return;
    const t = document.querySelector(id);
    if (!t) return;
    e.preventDefault();
    const y = t.getBoundingClientRect().top + window.pageYOffset - 72;
    window.scrollTo({ top: y, behavior: 'smooth' });
  });
});

// Reveal on scroll
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// FAQ
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  const a = item.querySelector('.faq-a');
  q.addEventListener('click', () => {
    const open = item.classList.toggle('open');
    a.style.maxHeight = open ? a.scrollHeight + 'px' : '0';
  });
});

// Terminal animation
(function terminal() {
  const body = document.querySelector('.terminal-body');
  if (!body) return;

  const lines = [
    { t: 400, html: '<span class="prompt">$</span> <span class="cmd">indica audit --target=your-ai-stack</span>' },
    { t: 700, html: '<span class="out">scanning production readiness...</span>' },
    { t: 1200, html: '<span class="out">[<span class="fail">✗</span>] retry logic          <span class="fail">missing</span></span>' },
    { t: 1500, html: '<span class="out">[<span class="fail">✗</span>] eval harness         <span class="fail">not found</span></span>' },
    { t: 1800, html: '<span class="out">[<span class="warn">!</span>] observability       <span class="warn">partial</span></span>' },
    { t: 2100, html: '<span class="out">[<span class="fail">✗</span>] cost guardrails     <span class="fail">disabled</span></span>' },
    { t: 2400, html: '<span class="out">[<span class="warn">!</span>] prompt versioning   <span class="warn">manual</span></span>' },
    { t: 2700, html: '<span class="out">[<span class="ok">✓</span>] vector store        <span class="ok">ok</span></span>' },
    { t: 3100, html: '<br><span class="out">verdict:</span> <span class="fail">not production-ready</span>' },
    { t: 3400, html: '<span class="out">ship risk:</span> <span class="warn">high</span> &nbsp;&nbsp; eta to prod: <span class="warn">2-4 weeks</span>' },
    { t: 3900, html: '<br><span class="prompt">$</span> <span class="cmd">contact --reason="make this real"</span>' },
    { t: 4300, html: '<span class="ok">→ booking link opened</span>' },
  ];

  const start = () => {
    body.innerHTML = '';
    lines.forEach(l => {
      setTimeout(() => {
        const el = document.createElement('span');
        el.className = 'term-line';
        el.innerHTML = l.html;
        body.appendChild(el);
        body.appendChild(document.createElement('br'));
      }, l.t);
    });
    setTimeout(() => {
      const c = document.createElement('span');
      c.className = 'term-cursor';
      body.appendChild(c);
    }, 4400);
  };

  // Start when visible
  const o = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { start(); o.disconnect(); } });
  }, { threshold: 0.3 });
  o.observe(body);
})();

// Year
document.querySelectorAll('.year').forEach(el => { el.textContent = new Date().getFullYear(); });

// =========================================================
// REGIONAL PRICING
// The region is already stamped on <html> by the inline script in
// <head> (before first paint). This only handles the things that
// have to happen after the DOM exists: the switch, the budget
// <option> text, and the London clock.
// =========================================================
(function region() {
  const REGIONS = ['uk', 'us', 'eu'];
  const CUR = { uk: 'gbp', us: 'usd', eu: 'eur' };
  const root = document.documentElement;

  const current = () => {
    const r = root.getAttribute('data-region');
    return REGIONS.indexOf(r) > -1 ? r : 'uk';
  };

  // Budget bands carry their currency in the submitted value, so a
  // lead's answer is unambiguous in the inbox.
  const syncBudget = (r) => {
    const key = CUR[r];
    document.querySelectorAll('#budget option[data-' + key + ']').forEach(opt => {
      const label = opt.getAttribute('data-' + key);
      if (label) { opt.textContent = label; opt.value = label; }
    });
  };

  const syncSwitch = (r) => {
    document.querySelectorAll('[data-region-set]').forEach(btn => {
      btn.setAttribute('aria-pressed', String(btn.dataset.regionSet === r));
    });
  };

  const apply = (r, persist) => {
    root.setAttribute('data-region', r);
    syncSwitch(r);
    syncBudget(r);
    if (!persist) return;
    try { localStorage.setItem('indica_region', r); } catch (e) { /* storage blocked */ }
    // Keep ?region= on the URL so a copied link carries the view the
    // sender was actually looking at.
    try {
      const u = new URL(window.location.href);
      u.searchParams.set('region', r);
      history.replaceState(null, '', u);
    } catch (e) { /* older browser — the choice still applies */ }
  };

  document.querySelectorAll('[data-region-set]').forEach(btn => {
    btn.addEventListener('click', () => {
      const r = btn.dataset.regionSet;
      if (REGIONS.indexOf(r) === -1) return;
      apply(r, true);
    });
  });

  apply(current(), false);

  // London clock — turns the availability claim into something the
  // visitor can check rather than take on trust.
  const clocks = document.querySelectorAll('[data-london-clock]');
  if (clocks.length) {
    const tick = () => {
      let t;
      try {
        t = new Date().toLocaleTimeString('en-GB', {
          timeZone: 'Europe/London', hour: '2-digit', minute: '2-digit'
        });
      } catch (e) { return; }
      clocks.forEach(el => { el.textContent = t; });
    };
    tick();
    setInterval(tick, 30000);
  }
})();

// =========================================================
// REEL FACADE — load YouTube only on click
// Nothing contacts Google until the visitor asks for the video.
// The player is then loaded from youtube-nocookie.com.
// =========================================================
document.querySelectorAll('.reel-facade').forEach(btn => {
  btn.addEventListener('click', () => {
    const id = btn.dataset.yt;
    if (!id) return;

    const frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
                '?autoplay=1&rel=0';
    frame.title = btn.querySelector('.reel-facade-title').textContent;
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';

    btn.replaceWith(frame);
  });
});
