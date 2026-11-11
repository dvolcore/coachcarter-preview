"""Patch 14: the whole film, self-hosted (no ads) + film stills and loops on every page.

Data: film.json gains media_base, per-scene slug/file/poster/order/act, 7 new fan-sourced scenes, the
'Real Coach Carter' featurette, 7 new caption-verified quotes, 20 wide stills (bands) and 4 loops.
Pages: a full-bleed film band on every page, loops behind the film sections, the scene library by act on
Archive, the featurette on Story. Idempotent."""
import json, shutil, subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent
FILM = R / "site/assets/data/film.json"
OUT = R / "tracking/film_media/out"
F = json.loads(FILM.read_text())


def dur(slug):
    s = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT / "v" / f"{slug}.mp4")]))
    return round(s, 1)


def dims(slug):
    w, h = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(OUT / "v" / f"{slug}.mp4")]).decode().strip().split(",")
    return round(int(w) / int(h), 3)


def mmss(s):
    return f"{int(s // 60)}:{int(round(s % 60)):02d}"


# posters -> site
pdir = R / "site/assets/film/p"; pdir.mkdir(parents=True, exist_ok=True)
for p in (OUT / "p").glob("*.jpg"):
    shutil.copy2(p, pdir / p.name)

F["media_base"] = "https://github.com/dvolcore/coachcarter-film/releases/download/scenes-v1/"
F["rights"] = ("Coach Carter (2005) © Paramount Pictures / MTV Films. Private client-review build: scenes are self-hosted "
               "copies (official Movieclips/Fandango uploads plus fan uploads for scenes with no official upload) so they play "
               "without ads; clearance is being handled by the Coach Carter team. Getty premiere photos are official Getty embeds.")

ACTS = [
    {"key": "contract", "label": "Act I", "title": "The contract", "line": "A new coach, a 2.3 GPA, coats and ties, and the losing stops now."},
    {"key": "lockout", "label": "Act II", "title": "The lockout", "line": "Undefeated, then padlocked. The town turns on him. The team stays."},
    {"key": "lastgame", "label": "Act III", "title": "The last game", "line": "St. Francis, the final shot, and what they won instead."},
]
F["acts"] = ACTS

# slug, youtube id, act, order, scene name, featured, hook (None = keep existing)
PLAN = [
    ("first-practice", "V1wAemvxNaM", "contract", 1, "Day One", True,
     "Day one at Richmond: 'sir' is a term of respect, the losing stops now, the contracts come out, and Cruz walks."),
    ("parents-contract", "fidQ2FQKGtQ", "contract", 2, "The Parents' Meeting", False,
     "Carter sells the parents on the contract ('student comes first'), then his son Damien signs up for a 3.5."),
    ("first-win", "qUiptlAJcyQ", "contract", 3, None, False, None),
    ("vision", "5Th5LyAVDRM", "contract", 4, "How Do You See Yourselves?", False,
     "Four seniors who could play in college. 'Tell me how you see yourselves.' Then Junior is suspended for skipping class."),
    ("juniors-mother", "WuSCEbZF4i4", "contract", 5, "Junior's Mother", False,
     "Junior Battle's mother comes to the store. Carter takes him back — after 1,000 push-ups and 1,000 suicides."),
    ("pushups", "1g82D68N-ys", "contract", 6, None, True, None),
    ("bay-hill", "JomrLxDiT5g", "lockout", 7, None, False, None),
    ("pool-party", "JFvtFgFv0Qw", "lockout", 8, "The Pool Party", False,
     "Undefeated and celebrating, the team sneaks off to a party in the suburbs. Carter finds them, and his own son, in the pool."),
    ("lockout", "lipT9ry5h3A", "lockout", 9, "The Lockout", True,
     "'In this hand I hold contracts…' Six players failing. Carter padlocks the gym and sends the team to the library."),
    ("better-life", "2FKPDOpKzDo", "lockout", 10, None, True, None),
    ("renny", "jdrcX9zjS80", "lockout", 11, "Renny", False,
     "Renny is shot. Timo Cruz runs to the one man he trusts: 'What do I got to do to play?'"),
    ("board-hearing", "iCc9rFHuzlI", "lockout", 12, "The Board Hearing", True,
     "The school board votes on the lockout. Carter: 'If you vote to end the lockout, you won't have to terminate me. I'll quit.'"),
    ("deepest-fear", "2_fDhqRk_Ro", "lockout", 13, None, True, None),
    ("pep-talk", "J97F53CAA1I", "lastgame", 14, None, False, None),
    ("final-shot", "fnH1ZtugoqU", "lastgame", 15, None, False, None),
    ("storybook-ending", "eSBnFu1YnrU", "lastgame", 16, None, True, None),
]
SOURCE = {
    "first-practice": "Boxoffice Movie Scenes (YouTube, 4K) — fuller cut of the official 'First Practice' scene",
    "parents-contract": "Movies and TV shows (YouTube)", "vision": "KnowledgeWorkx Video (YouTube, 1080p)",
    "juniors-mother": "NOW PLAYING (YouTube, 1080p)", "pool-party": "Boxoffice Movie Scenes (YouTube, 4K)",
    "lockout": "BENZ TV full-film upload, part 9 (YouTube, 266p — the only copy found)", "renny": "TheFallenSoul99 (YouTube, 1080p)",
    "board-hearing": "NOW ACTION (YouTube, 1080p)",
}
old = {c["id"]: c for c in F["clips"]}
act_label = {a["key"]: a["label"] for a in ACTS}
clips = []
for slug, yt, act, order, name, featured, hook in PLAN:
    c = dict(old.get(yt, {}))
    c.update({"id": yt, "yt": yt, "slug": slug, "file": f"{slug}.mp4", "poster": f"assets/film/p/{slug}.jpg", "aspect": dims(slug),
              "act": act, "act_label": act_label[act], "order": order, "featured": featured})
    d = dur(slug); c["duration_s"] = d; c["duration"] = mmss(d)
    if name: c["scene"] = name
    if hook: c["hook"] = hook
    if slug in SOURCE: c["web_source"] = SOURCE[slug]
    clips.append(c)
