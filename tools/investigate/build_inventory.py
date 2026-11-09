#!/usr/bin/env python3
"""Build videos.json + VIDEOS.md from the curated classification below plus cached metadata.

Inputs (created by yt_sweep.py / channel_dump.py / enrich.py):
  tracking/investigation/raw_search.json, channels/*.json, meta/*.json
Run: python3 build_inventory.py
"""
import glob, json, os, re, urllib.request, urllib.error
from collections import Counter, defaultdict

BASE = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"

CATS = [
    ("tv_news", "TV & news appearances"), ("keynote", "Keynotes & speeches"),
    ("interview", "Interviews & podcasts"), ("torch", "Olympic torch"), ("slamball", "SlamBall"),
    ("richmond", "Richmond (1999 and 2024)"), ("impact", "Impact Academy / Foundation / programs"),
    ("book", "Book (Yes Ma'am, No Sir)"), ("international", "International"), ("other", "Other"),
]

RIGHTS = {
    "own": "Coach's own channel: usable (check any third-party music before reuse)",
    "own_legacy": "Probably Coach's legacy/program channel: confirm with client, then usable",
    "news": "News outlet: embed only, no re-upload or clipping without a license",
    "university": "University/school: embed only; ask the institution for the master file",
    "nonprofit": "Event/nonprofit/org: embed only; ask the organiser for the master file",
    "bureau": "Speakers bureau promo: embed only; the bureau may share masters",
    "league": "League/broadcaster (SlamBall/ESPN): embed only",
    "podcast": "Podcast/show: embed only",
    "publisher": "Publisher/audiobook: embed only (publisher rights)",
    "fan": "Fan re-upload: rights unclear; don't feature until the original source is cleared",
    "film": "Film studio (Paramount/MTV): do not use",
}

