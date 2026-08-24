/**
 * Publish-queue reliability analysis — the logic behind the Publishing
 * Reliability Agent, as pure functions over rows.
 *
 * WHY PURE FUNCTIONS
 * The classification rules are the part that must be right, and they are the
 * part that cannot be tested if they only exist inside a Make scenario or a
 * spreadsheet formula. Here they take an array of plain objects and return
 * findings, so `automation/tests/queue-audit.test.mjs` can assert the exact
 * behaviour that matters most: that HOLD is never treated as a failure, and
 * that a bulk release is never recommended.
 *
 * This module never writes anything anywhere. It has no I/O at all.
 *
 * EXPECTED ROW SHAPE — see ../schemas/publish-queue-row.schema.json.
 * Unknown fields are ignored; missing fields are treated as unknown, never as
 * satisfied.
 */

/** Statuses the system knows about. Anything else is drift, and drift is reported. */
export const STATUSES = Object.freeze({
  DRAFT: 'not ready, not waiting on anything',
  STAGED: 'produced by an agent, inert until a human approves it',
  APPROVED: 'a human approved it; the publisher may act on it at its scheduled time',
  HOLD: 'a human decided this waits. NOT A FAILURE.',
  PROCESSING: 'the publisher has picked it up — transient',
  SENDING: 'the publisher is calling the platform — transient',
  RETRY: 'a previous attempt failed and a retry is pending — transient',
  PUBLISHED: 'the platform accepted it',
  FAILED: 'the publisher tried and gave up',
  CANCELLED: 'a human withdrew it'
});

export const TRANSIENT_STATUSES = Object.freeze(['PROCESSING', 'SENDING', 'RETRY']);

/** Platforms whose posts cannot exist without media. A row here with no asset cannot publish. */
export const MEDIA_REQUIRED = Object.freeze(['instagram', 'pinterest', 'tiktok', 'youtube']);

export const DEFAULTS = Object.freeze({
  /** Generous on purpose: a normally-running scheduler must never trip this. */
  overdueGraceMinutes: 90,
  /** A transient status older than this means a run died mid-flight. */
  staleTransientMinutes: 60,
  /** Two identical posts closer together than this are a duplicate risk, not a repost. */
  duplicateWindowHours: 72,
  /** Failures on one platform at or above this count are a pattern, not an incident. */
  failurePatternThreshold: 3,
  /** How far back route health looks. */
  windowDays: 14
});

const MINUTE = 60 * 1000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

function parseTime(value) {
  if (value == null || value === '') return null;
  const ms = value instanceof Date ? value.getTime() : Date.parse(value);
  return Number.isNaN(ms) ? null : ms;
}

function present(value) {
  return value != null && String(value).trim() !== '';
}

function normStatus(row) {
  return String(row?.status ?? '').trim().toUpperCase();
}

function finding(severity, check, row, message, extra = {}) {
  return {
    severity,          // 'critical' | 'warning' | 'info'
    check,
    row_id: row?.row_id ?? null,
    platform: row?.platform ?? null,
    content_id: row?.content_id ?? null,
    message,
    ...extra
  };
}

/* --------------------------------------------------------------- checks --- */

/**
 * The check that exists because of the incident: APPROVED, its time has passed,
 * and there is neither a published URL nor an error. The publisher did not run,
 * or ran and said nothing. Silence is the dangerous failure mode — a loud
 * failure gets noticed the same day.
 */
export function overdueApproved(rows, now, opts = DEFAULTS) {
  const cutoff = now - opts.overdueGraceMinutes * MINUTE;
  return rows
    .filter(row => {
      if (normStatus(row) !== 'APPROVED') return false;
      const scheduled = parseTime(row.scheduled_at);
      if (scheduled == null || scheduled > cutoff) return false;
      return !present(row.published_url) && !present(row.error);
    })
    .map(row => finding(
      'critical', 'overdue_approved', row,
      `approved for ${row.scheduled_at} and still unpublished, with no error recorded — ` +
      'the publisher either did not run or ran silently. Investigate the route, not the row.',
      { overdue_by_hours: Number(((now - parseTime(row.scheduled_at)) / HOUR).toFixed(1)) }
    ));
}

/** HOLD is a decision, not a fault. Counted and listed, never actioned. */
export function holds(rows) {
  return rows
    .filter(row => normStatus(row) === 'HOLD')
    .map(row => finding(
      'info', 'hold', row,
      'on HOLD by a human decision. Not a failure and not an action item.'
    ));
}

export function failedRows(rows) {
  return rows
    .filter(row => normStatus(row) === 'FAILED' || (normStatus(row) === 'APPROVED' && present(row.error)))
    .map(row => finding(
      'critical', 'publish_failed', row,
      `the publisher reported: ${String(row.error ?? 'no error text recorded')}`,
      { error: row.error ?? null }
    ));
}

