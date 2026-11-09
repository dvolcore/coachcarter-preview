"""Patch 03: accuracy wording + non-link rows."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:70]}"
    p.write_text(s.replace(old, new))


sub("src/record.html", '<span data-count="140">0</span>+</div><div class="l">Editorial photos in the<br>Getty Images archive',
    '<span data-count="140">0</span></div><div class="l">Editorial photos in the<br>Getty Images archive')
sub("src/partners.html", '<span data-count="25">0</span> yrs</div>', '<span data-count="25">0</span>+ yrs</div>')
sub("site/assets/css/site.css", ".appear .go { width: 44px;", ".appear div.r .go { opacity: .3; }\n.appear .go { width: 44px;")
print("ok")
