/**
 * Behavioural checks — the ones that assert a rule rather than measure a value.
 *
 * These protect the load-bearing rules from the root README, which are exactly
 * the kind that decay silently: they never produce a visible error, they simply
 * stop being true one commit at a time.
 */
import { settle, watch, blockExternalHosts, EXTERNAL_HOSTS } from '../lib/browser.mjs';
import {
  CATEGORIES, STATEMENTS_PER_CATEGORY, BOUNDARY_TOTALS,
  answersForTotal, score
} from '../../lib/scorecard.mjs';

const SCORECARD_ROUTE = '/insights/resources/trust-first-content-scorecard/';

/* ------------------------------------------------------- JavaScript off ---- */

/**
 * Load-bearing rule 4: hidden animation start-states stay scoped to `html.js`,
 * so a JavaScript failure renders a static page rather than a blank one.
 * Unscope them and the page silently becomes empty for anyone whose script did
 * not run — which is a failure no error log would ever show you.
 */
async function jsDisabled({ browser, origin, contentRoutes, findings }) {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1440, height: 900 } });
  await blockExternalHosts(context);
  for (const route of contentRoutes) {
    const page = await context.newPage();
    const at = { group: 'behaviour', route, viewport: 'js-disabled' };
    try {
      await page.goto(origin + route, { waitUntil: 'domcontentloaded', timeout: 20000 });
    } catch (err) {
      findings.error('behaviour.js-off-navigation', `could not load ${route} with scripting off: ${err.message.split('\n')[0]}`, at);
      await page.close();
      continue;
    }

    let state;
    try {
      state = await page.evaluate(() => {
      /* The distinction that makes this check trustworthy.
         A stuck REVEAL shows up as opacity or visibility, because the motion
         system only ever animates transform / opacity / filter. A display:none
         is almost always DELIBERATE STATE — a print-only paragraph, a panel
         gated behind a decision, a result block that is empty until the card is
         finished. Reporting those as failures would flag correct code, and a
         tool that flags correct code stops being read. */
      const describe = el => el.tagName.toLowerCase() +
        (el.className ? `.${String(el.className).trim().split(/\s+/).slice(0, 2).join('.')}` : '') +
        (el.id ? `#${el.id}` : '');
      const stuckReveal = [];
      const deliberatelyHidden = [];
      for (const el of document.querySelectorAll('main section, main h1, main h2, main p')) {
        if (el.textContent.trim().length < 10) continue;
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || parseFloat(style.opacity) < 0.05) {
          stuckReveal.push({ el: describe(el), opacity: style.opacity, visibility: style.visibility });
        } else if (style.display === 'none') {
          deliberatelyHidden.push(describe(el));
        }
      }
      return {
        visibleTextLength: (document.querySelector('main')?.innerText ?? '').trim().length,
        stuckReveal: stuckReveal.slice(0, 12),
        stuckRevealCount: stuckReveal.length,
        deliberatelyHidden: deliberatelyHidden.slice(0, 12),
        htmlHasJsClass: document.documentElement.classList.contains('js')
      };
      });
    } catch (err) {
      findings.error('behaviour.js-off', `could not measure ${route} with scripting off: ${err.message.split('\n')[0]}`, at);
      await page.close();
      continue;
    }

    if (state.htmlHasJsClass) {
      findings.error('behaviour.js-off-class', 'html carries the "js" class with scripting off, so js-scoped hidden start-states apply and content stays hidden', at);
    }
    if (state.visibleTextLength < 200) {
      findings.error('behaviour.js-off-content', `only ${state.visibleTextLength} characters of visible text in <main> with scripting off — the page is effectively blank`, at);
    } else if (state.stuckRevealCount > 0) {
      findings.error(
        'behaviour.js-off-hidden',
        `${state.stuckRevealCount} content element(s) left transparent or visibility:hidden with scripting off: ` +
        `${state.stuckReveal.map(x => x.el).join(', ')}. Hidden animation start-states must stay scoped to html.js, ` +
        'or a script failure renders a blank page instead of a static one.',
        { ...at, evidence: state.stuckReveal }
      );
    } else {
      findings.pass('behaviour.js-off', route);
      if (state.deliberatelyHidden.length) {
        findings.info(
          'behaviour.js-off-display-none',
          `display:none with scripting off, treated as deliberate state rather than a stuck reveal: ${state.deliberatelyHidden.join(', ')}`,
          at
        );
      }
    }
    await page.close();
  }
  await context.close();
}

