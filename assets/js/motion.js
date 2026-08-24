/* ==========================================================================
   SKLARZ CREATIVE — MOTION SYSTEM
   --------------------------------------------------------------------------
   One unified animation layer for the whole site.

   Principles this file enforces:
     · One IntersectionObserver and one rAF loop. Never a scroll listener that
       does layout work — everything reads cached geometry.
     · Motion is a reward for scrolling, not a tax on it. Reveals fire once and
       then unobserve themselves.
     · Reduced motion is honoured by skipping the choreography entirely, never
       by leaving content in a hidden state.
     · If this file fails to load, the CSS `.js` scope means the site renders
       fully visible and static. Motion is strictly additive.
   ========================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  function on(el, ev, fn, opt) { if (el) el.addEventListener(ev, fn, opt || false); }
  function all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ====================================================================== 1
     HEADER
     Frosts once the page leaves the hero. Hides on scroll-down past a
     threshold and returns on scroll-up, so long reading passages stay clean.
     ---------------------------------------------------------------------- */
  var head = document.querySelector('.site-head');
  var lastY = window.scrollY;
  var headHidden = false;

  function updateHead(y) {
    if (!head) return;

    var stuck = y > 40;
    head.classList.toggle('is-stuck', stuck);

    // Never hide while the mobile menu is open or near the top of the page.
    if (root.classList.contains('nav-open') || y < 240) {
      if (headHidden) { head.classList.remove('is-hidden'); headHidden = false; }
      return;
    }
    var delta = y - lastY;
    if (delta > 6 && !headHidden) { head.classList.add('is-hidden'); headHidden = true; }
    else if (delta < -6 && headHidden) { head.classList.remove('is-hidden'); headHidden = false; }
  }

  /* ====================================================================== 2
     MOBILE NAVIGATION
     ---------------------------------------------------------------------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');

  function setNav(open) {
    root.classList.toggle('nav-open', open);
    if (toggle) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    }
    // Lock the page behind the overlay without losing scroll position.
    document.body.style.overflow = open ? 'hidden' : '';
    if (open && nav) {
      // The overlay is visibility:hidden until the class lands, and focus() on
      // a not-yet-visible element is silently dropped. Force a style flush so
      // the links are focusable before we reach for them.
      void nav.offsetWidth;
      var first = nav.querySelector('a, button');
      if (first) first.focus({ preventScroll: true });
    }
  }

  on(toggle, 'click', function () {
    setNav(!root.classList.contains('nav-open'));
  });

  // Close on link activation, on Escape, and whenever we grow past the
  // breakpoint where the overlay stops existing.
  all('.nav a').forEach(function (a) {
    on(a, 'click', function () { setNav(false); });
  });

  on(document, 'keydown', function (e) {
    if (e.key === 'Escape' && root.classList.contains('nav-open')) {
      setNav(false);
      if (toggle) toggle.focus({ preventScroll: true });
    }
  });

  var wide = window.matchMedia('(min-width: 961px)');
  function onWide() { if (wide.matches && root.classList.contains('nav-open')) setNav(false); }
  if (wide.addEventListener) wide.addEventListener('change', onWide);
  else if (wide.addListener) wide.addListener(onWide);

  /* ====================================================================== 3
     LINE REVEALS
     The hero headline is authored as explicit .line > .line-i pairs so no
     measuring is needed and nothing can mis-split. Once a line has played we
     release its overflow clip, so later reflow can never crop the text.
     ---------------------------------------------------------------------- */
  function playLines(scope) {
    var lines = all('.line', scope);
    lines.forEach(function (line, i) {
      var inner = line.querySelector('.line-i');
      if (!inner) return;
      if (reduced.matches) { line.classList.add('is-done'); inner.classList.add('is-in'); return; }
      inner.style.setProperty('--line-delay', (i * 95 + 120) + 'ms');
      requestAnimationFrame(function () { inner.classList.add('is-in'); });
      // Release the clip after the longest possible transition.
      window.setTimeout(function () { line.classList.add('is-done'); }, i * 95 + 120 + 1400);
    });
  }

  /* ====================================================================== 4
     SCROLL REVEALS + COUNTERS
     A single observer for everything, unobserving on first entry.
     ---------------------------------------------------------------------- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target)) return;
    var suffix = el.getAttribute('data-count-suffix') || '';
    if (reduced.matches) { el.textContent = target + suffix; return; }

    var dur = 1400, t0 = 0;
    function step(now) {
      if (!t0) t0 = now;
      var p = Math.min(1, (now - t0) / dur);
      var eased = 1 - Math.pow(1 - p, 3);          // cubic out, matches --ease-out
      var value = target % 1 ? (target * eased).toFixed(1) : Math.round(target * eased);
      el.textContent = value + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  var revealTargets = all('[data-reveal]');
  var counters = all('[data-count]');

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);

        if (el.hasAttribute('data-reveal')) {
          // Stagger siblings that share a group, so grids cascade.
          var group = el.getAttribute('data-reveal-group');
          if (group) {
            var idx = parseInt(el.getAttribute('data-reveal-index') || '0', 10);
            el.style.setProperty('--reveal-delay', (idx * 90) + 'ms');
          }
          el.classList.add('is-in');
          if (el.querySelector('.line')) playLines(el);
        }
        if (el.hasAttribute('data-count')) countUp(el);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.06 });

    revealTargets.forEach(function (el) { io.observe(el); });
    counters.forEach(function (el) { io.observe(el); });
  } else {
    // No observer support: show everything immediately.
    revealTargets.forEach(function (el) { el.classList.add('is-in'); });
    counters.forEach(function (el) {
      el.textContent = el.getAttribute('data-count') + (el.getAttribute('data-count-suffix') || '');
    });
    all('.line').forEach(function (l) { l.classList.add('is-done'); });
    all('.line-i').forEach(function (l) { l.classList.add('is-in'); });
  }

  /* ====================================================================== 5
     LOAD CHOREOGRAPHY
     Hero content plays on load rather than on intersection, in a fixed order:
     header → headline lines → lede → actions → aside → cue.
     ---------------------------------------------------------------------- */
  function playHero() {
    var hero = document.querySelector('.hero');
    if (!hero) return;

    all('[data-hero-step]', hero).forEach(function (el) {
      var step = parseInt(el.getAttribute('data-hero-step'), 10) || 0;
      el.style.setProperty('--reveal-delay', reduced.matches ? '0ms' : (step * 130 + 260) + 'ms');
      el.classList.add('is-in');
    });

    var h1 = hero.querySelector('[data-lines]');
    if (h1) playLines(h1);
  }

  // Wait for the brand faces so display type never reflows mid-reveal, but
  // never wait longer than 900ms on a slow font CDN.
  var started = false;
  function begin() {
    if (started) return;
    started = true;
    root.classList.add('is-loaded');
    playHero();
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(begin);
    window.setTimeout(begin, 900);
  } else {
    begin();
  }

  /* ====================================================================== 6
     PARALLAX + RAIL PROGRESS
     One rAF loop, started only when there is work and motion is allowed.
     Geometry is cached and refreshed on resize, never read per frame.
     ---------------------------------------------------------------------- */
  var parallaxEls = all('[data-parallax]');
  var rails = all('[data-rail]');
  var cache = [];

  function measure() {
    cache = parallaxEls.map(function (el) {
      var rect = el.getBoundingClientRect();
      return {
        el: el,
        top: rect.top + window.scrollY,
        height: rect.height,
        speed: parseFloat(el.getAttribute('data-parallax')) || 0.08
      };
    });
    rails.forEach(function (r) {
      r._top = r.getBoundingClientRect().top + window.scrollY;
      r._height = r.offsetHeight;
    });
  }

  var ticking = false;
  var vh = window.innerHeight;

  function frame() {
    ticking = false;
    var y = window.scrollY;

    updateHead(y);
    lastY = y;

    if (!reduced.matches) {
      for (var i = 0; i < cache.length; i++) {
        var it = cache[i];
        // Progress of this element through the viewport, -1..1
        var mid = it.top + it.height / 2;
        var p = (y + vh / 2 - mid) / (vh + it.height);
        // Clamp travel so nothing ever detaches from its layout position.
        var shift = Math.max(-90, Math.min(90, p * it.speed * vh));
        it.el.style.transform = 'translate3d(0,' + shift.toFixed(2) + 'px,0)';
      }
      for (var j = 0; j < rails.length; j++) {
        var r = rails[j];
        var prog = (y + vh * 0.85 - r._top) / (r._height + vh * 0.35);
        r.style.setProperty('--rail-progress', Math.max(0, Math.min(1, prog)).toFixed(3));
      }
    }
  }

  function request() {
    if (!ticking) { ticking = true; requestAnimationFrame(frame); }
  }

  on(window, 'scroll', request, { passive: true });
  on(window, 'resize', function () {
    vh = window.innerHeight;
    measure();
    request();
  }, { passive: true });

  measure();
  request();
  // Late-loading images change geometry; remeasure once everything settles.
  on(window, 'load', function () { measure(); request(); });

  /* ====================================================================== 7
     CURSOR
     A single gold ring, damped toward the pointer, widening over anything
     interactive. Fine pointers only — it would be invisible noise on touch.
     ---------------------------------------------------------------------- */
  if (finePointer.matches && !reduced.matches) {
    var ring = document.createElement('div');
    ring.className = 'cursor-ring';
    ring.setAttribute('aria-hidden', 'true');
    document.body.appendChild(ring);

    var cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    var tx = cx, ty = cy, live = false, cursorRaf = 0;

    function cursorLoop() {
      cursorRaf = requestAnimationFrame(cursorLoop);
      cx += (tx - cx) * 0.16;
      cy += (ty - cy) * 0.16;
      ring.style.transform = 'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0)';
    }

    on(document, 'pointermove', function (e) {
      if (e.pointerType && e.pointerType !== 'mouse') return;
      tx = e.clientX; ty = e.clientY;
      if (!live) {
        live = true;
        ring.classList.add('is-live');
        cursorLoop();
      }
      var hot = e.target && e.target.closest &&
                e.target.closest('a, button, .card, [data-cursor-hot]');
      ring.classList.toggle('is-hot', !!hot);
    }, { passive: true });

    on(document, 'pointerleave', function () { ring.classList.remove('is-live'); });
    on(document, 'pointerenter', function () { if (live) ring.classList.add('is-live'); });
    on(document, 'visibilitychange', function () {
      if (document.hidden && cursorRaf) { cancelAnimationFrame(cursorRaf); cursorRaf = 0; live = false; ring.classList.remove('is-live'); }
    });
  }

  /* ====================================================================== 8
     PAGE TRANSITION
     A navy curtain rises before an internal navigation and falls away on
     arrival. Wrapped so any failure falls through to a normal click.
     ---------------------------------------------------------------------- */
  if (!reduced.matches) {
    var curtain = document.createElement('div');
    curtain.className = 'curtain';
    curtain.setAttribute('aria-hidden', 'true');
    document.body.appendChild(curtain);

    on(document, 'click', function (e) {
      try {
        if (e.defaultPrevented || e.button !== 0) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

        var a = e.target.closest && e.target.closest('a[href]');
        if (!a) return;
        if (a.target && a.target !== '_self') return;
        if (a.hasAttribute('download')) return;

        var url = new URL(a.href, location.href);
        if (url.origin !== location.origin) return;
        // Same-page anchors keep native smooth scrolling.
        if (url.pathname === location.pathname && url.hash) return;
        if (url.href === location.href) return;

        e.preventDefault();
        root.classList.add('is-leaving');
        var done = false;
        function go() { if (!done) { done = true; location.href = url.href; } }
        window.setTimeout(go, 420);
      } catch (err) {
        /* Any failure here must not block navigation — let the click proceed. */
      }
    });

    // Returning via the back button restores a cached page mid-transition.
    on(window, 'pageshow', function (e) {
      if (e.persisted) root.classList.remove('is-leaving');
    });
  }

  /* ====================================================================== 9
     CONSENT-GATED ANALYTICS
     Google Analytics is never requested until the visitor actively allows it.
     The small public API lets individual tools report meaningful completions
     without coupling those tools to Google.
     ---------------------------------------------------------------------- */
  var ANALYTICS_ID = 'G-15GX6KDX09';
  var ANALYTICS_CONSENT_KEY = 'sc_analytics_consent_v1';
  var analyticsConsent = readAnalyticsChoice();

  function readAnalyticsChoice() {
    try { return window.localStorage.getItem(ANALYTICS_CONSENT_KEY); }
    catch (err) { return null; }
  }

  function rememberAnalyticsChoice(choice) {
    analyticsConsent = choice;
    try { window.localStorage.setItem(ANALYTICS_CONSENT_KEY, choice); }
    catch (err) { /* The in-memory choice still applies for this page. */ }
  }

  function loadGoogleAnalytics() {
    if (document.querySelector('script[data-sc-analytics]')) return;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', ANALYTICS_ID, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_flags: 'SameSite=Lax;Secure'
    });

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ANALYTICS_ID);
    script.setAttribute('data-sc-analytics', '');
    document.head.appendChild(script);
  }

  window.scTrack = function (eventName, details) {
    if (analyticsConsent !== 'granted') return;
    loadGoogleAnalytics();
    window.gtag('event', eventName, details || {});
  };

  function clearAnalyticsCookies() {
    var names = document.cookie.split(';').map(function (part) {
      return part.split('=')[0].trim();
    }).filter(function (name) {
      return name === '_gid' || name.indexOf('_ga') === 0;
    });
    var domains = ['', location.hostname, '.sklarzcreative.com'];

    names.forEach(function (name) {
      domains.forEach(function (domain) {
        var suffix = domain ? '; domain=' + domain : '';
        document.cookie = name + '=; Max-Age=0; path=/' + suffix + '; SameSite=Lax; Secure';
      });
    });
  }

  function addAnalyticsPromptStyles() {
    if (document.getElementById('sc-analytics-consent-styles')) return;
    var style = document.createElement('style');
    style.id = 'sc-analytics-consent-styles';
    style.textContent = [
      '.sc-analytics-consent{position:fixed;z-index:9999;right:1rem;bottom:1rem;left:1rem;max-width:42rem;margin-left:auto;padding:1.15rem 1.2rem;background:#10243b;color:#fff;border:1px solid rgba(255,255,255,.18);border-radius:.45rem;box-shadow:0 1rem 3rem rgba(0,0,0,.28);font:inherit}',
      '.sc-analytics-consent p{margin:0;line-height:1.55}',
      '.sc-analytics-consent a{color:#f1cc73;text-underline-offset:.18em}',
      '.sc-analytics-consent__actions{display:flex;flex-wrap:wrap;gap:.65rem;margin-top:1rem}',
      '.sc-analytics-consent button{appearance:none;border:1px solid rgba(255,255,255,.55);border-radius:999px;padding:.65rem 1rem;background:transparent;color:#fff;font:inherit;font-weight:700;cursor:pointer}',
      '.sc-analytics-consent button[data-analytics-choice="granted"]{border-color:#f1cc73;background:#f1cc73;color:#10243b}',
      '.sc-analytics-consent button:focus-visible{outline:3px solid #fff;outline-offset:3px}',
      '@media (max-width:36rem){.sc-analytics-consent{right:.65rem;bottom:.65rem;left:.65rem}.sc-analytics-consent__actions button{flex:1 1 auto}}'
    ].join('');
    document.head.appendChild(style);
  }

  function showAnalyticsPrompt() {
    if (!document.body || document.querySelector('.sc-analytics-consent')) return;
    addAnalyticsPromptStyles();

    var prompt = document.createElement('aside');
    prompt.className = 'sc-analytics-consent';
    prompt.setAttribute('role', 'dialog');
    prompt.setAttribute('aria-labelledby', 'sc-analytics-consent-title');
    prompt.innerHTML =
      '<p id="sc-analytics-consent-title"><strong>May we measure what helps?</strong> ' +
      'Optional Google Analytics helps Sklarz Creative understand visits and improve the site. ' +
      'It stays off unless you allow it. <a href="/privacy/">Privacy details</a></p>' +
      '<div class="sc-analytics-consent__actions">' +
      '<button type="button" data-analytics-choice="denied">No thanks</button>' +
      '<button type="button" data-analytics-choice="granted">Allow analytics</button>' +
      '</div>';
    document.body.appendChild(prompt);

    on(prompt, 'click', function (e) {
      var button = e.target.closest && e.target.closest('[data-analytics-choice]');
      if (!button) return;
      var choice = button.getAttribute('data-analytics-choice');
      var wasLoaded = !!document.querySelector('script[data-sc-analytics]');
      rememberAnalyticsChoice(choice);

      if (choice === 'granted') {
        loadGoogleAnalytics();
      } else {
        if (typeof window.gtag === 'function') {
          window.gtag('consent', 'update', { analytics_storage: 'denied' });
        }
        clearAnalyticsCookies();
      }

      prompt.remove();
      if (choice === 'denied' && wasLoaded) {
        window.setTimeout(function () { location.reload(); }, 80);
      }
    });
  }

  on(document, 'click', function (e) {
    var control = e.target.closest && e.target.closest('[data-analytics-preferences]');
    if (!control) return;
    e.preventDefault();
    analyticsConsent = null;
    try { window.localStorage.removeItem(ANALYTICS_CONSENT_KEY); }
    catch (err) { /* The prompt still opens for this page. */ }
    showAnalyticsPrompt();
  });

  on(document, 'click', function (e) {
    var link = e.target.closest && e.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    var eventName = '';

    if (/^mailto:/i.test(href)) {
      eventName = 'email_click';
    } else if (/calendly\.com/i.test(href)) {
      eventName = 'booking_click';
    }
    if (!eventName) return;

    window.scTrack(eventName, {
      link_url: link.href,
      link_text: (link.textContent || '').trim().slice(0, 100),
      page_path: location.pathname
    });
  });

  if (analyticsConsent === 'granted') {
    loadGoogleAnalytics();
  } else if (analyticsConsent !== 'denied') {
    if (document.body) showAnalyticsPrompt();
    else on(document, 'DOMContentLoaded', showAnalyticsPrompt);
  }

  var queuedAnalyticsEvents = window.scPendingEvents || [];
  window.scPendingEvents = [];
  queuedAnalyticsEvents.forEach(function (item) {
    if (item && item.name) window.scTrack(item.name, item.details);
  });

})();
