import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildUrl, buildParams, readParams, auditUrl, UtmError, SOURCES, MEDIUMS } from '../lib/utm.mjs';

const SCORECARD = 'https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/';

test('a valid link is built with parameters in a stable order', () => {
  const url = buildUrl(SCORECARD, {
    source: 'linkedin', medium: 'organic_social',
    campaign: 'trust_first_scorecard', content: 'weakest_signal_carousel'
  });
  // Byte-identical output for identical input, so the same post always
  // produces the same link and the report does not split it in two.
  assert.equal(url, SCORECARD +
    '?utm_campaign=trust_first_scorecard&utm_content=weakest_signal_carousel' +
    '&utm_medium=organic_social&utm_source=linkedin');
  assert.equal(buildUrl(SCORECARD, { source: 'linkedin', medium: 'organic_social', campaign: 'trust_first_scorecard', content: 'weakest_signal_carousel' }), url);
});

test('case drift is rejected rather than normalised', () => {
  // Rejecting is deliberate: silently lowercasing would let "LinkedIn" into a
  // hand-written link somewhere else and only this path would be safe.
  assert.throws(() => buildParams({ source: 'LinkedIn', medium: 'organic_social', campaign: 'x_y' }), UtmError);
  assert.throws(() => buildParams({ source: 'linked-in', medium: 'organic_social', campaign: 'x_y' }), UtmError);
  assert.throws(() => buildParams({ source: 'linked in', medium: 'organic_social', campaign: 'x_y' }), UtmError);
  assert.throws(() => buildParams({ source: 'linkedin.com', medium: 'organic_social', campaign: 'x_y' }), UtmError);
});

test('a source outside the vocabulary is rejected with the vocabulary in the message', () => {
  try {
    buildParams({ source: 'mastodon', medium: 'organic_social', campaign: 'x_y' });
    assert.fail('should have thrown');
  } catch (err) {
    assert.ok(err instanceof UtmError);
    assert.match(err.message, /not in the vocabulary/);
    assert.match(err.message, /linkedin/);
  }
});

test('"direct" is reserved and may never be applied to a link', () => {
  assert.throws(() => buildParams({ source: 'direct', medium: 'referral', campaign: 'x_y' }), /reserved/);
});

test('utm_term is refused on organic social, where it is noise', () => {
  assert.throws(
    () => buildParams({ source: 'linkedin', medium: 'organic_social', campaign: 'a_b', term: 'trust' }),
    /only meaningful for paid or search/
  );
  assert.doesNotThrow(() => buildParams({ source: 'linkedin', medium: 'paid_social', campaign: 'a_b', term: 'trust' }));
});

test('existing deliberate tracking is preserved, not overwritten', () => {
  // The important behaviour: someone may have set those parameters for a
  // reason not visible from here. Overwriting silently destroys their data.
  const tagged = 'https://sklarzcreative.com/?utm_source=partner&utm_campaign=q3_review';
  assert.throws(
    () => buildUrl(tagged, { source: 'linkedin', medium: 'organic_social', campaign: 'site_launch_2026' }),
    /already carries deliberate tracking/
  );
  // Only an explicit, deliberate override proceeds.
  const forced = buildUrl(tagged, { source: 'linkedin', medium: 'organic_social', campaign: 'site_launch_2026', overwrite: true });
  assert.match(forced, /utm_source=linkedin/);
  assert.ok(!forced.includes('partner'));
});

test('http is refused', () => {
  assert.throws(() => buildUrl('http://sklarzcreative.com/', { source: 'linkedin', medium: 'organic_social', campaign: 'a_b' }), /must be https/);
});

test('readParams extracts and caps, and ignores non-utm keys', () => {
  const params = readParams('https://sklarzcreative.com/?utm_source=x&ref=abc&utm_content=' + 'a'.repeat(200));
  assert.deepEqual(Object.keys(params).sort(), ['utm_content', 'utm_source']);
  assert.equal(params.utm_content.length, 120, 'capped to the length the capture endpoint stores');
  assert.equal(params.ref, undefined);
});

test('the auditor finds every problem in one pass rather than the first', () => {
  const findings = auditUrl('https://sklarzcreative.com/?utm_source=LinkedIn&utm_medium=Social');
  const messages = findings.map(f => f.message).join(' | ');
  assert.match(messages, /utm_campaign is missing/);
  assert.match(messages, /utm_content is missing/);
  assert.match(messages, /not lower snake_case/);
  assert.match(messages, /outside the vocabulary/);
  assert.ok(findings.some(f => f.severity === 'error'));
});

test('an untagged link is reported as information, not as an error', () => {
  const findings = auditUrl('https://sklarzcreative.com/');
  assert.equal(findings.length, 1);
  assert.equal(findings[0].severity, 'info');
  assert.match(findings[0].message, /direct\/none/);
});

test('a conforming link audits clean', () => {
  const url = buildUrl(SCORECARD, { source: 'newsletter', medium: 'email', campaign: 'newsletter_growth', content: 'issue_014' });
  const findings = auditUrl(url);
  assert.deepEqual(findings.map(f => f.severity), ['info']);
  assert.match(findings[0].message, /conforms/);
});

test('every vocabulary key is itself lower snake_case', () => {
  // The vocabulary cannot violate the rule it enforces.
  for (const key of [...Object.keys(SOURCES), ...Object.keys(MEDIUMS)]) {
    assert.match(key, /^[a-z0-9]+(?:_[a-z0-9]+)*$/, `${key} breaks its own convention`);
  }
});
