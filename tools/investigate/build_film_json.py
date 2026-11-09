#!/usr/bin/env python3
"""build_film_json.py — assemble site/assets/data/film.json (the original-film library) from tool results:
  tracking/investigation/film/clips_meta.json      (film_clips.py: yt-dlp metadata + thumbnail HTTP/size checks)
  tracking/investigation/film/getty_film_oembed.json (getty_film.py: Getty oEmbed et/sig/w/h)
  tracking/investigation/film/subs/*.vtt           (YouTube caption tracks, used only to timestamp quotes)
  tracking/investigation/film/wikiquote_coach_carter.wiki, wikipedia_*.wiki, mojo.html, cnn_1999.html, sfgate_*.html
Curated text below (scene names, stills descriptions, quote picks) was written from those files on 2026-11-09.
No video is downloaded or re-hosted: clips are YouTube IDs for embedding; stills are i.ytimg.com URLs / Getty embeds."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "tracking/investigation/film"
OUT = ROOT / "site/assets/data/film.json"

meta = {m["id"]: m for m in json.loads((INV / "clips_meta.json").read_text()) if "error" not in m}
# Paramount Plus item: yt-dlp gives no formats (store/PO-token item), so metadata came from
# `yt-dlp --ignore-no-formats-error --dump-json` + the watch page (playabilityStatus OK, playableInEmbed true).
PPLUS = {"id": "a6Zpa4rtpkA", "title": "Coach Carter", "channel": "Paramount Plus", "channel_id": "UCrRttZIypNTA1Mrfwo745Sg",
         "upload_date": "20231208", "duration": 153, "view_count": None, "age_limit": 0, "playable_in_embed": True}

def yt(i): return f"https://www.youtube.com/watch?v={i}"

# Story order = Movieclips' own numbering (1/9 .. 9/9). clip_description = Movieclips' CLIP DESCRIPTION text (verbatim).
CLIPS = [
 ("V1wAemvxNaM", 1, "First Practice", True,
  "Coach Carter (Samuel L. Jackson) presents his new team with conduct contracts at the start of practice, but Timo (Rick Gonzalez) has other plans.",
  "Contracts, 'sir', and Carter pinning Timo to the wall: 'I'm not a teacher. I'm the new basketball coach.'"),
 ("qUiptlAJcyQ", 2, "Come-from-Behind Win", False,
  "Coach Carter's (Samuel L. Jackson) Richmond High team overcomes a three point deficit with help from freshman Damien (Robert Ri'chard) to get their first win of the season.", None),
 ("1g82D68N-ys", 3, "Push-Ups and Suicides", True,
  "The team shoulders the remaining drills assigned by Coach Carter (Samuel L. Jackson) to Timo (Rick Gonzalez) in order to help him earn back his spot on the roster.",
  "'One person struggles, we all struggle.'"),
 ("JomrLxDiT5g", 4, "Richmond vs. Bay Hill", False,
  "Coach Carter (Samuel L. Jackson) manages the final seconds of Richmond's road game against Bay Hill.", None),
 ("2FKPDOpKzDo", 5, "A Better Life", True,
  "Coach Carter (Samuel L. Jackson) assures his group of high school players that he will do anything to help them get to college.",
  "The stats speech: 'I see a system that's designed for you to fail.'"),
 ("2_fDhqRk_Ro", 6, "Our Deepest Fear", True,
  "The team recommits to improving their grades while Timo (Rick Gonzalez) eloquently expresses his thanks to Coach Carter (Samuel L. Jackson).",
  "The lockout payoff: the team keeps studying and Timo answers 'What is your deepest fear?'"),
 ("J97F53CAA1I", 7, "Timeout Pep Talk", False,
  "Coach Carter (Samuel L. Jackson) refocuses his team after getting behind during the third quarter of the championship game.", None),
 ("fnH1ZtugoqU", 8, "The Final Shot", True,
  "Coach Carter (Samuel L. Jackson) and the crowd watch Richmond and St. Francis play the final seconds of the championship game.", None),
 ("eSBnFu1YnrU", 9, "Not Your Storybook Ending", True,
  "Coach Carter (Samuel L. Jackson) addresses his team in the locker room following the championship game.",
  "'I came to coach basketball players, and you became students.' Then: 'Rich-what?' 'RICHMOND!'"),
]
OFFICIAL_NOTE = {"UC3gNmTGu-TTbFPpfSs5kNkg": "Movieclips — Fandango-owned official licensed movie-clip channel (verified badge)",
                 "UCTCjFFoX1un-j7ni4B6HJ3Q": "Rotten Tomatoes Classic Trailers — Fandango channel, formerly 'Movieclips Classic Trailers' (verified badge)",
                 "UCrRttZIypNTA1Mrfwo745Sg": "Paramount Plus — Paramount's official streaming channel"}

def thumbs(i, letterbox):
    m = meta.get(i, {})
    t = {k: {"url": v["url"], "status": v["status"], "w": v["w"], "h": v["h"]} for k, v in (m.get("thumbs") or {}).items()}
    for n in ("maxres1", "maxres2", "maxres3"):
        t[n] = {"url": f"https://i.ytimg.com/vi/{i}/{n}.jpg", "status": 200, "w": 1280, "h": 720, "picture_box": letterbox}
    return t

MC_BOX = {"x": 0, "y": 91, "w": 1280, "h": 538, "note": "2.38:1 scope picture; black bars above/below, MOVIECLIPS.com watermark in the bottom bar (~y 640-680) — crop to this box"}
TR_BOX = {"x": 0, "y": 88, "w": 1280, "h": 546, "note": "2.35:1 scope picture inside black letterbox bars — crop to this box"}

clips = []
for vid, n, name, feat, desc, hook in CLIPS:
    m = meta[vid]
    clips.append({
        "id": vid, "order": n, "scene": name, "featured": feat,
        "title": m["title"], "channel": m["channel"], "channel_id": m["channel_id"],
        "channel_verified": m.get("channel_is_verified"), "official_basis": OFFICIAL_NOTE[m["channel_id"]],
        "upload_date": m["upload_date"], "duration_s": m["duration"], "duration": m.get("duration_string"),
        "view_count": m["view_count"], "view_count_checked": "2026-11-09",
        "age_limit": m["age_limit"], "playable_in_embed": m["playable_in_embed"], "source_resolution": f'{m.get("width")}x{m.get("height")}',
        "description": desc, "description_source": "Movieclips CLIP DESCRIPTION (YouTube description)", "hook": hook,
        "url": yt(vid), "embed": f"https://www.youtube-nocookie.com/embed/{vid}",
        "poster": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
        "poster_note": "maxresdefault is a real 1280x720 custom thumbnail (HTTP 200, measured) but carries a Fandango 'F HD' badge bottom-left; for a clean frame use thumbs.maxres1-3 cropped to picture_box",
        "thumbs": thumbs(vid, MC_BOX),
    })

tr = meta["d_GleoanbPE"]
trailer = {
 "primary": {"id": tr["id"], "title": tr["title"], "channel": tr["channel"], "channel_id": tr["channel_id"],
   "channel_verified": tr.get("channel_is_verified"), "official_basis": OFFICIAL_NOTE[tr["channel_id"]],
   "upload_date": tr["upload_date"], "duration_s": tr["duration"], "view_count": tr["view_count"], "view_count_checked": "2026-11-09",
   "age_limit": tr["age_limit"], "playable_in_embed": tr["playable_in_embed"], "source_resolution": f'{tr.get("width")}x{tr.get("height")}',
   "description": "Original theatrical trailer (includes the 'Paramount Pictures and MTV Films present' card).",
   "url": yt(tr["id"]), "embed": f"https://www.youtube-nocookie.com/embed/{tr['id']}",
   "poster": f"https://i.ytimg.com/vi/{tr['id']}/maxresdefault.jpg",
   "poster_note": "maxresdefault 1280x720 carries 'CLASSIC TRAILER' text + Fandango badge; clean frames = thumbs.maxres1-3 (letterboxed)",
   "thumbs": thumbs(tr["id"], TR_BOX)},
 "alternate": {**PPLUS, "channel_verified": None, "official_basis": OFFICIAL_NOTE[PPLUS["channel_id"]],
   "description": "Paramount+ upload titled 'Coach Carter' (2:33). Its auto-frames maxres2/maxres3 match the Movieclips trailer frames, so it is the theatrical trailer; not watched end-to-end.",
   "caveats": ["view count not exposed by YouTube", "yt-dlp lists no formats for anonymous clients (store-style item); watch page reports playabilityStatus OK and playableInEmbed true",
               "maxresdefault here is an auto frame (letterboxed, no badge)"],
   "url": yt(PPLUS["id"]), "embed": f"https://www.youtube-nocookie.com/embed/{PPLUS['id']}",
   "poster": f"https://i.ytimg.com/vi/{PPLUS['id']}/maxresdefault.jpg", "thumbs": thumbs(PPLUS["id"], TR_BOX)},
}

IMDB_Q = "https://www.imdb.com/title/tt0393162/quotes/"
WQ = "https://en.wikiquote.org/wiki/Coach_Carter"
quotes = [
 {"text": "Our deepest fear is not that we are inadequate. Our deepest fear is that we are powerful beyond measure.",
  "speaker": "Timo Cruz", "actor": "Rick Gonzalez", "clip": "2_fDhqRk_Ro", "t": "0:40", "t_s": 40,
  "attribution": "Adapted from Marianne Williamson, 'A Return to Love: Reflections on the Principles of A Course in Miracles' (1992). Credit her whenever the line is shown.",
  "attribution_sources": [IMDB_Q, WQ, "https://en.wikipedia.org/wiki/A_Return_to_Love"],
  "sources": [IMDB_Q, WQ], "verified": True,
  "wording_note": "Both IMDb and Wikiquote open the speech with these two sentences (full speech is ~110 words)."},
 {"text": "Sir, I just wanna say thank you. You saved my life.", "speaker": "Timo Cruz", "actor": "Rick Gonzalez",
  "clip": "2_fDhqRk_Ro", "t": "1:23", "t_s": 83, "sources": [WQ], "verified": True,
  "wording_note": "Wikiquote gives it twice ('wanna say' / 'wanted to say'); the clip's caption track reads 'Sir, I just wanna say thank you.'"},
 {"text": "I came to coach basketball players, and you became students. I came to teach boys, and you became men.",
  "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson", "clip": "eSBnFu1YnrU", "t": "1:04", "t_s": 64,
  "also_in": [{"clip": "d_GleoanbPE", "t": "2:09"}], "sources": [IMDB_Q, WQ], "verified": True},
 {"text": "But you men played like champions, and never gave up. And champions hold their heads high.",
  "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson", "clip": "eSBnFu1YnrU", "t": "0:15", "t_s": 15,
  "sources": [WQ], "verified": True, "wording_note": "Wikiquote only (not on IMDb's quotes page)."},
 {"text": "Rich-what? / RICHMOND!", "speaker": "Coach Ken Carter and the team", "actor": "Samuel L. Jackson and cast",
  "clip": "eSBnFu1YnrU", "t": "1:46", "t_s": 106, "sources": [IMDB_Q, WQ], "verified": True},
 {"text": "You said we're a team. One person struggles, we all struggle. One person triumphs, we all triumph.",
  "speaker": "Jason Lyle", "actor": "Channing Tatum", "clip": "1g82D68N-ys", "t": "0:54", "t_s": 54,
  "also_in": [{"clip": "d_GleoanbPE", "t": "~2:00 (partial)"}], "sources": [IMDB_Q, WQ], "verified": True,
  "wording_note": "IMDb and Wikiquote agree on this wording; the clip's fan caption track reads 'One player triumphs'."},
 {"text": "Sir, they can cut the chains off the door, but they can't make us play.",
  "speaker": "Jason Lyle", "actor": "Channing Tatum", "clip": "2_fDhqRk_Ro", "t": "0:10", "t_s": 10, "sources": [IMDB_Q, WQ], "verified": True},
 {"text": "We've decided we're going to finish what you've started, sir.",
  "speaker": "Damien Carter", "actor": "Robert Ri'chard", "clip": "2_fDhqRk_Ro", "t": "0:17", "t_s": 17,
  "also_in": [{"clip": "d_GleoanbPE", "t": "~2:02"}], "sources": [IMDB_Q, WQ], "verified": True},
 {"text": "I'm not a teacher. I'm the new basketball coach.", "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson",
  "clip": "V1wAemvxNaM", "t": "1:52", "t_s": 112, "also_in": [{"clip": "d_GleoanbPE", "t": "0:31"}],
  "sources": [WQ], "verified": True, "wording_note": "Wikiquote dialogue section (reply to 'Teachers ain't supposed to touch students')."},
 {"text": "These boys are student athletes. \"Student\" comes first.", "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson",
  "clip": "d_GleoanbPE", "t": "0:50", "t_s": 50, "sources": [IMDB_Q], "verified": True,
  "wording_note": "IMDb (parents' meeting scene). Not in any of the 9 Movieclips scenes; heard in the trailer."},
 {"text": "I promise you I'll do everything in my power to get you to college and to a better life.",
  "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson", "clip": "2FKPDOpKzDo", "t": "1:56", "t_s": 116,
  "sources": [IMDB_Q], "verified": True, "wording_note": "Closing line of the 'stats' speech on IMDb."},
 {"text": "As of now, you are a sir. So are the rest of you. \"Sir\" is a term of respect, and you will have my respect until you abuse it.",
  "speaker": "Coach Ken Carter", "actor": "Samuel L. Jackson", "clip": None, "t": None,
  "sources": [WQ], "verified": "partial",
  "wording_note": "Wikiquote only (27 words; Wikiquote punctuates with '--' before 'and'). Not on IMDb and not in any official clip found — no timestamp. The exact phrase 'Sir, yes sir' is NOT a documented line of this film."},
]

getty = json.loads((INV / "getty_film_oembed.json").read_text())
PICK = {  # id -> short label (from the Getty caption)
 "51962764": "Director Thomas Carter, Ashanti and Samuel L. Jackson at the LA premiere",
 "51962766": "Director Thomas Carter, Ashanti and Samuel L. Jackson at the LA premiere",
 "51962751": "Texas Battle, Nana Gbewonyo, Rob Brown and Rick Gonzalez at the LA premiere",
 "51962754": "Nana Gbewonyo, Rob Brown, Denise Dowse, Texas Battle and Rick Gonzalez at the LA premiere",
 "51962755": "Rick Gonzalez, Denise Dowse, Antwon Tanner and Rob Brown compare watches at the premiere",
 "51962883": "Producers Brian Robbins and Mike Tollin with Samuel L. Jackson at the premiere",
 "524780360": "Samuel L. Jackson and Ashanti greet each other at the Grauman's Chinese premiere",
 "112420616": "Samuel L. Jackson on the red carpet at Grauman's Chinese Theatre",
 "51962472": "Samuel L. Jackson and Rick Gonzalez at the premiere afterparty",
 "51856250": "Channing Tatum, Robert Ri'chard, Nana Gbewonyo and Rick Gonzalez at a NY screening for high-school students",
 "109967051": "Coach Carter cast with Knicks great John Starks at the NY screening",
 "108766375": "Samuel L. Jackson wins the NAACP Image Award (Outstanding Actor) for Coach Carter",
 "108769840": "Samuel L. Jackson with his NAACP Image Award for Coach Carter",
 "452850363": "Atmosphere at the Coach Carter New York premiere, Loews 68th Street",
}
stills_getty = []
for g in getty:
    if not (g.get("landscape") and g.get("embed_ok")): continue
    stills_getty.append({"getty_id": g["id"], "pick": g["id"] in PICK, "label": PICK.get(g["id"]), "title": g["title"],
        "caption": g["caption"], "photographer": g["photographer"], "collection": g["collection"],
        "w": g["w"], "h": g["h"], "et": g["et"], "sig": g["sig"], "thumb": g["thumb"], "page": g["page"]})
stills_getty.sort(key=lambda s: (not s["pick"], s["getty_id"]))

YT_STILLS = [  # descriptions written from viewing each frame (contact sheet, 2026-11-09)
 ("1g82D68N-ys", "maxres3", "Carter, ball under his arm, watches Timo Cruz at the foot of the gym stairs", True),
 ("V1wAemvxNaM", "maxres3", "Carter pins Timo Cruz against the gym wall at the first practice", True),
 ("V1wAemvxNaM", "maxres1", "Carter, in suit and tie, squares up to a player in the gym", False),
 ("V1wAemvxNaM", "maxres2", "Players laughing at the new coach during the first practice", False),
 ("qUiptlAJcyQ", "maxres1", "Carter courtside under the gym lights", True),
 ("qUiptlAJcyQ", "maxres3", "Oilers players celebrate their first win", False),
 ("JomrLxDiT5g", "maxres3", "Carter smiles in front of a packed, cheering crowd", True),
 ("2FKPDOpKzDo", "maxres1", "Carter addresses the team in the school library", True),
 ("2FKPDOpKzDo", "maxres3", "Carter close-up in the library", False),
 ("2_fDhqRk_Ro", "maxres2", "Timo Cruz in the library scene ('Our Deepest Fear')", True),
 ("2_fDhqRk_Ro", "maxres3", "Carter in a tan suit, listening in the library", False),
 ("J97F53CAA1I", "maxres1", "Carter on the bench in front of the championship-game crowd", True),
 ("J97F53CAA1I", "maxres2", "Carter fires up the team during a timeout", False),
 ("fnH1ZtugoqU", "maxres1", "Fans in the stands during the final seconds against St. Francis", False),
 ("eSBnFu1YnrU", "maxres1", "Carter in the locker room after the championship game", True),
 ("eSBnFu1YnrU", "maxres2", "Players smiling in the locker room", False),
 ("d_GleoanbPE", "maxres2", "Carter with two players outdoors in golden late-day light (trailer)", True),
 ("d_GleoanbPE", "maxres1", "Two players in the gym (trailer)", False),
]
stills_yt = []
for vid, n, desc, pick in YT_STILLS:
    box = TR_BOX if vid == "d_GleoanbPE" else MC_BOX
    stills_yt.append({"video_id": vid, "variant": n, "url": f"https://i.ytimg.com/vi/{vid}/{n}.jpg", "w": 1280, "h": 720,
                      "http_status": 200, "picture_box": box, "pick": pick, "description": desc,
                      "channel": (meta.get(vid) or {}).get("channel")})

WP = "https://en.wikipedia.org/wiki/Coach_Carter"
MOJO = "https://www.boxofficemojo.com/title/tt0393162/"
IMDB = "https://www.imdb.com/title/tt0393162/"
facts = [
 {"key": "release_date", "value": "January 14, 2005 (US)", "sources": [MOJO, WP, IMDB]},
 {"key": "la_premiere", "value": "January 13, 2005, Grauman's Chinese Theatre, Hollywood (afterparty at The Highland)", "sources": ["https://www.gettyimages.com/detail/51962764", "https://www.gettyimages.com/detail/51962472"]},
 {"key": "director", "value": "Thomas Carter", "sources": [WP, IMDB]},
 {"key": "writers", "value": "Mark Schwahn & John Gatins", "sources": [WP, IMDB]},
 {"key": "producers", "value": "David Gale, Brian Robbins, Michael Tollin", "sources": [WP]},
 {"key": "studios", "value": "MTV Films and Tollin/Robbins Productions; distributed by Paramount Pictures", "sources": [WP, MOJO]},
 {"key": "cast", "value": [
   ["Samuel L. Jackson", "Coach Ken Carter"], ["Rob Brown", "Kenyon Stone"], ["Robert Ri'chard", "Damien Carter"],
   ["Rick Gonzalez", "Timo Cruz"], ["Nana Gbewonyo", "Junior Battle"], ["Antwon Tanner", "Worm"],
   ["Channing Tatum", "Jason Lyle (film debut)"], ["Ashanti", "Kyra"], ["Debbi Morgan", "Tonya Carter"],
   ["Texas Battle", "Maddux"], ["Denise Dowse", "Principal Garrison"], ["Octavia Spencer", "Mrs. Willa Battle"]],
   "sources": [WP, WQ]},
 {"key": "runtime", "value": "136 minutes (2 hr 16 min)", "sources": [MOJO, WP, IMDB]},
 {"key": "rating", "value": "PG-13", "sources": [MOJO, IMDB]},
 {"key": "music", "value": "Score by Trevor Rabin; soundtrack 'Coach Carter: Music from the Motion Picture' (Capitol Records, Jan 11, 2005)", "sources": [WP, "https://en.wikipedia.org/wiki/Coach_Carter_(soundtrack)"]},
 {"key": "soundtrack_tracks", "value": ["\"All Night Long\" – Red Café", "\"No Need for Conversation\" – Fabolous & Mike Shorey", "\"Professional\" – Chingy & G.I.B.",
   "\"Southside\" – The Game & Lil Scrappy", "\"Roll Wit' You\" – Ciara", "\"Wouldn't You Like to Ride\" – Kanye West, Malik Yusef, Common & JV",
   "\"Hope\" – Twista feat. Faith Evans (Billboard Hot 100 peak #31)", "\"Your Love (Is the Greatest Drug I've Ever Known)\" – Van Hunt"],
   "sources": ["https://en.wikipedia.org/wiki/Coach_Carter_(soundtrack)", "https://en.wikipedia.org/wiki/Hope_(Twista_song)"]},
 {"key": "soundtrack_charts", "value": "Billboard 200 #25; Billboard Soundtrack Albums #3; Top R&B/Hip-Hop Albums #15", "sources": ["https://en.wikipedia.org/wiki/Coach_Carter_(soundtrack)"]},
 {"key": "opening_weekend", "value": "#1 at the US box office, $24,182,961 from 2,524 theaters (Jan 14–16, 2005)", "sources": [MOJO, "https://www.boxofficemojo.com/weekend/2005W02/"]},
 {"key": "box_office", "value": "$67.26M domestic / $76.67M worldwide on a reported $30M budget (The Numbers reports $45M)", "sources": [MOJO, "https://www.the-numbers.com/movie/Coach-Carter-(2005)"],
  "note": "Full stats with sources: tracking/investigation/FILM_STATS.md"},
 {"key": "imdb_rating", "value": "7.4/10 from 196,834 ratings (checked 2026-11-09)", "sources": [IMDB]},
 {"key": "reception", "value": "Rotten Tomatoes 64% (149 reviews); Metacritic 57; CinemaScore 'A'; Roger Ebert 3 of 4 stars", "sources": [WP, "https://www.rogerebert.com/reviews/coach-carter-2005"]},
 {"key": "awards", "value": "Samuel L. Jackson won the NAACP Image Award for Outstanding Actor in a Motion Picture; Thomas Carter won Best Director at the Black Reel Awards and the Black Movie Awards", "sources": [WP, "https://www.gettyimages.com/detail/108766375"]},
 {"key": "filming", "value": "Los Angeles and Long Beach, California (incl. St. Anthony High School's gym)", "sources": [WP]},
 {"key": "home_video", "value": "DVD June 21, 2005; Blu-ray December 16, 2008", "sources": [WP]},
]
CNN = "https://www.cnn.com/US/9901/07/team.lockout/"
SF1 = "https://www.sfgate.com/news/article/Coach-scores-points-for-academics-3240562.php"
SF2 = "https://www.sfgate.com/education/article/Richmond-Rebound-High-school-basketball-players-2952622.php"
real_vs_film = [
 {"real": "Ken Carter padlocked the Richmond High gym and cancelled practices and games in early January 1999 while the Oilers were 13-0.", "sources": [CNN, SF1]},
 {"real": "15 of the program's 45 players (varsity, JV and freshman) had broken the academic contract — tardiness, missing homework, GPA under 2.3.", "sources": [SF2]},
 {"real": "The contract said 'basketball is the hook and education is the goal'; CNN described a 19-point pledge incl. 10 study hours a week and front-row seating.", "sources": [SF1, CNN]},
 {"real": "The lockout lasted about a week: on Jan 11, 1999 school officials announced all 45 players met the criteria and the season resumed without forfeits.", "film": "In the film the school board votes to end the lockout over Carter's objection and the team chooses to keep studying.", "sources": [SF2, WP]},
 {"real": "Carter was a 1977 Richmond High graduate who held the school's scoring record and owned a sporting-goods store.", "sources": [SF1]},
 {"real": "His son Damien Carter was on the 1999 team (quoted by CNN); the film's Damien Carter is played by Robert Ri'chard.", "sources": [CNN, WP]},
]

film = {
 "generated": "2026-11-09",
 "rights": "Paramount Pictures owns Coach Carter (2005). Video = embeds of official uploads only (Movieclips/Fandango, Rotten Tomatoes Classic Trailers/Fandango, Paramount Plus). Nothing is downloaded or re-hosted. Stills = YouTube-served thumbnails of those official uploads, and Getty Images editorial embeds (et/sig from Getty oEmbed).",
 "trailer": trailer,
 "clips": clips,
 "quotes": quotes,
 "stills": {"youtube": stills_yt, "getty": stills_getty,
            "getty_note": "Getty has NO film/production stills for Coach Carter (19 editorial search phrases run 2026-11-09, ~600 results reviewed by caption). These are landscape premiere/screening/award photos NOT already in getty_all.json. 'pick' = curated 14; others are extra landscape options. Embed with the gie widget like getty_all.json (id=et, sig, w, h, items=getty_id)."},
 "facts": facts,
 "real_vs_film": real_vs_film,
 "notes": [
  "Every official Coach Carter scene upload found is the Movieclips 9-clip set (all uploaded 2012-05-24, 1280x720, embeddable, age_limit 0). No Coach Carter uploads exist on Paramount Pictures, Paramount Movies or MTV channels (full upload lists scanned 2026-11-09).",
  "Scenes asked for but NOT available from an official channel: the lockout/chained gym doors (only the aftermath in 'Our Deepest Fear'), the contract-signing parents' meeting, the 'are you a madam?' first-practice exchange, the board hearing. Unofficial re-uploads exist (Boxoffice Movie Scenes, Binge Society, etc.) — do not use.",
  "View counts change; refresh with tools/investigate/film_clips.py before quoting them publicly.",
  "Quote timestamps come from each clip's YouTube caption track (fan/auto captions) and are approximate (±2 s).",
  "Thumbnails: maxresdefault for the Movieclips clips is a clean 16:9 frame but has a Fandango 'F HD' badge; maxres1/2/3 are auto-frames that are scope (≈2.38:1) inside black bars with a MOVIECLIPS.com watermark in the bottom bar — crop to picture_box. sddefault (640x480) and hqdefault (480x360) are 4:3 letterboxed.",
  "Coach Ken Carter's own channel 'Coach Carter' (UCX6fvPN4NHtzPkApTEmA08Q) has 3 low-view uploads titled 'CoachCarter salutes Actor Samuel L.Jackson's2005 Film, Coach Carter' — not checked for content/rights.",
 ],
}
OUT.write_text(json.dumps(film, indent=1, ensure_ascii=False))
print("wrote", OUT, "clips", len(clips), "quotes", len(quotes), "yt stills", len(stills_yt), "getty", len(stills_getty), sum(s["pick"] for s in stills_getty))
