/**
 * Tests for the validator itself. A validator nobody tested is a source of
 * false confidence: every schema check downstream is only as trustworthy as
 * this file.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validate, assertValid } from '../lib/validate.mjs';

test('types, including nullable unions and integer vs number', () => {
  assert.equal(validate(1, { type: 'integer' }).valid, true);
  assert.equal(validate(1.5, { type: 'integer' }).valid, false);
  assert.equal(validate(1.5, { type: 'number' }).valid, true);
  assert.equal(validate(1, { type: 'number' }).valid, true);
  assert.equal(validate(null, { type: ['integer', 'null'] }).valid, true);
  assert.equal(validate(null, { type: 'integer' }).valid, false);
  assert.equal(validate([], { type: 'array' }).valid, true);
  assert.equal(validate([], { type: 'object' }).valid, false, 'an array is not an object here');
  assert.equal(validate(null, { type: 'object' }).valid, false, 'null is not an object here');
});

test('required, additionalProperties and nested paths are reported precisely', () => {
  const schema = {
    type: 'object', required: ['a'], additionalProperties: false,
    properties: { a: { type: 'object', required: ['b'], properties: { b: { type: 'string' } } } }
  };
  const { valid, errors } = validate({ a: {}, z: 1 }, schema);
  assert.equal(valid, false);
  const paths = errors.map(e => e.path);
  assert.ok(paths.includes('.a.b'), 'nested required path reported');
  assert.ok(paths.includes('.z'), 'unexpected property reported');
});

test('every error is collected, not just the first', () => {
  const schema = { type: 'object', required: ['a', 'b', 'c'] };
  assert.equal(validate({}, schema).errors.length, 3);
});

test('oneOf requires exactly one match', () => {
  const schema = {
    oneOf: [
      { type: 'object', required: ['value', 'source'], properties: { value: { type: 'number' }, source: { type: 'string' } }, additionalProperties: false },
      { type: 'object', required: ['value', 'reason'], properties: { value: { const: 'NOT AVAILABLE' }, reason: { type: 'string' } }, additionalProperties: false }
    ]
  };
  assert.equal(validate({ value: 1, source: 's' }, schema).valid, true);
  assert.equal(validate({ value: 'NOT AVAILABLE', reason: 'r' }, schema).valid, true);
  assert.equal(validate({ value: 1 }, schema).valid, false, 'a number with no source matches neither');
  assert.equal(validate({ value: 'NOT AVAILABLE' }, schema).valid, false);
});

test('local $ref resolves, and a remote one throws rather than being skipped', () => {
  const schema = { $defs: { count: { type: ['integer', 'null'], minimum: 0 } }, properties: { n: { $ref: '#/$defs/count' } }, type: 'object' };
  assert.equal(validate({ n: 3 }, schema).valid, true);
  assert.equal(validate({ n: -1 }, schema).valid, false);
  assert.equal(validate({ n: null }, schema).valid, true);
  assert.throws(() => validate({}, { $ref: 'https://example.test/s.json' }), /remote \$ref is not supported/);
});

test('an unsupported keyword throws instead of silently passing', () => {
  // A validator that skips a keyword reports a pass it did not verify.
  assert.throws(() => validate({}, { if: { const: 1 }, then: { const: 2 } }), /unsupported keyword "if"/);
  assert.throws(() => validate([], { contains: { type: 'string' } }), /unsupported keyword "contains"/);
});

test('string length counts characters, not UTF-16 code units', () => {
  const schema = { type: 'string', maxLength: 2 };
  assert.equal(validate('ab', schema).valid, true);
  assert.equal(validate('abc', schema).valid, false);
  assert.equal(validate('😀😀', schema).valid, true, 'two emoji are two characters, not four');
});

test('formats are checked where declared', () => {
  assert.equal(validate('2026-08-24T00:00:00Z', { format: 'date-time', type: 'string' }).valid, true);
  assert.equal(validate('2026-08-24', { format: 'date-time', type: 'string' }).valid, false);
  assert.equal(validate('2026-08-24', { format: 'date', type: 'string' }).valid, true);
  assert.equal(validate('not an email', { format: 'email', type: 'string' }).valid, false);
  assert.equal(validate('a@b.test', { format: 'email', type: 'string' }).valid, true);
});

test('uniqueItems catches deep duplicates', () => {
  const schema = { type: 'array', uniqueItems: true };
  assert.equal(validate([{ a: 1 }, { a: 1 }], schema).valid, false);
  assert.equal(validate([{ a: 1 }, { a: 2 }], schema).valid, true);
});

test('assertValid throws with every failure listed', () => {
  assert.throws(
    () => assertValid({}, { type: 'object', required: ['a', 'b'] }, 'pack'),
    err => /pack failed schema validation/.test(err.message) && /\.a/.test(err.message) && /\.b/.test(err.message)
  );
});
