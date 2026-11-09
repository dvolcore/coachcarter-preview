#!/usr/bin/env python3
"""build_photos.py — merge every photo source into tracking/investigation/photos.json + PHOTOS.md.

Inputs (tracking/investigation/):
  getty_hits.json     <- getty_oembed.py     (Getty editorial, oEmbed captions)
  alamy_hits.json     <- alamy_search.py     (Alamy: ZUMA / AP / Everett / UPI / AdMedia ...)
  raw_sweep.json      <- img_sweep.py        (Bing + DDG image sweep, 32 queries)
  own_site_media.json <- coachcarter.com WP media API (Coach's own site)
  MANUAL list below   <- AP Newsroom, Mercury News, CC Pulse, YouTube, Flickr, etc. (hand-verified 2026-11-09)

Usage paths: own | embed-free | license | news-link-only
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "tracking/investigation"

CH = {
    "1999": "1. Richmond High era & 1999 lockout (1997-2004)",
    "torch": "2. 2002 Olympic torch",
    "film": "3. 2004-05 film / premiere / press tour / TV",
    "celeb": "4. With celebrities",
    "keynote": "5. Keynotes & events 2005-2026",
    "slamball": "6. SlamBall (2002 & 2023)",
    "academy": "7. Impact Academy / Foundation / service",
    "rich2024": "8. Richmond High return (Dec 2024)",
    "portrait": "9. Portraits & press",
}

KNOWN_IDS = set("""51962763 51962765 51962845 51962885 51962893 51962460 105411240 105393720 105381434
105593879 105593871 112420039 524771034 110239085 110239084 51962463 51962462 51962473 51962465
51962464 51962467 118036980 118040756 106848387 107285579 115144906 104862816 79508039 490354604
490354622 490354624 490354626 490356552""".split())


def known_getty(gid):
    g = int(gid)
    return (gid in KNOWN_IDS or 117806643 <= g <= 118041347 or 1556010530 <= g <= 1582372540
            or 2226407600 <= g <= 2226407674)


def getty_chapter(cap):
    c = cap or ""
    if re.search(r"SlamBall|Rumble", c): return "slamball"
    if re.search(r"Richmond High School coach|Envision", c): return "rich2024"
    if re.search(r"Life is Beautiful|Festival goers", c, re.I): return "keynote"
    if re.search(r"Aaron|Banks|Dean Cain|Gault|Dr\. Phil|Mary Bono|Lansing|Ashanti|Sharla|Oden|Greenberg", c): return "celeb"
    if re.search(r"^Coach Ken Carter \(Photo", c): return "portrait"
    return "film"


# ---------------- hand-verified items not reachable by the scripts ----------------
MANUAL = [
    # 1999 / Richmond era
    dict(chapter="1999", title="Carter talks to students in Richmond High's library; donated new jerseys (Jan 4 2004)",
         date="2004-01-04", source_page="https://www.mercurynews.com/2024/12/05/coach-carter-is-back-at-richmond-basketball-2024/",
         thumb="https://www.mercurynews.com/wp-content/uploads/2024/12/BNG-L-CARTER-1206.jpg?w=600",
         photographer="Doug Duran", agency="Contra Costa Times / Bay Area News Group archive", rights_holder="MediaNews Group (Bay Area News Group)",
         usage="license", origin="news:mercurynews", note="Lead image of Mercury News 2024-12-05 story; gallery also has Jan 2005 Courtney Anderson alumni-game photo (Doug Duran)"),
    dict(chapter="1999", title="Oakland Raiders TE / 1999 Richmond player Courtney Anderson talks to Coach Carter at alumni game (Jan 4 2005)",
         date="2005-01-04", source_page="https://www.mercurynews.com/2024/12/05/coach-carter-is-back-at-richmond-basketball-2024/",
         thumb=None, photographer="Doug Duran", agency="Contra Costa Times / Bay Area News Group archive",
         rights_holder="MediaNews Group (Bay Area News Group)", usage="license", origin="news:mercurynews"),
    *[dict(chapter="1999", title=f"AP Newsroom 'Dream Team' — 5-year lockout anniversary alumni game, Richmond (Jan 12-13 2004), AP ID {i}",
           date="2004-01-12", source_page=f"https://newsroom.ap.org/editorial-photos-videos/search?query=ken%20carter%20coach&mediaType=photo",
           thumb=None, photographer="Jeff Chiu (AP)", agency="Associated Press", rights_holder="AP",
           usage="license", origin="apnewsroom", ext_id=i, note="Same shoot as Alamy 2PF2XGR/2PF2XH1/2PF2XH5; license US use direct from AP Newsroom")
      for i in ("04011305666", "04011305167", "04011304872", "04011305434")],
    # torch
    dict(chapter="torch", title="'Coach Carter Olympic Torch 2002' — video on Coach's own YouTube channel @coachkencarter (2012-04-17)",
         date="2002-01-19", source_page="https://www.youtube.com/watch?v=PVuW6aQl8YQ",
         thumb="https://i.ytimg.com/vi/PVuW6aQl8YQ/hqdefault.jpg", thumb_local="thumbs/yt_PVuW6aQl8YQ.jpg",
         photographer=None, agency="Coach Ken Carter (own channel)", rights_holder="Coach Ken Carter (verify footage source)",
         usage="own", origin="youtube:own"),
    # film / press tour
    *[dict(chapter="film" if i != "041215019187" else "portrait",
           title=f"AP 'Film The Real Coach Carter' — Dallas interview/portrait session (Dec 15 2004), AP ID {i}",
           date="2004-12-15", source_page="https://newsroom.ap.org/editorial-photos-videos/search?query=ken%20carter%20coach&mediaType=photo",
           thumb=None, photographer="AP", agency="Associated Press", rights_holder="AP", usage="license", origin="apnewsroom", ext_id=i,
           note="Same shoot as Alamy 2NGCX92/2NGCX93/2NGCXAX")
      for i in ("041215019187", "041215019203", "041215019211")],
    dict(chapter="film", title="Ken Carter on set of 'Coach Carter' with Nana Gbewonyo, Antwon Tanner, Rick Gonzalez, Channing Tatum",
         date="2004", source_page="https://www.mercurynews.com/2024/12/05/coach-carter-is-back-at-richmond-basketball-2024/",
         thumb=None, photographer=None, agency="Photo courtesy of Ken Carter", rights_holder="Coach Ken Carter (personal photo)",
         usage="own", origin="news:mercurynews", note="Coach's own photo — ask him for the original file"),
    dict(chapter="film", title="Coach Ken Carter at LA premiere of 'Coach Carter', Chinese Theater (Jan 13 2005)",
         date="2005-01-13", source_page="https://depositphotos.com/editorial/coach-ken-carter-17062851.html",
         thumb="https://st.depositphotos.com/1814084/1706/i/950/depositphotos_17062851-stock-photo-coach-ken-carter.jpg",
         photographer="s_bukley", agency="Depositphotos (editorial)", rights_holder="s_bukley", usage="license", origin="sweep"),
    *[dict(chapter="film", title=f"Rex/Shutterstock editorial 'Coach Ken Carter' {i} (premiere, 2005)", date="2005-01-13",
           source_page=f"https://www.shutterstock.com/editorial/image-editorial/coach-ken-carter-{i}",
           thumb=None, photographer=None, agency="Rex Features / Shutterstock Editorial", rights_holder="Shutterstock",
           usage="license", origin="sweep", note="page blocks scripted fetch; caption from search title")
      for i in ("507729p", "507729k")],
    dict(chapter="celeb", title="Coach Ken Carter with Samuel L. Jackson (Rex/Shutterstock 507729ac)", date="2005-01-13",
         source_page="https://www.shutterstock.com/editorial/image-editorial/coach-ken-carter-samuel-l-jackson-507729ac",
         thumb="https://editorial01.shutterstock.com/wm-preview-1500/507729ac/b47dc5a7/Shutterstock_507729ac.jpg",
         photographer=None, agency="Rex Features / Shutterstock Editorial", rights_holder="Shutterstock", usage="license", origin="sweep"),
    dict(chapter="portrait", title="'Ken Carter, US high school basketball coach' (Rex/Shutterstock 8024063a, date unverified)", date=None,
         source_page="https://www.shutterstock.com/editorial/image-editorial/ken-carter-us-high-school-basketball-coach-8024063a",
         thumb="https://editorial01.shutterstock.com/preview-440/8024063a/17d7e3dd/Shutterstock_8024063a.jpg",
         photographer=None, agency="Rex Features / Shutterstock Editorial", rights_holder="Shutterstock", usage="license", origin="sweep",
         note="Possibly 1999-2005 era; open page in a browser to read date/caption"),
    dict(chapter="film", title="Coach Ken Carter at LA premiere (ImageCollect 219235)", date="2005-01-13",
         source_page="https://imagecollect.com/picture/ken-carter-photo-219235/coach-carter-los-angeles-premiere",
         thumb="http://imagecollect.com/picture/ken-carter-photo-219235/coach-carter-los-angeles-premiere.jpg",
         photographer=None, agency="ImageCollect", rights_holder="ImageCollect", usage="license", origin="sweep"),
    *[dict(chapter="film", title=f"UPI 'COACH CARTER PREMIERE' {n}", date="2005-01-13", source_page=u,
           thumb=f"https://cdnph.upi.com/pv/upi/{u.split('/')[6]}/HOLLYWOOD-PREMIERE.jpg", photographer="UPI", agency="UPI",
           rights_holder="UPI", usage="license", origin="sweep", note="check which frame shows Carter (UPI premiere set; Alamy TXXRRD is Carter)")
      for n, u in (("LAP2005011310", "https://www.upi.com/News_Photos/view/upi/8cd6c68476838e970a1d3c06cb975dc5/COACH-CARTER-PREMIERE/"),
                   ("LAP2005011309", "https://www.upi.com/News_Photos/view/upi/232439a8db8d660dd422335462085067/COACH-CARTER-PREMIERE/"))],
    # celebs / TV (own)
    dict(chapter="celeb", title="Coach Ken Carter, Samuel L. Jackson & Dr. Phil (labelled promo still, Dr. Phil show 2005)",
         date="2005", source_page="https://coachcarter.com/", thumb="https://coachcarter.com/wp-content/uploads/2022/02/coachcartercelebrities.png",
         thumb_local="thumbs/coachcarter_com_1367_coachcartercelebrities.png", photographer=None, agency="coachcarter.com",
         rights_holder="Coach Ken Carter / Dr. Phil (show still — confirm)", usage="own", origin="own:coachcarter.com"),
    dict(chapter="celeb", title="Dr. Phil set — Carter, Samuel L. Jackson, Dr. Phil (wide TV frame)", date="2005",
         source_page="https://coachcarter.com/", thumb="https://coachcarter.com/wp-content/uploads/2019/12/CoachCarterDrPhilandSamuelJackson.png",
         thumb_local="thumbs/coachcarter_com_1202_CoachCarterDrPhilandSamuelJackson-768x320.png", photographer=None, agency="coachcarter.com",
         rights_holder="Peteski Productions / CBS (TV frame)", usage="own", origin="own:coachcarter.com",
         note="TV frame on Coach's site; Dr. Phil clip also on his YouTube: https://www.youtube.com/watch?v=28kzO577IVw"),
    dict(chapter="celeb", title="Samuel L. Jackson and Coach Carter on location (street, film set)", date="2004",
         source_page="https://coachcarter.com/", thumb="https://coachcarter.com/wp-content/uploads/2019/12/Samuel-Jackson-and-Coach-Carter.jpg",
         thumb_local="thumbs/coachcarter_com_1228_Samuel-Jackson-and-Coach-Carter-300x197.jpg", photographer="unknown (likely Paramount unit still)",
         agency="coachcarter.com", rights_holder="Paramount/MTV Films? — confirm with Coach", usage="own", origin="own:coachcarter.com"),
    dict(chapter="celeb", title="Coach Carter and Samuel L. Jackson, arm around shoulder (event)", date=None,
         source_page="https://coachcarter.com/", thumb="https://coachcarter.com/wp-content/uploads/2019/12/Coach-Carter-and-Samuel-Jackson.jpg",
         thumb_local="thumbs/coachcarter_com_1211_Coach-Carter-and-Samuel-Jackson.jpg", photographer=None, agency="coachcarter.com",
         rights_holder="Coach Ken Carter (confirm)", usage="own", origin="own:coachcarter.com"),
    dict(chapter="celeb", title="'Rickey Smiley and Coach Carter' — Coach's YouTube (2012-02-14)", date="2012-02-14",
         source_page="https://www.youtube.com/watch?v=l-JuG82IsIQ", thumb="https://i.ytimg.com/vi/l-JuG82IsIQ/hqdefault.jpg",
         thumb_local="thumbs/yt_l-JuG82IsIQ.jpg", photographer=None, agency="YouTube @coachkencarter", rights_holder="Coach Ken Carter",
         usage="own", origin="youtube:own"),
    dict(chapter="celeb", title="'Coach Ken Carter on Dr Phil' — Coach's YouTube @kencarter8496 (posted 2022-02-05)", date="2005",
         source_page="https://www.youtube.com/watch?v=28kzO577IVw", thumb="https://i.ytimg.com/vi/28kzO577IVw/hqdefault.jpg",
         thumb_local="thumbs/yt_28kzO577IVw.jpg", photographer=None, agency="YouTube @kencarter8496", rights_holder="Coach (upload) / CBS (show)",
         usage="own", origin="youtube:own"),
    # keynotes
    dict(chapter="keynote", title="Coach Carter speaking, arms wide, packed gym (site hero)", date=None, source_page="https://coachcarter.com/",
         thumb="https://coachcarter.com/wp-content/uploads/2019/12/coachcarter_opt-1.jpg", thumb_local="thumbs/coachcarter_com_1198_coachcarter_opt-1-300x300.jpg",
         photographer=None, agency="coachcarter.com", rights_holder="Coach Ken Carter (confirm photographer)", usage="own", origin="own:coachcarter.com"),
    dict(chapter="keynote", title="Coach Carter – Speaker (on stage with mic)", date=None, source_page="https://coachcarter.com/",
         thumb="https://coachcarter.com/wp-content/uploads/2019/12/Coach-Carter-Speaker.jpg", thumb_local="thumbs/coachcarter_com_1212_Coach-Carter-Speaker-236x300.jpg",
         photographer=None, agency="coachcarter.com", rights_holder="Coach Ken Carter (confirm photographer)", usage="own", origin="own:coachcarter.com"),
    dict(chapter="keynote", title="'Coach Ken Carter - Speaker' reel — YouTube @kencarter8496 (2023-01-10)", date="2023-01-10",
         source_page="https://www.youtube.com/watch?v=VkpVPjp-_F8", thumb="https://i.ytimg.com/vi/VkpVPjp-_F8/hqdefault.jpg",
         thumb_local="thumbs/yt_VkpVPjp-_F8.jpg", photographer=None, agency="YouTube own", rights_holder="Coach Ken Carter", usage="own", origin="youtube:own"),
    dict(chapter="keynote", title="'Coach Carter Shooting Hoops at Baylor' — YouTube own (2019-09-11)", date="2019-09-11",
         source_page="https://www.youtube.com/watch?v=isjo1tHO2x8", thumb="https://i.ytimg.com/vi/isjo1tHO2x8/hqdefault.jpg",
         thumb_local="thumbs/yt_isjo1tHO2x8.jpg", photographer=None, agency="YouTube own", rights_holder="Coach Ken Carter", usage="own", origin="youtube:own"),
    dict(chapter="keynote", title="'They Call Me Coach' — YouTube @coachkencarter (2011-05-23)", date="2011-05-23",
         source_page="https://www.youtube.com/watch?v=1GCIavx0HMM", thumb="https://i.ytimg.com/vi/1GCIavx0HMM/hqdefault.jpg",
         thumb_local="thumbs/yt_1GCIavx0HMM.jpg", photographer=None, agency="YouTube own", rights_holder="Coach Ken Carter", usage="own", origin="youtube:own"),
    dict(chapter="keynote", title="'Get Coached by The Real Coach Carter' / 'Coach Ken Carter Trailer' — YouTube own (2018)", date="2018-02-27",
         source_page="https://www.youtube.com/watch?v=3-57R3Oanfw", thumb="https://i.ytimg.com/vi/3-57R3Oanfw/hqdefault.jpg",
         thumb_local="thumbs/yt_3-57R3Oanfw.jpg", photographer=None, agency="YouTube own", rights_holder="Coach Ken Carter", usage="own", origin="youtube:own"),
    dict(chapter="keynote", title="Coach Ken Carter honored at CYC's Highest Office event (May 12 2006)", date="2006-05-12",
         source_page="https://www.flickr.com/photos/erepublic/3963692648", thumb="https://live.staticflickr.com/3496/3963692648_79c16f150d_z.jpg",
         photographer="e.Republic (Flickr)", agency="Flickr", rights_holder="e.Republic", usage="embed-free", origin="sweep", note="Flickr embed; check CC license"),
    dict(chapter="keynote", title="Carter speaks at Dakota Collegiate Institute, Winnipeg (Apr 24 2014)", date="2014-04-24",
         source_page="https://www.flickr.com/photos/65205697@N04/14009951904/", thumb="https://live.staticflickr.com/7035/14009951904_62109409b9_b.jpg",
         photographer="Flickr user 65205697@N04 (Louis Riel SD?)", agency="Flickr", rights_holder="uploader", usage="embed-free", origin="sweep", note="Flickr embed; check CC license"),
    dict(chapter="keynote", title="FIVE STAR Speakers promo — Coach Ken Carter (May 25 2008)", date="2008-05-25",
         source_page="https://www.flickr.com/photos/13381743@N07/2520704402/", thumb="https://live.staticflickr.com/3257/2520704402_f841030e4e.jpg",
         photographer="FIVE STAR Speakers", agency="Flickr", rights_holder="FIVE STAR Speakers", usage="embed-free", origin="sweep"),
    # academy / service
    *[dict(chapter="academy", title=t, date=d, source_page=f"https://www.youtube.com/watch?v={v}", thumb=f"https://i.ytimg.com/vi/{v}/hqdefault.jpg",
           thumb_local=f"thumbs/yt_{v}.jpg", photographer=None, agency="YouTube own", rights_holder="Coach Ken Carter", usage="own", origin="youtube:own")
      for v, t, d in (("pGShjPueprM", "'Coach Ken Carter in Guatemala' — YouTube @coachkencarter", "2011-05-12"),
                      ("iUWk4NWkcww", "'Coach Carter in Guatemala' (2nd video) — YouTube @coachkencarter", "2012-01-26"),
                      ("gMRD2rtJdu0", "'Coach Carter Impact Academy Garden' — YouTube @coachkencarter", "2011-06-08"),
                      ("linNoPt8YjE", "'Coach Carter in the CCIA Garden' — YouTube @coachkencarter", "2012-01-26"),
                      ("2WjAgv_wFWo", "'Coach Carter's Impact Academy Garden' — YouTube @kencarter8496", None))],
    dict(chapter="academy", title="Coach Ken Carter continues to motivate after Impact Academy (article photos)", date=None,
         source_page="https://hollywoodmask.com/sports/coach-ken-carter-impact-academy.html", thumb=None, photographer=None,
         agency="hollywoodmask.com", rights_holder="unknown", usage="news-link-only", origin="sweep"),
    # richmond 2024
    dict(chapter="rich2024", title="Ken Carter in Richmond #12 hoodie between two players, first game back (Dec 12 2024)", date="2024-12-12",
         source_page="https://ccpulse.org/2024/12/16/coach-carter-returns-to-lead-richmond-high-after-more-than-20-years",
         thumb="https://ccpulse.org/wp-content/uploads/2024/12/1-Carter2players-1.jpg", photographer="Joe Porrello",
         agency="Contra Costa Pulse (Richmond Pulse)", rights_holder="Joe Porrello / CC Pulse", usage="license", origin="news:ccpulse",
         note="CC Pulse gallery of 8 (huddle, autographs, break-the-huddle) — nonprofit outlet; ask permission/credit"),
    dict(chapter="rich2024", title="CC Pulse: Carter signs autographs for Envision Academy players after game (Dec 12 2024)", date="2024-12-12",
         source_page="https://ccpulse.org/2024/12/16/coach-carter-returns-to-lead-richmond-high-after-more-than-20-years",
         thumb=None, photographer="Joe Porrello", agency="Contra Costa Pulse", rights_holder="Joe Porrello / CC Pulse", usage="license", origin="news:ccpulse"),
    dict(chapter="rich2024", title="CC Pulse: Oilers head coach Ken Carter and team break the huddle after halftime (Dec 12 2024)", date="2024-12-12",
         source_page="https://ccpulse.org/2024/12/16/coach-carter-returns-to-lead-richmond-high-after-more-than-20-years",
         thumb=None, photographer="Joe Porrello", agency="Contra Costa Pulse", rights_holder="Joe Porrello / CC Pulse", usage="license", origin="news:ccpulse"),
    dict(chapter="rich2024", title="Mercury News: 'Coach Carter's first game back at Richmond High…' (Jane Tyska gallery)", date="2024-12-12",
         source_page="https://www.mercurynews.com/2024/12/13/coach-carters-first-game-back-at-richmond-high-underscores-how-times-have-changed/",
         thumb="https://www.mercurynews.com/wp-content/uploads/2024/12/BNG-L-COACHCARTER-1214-3.jpg?w=600", photographer="Jane Tyska",
         agency="Bay Area News Group", rights_holder="MediaNews Group", usage="license", origin="news:mercurynews",
         note="Same shoot sold via Getty 2226407600-674 (no Getty embed)"),
    dict(chapter="rich2024", title="Mercury News 'They said it: Coming back for more' (Jane Tyska; also AP/Matt Kelley file photo)", date="2024-12-15",
         source_page="https://www.mercurynews.com/2024/12/15/they-said-it-coming-back-for-more/",
         thumb="https://www.mercurynews.com/wp-content/uploads/2024/12/BNG-L-COACHCARTER-1214-17.jpg?w=600", photographer="Jane Tyska",
         agency="Bay Area News Group", rights_holder="MediaNews Group", usage="license", origin="news:mercurynews"),
    # portraits
    dict(chapter="portrait", title="COACH KEN — studio portrait, suit & red tie, white seamless (site, 2025)", date="2025-06-03",
         source_page="https://coachcarter.com/", thumb="https://coachcarter.com/wp-content/uploads/2025/06/COACH-KEN.jpg",
         thumb_local="thumbs/coachcarter_com_1663_COACH-KEN-300x240.jpg", photographer=None, agency="coachcarter.com",
         rights_holder="Coach Ken Carter", usage="own", origin="own:coachcarter.com", note="Only 619 px wide online — request hi-res original"),
    dict(chapter="portrait", title="Official accounts: X/Twitter @CoachKCarter, Facebook /Coachkcarter, YouTube @coachkencarter + @kencarter8496",
         date=None, source_page="https://twitter.com/CoachKCarter", thumb="https://pbs.twimg.com/media/DBvZrYlUAAAIN8H?format=jpg&name=large",
         photographer=None, agency="Coach's social", rights_holder="Coach Ken Carter", usage="own", origin="sweep",
         note="Instagram handle not confirmed (login wall) — ask Coach; 'Olympic Torch Moment' IG post not reachable without login"),
]

# speaker-bureau / news pages from the sweep worth keeping as news-link-only (they host his headshots/event photos)
SWEEP_DOMAINS = {
    "eaglestalent.com": "portrait", "bigspeak.com": "portrait", "premierespeakers.com": "portrait", "capcityspeakers.com": "portrait",
    "executivespeakers.com": "portrait", "pdaspeakers.com": "portrait", "scarlettentertainment.com": "portrait",
    "corporatespeakeragency.com": "portrait", "goodmanspeakers.com": "portrait", "chartwellspeakers.com": "portrait",
    "el-talent.com": "portrait", "slamballleague.com": "slamball", "prismnews.com": "slamball",
    "wkbn.com": "keynote", "wkrg.com": "keynote", "cbc.ca": "keynote", "atmorenews.com": "keynote", "desertsun.com": "keynote",
    "wfmj.com": "keynote", "wktv.com": "keynote", "kfdm.com": "keynote", "krcrtv.com": "keynote", "bcaproud.com": "keynote",
    "mysweetcharity.com": "keynote", "socialwhirl.com": "keynote", "thewichitan.com": "keynote", "washingtoninformer.com": "keynote",
    "contractingbusiness.com": "keynote", "members.asicentral.com": "keynote", "weartv.com": "keynote", "givebutter.com": "keynote",
    "georgefox.edu": "1999", "myhero.com": "portrait", "wacotrib.com": "keynote",
    "distractify.com": "portrait", "fanbuzz.com": "portrait", "screenrant.com": "portrait", "facebook.com": "portrait",
}


def alamy_is_subject(cap):
    if re.search(r"Stunt Driver|evacuee|Avalon|Amtrak|Newingotn|Psychiatric|MOVIE TITLE|TV/FILM STILLS|as Ken Carter|as .Coach Ken Carter", cap): return False
    if "true story of" in cap and not cap.strip().startswith("Coach Ken Carter"): return False
    if "Characters:" in cap and "& Ken Carter Film" not in cap: return False
    return bool(re.search(r"ken carter", cap, re.I))


def alamy_chapter(cap, date):
    if "Olympic torch" in cap: return "torch"
    if "Richmond High School" in cap and date.startswith("2004-01"): return "1999"
    if re.search(r"Tracee|Samuel L\. Jackson &", cap): return "celeb"
    if re.search(r"Dallas", cap): return "film"
    if re.search(r"autograph|Mississippi University", cap): return "keynote"
    return "film"


def main():
    items = []
    # Getty
    for g in json.loads((INV / "getty_hits.json").read_text()):
        gid = g["getty_id"]
        cap = g.get("caption") or ""
        if gid.startswith("22264"):
            cap = cap or "Richmond High School coach Ken Carter vs Envision Academy, Richmond Calif., Dec 12 2024 (Jane Tyska/Digital First Media/East Bay Times via Getty Images)"
        embed = bool(g.get("embed_ok"))
        items.append(dict(id=f"getty:{gid}", chapter=getty_chapter(cap), title=cap[:300], date=None,
                          source_page=g.get("page") or f"https://www.gettyimages.com/detail/{gid}", thumb=g.get("thumb") or f"https://media.gettyimages.com/id/{gid}/photo/x.jpg?s=612x612",
                          photographer=g.get("photographer") or ("Jane Tyska" if gid.startswith("22264") else None),
                          agency=f"Getty Images / {g.get('collection')}" if g.get("collection") else "Getty Images (East Bay Times via Getty)",
                          rights_holder="Getty Images" if embed else "MediaNews Group/East Bay Times via Getty",
                          usage="embed-free" if embed else "license",
                          embed=f"https://embed.gettyimages.com/oembed?url=https://gty.im/{gid}" if embed else None,
                          commercial_path="Getty license (embed is editorial/non-commercial only)",
                          source="known" if known_getty(gid) else "getty_search_2026-11-09"))
    # Alamy
    for a in json.loads((INV / "alamy_hits.json").read_text()):
        cap = a["caption"]
        if not alamy_is_subject(cap): continue
        m = re.search(r"(?:Photo(?: Credit)?:? by:?|Credit Image: ©|\(AP Photo/|photo by)\s*([^.)/]+)", cap, re.I)
        items.append(dict(id=f"alamy:{a['alamy_ref']}", chapter=alamy_chapter(cap, a["date"]), title=cap[:300], date=a["date"] or None,
                          source_page=a["page"], thumb=a["thumb"], photographer=m.group(1).strip() if m else None,
                          agency=f"Alamy / {a['supplier']}", rights_holder=a["supplier"], usage="license",
                          commercial_path=f"Alamy {a['license']} ({a['collection']})" + (" — AP items only licensable outside US on Alamy; US = AP Newsroom" if a['supplier'] == 'Associated Press' else ""),
                          source="alamy_search_2026-11-09"))
    # Own site
    # Own site: own_site_media.json is curated into MANUAL (film stills / theme stock in the WP library excluded)
    # Manual
    for i, m in enumerate(MANUAL):
        m = dict(m); m.setdefault("thumb_local", None)
        ext = m.pop("ext_id", None)
        m["id"] = f"ap:{ext}" if ext else f"manual:{i:03d}"
        m["source"] = m.pop("origin")
        items.append(m)
    # Sweep: news/speaker pages (news-link-only), dedupe against existing pages
    have = {it["source_page"] for it in items}
    raw = json.loads((INV / "raw_sweep.json").read_text())["results"]
    for r in raw:
        page = r.get("source_page") or ""
        dom = re.sub(r"^www\.", "", page.split("/")[2]) if page.count("/") >= 2 else ""
        ch = next((v for k, v in SWEEP_DOMAINS.items() if dom.endswith(k)), None)
        if not ch or page in have: continue
        if dom.endswith("facebook.com") and "Coachkcarter" not in page: continue
        if re.search(r"Movie CLIP", r["title"]): continue  # film clips, not photos of Coach
        have.add(page)
        items.append(dict(id=f"sweep:{len(items)}", chapter=ch, title=r["title"][:200], date=None, source_page=page,
                          thumb=r.get("thumb_url"), image_url=r.get("image_url"), photographer=None, agency=dom,
                          rights_holder="unknown (site/bureau; usually Coach-supplied headshot)" if ch == "portrait" else dom,
                          usage="own" if "facebook.com/Coachkcarter" in page else "news-link-only", source="img_sweep"))

    top_ids = ["alamy:3A9HP7M", "alamy:3A9HP8J", "TORCHVID", "alamy:2PF2XH1", "alamy:2PF2XH5", "MERC2004",
               "getty:51962763", "getty:51962765", "getty:110239084", "SETPHOTO", "getty:51962463", "getty:51962473",
               "alamy:2NGCX93", "getty:117809466", "getty:490354604", "getty:1501185142", "getty:1581523881",
               "getty:2226407644", "CCPULSE", "SITEPORTRAIT"]
    alias = {"TORCHVID": "youtube.com/watch?v=PVuW6aQl8YQ", "MERC2004": "BNG-L-CARTER-1206", "SETPHOTO": "Samuel-Jackson-and-Coach-Carter.jpg",
             "CCPULSE": "1-Carter2players-1.jpg", "SITEPORTRAIT": "COACH-KEN.jpg"}
    rank = {}
    for n, t in enumerate(top_ids, 1):
        for it in items:
            if it["id"] == t or (t in alias and alias[t] in ((it.get("source_page") or "") + (it.get("thumb") or ""))):
                rank[it["id"]] = n; break
    for it in items:
        it["top20"] = rank.get(it["id"])
        it["chapter_label"] = CH[it["chapter"]]

    items.sort(key=lambda x: (x["chapter_label"], x["top20"] or 99, x.get("date") or "9999", x["id"]))
    (INV / "photos.json").write_text(json.dumps({"generated": "2026-11-09", "count": len(items),
                                                 "chapters": CH, "items": items}, indent=1))
    write_md(items)
    from collections import Counter
    print(Counter(i["chapter_label"] for i in items)); print(Counter(i["usage"] for i in items)); print("top20 matched", len(rank))


def write_md(items):
    from collections import Counter, defaultdict
    by = defaultdict(list)
    for it in items: by[it["chapter_label"]].append(it)
    L = ["# Coach Ken Carter — public photo inventory", "",
         "Generated 2026-11-09 by `tools/investigate/build_photos.py` (sources: Getty search + oEmbed, Alamy search API [US+GB geo], "
         "AP Newsroom, Bing/DDG image sweep of 32 queries, coachcarter.com media library, Coach's two YouTube channels, news pages). "
         "Nothing stock/news was downloaded; `thumbs/` holds only Coach's own site + own-YouTube thumbnails.", "",
         "**Usage paths** — `own`: Coach's own posts/site (confirm he holds rights to set/TV frames) · `embed-free`: Getty embed / YouTube / Flickr embed "
         "(editorial, non-commercial context only) · `license`: Alamy, AP, Getty (non-embeddable), Shutterstock, news photo desks · `news-link-only`: link to article.", "",
         "## Counts", "", "| Chapter | Items |", "|---|---|"]
    for ch in sorted(by): L.append(f"| {ch} | {len(by[ch])} |")
    c = Counter(i["usage"] for i in items)
    L += ["", "Usage: " + ", ".join(f"{k} {v}" for k, v in c.most_common()), "", "## Top 20 for the website", "",
          "| # | Item | Chapter | Path | Credit |", "|---|---|---|---|---|"]
    for it in sorted([i for i in items if i["top20"]], key=lambda x: x["top20"]):
        L.append(f"| {it['top20']} | [{it['title'][:110]}]({it['source_page']}) | {it['chapter_label'].split('.')[0]} | {it['usage']} | {it.get('photographer') or it.get('agency') or ''} |")
    L += ["", "## Gaps (searched, not found publicly)", "",
          "- **1999 lockout itself (padlocked gym, team, Jan 1999 press):** no 1999 frames on Getty, Alamy (US+GB), AP Newsroom (queries: ken carter richmond / coach / benched / richmond high basketball). "
          "Earliest Richmond-gym photos found = AP Jeff Chiu 5-yr anniversary alumni game Jan 2004 + Doug Duran (Contra Costa Times) Jan 2004. "
          "1999 originals likely sit in SF Chronicle / Contra Costa Times (now Bay Area News Group) print archives — request via their photo desks, or from Coach's scrapbook.",
          "- **Prince courtside, Best Damn Sports Show, Oprah/Today/GMA 1999:** no public photo found on Getty, Alamy, AP, Bing/DDG image indices or Coach's site/YouTube. Treat as Coach's personal archive — ask him for originals (or TV frame grabs with network clearance).",
          "- **2002 SlamBall season:** no Getty/Alamy frames of Carter (only 2023 Rumble). ",
          "- **Instagram:** handle unconfirmed; IG posts not reachable without login (not attempted).",
          "- **SFGATE 'Calling his own shots' / East Bay Times 'Real Coach Carter sticks to script':** headlines not found by web search; Mercury News 2024 pieces reachable and logged.", ""]
    for ch in sorted(by):
        L += [f"## {ch}", "", "| Top | Title / caption | Date | Credit | Path | Source page | Thumb |", "|---|---|---|---|---|---|---|"]
        for it in by[ch]:
            title = (it["title"] or "").replace("|", "/").replace("\n", " ")[:160]
            th = it.get("thumb_local") or it.get("thumb") or ""
            L.append(f"| {it['top20'] or ''} | {title} | {it.get('date') or ''} | {(it.get('photographer') or '')} / {it.get('agency') or ''} | "
                     f"{it['usage']} | [link]({it['source_page']}) | {('[thumb](' + th + ')') if th else ''} |")
        L.append("")
    (INV / "PHOTOS.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
