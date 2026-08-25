// browser-audit.js — the site checks that need a real browser.
//
//   npx --yes http-server -p 8099 -c-1 .      # in one terminal
//   npm install playwright && node tools/browser-audit.js
//
// Static analysis cannot see two of the repository's load-bearing rules, and
// they are the two that fail silently rather than visibly:
//
//   rule 4  hidden animation start-states stay scoped to html.js, so a
//           JavaScript failure yields a static page rather than a blank one
//   rule 5  prefers-reduced-motion resolves reveals to their final state,
//           never leaves them hidden
//
// Both look perfect in normal conditions. Rule 4 breaks only with JS disabled;
// rule 5 only for the readers who asked for less motion — the people least
// likely to report it. So they are checked here by actually loading every page
// with JS off, and again with reduced motion forced, and asserting the content
// is visible in both.
//
// Also: console errors, and horizontal overflow at 360px and 1280px. The body
// must never scroll sideways.
//
// Progress is printed per phase, because the whole sweep is ~56 page loads.

const { chromium } = require('playwright');
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const BASE = 'http://127.0.0.1:8099';
const PAGES = ['/', '/media-kit.html', '/work/', '/privacy/', '/404.html',
  '/insights/', '/insights/articles/', '/insights/clarity-before-content/',
  '/insights/podcast/', '/insights/research-notes/', '/insights/resources/',
  '/insights/resources/trust-first-content-scorecard/',
  '/insights/the-trust-files/', '/insights/the-trust-files/trust-is-not-a-vibe/'];

const findings = [];
const add = (sev, page, msg) => findings.push({ sev, page, msg });

(async () => {
  const browser = await chromium.launch({ executablePath: EXE });
  const phase = n => console.log(`[${new Date().toISOString().slice(11, 19)}] ${n}`);

  phase('1/4 console errors + desktop overflow');
  // ---------- 1. console errors + horizontal scroll + reveal state ----------
  for (const path of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    errs.forEach(e => add('HIGH', path, 'console error: ' + e.slice(0, 140)));

    // horizontal overflow at desktop
    const ov = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (ov > 1) add('MED', path, `horizontal overflow at 1280px: ${ov}px`);
    await ctx.close();
  }

  phase('2/4 mobile overflow at 360px');
  // ---------- 2. mobile horizontal scroll ----------
  for (const path of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await page.waitForTimeout(400);
    const ov = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (ov > 1) add('HIGH', path, `horizontal overflow at 360px: ${ov}px — body must never scroll sideways`);
    await ctx.close();
  }

  phase('3/4 rule 5 — prefers-reduced-motion');
  // ---------- 3. rule 5: prefers-reduced-motion resolves reveals ----------
  for (const path of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    const hidden = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('[data-reveal]').forEach(el => {
        const cs = getComputedStyle(el);
        if (parseFloat(cs.opacity) < 0.9) out.push((el.tagName + '.' + el.className).slice(0, 60));
      });
      return out;
    });
    hidden.forEach(h => add('HIGH', path, `rule 5: [data-reveal] still hidden under prefers-reduced-motion: ${h}`));
    await ctx.close();
  }

  phase('4/4 rule 4 — JavaScript disabled');
  // ---------- 4. rule 4: JS off must render content, not a blank page ----------
  for (const path of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, javaScriptEnabled: false });
    const page = await ctx.newPage();
    await page.goto(BASE + path, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const vis = await page.evaluate(() => {
      let shown = 0, total = 0;
      document.querySelectorAll('[data-reveal]').forEach(el => {
        total++;
        if (parseFloat(getComputedStyle(el).opacity) >= 0.9) shown++;
      });
      return { shown, total, text: document.body.innerText.trim().length };
    });
    if (vis.total && vis.shown < vis.total)
      add('HIGH', path, `rule 4: JS off leaves ${vis.total - vis.shown}/${vis.total} [data-reveal] blocks hidden`);
    if (vis.text < 400)
      add('HIGH', path, `rule 4: JS off renders only ${vis.text} chars of text — near-blank page`);
    await ctx.close();
  }

  await browser.close();

  const order = { HIGH: 0, MED: 1, LOW: 2 };
  findings.sort((a, b) => order[a.sev] - order[b.sev] || a.page.localeCompare(b.page));
  let cur = null;
  for (const f of findings) {
    if (f.sev !== cur) { console.log(`\n===== ${f.sev} =====`); cur = f.sev; }
    console.log(`  ${f.page}: ${f.msg}`);
  }
  console.log(`\n${PAGES.length} pages × 4 checks. ${findings.length} findings ` +
    `(${findings.filter(f => f.sev === 'HIGH').length} high, ${findings.filter(f => f.sev === 'MED').length} med).`);
})();
