/**
 * Discover the site's public surface from the working tree, and provide the
 * small amount of HTML extraction the static checks need.
 *
 * ON REGEX AND HTML
 * Parsing HTML with regular expressions is normally a mistake. It is acceptable
 * here for a narrow reason: this site is hand-authored, its head metadata is
 * one tag per line, and everything that genuinely needs a parser — heading
 * order after scripting, computed accessible names, duplicate ids in the live
 * DOM — is checked in a real browser instead. These extractors are a fast
 * pre-pass over the source, not a substitute for the rendered suite.
 *
 * Where an extractor cannot be confident, it returns null and the check
 * reports "could not determine" rather than a pass or a failure.
 */
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, sep, posix } from 'node:path';

/** Directories that are never part of the public site. */
export const EXCLUDED_DIRS = new Set([
  '.git', 'node_modules', 'automation', 'docs', 'integrations', '_original-design', '.github'
]);

export function findHtmlFiles(root) {
  const out = [];
  (function walk(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith('.') && entry.name !== '.well-known') continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (EXCLUDED_DIRS.has(entry.name)) continue;
        walk(full);
      } else if (entry.isFile() && entry.name.endsWith('.html')) {
        out.push(relative(root, full).split(sep).join(posix.sep));
      }
    }
  })(root);
  return out.sort();
}

/** The URL path GitHub Pages would serve a given file at. */
export function routeForFile(file) {
  if (file === 'index.html') return '/';
  if (file.endsWith('/index.html')) return '/' + file.slice(0, -'index.html'.length);
  return '/' + file;
}

/**
 * Case-sensitivity matters: GitHub Pages serves from a case-sensitive
 * filesystem, and macOS does not, so a link that works locally can 404 live.
 */
export function fileExistsExact(root, relPath) {
  const parts = relPath.split('/').filter(Boolean);
  let current = root;
  for (const part of parts) {
    let entries;
    try { entries = readdirSync(current); } catch { return false; }
    if (!entries.includes(part)) return false;
    current = join(current, part);
  }
  return existsSync(current);
}

export function isDirectory(root, relPath) {
  try { return statSync(join(root, relPath)).isDirectory(); } catch { return false; }
}

/* ------------------------------------------------------- HTML extraction --- */

const stripComments = html => html.replace(/<!--[\s\S]*?-->/g, '');

export function readPage(root, file) {
  const raw = readFileSync(join(root, file), 'utf8');
  return { file, route: routeForFile(file), raw, html: stripComments(raw) };
}

