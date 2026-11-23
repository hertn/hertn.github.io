# Portfolio-style screenshot gallery for the hertn product pages (LiteTV, DarkShed, ChopPad):
# one big picture with ‹ › arrows and a caption, a strip of small thumbnails under it; a thumbnail makes that picture big.
# Run on a page that has a hero screenshot (a.heroshot) and a screenshots section (div.gallery of a.thumb):
# both are replaced by one gallery under the intro. Rerun safe: a page that already has the gallery is rebuilt from it.
import os, re, html, sys
H = os.path.expanduser('~')
GRID = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="8" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/></svg>'
HUB_NAV = f'<nav class="hub wrap" aria-label="More by hertn"><a href="https://hertn.github.io/">{GRID} All projects by hertn</a></nav>'
CSS = '''
/* screenshots: one big picture, arrows, and a strip of thumbnails under it */
.gal.wrap{padding-top:40px}
.gal>*{max-width:960px;margin-left:auto;margin-right:auto}
section.wrap{padding-top:56px;padding-bottom:56px}   /* .wrap's side padding would otherwise cancel the section spacing */
@media (max-width:600px){section.wrap{padding-top:40px;padding-bottom:40px}.gal.wrap{padding-top:28px}}
.gal-stage{position:relative;height:0;padding-top:62.5%;background:#0c0b0e;border:1px solid rgba(255,255,255,.12);border-radius:14px;overflow:hidden}   /* a 16:10 frame (padding trick: older Safari has no aspect-ratio) */
.gal-stage img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;display:block}   /* the whole picture always fits, never cropped */
.gal-btn{flex:0 0 auto;width:44px;height:44px;border-radius:50%;border:0;background:rgba(120,120,128,.24);color:#fff;font-size:28px;line-height:1;cursor:pointer;display:grid;place-items:center;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.gal-btn svg{width:22px;height:22px;display:block}
.gal-btn:hover{background:rgba(120,120,128,.4)}
.gal-btn:focus-visible{outline:3px solid #fff;outline-offset:2px}
.gal-on{position:absolute;top:50%;transform:translateY(-50%);background:rgba(20,20,24,.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}   /* arrows on the big picture */
.gal-on:hover{background:rgba(40,40,46,.9)}
.gal-on.gal-prev{left:12px}.gal-on.gal-next{right:12px}
.gal-cap{margin:12px 0 0;color:rgba(235,235,245,.72);font-size:.95rem;text-align:center;min-height:1.5em}
.gal-strip{display:flex;gap:10px;margin-top:14px;overflow-x:auto;padding:4px 2px 8px;scrollbar-width:thin}
.gal-strip button:first-child{margin-left:auto}.gal-strip button:last-child{margin-right:auto}   /* centred, but scrolls from the start when it overflows */
.gal-strip button{flex:0 0 auto;padding:0;border:2px solid transparent;border-radius:9px;background:none;cursor:pointer;opacity:.55;transition:opacity .15s,border-color .15s}
.gal-strip button:hover{opacity:.85}
.gal-strip button[aria-current="true"]{opacity:1;border-color:#fff}
.gal-strip button:focus-visible{outline:3px solid #fff;outline-offset:2px}
.gal-strip img{display:block;height:56px;width:auto;border-radius:7px}
@media (max-width:700px){.gal-strip img{height:44px}.gal-cap{font-size:.88rem}}
@media (prefers-reduced-motion:reduce){.gal-strip button{transition:none}}
.gal-stage img{cursor:zoom-in}
dialog.gal-lb{border:0;padding:0;margin:0;background:transparent;max-width:none;max-height:none;width:100%;height:100%;color:#fff}
dialog.gal-lb::backdrop{background:rgba(6,6,8,.95)}
.gal-lb-in{position:fixed;top:0;left:0;right:0;bottom:0;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 72px 76px}
.gal-lb-in img{display:block;max-width:100%;max-height:calc(100vh - 176px);width:auto;height:auto;border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,.6)}
.gal-lb-cap{margin:12px 0 0;color:rgba(235,235,245,.75);font-size:.95rem;text-align:center}
.gal-lb .gal-btn{position:fixed;top:50%;transform:translateY(-50%);width:48px;height:48px;background:rgba(40,40,46,.88)}
.gal-lb .gal-btn:hover{background:rgba(70,70,78,.95)}
.gal-lb .gal-prev{left:12px}.gal-lb .gal-next{right:12px}
.gal-lb .gal-close{top:14px;right:14px;transform:none}
#lbImg{cursor:zoom-in;touch-action:none;transform-origin:center;transition:transform .15s;user-select:none;-webkit-user-select:none;-webkit-user-drag:none}
#lbImg.zoomed{cursor:grab}#lbImg.drag{transition:none}#lbImg.zoomed.drag{cursor:grabbing}
.gal-zoom{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);display:flex;align-items:center;gap:2px;padding:4px;border-radius:999px;background:rgba(40,40,46,.88);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.gal-zoom button{width:40px;height:40px;border:0;border-radius:50%;background:none;color:#fff;font-size:22px;line-height:1;cursor:pointer}
.gal-zoom button:hover{background:rgba(255,255,255,.14)}
.gal-zoom button:focus-visible{outline:3px solid #fff;outline-offset:-3px}
.gal-zoom #lbFit{width:auto;padding:0 14px;border-radius:999px;font-size:.9rem;font-weight:600}
.gal-zoom span{min-width:52px;text-align:center;font-size:.9rem;font-variant-numeric:tabular-nums;color:rgba(235,235,245,.85)}
@media (prefers-reduced-motion:reduce){#lbImg{transition:none}}
@media (max-width:700px){.gal-lb-in{padding:60px 8px 80px}.gal-lb .gal-prev,.gal-lb .gal-next{top:auto;bottom:16px;transform:none}}
'''
JS = '''<script>
(() => {   // the screenshot gallery: arrows, the arrow keys, a swipe or a thumbnail change the big picture
  const g = document.getElementById('gal'); if (!g) return;
  const lb = document.getElementById('galLb'), lbImg = document.getElementById('lbImg'), lbCap = document.getElementById('lbCap');
  const big = document.getElementById('galImg'), cap = document.getElementById('galCap'), th = [...g.querySelectorAll('.gal-strip button')]; let i = 0, resetZoom = () => {};
  const show = n => {
    i = (n + th.length) % th.length; const t = th[i], im = t.querySelector('img');
    big.src = t.dataset.src; big.alt = im.alt; cap.textContent = t.dataset.cap + '  ·  ' + (i + 1) + ' of ' + th.length;
    lbImg.src = big.src; lbImg.alt = big.alt; lbCap.textContent = cap.textContent; resetZoom();
    th.forEach((b, k) => b.setAttribute('aria-current', String(k === i))); t.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  };
  th.forEach((b, k) => b.addEventListener('click', () => show(k)));
  document.getElementById('galPrev').onclick = () => show(i - 1);
  document.getElementById('galNext').onclick = () => show(i + 1);
  // the big picture opens full size; the arrows, keys and swipes keep working there (Esc or a click outside closes)
  if (lb.showModal) {
    big.addEventListener('click', () => { lbImg.src = big.src; lbImg.alt = big.alt; lbCap.textContent = cap.textContent; lb.showModal(); });
    document.getElementById('lbPrev').onclick = () => show(i - 1);
    document.getElementById('lbNext').onclick = () => show(i + 1);
    document.getElementById('lbClose').onclick = () => lb.close();
    lb.addEventListener('click', e => { if (moved) { moved = false; return; } if (e.target === lb || e.target.classList.contains('gal-lb-in')) lb.close(); });
    // zoom: − / + / Fit, the mouse wheel, a click (real size, again = fit), +/-/0 keys, pinch; drag moves a zoomed picture
    let z = 1, tx = 0, ty = 0, moved = false, pinch = null; const ptr = new Map(), zl = document.getElementById('lbZoom');
    const fit = () => lbImg.offsetWidth / (lbImg.naturalWidth || lbImg.offsetWidth || 1);   // fitted size / real size
    const apply = () => {
      const mx = Math.max(0, (lbImg.offsetWidth * z - innerWidth) / 2 + 24), my = Math.max(0, (lbImg.offsetHeight * z - innerHeight) / 2 + 24);
      if (z <= 1) tx = ty = 0; else { tx = Math.max(-mx, Math.min(mx, tx)); ty = Math.max(-my, Math.min(my, ty)); }
      lbImg.style.transform = `translate(${tx}px, ${ty}px) scale(${z})`; lbImg.classList.toggle('zoomed', z > 1);
      zl.textContent = Math.round(z * fit() * 100) + '%';
    };
    const zoomAt = (z2, px = innerWidth / 2, py = innerHeight / 2) => {   // keep the point under the mouse/fingers still
      z2 = Math.max(1, Math.min(Math.max(4, 3 / fit()), z2));
      const r = lbImg.getBoundingClientRect(), cx = r.left + r.width / 2 - tx, cy = r.top + r.height / 2 - ty;
      tx = px - cx - (z2 / z) * (px - cx - tx); ty = py - cy - (z2 / z) * (py - cy - ty); z = z2; apply();
    };
    resetZoom = () => { z = 1; tx = ty = 0; apply(); };
    lbImg.addEventListener('load', apply);
    document.getElementById('lbIn').onclick = () => zoomAt(z * 1.5);
    document.getElementById('lbOut').onclick = () => zoomAt(z / 1.5);
    document.getElementById('lbFit').onclick = () => resetZoom();
    lb.addEventListener('wheel', e => { e.preventDefault(); zoomAt(z * Math.exp(-e.deltaY * 0.0025), e.clientX, e.clientY); }, { passive: false });
    lb.addEventListener('keydown', e => { if (e.key === '+' || e.key === '=') zoomAt(z * 1.5); else if (e.key === '-') zoomAt(z / 1.5); else if (e.key === '0') resetZoom(); });
    lb.addEventListener('pointerdown', e => { if (e.target !== lbImg) moved = false; });
    lbImg.addEventListener('pointerdown', e => {
      lbImg.setPointerCapture(e.pointerId); ptr.set(e.pointerId, { x: e.clientX, y: e.clientY }); moved = false; lbImg.classList.add('drag');
      if (ptr.size === 2) { const [a, b] = [...ptr.values()]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y) || 1, z }; }
    });
    lbImg.addEventListener('pointermove', e => {
      const p = ptr.get(e.pointerId); if (!p) return; const dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
      if (Math.abs(dx) + Math.abs(dy) > 1) moved = true;
      if (pinch && ptr.size === 2) { const [a, b] = [...ptr.values()]; zoomAt(pinch.z * Math.hypot(a.x - b.x, a.y - b.y) / pinch.d, (a.x + b.x) / 2, (a.y + b.y) / 2); }
      else if (z > 1) { tx += dx; ty += dy; apply(); }
    });
    const up = e => { ptr.delete(e.pointerId); if (ptr.size < 2) pinch = null; if (!ptr.size) lbImg.classList.remove('drag'); };
    lbImg.addEventListener('pointerup', up); lbImg.addEventListener('pointercancel', up);
    lbImg.addEventListener('click', e => { if (moved) return; if (z > 1) resetZoom(); else zoomAt(Math.max(2, 1 / fit()), e.clientX, e.clientY); });
    addEventListener('resize', () => { if (lb.open) apply(); });
    let x1 = null, multi = false;   // a one-finger swipe flips, but only when not zoomed
    lb.addEventListener('touchstart', e => { if (e.touches.length > 1) multi = true; else x1 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => { if (e.touches.length) return; const m = multi; multi = false; if (x1 === null || m || z > 1) { x1 = null; return; } const dx = e.changedTouches[0].clientX - x1; if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1)); x1 = null; });
  } else big.style.cursor = 'default';
  g.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { show(i + 1); e.preventDefault(); } if (e.key === 'ArrowLeft') { show(i - 1); e.preventDefault(); } });
  let x0 = null; const st = g.querySelector('.gal-stage');
  st.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  st.addEventListener('touchend', e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1)); x0 = null; });
})();
</script>
'''
def attr(a, k): m = re.search(k + r'="([^"]*)"', a); return m.group(1) if m else ''

