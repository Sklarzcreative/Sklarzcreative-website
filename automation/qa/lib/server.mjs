/**
 * A static file server for the working tree, close enough to GitHub Pages to
 * test against.
 *
 * Dependency-free by design: `http-server` would work and would also mean the
 * harness could not run on a clean checkout without an install. It matches the
 * two Pages behaviours that matter for QA:
 *   - a directory resolves to its index.html
 *   - a missing path serves 404.html WITH A REAL 404 STATUS
 *
 * That second one is the reason this exists rather than any convenient
 * alternative. A dev server that answers 200 for a missing page makes the 404
 * check pass while production is broken, which is precisely the class of lie
 * this harness is built to avoid.
 */
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, normalize, resolve } from 'node:path';

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8'
};

export async function startServer(root, { port = 0 } = {}) {
  const rootAbs = resolve(root);

  const server = createServer(async (req, res) => {
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
    } catch {
      res.writeHead(400).end('bad request');
      return;
    }

    // Contain every request inside the root. A QA server is still a server.
    const candidate = resolve(join(rootAbs, normalize(pathname)));
    if (candidate !== rootAbs && !candidate.startsWith(rootAbs + '/')) {
      res.writeHead(403).end('forbidden');
      return;
    }

    let target = candidate;
    try {
      const info = await stat(target);
      if (info.isDirectory()) target = join(target, 'index.html');
    } catch { /* fall through to the 404 path below */ }

    try {
      const body = await readFile(target);
      res.writeHead(200, {
        'Content-Type': TYPES[extname(target).toLowerCase()] ?? 'application/octet-stream',
        'Content-Length': body.length,
        'Cache-Control': 'no-store'
      });
      res.end(body);
    } catch {
      // Pages serves the branded 404 page with a genuine 404 status.
      try {
        const notFound = await readFile(join(rootAbs, '404.html'));
        res.writeHead(404, { 'Content-Type': TYPES['.html'], 'Content-Length': notFound.length });
        res.end(notFound);
      } catch {
        res.writeHead(404, { 'Content-Type': 'text/plain' }).end('404');
      }
    }
  });

  await new Promise((ok, fail) => {
    server.once('error', fail);
    server.listen(port, '127.0.0.1', ok);
  });

  const { port: actual } = server.address();
  return {
    origin: `http://127.0.0.1:${actual}`,
    close: () => new Promise(ok => server.close(ok))
  };
}
