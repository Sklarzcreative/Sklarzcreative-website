/**
 * Publish-queue reliability tests.
 *
 * Two of these are the reason the module exists: HOLD must never be treated as
 * a failure, and a bulk release must never be recommended. Both are asserted
 * against the recommendation text itself, not against an intention.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  auditQueue, overdueApproved, holds, missingAssets, publishedWithoutUrl,
  staleTransient, duplicateRisk, failurePatterns, routeHealth, unknownStatus,
  CONTROLLED_RELEASE_RECOMMENDATION, DEFAULTS
} from '../lib/queue-audit.mjs';

const NOW = Date.parse('2026-08-24T06:00:00Z');

test('an approved item past its time with no error is the silent failure', () => {
  const rows = [{ row_id: 'A', platform: 'linkedin', content_id: 'c1', status: 'APPROVED', scheduled_at: '2026-08-21T09:00:00Z' }];
  const found = overdueApproved(rows, NOW, DEFAULTS);
  assert.equal(found.length, 1);
  assert.equal(found[0].severity, 'critical');
  assert.equal(found[0].check, 'overdue_approved');
  assert.ok(found[0].overdue_by_hours > 60);
  assert.match(found[0].message, /ran silently/);
});

test('the grace period is generous enough that a normal scheduler never trips it', () => {
  const rows = [{ row_id: 'A', platform: 'x', content_id: 'c', status: 'APPROVED', scheduled_at: '2026-08-24T05:30:00Z' }];
  assert.equal(overdueApproved(rows, NOW, DEFAULTS).length, 0, '30 minutes late is not overdue');
});

test('HOLD is never a failure and never an action item', () => {
  const rows = [
    { row_id: 'H1', platform: 'x', content_id: 'c1', status: 'HOLD', scheduled_at: '2026-08-01T09:00:00Z' },
    { row_id: 'H2', platform: 'x', content_id: 'c2', status: 'HOLD', scheduled_at: '2026-07-01T09:00:00Z' }
  ];
  assert.equal(overdueApproved(rows, NOW, DEFAULTS).length, 0, 'a very old HOLD is still not overdue');
  const held = holds(rows);
  assert.equal(held.length, 2);
  for (const h of held) assert.equal(h.severity, 'info');

  const report = auditQueue(rows, { now: NOW });
  assert.equal(report.hold_count, 2);
  assert.equal(report.overdue_count, 0);
  assert.equal(report.findings.filter(f => f.severity === 'critical').length, 0);
});

test('a backlog produces the controlled-release sequence and never a bulk release', () => {
  const rows = Array.from({ length: 12 }, (_, i) => ({
    row_id: `Q${i}`, content_id: `c${i}`, platform: 'linkedin',
    status: 'APPROVED', scheduled_at: '2026-08-10T09:00:00Z', target_url: 'https://sklarzcreative.com/'
  }));
  const report = auditQueue(rows, { now: NOW });
  assert.equal(report.overdue_count, 12);

  const text = report.recommended_next_actions.join('\n');
  assert.match(text, /Do NOT release the backlog/);
  for (const step of CONTROLLED_RELEASE_RECOMMENDATION) {
    assert.ok(text.includes(step), `controlled-release step missing: ${step}`);
  }
  // The rule, asserted against the output rather than trusted.
  assert.doesNotMatch(text, /publish (all|every|everything)/i);
  assert.doesNotMatch(text, /release (all|the whole|everything overdue)/i);
  assert.doesNotMatch(text, /run all/i);
});

test('PUBLISHED without a published_url is never counted as a success', () => {
  const rows = [{ row_id: 'P', content_id: 'c', platform: 'threads', status: 'PUBLISHED', published_url: null, updated_at: '2026-08-23T10:00:00Z' }];
  const found = publishedWithoutUrl(rows);
  assert.equal(found.length, 1);
  assert.equal(found[0].severity, 'critical');

  const health = routeHealth(rows, NOW, DEFAULTS);
  assert.equal(health.threads.verified_publishes, 0);
  assert.equal(health.threads.published_without_url, 1);
  assert.equal(health.threads.status, 'degraded');
});

test('a media-required platform with no asset is caught before its time, and escalates after', () => {
  const future = missingAssets([{ row_id: 'F', content_id: 'c', platform: 'instagram', status: 'APPROVED', scheduled_at: '2026-08-30T09:00:00Z' }], NOW, DEFAULTS);
  assert.equal(future[0].severity, 'warning');
  assert.match(future[0].message, /still fixable/);

  const past = missingAssets([{ row_id: 'P', content_id: 'c', platform: 'instagram', status: 'APPROVED', scheduled_at: '2026-08-20T09:00:00Z' }], NOW, DEFAULTS);
  assert.equal(past[0].severity, 'critical');

  const withAsset = missingAssets([{ row_id: 'W', content_id: 'c', platform: 'instagram', status: 'APPROVED', scheduled_at: '2026-08-30T09:00:00Z', asset_ref: 'drive://x.png' }], NOW, DEFAULTS);
  assert.equal(withAsset.length, 0);

  const textOnly = missingAssets([{ row_id: 'T', content_id: 'c', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-30T09:00:00Z' }], NOW, DEFAULTS);
  assert.equal(textOnly.length, 0, 'LinkedIn does not require media');
});

test('a transient status left stale means a run died mid-flight', () => {
  const stale = staleTransient([{ row_id: 'S', content_id: 'c', platform: 'facebook', status: 'SENDING', updated_at: '2026-08-24T01:00:00Z' }], NOW, DEFAULTS);
  assert.equal(stale.length, 1);
  assert.equal(stale[0].severity, 'critical');

  const fresh = staleTransient([{ row_id: 'S', content_id: 'c', platform: 'facebook', status: 'SENDING', updated_at: '2026-08-24T05:45:00Z' }], NOW, DEFAULTS);
  assert.equal(fresh.length, 0, 'a status a few minutes old is simply in flight');
});

test('duplicate risk is reported as risk, because a deliberate repost is legitimate', () => {
  const near = duplicateRisk([
    { row_id: 'D1', content_id: 'same', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-24T09:00:00Z' },
    { row_id: 'D2', content_id: 'same', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-24T15:00:00Z' }
  ], DEFAULTS);
  assert.equal(near.length, 1);
  assert.equal(near[0].severity, 'warning');
  assert.match(near[0].message, /only a human knows which this is/);

  const spaced = duplicateRisk([
    { row_id: 'D1', content_id: 'same', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-01T09:00:00Z' },
    { row_id: 'D2', content_id: 'same', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-20T09:00:00Z' }
  ], DEFAULTS);
  assert.equal(spaced.length, 0, 'nineteen days apart is a repost, not a duplicate');

  const crossPlatform = duplicateRisk([
    { row_id: 'D1', content_id: 'same', platform: 'linkedin', status: 'APPROVED', scheduled_at: '2026-08-24T09:00:00Z' },
    { row_id: 'D2', content_id: 'same', platform: 'x', status: 'APPROVED', scheduled_at: '2026-08-24T09:05:00Z' }
  ], DEFAULTS);
  assert.equal(crossPlatform.length, 0, 'the same content on two platforms is the point of a distribution pack');
});

test('three failures on one route is reported as a pattern, not three incidents', () => {
  const rows = Array.from({ length: 3 }, (_, i) => ({
    row_id: `F${i}`, content_id: `c${i}`, platform: 'pinterest', status: 'FAILED',
    error: '401 Unauthorized', updated_at: '2026-08-23T07:00:00Z'
  }));
  const patterns = failurePatterns(rows, NOW, DEFAULTS);
  assert.equal(patterns.length, 1);
  assert.equal(patterns[0].failure_count, 3);
  assert.match(patterns[0].message, /points at the connection rather than the content/);

  assert.equal(failurePatterns(rows.slice(0, 2), NOW, DEFAULTS).length, 0, 'two is not yet a pattern');
});

test('a route with no activity is unknown, never healthy', () => {
  // Defaulting to healthy is how a dead route stays invisible.
  const health = routeHealth([], NOW, DEFAULTS, { onboardedRoutes: ['linkedin'] });
  assert.equal(health.linkedin.status, 'unknown');
  assert.match(health.linkedin.note, /absence of evidence/);
});

test('a platform not on the onboarded list is not_onboarded, not failing', () => {
  const health = routeHealth(
    [{ row_id: 'T', content_id: 'c', platform: 'tiktok', status: 'DRAFT' }],
    NOW, DEFAULTS,
    { onboardedRoutes: ['linkedin', 'instagram'] }
  );
  assert.equal(health.tiktok.status, 'not_onboarded');
});

test('an unrecognised status is reported verbatim, never coerced into a known bucket', () => {
  const found = unknownStatus([{ row_id: 'U', content_id: 'c', platform: 'x', status: 'Posted!' }]);
  assert.equal(found.length, 1);
  assert.equal(found[0].raw_status, 'Posted!');
  assert.match(found[0].message, /second system writing this column/);
});

test('an unreadable queue reports nulls, not a healthy empty queue', () => {
  const report = auditQueue([], { now: NOW, queueReadable: false });
  assert.equal(report.queue_readable, false);
  assert.equal(report.queue_total, null);
  assert.equal(report.overdue_count, null);
  assert.equal(report.hold_count, null);
  assert.equal(report.route_health, null);
  assert.equal(report.findings[0].check, 'queue_unreadable');
  assert.match(report.findings[0].message, /null rather than zero/);
});

test('an empty-but-readable queue is distinguishable from an unreadable one', () => {
  const report = auditQueue([], { now: NOW });
  assert.equal(report.queue_readable, true);
  assert.equal(report.queue_total, 0, 'a measured zero, not a null');
  assert.equal(report.overdue_count, 0);
});

test('the analysis instant is passed in, so a run is reproducible', () => {
  const rows = [{ row_id: 'A', content_id: 'c', platform: 'x', status: 'APPROVED', scheduled_at: '2026-08-24T05:00:00Z' }];
  assert.equal(auditQueue(rows, { now: '2026-08-24T05:30:00Z' }).overdue_count, 0);
  assert.equal(auditQueue(rows, { now: '2026-08-25T05:30:00Z' }).overdue_count, 1);
});

test('a clean queue recommends nothing rather than inventing work', () => {
  const rows = [{
    row_id: 'OK', content_id: 'c', platform: 'linkedin', status: 'PUBLISHED',
    published_url: 'https://www.linkedin.com/feed/update/urn:li:activity:1/',
    scheduled_at: '2026-08-23T09:00:00Z', updated_at: '2026-08-23T09:00:10Z'
  }];
  const report = auditQueue(rows, { now: NOW });
  assert.deepEqual(report.recommended_next_actions, ['No publishing action required from this run.']);
  assert.equal(report.findings.length, 0);
});