/* ------------------------------------------------- reduced motion --------- */

/**
 * Load-bearing rule 5: prefers-reduced-motion must resolve reveals to their
 * FINAL state, never leave them hidden. Getting this wrong turns an
 * accessibility preference into an empty page.
 */
async function reducedMotion({ browser, origin, contentRoutes, findings }) {
  const context = await browser.newContext({
    reducedMotion: 'reduce',
    viewport: { width: 1440, height: 900 }
  });
  await blockExternalHosts(context);
  for (const route of contentRoutes) {
    const page = await context.newPage();
    const at = { group: 'behaviour', route, viewport: 'reduced-motion' };
    try {
      await page.goto(origin + route, { waitUntil: 'domcontentloaded', timeout: 20000 });
    } catch (err) {
      findings.error('behaviour.reduced-motion-navigation', `could not load ${route}: ${err.message.split('\n')[0]}`, at);
      await page.close();
      continue;
    }
    // Deliberately do NOT scroll first: the point is that reveals resolve
    // without needing the scroll that would normally trigger them.
    let hidden;
    try {
      hidden = await page.evaluate(() => {
      /* Same distinction as the scripting-off check: a stuck reveal is an
         opacity or visibility, because that is all the motion system animates.
         A display:none is deliberate state and is not a reveal that failed to
         resolve. */
      const out = [];
      for (const el of document.querySelectorAll('main section, main h1, main h2, main p, main li')) {
        if (el.textContent.trim().length < 10) continue;
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || parseFloat(style.opacity) < 0.05) {
          out.push({
            tag: el.tagName.toLowerCase(),
            cls: String(el.className || '').trim().split(/\s+/).slice(0, 2).join('.'),
            id: el.id || null,
            opacity: style.opacity,
            visibility: style.visibility,
            display: style.display
          });
        }
      }
      return out;
      });
    } catch (err) {
      findings.error('behaviour.reduced-motion', `could not measure ${route} under prefers-reduced-motion: ${err.message.split('\n')[0]}`, at);
      await page.close();
      continue;
    }
    if (hidden.length) {
      findings.error(
        'behaviour.reduced-motion-hidden',
        `${hidden.length} content element(s) still hidden under prefers-reduced-motion — the preference must resolve reveals to their final state, not leave them unrevealed`,
        { ...at, evidence: hidden.slice(0, 8) }
      );
    } else findings.pass('behaviour.reduced-motion', route);
    await page.close();
  }
  await context.close();
}

/* ------------------------------------------------------ mobile navigation - */

