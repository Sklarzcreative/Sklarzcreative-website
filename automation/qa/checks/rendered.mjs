/**
 * Rendered checks — a real browser at three widths.
 *
 * Everything here needs layout or a live DOM: overflow, computed accessible
 * names, ids after scripting, whether an image actually decoded. The static
 * suite reads the source; this suite reads what a visitor gets.
 */
import { settle, watch, blockExternalHosts, EXTERNAL_HOSTS, VIEWPORTS } from '../lib/browser.mjs';

export async function runRenderedChecks({ browser, origin, routes, findings }) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1
    });
    await blockExternalHosts(context);

    for (const route of routes) {
      const page = await context.newPage();
      const observed = watch(page, { ignoreHosts: EXTERNAL_HOSTS });
      const at = { group: 'rendered', route, viewport: viewport.name };

      let response;
      try {
        response = await page.goto(origin + route, { waitUntil: 'domcontentloaded', timeout: 20000 });
        await page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
      } catch (err) {
        findings.error('rendered.navigation', `could not load ${route}: ${err.message.split('\n')[0]}`, at);
        await page.close();
        continue;
      }

      const status = response?.status() ?? 0;
      if (status !== 200) {
        findings.error('rendered.status', `${route} returned HTTP ${status}`, at);
      } else findings.pass('rendered.status', `${route} @ ${viewport.name}`);

      await settle(page);

      /* ------------------------------------------------------- overflow */
      const overflow = await page.evaluate(() => {
        const doc = document.documentElement;
        const excess = doc.scrollWidth - doc.clientWidth;
        if (excess <= 1) return null;
        // Name the widest offender, or the finding is unactionable.
        let worst = null;
        for (const el of document.querySelectorAll('body *')) {
          const rect = el.getBoundingClientRect();
          const right = rect.right + window.scrollX;
          if (right > doc.clientWidth + 1 && (!worst || right > worst.right)) {
            worst = {
              right: Math.round(right),
              selector: el.tagName.toLowerCase() +
                (el.id ? `#${el.id}` : '') +
                (el.className && typeof el.className === 'string' ? `.${el.className.trim().split(/\s+/).slice(0, 2).join('.')}` : '')
            };
          }
        }
        return { excess, clientWidth: doc.clientWidth, worst };
      });
      if (overflow) {
        findings.error(
          'rendered.horizontal-overflow',
          `${overflow.excess}px of horizontal overflow${overflow.worst ? `; widest element is ${overflow.worst.selector} reaching ${overflow.worst.right}px` : ''}`,
          { ...at, evidence: overflow }
        );
      } else findings.pass('rendered.horizontal-overflow', `${route} @ ${viewport.name}`);

      /* ------------------------- accessible names on links and buttons */
      const nameless = await page.evaluate(() => {
        const accessibleName = el => {
          const aria = el.getAttribute('aria-label');
          if (aria && aria.trim()) return aria.trim();
          const labelledBy = el.getAttribute('aria-labelledby');
          if (labelledBy) {
            const text = labelledBy.split(/\s+/)
              .map(id => document.getElementById(id)?.textContent ?? '')
              .join(' ').trim();
            if (text) return text;
          }
          if (el.textContent && el.textContent.trim()) return el.textContent.trim();
          const img = el.querySelector('img[alt]');
          if (img && img.getAttribute('alt').trim()) return img.getAttribute('alt').trim();
          const svgTitle = el.querySelector('svg title');
          if (svgTitle && svgTitle.textContent.trim()) return svgTitle.textContent.trim();
          const title = el.getAttribute('title');
          if (title && title.trim()) return title.trim();
          if (el.tagName === 'INPUT') return (el.value || '').trim();
          return '';
        };
        const out = [];
        for (const el of document.querySelectorAll('a[href], button, [role="button"], input[type="submit"]')) {
          // An element nobody can reach cannot be operated, so it needs no name.
          const style = getComputedStyle(el);
          if (style.display === 'none' || style.visibility === 'hidden') continue;
          if (el.getAttribute('aria-hidden') === 'true' || el.hasAttribute('inert')) continue;
          if (!accessibleName(el)) {
            out.push({
              tag: el.tagName.toLowerCase(),
              href: el.getAttribute('href'),
              html: el.outerHTML.slice(0, 140)
            });
          }
        }
        return out;
      });
      for (const item of nameless) {
        findings.error('rendered.accessible-name', `${item.tag} has no discernible accessible name`, { ...at, evidence: item });
      }
      if (!nameless.length) findings.pass('rendered.accessible-name', `${route} @ ${viewport.name}`);

      /* --------------------------------------- ids and h1 after scripting */
      const dom = await page.evaluate(() => {
        const idCounts = {};
        for (const el of document.querySelectorAll('[id]')) {
          idCounts[el.id] = (idCounts[el.id] || 0) + 1;
        }
        return {
          duplicateIds: Object.entries(idCounts).filter(([, n]) => n > 1).map(([id]) => id),
          h1Count: document.querySelectorAll('h1').length,
          hasSkipLink: !!document.querySelector('a[href^="#"]')
        };
      });
      if (dom.duplicateIds.length) {
        findings.error('rendered.duplicate-id', `duplicate id(s) in the live DOM: ${dom.duplicateIds.join(', ')}`, at);
      } else findings.pass('rendered.duplicate-id', `${route} @ ${viewport.name}`);

      /* ----------------------------------------------------------- images */
      const imageState = await page.evaluate(() => {
        const out = [];
        for (const img of document.querySelectorAll('img')) {
          const rect = img.getBoundingClientRect();
          const inDocument = rect.top + window.scrollY < document.documentElement.scrollHeight;
          out.push({
            src: img.currentSrc || img.src,
            complete: img.complete,
            naturalWidth: img.naturalWidth,
            loading: img.loading,
            offscreen: rect.width === 0 && rect.height === 0,
            inDocument
          });
        }
        return out;
      });
      for (const img of imageState) {
        if (img.naturalWidth > 0) continue;
        if (img.loading === 'lazy' && !img.complete) {
          /* An image parked far outside the viewport may never have been ASKED
             to load. That is unknowable, not broken, and reporting it as a
             failure sends someone chasing a bug that does not exist. */
          findings.info('rendered.image-not-requested', `${img.src} is lazy and was never requested at this viewport`, at);
          continue;
        }
        findings.error('rendered.image-load', `${img.src} did not load (naturalWidth 0)`, { ...at, evidence: img });
      }

      /* ------------------------------------------ console and network noise */
      for (const message of observed.pageErrors) {
        findings.error('rendered.page-error', `uncaught error: ${message}`, at);
      }
      for (const message of observed.consoleErrors) {
        findings.error('rendered.console-error', `console error: ${message.slice(0, 300)}`, at);
      }
      for (const message of observed.failedRequests) {
        findings.error('rendered.failed-request', `failed request: ${message}`, at);
      }
      if (!observed.pageErrors.length && !observed.consoleErrors.length && !observed.failedRequests.length) {
        findings.pass('rendered.console-clean', `${route} @ ${viewport.name}`);
      }

      await page.close();
    }

    await context.close();
  }
}
