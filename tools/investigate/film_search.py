#!/usr/bin/env python3
"""film_search.py — stage 1 of the original-film library: yt-dlp flat searches for Coach Carter (2005)
film content. Writes every hit (id/title/channel/channel_id) to tracking/investigation/film/search_hits.json.
Stage 2 (film_clips.py) pulls full metadata per candidate and filters to official channels."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tracking/investigation/film/search_hits.json"
QUERIES = [
 "Coach Carter Movieclips", "Coach Carter (2005) Movie CLIP", "Coach Carter Movie CLIP HD",
 "Coach Carter scene Movieclips", "Coach Carter 2005 official trailer", "Coach Carter trailer Paramount",
 "Coach Carter Paramount Movies", "Coach Carter Paramount Pictures", "Coach Carter Paramount Plus",
 "Coach Carter MTV", "Coach Carter our deepest fear scene", "Coach Carter lockout scene",
 "Coach Carter push ups scene", "Coach Carter contract scene", "Coach Carter Timo Cruz",
 "Coach Carter final game St. Francis", "Coach Carter Samuel L Jackson scene", "Coach Carter first practice",
 "Coach Carter Movieclips Classic Trailers", "Coach Carter Paramount Vault", "Coach Carter 2005 clip",
 "Coach Carter scene", "Coach Carter Sir yes sir", "Coach Carter gym locked scene",
 "Coach Carter Fandango", "Coach Carter Rotten Tomatoes", "Coach Carter Channing Tatum scene",
]
def search(q, n=50):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch{n}:{q}"], capture_output=True, text=True, timeout=300)
    if r.returncode: print("fail", q, r.stderr[-300:], file=sys.stderr); return []
    return json.loads(r.stdout).get("entries", [])
hits = {}
for q in QUERIES:
    for e in search(q):
        vid = e.get("id")
        if not vid: continue
        h = hits.setdefault(vid, {"id": vid, "title": e.get("title"), "channel": e.get("channel") or e.get("uploader"),
                                  "channel_id": e.get("channel_id"), "view_count": e.get("view_count"),
                                  "duration": e.get("duration"), "queries": []})
        h["queries"].append(q)
    print(q, len(hits), file=sys.stderr)
OUT.write_text(json.dumps(list(hits.values()), indent=1))
print(len(hits), "->", OUT, file=sys.stderr)