# id: (category, owner_type, rank 1-5, note, verified)
# verified: "yes" = title/description names the real Ken Carter; "likely" = strong context; "check" = needs a watch
C = {
 # ---------- Coach's own: Ken Carter (TheRealCoachCarter) UCkq8ZF3PXaOsHDjgxggkrBg ----------
 "3-57R3Oanfw": ("keynote", "own", 5, "Official lifetime-highlights trailer (20+ yrs, 5,000+ talks)", "yes"),
 "VkpVPjp-_F8": ("keynote", "own", 5, "Official speaker reel", "yes"),
 "28kzO577IVw": ("tv_news", "own", 5, "Dr. Phil appearance", "yes"),
 "TReXvx2yseU": ("torch", "own", 5, "Runs with the Olympic torch, Richmond CA 2002", "yes"),
 "ikKUrVzJ4KM": ("keynote", "own", 3, "Speech to Burleson ISD teachers (Centennial HS, TX)", "yes"),
 "akqKkkhiBes": ("keynote", "own", 3, "Black History Month, Georgia Gwinnett College", "yes"),
 "cV0tGvjjTUc": ("keynote", "own", 3, "Georgia Gwinnett College visit (second cut)", "yes"),
 "FhocgdnkLcA": ("impact", "own", 3, "'Get Coached' coaching program promo", "yes"),
 "7r8WktxWV5M": ("impact", "own", 3, "Talks hard work as a skill", "yes"),
 "A9hq6KkabAk": ("impact", "own", 2, "Mastermind group promo", "yes"),
 "HmsVCsh0grk": ("impact", "own", 2, "Mentorship program promo", "yes"),
 "rOZ74clpAEA": ("impact", "own", 2, "Super Bowl 52 game-plan promo", "yes"),
 "isjo1tHO2x8": ("other", "own", 2, "Shooting hoops at Baylor", "yes"),
 "ztwMCNe_B3k": ("other", "own", 1, "Kuli Kuli partnership", "yes"),
 "cG0g98thci8": ("other", "own", 1, "Kuli Kuli promo (description says the music isn't owned)", "yes"),
 "iPjJdi2VxU8": ("other", "own", 1, "Kuli Kuli promo part 2 (description says the music isn't owned)", "yes"),
 "3i2VF8R-j7k": ("other", "own", 1, "VET Logistics business story", "yes"),
 "8jvhQmSbQ4I": ("other", "own", 1, "VET Logistics 2", "yes"),
 "6wMbLOxoY6E": ("impact", "own", 2, "Packing okra from the Impact Academy garden", "yes"),
 "9SmAlqdEbto": ("impact", "own", 2, "Short: harvesting okra, Impact Academy garden", "yes"),
 "2WjAgv_wFWo": ("impact", "own", 1, "Impact Academy 'Obama Garden' (relative on camera: get client OK)", "yes"),
 "-CxCiYZhzeY": ("impact", "own", 1, "Picking greens (family on camera: get client OK)", "yes"),
 "cN0cXkyAp1E": ("impact", "own", 1, "Garden zucchini", "yes"),
 "at_nCD7fGGc": ("impact", "own", 1, "Cutting okra (raw clip)", "yes"),
 "fM2GtuZYp64": ("impact", "own", 1, "Pot-garden visit, Sacramento", "yes"),
 # ---------- Coach's own: coachkencarter UCamWLknpkAPEDfD_7RAWPYg ----------
 "PVuW6aQl8YQ": ("torch", "own", 4, "Carries the torch to Richmond City Hall, 2002", "yes"),
 "1GCIavx0HMM": ("tv_news", "own", 4, "'They Call Me Coach': Dr. Phil plus speech montage", "yes"),
 "l-JuG82IsIQ": ("book", "own", 4, "With Rickey Smiley talking about Yes Ma'am No Sir", "yes"),
 "LUv5egNVc90": ("book", "own", 4, "On the book and the Central Texas Barnes & Noble signings", "yes"),
 "bfFMoVGNdgc": ("book", "own", 3, "Book promo: the 12 Essential Steps", "yes"),
 "pGShjPueprM": ("international", "own", 4, "Guatemala speaking tour (sneak peek)", "yes"),
 "iUWk4NWkcww": ("international", "own", 3, "Guatemala tour glimpse", "yes"),
 "gMRD2rtJdu0": ("impact", "own", 4, "Tour of the Coach Carter Impact Academy garden", "yes"),
 "-TOsfWoBzKI": ("impact", "own", 3, "Impact Academy garden tour, part 2", "yes"),
 "linNoPt8YjE": ("impact", "own", 3, "CCIA garden", "yes"),
 # ---------- legacy / program channels (likely his; confirm) ----------
 "P7Fx-EaKC-Y": ("impact", "own_legacy", 3, "2009 'thecoachkencarter': shows Impact Academy and the renovated school", "likely"),
 "kx_O1mGlfI4": ("other", "own_legacy", 2, "2009 free-DVD welcome promo (8.6k views); check for film footage", "likely"),
 "BBgsZHBhKUQ": ("other", "own_legacy", 2, "2009 'CD of the Month' promo", "likely"),
 "HmLJTNwHU74": ("other", "own_legacy", 1, "2009 DVD promo; probably film footage, so don't use", "likely"),
 "sJiOkw5JZsY": ("impact", "own_legacy", 3, "'Book Coach Carter': Real Champions League (his program, Marlin TX)", "likely"),
 "ozxgLbwXu-g": ("impact", "own_legacy", 2, "Success Uncomplicated mastermind promo", "likely"),
 "zgN4Q23BnG8": ("impact", "own_legacy", 2, "Champions League Live, first event in Marlin TX (2017)", "likely"),
 "5diykgYi310": ("other", "own_legacy", 1, "'Coach Ken Carter' channel, 'December 5, 2025' (25 min, no description, 7 views); verify", "check"),
 # ---------- keynotes & speeches (third party) ----------
 "0328uq7KafA": ("keynote", "news", 5, "Full 34-min convocation keynote, MEC PowerPlay 2015 (34k views)", "yes"),
 "pqMlrzAIWO0": ("keynote", "nonprofit", 4, "MEC's own upload of the same 2015 keynote (36 min)", "yes"),
 "3iRDc3WcPOc": ("keynote", "nonprofit", 5, "Life is Beautiful Festival 2015 Ideas talk (19 min, clean stage talk)", "yes"),
 "IYOts4RDNwI": ("keynote", "news", 4, "Back-to-school convocation for 3,000 East Baton Rouge teachers, 2017 (56 min)", "yes"),
 "BB2XDkU4rgw": ("keynote", "nonprofit", 4, "Boys & Girls Clubs of Lanier Be Great Gala keynote, 2022 (full program)", "yes"),
 "sfXi-gXxP9k": ("keynote", "nonprofit", 3, "Biloxi presentation, 2022 (58 min; videographer upload)", "likely"),
 "wMnq-OfTM5g": ("keynote", "nonprofit", 3, "25-min feature, BDYM Media, 2016 (28k views)", "yes"),
 "7bMleQNcOXA": ("keynote", "nonprofit", 3, "Petfood Forum 2022 keynote: team-building tips", "yes"),
 "_-sEGiYJ4pE": ("keynote", "nonprofit", 2, "Petfood Forum 2022 recap", "yes"),
 "vNtLdIkR4dY": ("keynote", "university", 3, "MSU Billings 'Power of One' week, 2012", "yes"),
 "D9XQxQtqT0M": ("keynote", "university", 2, "Univ. of New Mexico SUB Ballroom talk, 2017 (Daily Lobo)", "yes"),
 "j-0ndf17rQQ": ("keynote", "nonprofit", 2, "Gulfstream Student Leadership Program opening, 2013", "yes"),
 "V0ghNyXrEqE": ("keynote", "nonprofit", 2, "AVBOT 2011 with Jim Greenleaf", "yes"),
 "vhOg6ts2m8U": ("keynote", "nonprofit", 1, "Find Your Why Main Event promo, 2007", "yes"),
 "LkA55JZbvaA": ("keynote", "nonprofit", 2, "Rainbow Days Pot of Gold Luncheon invite, 2023", "yes"),
 "lfKdKwfvfRk": ("keynote", "university", 4, "Horry County Schools students, Sep 2026 (most recent school talk)", "yes"),
 "uIUXlwa5PB4": ("keynote", "university", 2, "Lee County School District (SC) visit, 2017", "yes"),
 "jXNRdRaSJio": ("keynote", "nonprofit", 3, "Summerlin Library screening visit, Las Vegas, Oct 2026", "yes"),
 # speakers bureaus
 "CNo95QjAbmE": ("keynote", "bureau", 4, "Eagles Talent: motivational speaker reel (26k views)", "yes"),
 "RP6XynvF1uM": ("keynote", "bureau", 3, "Eagles Talent: inspirational basketball story (17k)", "yes"),
 "i0uHztxfq7o": ("keynote", "bureau", 3, "Eagles Talent: 'in 30 seconds'", "yes"),
 "tlP6T9ZOP-8": ("keynote", "bureau", 4, "TAG Speakers reel (88k views, most-viewed speaker clip)", "yes"),
 "HB--hJZeuw4": ("keynote", "bureau", 3, "TAG Speakers: Coach Carter quotes (15 min)", "yes"),
 "Bl2tvGFQYoM": ("keynote", "bureau", 3, "PDA Speakers (25 min)", "yes"),
 "-eUlPQ88xxU": ("keynote", "bureau", 2, "Brooks International speaker promo, 2012", "yes"),
 # ---------- TV & local news ----------
 "6elk4m5Hsmc": ("tv_news", "news", 5, "Bobbie Wygant Archive (NBC5 Dallas) 2005 film-junket interview, 22 min", "yes"),
 "U03FYmRnw-4": ("tv_news", "news", 3, "KTVO: Ottumwa IA student-athletes, 2022", "yes"),
 "B6tDSDCcjL4": ("tv_news", "news", 3, "WKBN27: Youngstown parents, 2021", "yes"),
 "RxOKHlwuKlI": ("tv_news", "news", 3, "WOAY: Woodrow Wilson HS visit, 2023", "yes"),
 "CQUnLvYzTEs": ("tv_news", "news", 3, "WBRC FOX6: joins GDA, 2023", "yes"),
 "IeZhxa0GdTc": ("tv_news", "news", 3, "Gulf Coast News: SW Florida basketball players, 2019", "likely"),
 "BZxVjjvtHYI": ("tv_news", "news", 2, "Heart of Illinois ABC: IDOT conference, 2020", "yes"),
 "CD-7SgLEqlc": ("tv_news", "news", 2, "KMTV: Omaha Home for Boys gala preview, 2016", "yes"),
 "T5HMJVO36B4": ("tv_news", "news", 3, "KMTV: Coach Ken Carter on the Imagine Our Youth Gala, 2016", "yes"),
 "kpJ4V6VISuI": ("tv_news", "news", 3, "Peoria Journal Star: Caterpillar Juneteenth pep talk, 2008", "yes"),
 "gbW-Xt2tCuo": ("tv_news", "news", 3, "WKTV: Strough Middle School, 2024", "yes"),
 "NN1Zn62SbBw": ("tv_news", "news", 2, "WUTR: preview of the Rome Free Academy visit, 2024", "yes"),
 "OTgiBz4Vpas": ("tv_news", "news", 3, "Herald/Review: Best of Preps event, Jun 2025", "yes"),
 "Ei4oIpYNXo8": ("tv_news", "news", 2, "WLFI-TV 2011 'Coach Carter' speech segment (no description)", "check"),
 "Ve2_mbXGf4g": ("tv_news", "news", 2, "redctv 2012 segment with the book", "likely"),
 "3EUVADgZpuE": ("tv_news", "fan", 2, "'The REAL Coach Carter on Samuel L. Jackson' (fan clip, 16.8k views); find the original", "likely"),
 "z7RNEFLKm6k": ("other", "news", 1, "E! 2004 premiere look-back (Carter on camera not confirmed)", "check"),
 # ---------- interviews & podcasts ----------
 "5vZxM5whfn8": ("interview", "university", 5, "Inside OSU: one-on-one with OSU President Burns Hargis, 2009 (12k views)", "yes"),
 "1eOZwnP6aHc": ("interview", "university", 5, "RFA Knightly News student interview, Mar 2024 (11k views)", "yes"),
 "zG3KQX9KQM8": ("interview", "podcast", 3, "Vatisha King book interview, 2013", "yes"),
 "x5j6e23uZSY": ("interview", "league", 3, "NBL Canada one-on-one, Halifax 2017", "yes"),
 "3nxUCQrD4RQ": ("interview", "university", 3, "KCPS-TV 'The KC Show' interview, 2014 (28 min)", "likely"),
 "IYipVclAezA": ("interview", "podcast", 3, "Josh Tolley Show, book interview, 2012 (28 min)", "yes"),
 "877pLgZq3-c": ("interview", "podcast", 3, "Beyond Big Influence, 'Build your billion dollar brand', 2022 (63 min)", "yes"),
 "u9RIVMpRkcw": ("interview", "podcast", 4, "TDF 'Coach Carter Podcast' highlight: the movie based on his life (36k)", "yes"),
 "Jr1Ii6WwmqU": ("interview", "podcast", 2, "TDF Coach Carter Podcast full episode with K-State's Rodney Perry, 2022", "likely"),
 "VcFdVtiw7Mk": ("interview", "podcast", 2, "TDF 'Coach Carter's One on One' with Rodney Perry", "likely"),
 "tfQyn3LGflQ": ("interview", "podcast", 1, "TDF One on One highlight", "likely"),
 "DocdwmizViM": ("interview", "podcast", 1, "TDF Coach Carter Podcast highlight (teacher pay; co-hosts)", "likely"),
 "HQpz_0HAMjw": ("interview", "podcast", 1, "TDF 'Post-Game with Coach Carter' (K-State); confirm it's Ken", "check"),
 "Z-fIy2VBZWY": ("interview", "podcast", 1, "TDF 'Post-Game with Coach Carter: Baylor at K-State 2023'; confirm", "check"),
 # ---------- Richmond ----------
 "n8beCoP9lc8": ("richmond", "fan", 5, "'The real Coach Carter' documentary pt 1, with Oilers players (1.4M views); likely the DVD featurette, so find the original", "yes"),
 "yzvd3xf6CTE": ("richmond", "fan", 5, "Documentary pt 2 (543k views); same rights caveat", "yes"),
 "g5hHp3r1bLQ": ("richmond", "nonprofit", 2, "STEAM the Streets Richmond event, Nov 2025 (description names him as attending)", "yes"),
 "_yHFz2y_Smw": ("richmond", "news", 2, "Sports360AZ: ex-Oiler Chris Dixon on playing for Carter, 2026", "yes"),
 "fmtiBk2pXPY": ("richmond", "fan", 2, "Fan recap 'Coach Carter 19 years later' (43k)", "likely"),
 "HbvIcc0j6ZA": ("richmond", "fan", 1, "Short: Richmond Oilers, where are they now", "likely"),
 # ---------- SlamBall (official league channel unless noted) ----------
 "kWDLwQ9cjGw": ("slamball", "league", 4, "Season 1 opener, Steal vs 'the Coach Carter-led Rumble' (2002)", "yes"),
 "a0gpD03Q0dU": ("slamball", "league", 4, "Series 1 Championship, Diablos vs Rumble (177k): his 2002 title", "likely"),
 "tv2SFncMLlc": ("slamball", "league", 2, "Series 1 playoffs, Rumble v Steal (93k)", "likely"),
 "SJv56MnJkmI": ("slamball", "league", 2, "Series 1, Rumble vs Mob (683k)", "likely"),
 "XT6GfjmzRy8": ("slamball", "league", 2, "Series 1, Bouncers vs Rumble (347k)", "likely"),
 "2YA2rIuJ6CI": ("slamball", "league", 2, "Series 1, Steal vs Rumble (229k)", "likely"),
 "xKVF240gAN4": ("slamball", "league", 2, "Series 2, Rumble vs Diablos", "likely"),
 "2SFferzp-9w": ("slamball", "league", 2, "Classic Series 2, Rumble vs Mob", "likely"),
 "K5_2rf83RUI": ("slamball", "league", 3, "'Rumble Throughout the Years'", "likely"),
 "rMhc1Fp1k_Q": ("slamball", "league", 2, "Short: the Rumble through the years", "likely"),
 "LZDInYPw-Yo": ("slamball", "league", 4, "First SlamBall game in a decade (2023): Mob vs Rumble, 'the real Coach Carter at the helm'", "yes"),
 "JjkKInUhopM": ("slamball", "league", 3, "2023 opener full game, Rumble vs Mob", "likely"),
 "i95eMrnm5rM": ("slamball", "league", 4, "ESPN: Rumble and Coach Carter's first 2023 win (16k)", "yes"),
 "PxXdpLazyws": ("slamball", "league", 2, "Rumble walk-off winner, full 4th quarter (2023)", "likely"),
 "MaBiZ_Qz9WY": ("slamball", "fan", 2, "'Coach Carter and the Rumble', week 6, 2008 season (fan upload)", "yes"),
 "CnJO9aOKgwY": ("slamball", "podcast", 2, "Bounce Off podcast: Rumble 2023 preview, Carter returns", "yes"),
 # ---------- book ----------
 "57vBgem-SFU": ("book", "publisher", 3, "Google Play audiobook preview, narrated by Coach Carter", "yes"),
 "G4RzgxeJi9o": ("book", "publisher", 1, "Narrator in the booth, ListenUp Audiobooks", "yes"),
 # ---------- other ----------
 "BzcCLcSjr2M": ("other", "fan", 1, "Endorses Ed Zimbardi, 2015", "yes"),
 "7VWVLq17FJo": ("other", "fan", 1, "Author And Grow Rich promo naming him, 2008 (he may not appear)", "check"),
 "EhjKfL8OTrs": ("other", "podcast", 1, "Robert Ri'chard says the real Carter picked him (about him, not featuring him)", "yes"),
}

