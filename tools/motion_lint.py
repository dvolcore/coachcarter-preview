"""Fail if a class used inside a motion plate is also styled by a bare global rule elsewhere on the site.
(Found the hard way: .o1, .curtain, .card and .play all had older site rules that reached into plates.)
Run: python3 tools/motion_lint.py"""
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import motion
import motion_pages  # noqa: F401  (registers the page scenes)

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {".sr", ".sr:focus"}
html = "".join(motion.SCENES.values()) + motion.plate("x", "seal", "01", ["A", "B"], "b", [("a", "#a")], "L")
mine = {c for m in re.findall(r'class="([^"]+)"', html) for c in m.split()}
hits = {}
for f in glob.glob(str(ROOT / "site/assets/css/*.css")):
    if f.endswith(("motion.css", "shell.css")):
        continue
    css = re.sub(r"/\*.*?\*/", "", Path(f).read_text(), flags=re.S)
    for sel_block, _ in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        for sel in sel_block.split(","):
            sel = sel.strip()
            if not sel or sel.startswith("@") or sel in ALLOWED:
                continue
            comps = re.split(r"\s*[>+~ ]\s*", sel)
            if all((m := re.fullmatch(r"\.([A-Za-z0-9_-]+)(::?[a-z-]+(\([^)]*\))?)*", c)) and m.group(1) in mine for c in comps):
                hits.setdefault(sel, set()).add(Path(f).name)
for sel, files in sorted(hits.items()):
    print("CLASH", sel, "in", ", ".join(sorted(files)))
print(f"motion_lint: {len(mine)} plate classes checked, {len(hits)} clashes")
sys.exit(1 if hits else 0)
