/**
 * Schema tests. Two jobs:
 *   1. every committed example validates against its schema, so the examples
 *      cannot rot into documentation that lies;
 *   2. the rules the schemas exist to enforce actually fail. A schema that
 *      accepts the thing it was written to reject is worse than no schema,
 *      because it produces a passing validation nobody checks.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { validate } from '../lib/validate.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = p => JSON.parse(readFileSync(join(root, p), 'utf8'));
const schema = name => readJson(`schemas/${name}.schema.json`);

/** Examples carry a _comment key for the reader; strip it before validating. */
const strip = obj => Object.fromEntries(Object.entries(obj).filter(([k]) => k !== '_comment'));

test('every schema file is valid JSON with an $id and a description', () => {
  const files = readdirSync(join(root, 'schemas')).filter(f => f.endsWith('.schema.json'));
  assert.ok(files.length >= 7, `expected at least 7 schemas, found ${files.length}`);
  for (const file of files) {
    const s = readJson(`schemas/${file}`);
    assert.ok(s.$id, `${file} has no $id`);
    assert.ok(s.title, `${file} has no title`);
    assert.ok(s.description && s.description.length > 40, `${file} needs a description explaining what it is for`);
  }
});

test('the distribution pack example validates', () => {
  const { valid, errors } = validate(readJson('examples/distribution-pack.example.json'), schema('distribution-pack'));
  assert.ok(valid, JSON.stringify(errors, null, 2));
});

test('the health report example validates', () => {
  const { valid, errors } = validate(readJson('examples/automation-health-report.example.json'), schema('automation-health-report'));
  assert.ok(valid, JSON.stringify(errors, null, 2));
});

test('the weekly performance example validates', () => {
  const { valid, errors } = validate(readJson('examples/weekly-performance-report.example.json'), schema('weekly-performance-report'));
  assert.ok(valid, JSON.stringify(errors, null, 2));
});

test('the missing-evidence case study example validates', () => {
  const { valid, errors } = validate(readJson('examples/case-study.missing-evidence.example.json'), schema('case-study'));
  assert.ok(valid, JSON.stringify(errors, null, 2));
});

test('every lead record example validates', () => {
  const s = schema('lead-record');
  for (const row of readJson('examples/lead-record.examples.json')) {
    const { valid, errors } = validate(strip(row), s);
    assert.ok(valid, `${row.lead_id}: ${JSON.stringify(errors)}`);
  }
});

test('every publish queue example validates', () => {
  const s = schema('publish-queue-row');
  for (const row of readJson('examples/publish-queue-rows.examples.json')) {
    const { valid, errors } = validate(strip(row), s);
    assert.ok(valid, `${row.row_id}: ${JSON.stringify(errors)}`);
  }
});

/* ------------------------------------------- the rules must actually bite --- */

test('a lead record rejects any consent value other than yes or no', () => {
  const s = schema('lead-record');
  const base = {
    lead_id: 'x', timestamp: '2026-08-24T00:00:00Z', first_name: 'A',
    email: 'a@b.test', resource: 'Trust-First Content Scorecard'
  };
  for (const bad of ['YES', 'true', '1', 'y', '']) {
    assert.equal(validate({ ...base, follow_up_opt_in: bad }, s).valid, false, `"${bad}" must not validate`);
  }
  assert.equal(validate({ ...base, follow_up_opt_in: 'yes' }, s).valid, true);
  assert.equal(validate({ ...base, follow_up_opt_in: 'no' }, s).valid, true);
});

test('a lead record rejects a score outside the instrument range', () => {
  const s = schema('lead-record');
  const base = {
    lead_id: 'x', timestamp: '2026-08-24T00:00:00Z', first_name: 'A',
    email: 'a@b.test', resource: 'r', follow_up_opt_in: 'no'
  };
  assert.equal(validate({ ...base, total_score: 41 }, s).valid, false);
  assert.equal(validate({ ...base, clarity_score: 9 }, s).valid, false);
  assert.equal(validate({ ...base, total_score: null }, s).valid, true, 'null is the correct value for an unfinished card');
  assert.equal(validate({ ...base, total_score: 0 }, s).valid, true, '0 is a measured zero and is legitimate');
});

test('a case study cannot declare itself publishable', () => {
  // There is no automated path from "the fields are filled in" to "this is on
  // the website making claims about a real client".
  const s = schema('case-study');
  const doc = readJson('examples/case-study.missing-evidence.example.json');
  assert.equal(validate({ ...doc, publishable: true }, s).valid, false);
});

test('a case study outcome cannot be a bare hedge', () => {
  const s = schema('case-study');
  const doc = readJson('examples/case-study.missing-evidence.example.json');
  // Prose is not a valid outcome — the outcome needs observable, verifiable_by
  // and measured, or the literal MISSING EVIDENCE.
  const hedged = structuredClone(doc);
  hedged.sections.observable_outcome = 'Early results were encouraging and the client was pleased.';
  assert.equal(validate(hedged, s).valid, false, 'a hedge must not validate as an outcome');

  const honest = structuredClone(doc);
  honest.sections.observable_outcome = {
    observable: 'The positioning document was adopted and is still in use.',
    verifiable_by: 'The client can confirm it is the document in use.',
    measured: false
  };
  assert.equal(validate(honest, s).valid, true, 'an unmeasured but observable outcome is legitimate');
});

