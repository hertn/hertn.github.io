"""Fetch the latest YouTube videos for the hub page into latest.json.

Runs from .github/workflows/latest.yml (YouTube's feeds can't be read from the browser).
To change which channels show, edit CHANNELS below. Order here = order on the page.
"""
import json, os, re, urllib.request, xml.etree.ElementTree as ET

CHANNELS = [
    "UC5LZwv59YVBltntRdi39cJw",  # HertWasHere (tech)
    "UCz5g7GTpBsuc0nuegjrj8hg",  # Hert Niks (OG)
]
PER_CHANNEL = 4  # full videos only, Shorts are skipped
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}
OUT = os.path.join(os.path.dirname(__file__), "..", "latest.json")
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def channel(cid):
    root = ET.fromstring(get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"))
    videos = []
    for e in root.findall("a:entry", NS):
        link = e.find("a:link", NS).get("href")
        if "/shorts/" in link:
            continue
        stats = e.find("media:group/media:community/media:statistics", NS)
        videos.append({"id": e.findtext("yt:videoId", namespaces=NS), "title": e.findtext("a:title", namespaces=NS),
                       "published": e.findtext("a:published", namespaces=NS), "url": link,
                       "views": int(stats.get("views", 0)) if stats is not None else None})
        if len(videos) == PER_CHANNEL:
            break
    info = {"name": root.findtext("a:title", namespaces=NS), "id": cid,
            "url": f"https://www.youtube.com/channel/{cid}", "videos": videos}
    try:  # channel picture, @handle and subscriber count come from the channel page
        page = get(info["url"]).decode("utf-8", "replace")
        if m := re.search(r'<meta property="og:image" content="([^"]+)"', page): info["avatar"] = m.group(1)
        if m := re.search(r'"canonicalBaseUrl":"/(@[^"]+)"', page): info["handle"] = m.group(1)
        if m := re.search(r'([\d.,]+[KM]?) subscribers', page): info["subscribers"] = m.group(1)
    except Exception as err:
        print(f"{cid} page: {err}")
    return info


old = {}
try:
    old = {c.get("id"): c for c in json.load(open(OUT)).get("youtube", [])}
except (OSError, ValueError):
    pass
data = {"youtube": []}
for cid in CHANNELS:
    try:
        data["youtube"].append(channel(cid))
    except Exception as err:  # keep the last good copy of a channel if YouTube hiccups
        print(f"{cid}: {err}")
        if cid in old:
            data["youtube"].append(old[cid])
assert data["youtube"], "no channel could be read"
json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
print("wrote", sum(len(c["videos"]) for c in data["youtube"]), "videos")
