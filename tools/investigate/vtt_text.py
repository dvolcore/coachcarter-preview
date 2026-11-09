"""Flatten a YouTube .vtt (manual or auto) to deduped '[mm:ss] text' lines. Usage: vtt_text.py file.vtt [every_s]"""
import re, sys

def parse(path):
    out, seen = [], set()
    t = None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", line) or re.match(r"(\d+):(\d+)\.\d+ -->", line)
        if m:
            g = [int(x) for x in m.groups()]
            t = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or t is None:
            continue
        txt = re.sub(r"<[^>]+>", "", line).strip()
        if txt and txt not in seen:
            seen.add(txt)
            out.append((t, txt))
    return out

if __name__ == "__main__":
    every = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    last = -999
    buf = []
    for t, txt in parse(sys.argv[1]):
        if every and t - last < every:
            buf.append(txt); continue
        if buf:
            print(" ".join(buf))
        buf = [f"[{t // 60:02d}:{t % 60:02d}] {txt}"]; last = t
    if buf:
        print(" ".join(buf))
