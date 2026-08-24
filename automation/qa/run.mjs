#!/usr/bin/env node
/**
 * Website QA harness for sklarzcreative.com.
 *
 * Reads. Measures. Reports. It cannot change the website, and that is a
 * property worth keeping — a QA tool that might rewrite your work is a tool
 * you stop running on a whim, and a tool you stop running catches nothing.
 *
 *   node automation/qa/run.mjs                 static + rendered + behaviour
 *   node automation/qa/run.mjs --static-only    no browser needed
 *   node automation/qa/run.mjs --live           also check the live domain
 *   node automation/qa/run.mjs --help
 *
 * Exit code is 1 if and only if there is at least one `error` finding.
 * Warnings, info and skips exit 0 — but a run with skips reports its verdict as
 * `incomplete`, never `pass`.
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Findings, buildReport, writeJson, writeText, summaryMarkdown, printConsole, HARNESS_VERSION } from './lib/report.mjs';
import { startServer } from './lib/server.mjs';
import { loadChromium, VIEWPORTS } from './lib/browser.mjs';
import { runStaticChecks, runSitemapRobotsChecks, isRedirectStub, APEX } from './checks/static-html.mjs';
import { runRenderedChecks } from './checks/rendered.mjs';
import { runBehaviourChecks } from './checks/behaviour.mjs';
import { runLiveChecks } from './checks/live.mjs';
import { parseSitemap, anchors, readPage, findHtmlFiles } from './lib/site.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..', '..');

function parseArgs(argv) {
  const flags = new Set(argv.filter(a => a.startsWith('--')));
  const get = name => {
    const hit = argv.find(a => a.startsWith(`--${name}=`));
    return hit ? hit.slice(name.length + 3) : null;
  };
  return {
    help: flags.has('--help') || flags.has('-h'),
    staticOnly: flags.has('--static-only'),
    live: flags.has('--live'),
    noBehaviour: flags.has('--no-behaviour'),
    noRendered: flags.has('--no-rendered'),
    out: get('out') ?? join(ROOT, 'automation', 'reports', 'qa-report.json'),
    summary: get('summary') ?? join(ROOT, 'automation', 'reports', 'qa-summary.md'),
    quiet: flags.has('--quiet')
  };
}

const HELP = `
Website QA harness for sklarzcreative.com

  node automation/qa/run.mjs [options]

Options
  --static-only      Source-level checks only. No browser, no server.
  --no-rendered      Skip the three-viewport rendered suite.
  --no-behaviour     Skip the behavioural suite (JS off, reduced motion, nav,
                     keyboard, scorecard arithmetic, fail-open).
  --live             Also check the live domain: real 404 status, www -> apex,
                     http -> https, share images, outbound destinations.
                     Skipped with a stated reason when the network cannot
                     reach it.
  --out=PATH         JSON report path.   Default automation/reports/qa-report.json
  --summary=PATH     Markdown summary.   Default automation/reports/qa-summary.md
  --quiet            Do not print findings to stdout.
  --help             This.

Environment
  QA_VERBOSE=1       Also print each passing check.

Exit code
  1  at least one error finding
  0  otherwise. A run that skipped checks reports verdict "incomplete",
     which is deliberately not "pass".
`;

function gitInfo() {
  const run = args => {
    try {
      return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    } catch {
      return null;
    }
  };
  const status = run(['status', '--porcelain']);
  return {
    sha: run(['rev-parse', 'HEAD']),
    branch: run(['rev-parse', '--abbrev-ref', 'HEAD']),
    dirty: status == null ? null : status.length > 0
  };
}

/** Outbound destinations the site actually links to, deduplicated by origin+path. */
function outboundUrls(root) {
  const seen = new Set();
  for (const file of findHtmlFiles(root)) {
    for (const a of anchors(readPage(root, file).html)) {
      if (!a.href || !/^https?:\/\//i.test(a.href)) continue;
      if (a.href.startsWith(APEX)) continue;
      try {
        const url = new URL(a.href);
        if (url.hostname.endsWith('sklarzcreative.com')) continue;
        seen.add(url.origin + url.pathname.replace(/\/$/, ''));
      } catch { /* not a URL we can check */ }
    }
  }
  return [...seen].sort();
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(HELP.trim());
    process.exit(0);
  }

  const findings = new Findings();
  const mode = {
    static: true,
    rendered: !options.staticOnly && !options.noRendered,
    behaviour: !options.staticOnly && !options.noBehaviour,
    live: options.live
  };

  /* ------------------------------------------------------------- static */
  let pages;
  try {
    ({ pages } = runStaticChecks(ROOT, findings));
    runSitemapRobotsChecks(ROOT, findings, pages);
  } catch (err) {
    // One broken check must not hide fifty working ones — but a broken SUITE
    // is reported as an error rather than swallowed.
    findings.error('harness.static', `the static suite threw: ${err.message}`, { group: 'harness', evidence: err.stack?.split('\n').slice(0, 4).join('\n') });
    pages = [];
  }

  const routes = pages.map(p => p.route);
  /* A redirect stub navigates away the instant it loads. Every behavioural
     assertion about it is meaningless (there is no content to keep visible, no
     nav to open), and any evaluate against it races the navigation. So it is
     tested for the one thing it is for — that it redirects — and excluded from
     the rest. */
  const stubRoutes = pages.filter(p => isRedirectStub(p.html)).map(p => p.route);
  const contentRoutes = routes.filter(r => !stubRoutes.includes(r));
  let environment = { node: process.version, chromium: null, viewports: [...VIEWPORTS], base_url: null };

  /* ------------------------------------------- rendered and behavioural */
  if (mode.rendered || mode.behaviour) {
    const chromium = await loadChromium();
    if (!chromium.ok) {
      // Honest degradation: the browser suites become skips with the reason,
      // never passes, and the verdict becomes "incomplete".
      for (const [check, description] of [
        ['rendered.suite', 'HTTP status, overflow, accessible names, images and console at three viewports'],
        ['behaviour.js-off', 'the page must render with scripting disabled'],
        ['behaviour.reduced-motion', 'reveals must resolve to their final state under prefers-reduced-motion'],
        ['behaviour.mobile-nav', 'the mobile menu must open, take focus, and return it on Escape'],
        ['behaviour.keyboard', 'the skip link must be first and must work'],
        ['behaviour.scorecard-integrity', "the page's arithmetic must agree with the specification at every band boundary"],
        ['behaviour.scorecard-fails-open', 'the diagnostic must open even when the capture endpoint is unreachable']
      ]) {
        findings.skip(check, description, chromium.reason, { group: 'harness' });
      }
      mode.rendered = false;
      mode.behaviour = false;
    } else {
      environment.chromium = chromium.version;
      let server;
      try {
        server = await startServer(ROOT);
        environment.base_url = server.origin;
      } catch (err) {
        // Without a server nothing rendered can be measured at all, and a
        // report that claimed otherwise would be worthless.
        console.error(`FATAL: could not start the local server: ${err.message}`);
        await chromium.browser.close();
        process.exit(2);
      }

      /* State the limitation once, in the report, rather than letting a reader
         assume the rendered measurements were taken with the real typeface. */
      findings.info(
        'harness.fonts-blocked',
        'Google Fonts requests are aborted so that page loads are deterministic. Every rendered measurement was therefore taken ' +
        'with the fallback type stack, not with Playfair Display / Montserrat / Inter. Overflow and layout findings are real signals; ' +
        'a clean overflow result is not proof that the real typography does not overflow. Confirm typography on the live domain.',
        { group: 'harness' }
      );

      const context = { browser: chromium.browser, origin: server.origin, routes, contentRoutes, stubRoutes, findings };
      try {
        if (mode.rendered) await runRenderedChecks(context);
      } catch (err) {
        findings.error('harness.rendered', `the rendered suite threw: ${err.message}`, { group: 'harness' });
      }
      try {
        if (mode.behaviour) await runBehaviourChecks(context);
      } catch (err) {
        findings.error('harness.behaviour', `the behavioural suite threw: ${err.message}`, { group: 'harness' });
      }

      await chromium.browser.close();
      await server.close();
    }
  } else {
    findings.skip('rendered.suite', 'the rendered and behavioural suites', 'not requested (--static-only)', { group: 'harness' });
  }

  /* --------------------------------------------------------------- live */
  if (mode.live) {
    const sitemapPath = join(ROOT, 'sitemap.xml');
    const sitemapUrls = existsSync(sitemapPath)
      ? parseSitemap(readFileSync(sitemapPath, 'utf8')).map(e => e.loc).filter(Boolean)
      : [];
    try {
      await runLiveChecks({ findings, sitemapUrls, outboundUrls: outboundUrls(ROOT) });
    } catch (err) {
      findings.error('harness.live', `the live suite threw: ${err.message}`, { group: 'harness' });
    }
  } else {
    findings.info('live.suite', 'live-domain checks were not requested; pass --live to run them', { group: 'harness' });
  }

  /* ------------------------------------------------------------- report */
  const report = buildReport({ findings, git: gitInfo(), mode, routes, environment });
  writeJson(options.out, report);
  writeText(options.summary, summaryMarkdown(report));

  if (!options.quiet) printConsole(report);
  console.log(`\nreport:  ${options.out}`);
  console.log(`summary: ${options.summary}`);
  console.log(`harness: ${HARNESS_VERSION}`);

  process.exit(report.verdict.exit_code);
}

main().catch(err => {
  console.error('FATAL: the harness itself failed.');
  console.error(err);
  // Exit 2, distinct from 1, so CI can tell "the site is broken" from
  // "the tool is broken". Conflating them wastes the first hour of debugging.
  process.exit(2);
});
