"""Motion plates for the inner pages: seven more scenes + which plate opens which page.

Same grammar as motion.py (640x400 SVG; d = draw, p = pop, f = fade; --i = order).
Only facts already on the site appear in a scene (13-0, six weeks, fifteen of fifteen, the outlets
in the home-page coverage strip). The investor chart carries no numbers and says it is not to scale.
"""
import motion

LOCK = '''<svg viewBox="0 0 640 400" class="sc sc-lock">
  <path class="d" style="--i:0;--t:1.4s" pathLength="1" d="M30 352 H610"/>
  <g transform="translate(64 0)">
  <path class="d" style="--i:1;--t:1.6s" pathLength="1" d="M150 352 V44 H490 V352"/>
  <rect class="d" style="--i:4" pathLength="1" x="162" y="56" width="154" height="296"/>
  <rect class="d" style="--i:5" pathLength="1" x="324" y="56" width="154" height="296"/>
  <rect class="d win" style="--i:8" pathLength="1" x="192" y="84" width="94" height="72"/>
  <rect class="d win" style="--i:9" pathLength="1" x="354" y="84" width="94" height="72"/>
  <g class="sign f" style="--i:6"><rect x="262" y="12" width="116" height="26" rx="2"/><text x="320" y="31">GYM</text></g>
  <path class="handle p" style="--i:11" d="M296 190 v52"/><path class="handle p" style="--i:11" d="M344 190 v52"/>
  <path class="chain d" style="--i:14;--t:.8s" pathLength="1" d="M296 204 q24 30 48 0"/><path class="chain d" style="--i:17;--t:.8s" pathLength="1" d="M296 224 q24 34 48 0"/>
  <g class="padlock"><path class="shackle" d="M307 256 v-12 a13 13 0 0 1 26 0 v12"/><g class="p" style="--i:22"><rect class="body" x="298" y="256" width="44" height="36" rx="5"/><circle class="key" cx="320" cy="270" r="4"/><path class="key" d="M320 272 v9"/></g></g>
  <g class="notice p" style="--i:27" transform="rotate(5 410 150)"><rect x="362" y="176" width="104" height="70"/><text class="a" x="414" y="203">GYM CLOSED</text><text class="b" x="414" y="221">STUDY HALL</text><text class="b" x="414" y="235">UNTIL GRADES COME UP</text></g>
  </g>
  <g class="rec f" style="--i:18"><text class="n" x="34" y="112">13–0</text><text class="l" x="34" y="134">RECORD WHEN</text><text class="l" x="34" y="148">THE DOORS LOCKED</text>
    <path class="rl" d="M34 170 h60"/><text class="l" x="34" y="194">RICHMOND HIGH</text><text class="l" x="34" y="208">JANUARY 1999</text></g>
</svg>'''


def _onair():
    bars = "".join(f'<rect class="wv" style="--i:{i}" x="{150 + i * 25}" y="{150 - h // 2}" width="11" height="{h}" rx="2"/>'
                   for i, h in enumerate([34, 62, 88, 50, 104, 72, 40, 96, 58, 84, 46, 70, 30, 54]))
    names = ["NPR", "CNN", "TODAY", "DR. PHIL", "THE VIEW"]
    outs = "".join(f'<text class="outlet outlet-{i + 1}" x="132" y="272">{n}</text>' for i, n in enumerate(names))
    return f'''<svg viewBox="0 0 640 400" class="sc sc-onair">
  <rect class="d" style="--i:0;--t:1.6s" pathLength="1" x="90" y="46" width="460" height="278" rx="10"/>
  <path class="d" style="--i:4" pathLength="1" d="M320 324 v26 M236 350 h168"/>
  <g class="lamp f" style="--i:6"><rect x="442" y="62" width="92" height="28" rx="14"/><circle cx="459" cy="76" r="5"/><text x="471" y="81">ON AIR</text></g>
  <g class="wave f" style="--i:8">{bars}</g>
  <text class="oa-cap f" style="--i:10" x="112" y="78">AS COVERED BY</text>
  <g class="third"><rect class="bar" x="110" y="240" width="330" height="48"/><rect class="edge" x="110" y="240" width="7" height="48"/>{outs}</g>
  <path class="tick d" style="--i:12" pathLength="1" d="M110 304 H530"/>
</svg>'''


