/**
 * Consent. One function, because there must be exactly one answer to
 * "may we email this person".
 *
 * WHY A WHOLE MODULE FOR ONE COMPARISON
 * Every accidental-enrolment story is the same story: the check was written
 * inline, twice, slightly differently. One place read `=== 'yes'`, another read
 * `truthy`, and a spreadsheet somewhere produced `TRUE`. Both looked correct in
 * review. The person who ticked nothing got the email.
 *
 * THE RULE
 * Only the exact string "yes" — trimmed, case-insensitive — is consent.
 * Everything else is not, INCLUDING every value that looks like a yes:
 * true, "true", "TRUE", 1, "1", "y", "Y", "on", "checked", "opted_in".
 *
 * That is deliberate and it is not pedantry. A boolean `true` in this field
 * means some system converted a value on this person's behalf, and a
 * conversion nobody reviewed is exactly what must not be trusted with someone's
 * inbox. The correct response to `true` is to fix the writer, not to widen the
 * reader.
 *
 * Consent is never inferred from behaviour. Completing the Scorecard is not
 * consent. Clicking the discovery-call link is not consent. Replying to an
 * email is not consent to a sequence. Ticking the box is consent.
 */

export const CONSENT_YES = 'yes';
export const CONSENT_NO = 'no';

/**
 * The only consent check in the system.
 *
 * @param {unknown} rawValue the value exactly as stored, unconverted
 * @returns {boolean} true only for the string "yes"
 */
export function hasFollowUpConsent(rawValue) {
  return typeof rawValue === 'string' && rawValue.trim().toLowerCase() === CONSENT_YES;
}

/**
 * The same decision, with its reasoning attached — for audit logs, where the
 * raw value matters as much as the verdict. A wrong enrolment must be
 * traceable to a value rather than argued about.
 *
 * @returns {{ enrol: boolean, raw: unknown, normalised: string, reason: string }}
 */
export function consentDecision(rawValue) {
  const raw = rawValue;
  if (hasFollowUpConsent(raw)) {
    return { enrol: true, raw, normalised: CONSENT_YES, reason: 'explicit opt-in recorded as "yes"' };
  }
  if (raw === undefined || raw === null || raw === '') {
    return {
      enrol: false, raw, normalised: CONSENT_NO,
      reason: 'no value recorded — absence of a no is not a yes'
    };
  }
  if (typeof raw !== 'string') {
    return {
      enrol: false, raw, normalised: CONSENT_NO,
      reason: `value is a ${typeof raw}, not the string "yes" — some system converted this, and a conversion nobody reviewed is not consent. Fix the writer.`
    };
  }
  return {
    enrol: false, raw, normalised: CONSENT_NO,
    reason: `value "${raw}" is not "yes" — only an exact yes enrols anyone`
  };
}

/**
 * Split a set of lead rows into who may be emailed and who may not, with a
 * reason for every exclusion. There is no third bucket and no "probably".
 *
 * @param {Array<object>} rows lead rows, each with a follow_up_opt_in field
 * @param {string} [field]
 */
export function partitionByConsent(rows, field = 'follow_up_opt_in') {
  const enrol = [];
  const exclude = [];
  for (const row of rows || []) {
    const decision = consentDecision(row?.[field]);
    (decision.enrol ? enrol : exclude).push({ row, decision });
  }
  return { enrol, exclude };
}

/**
 * A guard to call immediately before any send. It throws rather than returning
 * false, because at the point of sending there is no sensible way to continue
 * and a returned false is a value someone can forget to check.
 */
export function assertMayEmail(row, field = 'follow_up_opt_in') {
  const decision = consentDecision(row?.[field]);
  if (!decision.enrol) {
    throw new Error(
      `Refusing to email ${row?.lead_id ?? '<unknown lead>'}: ${decision.reason}. ` +
      'The lead is still captured. Enrolling someone who declined is the single outcome the checkbox exists to prevent.'
    );
  }
  return true;
}
