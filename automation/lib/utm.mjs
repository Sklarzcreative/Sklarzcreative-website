/**
 * The canonical UTM convention for Sklarz Creative, and the only place a
 * utm_* value is composed.
 *
 * WHY THIS EXISTS
 * A hand-typed UTM is an attribution loss that cannot be detected afterwards.
 * `utm_source=LinkedIn` and `utm_source=linkedin` are two channels in every
 * reporting tool ever built, and nothing warns you — you simply see half the
 * traffic you earned, split across rows you never notice are the same row.
 * By the time it matters the data is months old and unfixable.
 *
 * So: one vocabulary, one builder, one validator, and a test suite that fails
 * on a value outside the vocabulary.
 *
 * USAGE
 *   import { buildUrl, SOURCES } from './utm.mjs';
 *   buildUrl('https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/', {
 *     source: 'linkedin', medium: 'organic_social',
 *     campaign: 'trust_first_scorecard', content: 'weakest_signal_carousel'
 *   });
 *
 *   node automation/lib/utm.mjs <url> <source> <medium> <campaign> [content] [term]
 */

/** Only the apex. Every canonical, og:url and sitemap entry uses it. */
export const SITE_ORIGIN = 'https://sklarzcreative.com';

/**
 * utm_source — WHERE the click came from. A platform or a property, never a
 * campaign and never a format. Lower snake_case, always.
 *
 * The two LinkedIn values are separate on purpose: a personal profile and a
 * company page behave so differently that averaging them hides the finding.
 */
export const SOURCES = Object.freeze({
  linkedin: 'LinkedIn personal profile',
  linkedin_company: 'LinkedIn company page',
  instagram: 'Instagram',
  facebook: 'Facebook',
  threads: 'Threads',
  x: 'X (formerly Twitter)',
  pinterest: 'Pinterest',
  youtube: 'YouTube',
  tiktok: 'TikTok',
  bluesky: 'Bluesky',
  newsletter: 'The email newsletter',
  email: 'A one-to-one or transactional email',
  podcast: 'Podcast episode notes or description',
  media_kit: 'The media kit, when sent directly',
  partner: 'A named partner or collaborator placement',
  qr: 'A printed or on-screen QR code',
  direct: 'Deliberately untagged — reserved, do not apply to a link'
});

/**
 * utm_medium — HOW it travelled. The category of channel, not the platform.
 * Keep this list short: mediums are how you group sources, and a medium per
 * source defeats the purpose.
 */
export const MEDIUMS = Object.freeze({
  organic_social: 'An unpaid post on a social platform',
  paid_social: 'A paid placement on a social platform',
  email: 'Any email — newsletter, sequence, or one-to-one',
  referral: 'A link from someone else’s property',
  organic_search: 'Unpaid search. Rarely taggable; here for completeness',
  print: 'Printed material, usually via a QR code',
  offline: 'A talk, an event, a conversation',
  profile: 'A bio or profile link rather than a post'
});

/**
 * utm_campaign — WHY. A stable identifier for a body of work, reused across
 * every source and every post that belongs to it. Stability is the whole
 * value: a campaign renamed halfway through is two campaigns in the report.
 *
 * Not an exhaustive list — new campaigns are legitimate. The pattern is
 * enforced; the vocabulary is documented.
 */
export const KNOWN_CAMPAIGNS = Object.freeze({
  trust_first_scorecard: 'The Trust-First Content Scorecard as a lead asset',
  the_trust_files: 'The Trust Files essay series',
  clarity_before_content: 'The Clarity Before Content argument',
  discovery_calls: 'Directly driving discovery-call bookings',
  site_launch_2026: 'The 2026 site redesign launch',
  media_kit: 'Distribution of the media kit',
  newsletter_growth: 'Growing the owned list itself'
});

/**
 * utm_content — WHICH creative. The specific post, image or link position, so
 * two posts in one campaign can be told apart. This is the field that answers
 * "which post produced this lead", and it is the one most often left blank.
 */
export const CONTENT_PATTERN = /^[a-z0-9]+(?:_[a-z0-9]+)*$/;

/** Same shape for every identifier: lower snake_case, no spaces, no hyphens. */
const IDENTIFIER = /^[a-z0-9]+(?:_[a-z0-9]+)*$/;

