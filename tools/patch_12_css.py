"""Patch 12 (styles): film components — feature/trailer, scene rail, strip, quote band, real-vs-film, premiere, player."""
from pathlib import Path
C = Path(__file__).resolve().parent.parent / "site/assets/css/fx.css"
css = C.read_text()
M = "/* ---- the 2005 film ---- */"
if M not in css:
    css += "\n" + M + r"""
.ffeature { display: grid; grid-template-columns: 1.7fr 1fr; gap: 24px; align-items: stretch; }
.ftrailer { position: relative; display: block; padding: 0; border: 1px solid var(--line); border-radius: 22px; overflow: hidden; cursor: pointer; background: #000; aspect-ratio: 2.39 / 1; color: var(--chalk); text-align: left; }
.ftrailer img { width: 100%; height: 100%; object-fit: cover; transform: scale(1.02); transition: transform 1.2s var(--ease), filter .6s; filter: saturate(.92) contrast(1.05); }
.ftrailer:hover img { transform: scale(1.06); filter: saturate(1) contrast(1.08); }
.ft-over { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: flex-end; gap: 6px; padding: clamp(18px, 3vw, 34px); background: linear-gradient(180deg, rgba(8,9,11,0) 35%, rgba(8,9,11,.85)); }
.ft-over b { font: 400 clamp(38px, 5.4vw, 84px)/.9 "Cinzel", Georgia, serif; letter-spacing: .04em; background: var(--gold-grad); -webkit-background-clip: text; background-clip: text; color: transparent; }
.ft-cta { display: inline-flex; align-items: center; gap: 12px; margin-top: 6px; font: 600 13px/1 var(--f-head); letter-spacing: .2em; text-transform: uppercase; }
.fplay { display: inline-grid; place-items: center; width: 46px; height: 46px; border-radius: 50%; background: var(--gold); color: #101216; box-shadow: 0 0 0 6px rgba(184,130,46,.22); transition: transform .4s var(--ease); }
.fplay svg { width: 20px; height: 20px; margin-left: 2px; }
.ftrailer:hover .fplay, .fcard:hover .fplay { transform: scale(1.1); }
.ffacts { margin: 0; display: grid; align-content: center; gap: 0; border-top: 1px solid var(--line); }
.ffacts div { display: grid; grid-template-columns: 96px 1fr; gap: 14px; padding: 14px 0; border-bottom: 1px solid var(--line); }
.ffacts dt { font: 600 11px/1.6 var(--f-head); letter-spacing: .22em; text-transform: uppercase; color: var(--gold); }
.ffacts dd { margin: 0; color: rgba(245,240,232,.85); font-size: 15px; }
@media (max-width: 900px) { .ffeature { grid-template-columns: 1fr; } .ftrailer { aspect-ratio: 16 / 9; } }
.frail { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(280px, 30%); gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 26px 0 12px; scrollbar-width: thin; scrollbar-color: var(--gold-lo) transparent; }
.frail > div { scroll-snap-align: start; }
@media (max-width: 700px) { .frail { grid-auto-columns: 82%; } }
.fstrip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 1000px) { .fstrip { grid-template-columns: 1fr 1fr; } }
@media (max-width: 520px) { .fstrip { grid-template-columns: 1fr; } }
.fcard { display: grid; gap: 12px; width: 100%; padding: 0; border: 0; background: none; color: inherit; text-align: left; cursor: pointer; }
.fthumb { position: relative; display: block; aspect-ratio: 2.38 / 1; border-radius: 14px; overflow: hidden; background: #000; border: 1px solid var(--line); }
.fthumb img { width: 100%; height: 100%; object-fit: cover; transition: transform .9s var(--ease); }
.fcard:hover .fthumb img { transform: scale(1.06); }
.fthumb .fplay { position: absolute; left: 14px; bottom: 12px; width: 38px; height: 38px; }
.fthumb .fplay svg { width: 16px; height: 16px; }
.fthumb em { position: absolute; right: 10px; bottom: 10px; padding: 4px 8px; border-radius: 6px; background: rgba(8,9,11,.75); font: 600 11px/1 var(--f-body); font-style: normal; color: var(--chalk); }
.fmeta { display: grid; gap: 4px; }
.fmeta small { font: 600 11px/1 var(--f-head); letter-spacing: .2em; text-transform: uppercase; color: var(--gold); }
.fmeta b { font: 600 22px/1.05 var(--f-head); text-transform: uppercase; color: var(--chalk); }
.fmeta > span { color: var(--slate); font-size: 14px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.fmeta i { font-style: normal; font-size: 12px; color: rgba(245,240,232,.5); }
.light .fmeta b { color: var(--carbon); } .light .fmeta > span { color: #4a4e57; } .light .fmeta i { color: #6b6f78; }
.fcard:focus-visible { outline: 2px solid var(--gold-hi); outline-offset: 4px; border-radius: 14px; }
.fcredit { margin: 14px 0 0; font-size: 12px; color: var(--mute, rgba(245,240,232,.5)); }
.fquotes { display: grid; }
.fq { grid-area: 1 / 1; margin: 0; opacity: 0; visibility: hidden; transform: translateY(14px); transition: opacity .8s var(--ease), transform .8s var(--ease), visibility 0s .8s; display: grid; gap: 18px; justify-items: start; }
.fq.on { opacity: 1; visibility: visible; transform: none; transition-delay: 0s; }
.fq blockquote { margin: 0; font: 500 clamp(30px, 4vw, 58px)/1.1 var(--f-quote, Georgia, serif); font-style: italic; max-width: 26ch; color: var(--chalk); }
.light .fq blockquote { color: var(--carbon); }
.fq figcaption { display: grid; gap: 4px; }
.fq figcaption b { font: 600 14px/1 var(--f-head); letter-spacing: .2em; text-transform: uppercase; color: var(--gold-hi); }
.light .fq figcaption b { color: var(--gold-lo); }
.fq figcaption span { font-size: 13.5px; color: var(--slate); }
.light .fq figcaption span { color: #5a5e67; }
.fq .btn svg { width: 14px; height: 14px; }
.fq-dots { display: flex; gap: 8px; margin-top: 26px; }
.fq-dots button { width: 26px; height: 4px; padding: 0; border: 0; border-radius: 2px; background: var(--line-strong); cursor: pointer; transition: background .3s, width .3s; }
.light .fq-dots button { background: rgba(16,18,22,.18); }
.fq-dots button.on { width: 46px; background: var(--gold); }
@media (prefers-reduced-motion: reduce) { .fq { transition: none; } }
.freal { border-top: 1px solid var(--line); }
.fr-row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 28px; padding: 22px 0; border-bottom: 1px solid var(--line); align-items: start; }
.fr-row p { margin: 8px 0 0; color: rgba(245,240,232,.85); line-height: 1.55; }
.fr-row > div:nth-child(2) p { color: var(--slate); }
.fr-row nav { display: grid; gap: 4px; font-size: 12px; justify-items: end; }
@media (max-width: 800px) { .fr-row { grid-template-columns: 1fr; gap: 10px; } .fr-row nav { justify-items: start; grid-auto-flow: column; justify-content: start; gap: 14px; } }
.fprem { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
.fprem figcaption { display: grid; gap: 2px; margin-top: 10px; font-size: 13px; color: var(--slate); }
.fprem figcaption b { color: var(--chalk); font-weight: 600; }
@media (max-width: 900px) { .fprem { grid-template-columns: 1fr 1fr; } }
@media (max-width: 560px) { .fprem { grid-template-columns: 1fr; } }
.fplayer { position: fixed; inset: 0; z-index: 400; display: grid; place-items: center; padding: 20px; background: rgba(5,6,8,.9); backdrop-filter: blur(10px); opacity: 0; visibility: hidden; transition: opacity .35s, visibility 0s .35s; }
.fplayer.on { opacity: 1; visibility: visible; transition-delay: 0s; }
.fp-in { position: relative; width: min(1200px, 100%); }
.fp-box { position: relative; aspect-ratio: 16 / 9; border-radius: 16px; overflow: hidden; background: #000; box-shadow: 0 40px 120px -30px rgba(0,0,0,.9); }
.fp-box iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.fp-x { position: absolute; top: -52px; right: 0; width: 42px; height: 42px; border-radius: 50%; border: 1px solid var(--line-strong); background: rgba(8,9,11,.6); color: var(--chalk); font-size: 24px; line-height: 1; cursor: pointer; }
.fp-cap { margin: 12px 0 0; font: 600 12px/1.4 var(--f-head); letter-spacing: .16em; text-transform: uppercase; color: var(--gold-hi); }
.fp-cap span { color: var(--slate); }
html.fp-lock { overflow: hidden; }
.film-qband { padding-block: clamp(70px, 9vw, 130px); }
"""
    C.write_text(css)
print("patch_12_css ok")
