/**
 * Load Playwright, or say clearly that it is not available.
 *
 * The harness must degrade honestly. If Chromium cannot launch, the static
 * suite still runs and the browser suites are reported as `skipped` with the
 * reason — never as passing, and never as failing either, because "we could
 * not look" is not the same as "it is broken".
 */

export async function loadChromium() {
  let mod;
  for (const name of ['playwright', '@playwright/test', 'playwright-core']) {
    try {
      mod = await import(name);
      break;
    } catch { /* try the next one */ }
  }
  if (!mod?.chromium) {
    return {
      ok: false,
      reason:
        'Playwright is not installed. From automation/: `npm ci`. ' +
        'Chromium itself is not downloaded by this harness — set PLAYWRIGHT_BROWSERS_PATH ' +
        'or run `npx playwright install chromium` once.'
    };
  }
  try {
    const browser = await mod.chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
    return { ok: true, browser, version: browser.version() };
  } catch (err) {
    return { ok: false, reason: `Chromium failed to launch: ${err.message.split('\n')[0]}` };
  }
}

export const VIEWPORTS = Object.freeze([
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 834, height: 1112 },
  { name: 'mobile', width: 390, height: 844 }
]);

/**
 * Load a page and settle it: scroll the whole document so every
 * IntersectionObserver reveal has fired and every in-viewport image has been
 * asked to load, then return to the top.
 *
 * Measuring before this happens produced two classes of false result in the
 * previous manual QA — reveals still hidden, and images reported as broken
 * when they had simply never been requested.
 */
export async function settle(page) {
  await page.evaluate(async () => {
    const step = Math.floor(window.innerHeight * 0.8);
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await new Promise(r => requestAnimationFrame(() => r()));
    }
    window.scrollTo(0, 0);
    await new Promise(r => setTimeout(r, 120));
  });
  // Fonts, where the environment can reach them at all. Bounded, because a
  // never-resolving fonts.ready would hang the whole suite on one page.
  await Promise.race([
    page.evaluate(() => (document.fonts ? document.fonts.ready.then(() => {}) : null)).catch(() => {}),
    new Promise(r => setTimeout(r, 1500))
  ]);
}

/** Collect console errors, page errors and failed requests for one navigation. */
export function watch(page, { ignoreHosts = [] } = {}) {
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];

  page.on('console', msg => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    /* Our own doing: blockExternalHosts aborts the Google Fonts requests, and
       Chromium logs each abort as a console error. Reporting that would be the
       harness accusing the site of a failure the harness caused — the fastest
       way to make a QA tool worth ignoring. The fact that fonts were blocked
       is recorded once, as information, by the runner. */
    if (text.includes('ERR_BLOCKED_BY_CLIENT')) return;
    consoleErrors.push(text);
  });
  page.on('pageerror', err => pageErrors.push(err.message));
  page.on('requestfailed', req => {
    const url = req.url();
    // A blocked font CDN is a property of the sandbox, not of the site.
    if (ignoreHosts.some(h => url.includes(h))) return;
    failedRequests.push(`${url} — ${req.failure()?.errorText ?? 'unknown'}`);
  });

  return { consoleErrors, pageErrors, failedRequests };
}

/** Hosts this environment may not be able to reach. Reported as info, not failure. */
export const EXTERNAL_HOSTS = Object.freeze(['fonts.googleapis.com', 'fonts.gstatic.com']);

/**
 * Abort every request to a third-party host before it is made.
 *
 * WHY, AND WHAT IT COSTS
 * The page links Google Fonts. In a sandboxed or offline environment that
 * request does not fail fast — an egress proxy can hold it open until the
 * navigation timeout, which turns a two-second page load into twenty and makes
 * the suite unusable. Aborting up front makes every load deterministic.
 *
 * The cost is real and is stated rather than glossed: WITH FONTS BLOCKED, THE
 * DISPLAY TYPEFACE IS NOT WHAT A VISITOR SEES. Every measurement that depends
 * on glyph widths — text wrapping, element heights, and therefore any overflow
 * caused by a long word — is taken against the fallback stack rather than
 * against Playfair Display. An overflow finding from this harness is still a
 * real signal; a CLEAN overflow result is not proof that the real typography
 * does not overflow. Confirm typography on the live domain.
 *
 * The previous manual QA hit the same wall and recorded the same caveat.
 */
export async function blockExternalHosts(context) {
  await context.route('**/*', route => {
    const url = route.request().url();
    if (EXTERNAL_HOSTS.some(host => url.includes(host))) return route.abort('blockedbyclient');
    return route.continue();
  });
}
