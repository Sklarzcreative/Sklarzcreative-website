/**
 * The Trust-First Content Scorecard, as specified.
 *
 * THIS IS A TEST ORACLE, NOT A SECOND IMPLEMENTATION.
 * The instrument the visitor uses is authored in
 * `insights/resources/trust-first-content-scorecard/index.html` — twenty
 * statements in HTML so the card is complete and printable with scripting off,
 * and a scoring function that only reads them. This module exists so the QA
 * harness can drive that page in a real browser and assert that the page's own
 * arithmetic agrees with what was intended, at every band boundary.
 *
 * If the two ever disagree: the page is the truth about what visitors see, and
 * this file is the truth about what was intended. Reconcile deliberately.
 * Editing this file to match a page that changed by accident converts a caught
 * bug into a silent one.
 *
 * THE INSTRUMENT
 *   5 categories x 4 statements x {0,1,2}  ->  0..40
 *   Bands: 32-40 / 24-31 / 16-23 / 0-15
 *   The weakest signal is the lowest category. A tie is reported as a tie.
 */

export const CATEGORIES = Object.freeze(['Clarity', 'Consistency', 'Credibility', 'Connection', 'Conversion']);
export const STATEMENTS_PER_CATEGORY = 4;
export const MAX_PER_STATEMENT = 2;
export const MAX_PER_CATEGORY = STATEMENTS_PER_CATEGORY * MAX_PER_STATEMENT; // 8
export const MAX_TOTAL = CATEGORIES.length * MAX_PER_CATEGORY;              // 40
export const TOTAL_STATEMENTS = CATEGORIES.length * STATEMENTS_PER_CATEGORY; // 20

/**
 * Band thresholds, highest first. These are the exact strings the page renders,
 * so the harness can compare them literally rather than fuzzily — a fuzzy
 * comparison would pass through a reworded band and never mention it.
 */
export const BANDS = Object.freeze([
  { min: 32, title: 'Strong trust system' },
  { min: 24, title: 'Solid foundation' },
  { min: 16, title: 'Inconsistent signals' },
  { min: 0, title: 'Rebuild the basics' }
]);

export function bandFor(total) {
  if (!Number.isInteger(total) || total < 0 || total > MAX_TOTAL) {
    throw new RangeError(`total must be an integer 0..${MAX_TOTAL}, got ${total}`);
  }
  return BANDS.find(b => total >= b.min).title;
}

/**
 * @param {number[][]} answers CATEGORIES.length arrays of STATEMENTS_PER_CATEGORY values in {0,1,2}
 */
export function score(answers) {
  if (!Array.isArray(answers) || answers.length !== CATEGORIES.length) {
    throw new TypeError(`answers must be ${CATEGORIES.length} arrays, one per category`);
  }

  const subtotals = answers.map((group, i) => {
    if (!Array.isArray(group) || group.length !== STATEMENTS_PER_CATEGORY) {
      throw new TypeError(`category ${CATEGORIES[i]} needs exactly ${STATEMENTS_PER_CATEGORY} answers`);
    }
    return group.reduce((sum, v) => {
      if (!Number.isInteger(v) || v < 0 || v > MAX_PER_STATEMENT) {
        throw new RangeError(`answer ${v} in ${CATEGORIES[i]} is outside 0..${MAX_PER_STATEMENT}`);
      }
      return sum + v;
    }, 0);
  });

  const total = subtotals.reduce((a, b) => a + b, 0);
  const lowest = Math.min(...subtotals);
  const weakest = CATEGORIES.filter((_, i) => subtotals[i] === lowest);

  return {
    total,
    subtotals: Object.fromEntries(CATEGORIES.map((c, i) => [c, subtotals[i]])),
    band: bandFor(total),
    lowestSubtotal: lowest,
    /** Every category tied at the lowest. One entry means an unambiguous weakest signal. */
    weakestSignals: weakest,
    /**
     * A five-way tie is not a weakest signal, and the page says so rather than
     * picking one. Naming a winner from a tie is the kind of small dishonesty
     * that an instrument selling credibility cannot afford.
     */
    weakestSignal: weakest.length === 1 ? weakest[0] : null,
    isFiveWayTie: weakest.length === CATEGORIES.length
  };
}

/** Build an answer set summing to `total`, for boundary testing. */
export function answersForTotal(total) {
  if (!Number.isInteger(total) || total < 0 || total > MAX_TOTAL) {
    throw new RangeError(`total must be an integer 0..${MAX_TOTAL}`);
  }
  const answers = CATEGORIES.map(() => new Array(STATEMENTS_PER_CATEGORY).fill(0));
  let remaining = total;
  for (let c = 0; c < CATEGORIES.length && remaining > 0; c++) {
    for (let s = 0; s < STATEMENTS_PER_CATEGORY && remaining > 0; s++) {
      const give = Math.min(MAX_PER_STATEMENT, remaining);
      answers[c][s] = give;
      remaining -= give;
    }
  }
  return answers;
}

/** The exact boundaries worth testing: either side of every band edge, plus the extremes. */
export const BOUNDARY_TOTALS = Object.freeze([0, 15, 16, 23, 24, 31, 32, 39, 40]);

/**
 * One concrete first move per signal, mirrored from the page's NEXT_MOVE map.
 * Only the keys are asserted by the harness — that a move exists for every
 * category and for no other key. The wording is editorial and lives in the page.
 */
export const NEXT_MOVE_KEYS = Object.freeze([...CATEGORIES]);
