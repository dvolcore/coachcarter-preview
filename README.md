# The Real Coach Carter — platform preview

Approval preview of Coach Ken Carter's new platform (story, record, keynotes, partnerships, store, Coach Carter II, foundation, brand kit).

- `src/` — page bodies. `tools/build.py` wraps them in the shared layout and writes `site/`.
- `site/` — the deployed static site (GitHub Pages from the `gh-pages` branch; publish with `tools/deploy.sh`).
- `tools/make_logos.py` — builds the outlined SVG logo system (Cinzel + Barlow Condensed, OFL).
- `tools/encode_media.sh` — cuts the web video loops from the Coach Carter II masters.
- `tools/shoot.mjs`, `tools/elshot.mjs` — Playwright visual QA (`?qa` disables smooth scroll).

Build: `python3 tools/build.py` · Preview: `python3 -m http.server 8405 --directory site`

No footage, stills or poster art from the 2005 Paramount film is used. Video comes from the Studio405 Coach Carter II production.