async function mobileNav({ browser, origin, findings }) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await blockExternalHosts(context);
  const page = await context.newPage();
  const at = { group: 'behaviour', route: '/', viewport: 'mobile' };
  try {
    await page.goto(origin + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await settle(page);

    const toggle = page.locator('.nav-toggle');
    if (await toggle.count() === 0) {
      findings.error('behaviour.nav-toggle', 'no .nav-toggle on the homepage at 390px', at);
      return;
    }

    await toggle.click();
    await page.waitForTimeout(450); // the panel fades in; visibility flips discretely

    const opened = await page.evaluate(() => {
      const nav = document.querySelector('.nav');
      const toggle = document.querySelector('.nav-toggle');
      const first = nav?.querySelector('a, button');
      return {
        rootOpen: document.documentElement.classList.contains('nav-open'),
        expanded: toggle?.getAttribute('aria-expanded'),
        navVisible: nav ? getComputedStyle(nav).visibility : null,
        focusIsInNav: !!(nav && document.activeElement && nav.contains(document.activeElement)),
        focusTag: document.activeElement?.tagName?.toLowerCase() ?? null,
        firstLinkText: first?.textContent?.trim() ?? null
      };
    });

    if (!opened.rootOpen) findings.error('behaviour.nav-open', 'clicking the toggle did not open the navigation', { ...at, evidence: opened });
    if (opened.expanded !== 'true') findings.error('behaviour.nav-aria', `aria-expanded is "${opened.expanded}" after opening; a screen reader is told the menu is still closed`, at);
    if (opened.navVisible === 'hidden') {
      findings.error(
        'behaviour.nav-visibility',
        'the nav panel still computes to visibility:hidden when open. The browser silently refuses to focus a hidden element, so the menu is unusable by keyboard — this exact defect was found and fixed once before.',
        { ...at, evidence: opened }
      );
    }
    if (!opened.focusIsInNav) {
      findings.error('behaviour.nav-focus', `focus did not move into the nav panel (it is on <${opened.focusTag}>), leaving the keyboard behind a full-screen overlay`, { ...at, evidence: opened });
    } else findings.pass('behaviour.nav-focus');

    await page.keyboard.press('Escape');
    await page.waitForTimeout(450);
    const closed = await page.evaluate(() => ({
      rootOpen: document.documentElement.classList.contains('nav-open'),
      expanded: document.querySelector('.nav-toggle')?.getAttribute('aria-expanded'),
      focusOnToggle: document.activeElement === document.querySelector('.nav-toggle')
    }));
    if (closed.rootOpen) findings.error('behaviour.nav-escape', 'Escape did not close the navigation', at);
    else findings.pass('behaviour.nav-escape');
    if (!closed.focusOnToggle) {
      findings.error('behaviour.nav-focus-return', 'Escape closed the menu but did not return focus to the toggle, so the keyboard loses its place', { ...at, evidence: closed });
    } else findings.pass('behaviour.nav-focus-return');
  } catch (err) {
    findings.error('behaviour.mobile-nav', `mobile navigation check failed: ${err.message.split('\n')[0]}`, at);
  } finally {
    await page.close();
    await context.close();
  }
}

/* ------------------------------------------------------------ keyboard ---- */

async function keyboardPath({ browser, origin, contentRoutes, findings }) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await blockExternalHosts(context);
  for (const route of contentRoutes) {
    const page = await context.newPage();
    const at = { group: 'behaviour', route, viewport: 'keyboard' };
    try {
      await page.goto(origin + route, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.keyboard.press('Tab');
      const first = await page.evaluate(() => {
        const el = document.activeElement;
        return el ? {
          tag: el.tagName.toLowerCase(),
          text: (el.textContent ?? '').trim().slice(0, 40),
          href: el.getAttribute?.('href') ?? null,
          isSkipLink: el.classList?.contains('skip-link') ?? false,
          outlineVisible: getComputedStyle(el).outlineStyle !== 'none' || getComputedStyle(el).boxShadow !== 'none'
        } : null;
      });
      if (!first) {
        findings.error('behaviour.keyboard-first-focus', 'the first Tab moved focus nowhere', at);
      } else if (!first.isSkipLink) {
        findings.warn('behaviour.skip-link-first', `the first focusable element is <${first.tag}> "${first.text}" rather than a skip link`, { ...at, evidence: first });
      } else {
        findings.pass('behaviour.skip-link-first', route);
        // The skip link must actually move focus to the main landmark.
        await page.keyboard.press('Enter');
        await page.waitForTimeout(200);
        const landed = await page.evaluate(() => ({
          hash: location.hash,
          activeId: document.activeElement?.id ?? null,
          mainExists: !!document.getElementById((location.hash || '#main').slice(1))
        }));
        if (!landed.mainExists) {
          findings.error('behaviour.skip-link-target', `the skip link points at ${landed.hash || '#main'}, which does not exist on this page`, { ...at, evidence: landed });
        } else findings.pass('behaviour.skip-link-target', route);
      }
    } catch (err) {
      findings.error('behaviour.keyboard', `keyboard check failed on ${route}: ${err.message.split('\n')[0]}`, at);
    } finally {
      await page.close();
    }
  }
  await context.close();
}