F["clips"] = clips

T = F["trailer"]["primary"]
T.update({"slug": "trailer", "yt": T["id"], "file": "trailer.mp4", "poster": "assets/film/p/trailer.jpg", "aspect": dims("trailer"), "scene": "Original trailer"})

F["real_carter"] = [
    {"slug": "real-carter-1", "yt": "n8beCoP9lc8", "file": "real-carter-1.mp4", "poster": "assets/film/p/real-carter-1.jpg", "aspect": dims("real-carter-1"),
     "scene": "The Real Coach Carter · Part 1", "kicker": "DVD featurette · Part 1", "duration": mmss(dur("real-carter-1")),
     "hook": "Ken Carter, his players and his son Damien on camera: the Richmond gym with no nets, the contracts, and why he took the job."},
    {"slug": "real-carter-2", "yt": "yzvd3xf6CTE", "file": "real-carter-2.mp4", "poster": "assets/film/p/real-carter-2.jpg?v=2", "aspect": dims("real-carter-2"),
     "scene": "The Real Coach Carter · Part 2", "kicker": "DVD featurette · Part 2", "duration": mmss(dur("real-carter-2")),
     "hook": "The 1999 lockout as the people who lived it remember it — and what became of the team."},
]

# quotes: re-point to slugs; fix timings for the new Day One cut; add caption-verified lines
idmap = {c["id"]: c["slug"] for c in clips}; idmap[T["id"]] = "trailer"
Q = F["quotes"]
for q in Q:
    if q.get("clip") in idmap: q["clip"] = idmap[q["clip"]]
Q[8].update({"clip": "first-practice", "t": "3:59", "t_s": 239})
Q[9].update({"clip": "parents-contract", "t": "0:22", "t_s": 22})
Q[11].update({"clip": "first-practice", "t": "1:17", "t_s": 77, "verified": True,
              "wording_note": "Wikiquote wording; heard in the Day One scene at 1:17 (caption track)."})