const MAX_LENGTH = 120; // Matches the cap the capture endpoint applies.

export class UtmError extends Error {}

function requireIdentifier(value, field, { max = MAX_LENGTH } = {}) {
  if (typeof value !== 'string' || !value.length) {
    throw new UtmError(`utm_${field}: required, and must be a non-empty string`);
  }
  if (value.length > max) {
    throw new UtmError(`utm_${field}: longer than ${max} characters, which the capture endpoint truncates`);
  }
  if (!IDENTIFIER.test(value)) {
    throw new UtmError(
      `utm_${field}: "${value}" is not lower snake_case. ` +
      'Use letters, digits and single underscores — no spaces, capitals, hyphens or dots. ' +
      'Case and separator drift silently split one channel into several in every reporting tool.'
    );
  }
  return value;
}

/**
 * @param {object} params
 * @param {string} params.source    one of SOURCES
 * @param {string} params.medium    one of MEDIUMS
 * @param {string} params.campaign  stable identifier
 * @param {string} [params.content] specific creative
 * @param {string} [params.term]    keyword, for paid search only
 * @returns {{utm_source: string, utm_medium: string, utm_campaign: string, utm_content?: string, utm_term?: string}}
 */
export function buildParams({ source, medium, campaign, content, term } = {}) {
  requireIdentifier(source, 'source');
  requireIdentifier(medium, 'medium');
  requireIdentifier(campaign, 'campaign');

  if (!Object.prototype.hasOwnProperty.call(SOURCES, source)) {
    throw new UtmError(
      `utm_source: "${source}" is not in the vocabulary. Known: ${Object.keys(SOURCES).join(', ')}. ` +
      'Add it to SOURCES with a one-line description if it is genuinely new.'
    );
  }
  if (source === 'direct') {
    throw new UtmError('utm_source: "direct" is reserved for untagged traffic and must never be applied to a link');
  }
  if (!Object.prototype.hasOwnProperty.call(MEDIUMS, medium)) {
    throw new UtmError(
      `utm_medium: "${medium}" is not in the vocabulary. Known: ${Object.keys(MEDIUMS).join(', ')}.`
    );
  }

  const params = { utm_source: source, utm_medium: medium, utm_campaign: campaign };
  if (content !== undefined && content !== null && content !== '') {
    params.utm_content = requireIdentifier(content, 'content');
  }
  if (term !== undefined && term !== null && term !== '') {
    params.utm_term = requireIdentifier(term, 'term');
    if (medium !== 'paid_social' && medium !== 'organic_search') {
      throw new UtmError(
        'utm_term: only meaningful for paid or search mediums. ' +
        'On an organic social post it is noise that makes two identical links look different.'
      );
    }
  }
  return params;
}

/**
 * Compose a tagged URL.
 *
 * PRESERVES EXISTING TRACKING. If the URL already carries utm_* parameters,
 * this throws rather than overwriting, unless `{ overwrite: true }` is passed
 * explicitly. Someone may have set those parameters for a reason not visible
 * from here — a paid test, a partner report, a campaign roll-up — and silently
 * retagging their link destroys their data. Read it, report it, then decide.
 */
export function buildUrl(baseUrl, options = {}) {
  let url;
  try {
    url = new URL(baseUrl);
  } catch {
    throw new UtmError(`base URL is not a valid absolute URL: ${baseUrl}`);
  }
  if (url.protocol !== 'https:') {
    throw new UtmError(`base URL must be https, got ${url.protocol}`);
  }

  const existing = [...url.searchParams.keys()].filter(k => k.startsWith('utm_'));
  if (existing.length && !options.overwrite) {
    throw new UtmError(
      `base URL already carries deliberate tracking (${existing.join(', ')}). ` +
      'Refusing to overwrite it. Read what it is for first; pass { overwrite: true } only once you know.'
    );
  }
  if (existing.length) existing.forEach(k => url.searchParams.delete(k));

  for (const [key, value] of Object.entries(buildParams(options))) {
    url.searchParams.set(key, value);
  }
  // Stable key order, so the same inputs always produce a byte-identical link.
  url.search = new URLSearchParams(
    [...url.searchParams.entries()].sort(([a], [b]) => a.localeCompare(b))
  ).toString();
  return url.toString();
}