FILM_OWNED_BEHIND = {"aAsI_WOCYv0": "Behind the Scenes (1), LLL920 re-upload of Paramount EPK",
                     "Hl05uxy_tyA": "Behind the Scenes (2), LLL920 re-upload of Paramount EPK",
                     "ITexjlHujj8": "2005 TV commercial", "levuMVaUZeM": "film AMV"}
# Possible piracy of his book's audiobook (report to publisher, do not link)
PIRACY = ["0Qc9iaE6Bk8", "pQpJc2qcDOI", "kN1LxNn5RVg"]
# Not him (other Ken/Coach Carters) or unverified same-name coaches
NOT_HIM = {
 "xwkhSznoV0I": "Kenneth Carter, Delaware State football", "gDKjmYkFqcs": "Delaware State football",
 "Jcrr6ZUTXqg": "Delaware State football", "GPGRWecxeLI": "Delaware State football",
 "KjKitS2YdIg": "Alonzo Carter (Contra Costa College football, the 'dancing coach')",
 "8nslOqExKxI": "Gary Carter", "5MkRGJUn8Lc": "a different high school coach (Oak Mountain)",
 "uJ8SsUkKc0k": "Heavyn Carter", "udtFmAvTxxc": "'Coach Carter' channel UCX6fv… (cosplay/ShoutShow uploads, a different person)",
 "TQEaJSZYyz0": "Teach Hoops 'Coach Carter' 3-part interview (2026): unverified, channel also has Jason Carter",
 "fGNcSiXQKXk": "Underdog Hoops 'Coach Carter' interviews: unverified, channel also has Ametrius Carter",
 "HErcEtUz-DI": "Coaches Table 'coach Carter': unverified", "NNrEL9i9Mgk": "Spanish 'documental' re-upload (245k): unverified",
 "Rjc2IibQwKE": "Kenneth Carter, DSU football", "EJbbMasBSGY": "Kenneth Carter, Emory psychologist (TEDx)",
 "0dfmDM1ps6w": "Ken Carter, 'Mad Canadian' stuntman", "l895Qviyzpg": "stuntman Ken Carter",
 "Njf6_xF-WiQ": "Bishop Ken Carter (UMC)", "jovK7zHPj2Q": "student class project about him",
}

