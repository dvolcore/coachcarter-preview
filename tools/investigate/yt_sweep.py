#!/usr/bin/env python3
"""YouTube sweep for public videos featuring the real Coach Ken Carter.

Step 1: flat ytsearch over many query variants  -> raw_search.jsonl
Step 2: heuristic relevance score                -> candidates.json
Run:  python3 yt_sweep.py [--n 40] [--out DIR]
Re-runnable; caches raw search per query in OUT/cache/.
"""
import argparse, json, os, re, subprocess, sys, hashlib
from concurrent.futures import ThreadPoolExecutor

YTDLP = "/opt/homebrew/bin/yt-dlp"
DEFAULT_OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"

QUERIES = [
    "Coach Ken Carter", "Ken Carter keynote", "Ken Carter speech", "Ken Carter motivational speaker",
    "real coach carter interview", "the real Coach Carter", "Coach Carter Richmond High 1999 news",
    "Coach Carter lockout 1999 Richmond", "Ken Carter Olympic torch", "Ken Carter torch relay 2002",
    "Ken Carter SlamBall Rumble", "Coach Carter SlamBall", "Coach Carter Impact Academy Marlin",
    "Coach Ken Carter foundation", "Ken Carter commencement", "Coach Ken Carter commencement speech",
    "Ken Carter Dr Phil", "Ken Carter Oprah", "Ken Carter Today show 1999", "Ken Carter Best Damn Sports Show",
    "Ken Carter Prince", "Coach Carter returns Richmond 2024", "Coach Ken Carter back at Richmond High",
    "Ken Carter podcast", "Coach Ken Carter podcast interview", "Ken Carter Samuel Jackson premiere",
    "Yes Ma'am No Sir Coach Carter", "Yes Ma'am No Sir Ken Carter book", "Coach Ken Carter Guatemala",
    "Coach Carter Rickey Smiley", "Coach Ken Carter school assembly", "Coach Ken Carter students",
    "Coach Ken Carter documentary", "Ken Carter Richmond Oilers", "Coach Ken Carter 2025",
    "Coach Ken Carter TEDx", "Coach Ken Carter church", "Coach Carter real life story interview",
    "Ken Carter Coach Carter radio interview", "Coach Ken Carter basketball camp",
    "Coach Ken Carter visits", "Coach Ken Carter speaks to students", "Coach Ken Carter news",
    "Coach Carter Richmond High returns KTVU", "Coach Carter ABC7 Richmond", "Ken Carter Richmond High KRON",
    "Coach Carter NBC Bay Area Richmond", "Coach Ken Carter KPIX", "real Coach Carter Richmond High school 2025",
    "Coach Carter Richmond Oilers 2025 season", "Ken Carter coach interview 2005", "Coach Ken Carter radio",
    "Coach Ken Carter keynote conference", "Coach Ken Carter luncheon", "Coach Ken Carter gala",
    "Coach Ken Carter youth summit", "Coach Ken Carter rumble slamball coach", "Coach Ken Carter 2002 Olympic",
    "the real coach carter speaks", "Coach Ken Carter Real Champions League", "Coach Ken Carter library",
    "Ken Carter coach carter 60 minutes", "Ken Carter coach carter CNN", "Ken Carter coach carter ESPN",
    "Coach Carter Ken Carter Fox interview", "Coach Ken Carter Juneteenth", "Coach Ken Carter mentor",
    "Coach Ken Carter Beaumont", "Coach Ken Carter Kansas", "Coach Ken Carter Atlanta",
]