def _stage():
    crowd = "".join(f'<circle class="p" style="--i:{10 + (r * 3 + c) % 14}" cx="{92 + c * 35 + (r % 2) * 17}" cy="{334 + r * 22}" r="6"/>'
                    for r in range(3) for c in range(14 if r % 2 == 0 else 13))
    return f'''<svg viewBox="0 0 640 400" class="sc sc-stage">
  <path class="beam b1" d="M210 0 L96 300 H300 Z"/><path class="beam b2" d="M430 0 L340 300 H544 Z"/>
  <path class="d" style="--i:0;--t:1.5s" pathLength="1" d="M40 300 H600"/>
  <path class="d drape" style="--i:2" pathLength="1" d="M52 0 V300 M76 0 V300 M588 0 V300 M564 0 V300"/>
  <path class="d" style="--i:5" pathLength="1" d="M292 300 l8 -76 h40 l8 76"/>
  <path class="d" style="--i:7" pathLength="1" d="M320 224 v-34"/><circle class="mic p" style="--i:9" cx="320" cy="182" r="9"/>
  <g class="crowd">{crowd}</g>
  <g class="ticket p" style="--i:20" transform="rotate(-8 500 110)"><path d="M436 78 h128 v20 a8 8 0 0 0 0 16 v20 h-128 v-20 a8 8 0 0 0 0 -16 z"/><path class="perf" d="M470 82 v48"/><text class="a" x="517" y="104">KEYNOTE</text><text class="b" x="517" y="122">ADMIT ONE ROOM</text><text class="c" x="453" y="111" transform="rotate(-90 453 111)">KC</text></g>
</svg>'''


def _weeks():
    cols = []
    for i in range(6):
        x = 74 + i * 86
        cols.append(f'<rect class="track d" style="--i:{i}" pathLength="1" x="{x}" y="86" width="62" height="214" rx="5"/>'
                    f'<rect class="fill" style="--i:{i}" x="{x + 5}" y="91" width="52" height="204" rx="3"/>'
                    f'<path class="ck d" style="--i:{12 + i * 5};--t:.35s" pathLength="1" d="M{x + 18} {56} l9 10 l18 -22"/>'
                    f'<text class="wk f" style="--i:{4 + i}" x="{x + 31}" y="326">WEEK {i + 1}</text>')
    return f'''<svg viewBox="0 0 640 400" class="sc sc-weeks">
  {"".join(cols)}
  <path class="base d" style="--i:8;--t:1.6s" pathLength="1" d="M60 344 H580"/>
  <text class="tl f" style="--i:10" x="60" y="374">WEEKS COMPLETE</text>
  <text class="tn f" style="--i:10" x="580" y="382"><tspan data-tally="6">6</tspan><tspan class="of"> / 6</tspan></text>
</svg>'''


def _wall():
    tiles = []
    for r in range(3):
        for c in range(4):
            i = r * 4 + c
            x, y = 104 + c * 110, 44 + r * 104
            if (r + c) % 2 == 0:
                tiles.append(f'<g class="tile p" style="--i:{i}"><rect x="{x}" y="{y}" width="98" height="92" rx="3"/><image href="assets/brand/monogram_gold.svg" x="{x + 23}" y="{y + 20}" width="52" height="52"/></g>')
            else:
                tiles.append(f'<g class="tile yours p" style="--i:{i}"><rect x="{x}" y="{y}" width="98" height="92" rx="3"/><text x="{x + 49}" y="{y + 43}">YOUR</text><text x="{x + 49}" y="{y + 61}">BRAND</text></g>')
    return f'''<svg viewBox="0 0 640 400" class="sc sc-wall">
  {"".join(tiles)}
  <circle class="flash f1" cx="186" cy="330" r="26"/><circle class="flash f2" cx="470" cy="96" r="20"/><circle class="flash f3" cx="360" cy="230" r="16"/>
  <path class="rope d" style="--i:14;--t:1.6s" pathLength="1" d="M70 372 q250 -30 500 0"/>
  <path class="post p" style="--i:13" d="M70 384 v-30"/><path class="post p" style="--i:13" d="M570 384 v-30"/>
</svg>'''


CHART = '''<svg viewBox="0 0 640 400" class="sc sc-chart">
  <path class="d" style="--i:0;--t:1.5s" pathLength="1" d="M96 40 V332 H580"/>
  <rect class="bar hi" x="170" y="70" width="118" height="262"/><rect class="bar lo" x="390" y="268" width="118" height="64"/>
  <path class="dash f" style="--i:14" d="M288 70 H560"/>
  <path class="brk d" style="--i:16;--t:1s" pathLength="1" d="M532 76 V262"/><path class="brk d" style="--i:16" pathLength="1" d="M522 76 h20 M522 262 h20"/>
  <g class="gap p" style="--i:22"><rect x="474" y="150" width="116" height="38" rx="19"/><text x="532" y="175">THE GAP</text></g>
  <text class="lb f" style="--i:8" x="229" y="356">AWARENESS</text><text class="lb f" style="--i:10" x="449" y="356">REVENUE</text>
  <text class="note f" style="--i:24" x="580" y="388">ILLUSTRATION · NOT TO SCALE</text>
</svg>'''


