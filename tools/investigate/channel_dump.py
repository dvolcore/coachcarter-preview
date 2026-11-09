#!/usr/bin/env python3
"""Dump the full upload list (flat) of YouTube channels, then keep Carter-related rows.

Run: python3 channel_dump.py CHANNEL_URL_OR_ID [...]   (writes OUT/channels/<id>.json)
     python3 channel_dump.py --all   (uses CHANNELS below)
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

YTDLP = "/opt/homebrew/bin/yt-dlp"
OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation/channels"

CHANNELS = {
    # Coach's own / likely own
    "UCkq8ZF3PXaOsHDjgxggkrBg": "own", "UCamWLknpkAPEDfD_7RAWPYg": "own",
    "UCltQAbA_Fqeqv9DwJnyo2JA": "own?", "UCX6fvPN4NHtzPkApTEmA08Q": "own?", "UCw0RBt5CtusyoB33-PWDHmw": "own?",
    # bureaus / events / media with >=2 hits
    "UCtuSU3KtIjV0MglOms6wWEQ": "bureau", "UCWnoB1AOOGCEazP0kZWlaPw": "bureau", "UCBR0uJKc9xIz1p2DHjTyJbw": "news",
    "UC3AGqU2bx78W-B82EYTgBCw": "event", "UCxZJ7DOwRE2AQ7fwyhGlSgA": "podcast", "UCeDI5mIxi1GDmPQVZEoYOAQ": "podcast",
    "UC_x5E9llN4aw41NCWmsN0nQ": "fan", "UCj4p4EritSP1yXDj_Di3img": "podcast", "UCFI2pPNPjeH9rR2kDkeKXcw": "podcast",
}
CARTER = re.compile(r"carter|slamball|rumble|yes ma'?am", re.I)


def dump(cid):
    url = cid if cid.startswith("http") else f"https://www.youtube.com/channel/{cid}"
    rows = []
    for tab in ("/videos", "/shorts", "/streams"):
        p = subprocess.run([YTDLP, url.rstrip("/") + tab, "--flat-playlist", "--dump-json", "--no-warnings",
                            "--ignore-errors"], capture_output=True, text=True, timeout=600)
        for l in p.stdout.splitlines():
            try:
                d = json.loads(l)
            except Exception:
                continue
            rows.append({"id": d.get("id"), "title": d.get("title"), "duration": d.get("duration"),
                         "view_count": d.get("view_count"), "channel": d.get("channel") or d.get("playlist_uploader"),
                         "channel_id": d.get("channel_id") or d.get("playlist_channel_id"), "tab": tab[1:]})
    safe = re.sub(r"[^A-Za-z0-9_@-]", "_", cid)[-40:]
    json.dump(rows, open(os.path.join(OUT, f"{safe}.json"), "w"), indent=1)
    hits = [r for r in rows if CARTER.search(r.get("title") or "")]
    return cid, len(rows), hits


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    targets = list(CHANNELS) if "--all" in sys.argv else [a for a in sys.argv[1:] if not a.startswith("--")]
    with ThreadPoolExecutor(5) as ex:
        for cid, n, hits in ex.map(dump, targets):
            print(f"== {cid} [{CHANNELS.get(cid,'')}] total={n} carter_titles={len(hits)}")
            for h in hits:
                print(f"   {h['id']} {h['tab']:7} {h['duration']} {h['view_count']} | {h['title']}")
