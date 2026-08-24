/**
 * A dependency-free JSON Schema validator, covering the subset this repository
 * actually uses.
 *
 * WHY NOT ajv
 * The website has zero dependencies and that is a deliberate, defended
 * property. The automation directory allows exactly one — Playwright, because
 * driving a real browser cannot be reimplemented. Everything else stays
 * dependency-free so that `node automation/lib/validate.mjs` works on a clean
 * checkout with no install step, which is the difference between a validator
 * that gets run and one that does not.
 *
 * SUPPORTED
 *   $ref (local, #/$defs/... and #/definitions/...), type (incl. arrays and
 *   "null"), enum, const, required, properties, patternProperties,
 *   additionalProperties, items, prefixItems, minItems, maxItems, uniqueItems,
 *   minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf,
 *   minLength, maxLength, pattern, format (date-time, date, email, uri),
 *   allOf, anyOf, oneOf, not, minProperties, maxProperties, dependentRequired.
 *
 * NOT SUPPORTED — and it throws rather than ignoring them, because a validator
 * that silently skips a keyword reports a pass it did not verify:
 *   remote $ref, $dynamicRef, if/then/else, unevaluatedProperties, contains.
 *
 * USAGE
 *   node automation/lib/validate.mjs <schema.json> <instance.json> [more.json]
 *   import { validate } from './validate.mjs'
 */

const UNSUPPORTED = [
  '$dynamicRef', '$dynamicAnchor', 'if', 'then', 'else',
  'unevaluatedProperties', 'unevaluatedItems', 'contains'
];

const FORMATS = {
  'date-time': v => !Number.isNaN(Date.parse(v)) && /^\d{4}-\d{2}-\d{2}T/.test(v),
  date: v => /^\d{4}-\d{2}-\d{2}$/.test(v) && !Number.isNaN(Date.parse(v)),
  email: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v),
  uri: v => /^[a-z][a-z0-9+.-]*:/i.test(v)
};

function typeOf(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  if (Number.isInteger(value)) return 'integer';
  return typeof value;
}

function typeMatches(value, expected) {
  const actual = typeOf(value);
  if (expected === 'number') return actual === 'number' || actual === 'integer';
  if (expected === 'integer') return actual === 'integer';
  return actual === expected;
}

function resolveRef(ref, root) {
  if (!ref.startsWith('#')) {
    throw new Error(`validate.mjs: remote $ref is not supported: ${ref}`);
  }
  const parts = ref.slice(1).split('/').filter(Boolean);
  let node = root;
  for (const raw of parts) {
    const key = raw.replace(/~1/g, '/').replace(/~0/g, '~');
    if (node == null || !Object.prototype.hasOwnProperty.call(node, key)) {
      throw new Error(`validate.mjs: $ref does not resolve: ${ref}`);
    }
    node = node[key];
  }
  return node;
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (typeOf(a) !== typeOf(b)) return false;
  if (Array.isArray(a)) {
    return a.length === b.length && a.every((x, i) => deepEqual(x, b[i]));
  }
  if (a && typeof a === 'object') {
    const ka = Object.keys(a), kb = Object.keys(b);
    return ka.length === kb.length && ka.every(k => deepEqual(a[k], b[k]));
  }
  return false;
}

/**
 * Collect every failure rather than stopping at the first. A validator that
 * reports one error per run turns a ten-field mistake into ten round trips.
 */
