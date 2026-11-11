"""Film media pipeline: raw downloads (tracking/film_media/raw/*.mkv) -> web playback files.

  python3 tools/film_media.py crop            # detect letterbox crop per source, write crops.json
  python3 tools/film_media.py sheet ID        # 4x4 contact sheet of one source (for picking trims/stills)
  python3 tools/film_media.py encode [SLUG]   # encode playback mp4 + poster for every clip (or one)

Output: tracking/film_media/out/v/<slug>.mp4 (720p-wide H.264, crop to picture, faststart) and
        tracking/film_media/out/p/<slug>.jpg (poster). The out/ folder is what gets pushed to the media repo.
"""
import json, re, subprocess, sys
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent.parent
RAW = R / "tracking/film_media/raw"
OUT = R / "tracking/film_media/out"
CROPS = R / "tracking/film_media/crops.json"

# slug, source id, trim start (s), trim end (s or None = to end), poster time (s, relative to trimmed clip)
CLIPS = [
    ("trailer",          "d_GleoanbPE", 0, None, 20),
    ("first-practice",   "cmWstLTOqiQ", 0, 289.4, 238),
    ("parents-contract", "fidQ2FQKGtQ", 0, None, 30),
    ("first-win",        "qUiptlAJcyQ", 0, None, 60),
    ("pushups",          "1g82D68N-ys", 0, None, 50),
    ("vision",           "5Th5LyAVDRM", 0, None, 45),
    ("bay-hill",         "JomrLxDiT5g", 0, None, 60),
    ("pool-party",       "JFvtFgFv0Qw", 0, 237.4, 110),
    ("lockout",          "lipT9ry5h3A", 410, None, 45),
    ("better-life",      "2FKPDOpKzDo", 0, None, 60),
    ("juniors-mother",   "WuSCEbZF4i4", 0, 198.4, 60),
    ("renny",            "jdrcX9zjS80", 0, None, 120),
    ("board-hearing",    "iCc9rFHuzlI", 15, 283, 150),
    ("deepest-fear",     "2_fDhqRk_Ro", 0, None, 45),
    ("pep-talk",         "J97F53CAA1I", 0, None, 40),
    ("final-shot",       "fnH1ZtugoqU", 0, None, 80),
    ("storybook-ending", "eSBnFu1YnrU", 0, None, 64),
    ("real-carter-1",    "n8beCoP9lc8", 0, None, 20),
    ("real-carter-2",    "yzvd3xf6CTE", 0, None, 10),
]


def src(vid):
    hits = sorted(RAW.glob(f"{vid}.*"))
    hits = [h for h in hits if h.suffix in (".mkv", ".mp4", ".webm")]
    if not hits:
        raise SystemExit(f"missing raw for {vid}")
    return hits[0]


def probe(path):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return int(v["width"]), int(v["height"]), float(j["format"]["duration"])


def detect_crop(path):
    w, h, dur = probe(path)
    votes = Counter()
    for frac in (0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88):
        out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{dur * frac:.1f}", "-i", str(path), "-vf", "cropdetect=limit=24:round=2:reset=0",
                              "-frames:v", "40", "-f", "null", "-"], capture_output=True, text=True).stderr
        found = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", out)
        if found:
            votes[found[-1]] += 1
    cw, ch, cx, cy = map(int, votes.most_common(1)[0][0]) if votes else (w, h, 0, 0)
    # keep full width when the detector shaves a few px off the sides
    if cw > w * 0.96:
        cw, cx = w, 0
    if ch > h * 0.96:
        ch, cy = h, 0
    return {"w": w, "h": h, "dur": round(dur, 2), "crop": [cw, ch, cx, cy], "aspect": round(cw / ch, 3)}


def cmd_crop():
    crops = json.loads(CROPS.read_text()) if CROPS.exists() else {}
    for slug, vid, *_ in CLIPS:
        crops[vid] = detect_crop(src(vid))
        print(slug, vid, crops[vid])
    CROPS.write_text(json.dumps(crops, indent=1))


def cmd_sheet(vid, start=0, end=None):
    p = src(vid)
    _, _, dur = probe(p)
    end = end or dur
    step = max(1, (end - start) / 16)
    sheet = R / f"tracking/film_media/sheets/{vid}.jpg"
    sheet.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(start), "-t", str(end - start), "-i", str(p),
                    "-vf", f"fps=1/{step:.2f},scale=480:-2,tile=4x4:padding=4", "-frames:v", "1", "-q:v", "4", str(sheet)], check=True)
    print(sheet)


def cmd_encode(only=None):
    crops = json.loads(CROPS.read_text())
    (OUT / "v").mkdir(parents=True, exist_ok=True)
    (OUT / "p").mkdir(parents=True, exist_ok=True)
    report = {}
    for slug, vid, t0, t1, tp in CLIPS:
        if only and slug not in only.split(","):
            continue
        p = src(vid)
        cw, ch, cx, cy = crops[vid]["crop"]
        vf = f"crop={cw}:{ch}:{cx}:{cy},scale=1280:-2:flags=lanczos,format=yuv420p"
        trim = ["-ss", str(t0)] + (["-to", str(t1)] if t1 else [])
        mp4 = OUT / "v" / f"{slug}.mp4"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *trim, "-i", str(p), "-vf", vf,
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "1700k", "-bufsize", "3400k", "-profile:v", "high",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "112k", "-ac", "2", "-ar", "48000", "-movflags", "+faststart", str(mp4)], check=True)
        jpg = OUT / "p" / f"{slug}.jpg"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(tp), "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(jpg)], check=True)
        w, h, dur = probe(mp4)
        report[slug] = {"id": vid, "w": w, "h": h, "dur": round(dur, 1), "mb": round(mp4.stat().st_size / 1e6, 1), "t0": t0}
        print(slug, report[slug], flush=True)
    rp = OUT / "encode_report.json"
    old = json.loads(rp.read_text()) if rp.exists() else {}
    old.update(report)
    rp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "crop":
        cmd_crop()
    elif a[0] == "sheet":
        cmd_sheet(a[1], *(float(x) for x in a[2:]))
    elif a[0] == "encode":
        cmd_encode(a[1] if len(a) > 1 else None)
