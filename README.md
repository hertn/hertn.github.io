# hertn.github.io

The home page at [hertn.github.io](https://hertn.github.io/): links to every app and Stremio list, plus `robots.txt` and the site-wide `sitemap.xml`.

`tools/gen_lists.py` writes the landing page (`index.html` + `sitemap.xml`) of each Stremio list repo from `tools/list_template.html`. It expects the list repos cloned side by side in `~/seo-work`. Rerun it after big list changes so the built-in snapshot of titles stays close (the page also loads the live list).
