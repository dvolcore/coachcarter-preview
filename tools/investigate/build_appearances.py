#!/usr/bin/env python3
"""Build tracking/investigation/appearances.json + APPEARANCES.md for "The Record".

Data below was compiled 2026-11-09 from: podcast_sweep.py (iTunes API), imdb_credits.py,
wayback_coachcarter.py / wayback_fetch.py (Coach's own coachcarter.com 2000-2011),
archive.org advancedsearch, getty_hits.json + VIDEOS.md (sibling video/photo sweep),
and WebSearch/WebFetch research passes (press + speaking). Public record only.

Confidence: verified = a primary/public page documents it; likely = strong but indirect
(self-reported bio/CV, bibliography, search snippet, page blocked); unverified = claim only.
Run: python3 build_appearances.py
"""
import json, os
from collections import Counter

OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"
WB = "https://web.archive.org/web/"
CV09 = WB + "20091227040746/http://coachcarter.com:80/about/curriculum-vitae/"
CV02 = WB + "20020110013710/http://coachcarter.com:80/pages/about_vitae.html"
PH02 = WB + "20020314003746/http://coachcarter.com:80/Photos/list.html"
MED04 = WB + "20041204032200/http://www.coachcarter.com:80/media.htm"
MOV04 = WB + "20041216222008/http://www.coachcarter.com:80/moviemedia.htm"
YT = "https://www.youtube.com/watch?v="
V, L, U = "verified", "likely", "unverified"

# ---------------------------------------------------------------- TV & radio
# (date, outlet/show, title/what, url, confidence, note, known)
TV = [
 ("1999-01-07", "CNN", "National report on the lockout", "https://www.cnn.com/US/9901/07/team.lockout/", V, "", True),
 ("1999-01-11", "NPR", "National radio interview the week of the lockout", "https://www.npr.org/1999/01/11/1031779/coach", V, "", True),
 ("1999-01", "NBC — The Today Show (with Katie Couric)", "Network morning-show appearance", CV02, L, "Coach's own 2002 CV names Katie Couric; SFGate 2004-12-31 confirms Today + GMA appearances", False),
 ("1999-01", "ABC — Good Morning America", "Network morning-show appearance", "https://www.sfgate.com/bayarea/article/Coach-s-successes-leave-team-behind-Hollywood-2660624.php", L, "SFGate (2004) + SFGate 1999-01-12 say he appeared on Today and GMA", False),
 ("1999-01-11", "ABC World News Tonight with Peter Jennings", "Judy Muller report 'Hoop Dreams and GPAs'", WB + "20041103015806/http://www.coachcarter.com:80/abcnews.htm", L, "ABCNEWS.com text (by Judy Muller) archived on coachcarter.com; CV says 'featured on the Evening News with Peter Jennings'", False),
 ("1999-01", "KTVU Fox 2 — Mornings on 2 (Ross McGowan)", "Bay Area morning show interview", CV02, L, "Self-reported in 2002 CV", False),
 ("1999-01", "KRON-TV NewsCenter4 DayBreak (Dionne Anglin)", "Bay Area morning news interview", CV02, L, "Self-reported in 2002 CV", False),
 ("1999-02", "The Rush Limbaugh Show / The Limbaugh Letter", "Interview with Rush Limbaugh (transcript printed Feb 1999 Limbaugh Letter)", WB + "20041209125442/http://www.coachcarter.com:80/limbaughltr.htm", V, "Limbaugh called it 'one of the most inspiring' interviews; also cited by George Fox Journal 2005", False),
 ("2001-2002", "California Lottery — The Big Spin (TV)", "Appearance at the California Lottery Big Spin", PH02, L, "Photo caption #26 on Coach's 2002 site; tied to the Lottery/Gray Davis Heroes in Education award", False),
 ("2002-08-03", "SlamBall (TNN/Spike TV series, 2002–2003)", "Head coach, Rumble — on-air credits", "https://www.imdb.com/title/tt0337560/", V, "IMDb lists him as Actor ('Rumble Coach') and Self on the series; Rumble won the 2002 title", False),
 ("2005-01-06", "Dr. Phil (syndicated)", "With Samuel L. Jackson", YT + "28kzO577IVw", V, "Getty 'Samuel L. Jackson Visits the Dr. Phil Show – January 6, 2005' confirms", True),
 ("2005", "Paramount DVD — 'Coach Carter: The Man Behind the Movie'", "19-min documentary featurette, credited as Self", "https://www.imdb.com/title/tt8021926/", V, "IMDb Self credit (one of his only 2 'Self' credits; the other is SlamBall)", False),
 ("2005-01", "NBC5 Dallas — Bobbie Wygant", "22-min film-junket interview", YT + "6elk4m5Hsmc", V, "Bobbie Wygant Archive upload", False),
 ("2006-05-11", "Capital Public Radio (KXJZ) — Insight", "The real Coach Ken Carter on raising kids and the film's impact", "https://archive.org/details/Insight_060511", V, "archive.org audio", False),
 ("2008-06-27", "Peoria Journal Star (video)", "Caterpillar Juneteenth pep talk", YT + "kpJ4V6VISuI", V, "", False),
 ("2009-01-29", "Inside OSU (Oklahoma State University TV)", "One-on-one with OSU President Burns Hargis", YT + "5vZxM5whfn8", V, "", False),
 ("2011-01-18", "WLFI-TV (Lafayette, IN)", "'Coach Carter' speech segment", YT + "Ei4oIpYNXo8", U, "No description; watch to confirm", False),
 ("2012-02-21", "The Josh Tolley Show", "Book interview — Yes Ma'am, No Sir (28 min)", YT + "IYipVclAezA", V, "", False),
 ("2012", "Rickey Smiley (radio)", "Rickey Smiley and Coach Carter talk Yes Ma'am, No Sir", YT + "l-JuG82IsIQ", L, "Uploaded to Coach's own channel; show/date not stated", False),
 ("2013-01-11", "Capital Public Radio (KXJZ) — Insight", "Segment ahead of his Sacramento MLK keynote", "https://archive.org/details/Insight-130111", V, "Description names him as keynote of the 14th annual MLK event", False),
 ("2013-07-10", "Vatisha King (interview show)", "Interview about Yes Ma'am, No Sir", YT + "zG3KQX9KQM8", V, "", False),
 ("2014-01-24", "KCPS-TV — The KC Show with Kim Chexnayder", "28-min interview (Kansas City Public Schools TV)", YT + "3nxUCQrD4RQ", V, "", False),
 ("2016-08-31", "KMTV 3 News Now (Omaha)", "Coach Carter on the Imagine Our Youth Gala", YT + "T5HMJVO36B4", V, "", False),
 ("2017", "CBC News (Nova Scotia)", "Nova Scotia tour", "", V, "", True),
 ("2017-02-14", "NBL Canada", "One-on-One with Coach Carter (Halifax)", YT + "x5j6e23uZSY", V, "", False),
 ("2018-01-11", "NBC Bay Area", "'Coach Carter' reunited with former students at Richmond High", "https://www.nbcbayarea.com/news/local/coach-carter-reunited-with-former-students-at-richmond-high/57093/", V, "", False),
 ("2018-06-14", "KFDA NewsChannel 10 (Amarillo)", "Speaks with Amarillo youth on education", "https://www.newschannel10.com/story/38430123/coach-ken-carter-speaks-with-amarillo-youth-on-education/", V, "", False),
 ("2019", "WINK News (Fort Myers)", "Life lessons", "", V, "", True),
 ("2019-10-06", "Gulf Coast News (SW Florida)", "Speaks to Southwest Florida basketball players", YT + "IeZhxa0GdTc", L, "18k views", False),
 ("2020-02-11", "Heart of Illinois ABC (WHOI)", "Game plan of success at IDOT conference", YT + "BZxVjjvtHYI", V, "", False),
 ("2021", "WYTV (Youngstown)", "Youngstown City Schools", "", V, "", True),
 ("2021-10-22", "WKBN 27 (Youngstown)", "Speaks to Youngstown parents about student success", YT + "B6tDSDCcjL4", V, "", False),
 ("2022-10-21", "KTVO (Ottumwa, IA)", "Talks to student-athletes", YT + "U03FYmRnw-4", V, "", False),
 ("2023", "WEAR-TV (Pensacola)", "Escambia County teacher kickoff", "", V, "", True),
 ("2023", "KRCR (Redding)", "Coach Carter Experience, Corning/Red Bluff", "", V, "", True),
 ("2023-07-21", "ESPN (SlamBall relaunch)", "Rumble win season opener — full-game highlights", YT + "i95eMrnm5rM", V, "Also USA Today / Fox News coverage of SlamBall return", False),
 ("2023-08-15", "WBRC FOX6 (Birmingham)", "Coach Ken Carter joined GDA", YT + "CQUnLvYzTEs", V, "", False),
 ("2023-08-18", "WOAY-TV (Oak Hill/Beckley, WV)", "Visit to Woodrow Wilson High School", YT + "RxOKHlwuKlI", V, "", False),
 ("2024-02-27", "WKTV NewsChannel 2 / WUTR Eyewitness News (Utica)", "Rome Free Academy + Strough visits", YT + "gbW-Xt2tCuo", V, "Also " + YT + "NN1Zn62SbBw", False),
 ("2024-08-20", "KCRT (Richmond city TV)", "'With PAL' music video featuring Coach Ken Carter, Richmond PAL", "https://archive.org/details/kcrtca-KCRT_s_NewsBytes_-_RPAL_Music_Video_Release", V, "With Richmond Police Chief Bisa French", False),
 ("2024-12-23", "KSPD 790 AM / 94.5 FM — Here We Have Idaho", "Coach Ken Carter (radio show, also podcast)", "https://www.buzzsprout.com/2367617/episodes/16332557-coach-ken-carter", V, "", False),
 ("2025-06-10", "Herald/Review Media (Sierra Vista, AZ)", "Interview after Best of Preps", YT + "OTgiBz4Vpas", V, "", False),
 ("2026-04", "ABC57 (South Bend) — Brian Conybeare", "Interview ahead of Family & Children's Center Spotlight Dinner", "https://www.abc57.com/news/the-real-life-coach-carter-was-interviewed-by-brian-conybeare", V, "", False),
 ("2026-10-16", "News 3 Las Vegas (KSNV)", "Visits Las Vegas to talk leadership and academics", "https://news3lv.com/news/local/coach-carters-ken-carter-visits-las-vegas-to-talk-leadership-and-academics", V, "Says a new Coach Carter project to film in 2027", False),
]