/**
 * Detected before the scheduled time, which is the only point at which the
 * information is still actionable.
 */
export function missingAssets(rows, now, opts = DEFAULTS) {
  return rows
    .filter(row => {
      const status = normStatus(row);
      if (!['APPROVED', 'STAGED', 'RETRY'].includes(status)) return false;
      const platform = String(row.platform ?? '').trim().toLowerCase();
      const needsMedia = MEDIA_REQUIRED.includes(platform) || row.requires_media === true;
      return needsMedia && !present(row.asset_ref);
    })
    .map(row => {
      const scheduled = parseTime(row.scheduled_at);
      const future = scheduled != null && scheduled > now;
      return finding(
        future ? 'warning' : 'critical', 'missing_asset', row,
        `${row.platform} cannot publish without media and asset_ref is empty` +
        (future ? ' — still fixable before its scheduled time.' : ' — its time has passed.')
      );
    });
}

export function missingTargetUrl(rows) {
  return rows
    .filter(row => ['APPROVED', 'STAGED', 'RETRY'].includes(normStatus(row)) && !present(row.target_url))
    .map(row => finding(
      'warning', 'missing_target_url', row,
      'no target_url — the post would go out with nothing to click, so it can generate attention but not traffic.'
    ));
}

/**
 * PUBLISHED with no published_url. Either the route cannot return one or the
 * status was stamped optimistically. Either way it is unverifiable, so it is
 * never counted as a success.
 */
export function publishedWithoutUrl(rows) {
  return rows
    .filter(row => normStatus(row) === 'PUBLISHED' && !present(row.published_url))
    .map(row => finding(
      'critical', 'published_without_url', row,
      'marked PUBLISHED with no published_url. Unverifiable — either the route cannot return a URL ' +
      'or the status was stamped before the platform confirmed. Not counted as a success.'
    ));
}

/** A publisher that died mid-run leaves exactly this trace. */
export function staleTransient(rows, now, opts = DEFAULTS) {
  const cutoff = now - opts.staleTransientMinutes * MINUTE;
  return rows
    .filter(row => {
      if (!TRANSIENT_STATUSES.includes(normStatus(row))) return false;
      const touched = parseTime(row.updated_at) ?? parseTime(row.scheduled_at);
      return touched != null && touched < cutoff;
    })
    .map(row => finding(
      'critical', 'stale_transient', row,
      `stuck in ${normStatus(row)} since ${row.updated_at ?? row.scheduled_at} — ` +
      'a transient status this old means a run died mid-flight.'
    ));
}

export function unknownStatus(rows) {
  return rows
    .filter(row => {
      const status = normStatus(row);
      return status !== '' && !Object.prototype.hasOwnProperty.call(STATUSES, status);
    })
    .map(row => finding(
      'warning', 'unknown_status', row,
      `status "${row.status}" is not in the known set. Either a typo or a second system writing this column — ` +
      'both are worth knowing about. Not coerced into a known bucket.',
      { raw_status: row.status }
    ));
}

export function missingStatus(rows) {
  return rows
    .filter(row => normStatus(row) === '')
    .map(row => finding('warning', 'missing_status', row, 'no status recorded, so nothing can be concluded about this row.'));
}

/**
 * Reported as *risk*, never as a fault: a scheduled repost is legitimate, and
 * only a human knows which of the two this is.
 */