CAP = "Film audio, checked against the scene's caption track (2026-11-09)."
NEW = [
    ("The losing stops now.", "Coach Ken Carter", "Samuel L. Jackson", "first-practice", 123, "contracts"),
    ("Basketball is a privilege. If you want to play basketball on this team, these are the simple rules you have to follow.", "Coach Ken Carter", "Samuel L. Jackson", "parents-contract", 50, None),
    ("Part of growing up is making your own decisions and living with the consequences.", "Coach Ken Carter", "Samuel L. Jackson", "parents-contract", 186, None),
    ("We are a team. And until we all meet the terms of this contract, the gym will remain locked.", "Coach Ken Carter", "Samuel L. Jackson", "lockout", 75, "chain"),
    ("I took this job because I wanted to effect change in a special group of young men.", "Coach Ken Carter", "Samuel L. Jackson", "board-hearing", 175, "board-speech"),
    ("If you vote to end the lockout, you won't have to terminate me. I'll quit.", "Coach Ken Carter", "Samuel L. Jackson", "board-hearing", 187, "board-room"),
    ("Those are some stats for your ass.", "Coach Ken Carter", "Samuel L. Jackson", "better-life", 96, "desks"),
]
have = {q["text"] for q in Q}
for text, sp, actor, clip, t, still in NEW:
    if text in have: continue
    q = {"text": text, "speaker": sp, "actor": actor, "clip": clip, "t": mmss(t), "t_s": t, "sources": [], "verified": True, "wording_note": CAP}
    if still: q["still"] = still
    Q.append(q)

F["bands"] = json.loads((R / "site/assets/film/stills.json").read_text())
F["loops"] = [{"key": k, "src": f"assets/film/l/{k}.mp4", "poster": f"assets/film/l/{k}.webp"} for k in ("desks", "practice", "crowd", "carter")]
F["notes"] = [n for n in F["notes"] if not n.startswith("Scenes asked for but NOT available")] + [
    "2026-11-09: every scene now plays from self-hosted MP4s (github.com/dvolcore/coachcarter-film release scenes-v1) — no YouTube ads. "
    "Missing scenes (lockout, contract/parents, board hearing, Renny, Junior's mother, pool party, vision) come from fan uploads; "
    "the lockout is only available at 266p. Owner direction: build everything, clearance handled by the Coach Carter team."]
FILM.write_text(json.dumps(F, indent=1, ensure_ascii=False))
QI = {q["text"]: i for i, q in enumerate(Q)}
qi = lambda t: QI[t]
print("film.json: clips", len(clips), "quotes", len(Q), "bands", len(F["bands"]))

# ---------------- pages ----------------
def band(still, q=None, cls=""):
    qa = f' data-q="{q}"' if q is not None else ""
    return f'<section class="film-band{cls}" aria-label="From the film">\n<!-- film-band {still} -->\n  <div data-film="band" data-still="{still}"{qa}></div>\n</section>\n\n'


def before_last_section(page, block):
    p = R / "src" / page; s = p.read_text()
    marker = block.split("\n")[1]
    if marker in s: return
    i = s.rindex("<section")
    p.write_text(s[:i] + block + s[i:])


def insert(page, anchor, block, after=False):
    p = R / "src" / page; s = p.read_text()
    marker = block.split("\n")[1] if block.startswith("<section") else block.strip()
    if marker in s: return
    assert s.count(anchor) >= 1, f"{page}: anchor missing {anchor[:50]}"
    i = s.index(anchor) + (len(anchor) if after else 0)
    p.write_text(s[:i] + block + s[i:])


LOSING, PRIV, GROW = qi(NEW[0][0]), qi(NEW[1][0]), qi(NEW[2][0])
LOCKED, CHANGE, QUIT, STATS = qi(NEW[3][0]), qi(NEW[4][0]), qi(NEW[5][0]), qi(NEW[6][0])

before_last_section("index.html", band("desks", LOCKED))
before_last_section("story.html", band("board-speech", CHANGE))
before_last_section("keynotes.html", band("board-room", QUIT))
before_last_section("playbook.html", band("contracts", PRIV))
before_last_section("partners.html", band("bayhill-joy", 3))
before_last_section("series.html", band("homecoming", 2))
# investors: strictly business, no film band (Ralph 2026-11-09)
before_last_section("impact.html", band("desks-wide", 10))
before_last_section("record.html", band("pushups", 5))
before_last_section("brand.html", band("carter-gym", 11))
before_last_section("store.html", band("dream-team", 4))
before_last_section("archive.html", band("stfrancis-crowd", 7))

# second band on the long pages
insert("index.html", '<section class="section carbon" id="film">', band("chain", 6))
insert("story.html", '<section class="section carbon" id="real-vs-film">', band("street-night", GROW))

