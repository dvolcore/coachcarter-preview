"""Patch: footer year selector bug + faster intro curtain."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:60]}"
    p.write_text(s.replace(old, new))


sub("site/assets/js/site.js",
    '$$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });',
    '$$("[data-curyear]").forEach((el) => { el.textContent = new Date().getFullYear(); });')
sub("site/assets/js/site.js",
    '''  if (document.readyState === "complete") setTimeout(reveal, 500);
  else addEventListener("load", () => setTimeout(reveal, 400));
  setTimeout(reveal, 2600); // never trap the visitor behind the curtain''',
    '''  // lift as soon as fonts are ready (never wait on video); hard cap 1.6 s
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => setTimeout(reveal, 250));
  setTimeout(reveal, 1600);''')
sub("tools/build.py", "<span data-year>2026</span>", "<span data-curyear>2026</span>")
sub("site/assets/css/site.css", "transition: transform 1.6s var(--ease-io) .3s; }", "transition: transform 1.4s var(--ease-io) .1s; }")
sub("site/assets/css/site.css",
    ".loaded .reveal-mask { clip-path: inset(0 0 0 0); transition: clip-path 2.2s var(--ease-io) .9s; }",
    ".loaded .reveal-mask { clip-path: inset(0 0 0 0); transition: clip-path 1.8s var(--ease-io) .45s; }")
sub("site/assets/css/site.css",
    "transition: opacity 1.2s var(--ease) 1.6s, transform 1.2s var(--ease) 1.6s; }",
    "transition: opacity 1.1s var(--ease) 1s, transform 1.1s var(--ease) 1s; }")
print("patched")