/** Read utm_* out of a URL or a query string. Used to inspect, never to rewrite. */
export function readParams(urlOrQuery) {
  const query = urlOrQuery.includes('?') ? urlOrQuery.slice(urlOrQuery.indexOf('?')) : urlOrQuery;
  const out = {};
  for (const [key, value] of new URLSearchParams(query)) {
    if (key.startsWith('utm_')) out[key] = value.slice(0, MAX_LENGTH);
  }
  return out;
}

/**
 * Audit a link someone already made. Returns findings rather than throwing, so
 * a report can list every problem across a hundred links in one pass.
 */
export function auditUrl(rawUrl) {
  const findings = [];
  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    return [{ severity: 'error', message: `not a valid absolute URL: ${rawUrl}` }];
  }

  const present = readParams(url.search);
  const keys = Object.keys(present);
  if (keys.length === 0) {
    return [{ severity: 'info', message: 'no utm parameters — untagged, so this click will land in direct/none' }];
  }

  for (const required of ['utm_source', 'utm_medium', 'utm_campaign']) {
    if (!present[required]) findings.push({ severity: 'error', message: `${required} is missing` });
  }
  if (!present.utm_content) {
    findings.push({
      severity: 'warning',
      message: 'utm_content is missing — the campaign is attributable but the individual post is not'
    });
  }
  for (const [key, value] of Object.entries(present)) {
    if (!IDENTIFIER.test(value)) {
      findings.push({
        severity: 'error',
        message: `${key}="${value}" is not lower snake_case — it will not aggregate with its siblings`
      });
    }
  }
  if (present.utm_source && !Object.prototype.hasOwnProperty.call(SOURCES, present.utm_source)) {
    findings.push({ severity: 'error', message: `utm_source="${present.utm_source}" is outside the vocabulary` });
  }
  if (present.utm_medium && !Object.prototype.hasOwnProperty.call(MEDIUMS, present.utm_medium)) {
    findings.push({ severity: 'error', message: `utm_medium="${present.utm_medium}" is outside the vocabulary` });
  }
  if (url.origin !== SITE_ORIGIN) {
    findings.push({
      severity: 'warning',
      message: `points at ${url.origin}, not ${SITE_ORIGIN} — utm parameters on an off-site link are read by that site, not by us`
    });
  }
  if (findings.length === 0) findings.push({ severity: 'info', message: 'conforms to the convention' });
  return findings;
}

/* ------------------------------------------------------------------ CLI --- */

if (import.meta.url === `file://${process.argv[1]}`) {
  const [command, ...rest] = process.argv.slice(2);

  if (command === 'audit') {
    if (!rest[0]) { console.error('usage: node automation/lib/utm.mjs audit <url>'); process.exit(2); }
    const findings = auditUrl(rest[0]);
    for (const f of findings) console.log(`${f.severity.toUpperCase().padEnd(8)}${f.message}`);
    process.exit(findings.some(f => f.severity === 'error') ? 1 : 0);
  }

  if (command === 'vocab') {
    console.log('utm_source');
    for (const [k, v] of Object.entries(SOURCES)) console.log(`  ${k.padEnd(20)}${v}`);
    console.log('\nutm_medium');
    for (const [k, v] of Object.entries(MEDIUMS)) console.log(`  ${k.padEnd(20)}${v}`);
    console.log('\nutm_campaign (known — new ones are allowed, the pattern is enforced)');
    for (const [k, v] of Object.entries(KNOWN_CAMPAIGNS)) console.log(`  ${k.padEnd(28)}${v}`);
    process.exit(0);
  }

  const [url, source, medium, campaign, content, term] = [command, ...rest];
  if (!url || !source || !medium || !campaign) {
    console.error('usage: node automation/lib/utm.mjs <url> <source> <medium> <campaign> [content] [term]');
    console.error('       node automation/lib/utm.mjs audit <url>');
    console.error('       node automation/lib/utm.mjs vocab');
    process.exit(2);
  }
  try {
    console.log(buildUrl(url, { source, medium, campaign, content, term }));
  } catch (err) {
    console.error(err instanceof UtmError ? err.message : err);
    process.exit(1);
  }
}
