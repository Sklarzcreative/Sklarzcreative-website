import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  score, bandFor, answersForTotal, BOUNDARY_TOTALS,
  CATEGORIES, MAX_TOTAL, MAX_PER_CATEGORY, TOTAL_STATEMENTS, NEXT_MOVE_KEYS
} from '../lib/scorecard.mjs';

test('the instrument is 5 x 4 x 2 = 40', () => {
  assert.equal(CATEGORIES.length, 5);
  assert.equal(TOTAL_STATEMENTS, 20);
  assert.equal(MAX_PER_CATEGORY, 8);
  assert.equal(MAX_TOTAL, 40);
});

test('bands land on the documented thresholds, on both sides of every edge', () => {
  const expected = [
    [0, 'Rebuild the basics'], [15, 'Rebuild the basics'],
    [16, 'Inconsistent signals'], [23, 'Inconsistent signals'],
    [24, 'Solid foundation'], [31, 'Solid foundation'],
    [32, 'Strong trust system'], [40, 'Strong trust system']
  ];
  for (const [total, band] of expected) assert.equal(bandFor(total), band, `total ${total}`);
});

test('a total outside 0..40 is a range error, not a silently clamped band', () => {
  assert.throws(() => bandFor(-1), RangeError);
  assert.throws(() => bandFor(41), RangeError);
  assert.throws(() => bandFor(20.5), RangeError);
});

test('every boundary total is reachable and scores to itself', () => {
  for (const total of BOUNDARY_TOTALS) {
    const result = score(answersForTotal(total));
    assert.equal(result.total, total);
    assert.equal(result.band, bandFor(total));
  }
});

test('the weakest signal is the lowest category', () => {
  const result = score([[2, 2, 2, 2], [2, 2, 2, 2], [1, 1, 1, 0], [2, 2, 2, 2], [2, 2, 2, 1]]);
  assert.equal(result.total, 8 + 8 + 3 + 8 + 7);
  assert.equal(result.weakestSignal, 'Credibility');
  assert.deepEqual(result.weakestSignals, ['Credibility']);
  assert.equal(result.lowestSubtotal, 3);
});

test('a tie is reported as a tie and never resolved to a winner', () => {
  // Picking a winner from a tie is the kind of small dishonesty an instrument
  // that sells credibility cannot afford.
  const result = score([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2], [2, 2, 2, 2]]);
  assert.equal(result.weakestSignal, null, 'no single weakest signal on a tie');
  assert.deepEqual(result.weakestSignals, ['Clarity', 'Credibility']);
  assert.equal(result.isFiveWayTie, false);
});

test('a five-way tie is flagged as such rather than naming a weakest signal', () => {
  const result = score(CATEGORIES.map(() => [1, 1, 1, 1]));
  assert.equal(result.total, 20);
  assert.equal(result.isFiveWayTie, true);
  assert.equal(result.weakestSignal, null);
});

test('a perfect card has no weakest signal', () => {
  const result = score(CATEGORIES.map(() => [2, 2, 2, 2]));
  assert.equal(result.total, 40);
  assert.equal(result.band, 'Strong trust system');
  assert.equal(result.isFiveWayTie, true);
});

test('an all-zero card is a measured zero, not an absence', () => {
  const result = score(CATEGORIES.map(() => [0, 0, 0, 0]));
  assert.equal(result.total, 0);
  assert.equal(result.band, 'Rebuild the basics');
});

test('malformed input throws rather than scoring something plausible', () => {
  assert.throws(() => score(null), TypeError);
  assert.throws(() => score([[2, 2, 2, 2]]), TypeError, 'four categories missing');
  assert.throws(() => score(CATEGORIES.map(() => [2, 2, 2])), TypeError, 'three statements not four');
  assert.throws(() => score(CATEGORIES.map(() => [3, 0, 0, 0])), RangeError, '3 is outside 0..2');
  assert.throws(() => score(CATEGORIES.map(() => [-1, 0, 0, 0])), RangeError);
  assert.throws(() => score(CATEGORIES.map(() => [1.5, 0, 0, 0])), RangeError);
});

test('there is exactly one next move per category, and none for anything else', () => {
  assert.deepEqual([...NEXT_MOVE_KEYS].sort(), [...CATEGORIES].sort());
});

test('subtotals sum to the total, for every reachable total', () => {
  for (let t = 0; t <= MAX_TOTAL; t++) {
    const result = score(answersForTotal(t));
    const sum = Object.values(result.subtotals).reduce((a, b) => a + b, 0);
    assert.equal(sum, result.total, `subtotals must sum to the total at ${t}`);
    assert.equal(result.total, t);
  }
});