def _grid15():
    out = []
    for r in range(3):
        for c in range(5):
            i = r * 5 + c
            x, y = 96 + c * 92, 40 + r * 88
            out.append(f'<g class="kcard p" style="--i:{i}"><rect x="{x}" y="{y}" width="80" height="70" rx="3"/>'
                       f'<path class="ln" d="M{x + 12} {y + 18} h40 M{x + 12} {y + 32} h54 M{x + 12} {y + 46} h30"/></g>'
                       f'<path class="ck d" style="--i:{i + 12};--t:.3s" pathLength="1" d="M{x + 50} {y + 50} l6 7 l13 -18"/>')
    return f'''<svg viewBox="0 0 640 400" class="sc sc-cards">
  {"".join(out)}
  <path class="bar d" style="--i:16;--t:2.2s" pathLength="1" d="M96 326 H544"/>
  <text class="tl f" style="--i:10" x="96" y="358">WENT ON TO HIGHER EDUCATION</text><text class="tl f sm" style="--i:11" x="96" y="376">LOS ANGELES TIMES, 2001</text>
  <text class="tn f" style="--i:10" x="544" y="372"><tspan data-tally="15">15</tspan><tspan class="of"> / 15</tspan></text>
</svg>'''


OWN = "assets/img/own/"
CAMP = "assets/img/academy/campaign/"
motion.SCENES.update({
    "lock": LOCK, "onair": _onair(), "stage": _stage(), "weeks": _weeks(), "wall": _wall(), "chart": CHART, "cards-15": _grid15(),
    "strip-archive": motion._strip(["assets/img/private/" + f for f in ("all-stars-24-900.jpg", "drphil-jackson-900.jpg", "courtside-prince-jackson-900.jpg", "with-usher-900.jpg", "oilers-team-900.jpg", "huddle-900.jpg")]),
    "strip-lookbook": motion._strip([CAMP + f for f in ("front-row-opening-night.webp", "front-row-campus-duo.webp", "back-of-jacket.webp",
                                                         "front-row-library-pleats.webp", "after-hours-stage.webp", "front-row-outdoor-court.webp")]),
    "leader-series": motion.LEADER.replace("FREE PREVIEW · 0:60", "CLASS IS IN SESSION").replace("REEL 01", "A STUDIO405 PRODUCTION"),
    "contract-brief": (motion.CONTRACT.replace("THE CONTRACT", "THE BRIEFING").replace("2.3 GPA, EVERY SEMESTER", "KEY POINTS FIRST")
                       .replace("FRONT ROW, EVERY CLASS", "THEN THE FULL DETAIL").replace("TEN HOURS OF STUDY A WEEK", "WHY EACH PART IS HELD BACK")
                       .replace("COAT AND TIE ON GAME DAY", "PRIVATE, NOT FOR THE PUBLIC").replace(">SIGNED<", ">FOR COACH<")),
})