export function duplicateRisk(rows, opts = DEFAULTS) {
  const windowMs = opts.duplicateWindowHours * HOUR;
  const groups = new Map();
  for (const row of rows) {
    if (['CANCELLED', 'DRAFT'].includes(normStatus(row))) continue;
    if (!present(row.content_id) || !present(row.platform)) continue;
    const key = `${String(row.content_id).trim()}::${String(row.platform).trim().toLowerCase()}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }

  const out = [];
  for (const [key, group] of groups) {
    if (group.length < 2) continue;
    const sorted = [...group].sort((a, b) => (parseTime(a.scheduled_at) ?? 0) - (parseTime(b.scheduled_at) ?? 0));
    for (let i = 1; i < sorted.length; i++) {
      const a = parseTime(sorted[i - 1].scheduled_at);
      const b = parseTime(sorted[i].scheduled_at);
      const gapUnknown = a == null || b == null;
      if (gapUnknown || b - a < windowMs) {
        out.push(finding(
          'warning', 'duplicate_risk', sorted[i],
          `same content on the same platform as row ${sorted[i - 1].row_id ?? '?'}, ` +
          (gapUnknown
            ? 'with no scheduled time on one of them so the gap cannot be checked.'
            : `${((b - a) / HOUR).toFixed(1)}h apart, inside the ${opts.duplicateWindowHours}h window.`) +
          ' A deliberate repost is legitimate — only a human knows which this is.',
          { duplicate_of: sorted[i - 1].row_id ?? null, key }
        ));
      }
    }
  }
  return out;
}

/**
 * A single failure is an incident. Three on one route is a broken credential,
 * and saying so saves the investigation.
 */
export function failurePatterns(rows, now, opts = DEFAULTS) {
  const since = now - opts.windowDays * DAY;
  const byPlatform = new Map();
  for (const row of rows) {
    const status = normStatus(row);
    const failed = status === 'FAILED' || (status === 'APPROVED' && present(row.error));
    if (!failed) continue;
    const when = parseTime(row.updated_at) ?? parseTime(row.scheduled_at);
    if (when != null && when < since) continue;
    const platform = String(row.platform ?? 'unknown').trim().toLowerCase();
    if (!byPlatform.has(platform)) byPlatform.set(platform, []);
    byPlatform.get(platform).push(row);
  }

  const out = [];
  for (const [platform, group] of byPlatform) {
    if (group.length < opts.failurePatternThreshold) continue;
    const errors = [...new Set(group.map(r => String(r.error ?? '').trim()).filter(Boolean))];
    out.push({
      severity: 'critical',
      check: 'failure_pattern',
      row_id: null,
      platform,
      content_id: null,
      message:
        `${group.length} failures on ${platform} in the last ${opts.windowDays} days` +
        (errors.length === 1
          ? ` — all reporting the same error, which points at the connection rather than the content.`
          : ` across ${errors.length} distinct errors.`),
      failure_count: group.length,
      distinct_errors: errors.slice(0, 5),
      affected_rows: group.map(r => r.row_id ?? null)
    });
  }
  return out;
}

/**
 * Per-platform rollup. A platform whose data could not be read is `unknown`,
 * never `healthy` — defaulting to healthy is how a dead route stays invisible.
 */
export function routeHealth(rows, now, opts = DEFAULTS, { onboardedRoutes = null } = {}) {
  const since = now - opts.windowDays * DAY;
  const platforms = new Set(rows.map(r => String(r.platform ?? '').trim().toLowerCase()).filter(Boolean));
  if (onboardedRoutes) onboardedRoutes.forEach(p => platforms.add(String(p).toLowerCase()));

  const out = {};
  for (const platform of [...platforms].sort()) {
    const mine = rows.filter(r => String(r.platform ?? '').trim().toLowerCase() === platform);
    const inWindow = mine.filter(r => {
      const when = parseTime(r.updated_at) ?? parseTime(r.scheduled_at);
      return when == null || when >= since;
    });

    const verified = inWindow.filter(r => normStatus(r) === 'PUBLISHED' && present(r.published_url));
    const failures = inWindow.filter(r => normStatus(r) === 'FAILED' || (normStatus(r) === 'APPROVED' && present(r.error)));
    const overdue = overdueApproved(inWindow, now, opts);
    const unverified = inWindow.filter(r => normStatus(r) === 'PUBLISHED' && !present(r.published_url));

    let status;
    if (onboardedRoutes && !onboardedRoutes.map(String).map(s => s.toLowerCase()).includes(platform)) {
      status = 'not_onboarded';
    } else if (inWindow.length === 0) {
      // No activity is not health. It is an absence of evidence.
      status = 'unknown';
    } else if (failures.length >= opts.failurePatternThreshold || overdue.length >= opts.failurePatternThreshold) {
      status = 'failing';
    } else if (failures.length > 0 || overdue.length > 0 || unverified.length > 0) {
      status = 'degraded';
    } else if (verified.length > 0) {
      status = 'healthy';
    } else {
      status = 'unknown';
    }

    const lastVerified = verified
      .map(r => parseTime(r.updated_at) ?? parseTime(r.scheduled_at))
      .filter(t => t != null)
      .sort((a, b) => b - a)[0];

    out[platform] = {
      status,
      verified_publishes: verified.length,
      failures: failures.length,
      overdue: overdue.length,
      published_without_url: unverified.length,
      last_verified_publish_at: lastVerified ? new Date(lastVerified).toISOString() : null,
      note: status === 'unknown'
        ? 'no verifiable activity in the window — an absence of evidence, not evidence of health'
        : null
    };
  }
  return out;
}

/* ------------------------------------------------------------- rollup ----- */

/**
 * The one recommendation shape this system permits when a backlog exists.
 * It is a constant rather than generated prose so it cannot drift into
 * "release the backlog" under any wording.
 */
export const CONTROLLED_RELEASE_RECOMMENDATION = Object.freeze([
  'Pick ONE overdue item. Prefer the least time-sensitive one.',
  'Publish that single item through the normal route — one row, by hand or a single-row run.',
  'Verify BOTH that a published_url came back AND that the post is visible on the platform.',
  'Only then release current content — the pieces that are still timely.',
  'Then decide item by item which stale items are still worth posting. Most are not: a backlog is usually evidence, not inventory.'
]);

/**
 * Analyse a queue snapshot.
 *
 * @param {object[]} rows
 * @param {object} [options]
 * @param {number|string|Date} [options.now] the analysis instant — passed in, never read from the clock, so a run is reproducible
 * @param {string[]|null} [options.onboardedRoutes] platforms cleared by runbooks/route-onboarding.md
 * @param {boolean} [options.queueReadable] false when the queue could not be read at all
 */
export function auditQueue(rows, options = {}) {
  const opts = { ...DEFAULTS, ...(options.thresholds || {}) };
  const now = parseTime(options.now) ?? Date.now();
  const queueReadable = options.queueReadable !== false;

  if (!queueReadable) {
    // A read failure must never look like a healthy empty queue.
    return {
      queue_readable: false,
      queue_total: null,
      counts_by_status: null,
      findings: [{
        severity: 'critical', check: 'queue_unreadable', row_id: null, platform: null, content_id: null,
        message: 'the publish queue could not be read, so nothing about publishing state is known. ' +
                 'Every figure in this report is null rather than zero.'
      }],
      route_health: null,
      recommended_next_actions: ['Restore access to the publish queue before drawing any conclusion about publishing health.'],
      hold_count: null,
      overdue_count: null
    };
  }

  const list = Array.isArray(rows) ? rows : [];
  const countsByStatus = {};
  for (const row of list) {
    const status = normStatus(row) || '(blank)';
    countsByStatus[status] = (countsByStatus[status] || 0) + 1;
  }

  const overdue = overdueApproved(list, now, opts);
  const holdList = holds(list);

  const findings = [
    ...overdue,
    ...failedRows(list),
    ...publishedWithoutUrl(list),
    ...staleTransient(list, now, opts),
    ...missingAssets(list, now, opts),
    ...missingTargetUrl(list),
    ...duplicateRisk(list, opts),
    ...failurePatterns(list, now, opts),
    ...unknownStatus(list),
    ...missingStatus(list),
    ...holdList
  ];

  const recommendations = [];
  if (overdue.length > 0) {
    recommendations.push(
      `${overdue.length} approved item${overdue.length === 1 ? '' : 's'} overdue with no error recorded. ` +
      'Do NOT release the backlog. Controlled release only:'
    );
    recommendations.push(...CONTROLLED_RELEASE_RECOMMENDATION.map((s, i) => `  ${i + 1}. ${s}`));
  }
  const patterns = findings.filter(f => f.check === 'failure_pattern');
  for (const p of patterns) {
    recommendations.push(`Check the ${p.platform} connection before republishing anything to it — ${p.message}`);
  }
  const unverifiable = findings.filter(f => f.check === 'published_without_url');
  if (unverifiable.length) {
    recommendations.push(
      `${unverifiable.length} row${unverifiable.length === 1 ? '' : 's'} marked PUBLISHED without a published_url. ` +
      'Confirm on the platform by hand, and fix whichever step stamps the status before the platform confirms.'
    );
  }
  const assets = findings.filter(f => f.check === 'missing_asset');
  if (assets.length) {
    const stillFixable = assets.filter(f => f.severity === 'warning').length;
    const alreadyDue = assets.length - stillFixable;
    const parts = [];
    if (stillFixable) parts.push(`${stillFixable} still ahead of its scheduled time — the cheapest fix on this list`);
    if (alreadyDue) parts.push(`${alreadyDue} already past its scheduled time, so it could not have published`);
    recommendations.push(`${assets.length} row(s) need media: ${parts.join('; ')}.`);
  }
  if (holdList.length && recommendations.length === 0) {
    recommendations.push(`${holdList.length} item(s) on HOLD by decision. Nothing to do — listed so the count is not mistaken for a backlog.`);
  }
  if (recommendations.length === 0) {
    recommendations.push('No publishing action required from this run.');
  }

  return {
    queue_readable: true,
    queue_total: list.length,
    counts_by_status: countsByStatus,
    approved_waiting: list.filter(r => normStatus(r) === 'APPROVED').length,
    hold_count: holdList.length,
    overdue_count: overdue.length,
    findings,
    route_health: routeHealth(list, now, opts, { onboardedRoutes: options.onboardedRoutes ?? null }),
    recommended_next_actions: recommendations,
    analysed_at: new Date(now).toISOString(),
    thresholds: opts
  };
}
