/**
 * Live-domain checks. These are properties of GitHub Pages and DNS, not of the
 * code, and they cannot be answered from the working tree:
 *
 *   - does a missing path return a real 404 rather than a 200?
 *   - does www redirect to the apex?
 *   - does http upgrade to https?
 *   - are the share images actually fetchable?
 *   - do the outbound destinations answer?
 *
 * REACHABILITY IS PROBED FIRST, and if the network cannot reach the domain
 * every check in this suite is reported as `skipped` with the observed reason.
 * Reporting a live check as passing when the request never left the machine is
 * the single worst thing a QA harness can do — it converts an unknown into a
 * false reassurance, which is worse than having no check at all.
 */

const APEX = 'https://sklarzcreative.com';
const TIMEOUT_MS = 12000;

async function request(url, { method = 'GET', redirect = 'manual' } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(url, { method, redirect, signal: controller.signal });
    return {
      ok: true,
      status: response.status,
      location: response.headers.get('location'),
      headers: response.headers,
      contentType: response.headers.get('content-type'),
      body: method === 'GET' ? (await response.text()).slice(0, 20000) : ''
    };
  } catch (err) {
    return { ok: false, error: err.name === 'AbortError' ? `timed out after ${TIMEOUT_MS}ms` : err.message };
  }
}

/**
 * Establish whether this machine can actually reach the live site, and say how
 * it failed if it cannot. An egress proxy that answers 403 to CONNECT looks
 * exactly like a site returning 403, so the probe checks for the site's own
 * content rather than trusting the status code alone.
 */
async function probe() {
  const result = await request(APEX + '/', { redirect: 'follow' });
  if (!result.ok) {
    return { reachable: false, reason: `the live domain could not be reached from this environment: ${result.error}` };
  }
  if (result.status >= 200 && result.status < 300 && /Sklarz Creative/i.test(result.body)) {
    return { reachable: true };
  }
  return {
    reachable: false,
    reason:
      `a request to ${APEX}/ returned HTTP ${result.status} and did not contain the site's own markup, ` +
      'so this environment cannot see the live domain (an egress proxy or network policy is answering instead). ' +
      'No live check can be performed, and none is reported as passing.'
  };
}

export async function runLiveChecks({ findings, sitemapUrls, outboundUrls }) {
  const at = { group: 'live' };
  const { reachable, reason } = await probe();

  if (!reachable) {
    const skipped = [
      ['live.sitemap-urls', 'HTTP status of every sitemap URL'],
      ['live.404-status', 'a nonexistent path must return a real 404, not a 200'],
      ['live.www-redirect', 'www.sklarzcreative.com must redirect to the apex'],
      ['live.https-upgrade', 'http:// must upgrade to https://'],
      ['live.headers', 'compression and cache headers'],
      ['live.og-image-fetch', 'the share images must be fetchable with an image content type'],
      ['live.outbound', 'Calendly and the social destinations must answer']
    ];
    for (const [check, description] of skipped) {
      findings.skip(check, description, reason, at);
    }
    return;
  }

  /* ------------------------------------------------- every sitemap URL 200 */
  for (const url of sitemapUrls) {
    const result = await request(url, { method: 'GET', redirect: 'manual' });
    if (!result.ok) {
      findings.skip('live.sitemap-urls', `could not check ${url}`, result.error, at);
    } else if (result.status !== 200) {
      findings.error('live.sitemap-urls', `${url} returned HTTP ${result.status}${result.location ? ` -> ${result.location}` : ''}`, at);
    } else findings.pass('live.sitemap-urls', url);
  }

  /* ------------------------------------------------------- a genuine 404 */
  const missing = await request(`${APEX}/this-path-does-not-exist-${Date.now().toString(36)}`, { redirect: 'manual' });
  if (!missing.ok) {
    findings.skip('live.404-status', 'a nonexistent path must return a real 404', missing.error, at);
  } else if (missing.status !== 404) {
    findings.error(
      'live.404-status',
      `a nonexistent path returned HTTP ${missing.status}, not 404. A soft 404 lets search engines index an error page as content.`,
      at
    );
  } else findings.pass('live.404-status');

  /* -------------------------------------------------------- www -> apex */
  const www = await request('https://www.sklarzcreative.com/', { redirect: 'manual' });
  if (!www.ok) {
    findings.skip('live.www-redirect', 'www must redirect to the apex', www.error, at);
  } else if (www.status >= 300 && www.status < 400 && (www.location ?? '').startsWith(APEX)) {
    findings.pass('live.www-redirect');
  } else {
    findings.error(
      'live.www-redirect',
      `www.sklarzcreative.com returned HTTP ${www.status}${www.location ? ` -> ${www.location}` : ''}; every canonical is on the apex, so www must redirect there or the site serves two of everything`,
      at
    );
  }

  /* ------------------------------------------------------ http -> https */
  const insecure = await request('http://sklarzcreative.com/', { redirect: 'manual' });
  if (!insecure.ok) {
    findings.skip('live.https-upgrade', 'http must upgrade to https', insecure.error, at);
  } else if (insecure.status >= 300 && insecure.status < 400 && (insecure.location ?? '').startsWith('https://')) {
    findings.pass('live.https-upgrade');
  } else {
    findings.error('live.https-upgrade', `http:// returned HTTP ${insecure.status}${insecure.location ? ` -> ${insecure.location}` : ''} rather than redirecting to https`, at);
  }

  /* ------------------------------------------------------------- headers */
  const home = await request(APEX + '/', { redirect: 'follow' });
  if (home.ok) {
    const encoding = home.headers.get('content-encoding');
    const cache = home.headers.get('cache-control');
    if (!encoding) findings.warn('live.headers', 'no content-encoding on the homepage response — HTML is being served uncompressed', at);
    else findings.pass('live.headers', `content-encoding: ${encoding}`);
    if (!cache) findings.warn('live.headers', 'no cache-control header on the homepage response', at);
  }

  /* -------------------------------------------------------- share images */
  for (const image of [`${APEX}/social-share.png`, `${APEX}/social-share-scorecard.png`]) {
    const result = await request(image, { method: 'HEAD', redirect: 'follow' });
    if (!result.ok) {
      findings.skip('live.og-image-fetch', `could not fetch ${image}`, result.error, at);
    } else if (result.status !== 200) {
      findings.error('live.og-image-fetch', `${image} returned HTTP ${result.status}; the share card will not render`, at);
    } else if (!(result.contentType ?? '').startsWith('image/')) {
      findings.error('live.og-image-fetch', `${image} is served as ${result.contentType}, not an image type`, at);
    } else findings.pass('live.og-image-fetch', image);
  }

  /* ------------------------------------------------- outbound destinations */
  for (const url of outboundUrls) {
    const result = await request(url, { method: 'GET', redirect: 'follow' });
    if (!result.ok) {
      findings.skip('live.outbound', `could not reach ${url}`, result.error, at);
    } else if (result.status >= 400) {
      /* Several social platforms answer 401/403/429 to a headless request while
         working perfectly in a browser, so this is a warning that names the
         status rather than a failure that cries wolf. */
      findings.warn(
        'live.outbound',
        `${url} returned HTTP ${result.status}. Platforms often refuse headless requests, so confirm by hand before treating this as broken.`,
        at
      );
    } else findings.pass('live.outbound', url);
  }
}
