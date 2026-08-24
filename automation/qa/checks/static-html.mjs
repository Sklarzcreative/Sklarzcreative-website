/**
 * Static checks over the working tree. No browser required, so these run
 * everywhere and are the floor the harness can always deliver.
 *
 * What is deliberately NOT here: anything that depends on layout, computed
 * style, or the DOM after scripting. Those live in the rendered and behaviour
 * suites, where a real browser gives a real answer.
 */
import { join } from 'node:path';
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import {
  readPage, findHtmlFiles, routeForFile, title, meta, linkHref, headings, ids,
  images, anchors, assetRefs, jsonLdBlocks, visibleText, fileExistsExact, isDirectory, attr, tags,
  parseSitemap, parseRobots
} from '../lib/site.mjs';
import { imageSize } from '../lib/image.mjs';

export const APEX = 'https://sklarzcreative.com';

const TITLE_MAX = 70;      // Beyond this Google truncates in most layouts.
const DESC_MIN = 50;
const DESC_MAX = 165;

/**
 * A redirect stub is a deliberate one-line page that noindexes itself and
 * bounces. It is not held to the metadata standard a real page is, because it
 * has no content to describe — demanding og:image on it would be a false
 * positive, and false positives are how a QA tool loses its reader.
 */
export function isRedirectStub(html) {
  return /http-equiv\s*=\s*["']refresh["']/i.test(html);
}

/**
 * A shallow clone has no per-file history, so git's answer for "when did this
 * file last change" is the checkout commit for every file. That would make the
 * lastmod check fail on all thirteen entries at once, which is a false alarm —
 * so the check reports `skipped` with the reason instead. CI sets
 * fetch-depth: 0 so it can actually run there.
 */
function gitHistoryAvailable(root) {
  try {
    const shallow = execFileSync('git', ['rev-parse', '--is-shallow-repository'],
      { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    if (shallow === 'true') return { ok: false, reason: 'the repository is a shallow clone, so git has no per-file history to compare lastmod against. CI sets fetch-depth: 0 for this reason.' };
    execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, stdio: 'ignore' });
    return { ok: true };
  } catch {
    return { ok: false, reason: 'git is not available or this is not a git working tree, so there is no history to compare lastmod against.' };
  }
}

/** The date a file's content last changed, per git. null when unknown. */
function lastCommitDate(root, file) {
  try {
    const out = execFileSync('git', ['log', '-1', '--format=%ad', '--date=short', 'HEAD', '--', file],
      { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    return /^\d{4}-\d{2}-\d{2}$/.test(out) ? out : null;
  } catch {
    return null;
  }
}

function resolveRef(root, route, ref) {
  const clean = ref.split('#')[0].split('?')[0];
  if (!clean) return null;
  if (/^(https?:|mailto:|tel:|data:|javascript:|#)/i.test(clean)) return null;
  const path = clean.startsWith('/')
    ? clean.slice(1)
    : join(route.replace(/^\//, '').replace(/[^/]*$/, ''), clean).replace(/^\/+/, '');
  // Normalise any ../ segments.
  const parts = [];
  for (const segment of path.split('/')) {
    if (segment === '.' || segment === '') continue;
    if (segment === '..') parts.pop();
    else parts.push(segment);
  }
  return parts.join('/');
}

export function runStaticChecks(root, findings) {
  const files = findHtmlFiles(root);
  const pages = files.map(f => readPage(root, f));
  const seenTitles = new Map();
  const seenDescriptions = new Map();

  for (const page of pages) {
    const { file, route, html } = page;
    const at = { group: 'static', file, route };
    const stub = isRedirectStub(html);
    const noindex = (meta(html, 'robots') ?? '').toLowerCase().includes('noindex');
    /* A share card and structured data are for a page someone might share or
       find. A 404 and a redirect stub are neither, and demanding og:image on
       them would be a false positive — which is how a QA tool loses its
       reader's trust and stops being run. */
    const shareable = !stub && !noindex;

    /* ------------------------------------------------------------- basics */
    if (!/^<!DOCTYPE html>/i.test(page.raw.trimStart())) {
      findings.error('static.doctype', 'no <!DOCTYPE html> at the top of the file', at);
    } else findings.pass('static.doctype', file);

    const lang = attr(tags(html, 'html')[0] ?? '', 'lang');
    if (!lang) findings.error('static.html-lang', 'the <html> element has no lang attribute, so assistive technology cannot pick a voice', at);
    else findings.pass('static.html-lang', file);

    if (!meta(html, 'viewport')) findings.error('static.viewport', 'no viewport meta — the page will render at desktop width on a phone', at);
    else findings.pass('static.viewport', file);

    if (!/<meta[^>]+charset/i.test(html)) findings.error('static.charset', 'no charset declaration', at);
    else findings.pass('static.charset', file);

    /* -------------------------------------------------------------- title */
    const pageTitle = title(html);
    if (!pageTitle) {
      findings.error('static.title', 'no <title>', at);
    } else {
      findings.pass('static.title', file);
      if (pageTitle.length > TITLE_MAX) {
        findings.warn('static.title-length', `title is ${pageTitle.length} characters; most search layouts truncate past about ${TITLE_MAX}`, { ...at, evidence: pageTitle });
      }
      if (!stub) {
        const previous = seenTitles.get(pageTitle);
        if (previous) {
          findings.error('static.title-duplicate', `identical <title> to ${previous} — two pages competing for the same result`, { ...at, evidence: pageTitle });
        } else seenTitles.set(pageTitle, file);
      }
    }

    /* -------------------------------------------------------- description */
    const description = meta(html, 'description');
    if (!description) {
      if (stub) findings.info('static.description', 'redirect stub, no description needed', at);
      else findings.error('static.description', 'no meta description', at);
    } else {
      findings.pass('static.description', file);
      if (description.length < DESC_MIN) {
        findings.warn('static.description-length', `description is only ${description.length} characters`, { ...at, evidence: description });
      } else if (description.length > DESC_MAX) {
        findings.warn('static.description-length', `description is ${description.length} characters, so a search result will truncate it around ${DESC_MAX}. Not broken — but the sentence that gets cut is the one nobody reads.`, { ...at, evidence: description });
      }
      const previous = seenDescriptions.get(description);
      if (previous) {
        findings.error('static.description-duplicate', `identical meta description to ${previous}`, { ...at, evidence: description.slice(0, 120) });
      } else seenDescriptions.set(description, file);
    }

    /* ---------------------------------------------------------- canonical */
    const canonical = linkHref(html, 'canonical');
    if (!canonical) {
      findings.error('static.canonical', 'no rel=canonical', at);
    } else if (!canonical.startsWith(APEX + '/') && canonical !== APEX + '/') {
      findings.error('static.canonical-origin', `canonical points at ${canonical}; every canonical must be on ${APEX} — the apex is canonical and www redirects to it`, at);
    } else {
      const expected = APEX + route;
      if (stub) {
        // A stub canonicalising to its real destination is correct behaviour.
        findings.info('static.canonical-stub', `redirect stub canonicalises to ${canonical}`, at);
      } else if (canonical !== expected) {
        findings.error('static.canonical-self', `canonical is ${canonical} but this file is served at ${expected}`, at);
      } else findings.pass('static.canonical', file);
    }

    /* ------------------------------------------------ social card metadata */
    if (shareable) {
      const ogRequired = ['og:type', 'og:url', 'og:title', 'og:description', 'og:image', 'og:site_name'];
      const missingOg = ogRequired.filter(k => !meta(html, k));
      if (missingOg.length) {
        findings.error('static.opengraph', `missing Open Graph tags: ${missingOg.join(', ')} — the link will render as a bare URL when shared`, at);
      } else findings.pass('static.opengraph', file);

      const ogUrl = meta(html, 'og:url');
      if (ogUrl && canonical && ogUrl !== canonical) {
        findings.error('static.og-url-canonical', `og:url (${ogUrl}) disagrees with the canonical (${canonical}); platforms will attribute shares to two different URLs`, at);
      } else if (ogUrl) findings.pass('static.og-url-canonical', file);

      const twitterCard = meta(html, 'twitter:card');
      const twitterMissing = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'].filter(k => !meta(html, k));
      if (twitterMissing.length) {
        findings.warn('static.twitter-card', `missing: ${twitterMissing.join(', ')}`, at);
      } else findings.pass('static.twitter-card', file);

      /* The dimension check the brief specifically asks for: a
         summary_large_image card pointing at a square image is a real defect,
         because every platform then crops it differently and unpredictably.
         The dimensions are read from the FILE, not trusted from the markup. */
      const ogImage = meta(html, 'og:image');
      if (ogImage) {
        const rel = ogImage.startsWith(APEX) ? ogImage.slice(APEX.length + 1) : null;
        if (!ogImage.startsWith('https://')) {
          findings.error('static.og-image-absolute', `og:image must be an absolute https URL, got ${ogImage}`, at);
        } else if (!rel) {
          findings.warn('static.og-image-host', `og:image is hosted off ${APEX}: ${ogImage}`, at);
        } else if (!existsSync(join(root, rel))) {
          findings.error('static.og-image-missing', `og:image points at ${ogImage}, which is not a file in this repository`, at);
        } else {
          const size = imageSize(join(root, rel));
          const declaredW = meta(html, 'og:image:width');
          const declaredH = meta(html, 'og:image:height');
          if (size.width == null) {
            findings.warn('static.og-image-size', `could not read intrinsic dimensions of ${rel}: ${size.reason ?? 'unknown format'}`, at);
          } else {
            const ratio = size.width / size.height;
            if (twitterCard === 'summary_large_image' && ratio < 1.3) {
              findings.error(
                'static.og-image-aspect',
                `twitter:card is summary_large_image but ${rel} is ${size.width}x${size.height} (ratio ${ratio.toFixed(2)}). ` +
                'A large-image card needs roughly 1.91:1 — 1200x630 — or every platform crops it differently.',
                { ...at, evidence: { file: rel, width: size.width, height: size.height, card: twitterCard } }
              );
            } else if (Math.abs(ratio - 1200 / 630) > 0.25) {
              findings.warn('static.og-image-aspect', `${rel} is ${size.width}x${size.height}; the platform-safe shape is 1200x630`, at);
            } else findings.pass('static.og-image-aspect', rel);

            if (declaredW && Number(declaredW) !== size.width) {
              findings.error('static.og-image-declared', `og:image:width says ${declaredW}, the file is ${size.width}`, at);
            }
            if (declaredH && Number(declaredH) !== size.height) {
              findings.error('static.og-image-declared', `og:image:height says ${declaredH}, the file is ${size.height}`, at);
            }
            if (!declaredW || !declaredH) {
              findings.warn('static.og-image-declared', 'og:image:width / og:image:height not declared; some scrapers need them to render the card on first fetch', at);
            }
          }
          if (!meta(html, 'og:image:alt')) {
            findings.warn('static.og-image-alt', 'no og:image:alt', at);
          }
        }
      }
    }

    /* ---------------------------------------------------------- headings */
    const hs = headings(html);
    const h1s = hs.filter(h => h.level === 1);
    if (!stub) {
      if (h1s.length === 0) findings.error('static.h1', 'no <h1> on the page', at);
      else if (h1s.length > 1) findings.error('static.h1', `${h1s.length} <h1> elements; a page has one subject`, { ...at, evidence: h1s.map(h => h.text) });
      else findings.pass('static.h1', file);

      let previous = 0;
      for (const h of hs) {
        if (previous && h.level > previous + 1) {
          findings.error('static.heading-order', `heading level jumps from h${previous} to h${h.level} ("${h.text.slice(0, 60)}") — a screen-reader outline with a missing rung`, at);
        }
        previous = h.level;
      }
    }

    /* ------------------------------------------------------- duplicate ids */
    const seen = new Set();
    const duplicates = new Set();
    for (const id of ids(html)) {
      if (seen.has(id)) duplicates.add(id);
      seen.add(id);
    }
    if (duplicates.size) {
      findings.error('static.duplicate-id', `duplicate id(s): ${[...duplicates].join(', ')} — fragment links and label/for associations resolve to the first one only`, at);
    } else findings.pass('static.duplicate-id', file);

    /* -------------------------------------------------------------- images */
    for (const img of images(html)) {
      if (!img.hasAltAttribute) {
        findings.error('static.img-alt', `<img src="${img.src}"> has no alt attribute. Use alt="" if it is decorative — omitting it makes a screen reader read the filename.`, at);
      }
      if (!img.src) continue;
      const rel = resolveRef(root, route, img.src);
      if (rel && !fileExistsExact(root, rel)) continue; // reported by the asset check below
      if (rel && (img.width || img.height)) {
        const size = imageSize(join(root, rel));
        if (size.width != null) {
          if (img.width && img.width !== size.width) {
            findings.error('static.img-dimensions', `${img.src} declares width="${img.width}" but the file is ${size.width}px wide — the reserved space is wrong and the layout shifts when it decodes`, { ...at, evidence: size });
          }
          if (img.height && img.height !== size.height) {
            findings.error('static.img-dimensions', `${img.src} declares height="${img.height}" but the file is ${size.height}px tall`, { ...at, evidence: size });
          }
        }
      }
    }

    /* ------------------------------------------------ links and assets */
    for (const a of anchors(html)) {
      if (!a.href) {
        findings.error('static.anchor-href', `<a> with no href: "${a.text.slice(0, 50)}"`, at);
        continue;
      }
      if (a.target === '_blank') {
        const rel = (a.rel ?? '').toLowerCase();
        if (!rel.includes('noopener')) {
          findings.error('static.target-blank-noopener', `target="_blank" without rel="noopener" on ${a.href}`, at);
        }
      }
      const rel = resolveRef(root, route, a.href);
      if (rel == null) continue;
      const resolved = isDirectory(root, rel) ? `${rel}/index.html`.replace(/\/+/g, '/') : rel;
      if (!fileExistsExact(root, resolved)) {
        findings.error('static.broken-link', `link to ${a.href} does not resolve to a file on disk (tried ${resolved})`, { ...at, evidence: { text: a.text.slice(0, 60) } });
      }
      // A same-page fragment must find its target id here. Cross-page
      // fragments are left to the rendered suite, where the destination's DOM
      // is actually available.
      if (a.href.startsWith('#') && a.href.length > 1 && !seen.has(a.href.slice(1))) {
        findings.error('static.broken-fragment', `fragment link ${a.href} has no matching id on this page`, at);
      }
    }

    for (const ref of assetRefs(html)) {
      const rel = resolveRef(root, route, ref.value);
      if (rel == null) continue;
      if (!fileExistsExact(root, rel)) {
        findings.error('static.missing-asset', `${ref.kind} references ${ref.value}, which is not a file on disk (tried ${rel})`, at);
      }
    }

    /* --------------------------------------------------- structured data */
    const blocks = jsonLdBlocks(html);
    if (shareable && blocks.length === 0) {
      findings.warn('static.jsonld-present', 'no JSON-LD on the page', at);
    }
    const text = visibleText(html).toLowerCase();
    for (const [i, block] of blocks.entries()) {
      let data;
      try {
        data = JSON.parse(block.raw);
      } catch (err) {
        findings.error('static.jsonld-parse', `JSON-LD block ${i + 1} does not parse: ${err.message}`, at);
        continue;
      }
      findings.pass('static.jsonld-parse', `${file}#${i + 1}`);
      const nodes = data['@graph'] ?? [data];
      for (const node of Array.isArray(nodes) ? nodes : [nodes]) {
        if (!node || typeof node !== 'object') continue;
        if (!node['@type']) findings.warn('static.jsonld-type', `a JSON-LD node has no @type`, at);
        for (const key of ['url', '@id']) {
          const value = node[key];
          if (typeof value === 'string' && value.startsWith('http') && !value.startsWith(APEX)) {
            // An off-apex url in structured data is legitimate for a social
            // profile (sameAs), but not for the page's own identity.
            findings.warn('static.jsonld-origin', `JSON-LD ${key} is off-apex: ${value}`, at);
          }
        }
        /* No fabricated dates: a date asserted in structured data must be
           visible on the page. This is the check no external validator does. */
        for (const key of ['datePublished', 'dateModified', 'uploadDate']) {
          const value = node[key];
          if (typeof value !== 'string') continue;
          const day = value.slice(0, 10);
          const [y, m, d] = day.split('-');
          const monthName = Number.isFinite(Number(m))
            ? ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'][Number(m) - 1]
            : null;
          const stated = text.includes(day) ||
            (monthName && text.includes(monthName) && text.includes(String(Number(d))) && text.includes(y)) ||
            (monthName && text.includes(monthName) && text.includes(y));
          if (!stated) {
            findings.error(
              'static.jsonld-date-unstated',
              `${key} asserts ${value} in structured data, but that date does not appear in the page's visible text. ` +
              'A date is either known and stated, or absent — an invented one is a lie in machine-readable form.',
              { ...at, evidence: { key, value } }
            );
          } else findings.pass('static.jsonld-date-unstated', `${file} ${key}`);
        }
        for (const forbidden of ['aggregateRating', 'review', 'ratingValue']) {
          if (node[forbidden] !== undefined) {
            findings.error('static.jsonld-unsupported-claim', `structured data asserts ${forbidden}, which requires real ratings or reviews the page does not contain`, at);
          }
        }
      }
    }
  }

  return { pages, files };
}

/* ------------------------------------------------ sitemap and robots ------- */

export function runSitemapRobotsChecks(root, findings, pages) {
  const at = { group: 'static' };

  /* ------------------------------------------------------------- robots */
  const robotsPath = join(root, 'robots.txt');
  if (!existsSync(robotsPath)) {
    findings.error('static.robots-exists', 'no robots.txt', at);
  } else {
    const rules = parseRobots(readFileSync(robotsPath, 'utf8'));
    if (!rules.sitemaps.length) {
      findings.error('static.robots-sitemap', 'robots.txt does not declare a Sitemap', { ...at, file: 'robots.txt' });
    } else if (!rules.sitemaps.includes(`${APEX}/sitemap.xml`)) {
      findings.error('static.robots-sitemap', `robots.txt Sitemap is ${rules.sitemaps.join(', ')}, expected ${APEX}/sitemap.xml`, { ...at, file: 'robots.txt' });
    } else findings.pass('static.robots-sitemap');

    const disallowed = rules.groups.flatMap(g => g.disallow);
    for (const path of ['/_original-design/', '/docs/', '/integrations/', '/automation/']) {
      if (!disallowed.some(d => d === path || (d.endsWith('/') && path.startsWith(d)))) {
        findings.error(
          'static.robots-disallow',
          `robots.txt does not disallow ${path}. It is source or archive material, not content — indexing it produces duplicate or irrelevant results.`,
          { ...at, file: 'robots.txt' }
        );
      } else findings.pass('static.robots-disallow', path);
    }
  }

  /* ------------------------------------------------------------ sitemap */
  const sitemapPath = join(root, 'sitemap.xml');
  if (!existsSync(sitemapPath)) {
    findings.error('static.sitemap-exists', 'no sitemap.xml', at);
    return;
  }
  const entries = parseSitemap(readFileSync(sitemapPath, 'utf8'));
  if (!entries.length) {
    findings.error('static.sitemap-parse', 'sitemap.xml contains no <url> entries', { ...at, file: 'sitemap.xml' });
    return;
  }

  const byRoute = new Map(pages.map(p => [p.route, p]));
  const listed = new Set();
  const history = gitHistoryAvailable(root);
  if (!history.ok) {
    findings.skip('static.sitemap-lastmod-accuracy', 'every sitemap lastmod must match the date its page last changed', history.reason, { ...at, file: 'sitemap.xml' });
  }

  for (const entry of entries) {
    const file = { ...at, file: 'sitemap.xml' };
    if (!entry.loc) { findings.error('static.sitemap-loc', 'a <url> entry has no <loc>', file); continue; }
    if (!entry.loc.startsWith(APEX)) {
      findings.error('static.sitemap-origin', `sitemap entry ${entry.loc} is not on ${APEX}`, file);
      continue;
    }
    const route = entry.loc.slice(APEX.length) || '/';
    listed.add(route);
    const page = byRoute.get(route);
    if (!page) {
      findings.error('static.sitemap-orphan', `sitemap lists ${entry.loc}, which does not resolve to a page on disk`, file);
      continue;
    }
    const robots = (meta(page.html, 'robots') ?? '').toLowerCase();
    if (robots.includes('noindex')) {
      findings.error('static.sitemap-noindex', `sitemap lists ${route}, but that page is meta robots noindex — a sitemap asking for a page that refuses indexing`, file);
    } else findings.pass('static.sitemap-entry', route);

    if (entry.lastmod && !/^\d{4}-\d{2}-\d{2}/.test(entry.lastmod)) {
      findings.warn('static.sitemap-lastmod', `lastmod "${entry.lastmod}" for ${route} is not a plain ISO date`, file);
      continue;
    }

    /* A lastmod is a claim about when the content changed. On a hand-maintained
       sitemap it silently goes stale every time a page is edited and the sitemap
       is not — and a date that is asserted rather than true is the one kind of
       inaccuracy this site's own rules single out. git knows the answer, so the
       claim is checkable. */
    if (!entry.lastmod || !history.ok) continue;
    const actual = lastCommitDate(root, page.file);
    if (!actual) {
      findings.info('static.sitemap-lastmod-accuracy', `${route}: no git history for this file, so its lastmod cannot be checked`, file);
    } else if (entry.lastmod > actual) {
      findings.error(
        'static.sitemap-lastmod-accuracy',
        `${route} claims lastmod ${entry.lastmod}, but the file last changed ${actual} — a date in the future relative to its own history is an assertion that never happened`,
        { ...file, evidence: { route, claimed: entry.lastmod, actual } }
      );
    } else if (entry.lastmod < actual) {
      findings.warn(
        'static.sitemap-lastmod-accuracy',
        `${route} claims lastmod ${entry.lastmod}, but the file last changed ${actual}. Stale rather than wrong — but the sitemap is telling crawlers not to bother re-reading a page that did change.`,
        { ...file, evidence: { route, claimed: entry.lastmod, actual } }
      );
    } else findings.pass('static.sitemap-lastmod-accuracy', route);
  }

  for (const page of pages) {
    const robots = (meta(page.html, 'robots') ?? '').toLowerCase();
    if (robots.includes('noindex')) continue;
    if (listed.has(page.route)) continue;
    findings.error(
      'static.sitemap-missing',
      `${page.route} is indexable and on disk but absent from sitemap.xml`,
      { ...at, file: page.file }
    );
  }
}