NONYT = [
 {"id": "nbcbayarea-2018-01-11", "title": "'Coach Carter' Reunited With Former Students at Richmond High (Sergio Quintana)",
  "url": "https://www.nbcbayarea.com/on-air/as-seen-on/reunited-with-former-students-at-richmond-high_bay-area/57094/",
  "platform": "nbcbayarea.com", "channel": "NBC Bay Area (KNTV)", "upload_date": "20180111", "category": "richmond",
  "owner_type": "news", "rank": 4, "note": "Bay Area TV news: reunion with former players and launch of his speaking 'second chapter'", "verified": "yes",
  "embeddable": "link-out (station player)"},
 {"id": "tvarchive-KNTV_20180112_070000", "title": "NBC Bay Area News at 11, 2018-01-12 (same story, TV News Archive captions)",
  "url": "https://archive.org/details/KNTV_20180112_070000_NBC_Bay_Area_News_at_11#start/688/end/1032",
  "platform": "archive.org TV News", "channel": "Internet Archive TV News", "upload_date": "20180112", "category": "richmond",
  "owner_type": "news", "rank": 2, "note": "Research copy only (TV News Archive clips are fair-use research, not for the site)", "verified": "yes", "embeddable": "research only"},
 {"id": "archive-cojaxfl-33rd_Annual_MLK_Breakfast", "title": "City of Jacksonville 33rd Annual MLK Breakfast (Coach Ken Carter keynote), 2020",
  "url": "https://archive.org/details/cojaxfl-33rd_Annual_MLK_Breakfast", "platform": "archive.org", "channel": "City of Jacksonville community media",
  "upload_date": "20200117", "category": "keynote", "owner_type": "nonprofit", "rank": 3,
  "note": "Government community-media upload; the description says Carter 'brought the house down'", "verified": "yes", "embeddable": "archive.org embed"},
 {"id": "archive-kcrtca-RPAL", "title": "KCRT NewsBytes: RPAL 'With PAL' music video release (features Coach Ken Carter), 2024",
  "url": "https://archive.org/details/kcrtca-KCRT_s_NewsBytes_-_RPAL_Music_Video_Release", "platform": "archive.org",
  "channel": "KCRT (City of Richmond TV)", "upload_date": "20240820", "category": "richmond", "owner_type": "news", "rank": 3,
  "note": "City of Richmond TV, Richmond PAL youth: a pre-return Richmond appearance", "verified": "yes", "embeddable": "archive.org embed"},
 {"id": "archive-Insight_060511", "title": "Capital Public Radio 'Insight': the real Coach Ken Carter (AUDIO), 2006",
  "url": "https://archive.org/details/Insight_060511", "platform": "archive.org (audio)", "channel": "KXJZ Capital Public Radio",
  "upload_date": "20060511", "category": "interview", "owner_type": "news", "rank": 2, "note": "Audio only: radio interview on the movie's impact", "verified": "yes", "embeddable": "archive.org audio embed"},
 {"id": "archive-Insight-130111", "title": "Capital Public Radio 'Insight': segment on Coach Carter (AUDIO), 2013",
  "url": "https://archive.org/details/Insight-130111a", "platform": "archive.org (audio)", "channel": "KXJZ Capital Public Radio",
  "upload_date": "20130111", "category": "interview", "owner_type": "news", "rank": 1, "note": "Audio; Carter segment not confirmed", "verified": "check", "embeddable": "archive.org audio embed"},
 {"id": "vimeo-681468154", "title": "cityCURRENT Virtual Signature Event: Coach Ken Carter (2022)",
  "url": "https://vimeo.com/681468154", "platform": "vimeo", "channel": "cityCURRENT (via citycurrent.com)", "upload_date": "2022",
  "category": "keynote", "owner_type": "nonprofit", "rank": 2, "note": "Vimeo oEmbed returns 404 (private/removed); the event page lists it", "verified": "check", "embeddable": False},
 {"id": "audible-B0DR9YZDN7", "title": "Podcast episode 'Coach Ken Carter' (AUDIO, 2024-12-23)",
  "url": "https://origin-www.audible.fr/podcast/Coach-Ken-Carter/B0DR9YZDN7", "platform": "Audible", "channel": "podcast",
  "upload_date": "20241223", "category": "interview", "owner_type": "podcast", "rank": 1, "note": "Audio only; aired the week of his Richmond return", "verified": "likely", "embeddable": "link-out"},
 {"id": "buzzsprout-heartoftheathlete-16341962", "title": "Heart of the Athlete (FCA Idaho): Coach Ken Carter (AUDIO)",
  "url": "https://heartoftheathlete.buzzsprout.com/2163946/episodes/16341962-coach-ken-carter", "platform": "Buzzsprout", "channel": "FCA Idaho",
  "upload_date": "", "category": "interview", "owner_type": "podcast", "rank": 1, "note": "Audio podcast", "verified": "likely", "embeddable": "buzzsprout embed"},
 {"id": "ccpulse-2024-12-16", "title": "CC Pulse: Coach Carter Returns to Lead Richmond High After More Than 20 Years (article + photos, no video found)",
  "url": "https://ccpulse.org/2024/12/16/coach-carter-returns-to-lead-richmond-high-after-more-than-20-years",
  "platform": "ccpulse.org", "channel": "Community Pulse", "upload_date": "20241216", "category": "richmond", "owner_type": "news", "rank": 2,
  "note": "Only public coverage of the Dec 2024 return found; no TV video of the return turned up", "verified": "yes", "embeddable": "link-out"},
]