# loops behind the film sections
LOOP = '\n  <div class="film-loop" data-film="loop" data-loop="{k}"></div>'
for page, sec, k in (("index.html", '<section class="section carbon" id="film">', "carter"),
                     ("series.html", '<section class="section carbon" id="where-it-began">', "practice"),
                     ("archive.html", '<section class="section carbon" id="the-2005-film">', "desks")):
    p = R / "src" / page; s = p.read_text()
    if f'data-loop="{k}"' not in s:
        assert sec in s, (page, sec)
        s = s.replace(sec, sec.replace('class="section carbon"', 'class="section carbon has-loop"') + LOOP.format(k=k), 1)
        p.write_text(s)

# archive: whole film by act + stills gallery + featurette
p = R / "src/archive.html"; s = p.read_text()
s = s.replace("All nine official scenes, in story order, and the night the cast and the real coach walked the carpet at Grauman's Chinese Theatre.",
              "The whole film in sixteen scenes, in story order: the contract, the lockout, the last game. Then the real Coach Carter, and premiere night at Grauman's Chinese Theatre.")
s = s.replace('<span class="eyebrow">Every official scene · premiere night</span>', '<span class="eyebrow">Sixteen scenes · three acts · premiere night</span>')
if 'data-film="library"' not in s:
    s = s.replace('<div data-film="rail"></div>', '<div data-film="library"></div>\n    <h3 class="h-m mt-l">The real Coach Carter</h3>\n    <div class="mt-m" data-film="realcarter"></div>\n    <h3 class="h-m mt-l">Stills from the film</h3>\n    <div class="mt-m" data-film="stills"></div>', 1)
p.write_text(s)

# story: the featurette right after real-vs-film
REAL = """<section class="section" id="the-real-coach">
<!-- film-realcarter -->
  <span class="secnum">On camera</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">DVD featurette · Paramount, 2005</span><h2 class="h-l mt-s">The real<br><span class="gold-text">Coach Carter.</span></h2></div>
      <p class="lede" style="max-width:42ch">Before Samuel L. Jackson played him, Ken Carter told it himself — with the players he locked out and the son who followed him to Richmond.</p></div>
    <div data-film="realcarter"></div>
  </div>
</section>

"""
p = R / "src/story.html"; s = p.read_text()
if "film-realcarter" not in s:
    i = s.index('<section class="section tight light">')
    s = s[:i] + REAL + s[i:]
    p.write_text(s)

# story strip + series feature use the full scene set
p = R / "src/story.html"; s = p.read_text()
s = s.replace('data-ids="V1wAemvxNaM,2FKPDOpKzDo,2_fDhqRk_Ro,eSBnFu1YnrU"', 'data-ids="first-practice,lockout,board-hearing,deepest-fear"')
p.write_text(s)

# quote bands: add the new lines
for page, old_q, new_q in (("index.html", 'data-q="0,2,5,10,9,4"', f'data-q="0,{LOSING},5,{LOCKED},{QUIT},2,10,4"'),
                           ("keynotes.html", 'data-q="10,9,0"', f'data-q="10,{CHANGE},9,{GROW},0"'),
                           ("playbook.html", 'data-q="9,5,2"', f'data-q="{PRIV},9,{LOSING},5,{GROW},2"')):
    p = R / "src" / page; s = p.read_text(); p.write_text(s.replace(old_q, new_q))

# footer line
b = R / "tools/build.py"; s = b.read_text()
s = s.replace("Film scenes play from official Movieclips (Fandango) uploads on YouTube; no film footage is hosted here.",
              "Coach Carter (2005) © Paramount Pictures / MTV Films. Film scenes included for private client review.")
b.write_text(s)