/* --------------------------------------------- scorecard integrity -------- */

/**
 * Drive the real instrument in a real browser and compare its arithmetic
 * against automation/lib/scorecard.mjs at every band boundary.
 *
 * The oracle is not a second implementation to be kept in sync by editing
 * whichever one is convenient: the page is the truth about what visitors see,
 * and the oracle is the truth about what was intended. A disagreement is a
 * finding, not a merge conflict.
 */
async function scorecardIntegrity({ browser, origin, findings }) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  await blockExternalHosts(context);
  const page = await context.newPage();
  const at = { group: 'behaviour', route: SCORECARD_ROUTE };
  const observed = watch(page, { ignoreHosts: EXTERNAL_HOSTS });

  try {
    await page.goto(origin + SCORECARD_ROUTE, { waitUntil: 'domcontentloaded', timeout: 20000 });

    /* --------------------------------------------- the instrument's shape */
    const shape = await page.evaluate(() => {
      const cats = [...document.querySelectorAll('#categories .score-cat')];
      return {
        categories: cats.map(c => c.getAttribute('data-name')),
        radioGroups: [...new Set([...document.querySelectorAll('#categories input[type=radio]')].map(r => r.name))].length,
        radios: document.querySelectorAll('#categories input[type=radio]').length,
        // Each statement should be its own fieldset/legend rather than twenty
        // groups sharing one name — the fix made in the last QA pass.
        fieldsets: document.querySelectorAll('#categories fieldset').length,
        hasTotal: !!document.getElementById('total'),
        hasBand: !!document.getElementById('bandTitle'),
        hasLowest: !!document.getElementById('lowest')
      };
    });

    const expectedGroups = CATEGORIES.length * STATEMENTS_PER_CATEGORY;
    if (shape.categories.length !== CATEGORIES.length) {
      findings.error('behaviour.scorecard-shape', `the page has ${shape.categories.length} categories, the specification has ${CATEGORIES.length}`, { ...at, evidence: shape });
      return;
    }
    if (JSON.stringify(shape.categories) !== JSON.stringify([...CATEGORIES])) {
      findings.error('behaviour.scorecard-categories', `category names differ from the specification: page has ${shape.categories.join(', ')}`, { ...at, evidence: shape });
    }
    if (shape.radioGroups !== expectedGroups) {
      findings.error('behaviour.scorecard-groups', `${shape.radioGroups} radio groups, expected ${expectedGroups} (one per statement)`, { ...at, evidence: shape });
      return;
    }
    if (shape.radios !== expectedGroups * 3) {
      findings.error('behaviour.scorecard-radios', `${shape.radios} radio inputs, expected ${expectedGroups * 3} (0/1/2 per statement)`, { ...at, evidence: shape });
    }
    if (shape.fieldsets < expectedGroups) {
      findings.warn('behaviour.scorecard-fieldsets', `${shape.fieldsets} fieldsets for ${expectedGroups} statements; each statement should carry its own fieldset/legend so a screen reader announces which statement it is scoring`, at);
    } else findings.pass('behaviour.scorecard-fieldsets');
    if (!shape.hasTotal || !shape.hasBand || !shape.hasLowest) {
      findings.error('behaviour.scorecard-outputs', 'the total, band or weakest-signal output element is missing', { ...at, evidence: shape });
      return;
    }
    findings.pass('behaviour.scorecard-shape');

    /* ------------------------------------------------- arithmetic, boundaries */
    const fill = async answers => page.evaluate(values => {
      values.forEach((group, c) => group.forEach((value, s) => {
        const input = document.querySelector(`input[name="q${c}_${s}"][value="${value}"]`);
        if (input) {
          input.checked = true;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }));
      return {
        total: document.getElementById('total').textContent.trim(),
        band: document.getElementById('bandTitle').textContent.trim(),
        lowest: document.getElementById('lowest').textContent.trim(),
        subtotals: [0, 1, 2, 3, 4].map(i => document.getElementById('sub' + i).textContent.trim()),
        weakestName: document.getElementById('weakestName')?.textContent.trim() ?? null,
        resultReady: document.getElementById('resultBlock')?.hasAttribute('data-ready') ?? null,
        nextMove: document.getElementById('nextMove')?.textContent.trim() ?? null
      };
    }, answers);

    for (const total of BOUNDARY_TOTALS) {
      const answers = answersForTotal(total);
      const expected = score(answers);
      const actual = await fill(answers);

      if (Number(actual.total) !== expected.total) {
        findings.error(
          'behaviour.scorecard-total',
          `the page totalled ${actual.total} where the specification gives ${expected.total}`,
          { ...at, evidence: { answers, expected, actual } }
        );
        continue;
      }
      if (actual.band !== expected.band) {
        findings.error(
          'behaviour.scorecard-band',
          `at total ${total} the page reported band "${actual.band}", the specification gives "${expected.band}"`,
          { ...at, evidence: { total, expected: expected.band, actual: actual.band } }
        );
        continue;
      }
      const expectedSubs = CATEGORIES.map(c => String(expected.subtotals[c]));
      if (JSON.stringify(actual.subtotals) !== JSON.stringify(expectedSubs)) {
        findings.error('behaviour.scorecard-subtotals', `at total ${total} the category subtotals disagree`, { ...at, evidence: { expected: expectedSubs, actual: actual.subtotals } });
        continue;
      }

      /* A tie must be reported as a tie. Naming a winner from a tie is the kind
         of small dishonesty an instrument that sells credibility cannot make. */
      if (expected.weakestSignal === null) {
        if (actual.resultReady) {
          findings.error(
            'behaviour.scorecard-tie',
            `at total ${total} the lowest signal is a ${expected.weakestSignals.length}-way tie, but the page presented a single next move as if there were one weakest signal`,
            { ...at, evidence: { total, tied: expected.weakestSignals, weakestName: actual.weakestName } }
          );
        } else findings.pass('behaviour.scorecard-tie', `total ${total}`);
      } else {
        if (actual.weakestName !== expected.weakestSignal) {
          findings.error(
            'behaviour.scorecard-weakest',
            `at total ${total} the page named "${actual.weakestName}" as the weakest signal; the specification gives "${expected.weakestSignal}"`,
            { ...at, evidence: { total, expected: expected.weakestSignal, actual: actual.weakestName } }
          );
        } else if (!actual.nextMove) {
          findings.error('behaviour.scorecard-next-move', `at total ${total} the weakest signal is ${expected.weakestSignal} but no next move was shown`, at);
        } else findings.pass('behaviour.scorecard-weakest', `total ${total}`);
      }
      if (!String(actual.lowest).length && total > 0) {
        findings.warn('behaviour.scorecard-lowest-text', `at total ${total} the weakest-signal line is empty`, at);
      }
    }

    /* ----------------------------- a partial card must not produce a result */
    await page.reload({ waitUntil: 'domcontentloaded' });
    const partial = await page.evaluate(() => {
      const input = document.querySelector('input[name="q0_0"][value="2"]');
      input.checked = true;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      return {
        band: document.getElementById('bandTitle').textContent.trim(),
        resultReady: document.getElementById('resultBlock')?.hasAttribute('data-ready') ?? null
      };
    });
    if (partial.resultReady) {
      findings.error('behaviour.scorecard-partial', 'one answered statement produced a ready result; a next move derived from a partial score is a guess', { ...at, evidence: partial });
    } else findings.pass('behaviour.scorecard-partial');

    for (const message of observed.pageErrors) {
      findings.error('behaviour.scorecard-page-error', `uncaught error while driving the scorecard: ${message}`, at);
    }
  } catch (err) {
    findings.error('behaviour.scorecard', `scorecard integrity check failed: ${err.message.split('\n')[0]}`, at);
  } finally {
    await page.close();
    await context.close();
  }
}

