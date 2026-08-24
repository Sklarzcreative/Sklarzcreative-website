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
 * WHAT LANDS IN THE SHEET
 * One row per person. The capture creates it with name, email, consent and any
 * campaign parameters; if they go on to finish the twenty statements, the five
 * category scores, the total, the band and the weakest signal are written onto
 * that same row. That is what lets a follow-up email name the weakest signal
 * instead of guessing.
 *
 * NOTHING ELSE IN THE REPOSITORY NEEDS TO CHANGE, and no key goes near the
 * front end.
 */

/**
 * Header row, in order. Edit here and delete the sheet's first row to reset.
 *
 * `sequence_state` is the one column this script never writes. It belongs to
 * Make.com, which stamps it once it has handed a row to the email platform.
 * Without it a scheduled scenario has no way to tell a new lead from one it
 * already processed, and it re-sends Day 0 on every run — so the column is
 * cheaper than the alternative of Make guessing from timestamps.
 */
var HEADERS = [
  'timestamp', 'submission_id', 'first_name', 'email', 'follow_up_opt_in',
  'resource', 'page',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'total_score', 'clarity', 'consistency', 'credibility', 'connection',
  'conversion', 'weakest_signal', 'band', 'completed_at',
  'dwell_ms', 'spam_reason', 'sequence_state'
];

/** Which column holds what, derived from HEADERS so the two cannot drift. */
function col_(name) { return HEADERS.indexOf(name) + 1; }

/** A submission faster than this is not a human filling in two fields. */
var MIN_DWELL_MS = 1500;

function doPost(e) {
  try {
    var body = {};
    if (e && e.postData && e.postData.contents) {
      body = JSON.parse(e.postData.contents);
    }

    /* Two kinds of message. A capture creates the row; a result fills in the
       score columns on the row the capture created. Keeping one row per person
       means the sheet is the export and Make.com has one thing to watch. */
    if (body.event === 'result') {
      recordResult_(body);
      return reply_({ ok: true });
    }

    var reason = spamReason_(body);
    // Recorded rather than silently dropped, so a false positive is visible.
    append_(body, reason);
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

function sheet_() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function str_(v, n) { return String(v == null ? '' : v).slice(0, n); }

function append_(body, spamReason) {
  var sheet = sheet_();
  var row = [];
  row[col_('timestamp') - 1]        = new Date();
  row[col_('submission_id') - 1]    = str_(body.submission_id, 80);
  row[col_('first_name') - 1]       = str_(body.first_name, 120);
  row[col_('email') - 1]            = str_(body.email, 240);
  row[col_('follow_up_opt_in') - 1] = body.follow_up_opt_in === 'yes' ? 'yes' : 'no';
  row[col_('resource') - 1]         = str_(body.resource, 120);
  row[col_('page') - 1]             = str_(body.page, 240);
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
    .forEach(function (k) { row[col_(k) - 1] = str_(body[k], 120); });
  row[col_('dwell_ms') - 1]         = Number(body.dwell_ms) || '';
  row[col_('spam_reason') - 1]      = spamReason;

  for (var i = 0; i < HEADERS.length; i++) if (row[i] === undefined) row[i] = '';
  sheet.appendRow(row);
}

/**
 * Write the finished scores onto the row its capture created.
 *
 * If no matching row exists — the visitor completed the card without ever
 * submitting the form, and reportAnonymous is on — the result is appended as a
 * standalone row with no name or email. That gives a completion rate without
 * attaching it to a person.
 */
function recordResult_(body) {
  var sheet = sheet_();
  var id = str_(body.submission_id, 80);
  var scores = {
    total_score: Number(body.total),
    clarity: Number(body.clarity),
    consistency: Number(body.consistency),
    credibility: Number(body.credibility),
    connection: Number(body.connection),
    conversion: Number(body.conversion),
    weakest_signal: str_(body.weakest_signal, 60),
    band: str_(body.band, 60),
    completed_at: str_(body.completed_at, 40)
  };

  var rowIndex = id ? findRowById_(sheet, id) : 0;

  if (!rowIndex) {
    var row = [];
    row[col_('timestamp') - 1]     = new Date();
    row[col_('submission_id') - 1] = id;
    row[col_('resource') - 1]      = 'Trust-First Content Scorecard';
    row[col_('spam_reason') - 1]   = id ? 'result_without_capture' : 'anonymous_result';
    Object.keys(scores).forEach(function (k) { row[col_(k) - 1] = scores[k]; });
    for (var i = 0; i < HEADERS.length; i++) if (row[i] === undefined) row[i] = '';
    sheet.appendRow(row);
    return;
  }

  Object.keys(scores).forEach(function (k) {
    sheet.getRange(rowIndex, col_(k)).setValue(scores[k]);
  });
}

function findRowById_(sheet, id) {
  var last = sheet.getLastRow();
  if (last < 2) return 0;
  var ids = sheet.getRange(2, col_('submission_id'), last - 1, 1).getValues();
  for (var i = ids.length - 1; i >= 0; i--) {          // newest first
    if (String(ids[i][0]) === id) return i + 2;
  }
  return 0;
}

function reply_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
