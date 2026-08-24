/**
 * Finding collection and report writing.
 *
 * The design rule here is one sentence: SKIPPED IS ITS OWN STATE. A QA tool
 * that reports a check it could not run as a pass is worse than no tool,
 * because it converts an unknown into a false reassurance. So `skipped` is a
 * severity, it is counted separately, and a run with skips and no failures
 * reports `incomplete` rather than `pass`.
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export const HARNESS_VERSION = '1.0.0';

export class Findings {
  constructor() {
    this.items = [];
    this.passCount = 0;
  }

  /** A passing check is counted, not listed — fifty "ok" lines hide one failure. */
  pass(check, detail) {
    this.passCount++;
    if (process.env.QA_VERBOSE) console.log(`  pass  ${check}${detail ? ` — ${detail}` : ''}`);
    return this;
  }

  add(severity, check, message, extra = {}) {
    if (!['error', 'warning', 'info', 'skipped'].includes(severity)) {
      throw new Error(`unknown severity "${severity}" for check ${check}`);
    }
    if (severity === 'skipped' && !extra.reason) {
      // A skip with no reason is indistinguishable from a check nobody wrote.
      throw new Error(`skipped finding for "${check}" must carry a reason`);
    }
    const item = { check, severity, message, ...extra };
    for (const key of ['group', 'route', 'file', 'viewport', 'reason']) {
      if (item[key] === undefined) item[key] = null;
    }
    this.items.push(item);
    return this;
  }

  error(check, message, extra) { return this.add('error', check, message, extra); }
  warn(check, message, extra) { return this.add('warning', check, message, extra); }
  info(check, message, extra) { return this.add('info', check, message, extra); }
  skip(check, message, reason, extra = {}) { return this.add('skipped', check, message, { ...extra, reason }); }

  count(severity) { return this.items.filter(i => i.severity === severity).length; }

  totals() {
    return {
      checks: this.passCount + this.items.length,
      pass: this.passCount,
      error: this.count('error'),
      warning: this.count('warning'),
      info: this.count('info'),
      skipped: this.count('skipped')
    };
  }

  verdict() {
    const t = this.totals();
    if (t.error > 0) {
      return { status: 'fail', exit_code: 1, summary: `${t.error} error${t.error === 1 ? '' : 's'}` };
    }
    if (t.skipped > 0) {
      // Deliberately not "pass". Nothing failed, but not everything was checked.
      return {
        status: 'incomplete', exit_code: 0,
        summary: `no errors, but ${t.skipped} check${t.skipped === 1 ? '' : 's'} could not run — this is not a clean bill of health`
      };
    }
    if (t.warning > 0) {
      return { status: 'pass_with_warnings', exit_code: 0, summary: `${t.warning} warning${t.warning === 1 ? '' : 's'}` };
    }
    return { status: 'pass', exit_code: 0, summary: 'everything checked, everything passed' };
  }

  /** Errors first, then warnings, then skips, then info — reading order for a triage. */
  sorted() {
    const rank = { error: 0, warning: 1, skipped: 2, info: 3 };
    return [...this.items].sort((a, b) =>
      rank[a.severity] - rank[b.severity] ||
      String(a.check).localeCompare(String(b.check)) ||
      String(a.route ?? a.file ?? '').localeCompare(String(b.route ?? b.file ?? ''))
    );
  }
}

export function buildReport({ findings, git, mode, routes, environment }) {
  return {
    schema_version: '1.0',
    generated_at: new Date().toISOString(),
    harness_version: HARNESS_VERSION,
    git,
    mode,
    environment,
    routes,
    totals: findings.totals(),
    findings: findings.sorted(),
    verdict: findings.verdict()
  };
}

export function writeJson(path, report) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(report, null, 2) + '\n');
}

export function writeText(path, text) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, text.endsWith('\n') ? text : text + '\n');
}

const LABEL = { error: 'ERROR', warning: 'WARN', skipped: 'SKIP', info: 'INFO' };

export function summaryMarkdown(report) {
  const t = report.totals;
  const lines = [
    '# Website QA report',
    '',
    `**${report.verdict.status.toUpperCase()}** — ${report.verdict.summary}`,
    '',
    `| | |`,
    `| --- | --- |`,
    `| Generated | ${report.generated_at} |`,
    `| Commit | \`${report.git.sha ?? 'unknown'}\`${report.git.dirty ? ' (working tree dirty)' : ''} |`,
    `| Branch | ${report.git.branch ?? 'unknown'} |`,
    `| Harness | ${report.harness_version} |`,
    `| Suites run | ${Object.entries(report.mode).filter(([, v]) => v).map(([k]) => k).join(', ') || 'none'} |`,
    `| Routes | ${report.routes.length} |`,
    `| Checks | ${t.checks} |`,
    `| Passed | ${t.pass} |`,
    `| Errors | **${t.error}** |`,
    `| Warnings | ${t.warning} |`,
    `| Skipped | ${t.skipped} |`,
    ''
  ];

  if (t.skipped > 0) {
    lines.push(
      '> **This run is incomplete.** ' +
      `${t.skipped} check${t.skipped === 1 ? '' : 's'} could not be performed. ` +
      'They are listed below with the reason, and none of them is reported as passing.',
      ''
    );
  }

  for (const severity of ['error', 'warning', 'skipped', 'info']) {
    const items = report.findings.filter(f => f.severity === severity);
    if (!items.length) continue;
    lines.push(`## ${LABEL[severity]} (${items.length})`, '');
    for (const item of items) {
      const where = [item.route, item.file, item.viewport].filter(Boolean).join(' · ');
      lines.push(`- **\`${item.check}\`**${where ? ` — ${where}` : ''}`);
      lines.push(`  ${item.message}`);
      if (item.reason) lines.push(`  *Reason:* ${item.reason}`);
      if (item.evidence !== undefined && item.evidence !== null) {
        const text = typeof item.evidence === 'string' ? item.evidence : JSON.stringify(item.evidence);
        lines.push(`  *Evidence:* \`${text.length > 400 ? text.slice(0, 400) + '…' : text}\``);
      }
    }
    lines.push('');
  }

  if (t.error === 0 && t.warning === 0 && t.skipped === 0) {
    lines.push('Nothing to report. Every check that exists ran and passed.', '');
  }
  return lines.join('\n');
}

export function printConsole(report) {
  const t = report.totals;
  const order = ['error', 'warning', 'skipped'];
  for (const severity of order) {
    for (const item of report.findings.filter(f => f.severity === severity)) {
      const where = [item.route, item.file, item.viewport].filter(Boolean).join(' · ');
      console.log(`${LABEL[severity].padEnd(6)}${item.check}${where ? `  [${where}]` : ''}`);
      console.log(`      ${item.message}`);
      if (item.reason) console.log(`      reason: ${item.reason}`);
    }
  }
  console.log('');
  console.log(`${t.checks} checks · ${t.pass} passed · ${t.error} errors · ${t.warning} warnings · ${t.skipped} skipped`);
  console.log(`verdict: ${report.verdict.status} — ${report.verdict.summary}`);
}