/* ------------------------------------------------- the fail-open guarantee - */

/**
 * THE MOST IMPORTANT ASSERTION IN THE SUITE.
 *
 * With capture configured and the endpoint deliberately unreachable, access to
 * the diagnostic must still be granted. A capture that fails costs Sklarz
 * Creative a lead record; it must never cost the visitor the tool.
 *
 * This is checked by injecting a capture configuration before any script runs
 * and blackholing the endpoint, so it exercises the real code path rather than
 * the shipped-off default. Nothing is posted anywhere — the endpoint is a
 * non-routable test URL, and it is aborted at the network layer besides.
 */
async function scorecardFailsOpen({ browser, origin, findings }) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  await blockExternalHosts(context);
  const page = await context.newPage();
  const at = { group: 'behaviour', route: SCORECARD_ROUTE };
  const FAKE = 'https://qa-harness.invalid/capture-endpoint-that-does-not-exist';

  try {
    // Belt and braces: the host is non-routable AND every request to it is
    // aborted, so nothing can leave this machine.
    await page.route('**/qa-harness.invalid/**', route => route.abort('connectionrefused'));

    /* The page's own head script ASSIGNS window.TFCS_CAPTURE, so a plain
       injected value is overwritten before the gate logic reads it. Installing
       an accessor instead means the page's own assignment is honoured in every
       respect except the endpoint, which is forced to the unreachable test URL.
       That exercises the real configured-capture code path rather than the
       shipped-off default — which is the whole point of this check. */
    await page.addInitScript(endpoint => {
      let stored = { endpoint, mode: 'cors', reportResults: false, reportAnonymous: false };
      Object.defineProperty(window, 'TFCS_CAPTURE', {
        configurable: true,
        get() { return stored; },
        set(value) {
          stored = Object.assign({}, value, { endpoint, mode: 'cors', reportResults: false, reportAnonymous: false });
        }
      });
    }, FAKE);

    await page.goto(origin + SCORECARD_ROUTE, { waitUntil: 'domcontentloaded', timeout: 20000 });

    const gated = await page.evaluate(() => ({
      gateShown: !document.documentElement.classList.contains('tfcs-open'),
      hasForm: !!document.getElementById('capture')
    }));
    if (!gated.hasForm) {
      findings.skip('behaviour.scorecard-fails-open', 'could not exercise the capture path', 'no #capture form is present in the page, so the injected configuration had nothing to enable', at);
      return;
    }
    if (!gated.gateShown) {
      findings.warn('behaviour.scorecard-gate', 'with an endpoint configured the diagnostic was already open, so the gate could not be exercised (a stored access flag would do this)', at);
    }

    await page.fill('#capture [name="first_name"]', 'QA Harness', { timeout: 5000 });
    await page.fill('#capture [name="email"]', 'qa-harness@example.invalid', { timeout: 5000 });
    // Beat the dwell-time spam guard so this exercises the real submit path.
    await page.waitForTimeout(1700);
    await page.click('#capture button[type="submit"], #capture [type="submit"]');
    await page.waitForTimeout(1200);

    const after = await page.evaluate(() => ({
      open: document.documentElement.classList.contains('tfcs-open'),
      statusText: document.getElementById('capture-status')?.textContent.trim() ?? null,
      scorecardVisible: (() => {
        const el = document.getElementById('categories');
        if (!el) return null;
        const style = getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden';
      })()
    }));

    if (!after.open || after.scorecardVisible === false) {
      findings.error(
        'behaviour.scorecard-fails-open',
        'THE SCORECARD DID NOT FAIL OPEN. With the capture endpoint unreachable, access to the diagnostic was not granted. ' +
        'A capture failure must cost a lead record, never the visitor the tool.',
        { ...at, evidence: after }
      );
    } else {
      findings.pass('behaviour.scorecard-fails-open');
      if (!after.statusText) {
        findings.warn('behaviour.scorecard-failure-reported', 'access was granted but the capture failure was not reported to the visitor; in cors mode a real failure should say so', { ...at, evidence: after });
      } else findings.pass('behaviour.scorecard-failure-reported', after.statusText.slice(0, 60));
    }

    /* Declining the follow-up must not reduce what the visitor gets. */
    await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await page.reload({ waitUntil: 'domcontentloaded' });
    const declined = await page.evaluate(async () => {
      const form = document.getElementById('capture');
      if (!form) return { skipped: true };
      form.elements['first_name'].value = 'QA Harness';
      form.elements['email'].value = 'qa-harness@example.invalid';
      const box = form.elements['follow_up_opt_in'];
      return { checkedByDefault: box ? box.checked : null, skipped: false };
    });
    if (declined.checkedByDefault === true) {
      findings.error(
        'behaviour.consent-default',
        'the follow-up opt-in is CHECKED BY DEFAULT. Consent must be an act, not an omission — a pre-ticked box is not consent.',
        at
      );
    } else if (declined.checkedByDefault === false) {
      findings.pass('behaviour.consent-default');
    }
  } catch (err) {
    findings.error('behaviour.scorecard-fails-open', `fail-open check could not complete: ${err.message.split('\n')[0]}`, at);
  } finally {
    await page.close();
    await context.close();
  }
}

