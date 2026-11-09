"""Wide film stills + muted ambient loops for the site (site/assets/film/s, site/assets/film/l).

Stills: exact frame -> crop to picture (Boxoffice 4K: extra top crop removes the channel bug) -> webp 2400w/1200w.
Loops: 6-8 s, muted, 1280w H.264 + poster.  Run: python3 tools/film_stills.py [stills|loops]
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
RAW = R / "tracking/film_media/raw"
OUT = R / "site/assets/film"
BOX = [3840, 1548, 0, 336]          # Boxoffice 4K picture minus logo strip
CROP = {
    "cmWstLTOqiQ": BOX, "dfGYZMXUvnQ": BOX, "sHgTSEhsRjQ": BOX, "ITuhV9Tw_bY": BOX, "kLENW1JSjqk": BOX,
    "8WJ2C1s1ee8": BOX, "K2-D4iIZ5ss": BOX, "JFvtFgFv0Qw": BOX, "JiRsPPqbIpk": BOX,
    "iCc9rFHuzlI": [1920, 800, 0, 140], "jdrcX9zjS80": [1920, 804, 0, 138], "WuSCEbZF4i4": [1920, 800, 0, 140],
}

# key, source, time (s), alt text, scene slug to play, start time in that scene's web file
STILLS = [
    ("team-lineup",     "cmWstLTOqiQ", 24.539,  "The Richmond players line up in the old gym as Coach Carter walks in", "first-practice", 20),
    ("contracts",       "cmWstLTOqiQ", 49.079,  "The players react as Carter hands out the contracts", "first-practice", 95),
    ("carter-gym",      "cmWstLTOqiQ", 282.202, "Carter in the Richmond gym on day one", "first-practice", 270),
    ("carter-cruz",     "cmWstLTOqiQ", 225.0, "Carter faces Timo Cruz on the first day", "first-practice", 228),
    ("stairs",          "dfGYZMXUvnQ", 89.5,  "Carter at the foot of the gym stairs as Cruz comes back", "pushups", 0),
    ("pushups",         "dfGYZMXUvnQ", 112.5, "The whole team runs suicides and push-ups for Cruz", "pushups", 50),
    ("chain",           "sHgTSEhsRjQ", 47.674,  "Carter holds the chain cut from the gym doors", "deepest-fear", 0),
    ("desks",           "sHgTSEhsRjQ", 68.5,  "The team studying at desks on the gym floor", "deepest-fear", 10),
    ("desks-wide",      "sHgTSEhsRjQ", 170.5, "Light through the gym windows over the players' desks", "deepest-fear", 100),
    ("board-room",      "iCc9rFHuzlI", 24.286,  "Coach Carter before the packed school board", "board-hearing", 9),
    ("board-speech",    "iCc9rFHuzlI", 170.005, "Coach Carter addresses the board", "board-hearing", 150),
    ("street-night",    "jdrcX9zjS80", 130.829, "Richmond streets at night", "renny", 120),
    ("bayhill-arena",   "ITuhV9Tw_bY", 119.904, "The Bay Hill tournament, packed stands", "bay-hill", 40),
    ("bayhill-joy",     "ITuhV9Tw_bY", 314.749, "Carter celebrates the Bay Hill championship", "bay-hill", 120),
    ("stfrancis-crowd", "kLENW1JSjqk", 391.223, "Carter and Kenyon on the sideline at St. Francis", "final-shot", 10),
    ("dream-team",      "kLENW1JSjqk", 576.540, "Carter with his team in the locker room", "storybook-ending", 0),
    ("locker-team",     "8WJ2C1s1ee8", 51.0,  "The team in the locker room after St. Francis", "storybook-ending", 30),
    ("locker-carter",   "8WJ2C1s1ee8", 79.780,  "Carter in the locker room after the last game", "storybook-ending", 64),
    ("homecoming",      "8WJ2C1s1ee8", 127.758, "Richmond's gym packed for the team's return", "storybook-ending", 110),
    ("store",           "WuSCEbZF4i4", 42.796,  "Junior Battle's mother comes to see Carter", "juniors-mother", 30),
]

# key, source, start, seconds
LOOPS = [
    ("desks",    "sHgTSEhsRjQ", 64.0, 8),
    ("practice", "dfGYZMXUvnQ", 104.5, 7),
    ("crowd",    "kLENW1JSjqk", 327.0, 7),
    ("carter",   "cmWstLTOqiQ", 278.0, 8),
]


def raw(v):
    return next(p for p in RAW.glob(f"{v}.*") if p.suffix in (".mkv", ".mp4", ".webm"))


def stills():
    (OUT / "s").mkdir(parents=True, exist_ok=True)
    meta = []
    for key, v, t, alt, scene, ts in STILLS:
        cw, ch, cx, cy = CROP[v]
        for w in (2400, 1200):
            ww = min(w, cw)
            dst = OUT / "s" / f"{key}-{w}.webp"
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t}", "-i", str(raw(v)), "-frames:v", "1",
                            "-vf", f"crop={cw}:{ch}:{cx}:{cy},scale={ww}:-2:flags=lanczos", "-c:v", "libwebp", "-quality", "82", str(dst)], check=True)
        meta.append({"key": key, "alt": alt, "scene": scene, "t": ts, "aspect": round(cw / ch, 3),
                     "src": f"assets/film/s/{key}-2400.webp", "src_sm": f"assets/film/s/{key}-1200.webp", "from": v, "at": t})
        print(key, flush=True)
    (OUT / "stills.json").write_text(json.dumps(meta, indent=1))


def loops():
    (OUT / "l").mkdir(parents=True, exist_ok=True)
    for key, v, t, d in LOOPS:
        cw, ch, cx, cy = CROP[v]
        mp4 = OUT / "l" / f"{key}.mp4"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t}", "-t", f"{d}", "-i", str(raw(v)), "-an",
                        "-vf", f"crop={cw}:{ch}:{cx}:{cy},scale=1600:-2:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
                        "-crf", "27", "-profile:v", "high", "-movflags", "+faststart", str(mp4)], check=True)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(mp4), "-frames:v", "1", "-c:v", "libwebp", "-quality", "75",
                        str(OUT / "l" / f"{key}.webp")], check=True)
        print(key, round(mp4.stat().st_size / 1e6, 2), "MB", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("stills", "all"):
        stills()
    if what in ("loops", "all"):
        loops()
