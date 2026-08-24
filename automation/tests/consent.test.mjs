/**
 * Consent tests.
 *
 * This is the most important test file in the repository. Everything else here
 * protects a metric or a page; this protects a person's inbox from a message
 * they did not ask for — which is the one failure that cannot be corrected by
 * pushing a fix.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hasFollowUpConsent, consentDecision, partitionByConsent, assertMayEmail } from '../lib/consent.mjs';

test('the exact string "yes" is consent', () => {
  assert.equal(hasFollowUpConsent('yes'), true);
});

test('case and surrounding whitespace do not defeat a real yes', () => {
  for (const value of ['Yes', 'YES', 'yEs', ' yes', 'yes ', '\tyes\n']) {
    assert.equal(hasFollowUpConsent(value), true, `expected "${value}" to be consent`);
  }
});

test('every value that merely LOOKS like a yes is not consent', () => {
  // Each of these has been mistaken for consent in some system somewhere.
  // A boolean true means something converted the value on the person's behalf,
  // and a conversion nobody reviewed is exactly what must not be trusted here.
  const lookalikes = [
    true, 'true', 'TRUE', 'True',
    1, '1', 'y', 'Y', 'on', 'checked', 'opted_in', 'opt_in',
    'yes please', 'yes,', 'yess', 'oui', 'si',
    'YES!'
  ];
  for (const value of lookalikes) {
    assert.equal(
      hasFollowUpConsent(value), false,
      `${JSON.stringify(value)} must NOT be treated as consent`
    );
  }
});

test('absence is not consent', () => {
  for (const value of ['', ' ', null, undefined, 0, false, [], {}, NaN]) {
    assert.equal(hasFollowUpConsent(value), false, `${JSON.stringify(value)} must not be consent`);
  }
});

test('an explicit no is a no', () => {
  for (const value of ['no', 'NO', 'No', ' no ']) {
    assert.equal(hasFollowUpConsent(value), false);
  }
});

test('the decision carries the raw value, so a wrong enrolment is traceable', () => {
  const d = consentDecision('TRUE');
  assert.equal(d.enrol, false);
  assert.equal(d.raw, 'TRUE');
  assert.equal(d.normalised, 'no');
  assert.match(d.reason, /not "yes"/);

  const empty = consentDecision('');
  assert.equal(empty.enrol, false);
  assert.match(empty.reason, /absence of a no is not a yes/);

  const converted = consentDecision(true);
  assert.equal(converted.enrol, false);
  assert.match(converted.reason, /Fix the writer/);
});

test('partitioning never puts a non-yes in the enrol bucket', () => {
  const rows = [
    { lead_id: 'a', follow_up_opt_in: 'yes' },
    { lead_id: 'b', follow_up_opt_in: 'no' },
    { lead_id: 'c', follow_up_opt_in: '' },
    { lead_id: 'd', follow_up_opt_in: true },
    { lead_id: 'e' },
    { lead_id: 'f', follow_up_opt_in: ' YES ' }
  ];
  const { enrol, exclude } = partitionByConsent(rows);
  assert.deepEqual(enrol.map(e => e.row.lead_id), ['a', 'f']);
  assert.equal(exclude.length, 4);
  for (const e of exclude) assert.ok(e.decision.reason.length > 10, 'every exclusion carries a reason');
});

test('the send guard throws rather than returning false', () => {
  // A returned false is a value someone can forget to check. At the point of
  // sending there is no sensible way to continue, so it throws.
  assert.throws(
    () => assertMayEmail({ lead_id: 'x', follow_up_opt_in: 'no' }),
    /Refusing to email x/
  );
  assert.throws(() => assertMayEmail({ lead_id: 'y' }), /Refusing to email y/);
  assert.throws(() => assertMayEmail(null), /Refusing to email <unknown lead>/);
  assert.equal(assertMayEmail({ lead_id: 'z', follow_up_opt_in: 'yes' }), true);
});

test('completing the scorecard is not consent', () => {
  // Behaviour is never consent. This row finished the card and scored well;
  // it still may not be emailed.
  const row = {
    lead_id: 'behaviour',
    follow_up_opt_in: 'no',
    total_score: 38,
    completed_at: '2026-08-24T10:00:00Z',
    discovery_call_clicked: true
  };
  assert.equal(hasFollowUpConsent(row.follow_up_opt_in), false);
  assert.throws(() => assertMayEmail(row));
});
