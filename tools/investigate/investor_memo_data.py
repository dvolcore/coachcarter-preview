"""Investor memo data -> site/assets/data/memo.json.
Sources: ~/Desktop/Coach Carter Brand Research - 2026-11-09/ (Claude_Coach_Carter_Brand_Valuation_Playbook.md,
Coach_Carter_Billion_Dollar_Brand.md, model CSVs) + tracking/investigation (film_stats.json, cpi_u.json).
Every modeled number is labeled as an estimate in the page; facts carry their source URL."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "tracking/investigation"
cpi = json.loads((INV / "cpi_u.json").read_text())
ANN = {int(k): v for k, v in cpi["annual"].items()}
NOW = cpi["latest"][1]
fs = json.loads((INV / "film_stats.json").read_text())


def today(usd, year):
    return round(usd * NOW / ANN[year] / 1e6, 1)


film_money = [
    {"label": "Opening weekend", "nominal": 24.2, "today": today(24182961, 2005)},
    {"label": "MLK four-day opening", "nominal": 29.2, "today": today(29168181, 2005)},
    {"label": "Domestic box office", "nominal": 67.3, "today": today(67264877, 2005)},
    {"label": "Worldwide box office", "nominal": 76.7, "today": today(76670000, 2005)},
]
rows = fs["basketball_rank"]["chart_rows"]
basketball = [{"title": r["title"], "year": int(r["release"][-4:]), "nominal": round(r["domestic_usd"] / 1e6, 1),
               "today": today(r["domestic_usd"], int(r["release"][-4:]))} for r in rows]

memo = {
    "cpi_note": f"Today's dollars use the U.S. Bureau of Labor Statistics CPI-U (CUUR0000SA0), release-year annual average to September 2026 ({NOW}).",
    "cpi_source": "https://www.bls.gov/cpi/data.htm",
    "film_money": film_money,
    "basketball": basketball,
    "basketball_source": fs["basketball_rank"]["chart_source"],
    "mojo_ticket_adjusted": 125.5,
    # comparable true-story subjects (Claude playbook; net worths are unaudited tiers)
    "fee_comps": [
        {"label": "Kurt Warner", "film": "American Underdog", "lo": 100, "hi": 200},
        {"label": "Tony Dungy", "film": "Coach / author", "lo": 100, "hi": 200},
        {"label": "Chris Gardner", "film": "The Pursuit of Happyness", "lo": 50, "hi": 94},
        {"label": "Lou Holtz", "film": "Coach / TV", "lo": 50, "hi": 75},
        {"label": "Michael Oher", "film": "The Blind Side", "lo": 30, "hi": 50},
        {"label": "Bethany Hamilton", "film": "Soul Surfer", "lo": 30, "hi": 50},
        {"label": "Coach Ken Carter", "film": "Coach Carter", "lo": 10, "hi": 20, "hl": True},
        {"label": "Rudy Ruettiger", "film": "Rudy", "lo": 10, "hi": 20},
    ],
    "fee_source": "Speaker-bureau listings compiled in the Coach Carter Brand Valuation Playbook (Nov 2026): Key Speakers, AthleteSpeakers, All American Speakers, BigSpeak.",
    # year-3 revenue lines ($M) — estimates
    "revenue_lines": [
        {"label": "Keynotes repriced to $30–50K", "lo": 0.9, "hi": 2.5},
        {"label": "Video podcast", "lo": 0.3, "hi": 5.0},
        {"label": "Brand-funded micro-drama seasons", "lo": 0.3, "hi": 1.8},
        {"label": "Documentary (archive, EP, subject fee)", "lo": 0.25, "hi": 1.0},
        {"label": "Coach Carter II series / sequel fees", "lo": 0.5, "hi": 3.0},
        {"label": "The Contract school program", "lo": 0.5, "hi": 3.0},
        {"label": "Corporate leadership course", "lo": 0.25, "hi": 2.0},
        {"label": "Coach Carter camps", "lo": 0.5, "hi": 2.0},
        {"label": "AI voice & likeness license", "lo": 0.5, "hi": 2.5},
        {"label": "Merch, memberships, licensing", "lo": 0.2, "hi": 1.5},
    ],
    # valuation ladder ($M) — estimates with stated odds
    "ladder": [
        {"label": "As-is (today)", "rev": "$0.2–0.6M", "lo": 1, "hi": 3, "odds": "—", "what": "Keynote fees only; no owned media, store or list"},
        {"label": "Base build · 12–24 mo", "rev": "$4–8M", "lo": 5, "hi": 15, "odds": "High if executed", "what": "New platform & socials, clip engine, podcast, 2 sponsored seasons, repriced speaking"},
        {"label": "Strong build · ~3 yrs", "rev": "$15–25M", "lo": 25, "hi": 75, "odds": "~20–30%", "what": "Documentary deal, Coach Carter II ordered, school & corporate programs, AI likeness license"},
        {"label": "Breakout", "rev": "$50–80M", "lo": 150, "hi": 320, "odds": "~5–10%", "what": "Owned values-media studio plus program, camp or academy network"},
        {"label": "$500M company", "rev": "$125–250M", "lo": 500, "hi": 500, "odds": "~10% · 7–10 yrs", "what": "Universe IP plus the club and academy network"},
        {"label": "$1B franchise", "rev": "$250–500M", "lo": 1000, "hi": 1000, "odds": "~5% · 7–10 yrs", "what": "Full stack: universe IP, clubs & academies, licensing, programs, platform stakes"},
    ],
    "stack": [
        {"label": "Story universe IP", "lo": 200, "hi": 450, "basis": "8–18× licensing & library revenue (Roald Dahl ~18×, SpringHill ~7×)"},
        {"label": "Clubs & Academy network", "lo": 250, "hi": 450, "basis": "12–15× EBITDA (Unrivaled Sports >$650M; IMG Academy $1.25B)"},
        {"label": "Licensing & consumer products", "lo": 80, "hi": 300, "basis": "8–12× royalties (Peanuts 23× EBITDA)"},
        {"label": "Programs: schools & companies", "lo": 50, "hi": 150, "basis": "2–4× revenue (FranklinCovey)"},
        {"label": "Platform stakes (AI / micro-drama)", "lo": 25, "hi": 100, "basis": "Option value (Lionsgate–Runway, Fox–Holywater)"},
    ],
    "comps": [
        {"name": "SpringHill (LeBron James)", "value": "$725M valuation, 2021", "url": "https://redbirdcap.com/wp-content/uploads/2021/10/TSHC-Announcement.pdf"},
        {"name": "Omaha Productions (Peyton Manning)", "value": "~$800M reported", "url": "https://omahaproductions.com/about/jamie-horowitz/"},
        {"name": "Unrivaled (3x3 basketball)", "value": "$650M in ~3 years", "url": "https://www.axios.com/2026/08/26/unrivaled-womens-basketball"},
        {"name": "Unrivaled Sports (youth facilities)", "value": ">$650M in 14 months", "url": "https://www.sportspro.com/news/unrivaled-sports-youth-harris-blitzer-investment-dicks-sporting-goods-may-2025/"},
        {"name": "IMG Academy", "value": "$1.25B sale", "url": "https://www.businesswire.com/news/home/20230425005615/en/Endeavor-Enters-Agreement-to-Sell-IMG-Academy-to-BPEA-EQT-in-Partnership-With-Nord-Anglia-Education-for-$1.25-Billion"},
        {"name": "Wrexham AFC", "value": "£2M → ~£350M on a docuseries", "url": "https://frontofficesports.com/article/wrexham-sale-valuation-growth-475-million/"},
        {"name": "Peanuts", "value": "~$219M → ~C$1.54B re-rating", "url": "https://s25.q4cdn.com/252078091/files/doc_news/WILDBRAIN-TO-SELL-ITS-41-STAKE-IN-PEANUTS-TO-SONY-FOR-630-MILLION-12-18-2025-2025.pdf"},
        {"name": "FranklinCovey", "value": "$261.5M annual revenue; 8,000+ schools", "url": "https://ir.franklincovey.com/news-releases/news-release-details/franklin-covey-reports-financial-results-fourth-quarter-and-0"},
    ],
    "revivals": [
        {"label": "Creed (Rocky)", "gap": 39}, {"label": "A Different World", "gap": 39}, {"label": "Top Gun: Maverick", "gap": 36},
        {"label": "Cobra Kai (Karate Kid)", "gap": 34}, {"label": "Bel-Air", "gap": 32}, {"label": "Happy Gilmore 2", "gap": 29},
        {"label": "Coach Carter · today", "gap": 21, "hl": True}, {"label": "Coach Carter · Jan 2030", "gap": 25, "hl": True},
    ],
    "cost_per_hour": [{"label": "Live-action vertical series", "v": 150}, {"label": "AI-assisted production", "v": 25, "range": "20–30"}],
    "cost_source": "https://www.thewrap.com/media-platforms/tv/ai-generated-microdramas-could-be-the-future-of-mobile-entertainment/",
}
(ROOT / "site/assets/data/memo.json").write_text(json.dumps(memo, indent=1))
print("film_money", film_money)
print("basketball today top5", sorted([(b["today"], b["title"]) for b in basketball], reverse=True)[:5])
