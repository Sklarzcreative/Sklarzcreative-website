/**
 * Read an image's REAL intrinsic dimensions from the file header.
 *
 * WHY NOT TRUST THE MARKUP
 * The launch QA found three assets whose declared width/height did not match
 * the file — a headshot declared 900x1100 that was 900x900, two diagrams
 * declared 1080x1080 that were 1200x800. Declared dimensions are a promise the
 * browser uses to reserve space; a wrong one shifts the layout when the image
 * decodes. The only way to check the promise is to read the file.
 *
 * Supports PNG, JPEG, GIF, WebP and SVG. Anything else returns
 * { format: 'unknown' } rather than a guess.
 */
import { readFileSync } from 'node:fs';

function svgDimensions(text) {
  const tag = text.match(/<svg\b[^>]*>/i);
  if (!tag) return null;
  const attr = name => {
    const m = tag[0].match(new RegExp(`\\b${name}\\s*=\\s*["']([^"']+)["']`, 'i'));
    return m ? m[1].trim() : null;
  };
  const parse = v => {
    if (v == null) return null;
    const n = parseFloat(v);
    // A percentage width tells you nothing about intrinsic size.
    return Number.isFinite(n) && !v.includes('%') ? n : null;
  };
  let width = parse(attr('width'));
  let height = parse(attr('height'));
  const viewBox = attr('viewBox');
  if ((width == null || height == null) && viewBox) {
    const parts = viewBox.split(/[\s,]+/).map(Number);
    if (parts.length === 4 && parts.every(Number.isFinite)) {
      width = width ?? parts[2];
      height = height ?? parts[3];
    }
  }
  return width != null && height != null ? { width, height, format: 'svg' } : null;
}

function jpegDimensions(buf) {
  // Walk the segment chain to the first Start-Of-Frame marker.
  let offset = 2;
  while (offset < buf.length - 9) {
    if (buf[offset] !== 0xff) { offset++; continue; }
    const marker = buf[offset + 1];
    // SOF0..SOF15, excluding the non-frame markers at C4, C8 and CC.
    if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
      return {
        height: buf.readUInt16BE(offset + 5),
        width: buf.readUInt16BE(offset + 7),
        format: 'jpeg'
      };
    }
    if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { offset += 2; continue; }
    const length = buf.readUInt16BE(offset + 2);
    if (length < 2) return null;
    offset += 2 + length;
  }
  return null;
}

function webpDimensions(buf) {
  const chunk = buf.toString('ascii', 12, 16);
  if (chunk === 'VP8 ') {
    return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff, format: 'webp' };
  }
  if (chunk === 'VP8L') {
    const bits = buf.readUInt32LE(21);
    return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1, format: 'webp' };
  }
  if (chunk === 'VP8X') {
    const width = 1 + (buf[24] | (buf[25] << 8) | (buf[26] << 16));
    const height = 1 + (buf[27] | (buf[28] << 8) | (buf[29] << 16));
    return { width, height, format: 'webp' };
  }
  return null;
}

/**
 * @returns {{width: number, height: number, format: string} | {format: 'unknown', reason: string}}
 */
export function imageSize(filePath) {
  let buf;
  try {
    buf = readFileSync(filePath);
  } catch (err) {
    return { format: 'unknown', reason: `could not read: ${err.code ?? err.message}` };
  }
  if (buf.length < 24) return { format: 'unknown', reason: 'file too short to carry a header' };

  try {
    if (buf.toString('ascii', 1, 4) === 'PNG' && buf[0] === 0x89) {
      return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20), format: 'png' };
    }
    if (buf[0] === 0xff && buf[1] === 0xd8) {
      return jpegDimensions(buf) ?? { format: 'unknown', reason: 'no JPEG SOF marker found' };
    }
    if (buf.toString('ascii', 0, 3) === 'GIF') {
      return { width: buf.readUInt16LE(6), height: buf.readUInt16LE(8), format: 'gif' };
    }
    if (buf.toString('ascii', 0, 4) === 'RIFF' && buf.toString('ascii', 8, 12) === 'WEBP') {
      return webpDimensions(buf) ?? { format: 'unknown', reason: 'unrecognised WebP chunk' };
    }
    const head = buf.toString('utf8', 0, Math.min(buf.length, 4096));
    if (head.includes('<svg')) {
      return svgDimensions(buf.toString('utf8')) ?? { format: 'svg', reason: 'no intrinsic size declared', width: null, height: null };
    }
  } catch (err) {
    return { format: 'unknown', reason: `header parse failed: ${err.message}` };
  }
  return { format: 'unknown', reason: 'unrecognised image format' };
}