function check(value, schema, root, path, errors) {
  if (schema === true || schema === undefined) return;
  if (schema === false) {
    errors.push({ path, message: 'schema is false — nothing validates here' });
    return;
  }

  for (const keyword of UNSUPPORTED) {
    if (Object.prototype.hasOwnProperty.call(schema, keyword)) {
      throw new Error(
        `validate.mjs: unsupported keyword "${keyword}" at ${path || '#'}. ` +
        'Refusing to validate rather than skipping it silently.'
      );
    }
  }

  if (schema.$ref) {
    check(value, resolveRef(schema.$ref, root), root, path, errors);
    // Sibling keywords alongside $ref are valid in 2020-12 and still apply.
  }

  if (schema.type !== undefined) {
    const allowed = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!allowed.some(t => typeMatches(value, t))) {
      errors.push({
        path,
        message: `expected type ${allowed.join(' | ')}, got ${typeOf(value)}`
      });
      return; // Further keyword checks would be noise once the type is wrong.
    }
  }

  if (schema.enum !== undefined && !schema.enum.some(e => deepEqual(e, value))) {
    errors.push({ path, message: `value ${JSON.stringify(value)} is not one of ${JSON.stringify(schema.enum)}` });
  }
  if (schema.const !== undefined && !deepEqual(schema.const, value)) {
    errors.push({ path, message: `value must be ${JSON.stringify(schema.const)}` });
  }

  for (const [key, subs] of [['allOf', schema.allOf], ['anyOf', schema.anyOf], ['oneOf', schema.oneOf]]) {
    if (!Array.isArray(subs)) continue;
    const results = subs.map(sub => {
      const local = [];
      check(value, sub, root, path, local);
      return local;
    });
    const passing = results.filter(r => r.length === 0).length;
    if (key === 'allOf' && passing !== subs.length) {
      results.forEach(r => errors.push(...r));
    }
    if (key === 'anyOf' && passing === 0) {
      errors.push({ path, message: `matched none of the ${subs.length} anyOf alternatives` });
    }
    if (key === 'oneOf' && passing !== 1) {
      errors.push({ path, message: `matched ${passing} of the oneOf alternatives, expected exactly 1` });
    }
  }
  if (schema.not !== undefined) {
    const local = [];
    check(value, schema.not, root, path, local);
    if (local.length === 0) errors.push({ path, message: 'value matched a "not" schema' });
  }

  const kind = typeOf(value);

  if (kind === 'string') {
    if (schema.minLength !== undefined && [...value].length < schema.minLength) {
      errors.push({ path, message: `shorter than minLength ${schema.minLength}` });
    }
    if (schema.maxLength !== undefined && [...value].length > schema.maxLength) {
      errors.push({ path, message: `longer than maxLength ${schema.maxLength} (is ${[...value].length})` });
    }
    if (schema.pattern !== undefined && !new RegExp(schema.pattern, 'u').test(value)) {
      errors.push({ path, message: `does not match pattern ${schema.pattern}` });
    }
    if (schema.format !== undefined) {
      const fn = FORMATS[schema.format];
      if (fn && !fn(value)) {
        errors.push({ path, message: `not a valid ${schema.format}` });
      }
    }
  }

  if (kind === 'number' || kind === 'integer') {
    if (schema.minimum !== undefined && value < schema.minimum) {
      errors.push({ path, message: `below minimum ${schema.minimum}` });
    }
    if (schema.maximum !== undefined && value > schema.maximum) {
      errors.push({ path, message: `above maximum ${schema.maximum}` });
    }
    if (schema.exclusiveMinimum !== undefined && value <= schema.exclusiveMinimum) {
      errors.push({ path, message: `must be greater than ${schema.exclusiveMinimum}` });
    }
    if (schema.exclusiveMaximum !== undefined && value >= schema.exclusiveMaximum) {
      errors.push({ path, message: `must be less than ${schema.exclusiveMaximum}` });
    }
    if (schema.multipleOf !== undefined && value % schema.multipleOf !== 0) {
      errors.push({ path, message: `not a multiple of ${schema.multipleOf}` });
    }
  }

  if (kind === 'array') {
    if (schema.minItems !== undefined && value.length < schema.minItems) {
      errors.push({ path, message: `fewer than minItems ${schema.minItems}` });
    }
    if (schema.maxItems !== undefined && value.length > schema.maxItems) {
      errors.push({ path, message: `more than maxItems ${schema.maxItems}` });
    }
    if (schema.uniqueItems === true) {
      for (let i = 0; i < value.length; i++) {
        for (let j = i + 1; j < value.length; j++) {
          if (deepEqual(value[i], value[j])) {
            errors.push({ path, message: `items ${i} and ${j} are duplicates` });
          }
        }
      }
    }
    const prefix = schema.prefixItems || [];
    value.forEach((item, i) => {
      if (i < prefix.length) check(item, prefix[i], root, `${path}[${i}]`, errors);
      else if (schema.items !== undefined) check(item, schema.items, root, `${path}[${i}]`, errors);
    });
  }

  if (kind === 'object') {
    const keys = Object.keys(value);
    if (schema.minProperties !== undefined && keys.length < schema.minProperties) {
      errors.push({ path, message: `fewer than minProperties ${schema.minProperties}` });
    }
    if (schema.maxProperties !== undefined && keys.length > schema.maxProperties) {
      errors.push({ path, message: `more than maxProperties ${schema.maxProperties}` });
    }
    for (const required of schema.required || []) {
      if (!Object.prototype.hasOwnProperty.call(value, required)) {
        errors.push({ path: `${path}.${required}`, message: 'required property is missing' });
      }
    }
    for (const [prop, needed] of Object.entries(schema.dependentRequired || {})) {
      if (!Object.prototype.hasOwnProperty.call(value, prop)) continue;
      for (const dep of needed) {
        if (!Object.prototype.hasOwnProperty.call(value, dep)) {
          errors.push({ path: `${path}.${dep}`, message: `required because "${prop}" is present` });
        }
      }
    }

    const patternProps = Object.entries(schema.patternProperties || {});
    for (const key of keys) {
      const childPath = `${path}.${key}`;
      let matched = false;
      if (schema.properties && Object.prototype.hasOwnProperty.call(schema.properties, key)) {
        matched = true;
        check(value[key], schema.properties[key], root, childPath, errors);
      }
      for (const [pattern, sub] of patternProps) {
        if (new RegExp(pattern, 'u').test(key)) {
          matched = true;
          check(value[key], sub, root, childPath, errors);
        }
      }
      if (!matched && schema.additionalProperties !== undefined) {
        if (schema.additionalProperties === false) {
          errors.push({ path: childPath, message: 'property is not allowed (additionalProperties: false)' });
        } else {
          check(value[key], schema.additionalProperties, root, childPath, errors);
        }
      }
    }
  }
}

