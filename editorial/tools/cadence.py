#!/usr/bin/env python3
"""
cadence.py — measure the rhythm of a draft.

Reports paragraph length, sentence length, first-person density, and stacked
one-line fragments for one or more Markdown drafts.

Why this exists
---------------
The single most useful finding in the first round of Editorial Director reviews
was not a judgement call. It was a number: Curves Ahead Editions 01 and 03 both
averaged ~12.8 words per paragraph, across completely different subjects, while
Edition 02 — written through a different process — averaged 19.8 and contained
zero instances of "I".

Uniform paragraph length is the most reliable structural signal of generated
prose, and unlike most editorial findings it can be counted rather than argued
about. Counting it makes the conversation concrete: not "this feels choppy" but
"93 paragraphs averaging 12.8 words, and here are the fifteen fragment stacks."

What the numbers mean
---------------------
These are diagnostics, not a score. There is no target to hit, and writing to
one would produce exactly the mechanical prose the standard exists to remove.
Read them as prompts to look:

  words/paragraph   Under ~15 sustained across a whole piece usually means the
                    one-line-paragraph habit. Healthy editorial prose varies —
                    what matters is the spread, not the mean.
  paragraph spread  A low standard deviation is the real tell. One rhythm is
                    no rhythm.
  words/sentence    Under ~10 sustained suggests the same habit at sentence
                    level.
  first person      Not a target. A gap between drafts in the same publication
                    is worth asking about — that is how Edition 02's absent
                    voice was found.
  fragment stacks   Runs of 3+ consecutive very short paragraphs. Effective
                    once or twice; a habit by the fifth.

Usage
-----
    python3 editorial/tools/cadence.py editorial/drafts/*.md
    python3 editorial/tools/cadence.py draft.md edited.md    # before/after

YAML front matter, blockquotes (editorial notes), headings and code fences are
excluded so the numbers describe the prose, not the scaffolding.
"""

import re
import statistics
import sys


SHORT_PARAGRAPH_WORDS = 8   # what counts as a "fragment" for stack detection
STACK_MIN = 3               # consecutive fragments before it counts as a stack


def strip_scaffolding(text):
    """Remove front matter, editorial notes, headings, fences and source notes."""
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) == 3:
            text = parts[2]
    text = re.sub(r'^```.*?^```', '', text, flags=re.M | re.S)
    text = re.sub(r'^>.*$', '', text, flags=re.M)          # blockquoted notes
    text = re.sub(r'^\[\^\d+\]:.*$', '', text, flags=re.M)  # footnote bodies
    text = re.sub(r'\*\*(EDITORIAL NOTE|SOURCE / FACT-CHECK).*', '',
                  text, flags=re.S)
    return text


def words(s):
    return re.findall(r"[A-Za-z0-9'’\-]+", s)


def analyse(path):
    raw = open(path, encoding='utf-8').read()
    text = strip_scaffolding(raw)

    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
    paras = [b for b in blocks
             if not b.startswith('#') and not b.startswith('---')]

    para_lengths = [len(words(p)) for p in paras if words(p)]
    if not para_lengths:
        return None

    body = ' '.join(text.split())
    sentences = [s for s in re.split(r'(?<=[.!?])\s+', body) if len(words(s)) > 1]
    sent_lengths = [len(words(s)) for s in sentences]

    # first person: standalone "I", "I'm", "I've" etc. Not "if", not "In".
    first_person = len(re.findall(r"\bI\b(?:['’]\w+)?", text))

    # fragment stacks: runs of >= STACK_MIN consecutive short paragraphs
    stacks, run = [], 0
    for n in para_lengths:
        if n <= SHORT_PARAGRAPH_WORDS:
            run += 1
        else:
            if run >= STACK_MIN:
                stacks.append(run)
            run = 0
    if run >= STACK_MIN:
        stacks.append(run)

    return {
        'words': sum(para_lengths),
        'paras': len(para_lengths),
        'w_para': statistics.mean(para_lengths),
        'sd_para': statistics.pstdev(para_lengths) if len(para_lengths) > 1 else 0.0,
        'w_sent': statistics.mean(sent_lengths) if sent_lengths else 0.0,
        'first_person': first_person,
        'stacks': len(stacks),
        'stacked_paras': sum(stacks),
    }


def main(paths):
    if not paths:
        print(__doc__.strip())
        return 1

    rows = []
    for p in paths:
        try:
            r = analyse(p)
        except OSError as e:
            print(f"  ! {p}: {e}", file=sys.stderr)
            continue
        if r is None:
            print(f"  ! {p}: no prose found", file=sys.stderr)
            continue
        r['name'] = p.split('/')[-1].replace('.md', '')
        rows.append(r)

    if not rows:
        return 1

    width = max(len(r['name']) for r in rows)
    header = (f"{'draft'.ljust(width)}  {'words':>6} {'paras':>6} {'w/para':>7} "
              f"{'sd':>6} {'w/sent':>7} {'I':>4} {'stacks':>7}")
    print(header)
    print('-' * len(header))
    for r in rows:
        print(f"{r['name'].ljust(width)}  {r['words']:6d} {r['paras']:6d} "
              f"{r['w_para']:7.1f} {r['sd_para']:6.1f} {r['w_sent']:7.1f} "
              f"{r['first_person']:4d} {r['stacks']:7d}")

    print()
    for r in rows:
        if r['w_para'] < 15:
            print(f"  · {r['name']}: {r['w_para']:.1f} words/paragraph — check for "
                  f"the one-line-paragraph habit")
        if r['sd_para'] and r['sd_para'] < 8:
            print(f"  · {r['name']}: paragraph spread {r['sd_para']:.1f} — one "
                  f"rhythm throughout, little variation")
        if r['stacks'] >= 5:
            print(f"  · {r['name']}: {r['stacks']} fragment stacks covering "
                  f"{r['stacked_paras']} paragraphs — effective twice, a habit by five")
    print("\n  Diagnostics, not a score. Nothing here is a target to write toward.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