# ---------------------------------------------------------------- podcasts
PODS = [
 ("2016-12", "ASI Strategy Session (podcast)", "Coach Ken Carter: Powered by the Positive", "https://members.asicentral.com/news/web-exclusive/december-2016/coach-ken-carter-powered-by-the-positive/", V, "", False),
 ("2021-10-21", "21 WFMJ News Podcast", "Famed Coach Ken Carter joins YCSD to promote parent engagement", "https://podcasts.apple.com/us/podcast/famed-coach-ken-carter-joins-ycsd-to-promote-parent/id1503584888?i=1000539337118", V, "Anchor Derek Steyer", False),
 ("2021-11-11", "Alternate Take (Danny)", "#35 – 'Coach Carter' Richmond High Basketball Coach – Ken \"Coach\" Carter", "https://podcasts.apple.com/us/podcast/35-coach-carter-richmond-high-basketball-coach-ken/id1455108634?i=1000541513256", V, "Long-form: McComb upbringing, contracts, lockout", False),
 ("2022-07-24", "Beyond Big Influence", "Build Your Billion Dollar Brand – Coach Carter", "https://podcasts.apple.com/us/podcast/build-your-billion-dollar-brand-coach-carter/id1652833356?i=1000584896083", V, "63-min video version " + YT + "877pLgZq3-c", False),
 ("2022-08-28", "TDF Network — 'Coach Carter Podcast'", "The Real Coach Carter Talks About The Movie Based On His Life (highlight)", YT + "u9RIVMpRkcw", L, "36k views; co-hosts Aleece Desiree, Big Bob, Rodney Perry; other TDF 'Coach Carter' K-State episodes may be a different Coach Carter — confirm", False),
 ("2024-12-23", "Here We Have Idaho (KSPD)", "Coach Ken Carter", "https://podcasts.apple.com/us/podcast/coach-ken-carter/id1752713045?i=1000681493407", V, "Radio show + podcast", False),
 ("2024-12-28", "Heart of the Athlete (FCA Idaho)", "Coach Ken Carter", "https://podcasts.apple.com/mw/podcast/coach-ken-carter/id1329804276?i=1000681955037", V, "", True),
 ("2012", "Hachette Audio (audiobook)", "Yes Ma'am, No Sir — narrated by Vince Bailey and Coach Carter", "https://www.hachettebookgroup.com/contributor/coach-carter/", V, "iTunes 'podcast' feeds offering this audiobook look like piracy — don't link", False),
 ("2021-05-17", "Reel Talk Extra (RTX)", "Coach Carter | Beyond Self Preservation (discussion ABOUT him, not a guest spot)", "https://podcasts.apple.com/us/podcast/coach-carter-beyond-self-preservation/id1550687625?i=1000521961874", U, "Not an appearance; listed so it isn't re-researched", False),
]

