/**
 * Trust-First Content Scorecard — lead capture endpoint
 * Google Apps Script, bound to a Google Sheet.
 *
 * WHY THIS AND NOT A FORM SERVICE
 * The submissions land in a spreadsheet inside the Sklarz Creative Google
 * account. No third party processes or stores the leads, the export is the
 * sheet itself, and Make.com reads Google Sheets natively when the follow-up
 * sequence gets wired up. It is free at any volume this tool will see.
 *
 * SETUP — this is the one manual step. Roughly five minutes.
 *   1. Create a Google Sheet named e.g. "Sklarz Creative — Scorecard leads".
 *   2. Extensions → Apps Script. Delete the placeholder, paste this file.
 *   3. Deploy → New deployment → type "Web app".
 *        Execute as:       Me
 *        Who has access:   Anyone
 *      "Anyone" is required: visitors are not signed in to Google. The URL is
 *      a public write-only endpoint, not a credential — it can receive data
 *      and returns nothing readable.
 *   4. Copy the /exec URL.
 *   5. Paste it into window.TFCS_CAPTURE.endpoint in
 *      insights/resources/trust-first-content-scorecard/index.html
 *      and leave mode as 'opaque'. Commit and push.
 *
 * NOTHING ELSE IN THE REPOSITORY NEEDS TO CHANGE, and no key goes near the
 * front end.
 */

/** Header row, in order. Edit here and delete the sheet's first row to reset. */
var HEADERS = [
  'timestamp', 'first_name', 'email', 'follow_up_opt_in',
  'resource', 'page', 'dwell_ms', 'spam_reason'
];

/** A submission faster than this is not a human filling in two fields. */
var MIN_DWELL_MS = 1500;

function doPost(e) {
  try {
    var body = {};
    if (e && e.postData && e.postData.contents) {
      body = JSON.parse(e.postData.contents);
    }

    var reason = spamReason_(body);
    if (reason) {
      // Recorded rather than silently dropped, so a false positive is visible.
      append_(body, reason);
      return reply_({ ok: true });
    }

    append_(body, '');
    return reply_({ ok: true });
  } catch (err) {
    // Never surface a stack trace to a public endpoint.
    return reply_({ ok: false });
  }
}

/** The endpoint is write-only. A GET should not enumerate anything. */
function doGet() {
  return reply_({ ok: true });
}

function spamReason_(body) {
  if (body.company_website) return 'honeypot';
  var dwell = Number(body.dwell_ms);
  if (isFinite(dwell) && dwell > 0 && dwell < MIN_DWELL_MS) return 'too_fast';
  var email = String(body.email || '');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return 'bad_email';
  if (!String(body.first_name || '').trim()) return 'no_name';
  return '';
}

function append_(body, spamReason) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }

  sheet.appendRow([
    new Date(),
    String(body.first_name || '').slice(0, 120),
    String(body.email || '').slice(0, 240),
    body.follow_up_opt_in === 'yes' ? 'yes' : 'no',
    String(body.resource || '').slice(0, 120),
    String(body.page || '').slice(0, 240),
    Number(body.dwell_ms) || '',
    spamReason
  ]);
}

function reply_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
