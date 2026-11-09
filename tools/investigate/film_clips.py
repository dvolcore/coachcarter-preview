#!/usr/bin/env python3
"""film_clips.py — stage 2: full yt-dlp metadata (no download) for official Coach Carter (2005) uploads,
plus YouTube thumbnail resolution checks (maxres/sd/hq) by HTTP status + real pixel size.
Official channel allow-list = channel_id, not name (names can be spoofed).
Output: tracking/investigation/film/clips_meta.json"""
import json, subprocess, sys, struct, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tracking/investigation/film/clips_meta.json"
OFFICIAL = {
    "UC3gNmTGu-TTbFPpfSs5kNkg": "Movieclips (Fandango, official licensed clips)",
    "UCTCjFFoX1un-j7ni4B6HJ3Q": "Rotten Tomatoes Classic Trailers (Fandango; formerly Movieclips Classic Trailers)",
    "UCF9imwPMSGz4Vq1NiTWCC7g": "Paramount Pictures",
    "UC9YHyj7QSkkSg2pjQ7M8Khg": "Paramount Movies",
    "UCrRttZIypNTA1Mrfwo745Sg": "Paramount Plus",
    "UCxAICW_LdkfFYwTqTHHE0vg": "MTV",
}
IDS = sys.argv[1:] or """V1wAemvxNaM qUiptlAJcyQ 1g82D68N-ys JomrLxDiT5g 2FKPDOpKzDo 2_fDhqRk_Ro J97F53CAA1I
fnH1ZtugoqU eSBnFu1YnrU d_GleoanbPE a6Zpa4rtpkA""".split()
KEEP = ["id", "title", "channel", "channel_id", "uploader_id", "channel_is_verified", "upload_date", "duration",
        "duration_string", "view_count", "like_count", "age_limit", "playable_in_embed", "availability",
        "is_live", "description", "width", "height", "aspect_ratio", "categories", "tags", "webpage_url"]

def img_size(url):
    """Return (status, w, h) for a JPEG/WebP thumbnail without saving it."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
            data = r.read(); st = r.status
    except urllib.error.HTTPError as e:
        return e.code, None, None
    i = 2
    while i < len(data) - 9:  # JPEG SOF scan
        if data[i] != 0xFF: i += 1; continue
        m = data[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9]); return st, w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return st, None, None

out = []
for vid in IDS:
    r = subprocess.run(["yt-dlp", "--dump-json", "--skip-download", "--no-warnings", f"https://www.youtube.com/watch?v={vid}"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode:
        out.append({"id": vid, "error": r.stderr.strip()[-400:]}); print("FAIL", vid, r.stderr[-200:], file=sys.stderr); continue
    d = json.loads(r.stdout)
    rec = {k: d.get(k) for k in KEEP}
    rec["official_channel"] = OFFICIAL.get(d.get("channel_id"))
    thumbs = {}
    for name in ("maxresdefault", "sddefault", "hqdefault"):
        u = f"https://i.ytimg.com/vi/{vid}/{name}.jpg"
        st, w, h = img_size(u)
        thumbs[name] = {"url": u, "status": st, "w": w, "h": h}
    rec["thumbs"] = thumbs
    out.append(rec)
    print(vid, rec["channel"], rec["upload_date"], rec["duration"], rec["view_count"], "embed=", rec["playable_in_embed"],
          "age=", rec["age_limit"], {k: (v["status"], v["w"], v["h"]) for k, v in thumbs.items()}, file=sys.stderr)
OUT.write_text(json.dumps(out, indent=1))
print(len(out), "->", OUT, file=sys.stderr)
