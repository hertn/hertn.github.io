#!/usr/bin/env python3
"""Write the index.html landing pages into each Stremio list repo (served at the Pages root)."""
import html, json, os, sys

ROOT = os.path.expanduser('~')
LISTS = [
  dict(repo='christmas-movie-list', h1="Hert's Xmas List", kw='Christmas movies for Stremio',
       title="Christmas Movies for Stremio: Hert's Xmas List",
       desc='A hand-picked list of the best Christmas movies for Stremio, sorted by mood: family classics, golden age, cozy, comedy, musicals and animated.',
       lede='A hand-picked <strong>Christmas movie list for Stremio</strong>, sorted by mood. From Home Alone and Elf to the golden-age classics, ready to browse on your TV, phone or computer.',
       c1='#34c759', c2='#14672f', short='Xmas List'),
  dict(repo='halloween-movie-list', h1="Hert's Halloween List", kw='Halloween and horror movies for Stremio',
       title="Halloween Horror Movies for Stremio: Hert's Halloween List",
       desc='A hand-picked list of 162 Halloween movies for Stremio: classic horror, slashers, thrillers, monsters, horror comedy and family frights, 2006 and earlier.',
       lede='A hand-picked <strong>Halloween and horror movie list for Stremio</strong>: Hitchcock, slashers, the supernatural, monsters and zombies, horror comedy and family-friendly spooky films. Everything from 2006 and earlier.',
       c1='#ff9f43', c2='#c2410c', short='Halloween List'),
  dict(repo='childhood-movie-list', h1="Hert's Childhood List", kw='80s and 90s childhood movies for Stremio',
       title="80s and 90s Kids Movies for Stremio: Hert's Childhood List",
       desc='A hand-picked list of 80s and 90s childhood movies for Stremio: Disney classics and the Disney Renaissance, animated films, adventure, magic and comedy.',
       lede='A hand-picked <strong>80s and 90s childhood movie list for Stremio</strong>, sorted by mood: Disney classics, the Disney Renaissance, animation, adventure, magic, comedy and musicals.',
       c1='#ffb340', c2='#c94a17', short='Childhood List'),
  dict(repo='uk-comedy-game-shows', h1='UK Comedy &amp; Game Shows', kw='UK panel shows and game shows for Stremio',
       title='UK Comedy Panel Shows and Game Shows for Stremio',
       desc='Every UK comedy panel show, game show, quiz, chat show and stand-up showcase in one Stremio list. Taskmaster, QI, Would I Lie to You and more.',
       lede='Every <strong>UK comedy panel show, game show and quiz</strong> in one Stremio list, plus chat shows and stand-up showcases. No scripted comedy, no reality TV.',
       c1='#ff5e9c', c2='#6d3fe0', short='UK Comedy &amp; Game Shows'),
  dict(repo='uk-tv-list', h1="Hert's UK TV", kw='UK TV shows for Stremio',
       title="UK TV for Stremio: BBC iPlayer, ITVX, Channel 4, U&amp;Dave",
       desc='UK-made shows streaming now on BBC iPlayer, ITVX, Channel 4 and U&Dave, as a Stremio addon. Sorted by genre, newest episodes first, updated every week.',
       lede='<strong>UK-made TV shows</strong> streaming right now on <strong>BBC iPlayer, ITVX, Channel 4 and U&amp;Dave</strong>, as Stremio catalogs. Sorted by genre, newest episodes first, and updated every week.',
       c1='#3b6fe0', c2='#c8283c', short='UK TV'),
]

def esc(x): return html.escape(str(x), quote=True)

def tiles(metas):
    return ''.join(f'<li><a href="https://web.stremio.com/#/detail/{esc(m["type"])}/{esc(m["id"])}"><img src="{esc(m.get("poster",""))}" alt="" loading="lazy" width="132" height="198"><span>{esc(m["name"])} <small>{esc(m.get("releaseInfo",""))}</small></span></a></li>' for m in metas)

def snapshot(repo):
    # shortcut: snapshot is from the day this script ran; the live script refreshes it, rerun after big list edits.
    d = os.path.join(ROOT, repo); man = json.load(open(os.path.join(d, 'manifest.json')))
    out = []
    for c in man['catalogs']:
        gs = next((e['options'] for e in c.get('extra', []) if e['name'] == 'genre'), c.get('genres', []))
        many = len(man['catalogs']) > 1
        for g in gs:
            p = os.path.join(d, 'catalog', c['type'], c['id'], f'genre={g}.json')
            if not os.path.exists(p): continue
            metas = json.load(open(p))['metas']
            if not metas: continue
            if many: metas = metas[:12]
            name = f"{c['name']}: {g}" if many else g
            out.append(f'<section><h2>{esc(name)}<span class="count">{"" if many else len(metas)}</span></h2><ul class="grid">{tiles(metas)}</ul></section>')
    return ''.join(out)

TPL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'list_template.html')).read()

for L in LISTS:
    base = f"https://hertn.github.io/{L['repo']}/"
    others = ''.join(f'<li><a href="https://hertn.github.io/{o["repo"]}/">{o["short"]}</a></li>' for o in LISTS if o is not L)
    ld = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": html.unescape(L['title']), "description": L['desc'], "url": base,
        "isPartOf": {"@type": "WebSite", "name": "hertn", "url": "https://hertn.github.io/"},
        "author": {"@type": "Person", "name": "hertn", "url": "https://github.com/hertn"},
        "sameAs": [f"https://github.com/hertn/{L['repo']}"],
    }
    out = TPL
    for k, v in {**L, 'base': base, 'others': others, 'ld': json.dumps(ld, indent=1, ensure_ascii=False).replace('</', '<\\/'),
                 'desc_attr': html.escape(L['desc']), 'snapshot': snapshot(L['repo'])}.items():
        out = out.replace('{{' + k + '}}', v)
    assert '{{' not in out, L['repo']
    open(os.path.join(ROOT, L['repo'], 'index.html'), 'w').write(out)
    open(os.path.join(ROOT, L['repo'], 'sitemap.xml'), 'w').write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{base}</loc><lastmod>2026-11-14</lastmod></url>\n</urlset>\n')
    print('wrote', L['repo'])