/** Attribute value from a tag string, entity-decoded for the few entities used here. */
export function attr(tag, name) {
  const m = tag.match(new RegExp(`\\b${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  if (!m) return null;
  const value = m[2] ?? m[3] ?? m[4] ?? '';
  return value
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–').replace(/&nbsp;/g, ' ');
}

export function tags(html, tagName) {
  return html.match(new RegExp(`<${tagName}\\b[^>]*>`, 'gi')) ?? [];
}

/** <meta name="x"> or <meta property="x"> content. */
export function meta(html, key) {
  for (const tag of tags(html, 'meta')) {
    const name = attr(tag, 'name') ?? attr(tag, 'property');
    if (name && name.toLowerCase() === key.toLowerCase()) return attr(tag, 'content') ?? '';
  }
  return null;
}

export function linkHref(html, rel) {
  for (const tag of tags(html, 'link')) {
    const value = attr(tag, 'rel');
    if (value && value.toLowerCase().split(/\s+/).includes(rel.toLowerCase())) return attr(tag, 'href');
  }
  return null;
}

export function title(html) {
  const m = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  if (!m) return null;
  return m[1]
    .replace(/&amp;/g, '&').replace(/&mdash;/g, '—').replace(/&ndash;/g, '–')
    .replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
}

export function headings(html) {
  const out = [];
  const re = /<(h[1-6])\b[^>]*>([\s\S]*?)<\/\1>/gi;
  let m;
  while ((m = re.exec(html))) {
    out.push({
      level: Number(m[1][1]),
      text: m[2].replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(),
      index: m.index
    });
  }
  return out;
}

export function ids(html) {
  return tags(html, '[a-zA-Z][a-zA-Z0-9-]*')
    .map(tag => attr(tag, 'id'))
    .filter(Boolean);
}

export function images(html) {
  return tags(html, 'img').map(tag => ({
    tag,
    src: attr(tag, 'src'),
    alt: attr(tag, 'alt'),
    // A missing alt attribute and alt="" are different: the second is a
    // deliberate statement that the image is decorative.
    hasAltAttribute: /\balt\s*=/.test(tag),
    width: attr(tag, 'width') ? Number(attr(tag, 'width')) : null,
    height: attr(tag, 'height') ? Number(attr(tag, 'height')) : null,
    loading: attr(tag, 'loading')
  }));
}

export function anchors(html) {
  const out = [];
  const re = /<a\b([^>]*)>([\s\S]*?)<\/a>/gi;
  let m;
  while ((m = re.exec(html))) {
    const tag = `<a ${m[1]}>`;
    out.push({
      tag,
      href: attr(tag, 'href'),
      target: attr(tag, 'target'),
      rel: attr(tag, 'rel'),
      text: m[2].replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
    });
  }
  return out;
}

/** Every local asset reference the page depends on. */
export function assetRefs(html) {
  const refs = [];
  const push = (value, kind) => { if (value) refs.push({ value, kind }); };
  for (const tag of tags(html, 'img')) {
    push(attr(tag, 'src'), 'img');
    for (const part of (attr(tag, 'srcset') ?? '').split(',')) {
      const url = part.trim().split(/\s+/)[0];
      if (url) push(url, 'srcset');
    }
  }
  for (const tag of tags(html, 'link')) {
    const rel = (attr(tag, 'rel') ?? '').toLowerCase();
    if (['stylesheet', 'icon', 'apple-touch-icon', 'preload', 'manifest'].some(r => rel.includes(r))) {
      push(attr(tag, 'href'), `link:${rel}`);
    }
  }
  for (const tag of tags(html, 'script')) push(attr(tag, 'src'), 'script');
  for (const tag of tags(html, 'source')) push(attr(tag, 'src'), 'source');
  return refs;
}

export function jsonLdBlocks(html) {
  const out = [];
  const re = /<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) out.push({ raw: m[1].trim(), index: m.index });
  return out;
}

/** Visible text, for checking that a structured-data date is actually on the page. */
export function visibleText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&[a-z]+;|&#\d+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/* -------------------------------------------------- sitemap and robots ----- */

export function parseSitemap(xml) {
  const urls = [];
  const re = /<url>([\s\S]*?)<\/url>/gi;
  let m;
  while ((m = re.exec(xml))) {
    const block = m[1];
    const get = tag => {
      const t = block.match(new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`, 'i'));
      return t ? t[1].trim() : null;
    };
    urls.push({ loc: get('loc'), lastmod: get('lastmod'), changefreq: get('changefreq'), priority: get('priority') });
  }
  return urls;
}

export function parseRobots(text) {
  const lines = text.split(/\r?\n/);
  const rules = { sitemaps: [], groups: [] };
  let group = null;
  for (const line of lines) {
    const clean = line.replace(/#.*$/, '').trim();
    if (!clean) continue;
    const [rawKey, ...rest] = clean.split(':');
    const key = rawKey.trim().toLowerCase();
    const value = rest.join(':').trim();
    if (key === 'sitemap') { rules.sitemaps.push(value); continue; }
    if (key === 'user-agent') { group = { agent: value, allow: [], disallow: [] }; rules.groups.push(group); continue; }
    if (!group) continue;
    if (key === 'allow') group.allow.push(value);
    if (key === 'disallow') group.disallow.push(value);
  }
  return rules;
}