# ---------------- css ----------------
C = R / "site/assets/css/fx.css"; css = C.read_text()
M = "/* ---- the 2005 film · bands, loops, library ---- */"
if M not in css:
    css += "\n" + M + r"""
.film-band { position: relative; padding: 0; background: #050608; overflow: hidden; }
.fband-in { position: relative; margin: 0; aspect-ratio: 2.48 / 1; min-height: 360px; max-height: 88vh; width: 100%; }
.fband-in img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.08); transition: transform 9s linear; }
[data-film="band"].in .fband-in img { transform: scale(1.0); }
.fband-in::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(5,6,8,.55) 0%, rgba(5,6,8,0) 30%, rgba(5,6,8,0) 45%, rgba(5,6,8,.88) 100%), linear-gradient(90deg, rgba(5,6,8,.55), rgba(5,6,8,0) 60%); pointer-events: none; }
.fband-in figcaption { position: absolute; left: 0; right: 0; bottom: clamp(22px, 5vw, 64px); z-index: 1; display: grid; gap: 14px; justify-items: start; }
.fband-in blockquote { margin: 0; max-width: 24ch; font: 500 clamp(26px, 3.6vw, 56px)/1.08 var(--f-quote, Georgia, serif); font-style: italic; color: var(--chalk); text-shadow: 0 2px 30px rgba(0,0,0,.6); }
.fband-who { font: 600 12px/1.4 var(--f-head); letter-spacing: .2em; text-transform: uppercase; color: rgba(245,240,232,.78); }
.fband-who b { color: var(--gold-hi); font-weight: 600; }
.fband-play { display: inline-flex; align-items: center; gap: 12px; padding: 0; border: 0; background: none; color: var(--chalk); cursor: pointer; font: 600 12px/1 var(--f-head); letter-spacing: .2em; text-transform: uppercase; }
.fband-play .fplay { width: 42px; height: 42px; }
.fband-play:hover .fplay { transform: scale(1.1); }
.fband-play:focus-visible { outline: 2px solid var(--gold-hi); outline-offset: 6px; border-radius: 30px; }
@media (max-width: 700px) { .fband-in { aspect-ratio: auto; height: 78vh; min-height: 460px; } .fband-in img { object-position: 50% 50%; } .fband-in blockquote { font-size: 26px; } }
@media (prefers-reduced-motion: reduce) { .fband-in img { transition: none; transform: none; } }
.has-loop { position: relative; isolation: isolate; }
.film-loop { position: absolute; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }
.film-loop video, .film-loop img { width: 100%; height: 100%; object-fit: cover; opacity: .22; filter: saturate(.85); }
.film-loop::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, var(--carbon, #101216) 0%, rgba(16,18,22,.55) 30%, rgba(16,18,22,.7) 70%, var(--carbon, #101216) 100%); }
.flib-act { padding-top: clamp(30px, 4vw, 54px); }
.flib-act + .flib-act { margin-top: clamp(20px, 3vw, 40px); border-top: 1px solid var(--line); }
.flib-head { display: grid; grid-template-columns: 120px minmax(0, 1fr); column-gap: 24px; align-items: baseline; margin-bottom: 24px; }
.flib-head .eyebrow { grid-row: span 2; }
.flib-head h3 { margin: 0; }
.flib-head p { margin: 6px 0 0; color: var(--slate); }
@media (max-width: 700px) { .flib-head { grid-template-columns: 1fr; } .flib-head .eyebrow { grid-row: auto; } }
.freal-two { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.fcard-doc .fthumb { aspect-ratio: 4 / 3; }
@media (max-width: 760px) { .freal-two { grid-template-columns: 1fr; } }
.fstills { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.fstill { position: relative; padding: 0; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: #000; cursor: pointer; aspect-ratio: 2.48 / 1; }
.fstill img { width: 100%; height: 100%; object-fit: cover; transition: transform .9s var(--ease), opacity .4s; }
.fstill span { position: absolute; left: 0; right: 0; bottom: 0; padding: 18px 10px 8px; font-size: 12px; line-height: 1.3; text-align: left; color: var(--chalk); background: linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.8)); opacity: 0; transition: opacity .3s; }
.fstill:hover img { transform: scale(1.06); } .fstill:hover span, .fstill:focus-visible span { opacity: 1; }
.fstill:focus-visible { outline: 2px solid var(--gold-hi); outline-offset: 3px; }
@media (max-width: 1000px) { .fstills { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 640px) { .fstills { grid-template-columns: 1fr 1fr; } .fstill span { opacity: 1; font-size: 11px; } }
.fp-box { aspect-ratio: 2.39 / 1; }
.fp-box video { position: absolute; inset: 0; width: 100%; height: 100%; background: #000; }
.fp-in { width: min(1400px, 100%); }
"""
    C.write_text(css)
print("patch_14 ok")