/* ------------------------------------------------------- redirect stubs ---- */

/**
 * A redirect stub exists to do one thing. Assert that it does it — and that it
 * does not become a second indexable copy of the page it points at.
 */
async function redirectStubs({ browser, origin, stubRoutes, findings }) {
  if (!stubRoutes.length) return;
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await blockExternalHosts(context);
  for (const route of stubRoutes) {
    const page = await context.newPage();
    const at = { group: 'behaviour', route };
    try {
      await page.goto(origin + route, { waitUntil: 'domcontentloaded', timeout: 20000 });
      // The stub replaces the location; give it a moment and read where we are.
      await page.waitForTimeout(700);
      const landed = new URL(page.url()).pathname;
      if (landed === route) {
        findings.error(
          'behaviour.redirect-stub',
          `${route} declares a redirect but the browser is still on it after loading, so a visitor lands on a page with no content`,
          at
        );
      } else {
        findings.pass('behaviour.redirect-stub', `${route} -> ${landed}`);
      }
      // A stub must also offer a link, for anyone whose scripting is off.
      const fallback = await page.evaluate(() => document.querySelector('a[href]')?.getAttribute('href') ?? null).catch(() => null);
      if (fallback === null) {
        findings.warn('behaviour.redirect-stub-fallback', `${route} has no link for a visitor whose scripting is off`, at);
      }
    } catch (err) {
      findings.error('behaviour.redirect-stub', `could not check ${route}: ${err.message.split('\n')[0]}`, at);
    } finally {
      await page.close();
    }
  }
  await context.close();
}

/**
 * Each sub-suite is isolated. One broken check must not hide fifty working
 * ones — but a suite that dies is reported as an error, not swallowed.
 */
export async function runBehaviourChecks(options) {
  const suites = [
    ['js-disabled', jsDisabled],
    ['reduced-motion', reducedMotion],
    ['redirect-stubs', redirectStubs],
    ['mobile-nav', mobileNav],
    ['keyboard', keyboardPath],
    ['scorecard-integrity', scorecardIntegrity],
    ['scorecard-fails-open', scorecardFailsOpen]
  ];
  for (const [name, suite] of suites) {
    try {
      await suite(options);
    } catch (err) {
      options.findings.error(
        `behaviour.suite-${name}`,
        `the ${name} suite threw and did not complete: ${err.message.split('\n')[0]}`,
        { group: 'behaviour', evidence: err.stack?.split('\n').slice(0, 3).join(' | ') }
      );
    }
  }
}
