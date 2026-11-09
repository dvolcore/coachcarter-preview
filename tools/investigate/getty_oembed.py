#!/usr/bin/env python3
"""getty_oembed.py — resolve Getty Images IDs of Coach Ken Carter to caption/photographer/thumbnail
via the public Getty embed oEmbed endpoint (the free-embed path). No image downloads.

ID list = every result of Getty editorial search "\"ken carter\"" (181 results, harvested 2026-11-09
in-browser, sorted oldest) minus other people named Ken Carter (stunt driver, chef, Trump-rally
attendee, Victoria wards, El Gran Cambio producer [verified by face], Ocean City land story).

Usage: python3 getty_oembed.py [extra IDs...]   -> tracking/investigation/getty_hits.json
"""
import json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tracking/investigation/getty_hits.json"

IDS = """51962460 51962462 51962463 51962464 51962465 51962467 51962473 51962763 51962765 51962845
51962885 51962893 79508039 104862816 105381434 105393720 105411240 105593871 105593879 106848387
107285579 110239084 110239085 112420039 115144906 117806643 117806665 117806761 117806822 117806974
117807404 117807545 117807652 117807664 117807800 117807881 117807890 117807906 117808488 117808648
117808979 117809112 117809260 117809386 117809466 117809489 117809540 118035771 118036057 118036746
118036748 118036839 118036888 118036980 118037018 118037716 118037718 118038473 118038474 118038629
118040381 118040756 118040807 118040847 118041241 118041346 118041347 490354604 490354622 490354624
490354626 490356552 524771034 1501185120 1501185121 1501185125 1501185126 1501185127 1501185128
1501185142 1501185151 1501185152 1501185153 1501185156 1501185157 1501185160 1501185161 1501185164
1501185165 1501185177 1501185178 1501185179 1501185183 1501185184 1501185186 1501185187 1501185188
1556010530 1556011111 1556011113 1556011115 1556011116 1556011119 1556012150 1556012151 1556012152
1556012153 1556012154 1556012673 1556012675 1556012676 1556012677 1556012678 1556012684 1556013198
1556032239 1556032244 1556032782 1556032807 1556032817 1556032970 1556033010 1556033357 1556033394
1556033404 1556033405 1556033409 1561588922 1561593138 1561642084 1561642086 1577644499 1581420971
1581501890 1581508794 1581519657 1581519658 1581519660 1581523881 1581549973 1581561726 1581573399
1581619731 1582372540 2226407600 2226407602 2226407604 2226407605 2226407609 2226407627 2226407629
2226407632 2226407637 2226407644 2226407665 2226407668 2226407669 2226407672 2226407674""".split()


def oembed(gid):
    url = f"https://embed.gettyimages.com/oembed?url=https://gty.im/{gid}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
        return json.loads(r.read())


def main():
    ids = IDS + sys.argv[1:]
    out = []
    for gid in ids:
        try:
            d = oembed(gid)
        except Exception as e:
            print(f"fail {gid}: {e}", file=sys.stderr); out.append({"getty_id": gid, "error": str(e)}); continue
        out.append({"getty_id": gid, "title": d.get("title"), "caption": d.get("caption"),
                    "photographer": d.get("photographer"), "collection": d.get("collection"),
                    "thumb": d.get("thumbnail_url"), "page": f"https://www.gettyimages.com/detail/{gid}",
                    "embed_ok": "gie-single" in (d.get("html") or "")})
        time.sleep(0.25)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"{len(out)} -> {OUT} ({sum(1 for o in out if o.get('embed_ok'))} embeddable)", file=sys.stderr)


if __name__ == "__main__":
    main()
