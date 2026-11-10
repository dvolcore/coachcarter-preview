"""Merge tracking/coach_extract/part*.json into site/assets/data/coach.json (grouped into parts)."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
X = R / "tracking/coach_extract"
PARTS = [
    ("part0", "Start here", "Decisions, status and the honest numbers"),
    ("part3", "The plan", "The one-page summary, the first 90 days, the $60K test, the team and the money"),
    ("part1", "The opportunity", "Demand, audience, buyers, revivals, the franchise and every offer on the menu"),
    ("part2", "Story and scenarios", "The documentary, people to study, costs, operating scenarios, the big targets, AI and lost opportunities"),
    ("part4", "Collection, contract and evidence", "Academy fashion, the original contract, the Seven Sisters, offers to test and how sure we are"),
]
out = {"parts": []}
for key, title, sub in PARTS:
    f = X / f"{key}.json"
    if not f.exists():
        print("MISSING", f); continue
    secs = json.loads(f.read_text())["sections"]
    if key == "part3":  # summary first
        secs.sort(key=lambda s: 0 if "summary" in s.get("chapter", "").lower() else 1)
    out["parts"].append({"title": title, "sub": sub, "sections": secs})
(R / "site/assets/data/coach.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("parts", len(out["parts"]), "sections", sum(len(p["sections"]) for p in out["parts"]))
