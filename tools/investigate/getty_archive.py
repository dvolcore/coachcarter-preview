"""Build site/assets/data/getty_all.json: every embeddable Getty photo of Coach Ken Carter,
with caption, photographer, embed token and a chapter. Re-run any time; IDs come from
the Getty 'coach-ken-carter' listing (scraped in a browser session)."""
import json
import re
import time
import urllib.request
from pathlib import Path

IDS = """51962460,51962462,51962463,51962464,51962465,51962467,51962473,51962763,51962765,51962845,51962885,51962893,79508039,104862816,105381434,105393720,105411240,105593871,105593879,106848387,107285579,110239084,110239085,112420039,115144906,117806643,117806665,117806761,117806822,117806974,117807404,117807545,117807652,117807664,117807800,117807881,117807890,117807906,117808488,117808648,117808979,117809112,117809260,117809386,117809466,117809489,117809540,118035771,118036057,118036746,118036748,118036839,118036888,118036980,118037018,118037716,118037718,118038473,118038474,118038629,118040381,118040756,118040807,118040847,118041241,118041346,118041347,490354604,490354622,490354624,490354626,490356552,524771034,1556010530,1556011111,1556011113,1556011115,1556011116,1556011119,1556012150,1556012151,1556012152,1556012153,1556012154,1556012673,1556012675,1556012676,1556012677,1556012678,1556012684,1556013198,1556032239,1556032244,1556032782,1556032807,1556032817,1556032970,1556033010,1556033357,1556033394,1556033404,1556033405,1556033409,1561588922,1561593138,1561642084,1561642086,1577644499,1581420971,1581501890,1581508794,1581519657,1581519658,1581519660,1581523881,1581549973,1581561726,1581573399,1581619731,1582372540""".split(",")

# Wire photos (embedding disabled) — listed with links only
LINK_ONLY = "2226407600,2226407602,2226407604,2226407605,2226407609,2226407627,2226407629,2226407632,2226407637,2226407644,2226407665,2226407668,2226407669,2226407672,2226407674".split(",")

FEATURED = {"51962763", "51962765", "51962845", "112420039", "110239085", "110239084", "51962463", "51962473",
            "51962893", "51962885", "117809386", "117809466", "118037718", "115144906", "104862816", "490354626",
            "490356552", "1561588922", "1581561726", "1556033357"}


def chapter(cap, title):
    t = (cap + " " + title).lower()
    if "dr. phil" in t or "dr phil" in t:
        return "tv", "Dr. Phil"
    if "afterparty" in t or "after-party" in t:
        return "premiere", "Premiere celebration"
    if "chinese thea" in t or "los angeles premiere" in t:
        return "premiere", "Hollywood premiere"
    if "channing tatum" in t or "antwon tanner" in t:
        return "cast", "The team that played his team"
    if "palm springs" in t:
        return "festival", "Palm Springs Int'l Film Festival"
    if "life is beautiful" in t:
        return "stage", "Life Is Beautiful"
    if "slamball" in t or "rumble" in t:
        return "slamball", "SlamBall · the Rumble"
    if "net gain" in t or "gault" in t:
        return "courts", "Celebrity & benefit games"
    return "portraits", "Portraits"


def clean(cap):
    cap = re.sub(r"^[A-Z ,.\-]+\d{1,2}:\s*", "", cap or "").strip()  # drop "LOS ANGELES - JANUARY 13:"
    cap = re.sub(r"\s*\(Photo by[^)]*\)\s*$", "", cap)
    cap = re.sub(r"\*+\s*Exclusive\s*\*+|\*+", "", cap).strip()
    return cap


out = []
for gid in IDS:
    req = urllib.request.Request(f"https://embed.gettyimages.com/oembed?url=https://gty.im/{gid}", headers={"User-Agent": "Mozilla/5.0"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:  # noqa: BLE001
        print("FAIL", gid, e)
        continue
    html = d["html"]
    key, label = chapter(d.get("caption", ""), d.get("title", ""))
    out.append({
        "id": gid, "chapter": key, "chapter_label": label, "featured": gid in FEATURED,
        "title": d.get("title", ""), "caption": clean(d.get("caption", "")),
        "photographer": d.get("photographer", ""), "collection": d.get("collection", ""),
        "w": d.get("width"), "h": d.get("height"),
        "et": re.search(r"id:'([^']+)'", html).group(1), "sig": re.search(r"sig:'([^']+)'", html).group(1),
        "thumb": d.get("thumbnail_url", ""),
    })
    time.sleep(0.15)

root = Path(__file__).resolve().parents[2]
(root / "site/assets/data/getty_all.json").write_text(json.dumps({"photos": out, "link_only": LINK_ONLY}, indent=0))
from collections import Counter
print(len(out), Counter(o["chapter"] for o in out))
