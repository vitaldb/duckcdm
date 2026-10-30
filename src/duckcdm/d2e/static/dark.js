// Dark theme for the D2E portal. It follows the OS setting (prefers-color-scheme), as the app platform asks of apps.
// D2E 0.18 has no dark theme, and most of its styles are made in JS (MUI/emotion, the Vue plugins), so the colours are
// swapped where they are applied: every style rule (CSS files, <style> elements, insertRule), inline style attributes,
// SVG fill/stroke attributes and canvas drawing (charts). A colour gets the dark value of its role — text, surface,
// line or fill: TABLE names the dark value of D2E's own colours one by one; any other colour keeps its hue and gets a
// lightness for its role. Switching the OS setting reloads the page.
(function () {
  var mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
  if (!mq) return;
  if (mq.addEventListener) mq.addEventListener('change', function () { location.reload(); });
  if (!mq.matches) return;

  // D2E's colours (as #rrggbb) -> their dark value, per role; '*' applies to every role. D2E's navy (#000080) becomes
  // neutral grey, as the platform's own dark theme is (#0a0a0a page, #fafafa text, #a1a1a1 secondary text).
  var TABLE = {
    bg: {
      '#f2f0f1': '#0a0a0a', '#f2f0f0': '#0a0a0a', '#fbfbfd': '#141414', '#ffffff': '#171717', '#fafafb': '#141414',
      '#fafafa': '#141414', '#f5f5f5': '#1c1c1c', '#000080': '#404040', '#000e7e': '#404040', '#ebf1f8': '#1f1f1f',
      '#ebf2fa': '#1f1f1f', '#d2dbee': '#262626', '#ccdef1': '#262626'
    },
    text: {
      '#000080': '#ededed', '#000e7e': '#ededed', '#000000': '#fafafa', '#0a0a0a': '#fafafa', '#212121': '#ededed',
      '#333333': '#e0e0e0', '#464646': '#cfcfcf', '#666666': '#b0b0b0', '#737373': '#a1a1a1'
    },
    line: { '#e5e5e5': '#2e2e2e', '#000080': '#d4d4d4', '#000e7e': '#d4d4d4' },
    fill: { '#000080': '#a3a3a3', '#000e7e': '#a3a3a3' },   // chart series
    '*': {}
  };
  var NAMES = { white: '#ffffff', black: '#000000', gray: '#808080', grey: '#808080', silver: '#c0c0c0',
    lightgray: '#d3d3d3', lightgrey: '#d3d3d3', gainsboro: '#dcdcdc', whitesmoke: '#f5f5f5', darkgray: '#a9a9a9',
    darkgrey: '#a9a9a9', dimgray: '#696969', dimgrey: '#696969', navy: '#000080' };

  function hex2(n) { n = Math.round(Math.max(0, Math.min(255, n))); return (n < 16 ? '0' : '') + n.toString(16); }
  function parse(s) {
    var m, t = s.toLowerCase();
    if (NAMES[t]) t = NAMES[t];
    if ((m = /^#([0-9a-f]{3,8})$/.exec(t))) {
      var h = m[1];
      if (h.length === 3 || h.length === 4) h = h.replace(/./g, '$&$&');
      if (h.length !== 6 && h.length !== 8) return null;
      return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16),
        h.length === 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1];
    }
    if ((m = /^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*(?:[,/]\s*([\d.]+%?))?\s*\)$/.exec(t))) {
      var a = m[4] === undefined ? 1 : (m[4].slice(-1) === '%' ? parseFloat(m[4]) / 100 : parseFloat(m[4]));
      return [+m[1], +m[2], +m[3], a];
    }
    return null;
  }
  function hsl(c) {
    var r = c[0] / 255, g = c[1] / 255, b = c[2] / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    var l = (mx + mn) / 2, d = mx - mn, s = 0, h = 0;
    if (d) {
      s = d / (1 - Math.abs(2 * l - 1));
      h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
      h = (h * 60 + 360) % 360;
    }
    return [h, s, l];
  }
  function rgb(h, s, l) {
    var c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = l - c / 2, r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; } else if (h < 120) { r = x; g = c; } else if (h < 180) { g = c; b = x; }
    else if (h < 240) { g = x; b = c; } else if (h < 300) { r = x; b = c; } else { r = c; b = x; }
    return [(r + m) * 255, (g + m) * 255, (b + m) * 255];
  }
  function out(c, a) {
    return a >= 1 ? '#' + hex2(c[0]) + hex2(c[1]) + hex2(c[2])
      : 'rgba(' + Math.round(c[0]) + ', ' + Math.round(c[1]) + ', ' + Math.round(c[2]) + ', ' + +a.toFixed(3) + ')';
  }

  // the dark value of one colour in a role: text (glyphs), bg (surfaces), line (borders, shadows), fill (SVG, canvas)
  function swap(s, role) {
    var c = parse(s);
    if (!c) return s;
    var key = '#' + hex2(c[0]) + hex2(c[1]) + hex2(c[2]);
    var t = (role === 'fill' && TABLE.fill[key]) || TABLE[role === 'fill' ? (hsl(c)[2] < 0.5 ? 'text' : 'bg') : role][key]
      || TABLE['*'][key];
    if (t) { var tc = parse(t); return out(tc, c[3] * tc[3]); }
    var x = hsl(c), h = x[0], sat = x[1], l = x[2];
    var data = role === 'fill';
    if (role === 'fill') role = l < 0.5 ? 'text' : 'bg';
    if (data && sat >= 0.12 && l > 0.6 && l <= 0.88) {    // pastel chart colours: a deeper shade, labels stay readable
      return out(rgb(h, Math.min(sat, 0.55), 0.3 + (l - 0.6) * 0.4), c[3]);
    }
    if (h >= 200 && h <= 260 && (l > 0.85 || l < 0.45)) sat = 0;   // D2E's navy and its pale tints: grey
    if (Math.max(c[0], c[1], c[2]) - Math.min(c[0], c[1], c[2]) < 16 || sat < 0.12) {                       // greys: dark ones become light (text, lines), light surfaces become dark
      if (role === 'text') l = l < 0.5 ? 0.98 - 0.72 * l : l;
      else if (role === 'bg') l = l > 0.5 ? 0.09 + (1 - l) * 0.5 : l;
      else l = l > 0.5 ? 0.15 + (1 - l) * 0.6 : 0.55 - 0.4 * l;
    } else if (role === 'bg') {             // tints become dark tints; deep colours stay deep but visible
      if (l > 0.85) { l = 0.09 + (1 - l) * 0.9; sat = Math.min(sat, 0.35); }
      else if (l < 0.45) { l = Math.max(l, 0.38); sat = Math.min(sat, 0.6); }
    } else if (l < 0.45) {                  // deep colours as text or lines: the light shade of the same hue
      l = Math.min(Math.max(1 - l, 0.65), 0.82);
    }
    return out(rgb(h, sat, l), c[3]);
  }
  var COLOR = /#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|(?<![\w-])(?:white|black|gray|grey|silver|lightgr[ae]y|gainsboro|whitesmoke|darkgr[ae]y|dimgr[ae]y|navy)(?![\w-])/g;
  // colours in a value, and the variables it uses: var(--x) -> var(--x--dk-<role>), the copy of --x for that role
  function swapAll(v, role) {
    return v.replace(COLOR, function (m) { return swap(m, role); })
      .replace(/var\(\s*(--[\w-]+?)(?=\s*[,)])/g, function (m, n) { return n.indexOf('--dk-') > 0 ? m : 'var(' + n + '--dk-' + role; });
  }
  var ROLES = ['text', 'bg', 'line', 'fill'];
  // a variable's value: also a bare "r,g,b" (Vuetify keeps its theme colours so: rgb(var(--v-theme-surface)))
  function swapVar(v, role) {
    var m = /^\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*$/.exec(v);
    if (!m) return swapAll(v, role);
    var c = parse(swap('rgb(' + m[1] + ',' + m[2] + ',' + m[3] + ')', role));
    return Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]);
  }
  // a shorthand with a var() in it shows its value only on itself, its longhands read empty
  var SHORT = ['background', 'border', 'border-color', 'border-top', 'border-right', 'border-bottom', 'border-left',
    'border-block', 'border-inline', 'border-block-start', 'border-block-end', 'border-inline-start',
    'border-inline-end', 'outline', 'column-rule', 'text-decoration'];

  function role(p) {
    if (p === 'color' || p === 'caret-color' || p === 'text-decoration-color' || p === '-webkit-text-fill-color'
      || p === 'text-shadow') return 'text';
    if (p === 'background-color' || p === 'background-image' || p === 'background') return 'bg';
    if (p.indexOf('border') === 0 || p.indexOf('outline') === 0 || p === 'box-shadow' || p === 'column-rule-color')
      return 'line';
    if (p === 'fill' || p === 'stroke' || p === 'stop-color' || p === 'flood-color') return 'fill';
    return null;
  }

  // a custom property keeps its value and gets one dark copy per role (--x--dk-text, --x--dk-bg, ...): the same
  // variable is often both a background and a text colour, and its uses above point at the copy of their role
  function fixStyle(st, seen) {
    var props = [];
    for (var i = 0; i < st.length; i++) props.push(st[i]);
    props.forEach(function (p) {
      var custom = p.lastIndexOf('--', 0) === 0, r = custom ? null : role(p);
      if (seen && r === 'bg') r = 'fill';   // a colour set on one element (a legend swatch) is drawn like a chart's
      if ((!custom && !r) || (custom && p.indexOf('--dk-') > 0)) return;
      var v = st.getPropertyValue(p);
      if (!v || (seen && seen[p] === v)) return;
      if (seen) seen[p] = v;
      if (custom) {
        ROLES.forEach(function (x) { st.setProperty(p + '--dk-' + x, swapVar(v, x)); });
        if (seen) seen[p] = st.getPropertyValue(p);
        return;
      }
      var nv = swapAll(v, r);
      if (nv !== v) st.setProperty(p, nv, st.getPropertyPriority(p));
      if (seen) seen[p] = st.getPropertyValue(p);   // as the browser keeps it (#171717 reads back as rgb(23, 23, 23))
    });
    SHORT.forEach(function (p) {
      var v = st.getPropertyValue(p);
      if (!v || v.indexOf('var(') < 0 || (seen && seen[p] === v)) return;
      var nv = swapAll(v, p === 'background' ? (seen ? 'fill' : 'bg') : p === 'text-decoration' ? 'text' : 'line');
      if (nv !== v) st.setProperty(p, nv, st.getPropertyPriority(p));
      if (seen) seen[p] = st.getPropertyValue(p);
    });
  }
  var done = new WeakSet();
  function fixRules(rules) {
    for (var i = 0; i < rules.length; i++) {
      var r = rules[i];
      if (done.has(r)) continue;
      done.add(r);
      if (r.style) fixStyle(r.style);
      if (r.cssRules) fixRules(r.cssRules);
    }
  }
  function fixSheet(sh) { try { if (sh && sh !== own) fixRules(sh.cssRules); } catch (e) { /* another origin */ } }
  function fixSheets() {
    for (var i = 0; i < document.styleSheets.length; i++) fixSheet(document.styleSheets[i]);
  }

  // rules added one at a time (emotion, the CSS-in-JS of MUI, does this in production)
  var insert = CSSStyleSheet.prototype.insertRule;
  CSSStyleSheet.prototype.insertRule = function () {
    var i = insert.apply(this, arguments);
    if (this !== own) { try { fixRules([this.cssRules[i]]); } catch (e) { /* ignore */ } }
    return i;
  };

  // inline styles and SVG presentation attributes; what was written here is remembered so it is not swapped twice
  var mine = new WeakMap();
  function fixElement(el) {
    var rec = mine.get(el);
    if (!rec) { rec = { css: {}, attr: {} }; mine.set(el, rec); }
    if (el.style && el.style.length) fixStyle(el.style, rec.css);
    if (el.namespaceURI === 'http://www.w3.org/2000/svg') {
      ['fill', 'stroke', 'stop-color'].forEach(function (a) {
        var v = el.getAttribute(a);
        if (!v || rec.attr[a] === v) return;
        var nv = swapAll(v, 'fill');
        rec.attr[a] = nv;
        if (nv !== v) el.setAttribute(a, nv);
      });
    }
  }
  function fixTree(n) {
    if (n.nodeType !== 1) return;
    if (n.tagName === 'STYLE') fixSheet(n.sheet);
    else if (n.tagName === 'LINK') { fixSheet(n.sheet); n.addEventListener('load', function () { fixSheet(n.sheet); }); }
    if (n.hasAttribute('style') || n.hasAttribute('fill') || n.hasAttribute('stroke')) fixElement(n);
    var q = n.querySelectorAll('style,link[rel=stylesheet],[style],[fill],[stroke]');
    for (var i = 0; i < q.length; i++) {
      var e = q[i];
      if (e.tagName === 'STYLE') fixSheet(e.sheet);
      else if (e.tagName === 'LINK') { fixSheet(e.sheet); e.addEventListener('load', (function (l) { return function () { fixSheet(l.sheet); }; })(e)); }
      else fixElement(e);
    }
  }
  new MutationObserver(function (ms) {
    for (var i = 0; i < ms.length; i++) {
      var m = ms[i], t = m.target;
      if (m.type === 'attributes') { fixElement(t); continue; }
      var st = t.nodeType === 1 ? t : t.parentNode;   // text of a <style> changed: its rules are new
      if (st && st.tagName === 'STYLE') { fixSheet(st.sheet); continue; }
      for (var j = 0; j < m.addedNodes.length; j++) fixTree(m.addedNodes[j]);
    }
  }).observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true,
    attributeFilter: ['style', 'fill', 'stroke', 'stop-color'] });

  // charts drawn on a canvas
  if (window.CanvasRenderingContext2D) {
    ['fillStyle', 'strokeStyle', 'shadowColor'].forEach(function (k) {
      var d = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, k);
      if (!d || !d.set) return;
      Object.defineProperty(CanvasRenderingContext2D.prototype, k, { configurable: true, enumerable: d.enumerable,
        get: d.get, set: function (v) { d.set.call(this, typeof v === 'string' ? swap(v, 'fill') : v); } });
    });
  }

  // the page itself, form controls and scroll bars, and images drawn for a light page
  var el = document.createElement('style');
  el.textContent = ':root{color-scheme:dark}html,body{background:#0a0a0a;color:#fafafa}'
    + 'img.logo,img[src$="d2e-data2evidence.png"]{filter:brightness(0) invert(.92)}';
  document.head.appendChild(el);
  var own = el.sheet;
  fixSheets();
  document.addEventListener('DOMContentLoaded', function () { fixSheets(); fixTree(document.body); });
  window.addEventListener('load', fixSheets);
})();