TOP15 = [
 ("3-57R3Oanfw", "Owned career-highlights trailer: the ideal hero video"),
 ("VkpVPjp-_F8", "Owned speaker reel: the booking page anchor"),
 ("28kzO577IVw", "Owned Dr. Phil clip: national TV credibility"),
 ("TReXvx2yseU", "Owned 2002 Olympic torch footage: unique milestone"),
 ("0328uq7KafA", "Full 34-min keynote, 34k views: shows the complete talk"),
 ("3iRDc3WcPOc", "Clean 19-min festival talk (Life is Beautiful 2015): best-produced speech"),
 ("6elk4m5Hsmc", "2005 film-junket interview: Carter in his own words at the film's release"),
 ("5vZxM5whfn8", "University president one-on-one (OSU 2009): authority and context"),
 ("1eOZwnP6aHc", "2024 student interview, 11k views: recent, youth-facing"),
 ("lfKdKwfvfRk", "Sep 2026 school talk: proves he's active now"),
 ("kWDLwQ9cjGw", "SlamBall 2002 Season 1, explicitly 'Coach Carter-led Rumble'"),
 ("i95eMrnm5rM", "ESPN 2023: Rumble and Coach Carter win, big-network proof of the comeback"),
 ("pGShjPueprM", "Owned Guatemala tour: international reach"),
 ("l-JuG82IsIQ", "Owned Rickey Smiley + book: media + Yes Ma'am No Sir"),
 ("gMRD2rtJdu0", "Owned Impact Academy garden tour: the Foundation/Academy story"),
]

