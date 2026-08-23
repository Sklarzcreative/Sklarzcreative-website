# Original Sklarz Creative site — full backup

This folder is a complete, byte-for-byte copy of the Sklarz Creative website
**as it existed before the 2026 cinematic redesign**, taken from commit
`3e44ab7` ("Use confirmed Cassandra Sklarz LinkedIn URL").

Every original page is fully self-contained here — each `.html` file still has
its own inline `<style>` block, exactly as it shipped. Nothing in this folder
depends on the new design system, so it will keep working forever even if the
new CSS and JS files are deleted.

## What is in here

| File | What it was |
| --- | --- |
| `index.html` | Original homepage (navy gradient hero, capability grid, process strip) |
| `media-kit.html` | Original media kit |
| `404.html` | Original branded 404 page |
| `Index.html` | Legacy capital-I redirect to `/` |
| `insights/**` | All nine original Insights pages, including The Trust Files and File 001 |
| `assets/graphics/*.svg` | Original editorial SVG graphics |
| `assets/images/*.webp` | Original optimized founder headshot |
| `robots.txt`, `sitemap.xml`, `CNAME` | Original site configuration |
| `QA_POST_LAUNCH_2026-08-09.md` | The previous QA audit |
| `README.md` | Original repository README |

## What is deliberately *not* duplicated here

The four large PNG masters are **not** copied into this folder, because they
were never modified by the redesign and still sit untouched in the repository
root at their original paths:

- `/sklarz-creative-logo.png`
- `/cassandra-sklarz-headshot.jpg.png`
- `/social-share.png`
- `/Favicon.png`

Keeping one copy instead of two avoids adding ~6.5 MB of duplicate binaries to
the repository. They are safe — the redesign only *adds* optimized derivatives
alongside them.

## How to roll back

### Option 1 — restore just the pages (fastest, no git knowledge needed)

Copy the originals back over the live files:

```bash
cp _original-design/index.html      ./index.html
cp _original-design/media-kit.html  ./media-kit.html
cp _original-design/404.html        ./404.html
cp -r _original-design/insights/.   ./insights/
cp _original-design/robots.txt      ./robots.txt
cp _original-design/sitemap.xml     ./sitemap.xml
```

The original pages carry their own inline CSS, so the site returns to its exact
previous appearance immediately. The new `assets/css/` and `assets/js/` files
become unused and can be deleted or simply left in place.

### Option 2 — restore the whole repository from the backup branch

> **Updated after launch.** The redesign has shipped, so `main` now holds the
> *redesign* — it is what is live. The original is preserved on a permanent
> branch instead: **`pre-luxury-redesign-2026-08-22`**, pinned to `e5aa3a6`, the
> exact commit that was serving before the redesign. Do not delete that branch.

To put the original site back live:

```bash
git fetch origin
git checkout main
git reset --hard pre-luxury-redesign-2026-08-22
git push --force-with-lease origin main
```

GitHub Pages rebuilds automatically, in about 30 seconds. To inspect the
original without changing what is live:

```bash
git checkout pre-luxury-redesign-2026-08-22
```

### Option 3 — recover a single original file from git history

```bash
git show 3e44ab7:index.html > index.html
```

## Publicly reachable

Because this repository has `.nojekyll`, GitHub Pages serves every folder,
including this one. `robots.txt` has a `Disallow: /_original-design/` rule and
this folder is excluded from `sitemap.xml`, so search engines will not index the
old pages as duplicate content. If you would rather it not be reachable at all,
delete the folder — `main` and the git history still hold everything.