def unesc(x):
    """undo every layer of escaping: alts read from the page are escaped again on output (earlier builds stacked &amp;amp;...)"""
    while (y := html.unescape(x)) != x: x = y
    return x

def shots_of(s):
    """(src, alt, caption) in page order: the hero shot first, then the screenshots section; or from an existing gallery."""
    out = []
    if 'id="gal"' in s:
        for b in re.finditer(r'<button type="button" data-src="([^"]*)" data-cap="([^"]*)"[^>]*><img [^>]*alt="([^"]*)"', s): out.append((b.group(1), unesc(b.group(3)), unesc(b.group(2))))
        return out
    for a in re.finditer(r'<a class="(?:heroshot|thumb)" href="([^"]+)"[^>]*data-cap="([^"]*)"[^>]*>\s*<img ([^>]*)>', s):
        if a.group(1) not in [o[0] for o in out]: out.append((a.group(1), unesc(attr(a.group(3), 'alt')), unesc(a.group(2))))
    return out

def gallery_html(shots):
    s0 = shots[0]; e = lambda x: html.escape(x, quote=True)
    cur = ' aria-current="true"'
    thumbs = ''.join(f'        <button type="button" data-src="{e(src)}" data-cap="{e(cap)}" aria-label="Show: {e(cap)}"{cur if k == 0 else ""}><img src="{e(src)}" alt="{e(alt)}" loading="lazy"></button>\n' for k, (src, alt, cap) in enumerate(shots))
    return f'''  <section class="wrap gal" id="gal" aria-label="Screenshots">
    <div class="gal-stage">
      <img id="galImg" src="{e(s0[0])}" alt="{e(s0[1])}">
      <button type="button" class="gal-btn gal-on gal-prev" id="galPrev" aria-label="Previous screenshot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button type="button" class="gal-btn gal-on gal-next" id="galNext" aria-label="Next screenshot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
    </div>
    <p class="gal-cap" id="galCap">{e(s0[2])}  ·  1 of {len(shots)}</p>
    <div class="gal-strip">
{thumbs}    </div>
    <dialog class="gal-lb" id="galLb" aria-label="Screenshot, full size">
      <div class="gal-lb-in">
        <img id="lbImg" src="" alt="" draggable="false">
        <p class="gal-lb-cap" id="lbCap"></p>
      </div>
      <button type="button" class="gal-btn gal-prev" id="lbPrev" aria-label="Previous screenshot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button type="button" class="gal-btn gal-next" id="lbNext" aria-label="Next screenshot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
      <button type="button" class="gal-btn gal-close" id="lbClose" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <div class="gal-zoom" role="group" aria-label="Zoom">
        <button type="button" id="lbOut" aria-label="Zoom out">−</button>
        <span id="lbZoom" aria-live="polite">100%</span>
        <button type="button" id="lbIn" aria-label="Zoom in">+</button>
        <button type="button" id="lbFit" aria-label="Fit to screen">Fit</button>
      </div>
    </dialog>
  </section>
'''