# page -> (scene, kicker, title lines, blurb, [(chip, href)], regex of the section the plate goes in front of)
SEC = r'<section\b[^>]*\bid="%s"'
PAGE_PLATES = {
    "story": ("lock", "The Man · The Story", ["The", "Lockout"], "January 1999. Thirteen and oh, and the gym doors chained until the grades came up.",
              [("The season", "#undefeated-wasn-t-enough"), ("Timeline", "#from-richmond-to-the-world"), ("The headlines", "#loved-on-friday-hated-by-monday"),
               ("The contract", "#original-contract"), ("Real life vs. the film", "#real-vs-film")], SEC % "undefeated-wasn-t-enough"),
    "record": ("onair", "The Man · The Record", ["On the", "Record"], "National television, full rooms and honors. Every claim linked to where it ran.",
               [("On air", "#the-country-tuned-in"), ("In the room", "#room"), ("On film", "#the-moments-on-film"), ("Coast to coast", "#coast-to-coast"),
                ("Honors", "#honored-for-the-work")], SEC % "the-country-tuned-in"),
    "archive": ("strip-archive", "The Man · The Archive", ["The", "Archive"], "His private collection, the 2005 film scene by scene, and the document behind the lockout.",
                [("Private collection", "#private-collection"), ("Headliners", "#headliners-sec"), ("Scrapbook", "#scrapbook"), ("The 2005 film", "#the-2005-film"), ("The contract", "#original-contract"),
                 ("Films", "#films"), ("Photographs", "#photos")], SEC % "private-collection"),
    "impact": ("cards-15", "The Man · The Foundation", ["Fifteen", "of Fifteen"], "The fifteen who fell short of the contract all went on to higher education. The game was the hook.",
               [("Our goal", "#our-goal-is-to-change-the-neighborhood"), ("Where the work happens", "#where-the-work-happens"),
                ("The relaunch", "#be-first-in-for-the-relaunch"), ("The story and its source", "story.html#from-richmond-to-the-world")], SEC % "our-goal-is-to-change-the-neighborhood"),
    "keynotes": ("stage", "Work with Coach · Keynotes", ["On", "Stage"], "Five signature talks, each built around your room. Then check a date.",
                 [("The reel", "#see-the-room-change"), ("Five talks", "#five-talks-one-standard"), ("Rooms he has worked", "#in-the-room-for-the-best"),
                  ("Formats", "#built-for-your-event"), ("What hosts say", "#what-hosts-say"), ("Book", "#book")], SEC % "see-the-room-change"),
    "teams": ("weeks", "Work with Coach · Teams & Schools", ["Six", "Weeks"], "One contract, six weeks. Every player, parent and coach signs something.",
              [("The program", "#program"), ("The commitment", "#commitment"), ("Week by week", "#weeks"), ("Price", "#price"), ("Run the play", "#run-the-play"),
               ("Inquire", "#inquire")], SEC % "i-m-a"),
    "partners": ("wall", "Work with Coach · Partners", ["Your Brand,", "His Standard"], "Partnership positions, a live package builder and clear rules for using the name.",
                 [("The scenes", "#the-film"), ("Positions", "#pick-your-position"), ("Budget owners", "#budget-owners"), ("Build a package", "#builder"),
                  ("Rules", "#clear-rules-fast-approvals"), ("Inquire", "#inquire")], SEC % "the-film"),
    "playbook": ("court", "Work with Coach · The Playbook", ["Run", "the Play"], "One standard, ten ways in. Pick the play that fits your team, school or company.",
                 [("The plays", "#plays"), ("Pilots", "#pilots"), ("The family of marks", "#the-coach-carter-family-of-marks"),
                  ("Talk to us", "#tell-us-the-standard-you-want-to-be-know")], SEC % "plays"),
    "series": ("leader-series", "Academy · The Series", ["Class Is", "In Session"], "Coach Carter Academy. A free preview now, Season One at launch.",
               [("Season One", "#watch-plans"), ("The story", "#the-man-who-taught-them-to-finish"), ("It really happened", "#true-story"),
                ("Where it began", "#where-it-began"), ("The slate", "#slate"), ("Sponsor the season", "#partner")], SEC % "watch-plans"),
    "gallery": ("strip-lookbook", "Academy · The Lookbook", ["The", "Lookbook"], "The Front Row Letterman on campus, after hours and in editorial.",
                [("On campus", "#on-campus"), ("Both sides of the jacket", "#academy-contract"), ("After hours", "#after-hours"),
                 ("Editorial", "#fashion-editorial"), ("See the jacket", "academy-product.html?product=front-row-letterman")], SEC % "on-campus"),
    "investors": ("chart", "Company · Investors", ["The", "Gap"], "Top-tier awareness, bottom-tier monetization. The distance between them is the case.",
                  [("Thesis", "#thesis"), ("The asset", "#asset"), ("The gap", "#gap"), ("The model", "#model"), ("Valuation", "#valuation"), ("Risks", "#risks"),
                   ("Data room", "#contact")], SEC % "thesis"),
    "brand": ("seal", "Company · Press & Brand Kit", ["One", "Mark"], "The KC seal, the wordmark, the palette and the type. Built to be used the same way every time.",
              [("For press & programs", "#for-press-programs"), ("The story", "story.html"), ("Partnerships", "partners.html")],
              r'<section class="section carbon">'),
    "coach": ("contract-brief", "Company · Private", ["The", "Briefing"], "Everything in the playbook that stays off the public site. Key points first, then the detail.",
              [("Index", "#covers"), ("Start here", "#part-1"), ("The plan", "#part-2"), ("The opportunity", "#part-3"), ("Story and scenarios", "#part-4"),
               ("Evidence", "#part-5")], SEC % "covers"),
}