KNOWN = {"VkpVPjp-_F8", "28kzO577IVw", "TReXvx2yseU", "PVuW6aQl8YQ", "l-JuG82IsIQ", "0328uq7KafA", "1eOZwnP6aHc",
         "n8beCoP9lc8", "yzvd3xf6CTE"}
KNOWN_CHANNELS = {"UCkq8ZF3PXaOsHDjgxggkrBg", "UCamWLknpkAPEDfD_7RAWPYg"}

FILM_RE = re.compile(r"movieclips|boxoffice|binge society|now (playing|action)|krey'?s clips|movientação|scene|clip|"
                     r"cinemix|benz tv|movietheather|quotedmovie|paramount|mtv", re.I)


def oembed(vid):
    try:
        with urllib.request.urlopen(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json", timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def main():
    raw = {r["id"]: r for r in json.load(open(f"{BASE}/raw_search.json"))}
    chan = {}
    for f in glob.glob(f"{BASE}/channels/*.json"):
        for r in json.load(open(f)):
            chan.setdefault(r["id"], r)
    meta = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{BASE}/meta/*.json")}
    out = []
    for vid, (cat, own, rank, note, ver) in C.items():
        m, fl = meta.get(vid, {}), raw.get(vid) or chan.get(vid) or {}
        status = m.get("oembed_status") or oembed(vid)
        cid = m.get("channel_id") or fl.get("channel_id") or ""
        src = "known" if (vid in KNOWN or cid in KNOWN_CHANNELS) else "new"
        out.append({
            "id": vid, "platform": "youtube", "url": f"https://www.youtube.com/watch?v={vid}",
            "title": m.get("title") or fl.get("title"), "channel": m.get("channel") or fl.get("channel"),
            "channel_id": cid, "upload_date": m.get("upload_date"), "duration": m.get("duration") or fl.get("duration"),
            "view_count": m.get("view_count") or fl.get("view_count"), "category": cat, "owner_type": own,
            "rights": RIGHTS[own], "rank": rank, "note": note, "verified": ver,
            "embeddable": status == 200 and m.get("playable_in_embed") is not False, "oembed_status": status,
            "source": src, "top15": vid in dict(TOP15),
        })
    for n in NONYT:
        out.append({**n, "rights": RIGHTS[n["owner_type"]], "source": "new", "top15": False})
    out.sort(key=lambda x: ([c for c, _ in CATS].index(x["category"]), -x["rank"], x.get("upload_date") or ""))
    excluded = {
        "film_owned_do_not_use": [], "possible_audiobook_piracy": [], "not_him_or_unverified": [],
    }
    # film-owned: Coach Carter titles from film/clip channels in the sweep
    film = [r for r in raw.values() if "carter" in (r["title"] or "").lower() and r["id"] not in C
            and (r.get("film_channel") or FILM_RE.search(r["channel"] or "") or r["id"] in FILM_OWNED_BEHIND)]
    for r in sorted(film, key=lambda r: -(r.get("view_count") or 0)):
        excluded["film_owned_do_not_use"].append({"id": r["id"], "title": r["title"], "channel": r["channel"],
                                                   "view_count": r.get("view_count")})
    for vid, why in FILM_OWNED_BEHIND.items():
        if not any(x["id"] == vid for x in excluded["film_owned_do_not_use"]):
            r = raw.get(vid) or chan.get(vid) or {}
            excluded["film_owned_do_not_use"].append({"id": vid, "title": r.get("title"), "channel": r.get("channel"), "note": why})
    for vid in PIRACY:
        r = raw.get(vid, {})
        excluded["possible_audiobook_piracy"].append({"id": vid, "title": r.get("title"), "channel": r.get("channel")})
    for vid, why in NOT_HIM.items():
        r = raw.get(vid) or chan.get(vid) or meta.get(vid) or {}
        excluded["not_him_or_unverified"].append({"id": vid, "title": r.get("title"), "channel": r.get("channel"), "reason": why})
    json.dump({"generated": "2026-11-09", "videos": out, "excluded": excluded}, open(f"{BASE}/videos.json", "w"), indent=1)
    write_md(out, excluded)
    c = Counter(x["category"] for x in out)
    print("total", len(out), dict(c), "known", sum(x["source"] == "known" for x in out),
          "film_owned", len(excluded["film_owned_do_not_use"]), "not_him", len(excluded["not_him_or_unverified"]))


def fmt_dur(d):
    if not d:
        return ""
    d = int(d)
    return f"{d//3600}:{d%3600//60:02d}:{d%60:02d}" if d >= 3600 else f"{d//60}:{d%60:02d}"


def fmt_date(s):
    return f"{s[:4]}-{s[4:6]}-{s[6:]}" if s and len(s) == 8 else (s or "")


def esc(s):
    return (str(s or "")).replace("|", "/")


def write_md(out, excluded):
    byid = {x["id"]: x for x in out}
    L = ["# Coach Ken Carter: public video inventory", "",
         "Generated 2026-11-09 by `tools/investigate/` (yt_sweep → channel_dump → enrich → build_inventory). "
         "Public professional record only; no logins used. The machine-readable copy is `videos.json`.", "",
         "**Rights key:** own = usable · own? = probably his, confirm · news/university/org/bureau/league/podcast = embed only · "
         "fan = rights unclear · film = do not use. **Verified:** yes = title/description names him · likely = strong context · check = watch before use.", "",
         f"**Totals:** {len(out)} relevant items ({sum(x['platform']=='youtube' for x in out)} YouTube, "
         f"{sum(x['platform']!='youtube' for x in out)} elsewhere) · {sum(x['owner_type']=='own' for x in out)} on his own channels · "
         f"{sum(x['source']=='new' for x in out)} new vs. the known list · all YouTube items embeddable (oEmbed 200) unless marked.", "",
         "## Top 15 for the website", "", "| # | Video | Channel | Year | Rights | Why |", "|---|---|---|---|---|---|"]
    for i, (vid, why) in enumerate(TOP15, 1):
        x = byid[vid]
        L.append(f"| {i} | [{esc(x['title'])}]({x['url']}) `{vid}` | {esc(x['channel'])} | {fmt_date(x.get('upload_date'))[:4]} | {x['owner_type']} | {why} |")
    L += ["", "Gap: no video of the **Dec 2024 Richmond return** turned up on YouTube, the Bay Area TV archive or the web "
          "(only the CC Pulse article). The closest are NBC Bay Area's Jan 2018 Richmond reunion and KCRT's Aug 2024 RPAL piece. "
          "The 1999 Today show, Oprah, Best Damn Sports Show and Prince appearances have no public video online; ask the client for his own tapes.", ""]
    own_lbl = {"own": "own", "own_legacy": "own?", "news": "news", "university": "school/univ", "nonprofit": "org/event",
               "bureau": "bureau", "league": "league", "podcast": "podcast", "publisher": "publisher", "fan": "fan", "film": "film"}
    for key, label in CATS:
        rows = [x for x in out if x["category"] == key]
        if not rows:
            continue
        L += [f"## {label} ({len(rows)})", "", "| ★ | Video | Channel | Date | Len | Views | Owner | Emb | Ver | Src | Note |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in rows:
            emb = "✓" if x["embeddable"] is True else ("✗" if x["embeddable"] is False else esc(x["embeddable"]))
            L.append(f"| {'★'*x['rank']} | [{esc(x['title'])}]({x['url']}) | {esc(x['channel'])} | {fmt_date(x.get('upload_date'))} | "
                     f"{fmt_dur(x.get('duration'))} | {x.get('view_count') or ''} | {own_lbl[x['owner_type']]} | {emb} | {x['verified']} | "
                     f"{x['source']} | {esc(x['note'])} |")
        L.append("")
    fo = excluded["film_owned_do_not_use"]
    L += ["## Film-owned clips (do not use)", "",
          f"{len(fo)} 'Coach Carter' film clips, scenes, trailers, EPK re-uploads and film reviews/reactions surfaced in the sweep (built on studio footage). Main channels: " +
          ", ".join(f"{c} ({n})" for c, n in Counter(x["channel"] for x in fo).most_common(12)) + ". The full list is in `videos.json → excluded`.", "",
          "## Possible audiobook piracy (report to the publisher, don't link)", ""]
    L += [f"- `{x['id']}` {esc(x['title'])} ({esc(x['channel'])})" for x in excluded["possible_audiobook_piracy"]]
    L += ["", "## Not him / unverified same-name results (excluded)", ""]
    L += [f"- `{x['id']}` {esc(x['title'])}: {x['reason']}" for x in excluded["not_him_or_unverified"]]
    L += ["", "## Sources checked", "",
          "- YouTube: 70 `ytsearch40` queries (1,444 unique hits); full upload lists of 17 channels (his 2 known + 3 candidate own channels, "
          "Eagles Talent, TAG Speakers, Louisiana Hometown, Petfood Forum, TDF Network, Bounce Off, LLL920, Teach Hoops, Underdog Hoops, "
          "SlamBall official, SlamBall Europe); full metadata + oEmbed for 147 candidates.",
          "- Internet Archive advancedsearch (4 queries) + TV News Archive captions via the GDELT TV API (SF Bay Area + national, 2009–2026).",
          "- Web search: Vimeo, C-SPAN (only floor speeches mentioning the film, no Carter appearance), Facebook/Instagram/TikTok (nothing indexed), "
          "Bay Area news on the 2024 return, podcasts.",
          "- YouTube started bot-checking full-metadata requests near the end. Items marked `check` were not watched; "
          "no cookies or logins were used, by design.", ""]
    open(f"{BASE}/VIDEOS.md", "w").write("\n".join(L))


if __name__ == "__main__":
    main()