def build(path):
    s = open(path).read(); shots = shots_of(s); assert shots, path
    s = re.sub(r'<nav class="hub wrap"[^\n]*</nav>', HUB_NAV, s)
    # drop the old pieces: hero block, screenshots section, lightbox, and their CSS
    if 'id="gal"' in s:
        a = s.index('  <section class="wrap gal" id="gal"'); b = s.index('</section>\n', a) + len('</section>\n'); s = s[:a] + '@@GAL@@' + s[b:]
    else:
        h = s.index('class="heroshot"'); a = s.rindex('  <div class="wrap">', 0, h); b = s.index('  </div>\n', h) + len('  </div>\n'); s = s[:a] + '@@GAL@@' + s[b:]
        g = s.index('<div class="gallery">'); a = s.rindex('  <section', 0, g); b = s.index('</section>\n', g) + len('</section>\n'); s = s[:a] + s[b:]
    s = re.sub(r'<dialog class="lb".*?</dialog>\s*<script>.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<script>\n\(\(\) => \{   // the screenshot gallery.*?</script>\n', '', s, flags=re.S)
    for pat in [r'\n/\* screenshots: thumbnails open a lightbox.*?(?=\n[.a-z@]*hub|</style>)', r'\n/\* screenshots: one big picture.*?(?=</style>)',
                r'\n\.heroshot\{[^\n]*', r'\n\.heroshot img\{[^\n]*', r'\n\.heroshot:focus-visible[^\n]*', r'\n\.gallery\{[^\n]*', r'\n@media \(max-width:700px\)\{\.gallery[^\n]*',
                r'\n\.thumb[^\n]*', r'\n@media \(prefers-reduced-motion:reduce\)\{\.thumb[^\n]*', r'\ndialog\.lb[^\n]*', r'\n\.lb-[^\n]*', r'\n@media \(max-width:600px\)\{\.lb-[^\n]*']:
        s = re.sub(pat, '', s, flags=re.S)
    s = s.replace('@@GAL@@', gallery_html(shots)).replace('</style>', CSS + '</style>', 1).replace('</body>', JS + '</body>', 1)
    open(path, 'w').write(s); return len(shots)

if __name__ == '__main__':
    for p in sys.argv[1:] or [f'{H}/TVApp/docs/index.html', f'{H}/darkshed/docs/index.html', f'{H}/ChopPad-app/docs/index.html']: print(p, build(p))