# ---------------------------------------------------------------- press (new)
# (date, outlet, title, author, url, confidence, summary)
PRESS = [
 ("1999-01-08", "San Francisco Chronicle", "Coach scores points for academics", "", "https://www.sfgate.com/news/article/Coach-scores-points-for-academics-3240562.php", L, "Early Chronicle account, p. A19"),
 ("1999-01-10", "Los Angeles Times", "A Textbook Play", "", "https://www.latimes.com/archives/la-xpm-1999-jan-10-mn-62258-story.html", L, "Separate from the known 1/12 story"),
 ("1999-01-11", "ABCNEWS.com", "Hoop Dreams and GPAs", "Judy Muller", WB + "20041103015806/http://www.coachcarter.com:80/abcnews.htm", V, "Network story; text archived on Coach's site"),
 ("1999-01-12", "San Francisco Chronicle", "Richmond Rebound / players hit books, coach lifts his lockout", "Sam McManis", "https://www.sfgate.com/education/article/Richmond-Rebound-High-school-basketball-players-2952622.php", L, "Lockout ends; library tutoring"),
 ("1999-01", "San Francisco Chronicle", "Winning Hoopsters Benched For Sloughing Off on Studies", "", "https://www.sfchronicle.com/sports/article/Winning-Hoopsters-Benched-For-Sloughing-Off-on-2953673.php", L, ""),
 ("1999-01-13", "Deseret News (AP)", "Team hits books, returns to court", "AP", "https://www.deseret.com/1999/1/13/19423064/team-hits-books-returns-to-court/", V, "Return win 61–51 with Gov. Gray Davis in the crowd"),
 ("1999-01-13", "Standard-Times / SouthCoast Today (AP)", "Calif. coach ends lockout", "AP", "https://www.southcoasttoday.com/story/sports/1999/01/13/calif-coach-ends-lockout/50535241007/", L, "Wire pickup"),
 ("1999-01-25", "People", "Give Me an A!", "", WB + "20041204032200/http://www.coachcarter.com:80/peoplemag.htm", V, "People p. 92; full text archived on Coach's site"),
 ("1999-02", "The Limbaugh Letter", "Interview with Ken Carter", "Rush Limbaugh", WB + "20041209125442/http://www.coachcarter.com:80/limbaughltr.htm", V, "Q&A transcript"),
 ("2000-03-01", "San Francisco Chronicle", "MAKING THE GRADE / Some improvement seen at Richmond High", "", "https://www.sfgate.com/sports/article/MAKING-THE-GRADE-Some-improvement-seen-at-3304689.php", L, "p. E1"),
 ("2001-06-12", "Oakland Tribune", "Scholar-athletes Taste Success", "Dave Newhouse", WB + "20041209144518/http://www.coachcarter.com:80/oaktribune.htm", V, "Lockout players' college scholarships"),
 ("2001-07", "Endless Possibilities", "Coach Ken Carter Shows His Players Much Tough Love!", "", MED04, L, "Listed on Coach's 2004 media page"),
 ("2001-07-14", "San Francisco Chronicle", "Richmond coach proved right / 6 benched to study are now in college", "Chip Johnson", "https://www.sfgate.com/bayarea/johnson/article/Richmond-coach-proved-right-6-benched-to-study-2900017.php", L, "Column, p. A15"),
 ("2002-06-13", "The Hollywood Reporter", "Writer Schwahn, Par' get Carter", "Zorianna Kit", WB + "20041027141540/http://www.coachcarter.com:80/reporter_article2.htm", V, "Front page: Paramount/MTV Films/Tollin-Robbins buy his life rights"),
 ("2003-08-25", "The Hollywood Reporter", "Jackson may take 'Day' job for Paramount", "", MOV04, L, "Jackson attached"),
 ("2003-09-08", "Sports Illustrated", "Sports Beat item (p. 36)", "", WB + "20041028032738/http://www.coachcarter.com:80/sportsillusrt-art.htm", L, "Listed on Coach's movie-media page"),
 ("2004-01-05", "The Hollywood Reporter", "Ashanti Gets 'Carter' for First Film", "", MOV04, L, ""),
 ("2004-12-31", "SFGate", "Coach's successes leave team behind", "Carrie Sturrock", "https://www.sfgate.com/bayarea/article/Coach-s-successes-leave-team-behind-Hollywood-2660624.php", L, "Pre-release: his speaking career took off"),
 ("2005-01", "George Fox Journal", "Coach Ken Carter: From Lockout to Open Doors", "Sean Patterson", "https://www.georgefox.edu/journalonline/winter05/lockout.html", V, "Alumni profile; lists outlets that called"),
 ("2005-01-11", "Crosswalk.com", "Making the Grade: An Interview with the Real 'Coach Carter'", "Annabelle Robertson", "https://www.crosswalk.com/culture/features/making-the-grade-an-interview-with-the-real-%E2%80%98coach-carter%E2%80%99-1306513.html", V, "Press-tour interview"),
 ("2005-01-11", "The Michigan Daily", "Coach Carter approves of his cinematic story", "", "https://digital.bentley.umich.edu/midaily/mdp.39015071755131/65", L, ""),
 ("2005-01-13", "ESPN.com Page 3", "The real Coach Carter is a class act", "Miki Turner", "http://sports.espn.go.com/espn/page3/story?page=turner/kencarter", L, "URL now 404; cited by Wikipedia"),
 ("2005-01-13", "San Diego Union-Tribune", "(Coach Carter feature, p. E1)", "", "", L, "Bibliography only (Encyclopedia.com)"),
 ("2005-01-14", "The Oklahoman", "'Coach Carter' teaches lessons on, off the court", "Sandi Davis", "https://www.oklahoman.com/story/news/2005/01/14/coach-carter-teaches-lessons-on-off-the-court/61958785007/", L, ""),
 ("2005-01-14", "One Guy's Opinion", "Ken Carter on 'Coach Carter'", "", "https://www.oneguysopinion.com/ken-carter-on-coach-carter/", V, "Interview on accuracy"),
 ("2005-01-17", "Jet", "Coach Carter feature (pp. 54–55)", "", "https://books.google.com/books?id=NbYDAAAAMBAJ&pg=PA54", V, "Torch, Jackson's praise"),
 ("2005-01-20", "Sacramento Bee", "(Coach Carter feature, p. E1)", "", "", L, "Bibliography only"),
 ("2005-01-24", "Sports Illustrated", "Under Review (p. 29)", "", "https://vault.si.com/vault/2005/01/24/under-review", L, "Film vs. the real lockout; Vault URL now 404, also in Encyclopedia.com bibliography"),
 ("2005-01", "MTV News", "Reel to Real: Did Hollywood Have Its Way With Coach Carter's Story?", "", "https://www.mtv.com/news/q7gd5z/reel-to-real-did-hollywood-have-its-way-with-coach-carters-story", L, "Quotes his Chicago Sun-Times remarks"),
 ("2005-02-02", "Seattle Times", "(Coach Carter feature, p. F5)", "", "", L, "Bibliography only"),
 ("2005-02-28", "Lehigh University News", "Real-life Coach Carter leads by example", "Sarah Cooke", "https://news.lehigh.edu/real-life-coach-carter-leads-by-example", V, "Crumpled $20 bill lesson"),
 ("2005-06-15", "Columbus Ledger-Enquirer", "(Coach Carter feature)", "", "", L, "Bibliography only"),
 ("2006-02", "The University News (Saint Louis Univ.)", "'Coach' Carter talks discipline, integrity", "", "https://unewsonline.com/2006/02/coachcartertalksdisciplineintegrity/", L, ""),
 ("2015-01-22", "Deadspin / Dallas Morning News / ESPN-AP / HBCU Sports", "Baylor vs. Huston-Tillotson game staged for a Coach Carter sequel", "Tom Ley (Deadspin)", "https://deadspin.com/baylor-played-an-naia-team-for-the-sake-of-a-dopey-movi-1681094299/", V, "Coverage is mocking in tone; use the facts with care, not the headline"),
 ("2015", "Esquire", "What It's Like to Have Your Life Made Into a Movie", "", "https://www.esquire.com/sports/interviews/a39829/what-its-like-your-life-made-into-movie-coach-carter/", L, "First-person; title from URL slug"),
 ("2016-01-20", "ESPN.com", "Baylor's Gathers isn't letting offseason trouble define him", "Myron Medcalf", "https://www.espn.com/mens-college-basketball/story/_/id/14610495/baylor-bears-rico-gathers-unknown-future-stems-offseason-incident", V, "Carter mentored Rico Gathers"),
 ("2016-10-27", "Washington Informer", "Coach Carter shares his strategy for success", "", "https://www.washingtoninformer.com/coach-carter-shares-his-strategy-for-success/", V, "Howard men's basketball talk"),
 ("2017-01", "ASI Promogram", "Carter touts passion, accountability at keynote", "", "https://members.asicentral.com/news/newsletters/promogram/january-2017/carter-touts-passion-accountability-at-keynote", V, "ASI Orlando keynote recap"),
 ("2020-03-09", "Richmond Standard", "Coach Carter dishes assist to Richmond elementary school team", "", "https://richmondstandard.com/sports/2020/03/09/coach-carter-dishes-assist-to-richmond-elementary-school-team/", L, ""),
 ("2020-09-26", "Distractify", "Real Coach Carter Today", "Samantha Faragalli Younghans", "https://www.distractify.com/p/real-coach-carter-today", V, ""),
 ("2022-03-21", "Decider", "Is 'Coach Carter' Based on a True Story?", "", "https://decider.com/2022/03/21/is-coach-carter-based-on-a-true-story/", L, ""),
 ("2022-10-05", "Ottumwa Courier", "IHCC to host 40th Annual Celebrity Night featuring Coach Carter", "", "https://www.yahoo.com/news/ihcc-host-40th-annual-celebrity-015400473.html", V, ""),
 ("2022-12-08", "Atlanta Black Star", "Is 'Coach Carter' a True Story?", "Kiara Washington", "https://atlantablackstar.com/2022/12/08/coach-carter-returns-to-netflix-learn-about-the-name-behind-the-film-that-inspired-millions/", V, ""),
 ("2023-07-21", "USA TODAY Sports", "Slamball is back…", "Jordan Mendoza", "https://ca.sports.yahoo.com/news/slamball-back-highlight-driven-sport-230545685.html", V, "Carter coaching Rumble again"),
 ("2023-07-23", "Fox News", "SlamBall coaches exchange words as hard-hitting basketball returns", "Ryan Morik", "https://www.foxnews.com/sports/slamball-coaches-exchange-words-hard-hitting-basketball-returns-forefront", V, "Notes his 2002 title"),
 ("2023-09", "Solutions Magazine", "From McComb to the Movies: The Coach Carter Story", "", "https://www.solutionsmagazine-digital.com/hccq/0323_fall_2023/MobilePagedArticle.action?articleId=1920098", L, ""),
 ("2023-10", "Contracting Business", "Coach Kenny Ray Carter inspires audience at PHCCCONNECT2023", "", "https://www.contractingbusiness.com/columns/the-first-word/article/21276600/coach-kenny-ray-carter-inspires-audience-phccconnect-2023", V, ""),
 ("2024-12-05", "The Mercury News", "Coach Carter is back for a sequel, but can he save Richmond basketball again?", "Nathan Canilao", "https://www.mercurynews.com/2024/12/05/coach-carter-is-back-at-richmond-basketball-2024/", L, "The 'coming back' story"),
 ("2024-12-13", "The Mercury News", "Coach Carter's first game back at Richmond High underscores how times have changed", "", "https://www.mercurynews.com/2024/12/13/coach-carters-first-game-back-at-richmond-high-underscores-how-times-have-changed/", L, ""),
 ("2026-01-14", "The Contra Costa Pulse", "Kennedy High snaps losing streak with big win over Richmond High", "Joe Porrello", "https://ccpulse.org/2026/01/14/kennedy-high-basketball-snaps-losing-streak-with-big-win-over-richmond-high/", V, "FLAG: says paperwork cut his return short; Kenny Spaight now head coach"),
 ("2026-11-04", "Screen Rant", "Coach Carter True Story: How Much Is Real & What Happened Next", "", "https://screenrant.com/coach-carter-movie-true-story-accuracy-updates/", V, "Updated for the 2024 return"),
]
PRESS_KNOWN = ["SF Chronicle 1999-01-07", "NYT/AP 1999-01-09", "LA Times 1999-01-12", "LA Times 2001-07-11 'Benching Dream Team Was Right Move' (John M. Glionna, front page)",
               "Christianity Today 2005 (now https://www.christianitytoday.com/2005/01/kencarter/)", "Richmond Standard 2023", "CC Pulse 2024-12-16"]

