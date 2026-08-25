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
// rule 5 only for readers who asked for less motion — the people least likely
// to report it. So every page is loaded with JS off, and again with reduced
// motion forced, and the content is asserted visible in both.
//
// Two things this script learned the hard way, kept here so the next person
// does not repeat them:
//
//   waitUntil:'networkidle' hangs forever behind an egress proxy, because the
//   Google Fonts request never settles. External requests are aborted and the
//   page is judged on DOM readiness plus a short settle instead.
//
//   With JS on and motion enabled, most [data-reveal] blocks are SUPPOSED to be
//   hidden — they animate in on scroll. Counting them without scrolling reports
//   37/40 "hidden" on the homepage and looks alarming. That is the motion system
//   working. The scroll pass below confirms they resolve, and it is the only
//   honest way to check that lane.

const { chromium } = require('playwright');

const EXE = process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const BASE = process.env.BASE || 'http://127.0.0.1:8099';
const PAGES = ['/', '/media-kit.html', '/work/', '/privacy/', '/404.html',
  '/insights/', '/insights/articles/', '/insights/clarity-before-content/',
  '/insights/podcast/', '/insights/research-notes/', '/insights/resources/',
  '/insights/resources/trust-first-content-scorecard/',
  '/insights/the-trust-files/', '/insights/the-trust-files/trust-is-not-a-vibe/'];

const findings = [];
const add = (sev, page, msg) => findings.push({ sev, page, msg });

async function context(browser, opts) {
  const ctx = await browser.newContext(opts);
  ctx.setDefaultTimeout(8000);
  ctx.setDefaultNavigationTimeout(8000);
  // External hosts stall behind a proxy and are irrelevant to every check here.
  await ctx.route('**/*', r =>
    r.request().url().startsWith(BASE) ? r.continue() : r.abort());
  return ctx;
}

async function open(page, path) {
  await page.goto(BASE + path, { waitUntil: 'commit' });
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(450);
}

const revealState = () => {
  let hidden = 0, total = 0;
  document.querySelectorAll('[data-reveal]').forEach(el => {
    total++;
    if (parseFloat(getComputedStyle(el).opacity) < 0.9) hidden++;
  });
  return { hidden, total,
    text: document.body.innerText.trim().length,
    ov: document.documentElement.scrollWidth - document.documentElement.clientWidth };
};

(async () => {
  const browser = await chromium.launch({ executablePath: EXE });
  const phase = n => console.log(`[${new Date().toISOString().slice(11, 19)}] ${n}`);

  // ---- rule 5: prefers-reduced-motion must resolve reveals, not hide them ----
  phase('1/4  rule 5 — prefers-reduced-motion');
  let ctx = await context(browser, { viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  let page = await ctx.newPage();
  for (const p of PAGES) {
    try {
      await open(page, p);
      const r = await page.evaluate(revealState);
      if (r.hidden) add('HIGH', p, `rule 5: ${r.hidden}/${r.total} [data-reveal] still hidden under prefers-reduced-motion`);
    } catch (e) { add('MED', p, 'reduced-motion load failed: ' + e.message.split('\n')[0].slice(0, 70)); }
  }
  await ctx.close();

  // ---- rule 4: JS off must render a static page, not a blank one ----
  phase('2/4  rule 4 — JavaScript disabled');
  ctx = await context(browser, { viewport: { width: 1280, height: 900 }, javaScriptEnabled: false });
  page = await ctx.newPage();
  for (const p of PAGES) {
    try {
      await open(page, p);
      const r = await page.evaluate(revealState);
      if (r.hidden) add('HIGH', p, `rule 4: JS off leaves ${r.hidden}/${r.total} [data-reveal] blocks hidden`);
      if (r.text < 300) add('HIGH', p, `rule 4: JS off renders only ${r.text} chars — near-blank page`);
    } catch (e) { add('MED', p, 'js-off load failed: ' + e.message.split('\n')[0].slice(0, 70)); }
  }
  await ctx.close();

  // ---- horizontal overflow: the body must never scroll sideways ----
  phase('3/4  horizontal overflow at 360px and 1280px');
  for (const vp of [{ width: 360, height: 780 }, { width: 1280, height: 900 }]) {
    ctx = await context(browser, { viewport: vp });
    page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(`${page.url()} :: ${e.message}`));
    for (const p of PAGES) {
      try {
        await open(page, p);
        const r = await page.evaluate(revealState);
        if (r.ov > 1) add('HIGH', p, `horizontal overflow at ${vp.width}px: ${r.ov}px`);
      } catch (e) { add('MED', p, `overflow check failed at ${vp.width}px: ${e.message.split('\n')[0].slice(0, 60)}`); }
    }
    errs.forEach(e => add('HIGH', e.split(' :: ')[0], 'uncaught page error: ' + e.split(' :: ')[1].slice(0, 120)));
    await ctx.close();
  }

  // ---- reveals must actually resolve when a reader scrolls ----
  phase('4/4  reveals resolve on scroll');
  ctx = await context(browser, { viewport: { width: 360, height: 780 } });
  page = await ctx.newPage();
  for (const p of ['/', '/insights/', '/work/']) {
    try {
      await open(page, p);
      await page.evaluate(async () => {
        const step = window.innerHeight * 0.8;
        for (let y = 0; y < document.body.scrollHeight; y += step) {
          window.scrollTo(0, y);
          await new Promise(r => setTimeout(r, 200));
        }
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 800));
      });
      const r = await page.evaluate(revealState);
      if (r.hidden) add('HIGH', p, `${r.hidden}/${r.total} [data-reveal] still hidden after scrolling the whole page`);
    } catch (e) { add('MED', p, 'scroll check failed: ' + e.message.split('\n')[0].slice(0, 70)); }
  }
  await ctx.close();
  await browser.close();

  const order = { HIGH: 0, MED: 1, LOW: 2 };
  findings.sort((a, b) => order[a.sev] - order[b.sev] || a.page.localeCompare(b.page));
  let cur = null;
  for (const f of findings) {
    if (f.sev !== cur) { console.log(`\n===== ${f.sev} =====`); cur = f.sev; }
    console.log(`  ${f.page}: ${f.msg}`);
  }
  console.log(`\n${PAGES.length} pages checked. ${findings.length} findings ` +
    `(${findings.filter(f => f.sev === 'HIGH').length} high, ${findings.filter(f => f.sev === 'MED').length} med).`);
  process.exit(findings.some(f => f.sev === 'HIGH') ? 1 : 0);
})();
