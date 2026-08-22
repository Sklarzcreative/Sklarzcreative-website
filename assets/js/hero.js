/* ==========================================================================
   SKLARZ CREATIVE — CINEMATIC HERO  ·  "The Signal Prism"
   --------------------------------------------------------------------------
   One unforgettable object: a faceted gold monolith turning slowly inside a
   navy void, wrapped by a single thin orbital ring. Light rakes across the
   facets; dust drifts through the beam. The read is precision, singularity,
   and something worth trusting.

   Built as a raymarched signed-distance scene in one fragment shader, with no
   3D library at all. That is a deliberate call: Three.js would add ~600 KB
   transfer to a hero that needs exactly one object, and hand-authoring the
   material is the only way to get anisotropic brushed gold that matches the
   brand swatch rather than a generic chrome preset.

   Guards, in order of importance:
     · no WebGL, or shader compile failure  → CSS gradient stays, canvas hidden
     · prefers-reduced-motion               → one static frame, no loop
     · hero scrolled out of view            → loop stops
     · tab hidden                           → loop stops
     · sustained slow frames                → resolution steps down, then bails
   ========================================================================== */
(function () {
  'use strict';

  var canvas = document.querySelector('[data-hero-canvas]');
  if (!canvas) return;

  /* ---------------------------------------------------------------- shaders */

  var VERT = [
    'attribute vec2 aPos;',
    'void main(){ gl_Position = vec4(aPos, 0.0, 1.0); }'
  ].join('\n');

  var FRAG = [
    '#ifdef GL_FRAGMENT_PRECISION_HIGH',
    'precision highp float;',
    '#else',
    'precision mediump float;',
    '#endif',

    'uniform vec2  uRes;',
    'uniform vec2  uPointer;',   // damped pointer, -1..1
    'uniform vec2  uCenter;      // object offset in uv space',
    'uniform float uTime;',
    'uniform float uScroll;',    // 0..1 across the hero
    'uniform float uIntro;',     // 0..1 load choreography
    'uniform float uSteps;',     // march budget, lowered on weak hardware
    'uniform float uPortrait;',  // 1.0 when the object sits behind the type

    /* Brand constants, linearised from the official swatches. */
    'const vec3 GOLD  = vec3(0.788, 0.659, 0.298);',  // #C9A84C
    'const vec3 CHAMP = vec3(0.882, 0.792, 0.514);',  // #E1CA83
    'const vec3 NAVY  = vec3(0.102, 0.184, 0.294);',  // #1A2F4B

    'mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }',

    'float hash1(vec2 p){',
    '  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);',
    '}',
    'vec2 hash2(vec2 p){',
    '  return fract(sin(vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)))) * 43758.5453);',
    '}',

    /* Value noise — drives the brushed-metal roughness breakup. */
    'float vnoise(vec2 p){',
    '  vec2 i = floor(p), f = fract(p);',
    '  f = f * f * (3.0 - 2.0 * f);',
    '  float a = hash1(i);',
    '  float b = hash1(i + vec2(1.0, 0.0));',
    '  float c = hash1(i + vec2(0.0, 1.0));',
    '  float d = hash1(i + vec2(1.0, 1.0));',
    '  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);',
    '}',

    'float sdOctahedron(vec3 p, float s){',
    '  p = abs(p);',
    '  return (p.x + p.y + p.z - s) * 0.57735027;',
    '}',
    'float sdTorus(vec3 p, vec2 t){',
    '  return length(vec2(length(p.xz) - t.x, p.y)) - t.y;',
    '}',

    /* Scene. x = distance, y = material id (1 monolith, 2 ring). */
    'vec2 map(vec3 p){',
    '  vec3 q = p;',
    '  float t = uTime * 0.075;',
    '  q.xz *= rot(t + uPointer.x * 0.26);',
    '  q.yz *= rot(sin(t * 0.62) * 0.11 + uPointer.y * 0.13 - uScroll * 0.22);',

    /* Monolith: a cut gem, not a plain solid. An octahedron stretched on Y
       gives the tapered silhouette; four 45-degree vertical planes cut its
       corners into an eight-sided girdle; flat caps finish the top and bottom.
       Roughly fourteen faces, which is what breaks the key light into separate
       highlights instead of two large flat washes.
       The distance is scaled by the smallest axis factor so the march stays a
       safe underestimate after the non-uniform squash. */
    '  vec3 s = q;',
    '  s.y *= 0.54;',
    '  float shard = sdOctahedron(s, 1.0) * 0.54;',
    '  shard = max(shard, (abs(q.x) + abs(q.z)) * 0.7071 - 0.96);',
    '  shard = max(shard, abs(q.x) - 0.92);',
    '  shard = max(shard, abs(q.z) - 0.92);',
    '  shard = max(shard, abs(q.y) - 1.46);',

    /* Single orbital ring — a thin gold filament tracing the object. */
    '  vec3 r = q;',
    '  r.yz *= rot(1.24);',
    '  r.xz *= rot(t * 1.6);',
    '  float ring = sdTorus(r, vec2(1.34, 0.017));',

    '  return shard < ring ? vec2(shard, 1.0) : vec2(ring, 2.0);',
    '}',

    'vec3 normalAt(vec3 p){',
    '  vec2 e = vec2(0.0013, 0.0);',
    '  return normalize(vec3(',
    '    map(p + e.xyy).x - map(p - e.xyy).x,',
    '    map(p + e.yxy).x - map(p - e.yxy).x,',
    '    map(p + e.yyx).x - map(p - e.yyx).x));',
    '}',

    'float ambientOcc(vec3 p, vec3 n){',
    '  float occ = 0.0, sca = 1.0;',
    '  for (int i = 0; i < 4; i++){',
    '    float h = 0.02 + 0.15 * float(i) / 3.0;',
    '    occ += (h - map(p + n * h).x) * sca;',
    '    sca *= 0.72;',
    '  }',
    '  return clamp(1.0 - 2.3 * occ, 0.0, 1.0);',
    '}',

    /* Procedural environment. Two lights live here rather than as discrete
       terms so the metal reflects them, which is what sells it as metal. */
    'vec3 env(vec3 d){',
    '  float h = d.y * 0.5 + 0.5;',
    '  vec3 c = mix(vec3(0.085, 0.056, 0.030), NAVY * 0.88, smoothstep(0.12, 0.96, h));',
    '  float key = pow(max(dot(d, normalize(vec3(0.52, 0.60, -0.60))), 0.0), 15.0);',
    '  c += CHAMP * key * 3.4;',
    '  float bounce = pow(max(dot(d, normalize(vec3(-0.62, -0.34, 0.32))), 0.0), 5.0);',
    '  c += GOLD * bounce * 0.34;',
    '  return c;',
    '}',

    /* Backdrop: navy gradient plus a warm bloom the monolith will occlude,
       which is what reads as a light source sitting behind the object. */
    'vec3 backdrop(vec2 uv){',
    '  vec3 c = mix(vec3(0.013, 0.026, 0.046), vec3(0.028, 0.058, 0.100),',
    '               smoothstep(-0.65, 0.85, uv.y));',
    '  float g = exp(-length((uv - vec2(0.26, 0.14)) * vec2(1.0, 1.22)) * 2.25);',
    '  c += GOLD * g * 0.30;',
    '  c += NAVY * exp(-length(uv + vec2(0.48, 0.34)) * 2.0) * 0.34;',
    '  return c;',
    '}',

    /* Three parallax layers of drifting dust. */
    'float dust(vec2 uv){',
    '  float acc = 0.0;',
    '  for (int i = 0; i < 3; i++){',
    '    float fi = float(i);',
    '    vec2 g = uv * (7.0 + fi * 8.0);',
    '    g.y += uTime * (0.055 + fi * 0.032);',
    '    g.x += sin(uTime * 0.14 + fi * 2.1) * 0.22;',
    '    vec2 id = floor(g);',
    '    vec2 f  = fract(g) - 0.5;',
    '    float d = length(f - (hash2(id + fi * 17.0) - 0.5) * 0.72);',
    '    acc += smoothstep(0.038, 0.0, d) * step(0.945, hash1(id + fi * 31.0)) * (0.55 - fi * 0.13);',
    '  }',
    '  return acc;',
    '}',

    'vec3 tonemap(vec3 x){',
    '  x = max(x, 0.0);',
    '  return (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14);',
    '}',

    'void main(){',
    '  vec2 uv = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;',
    '  vec2 suv = uv - uCenter;',

    '  vec3 col = backdrop(uv);',

    /* Camera. Scroll dollies back; the pointer nudges the ray, never the
       object, so the parallax feels like a head movement. The base distance is
       set so the monolith reads as an object in a room rather than filling the
       frame — it has to share the composition with the headline. */
    '  float dolly = 7.6 + uScroll * 1.9 + (1.0 - uIntro) * 1.1;',
    '  vec3 ro = vec3(0.0, 0.0, -dolly);',
    '  vec3 rd = normalize(vec3(suv, 1.52));',
    '  rd.yz *= rot(-uPointer.y * 0.055);',
    '  rd.xz *= rot( uPointer.x * 0.075);',

    '  float t = 0.0;',
    '  float mid = 0.0;',
    '  bool hit = false;',
    '  for (int i = 0; i < 96; i++){',
    '    if (float(i) >= uSteps) break;',
    '    vec3 p = ro + rd * t;',
    '    vec2 h = map(p);',
    '    if (h.x < 0.0016 * t + 0.0009){ hit = true; mid = h.y; break; }',
    '    t += h.x * 0.92;',
    '    if (t > 14.5) break;',
    '  }',

    '  if (hit){',
    '    vec3 p = ro + rd * t;',
    '    vec3 n = normalAt(p);',
    '    vec3 v = -rd;',
    '    float fres = pow(1.0 - max(dot(n, v), 0.0), 3.4);',
    '    vec3 m;',

    '    if (mid > 1.5){',
    /* The ring is a light trace, not a lit surface. Shading it as metal made
       it read grey, because a filament this thin mostly reflects the navy sky.
       Treating it as dim emissive gold keeps it on-brand at every angle while
       staying a supporting line rather than a bright white hoop. */
    '      m = GOLD * 0.62 + CHAMP * fres * 0.45;',
    '    } else {',

    /* Anisotropic brushed streaks: roughness varies around and along the
       object, so highlights smear the way turned metal does. */
    '      float streak = vnoise(vec2(atan(n.z, n.x) * 3.4, p.y * 26.0));',
    '      float rough = 0.11 + 0.24 * streak;',

    '      vec3 refl = reflect(rd, n);',
    '      vec3 spec = env(refl);',
    /* Cheap roughness blur: mix the sharp reflection toward a normal-facing
       sample instead of taking multiple env taps. */
    '      spec = mix(spec, env(normalize(n + refl * 0.35)), rough * 1.5);',

    '      float occ = ambientOcc(p, n);',

    /* Polished metal has almost no diffuse albedo — nearly everything you see
       is reflected environment. An earlier version added a Lambert key term
       and the gem immediately read as matte plastic, because every facet lit
       to a similar value. So: reflection carries the form, the key lives
       inside env() where the metal can actually mirror it, and the fill is a
       whisper of cool bounce that only rescues the darkest facets. */
    '      vec3 KEY  = normalize(vec3( 0.58,  0.74, -0.52));',
    '      vec3 FILL = normalize(vec3(-0.72, -0.20,  0.36));',
    '      vec3 RIM  = normalize(vec3(-0.30,  0.42,  0.85));',

    /* Schlick-tinted reflection. Multiplying the gold albedo straight into a
       navy reflection lands on olive green, which is what the shadow facets
       were doing. Blending the tint toward white at grazing angles — and
       adding a small untinted navy ambient — keeps the darks warm-to-cool
       instead of green. */
    '      float fs = pow(1.0 - max(dot(n, v), 0.0), 5.0);',
    '      vec3 F = mix(GOLD, vec3(1.0), fs);',
    '      m  = F * spec * 1.3 * occ;',
    '      m += GOLD * 0.06 * occ;',

    '      vec3 hv = normalize(KEY + v);',
    '      m += CHAMP * pow(max(dot(n, hv), 0.0), mix(230.0, 24.0, rough)) * 2.1;',

    '      float fd = max(dot(n, FILL), 0.0);',
    '      m += mix(NAVY, GOLD, 0.5) * fd * 0.26 * occ;',

    '      float rd2 = max(dot(n, RIM), 0.0);',
    '      m += CHAMP * pow(rd2, 3.0) * 0.16;',
    '      m += CHAMP * fres * 0.42;',

    /* Fine sparkle along the facet seams. */
    '      m += CHAMP * pow(streak, 6.0) * 0.20;',
    '    }',

    /* Fog the far side into the void so the object has real depth. */
    '    col = mix(col, m, 1.0 - smoothstep(8.2, 14.0, t));',
    '  }',

    '  col += CHAMP * dust(uv) * 0.5 * (1.0 - uScroll * 0.6);',

    /* Vignette, exposure ramp on load, and scroll fade. */
    '  col *= 1.0 - 0.55 * smoothstep(0.45, 1.35, length(uv * vec2(0.82, 1.0)));',
    '  col *= mix(0.35, 1.0, uIntro);',
    '  col *= 1.0 - uScroll * 0.55;',
    /* In portrait the object is a backdrop behind the headline, so pull it
       down hard — legibility of the type wins over spectacle. */
    '  col *= mix(1.0, 0.34, uPortrait);',

    '  col = tonemap(col * 0.95);',
    '  col = pow(col, vec3(0.4545));',

    /* Dither. Without this a navy gradient this dark bands visibly on 8-bit. */
    '  col += (hash1(gl_FragCoord.xy) - 0.5) / 255.0;',

    '  gl_FragColor = vec4(col, 1.0);',
    '}'
  ].join('\n');

  /* ------------------------------------------------------------------ setup */

  var gl = null;
  try {
    var opts = { alpha: false, antialias: false, depth: false, stencil: false,
                 powerPreference: 'high-performance', failIfMajorPerformanceCaveat: false };
    gl = canvas.getContext('webgl', opts) || canvas.getContext('experimental-webgl', opts);
  } catch (e) { gl = null; }

  if (!gl) return;   // CSS gradient fallback remains visible

  function compile(type, src) {
    var sh = gl.createShader(type);
    gl.shaderSource(sh, src);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      gl.deleteShader(sh);
      return null;
    }
    return sh;
  }

  var vs = compile(gl.VERTEX_SHADER, VERT);
  var fs = compile(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;

  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var aPos = gl.getAttribLocation(prog, 'aPos');
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  var U = {};
  ['uRes', 'uPointer', 'uCenter', 'uTime', 'uScroll', 'uIntro', 'uSteps', 'uPortrait'].forEach(function (k) {
    U[k] = gl.getUniformLocation(prog, k);
  });

  /* ------------------------------------------------------------------ state */

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var coarse  = window.matchMedia('(pointer: coarse)');

  var cores = navigator.hardwareConcurrency || 4;
  var weak  = cores <= 4 || coarse.matches;

  var scale    = weak ? 0.72 : 0.9;      // render scale below CSS pixels
  var maxDpr   = weak ? 1.25 : 1.6;
  var steps    = weak ? 46 : 82;

  var pointer = { x: 0, y: 0, tx: 0, ty: 0 };
  var scroll = 0;
  var intro = 0;
  var running = false;
  var visible = true;
  var frameId = 0;
  var startTime = 0;
  var w = 0, h = 0;

  /* Frame-time watchdog: degrade rather than stutter. */
  var samples = 0, accum = 0, tier = 0;

  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, maxDpr);
    var rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    w = Math.max(1, Math.round(rect.width  * dpr * scale));
    h = Math.max(1, Math.round(rect.height * dpr * scale));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    gl.viewport(0, 0, w, h);
  }

  function centerFor() {
    // Landscape: the object owns the right half, clear of the headline column.
    // Portrait: it centres and sits low, behind the type as a backdrop.
    var rect = canvas.getBoundingClientRect();
    var aspect = rect.height ? rect.width / rect.height : 1;
    return aspect > 1.05 ? [0.42, 0.10, 0.0] : [0.04, -0.62, 1.0];
  }

  function draw(timeMs) {
    var t = (timeMs - startTime) / 1000;
    var c = centerFor();

    gl.uniform2f(U.uRes, w, h);
    gl.uniform2f(U.uPointer, pointer.x, pointer.y);
    gl.uniform2f(U.uCenter, c[0], c[1]);
    gl.uniform1f(U.uTime, t);
    gl.uniform1f(U.uScroll, scroll);
    gl.uniform1f(U.uIntro, intro);
    gl.uniform1f(U.uSteps, steps);
    gl.uniform1f(U.uPortrait, c[2]);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  function degrade() {
    tier++;
    if (tier === 1)      { scale = 0.62; steps = Math.min(steps, 54); }
    else if (tier === 2) { scale = 0.5;  steps = Math.min(steps, 38); }
    else { stop(); return; }   // give up; the CSS gradient is a good hero on its own
    resize();
  }

  var last = 0;
  function loop(now) {
    if (!running) return;
    frameId = requestAnimationFrame(loop);

    // Damped pointer follow — the lag is what makes it feel like a camera.
    pointer.x += (pointer.tx - pointer.x) * 0.055;
    pointer.y += (pointer.ty - pointer.y) * 0.055;
    if (intro < 1) intro = Math.min(1, intro + 0.012);

    draw(now);

    if (last) {
      accum += now - last;
      if (++samples >= 70) {
        if (accum / samples > 27 && tier < 3) degrade();
        samples = 0; accum = 0;
      }
    }
    last = now;
  }

  function start() {
    if (running || reduced.matches) return;
    running = true;
    last = 0; samples = 0; accum = 0;
    if (!startTime) startTime = performance.now();
    frameId = requestAnimationFrame(loop);
  }

  function stop() {
    running = false;
    if (frameId) cancelAnimationFrame(frameId);
    frameId = 0;
  }

  /* ------------------------------------------------------------------ events */

  var hero = canvas.closest('.hero') || canvas.parentElement;

  function onScroll() {
    if (!hero) return;
    var rect = hero.getBoundingClientRect();
    var range = rect.height || 1;
    scroll = Math.min(1, Math.max(0, -rect.top / range));
    // Reduced motion still gets a correct single frame on demand.
    if (reduced.matches && visible) { resize(); draw(performance.now()); }
  }

  if (!coarse.matches) {
    window.addEventListener('pointermove', function (e) {
      pointer.tx = (e.clientX / window.innerWidth  - 0.5) * 2;
      pointer.ty = (e.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () { resize(); onScroll(); }, { passive: true });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop();
    else if (visible) start();
  });

  if ('IntersectionObserver' in window && hero) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && !document.hidden) start(); else stop();
    }, { threshold: 0 }).observe(hero);
  }

  if ('ResizeObserver' in window) {
    new ResizeObserver(function () { resize(); }).observe(canvas);
  }

  /* ------------------------------------------------------------------- boot */

  resize();
  onScroll();

  if (reduced.matches) {
    // One frame, fully lit, no animation loop at all.
    intro = 1;
    startTime = performance.now();
    draw(startTime);
  } else {
    startTime = performance.now();
    draw(startTime);   // paint frame zero before revealing, so there is no flash
    start();
  }

  requestAnimationFrame(function () { canvas.classList.add('is-ready'); });

  canvas.addEventListener('webglcontextlost', function (e) {
    e.preventDefault();
    stop();
    canvas.classList.remove('is-ready');
  });
  canvas.addEventListener('webglcontextrestored', function () {
    canvas.classList.add('is-ready');
    start();
  });
})();