/** @returns {{ valid: boolean, errors: Array<{path: string, message: string}> }} */
export function validate(instance, schema) {
  const errors = [];
  check(instance, schema, schema, '', errors);
  return { valid: errors.length === 0, errors };
}

/** Throws with every failure listed. For use inside an agent before it presents output. */
export function assertValid(instance, schema, label = 'instance') {
  const { valid, errors } = validate(instance, schema);
  if (!valid) {
    throw new Error(
      `${label} failed schema validation:\n` +
      errors.map(e => `  ${e.path || '#'}: ${e.message}`).join('\n')
    );
  }
  return instance;
}

/* ------------------------------------------------------------------ CLI --- */

if (import.meta.url === `file://${process.argv[1]}`) {
  const { readFileSync } = await import('node:fs');
  const [schemaPath, ...instancePaths] = process.argv.slice(2);

  if (!schemaPath || instancePaths.length === 0) {
    console.error('usage: node automation/lib/validate.mjs <schema.json> <instance.json> [more.json ...]');
    process.exit(2);
  }

  const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));
  let failed = 0;

  for (const instancePath of instancePaths) {
    let result;
    try {
      result = validate(JSON.parse(readFileSync(instancePath, 'utf8')), schema);
    } catch (err) {
      console.error(`FAIL  ${instancePath}\n      ${err.message}`);
      failed++;
      continue;
    }
    if (result.valid) {
      console.log(`PASS  ${instancePath}`);
    } else {
      failed++;
      console.error(`FAIL  ${instancePath}`);
      for (const e of result.errors) console.error(`      ${e.path || '#'}: ${e.message}`);
    }
  }

  process.exit(failed === 0 ? 0 : 1);
}