# Strong positive / negative cues
POS = [
    (r"\bken(neth)? carter\b", 3), (r"\bcoach ken\b", 3), (r"real(-| )?(life )?coach carter", 4),
    (r"therealcoachcarter", 5), (r"\brichmond\b", 2), (r"\boilers?\b", 1), (r"torch", 2),
    (r"slamball", 2), (r"impact academy|marlin", 2), (r"yes ma'?am", 3), (r"keynote|speaker|speech|speaks", 1),
    (r"interview", 1), (r"podcast", 1), (r"commencement|graduation", 1), (r"dr\.? ?phil", 2),
    (r"oprah", 1), (r"rickey smiley", 2), (r"guatemala", 2), (r"documentary", 1), (r"lockout", 2),
]
NEG = [
    (r"\bmovieclips\b", -10), (r"\b(scene|clip)\b.*\b(hd|1080p|4k)\b", -4), (r"\breaction\b", -6),
    (r"\breacts?\b", -5), (r"\btrailer\b", -3), (r"stunt", -6), (r"\bfull movie\b", -8),
    (r"\bedit\b|\bedits\b", -3), (r"tiktok compilation", -4), (r"\bfortnite|nba 2k|2k2\d\b", -6),
    (r"timo cruz|kenyon|worm|deep fear|our deepest fear", -4), (r"\bspeech scene\b", -5),
    (r"\bmeme\b", -4), (r"\bbreakdown\b|\breview\b|\bexplained\b", -2),
]
FILM_CHANNELS = re.compile(r"movieclips|paramount|movie ?clips|filmisnow|fandango|rotten tomatoes|"
                           r"scene ?(city|stealers)|cinema|movies?(\s|$)|film ?clips|zero media", re.I)


def run_search(q, n, cache_dir):
    key = hashlib.md5(f"{q}|{n}".encode()).hexdigest()[:12]
    cpath = os.path.join(cache_dir, f"{key}.jsonl")
    if os.path.exists(cpath) and os.path.getsize(cpath) > 0:
        lines = open(cpath).read().splitlines()
    else:
        p = subprocess.run([YTDLP, f"ytsearch{n}:{q}", "--flat-playlist", "--dump-json",
                            "--no-warnings", "--ignore-errors"], capture_output=True, text=True, timeout=300)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        open(cpath, "w").write("\n".join(lines))
    out = []
    for l in lines:
        try:
            d = json.loads(l)
        except Exception:
            continue
        out.append({
            "id": d.get("id"), "title": d.get("title") or "", "channel": d.get("channel") or d.get("uploader") or "",
            "channel_id": d.get("channel_id") or "", "duration": d.get("duration"), "view_count": d.get("view_count"),
            "url": f"https://www.youtube.com/watch?v={d.get('id')}", "description": (d.get("description") or "")[:500],
            "query": q,
        })
    return out


def score(item):
    text = f"{item['title']} {item['channel']} {item.get('description','')}".lower()
    s = 0
    for pat, w in POS:
        if re.search(pat, text):
            s += w
    for pat, w in NEG:
        if re.search(pat, text):
            s += w
    if "carter" not in text:
        s -= 5
    film = bool(FILM_CHANNELS.search(item["channel"] or ""))
    if film:
        s -= 6
    d = item.get("duration") or 0
    if d and d < 45:
        s -= 1  # shorts are usually fan edits
    return s, film


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    cache = os.path.join(a.out, "cache", "search")
    os.makedirs(cache, exist_ok=True)
    allhits = {}
    with ThreadPoolExecutor(6) as ex:
        for res in ex.map(lambda q: run_search(q, a.n, cache), QUERIES):
            for it in res:
                if not it["id"]:
                    continue
                if it["id"] in allhits:
                    allhits[it["id"]]["queries"].append(it["query"])
                    continue
                it["queries"] = [it.pop("query")]
                allhits[it["id"]] = it
    for it in allhits.values():
        it["score"], it["film_channel"] = score(it)
        it["score"] += min(len(it["queries"]), 5) - 1  # appears in many queries
    rows = sorted(allhits.values(), key=lambda x: -x["score"])
    with open(os.path.join(a.out, "raw_search.json"), "w") as f:
        json.dump(rows, f, indent=1)
    cands = [r for r in rows if r["score"] >= 3]
    with open(os.path.join(a.out, "candidates.json"), "w") as f:
        json.dump(cands, f, indent=1)
    print(f"queries={len(QUERIES)} unique={len(rows)} candidates(score>=3)={len(cands)}", file=sys.stderr)


if __name__ == "__main__":
    main()
