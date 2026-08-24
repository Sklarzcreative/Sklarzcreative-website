#!/usr/bin/env node
/**
 * Run the publishing-reliability analysis against a queue export.
 *
 * WHY AN EXPORT AND NOT A LIVE READ
 * Reading `MAKE - Publish Queue` directly needs a Google credential, and no
 * credential belongs in a public repository. So the analysis takes a file. That
 * is a real limitation and it is stated in the output rather than worked around:
 * this tool cannot notice a publishing failure on its own — a human or a Make
 * scenario has to hand it the snapshot.
 *
 * It also makes the analysis reproducible. The same snapshot and the same `now`
 * always produce the same report, which is what you want at 8am during an
 * incident.
 *
 * USAGE
 *   node automation/scripts/audit-queue.mjs <queue-export.json> [--now=ISO] [--json]
 *
 * The export is a JSON array of rows matching
 * automation/schemas/publish-queue-row.schema.json. To produce it from the
 * spreadsheet: File > Download > CSV, then convert (any CSV-to-JSON tool), or
 * paste the rows from a Make "Search Rows" run.
 *
 * IT WRITES NOTHING ANYWHERE. It reads a file and prints a report.
 */
import { readFileSync } from 'node:fs';
import { auditQueue } from '../lib/queue-audit.mjs';
import { validate } from '../lib/validate.mjs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

/** Routes cleared by runbooks/route-onboarding.md as of 24 August 2026. */
const ONBOARDED = ['linkedin', 'linkedin_company', 'instagram', 'facebook', 'threads', 'x', 'pinterest'];

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--'));
const nowArg = args.find(a => a.startsWith('--now='))?.slice(6);
const asJson = args.includes('--json');

if (!file) {
  console.error(`usage: node automation/scripts/audit-queue.mjs <queue-export.json> [--now=ISO] [--json]

The export is a JSON array of publish-queue rows. Onboarded routes are
${ONBOARDED.join(', ')} — anything else reports as not_onboarded.`);
  process.exit(2);
}

let rows;
try {
  rows = JSON.parse(readFileSync(file, 'utf8'));
} catch (err) {
  console.error(`could not read ${file}: ${err.message}`);
  process.exit(2);
}
if (!Array.isArray(rows)) {
  console.error('the export must be a JSON array of rows');
  process.exit(2);
}

// Strip the _comment key the committed examples carry for readers.
rows = rows.map(r => Object.fromEntries(Object.entries(r).filter(([k]) => k !== '_comment')));

/* Validate first. A malformed row analysed silently produces a confident wrong
   answer, which during an incident is worse than a refusal. */
const schema = JSON.parse(readFileSync(join(HERE, '..', 'schemas', 'publish-queue-row.schema.json'), 'utf8'));
const invalid = [];
rows.forEach((row, i) => {
  const { valid, errors } = validate(row, schema);
  if (!valid) invalid.push({ index: i, row_id: row.row_id ?? null, errors });
});

const report = auditQueue(rows, {
  now: nowArg ?? new Date().toISOString(),
  onboardedRoutes: ONBOARDED
});

if (asJson) {
  console.log(JSON.stringify({ ...report, invalid_rows: invalid }, null, 2));
  process.exit(report.findings.some(f => f.severity === 'critical') ? 1 : 0);
}

const line = '─'.repeat(72);
console.log(`\nPUBLISH QUEUE RELIABILITY — ${report.analysed_at}`);
console.log(`snapshot: ${file}`);
console.log(line);

if (invalid.length) {
  console.log(`\n${invalid.length} row(s) failed schema validation. Analysis continues, but treat`);
  console.log('their findings with suspicion — a malformed row is a data-quality problem in itself.');
  for (const bad of invalid.slice(0, 10)) {
    console.log(`  row ${bad.row_id ?? `#${bad.index}`}: ${bad.errors.map(e => `${e.path || '#'} ${e.message}`).join('; ')}`);
  }
}

console.log(`\nrows ${report.queue_total} · approved waiting ${report.approved_waiting} · HOLD ${report.hold_count} · OVERDUE ${report.overdue_count}`);
console.log(`by status: ${Object.entries(report.counts_by_status).map(([k, v]) => `${k} ${v}`).join(' · ')}`);

const bySeverity = { critical: [], warning: [], info: [] };
for (const f of report.findings) bySeverity[f.severity].push(f);

for (const severity of ['critical', 'warning']) {
  if (!bySeverity[severity].length) continue;
  console.log(`\n${severity.toUpperCase()} (${bySeverity[severity].length})`);
  console.log(line);
  for (const f of bySeverity[severity]) {
    console.log(`  ${f.check}  ${f.row_id ? `row ${f.row_id}` : ''}${f.platform ? ` · ${f.platform}` : ''}`);
    console.log(`    ${f.message}`);
  }
}

if (bySeverity.info.length) {
  const holds = bySeverity.info.filter(f => f.check === 'hold');
  if (holds.length) {
    console.log(`\nON HOLD (${holds.length}) — a human decision, not a failure. Listed so the count is not mistaken for a backlog.`);
    console.log(line);
    console.log(`  rows: ${holds.map(f => f.row_id).join(', ')}`);
  }
}

console.log('\nROUTE HEALTH');
console.log(line);
for (const [platform, health] of Object.entries(report.route_health)) {
  const bits = [`verified ${health.verified_publishes}`, `failures ${health.failures}`, `overdue ${health.overdue}`];
  console.log(`  ${platform.padEnd(18)}${health.status.padEnd(15)}${bits.join(' · ')}`);
  if (health.note) console.log(`  ${' '.repeat(18)}${health.note}`);
}

console.log('\nRECOMMENDED NEXT ACTIONS');
console.log(line);
for (const action of report.recommended_next_actions) console.log(`  ${action}`);
console.log('');

process.exit(bySeverity.critical.length ? 1 : 0);
