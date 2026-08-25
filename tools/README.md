# tools

Repository maintenance scripts. Not part of the site, not served, excluded in
`robots.txt`.

| Script | What it does | Needs |
| --- | --- | --- |
| [`audit.py`](./audit.py) | Checks every content page against the load-bearing rules, plus links, alt text, canonicals, and sitemap agreement | Python 3 only |
| [`browser-audit.js`](./browser-audit.js) | The checks that need a real browser: console errors, horizontal overflow at 360px and 1280px, and load-bearing rules 4 and 5 | Node + Playwright |

```bash
python3 tools/audit.py                       # no install

npx --yes http-server -p 8099 -c-1 .         # in one terminal
npm install playwright && node tools/browser-audit.js   # in another
```

`audit.py` has no dependencies, in keeping with the repository having no build
step. `browser-audit.js` needs Playwright, which is why it is optional and why
the checks that *can* be done without a browser are not in it.

## Reading a finding before fixing it

The first run of `audit.py` produced twenty findings. All twenty were on
redirect stubs and a template — files that were already correct — and acting on
any of them would have made the site worse. Adding an `h1` and a meta
description to a redirect stub is not a fix.

Both scripts now exclude stubs and templates. The general point stands: confirm
a finding is real before changing anything, especially when a check is
mechanical.
