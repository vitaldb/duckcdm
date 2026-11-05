"""Small-cell suppression for what the WebAPI hands to the browser.

SMALL_CELL_MIN=N (default 0 = off): any person/record count in 1..N-1 leaves the server as MASK, and the
ATLAS page (cells.js) shows MASK as "<N" — and as "—" where the page scaled it (rates per 1,000, percentages). Achilles report rows carrying such a count are dropped instead,
the way Achilles' own min-cell option does, since charts cannot draw "<N".
Differencing (base - final, sums of the rest) is not prevented.
"""
import os

MIN = int(os.environ.get('SMALL_CELL_MIN', '0') or 0)
MASK = -999999                     # never a real count; cells.js renders it as "<MIN"


def small(n):
    return bool(MIN) and isinstance(n, (int, float)) and 0 < n < MIN


def mask(n):
    return MASK if small(n) else n


def row_ok(row):
    """False for an Achilles report row that carries a small count."""
    for k, v in row.items():
        k = k.lower()
        if ('count' in k or k.startswith('num_person')) and small(v):
            return False
    return True


def page_js():
    """Loaded first by index.html: hide the login control (the portal authenticates) and render MASK as "<MIN"."""
    label = '<%d' % MIN if MIN else ''
    return """(function(){
var S=%d,L=%s,s=document.createElement('style');
s.textContent='.nav-bar__auth{display:none!important}';document.head.appendChild(s);
if(!L)return;
var d=Object.getOwnPropertyDescriptor(Intl.NumberFormat.prototype,'format');
Object.defineProperty(Intl.NumberFormat.prototype,'format',{configurable:true,get:function(){var f=d.get.call(this);return function(v){return Number(v)===S?L:f(v)}}});
var t=Number.prototype.toLocaleString;Number.prototype.toLocaleString=function(){return Number(this)===S?L:t.apply(this,arguments)};
var num=function(m){var x=parseFloat(m.replace(/[,%%]/g,''));if(x===S&&m.indexOf('%%')<0)return L;
 return m.replace(/\\D/g,'').indexOf('999999')===0?'\\u2014':m};
var txt=function(v){var w=v.replace(/-\\d[\\d,]*(?:\\.\\d+)?%%?/g,num).replace(/-\\d{5,}(?:\\.\\d+)?%%/g,'\\u2014');
 if(w.indexOf(L)>=0)w=w.replace(/\\u25bc\\s?[\\d,]+/g,'\\u25bc\\u2014');return w};
var fix=function(n){if(n.nodeType===3){var w=txt(n.nodeValue);if(w!==n.nodeValue)n.nodeValue=w}else{for(var c=n.firstChild;c;c=c.nextSibling)fix(c)}};
new MutationObserver(function(ms){ms.forEach(function(m){if(m.type==='characterData')fix(m.target);else m.addedNodes.forEach(fix)})}).observe(document.documentElement,{subtree:true,childList:true,characterData:true});
})();""" % (MASK, repr(label))