test('a case study decision requires the rejected alternative', () => {
  const s = schema('case-study');
  const doc = structuredClone(readJson('examples/case-study.missing-evidence.example.json'));
  doc.sections.strategic_decision = { decision: 'We narrowed the positioning to one buyer.' };
  assert.equal(validate(doc, s).valid, false, 'a decision with no discarded option must not validate');

  doc.sections.strategic_decision.alternative_rejected = 'Keeping three buyer segments and writing for all of them.';
  assert.equal(validate(doc, s).valid, true);
});

test('a performance metric cannot be a number without a source', () => {
  // This is the no-fabrication rule, enforced mechanically rather than trusted.
  const s = schema('weekly-performance-report');
  const doc = structuredClone(readJson('examples/weekly-performance-report.example.json'));
  doc.funnel.leads = { value: 42 };
  assert.equal(validate(doc, s).valid, false, 'a bare number must not validate');

  doc.funnel.leads = { value: 42, data_source: 'lead sheet', retrieved_at: '2026-08-24T05:00:00Z' };
  assert.equal(validate(doc, s).valid, true);

  doc.funnel.leads = { value: 'NOT AVAILABLE' };
  assert.equal(validate(doc, s).valid, false, 'NOT AVAILABLE must carry a reason');

  doc.funnel.leads = { value: 'NOT AVAILABLE', reason: 'capture is switched off' };
  assert.equal(validate(doc, s).valid, true);
});

test('a distribution pack derivative cannot claim two primary jobs', () => {
  const s = schema('distribution-pack');
  const pack = structuredClone(readJson('examples/distribution-pack.example.json'));
  pack.derivatives[0].primary_job = ['authority', 'traffic'];
  assert.equal(validate(pack, s).valid, false);
});

test('a distribution pack derivative cannot be marked approved or published', () => {
  const s = schema('distribution-pack');
  for (const status of ['approved', 'scheduled', 'published', 'APPROVED']) {
    const pack = structuredClone(readJson('examples/distribution-pack.example.json'));
    pack.derivatives[0].status = status;
    assert.equal(validate(pack, s).valid, false, `an agent must not be able to write status "${status}"`);
  }
});

test('a distribution pack cannot exist for an unapproved source', () => {
  const s = schema('distribution-pack');
  const pack = structuredClone(readJson('examples/distribution-pack.example.json'));
  pack.source.approved = false;
  assert.equal(validate(pack, s).valid, false);
});

test('a distribution pack link must be on the apex and lower snake_case', () => {
  const s = schema('distribution-pack');
  const pack = structuredClone(readJson('examples/distribution-pack.example.json'));
  pack.canonical_url = 'https://www.sklarzcreative.com/';
  assert.equal(validate(pack, s).valid, false, 'www is not canonical');

  const drift = structuredClone(readJson('examples/distribution-pack.example.json'));
  drift.derivatives[0].link.utm.utm_source = 'LinkedIn';
  assert.equal(validate(drift, s).valid, false);
});

test('a QA report cannot report a skipped check as a pass', () => {
  const s = schema('qa-report');
  const base = {
    schema_version: '1.0', generated_at: '2026-08-24T00:00:00Z', harness_version: '1.0.0',
    git: { sha: 'abc', branch: 'main' },
    mode: { static: true, rendered: false, behaviour: false, live: false },
    routes: ['/'],
    totals: { checks: 1, pass: 0, error: 0, warning: 0, info: 0, skipped: 1 },
    findings: [{ check: 'live.redirect', severity: 'skipped', message: 'not run', reason: 'no network' }],
    verdict: { status: 'incomplete', exit_code: 0 }
  };
  assert.equal(validate(base, s).valid, true);

  const bad = structuredClone(base);
  bad.findings[0].severity = 'pass';
  assert.equal(validate(bad, s).valid, false, '"pass" is not a finding severity — a pass is the absence of a finding');
});

test('a QA report requires a git SHA field, so it is attributable to a state of the code', () => {
  const s = schema('qa-report');
  const doc = {
    schema_version: '1.0', generated_at: '2026-08-24T00:00:00Z', harness_version: '1.0.0',
    mode: { static: true, rendered: false, behaviour: false, live: false },
    routes: [], totals: { checks: 0, pass: 0, error: 0, warning: 0, info: 0, skipped: 0 },
    findings: [], verdict: { status: 'pass', exit_code: 0 }
  };
  assert.equal(validate(doc, s).valid, false, 'git is required');
});

test('a health report count may be null but never negative', () => {
  const s = schema('automation-health-report');
  const doc = structuredClone(readJson('examples/automation-health-report.example.json'));
  doc.publishing.overdue_count = -1;
  assert.equal(validate(doc, s).valid, false);
  doc.publishing.overdue_count = null;
  assert.equal(validate(doc, s).valid, true, 'null is the correct value for an unmeasured count');
});

test('a health report route cannot be healthy by default when nothing was read', () => {
  const s = schema('automation-health-report');
  const doc = structuredClone(readJson('examples/automation-health-report.example.json'));
  doc.publishing.platform_route_health.linkedin.status = 'probably_fine';
  assert.equal(validate(doc, s).valid, false, 'only the enumerated statuses exist');
});