# ---------------------------------------------------------------- celebrity / public-figure connections
CELEB = [
 ("Samuel L. Jackson", "actor", "Played him; together on Dr. Phil (2005-01-06) and at the LA premiere (2005-01-13)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Dr. Phil McGraw", "TV host", "Getty: 'Ken Carter, Samuel L. Jackson and Dr. Phil' (Jan 6 2005)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Hank Aaron", "Baseball Hall of Famer", "Met at the premiere afterparty, The Highland, 2005-01-13 (Getty/Kevin Winter); Carter first met the producers via their Aaron documentary", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Ernie Banks", "Baseball Hall of Famer", "Premiere afterparty 2005-01-13 (Getty)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Sherry Lansing", "Paramount Pictures chair", "Premiere arrivals + afterparty 2005-01-13 (Getty)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Ashanti; director Thomas Carter; Channing Tatum, Rick Gonzalez, Antwon Tanner, Nana Gbewony", "film cast", "Premiere (2005-01-13) + Palm Springs opening night (Getty)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Mike Tollin & Brian Robbins", "producers", "Hollywood Reporter 2002-06-13: he approached them after their Hank Aaron documentary", WB + "20041027141540/http://www.coachcarter.com:80/reporter_article2.htm", V),
 ("Rep. Mary Bono; Palm Springs Mayor Ron Oden; Earl Greenberg (PSIFF chair)", "politicians / festival", "Palm Springs Int'l Film Festival opening night, Jan 2005 (Getty/WireImage)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Dean Cain", "actor", "'Net Gain' celebrity basketball game for LA kids, Santa Monica, 2004-10-17 (Getty)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Willie Gault", "NFL All-Star (Raiders/Bears)", "'A Time To Care' ALS Association benefit, Playboy Mansion (Getty/WireImage)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Gov. Gray Davis", "California governor", "At the Jan 1999 comeback game (AP); Feb 1999 Senate Education Committee at his request; photo on Coach's 2002 site", "https://www.deseret.com/1999/1/13/19423064/team-hits-books-returns-to-court/", V),
 ("Mayor Willie Brown", "San Francisco mayor", "Leadership Award; photo with the Richmond High team (2002 site)", PH02, L),
 ("Rush Limbaugh", "radio host", "Interviewed him, Feb 1999", WB + "20041209125442/http://www.coachcarter.com:80/limbaughltr.htm", V),
 ("Rev. Jesse Jackson", "civil-rights leader", "Photo with Coach (caption #10, 2002 site)", PH02, L),
 ("Chris Tucker", "actor/comedian", "Photo with Coach (caption #12, 2002 site)", PH02, L),
 ("Gladys Knight & Les Brown", "singer; motivational speaker", "Photo together (caption #13, 2002 site)", PH02, L),
 ("Downtown Julie Brown", "TV host", "Photo (caption #14, 2002 site)", PH02, L),
 ("Eric Dickerson", "NFL Hall of Famer", "Photo (caption #15, 2002 site)", PH02, L),
 ("Phil Jackson", "NBA coach", "Photo 'Coach Phil Jackson and Coach Carter' (caption #17, 2002 site)", PH02, L),
 ("Rep. George Miller", "U.S. Congressman (Richmond district)", "Photo (caption #11, 2002 site)", PH02, L),
 ("Rickey Smiley", "radio/TV host", "Book conversation, c. 2012 (Coach's channel)", YT + "l-JuG82IsIQ", L),
 ("Mason Gordon", "SlamBall founder", "Sideline together, Las Vegas 2023-07-30 (Getty)", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V),
 ("Scott Drew & Rico Gathers", "Baylor coach; Baylor/NFL athlete", "Drew hosted the 2015 sequel game as a favor; Carter mentored Gathers (ESPN 2016)", "https://www.espn.com/mens-college-basketball/story/_/id/14610495/baylor-bears-rico-gathers-unknown-future-stems-offseason-incident", V),
 ("Hal & Mary Daub", "former U.S. Congressman / Omaha mayor", "Chaired the 2016 Omaha Home for Boys gala he headlined", "https://ohb.org/ken-coach-carter-headlines-omaha-home-for-boys-fundraising-gala/", V),
 ("Robert Ri'chard", "actor", "Says the real Carter picked him to play Damien (2020 video)", YT + "EhjKfL8OTrs", L),
 ("Prince", "musician", "Courtside photo per Coach — NO public source found", "", U),
 ("'the President of the United States'", "—", "Bureau bios (Gotham Artists) claim it; no president named or documented", "https://gothamartists.com/coach_ken_carter/", U),
]

# ---------------------------------------------------------------- speaking (new, beyond the known ~31)
# (date, org, event, city, state, type, url, confidence, note)
SPK = [
 # pre-2005 from Coach's own CVs (2002, 2009) and 2004 media pages
 ("1999-02", "California Senate Education Committee", "Special legislative session, at Gov. Davis's request", "Sacramento", "CA", "government", CV02, L, "Self-reported CV"),
 ("1999-05", "Athletes United for Peace", "Head coach, delegation to Amsterdam", "Amsterdam", "Netherlands", "international", CV02, L, "Self-reported CV"),
 ("2000-02", "Los Medanos College", "Keynote to student-athletes", "Pittsburg", "CA", "university", CV02, L, "CV spells it 'Los Modanos'"),
 ("2001-02", "Contra Costa Youth Detention Center", "Life skills/education talk", "Martinez", "CA", "corrections", CV02, L, ""),
 ("2001-02", "Iron Triangle Faith Community Retreat", "Speaker", "Richmond", "CA", "church", CV02, L, ""),
 ("2001-02", "Peres Elementary School", "Speaker/sponsor, touring science program", "Richmond", "CA", "school", CV02, L, ""),
 ("2001-03", "Marsh Creek Adult Detention Facility", "Graduation commencement keynote", "Clayton", "CA", "corrections", CV02, L, ""),
 ("2001-03", "Golden Gate University", "Guest speaker, Women in Politics panel", "San Francisco", "CA", "university", CV02, L, ""),
 ("2001-04", "Urban Financial Services Coalition / Federal Reserve Bank of SF", "17th Annual Scholarship Reception keynote", "San Francisco", "CA", "corporate", CV02, L, ""),
 ("2001-05", "JCCASAC (Juvenile Court & Alternative Schools Administrators of CA)", "32nd Annual State Conference keynote", "", "CA", "conference", CV02, L, ""),
 ("2001-06", "Kids First", "Annual conference keynote, 'Molding Minds for the Future'", "New York", "NY", "conference", CV02, L, ""),
 ("2001-07", "International Center for Leadership in Education", "9th Model Schools Conference, guest educator", "Orlando", "FL", "conference", CV02, L, ""),
 ("2001-07", "Indiana College Connections (DePauw Univ.)", "Keynote", "Greencastle", "IN", "university", CV02, L, ""),
 ("2001-08", "CHARACTER COUNTS! Sports", "'Pursuing Victory With Honor' speaker", "Kansas City", "MO", "conference", CV09, L, ""),
 ("2002-02", "Chevron-Texaco", "Awareness Celebration keynote", "Concord", "CA", "corporate", CV09, L, ""),
 ("2002-07", "International Center for Leadership in Education", "10th Model Schools Conference presenter", "Washington", "DC", "conference", CV09, L, ""),
 ("2003-11-22", "Long Beach Midnight Basketball League", "Annual Fall Awards Banquet keynote", "Long Beach", "CA", "nonprofit", WB + "20041204032200/http://www.coachcarter.com:80/media.htm", V, "Article archived on coachcarter.com"),
 ("2004-01", "East Oakland Youth Training Program", "Mentoring at-risk youth", "Oakland", "CA", "nonprofit", CV09, L, ""),
 ("2004-01", "Richmond High School", "5th anniversary of the lockout: scholarships + alumni game", "Richmond", "CA", "school", CV09, L, ""),
 ("2004-05-29", "St. Anthony High School", "Class of 2004 commencement address", "Long Beach", "CA", "school", WB + "20041204032200/http://www.coachcarter.com:80/media.htm", V, "Film shot in its gym"),
 ("2004-06-02", "Foundations Inc. / Martin Luther King High School", "'Average Is Just Not Good Enough' keynote", "Philadelphia", "PA", "school", WB + "20041204032200/http://www.coachcarter.com:80/media.htm", V, ""),
 ("2004-09", "California Golden State ScholarShare", "Keynote launching the college-savings program", "Sacramento", "CA", "government", CV09, L, ""),
 ("2004-09", "College Savings Month", "Keynote seminar", "Los Angeles", "CA", "government", CV09, L, ""),
 # 2005–2026 (speaking research pass + video sweep)
 ("2005-01", "Palm Springs International Film Festival", "Spoke at opening-night 'Coach Carter' screening", "Palm Springs", "CA", "other", "https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter", V, "Getty: 'Ken Carter, coach speaks at the opening night screening'"),
 ("2005-03-07", "Cal Poly Pomona", "Student presentation + athletes session", "Pomona", "CA", "university", "https://www.cpp.edu/news/content/2005/02/real_life_coach_carter_to_speak_to_students_about_his_experiences_attaining_success/index.shtml", V, ""),
 ("2005-10-06", "American Association of School Librarians (ALA)", "12th National Conference opening keynote", "Pittsburgh", "PA", "conference", "https://www.ala.org/news/news/pressreleases2005/september2005/aasl05keynote", V, ""),
 ("2006-02", "TCEA (Texas Computer Education Assn.)", "Opening keynote", "Austin", "TX", "conference", "https://www.speedofcreativity.org/2006/02/08/coach-ken-carter-on-education/", L, ""),
 ("2006-02", "Saint Louis University", "Campus talk", "St. Louis", "MO", "university", "https://unewsonline.com/2006/02/coachcartertalksdisciplineintegrity/", L, ""),
 ("2007-02", "Find Your Why Main Event", "Featured speaker", "", "", "conference", YT + "vhOg6ts2m8U", L, ""),
 ("2008", "Penn State University", "MLK Commemoration keynote", "University Park", "PA", "university", "https://mlk.psu.edu/mlk-2008/", V, ""),
 ("2008-06", "Caterpillar Inc.", "Juneteenth pep talk", "Peoria", "IL", "corporate", YT + "kpJ4V6VISuI", V, "Journal Star video"),
 ("2008-08-15", "Newton Municipal School District", "'A Back to School Explosion'", "Newton", "MS", "school", "https://meridianstar.com/2008/08/13/the-real-coach-carter-to-speak-at-newton-high-friday", V, ""),
 ("2009-01", "Oklahoma State University", "Speakers Board lecture + Inside OSU", "Stillwater", "OK", "university", YT + "5vZxM5whfn8", V, ""),
 ("2009-02-26", "Nova Southeastern University", "Carrie P. Meek Education Leadership Awards keynote", "Davie", "FL", "university", "https://nsunews.nova.edu/fifth-annual-carrie-p-meek-outstanding-education-leadership-achievement-awards-honors-exemplary-community-members/index.html", V, ""),
 ("2010-08-16", "Pastor J.T. Cotton (community)", "Free motivational talk, Estacado HS", "Lubbock", "TX", "church", "https://www.kcbd.com/story/12953187/coach-ken-carter-coming-to-lubbock/", V, ""),
 ("2010-10", "Lincoln church (per Journal Star)", "Church talk", "Lincoln", "NE", "church", "https://journalstar.com/news/local/education/article_f0cb8368-db04-11df-81c2-001cc4c03286.html", U, "Headline only"),
 ("2011", "Speaking tour", "Guatemala tour", "", "Guatemala", "international", YT + "pGShjPueprM", V, "Coach's own videos 2011–2012"),
 ("2011-02", "AVBOT 2011 (with Jim Greenleaf)", "Featured speaker", "", "", "conference", YT + "V0ghNyXrEqE", L, ""),
 ("2012-01", "Montana State University Billings", "'Power of One' week", "Billings", "MT", "university", YT + "vNtLdIkR4dY", L, ""),
 ("2012-04-19", "Radford University / McGlothlin Foundation", "McGlothlin Celebration of Teaching", "Radford", "VA", "university", "https://www.radford.edu/content/radfordcore/home/news/releases/2012/February/carter-mcglothlin.html", L, ""),
 ("2012-08-25", "Midwestern State University Athletics", "Student-Athlete Life Skills Day", "Wichita Falls", "TX", "university", "https://thewichitan.com/3136/news/the-real-coach-carter-encourages-student-athletes/", V, ""),
 ("2013", "MLK Celebration Sacramento", "Keynote", "Sacramento", "CA", "nonprofit", "https://www.mlkcelebrationsacramento.org/past-keynote-speakers/", V, ""),
 ("2013-01", "Gulfstream Student Leadership Program", "Program opening", "", "", "school", YT + "j-0ndf17rQQ", L, ""),
 ("2013-06", "Credit Union Association of New York", "Annual Meeting & Convention lead keynote", "Bolton Landing", "NY", "conference", "https://cuinsight.com/?p=21332", L, ""),
 ("2014-04-24", "Dakota Collegiate", "Fundraiser keynote", "Winnipeg", "MB, Canada", "international", "https://www.basketballmanitoba.ca/2014/03/dakota-collegiate-to-host-coach-carter.html", V, ""),
 ("2015-07", "HARDI (heating & cooling distributors)", "Emerging Leaders summer conference", "", "", "conference", YT + "hWfi344NYVY", L, ""),
 ("2016-02-27", "Modesto Junior College", "African American Education Conference keynote", "Modesto", "CA", "university", "https://www.turlockjournal.com/news/education/mjc-to-host-annual-african-american-education-conference/", L, ""),
 ("2016-08", "Burleson ISD", "Teacher convocation, Centennial HS", "Burleson", "TX", "school", YT + "ikKUrVzJ4KM", V, ""),
 ("2016-09-15", "Omaha Home for Boys", "Imagine Our Youth Gala keynote", "La Vista", "NE", "nonprofit", "https://ohb.org/ken-coach-carter-headlines-omaha-home-for-boys-fundraising-gala/", V, ""),
 ("2016-10-22", "Howard University men's basketball", "Locker-room talk", "Washington", "DC", "sports-team", "https://www.washingtoninformer.com/coach-carter-shares-his-strategy-for-success/", V, ""),
 ("2017-08", "East Baton Rouge Parish Schools", "Back-to-school convocation for ~3,000 teachers", "Baton Rouge", "LA", "school", YT + "IYOts4RDNwI", V, ""),
 ("2017-08", "Lee County School District", "District visit", "Bishopville", "SC", "school", YT + "uIUXlwa5PB4", V, ""),
 ("2017-09", "Regional Access Project Foundation", "Nonprofit Conference keynote + student session", "Cathedral City", "CA", "nonprofit", "https://ukenreport.com/coach-carter-inspires-coachella-valley-students/", V, ""),
 ("2017-10", "University of New Mexico", "SUB Ballroom talk", "Albuquerque", "NM", "university", YT + "D9XQxQtqT0M", V, ""),
 ("2018-02", "Georgia Gwinnett College", "Black History Month talk", "Lawrenceville", "GA", "university", YT + "akqKkkhiBes", V, ""),
 ("2018-06-14", "G.O.T.C.H.A. / City of Amarillo", "Youth talk with Mayor Nelson", "Amarillo", "TX", "nonprofit", "https://www.newschannel10.com/story/38430123/coach-ken-carter-speaks-with-amarillo-youth-on-education/", V, ""),
 ("2019-09-30", "Southeastern California Conference of SDA", "Pastor/Teacher Health Day", "Loma Linda", "CA", "church", "https://drayson.llu.edu/about/drayson-news/secc-teachers-and-pastors-enjoy-day-of-wellness-and-fun", V, ""),
 ("2020-01-17", "City of Jacksonville", "33rd Annual MLK Breakfast keynote", "Jacksonville", "FL", "government", "https://archive.org/details/cojaxfl-33rd_Annual_MLK_Breakfast", V, ""),
 ("2020-02", "Illinois Dept. of Transportation (IDOT)", "Conference keynote", "Peoria", "IL", "government", YT + "BZxVjjvtHYI", V, ""),
 ("2022-02", "Roanoke College (Pi Lambda Phi + CLEI)", "Leadership Speaker", "Salem", "VA", "university", "https://www.pilambdaphi.org/news/coach-carter-speaks-at-roanoke/", L, ""),
 ("2022", "Boys & Girls Clubs of Lanier", "Be Great Gala keynote", "Gainesville", "GA", "nonprofit", YT + "BB2XDkU4rgw", V, ""),
 ("2022", "cityCURRENT", "Virtual Signature Event", "", "", "corporate", "https://vimeo.com/681468154", L, ""),
 ("2022-06", "Biloxi presentation", "Presentation (58-min video)", "Biloxi", "MS", "other", YT + "sfXi-gXxP9k", L, "Host org not named"),
 ("2022-10", "Indian Hills Community College", "40th Annual Celebrity Night", "Ottumwa", "IA", "university", "https://www.yahoo.com/news/ihcc-host-40th-annual-celebrity-015400473.html", V, ""),
 ("2023-05-05", "Rainbow Days", "26th Pot of Gold Luncheon keynote", "Dallas", "TX", "nonprofit", "https://dallas.culturemap.com/eventdetail/rainbow-days-presents-26th-annual-pot-of-gold-luncheon/", V, ""),
 ("2023-08-08", "Sylacauga City Schools", "District institute keynote", "Sylacauga", "AL", "school", "https://www.sylacauganews.com/local/coach-ken-carter-speaks-at-sylacauga-city-schools-institute-with-unyielding-message-of-possibility", V, ""),
 ("2023-08", "Woodrow Wilson High School", "School visit", "Beckley", "WV", "school", YT + "RxOKHlwuKlI", V, ""),
 ("2023-08", "GDA (per WBRC)", "Joined GDA event", "Birmingham area", "AL", "other", YT + "CQUnLvYzTEs", L, "Confirm what GDA is"),
 ("2023-10-24", "Greater Waco Chamber", "Tip Off Luncheon", "Waco", "TX", "corporate", "https://business.wacochamber.com/events/Details/2023-tip-off-luncheon-901417", L, ""),
 ("2023-10-25", "PHCC National", "PHCCCONNECT2023 opening keynote", "Cleveland", "OH", "conference", "https://www.contractingbusiness.com/columns/the-first-word/article/21276600/coach-kenny-ray-carter-inspires-audience-phccconnect-2023", V, "Standing ovation"),
 ("2025-01-03", "Exceeding Excellence Education Foundation", "ISA Invitational Dinner Gala", "Nampa", "ID", "nonprofit", "https://eeef.betterworld.org/events/coach-ken-carter", V, ""),
 ("2025-03", "Federal Probation and Pretrial Officers Association", "Centennial Celebration closing speaker", "Arlington", "VA", "corrections", "https://fppoa.org/content.aspx?page_id=22&club_id=981031&module_id=718626", V, ""),
 ("2025-06-07", "Sierra Vista Herald/Review", "Best of Preps 2025", "Sierra Vista", "AZ", "other", "https://www.myheraldreview.com/free_access/ken-carter-of-coach-carter-movie-fame-the-guest-speaker-for-best-of-preps/article_5d5a497b-cb1d-4382-99d1-35213be1d7e3.html", V, ""),
 ("2025-08-13", "Martinsville City Public Schools", "District engagement", "Martinsville", "VA", "school", "https://www.aaespeakers.com/keynote-speakers/coach-ken-carter", L, "Bureau review listing"),
 ("2025-09", "BCA", "All-Star Speaker Series", "Philadelphia (inferred)", "PA", "corporate", "https://bcaproud.com/news-and-latest/announcing-our-september-all-star-speaker-coach-ken-carter-famed-high-school-basketball-coach-with-hard-hitting-advice-about-accountability-integrity-teamwork-and-leadership/", L, ""),
 ("2026-04-16", "Family & Children's Center", "Spotlight Dinner", "South Bend", "IN", "nonprofit", "https://www.abc57.com/news/the-real-life-coach-carter-was-interviewed-by-brian-conybeare", V, ""),
 ("2026-05-13", "BMW Manufacturing", "BMW Supplier XChange 2026 keynote", "Greenville", "SC", "corporate", "https://scinnovates.org/2026/05/18/bmw-supplier-xchange-on-may-13-2026/", V, ""),
 ("2026-08-12", "Moline-Coal Valley School District", "Public talk + all-staff in-service", "Moline", "IL", "school", "https://www.ourquadcities.com/news/local-news/coach-ken-carter-will-speak-at-moline-high-school/", L, ""),
 ("2026-09-11", "Walters State CC / Mid-East TN P-16 Council", "East Tennessee Literacy Conference keynote", "Morristown", "TN", "conference", "https://ws.edu/news/2026/coach_carter_to_headline_literacy_conference.aspx", V, ""),
 ("2026-09-22", "Horry-Georgetown Tech / SC Dept. of Employment & Workforce / Horry County Schools", "Student leadership event, 12 high schools", "Conway", "SC", "school", "https://whosonthemove.com/coach-ken-carter-to-address-regional-high-school-students-at-hgtc/", V, "HCS video: " + YT + "lfKdKwfvfRk"),
 ("2026-10", "Las Vegas-Clark County Library District", "Summerlin Library screening visit", "Las Vegas", "NV", "other", YT + "jXNRdRaSJio", V, "Same trip as the known MBK Las Vegas 2026"),
 ("", "University of Michigan-Flint", "Talk to ~1,000 + scholarship reception", "Flint", "MI", "university", "https://record.umich.edu/articles/real-coach-carter-bounces-into-u-m-flint/", L, "Date unknown (c. 2005–06)"),
 ("", "Illinois state agency (per WCIA)", "Talk to inspire a state agency", "Springfield", "IL", "government", YT + "cjiybcoT9b0", L, "Date unknown"),
 ("", "Mississippi School Superintendents", "Keynote", "", "MS", "conference", "https://capcityspeakers.com/coach-ken-carter/", U, "Testimonial only"),
 ("", "Carolinas Food Industry Council", "Presentation", "", "NC/SC", "corporate", "https://premierespeakers.com/speakers/ken-carter", U, "Testimonial only"),
 ("", "NAAA (likely National Auto Auction Assn.)", "Keynote", "", "", "conference", "https://executivespeakers.com/speaker/ken-carter", U, "Testimonial only"),
 ("", "City of Long Beach", "Appearance (Vice Mayor's testimonial)", "Long Beach", "CA", "government", "https://www.espeakers.com/marketplace/profile/6590/ken-carter", U, "Testimonial only"),
]

# corrections/better sources for the KNOWN speaking list
KNOWN_FIXES = [
 ("Wake Forest", "2005-01-19, Benson University Center", "https://news.wfu.edu/2005/01/05/coach-ken-carter-to-give-hard-hitting-advice-at-wfu/"),
 ("Univ. of Tennessee", "2005-10-31", "https://news.utk.edu/2005/10/13/coach-carter-to-speak-at-ut-oct-31/"),
 ("Mississippi State", "2006-02-09, Black History Month keynote", "https://www.newsarchive.msstate.edu/newsroom/article/2006/02/coach-carter-keynote-black-history-month-program-msu"),
 ("Syracuse", "2010-02-13, Goldstein Auditorium", "https://dailyorange.com/2010/02/coach-carter-promotes-the-importance-of-education/"),
 ("St. Thomas (MN)", "Tue Feb 23 (→2010)", "https://news.stthomas.edu/noted-basketball-coach-ken-carter-to-speak-here-next-tuesday/"),
 ("Ball State", "2014-01-21 (MLK/Unity Week)", "https://www.bsu.edu/news/press-center/archives/2014/1/coach-carter-to-speak-jan-21-at-ball-state-in-honor-of-mlk-jr-day"),
 ("CSU Pueblo", "2015-01", "https://www.csupueblo.edu/news/2015/01-08-coach-ken-carter.html"),
 ("Penn State Harrisburg", "2019-01-24", "https://harrisburg.psu.edu/story/13896/2019/01/17/author-and-speaker-coach-ken-carter-visit-penn-state-harrisburg"),
 ("ASI Show 'Chicago 2017'", "CORRECTION: ASI Orlando, ~2017-01-19", "https://members.asicentral.com/news/newsletters/promogram/january-2017/carter-touts-passion-accountability-at-keynote"),
 ("Escambia County 'FL' 2023", "CORRECTION: Escambia County, ALABAMA Schools pep rally, Flomaton HS, 2023-08-04", "https://atmorenews.com/?p=30218"),
 ("NAI Global 2023", "2023-02-08 general session", "https://naiglobal.swoogo.com/2023convention/session/1100144/general-session-keynote-speaker-coach-carter"),
 ("Youngstown 2021", "2021-11-17 Parent University, Chaney HS", ""),
 ("Boys & Girls Clubs of Central Wyoming 2026", "2026-09-16, Ford Wyoming Center", "https://oilcity.news/community/2026/09/16/leaders-young-and-old-celebrated-at-annual-boys-and-girls-club-event-in-casper/"),
 ("GTC West 2006", "source", "https://www.govtech.com/archive/Coach-Ken-Carter-Keynotes-GTC-West.html"),
 ("Fort Myers 2019", "New Hope Presbyterian Church", "https://www.winknews.com/archives/coach-carter-portrayed-in-2005-film-shares-life-lessons-in-fort-myers/article_8e1d9266-e8bc-59c4-ad1d-1b93d1cfc945.html"),
]

# ---------------------------------------------------------------- testimonials
# (quote, person, title, org, url, confidence)
TEST = [
 ("Coach Carter is now in the number 1 spot of keynote speakers!!! He was just amazing – had the audience in tears and laughing. Can't wait to have him back.", "Heidi S.", "Director, Education & Training", "PHCC (National)", "https://www.bigspeak.com/speakers/coach-ken-carter/", V),
 ("Coach Carter is a distinguished spokesperson and educator in his own right. He has engaged himself in one of today's most important challenges - the education of our youth.", "Frank Colonna", "Vice Mayor", "City of Long Beach, CA", "https://www.espeakers.com/marketplace/profile/6590/ken-carter", V),
 ("Coach Carter did a great job! He connected with our audience and held their attention throughout his presentation.", "", "", "Mississippi School Superintendents", "https://capcityspeakers.com/coach-ken-carter/", V),
 ("Coach Carter did a wonderful job and was very personable onsite. He won the crowd over.", "", "", "NAAA", "https://executivespeakers.com/speaker/ken-carter", V),
 ("Your presentation was fantastic--high energy, motivating and inspiring.", "", "", "Carolinas Food Industry Council", "https://premierespeakers.com/speakers/ken-carter", V),
 ("Coach Ken Carter brought the house down with his inspirational speech!", "City of Jacksonville", "official community-media post", "City of Jacksonville — 33rd MLK Breakfast (2020)", "https://archive.org/details/cojaxfl-33rd_Annual_MLK_Breakfast", V),
 ("The highlight of the conference was an inspiring talk from Coach Ken Carter.", "SC Innovates", "", "BMW Supplier XChange 2026", "https://scinnovates.org/2026/05/18/bmw-supplier-xchange-on-may-13-2026/", V),
 ("His multi-directional message was so inspiring.", "Contracting Business columnist", "", "PHCCCONNECT2023", "https://www.contractingbusiness.com/columns/the-first-word/article/21276600/coach-kenny-ray-carter-inspires-audience-phccconnect-2023", V),
 ("I love how Coach Carter told stories throughout his presentation.", "Wesley Fryer", "Educator/blogger", "TCEA 2006", "https://www.speedofcreativity.org/2006/02/08/coach-ken-carter-on-education/", V),
 ("He had a whole lotta energy", "William Halchuk", "", "Pakmark (ASI Orlando 2017 attendee)", "https://members.asicentral.com/news/newsletters/promogram/january-2017/carter-touts-passion-accountability-at-keynote", V),
 ("The DHSHS students really enjoyed hearing the 'real' Coach Carter speak.", "Juldene Sims", "Teacher", "Desert Hot Springs High School", "https://ukenreport.com/coach-carter-inspires-coachella-valley-students/", V),
 ("one of the most inspiring I have ever experienced", "Rush Limbaugh", "radio host", "The Limbaugh Letter, Feb 1999 (on his interview)", WB + "20041209125442/http://www.coachcarter.com:80/limbaughltr.htm", V),
 ("His message of don't stick to the status quo, push the students beyond their limits, and that academic comes first even if you're a coach", "Michele McClung", "Superintendent", "Escambia County (AL) Schools", "https://weartv.com/news/local/former-basketball-coach-ken-carter-inspires-escambia-county-teachers-with-lessons-on-adversity-accountability", L),
 ("His is an inspirational story about caring, perseverance and dedication to success.", "Lori Bechtold", "Director of Development", "Omaha Home for Boys (pre-event)", "https://ohb.org/ken-coach-carter-headlines-omaha-home-for-boys-fundraising-gala/", V),
]

# ---------------------------------------------------------------- awards & honors
# (year, honor, source url, confidence, note)
AW = [
 ("1999-01", "Ed Hopkins Memorial Tournament Trophy (team)", CV09, L, "CV"),
 ("1999-01", "Downey Community Hospital nominee — California HS Basketball Coach of the Year", CV09, L, "CV"),
 ("1999–2002", "City of Richmond proclamation / 'Coach Carter Day'; Contra Costa Board of Supervisors resolution commending him (Supervisor John Gioia)", CV02, L, "CV + Gotham Artists bio; county record not yet pulled"),
 ("1999–2002", "Harvard Club of San Francisco — Distinguished Secondary Educator Award", "https://www.newsarchive.msstate.edu/newsroom/article/2006/02/coach-carter-keynote-black-history-month-program-msu", L, "All sources trace to his bio"),
 ("1999–2002", "NAACP Impact Citizen of the Year", "https://www.encyclopedia.com/education/news-wires-white-papers-and-books/carter-ken", L, ""),
 ("1999–2002", "California State Lottery / Gov. Gray Davis — Heroes in Education Award", CV02, L, "Big Spin appearance photo supports it"),
 ("1999–2002", "San Francisco Mayor Willie Brown Leadership Award", CV02, L, ""),
 ("1999–2002", "California Unsung Heroes Award", CV02, L, ""),
 ("1999–2002", "A.N.G. California Boys' Coach of the Year", CV02, L, "A.N.G. = Alameda Newspaper Group"),
 ("1999–2002", "City of San Pablo Citizen of the Year", CV02, L, ""),
 ("2000", "CityFlight Newsmagazine — Ten Most Influential African Americans in the Bay Area (Sports)", "https://www.speakinc.com/speakers/coach-ken-carter/", L, ""),
 ("2001", "BBL — San Francisco Bay Area Entrepreneur of the Year (July/Aug 2001)", CV02, L, "Also Encyclopedia.com"),
 ("2001", "Governor's performance grant for his team", "https://www.crosswalk.com/culture/features/making-the-grade-an-interview-with-the-real-%E2%80%98coach-carter%E2%80%99-1306513.html", L, ""),
 ("2002-01-19", "Olympic Torchbearer — 2002 Salt Lake City Winter Games, Richmond/Bay Area leg", CV09, V, "Date from CV; torch photos on 2002 site; Jet 2005"),
 ("2002", "SlamBall champion — head coach, LA Rumble", "https://www.foxnews.com/sports/slamball-coaches-exchange-words-hard-hitting-basketball-returns-forefront", V, ""),
 ("2000s", "Charles Houston Bar Association — Benjamin Travis Community Service Award", CV09, L, "2009 CV"),
 ("2000s", "African American Excellence in Business Award", PH02, U, "Photo caption only"),
 ("—", "'Life Saver Award' for rescuing young men from jails and gangs", "https://gothamartists.com/coach_ken_carter/", U, "Bureau bio only"),
 ("—", "Keys to the city", "", U, "None found in any public source"),
]

# ---------------------------------------------------------------- leads with no public record
NOT_FOUND = [
 ("The Best Damn Sports Show Period (Fox Sports Net)", "No listing, IMDb credit, transcript or clip found. IMDb shows only 4 credits for him (nm1939736). Get the tape/date from Coach."),
 ("Prince (courtside)", "No public source. Needs Coach's photo + context (venue/date)."),
 ("Oprah", "No evidence anywhere, incl. Coach's own 2002/2009 CVs (which list Today, CNN, ABC, KTVU, KRON). Don't claim it."),
 ("Tavis Smiley, Larry King, The View, BET, TV One, Steve Harvey, Tom Joyner, Jim Rome, 60 Minutes, CBS This Morning, ESPN OTL/SportsCenter", "Nothing found."),
 ("People/SI 2005, USA Today, Ebony, Chicago Sun-Times original, Time/Newsweek, Guardian/BBC, Variety/THR 2005", "Not found (People 1999 and SI 2003/2005 ARE found)."),
 ("Same-name traps", "Bishop Ken Carter (UMC: The Weight, Kate Bowler podcasts), Dr. Ken Carter (Emory), Ken Carter stuntman, Kenny Carter (Delaware State football), Adam/Ashley/Jack Carter 'Coach Carter' podcasts — all excluded."),
]
FLAGS = [
 "Contra Costa Pulse (2026-01-14) reports his Dec 2024 Richmond return was cut short by employment paperwork; Kenny Spaight is now Richmond's head coach. The site should not say he currently coaches Richmond High.",
 "A c. 2009–10 Waco Tribune-Herald item about a personal legal matter in Marlin, TX exists in the public record. Deliberately NOT logged here (private/family); the client team should know it is findable.",
 "Deadspin's 2015 coverage of the Baylor 'sequel' game is mocking in tone — cite facts, not that outlet.",
 "Coach's 2009 site sold a $297–$497 'Coach Carter Experience' network-marketing boot camp; worth knowing for brand positioning.",
]


def rows(items, keys):
    return [dict(zip(keys, it)) for it in items]


def main():
    tv = rows(TV, ["date", "outlet", "title", "url", "confidence", "note", "known"])
    pods = rows(PODS, ["date", "show", "title", "url", "confidence", "note", "known"])
    press = rows(PRESS, ["date", "outlet", "title", "author", "url", "confidence", "summary"])
    celeb = rows(CELEB, ["name", "who", "connection", "url", "confidence"])
    spk = rows(SPK, ["date", "org", "event", "city", "state", "type", "url", "confidence", "note"])
    test = rows(TEST, ["quote", "person", "title", "org", "url", "confidence"])
    aw = rows(AW, ["year", "honor", "url", "confidence", "note"])
    data = {
        "generated": "2026-11-09", "subject": "Coach Ken Carter (Richmond High, CA)",
        "confidence_key": {"verified": "public page documents it", "likely": "strong but indirect (self-reported CV/bio, bibliography, blocked page)", "unverified": "claim only"},
        "tv_radio": tv, "podcasts": pods, "press_features": press, "press_known": PRESS_KNOWN,
        "celebrity_connections": celeb, "speaking": spk, "speaking_known_fixes": rows(KNOWN_FIXES, ["item", "fix", "url"]),
        "testimonials": test, "awards": aw, "not_found": rows(NOT_FOUND, ["lead", "status"]), "flags": FLAGS,
        "sources": ["tools/investigate/podcast_sweep.py → podcasts_itunes.json", "tools/investigate/imdb_credits.py → imdb_credits.json",
                    "tools/investigate/wayback_coachcarter.py + wayback_fetch.py → wayback/*.txt", "getty_hits.json + VIDEOS.md (sibling sweep)",
                    "archive.org advancedsearch", "WebSearch/WebFetch press + speaking passes"],
    }
    json.dump(data, open(os.path.join(OUT, "appearances.json"), "w"), indent=1, ensure_ascii=False)

    def c(x):
        return {"verified": "✅", "likely": "🟡", "unverified": "⚪"}[x]

    def link(t, u):
        return f"[{t}]({u})" if u else t
    md = ["# Coach Ken Carter — The Record: appearances & press", "",
          "Generated 2026-11-09 by `tools/investigate/build_appearances.py` (machine copy: `appearances.json`). Public professional record only.",
          "Confidence: ✅ verified · 🟡 likely · ⚪ unverified. *(known)* = already on the site list.", ""]
    cnt = lambda L: Counter(x["confidence"] for x in L)
    md += ["## Counts", "", "| Section | Items | ✅ | 🟡 | ⚪ |", "|---|---|---|---|---|"]
    for name, L in [("TV & radio", tv), ("Podcasts", pods), ("Press features (new)", press), ("Celebrity connections", celeb),
                    ("Speaking (new)", spk), ("Testimonials", test), ("Awards & honors", aw)]:
        k = cnt(L)
        md.append(f"| {name} | {len(L)} | {k['verified']} | {k['likely']} | {k['unverified']} |")
    md += ["", "## ⚠️ Flags for the client team", ""] + [f"- {f}" for f in FLAGS]
    md += ["", "## TV & radio", "", "| Date | Outlet / show | What | Conf | Note |", "|---|---|---|---|---|"]
    for x in sorted(tv, key=lambda r: r["date"]):
        md.append(f"| {x['date']} | {x['outlet']}{' *(known)*' if x['known'] else ''} | {link(x['title'], x['url'])} | {c(x['confidence'])} | {x['note']} |")
    md += ["", "## Podcasts", "", "| Date | Show | Episode | Conf | Note |", "|---|---|---|---|---|"]
    for x in sorted(pods, key=lambda r: r["date"]):
        md.append(f"| {x['date']} | {x['show']}{' *(known)*' if x['known'] else ''} | {link(x['title'], x['url'])} | {c(x['confidence'])} | {x['note']} |")
    md += ["", "Raw iTunes sweep (662 episodes, scored): `podcasts_itunes.json`. Most hits are film-review shows *about* the movie.", ""]
    md += ["## Press features (new — not in the known list)", "", "| Date | Outlet | Title | Author | Conf | Note |", "|---|---|---|---|---|---|"]
    for x in sorted(press, key=lambda r: r["date"]):
        md.append(f"| {x['date']} | {x['outlet']} | {link(x['title'], x['url'])} | {x['author']} | {c(x['confidence'])} | {x['summary']} |")
    md += ["", "Known (not repeated): " + "; ".join(PRESS_KNOWN), ""]
    md += ["## Celebrity & public-figure connections", "", "| Who | Role | Connection | Conf |", "|---|---|---|---|"]
    for x in celeb:
        md.append(f"| {x['name']} | {x['who']} | {link(x['connection'], x['url'])} | {c(x['confidence'])} |")
    md += ["", "Getty captions (159) are in `getty_hits.json`; the 2002 photo-caption list is archived at " + PH02, ""]
    md += ["## Speaking engagements (new, beyond the known ~31)", "", "| Date | Org | Event | Place | Type | Conf | Note |", "|---|---|---|---|---|---|---|"]
    for x in sorted(spk, key=lambda r: (r["date"] or "9999")):
        place = ", ".join(p for p in (x["city"], x["state"]) if p)
        md.append(f"| {x['date'] or '?'} | {x['org']} | {link(x['event'], x['url'])} | {place} | {x['type']} | {c(x['confidence'])} | {x['note']} |")
    md += ["", "### Better dates / corrections for already-known engagements", ""]
    for i, f, u in KNOWN_FIXES:
        md.append(f"- **{i}:** {link(f, u)}")
    md += ["", "## Client testimonials", ""]
    for x in test:
        who = ", ".join(p for p in (x["person"], x["title"], x["org"]) if p)
        md.append(f"- {c(x['confidence'])} “{x['quote']}” — {link(who, x['url'])}")
    md += ["", "## Awards & honors", "", "| Year | Honor | Conf | Note |", "|---|---|---|---|"]
    for x in aw:
        md.append(f"| {x['year']} | {link(x['honor'], x['url'])} | {c(x['confidence'])} | {x['note']} |")
    md += ["", "## Looked for, not found", ""] + [f"- **{a}:** {b}" for a, b in NOT_FOUND]
    md += ["", "## Re-run", "", "```", "python3 tools/investigate/podcast_sweep.py", "python3 tools/investigate/imdb_credits.py",
           "python3 tools/investigate/wayback_coachcarter.py   # + wayback_fetch.py <page.htm>", "python3 tools/investigate/build_appearances.py", "```", ""]
    open(os.path.join(OUT, "APPEARANCES.md"), "w").write("\n".join(md))
    for name, L in [("tv", tv), ("pods", pods), ("press", press), ("celeb", celeb), ("speaking", spk), ("testimonials", test), ("awards", aw)]:
        print(name, len(L), dict(cnt(L)))


if __name__ == "__main__":
    main()
