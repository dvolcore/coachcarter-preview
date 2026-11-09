"""Patch 10: Foundation/Academy diligence — stop presenting lapsed entities as active.
Per the brand research (IRS revocation list 2010; Texas entity forfeited 2015), the Foundation
is framed as being reconstituted and no donations are solicited until it is."""
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:80]}"
    p.write_text(s.replace(old, new, 1))


I = "src/impact.html"
sub(I, '"title": "Impact — Coach Ken Carter Foundation", "desc": "The Coach Ken Carter Foundation: education, training and mentoring for young people who need someone to hold them to a standard."',
    '"title": "Impact — The Coach Carter Standard in Communities", "desc": "Mentoring, study-first programs and school visits built on the Contract — and the relaunch of the Coach Ken Carter Foundation."')
sub(I, "<p class=\"lede\">The Coach Ken Carter Foundation provides education, training and mentoring for young people — so the next generation doesn't need a padlock to find its way.</p>",
    "<p class=\"lede\">Mentoring, study-first programs and school visits built on the Contract — so the next generation doesn't need a padlock to find its way.</p>")
sub(I, '<span class="eyebrow">Coach Ken Carter Foundation</span>', '<span class="eyebrow">Coach Ken Carter Foundation · relaunching</span>')
s = (R / I).read_text()
s = re.sub(r'<p class="lede" data-reveal>Founded and chaired by Coach Carter, the Foundation promotes.*?</p>',
           '<p class="lede" data-reveal>Coach founded the Coach Ken Carter Foundation to provide education, training and mentoring for young people. It is being reconstituted as the nonprofit home for the Contract programs — built on the same four rules: accountability, discipline, respect and education first.</p>', s, flags=re.S)
s = s.replace('<span class="eyebrow">Support the Foundation</span>', '<span class="eyebrow">Founding supporters</span>')
s = s.replace('<h2 class="h-l mt-s">Sponsor the<br><span class="gold-text">next fifteen.</span></h2>', '<h2 class="h-l mt-s">Be first in<br><span class="gold-text">for the relaunch.</span></h2>')
s = s.replace("<p class=\"lede mt-m\">Fund a mentoring cohort, a school visit or a season of study hall. Corporate partners receive an annual impact report.</p>",
              "<p class=\"lede mt-m\">The Foundation is being re-established. Leave your details and we'll contact founding supporters when giving opens — mentoring cohorts, school visits and study halls.</p>")
s = s.replace('data-simple="Thank you — the Foundation team will be in touch"', 'data-simple="Thank you — we\'ll be in touch when giving opens"')
s = s.replace('<button class="btn btn-gold" type="submit">Pledge support {{arr}}</button>', '<button class="btn btn-gold" type="submit">Notify me {{arr}}</button>')
s = s.replace("<p class=\"lede\" data-reveal>Founded in Marlin, Texas to help young people reach their full academic and life potential. The next chapter is in planning.</p>",
              "<p class=\"lede\" data-reveal>Opened in Marlin, Texas in 2009 to help young people reach their full academic and life potential. The next chapter is in planning.</p>")
(R / I).write_text(s)
for t in ["Founded in Marlin, Texas to help young people reach their full academic and life potential. The next chapter is in planning."]:
    s = (R / I).read_text(); (R / I).write_text(s.replace(t, "Opened in Marlin, Texas in 2009 to help young people reach their full academic and life potential. The next chapter is in planning."))

P = "src/playbook.html"
s = (R / P).read_text()
s = re.sub(r'<h3>Foundation Partner</h3><p>Underwrite study halls, mentoring cohorts and school visits through the Coach Ken Carter F.*?</p>',
           '<h3>Founding Foundation Partner</h3><p>Help relaunch the Coach Ken Carter Foundation as the nonprofit home for study halls, mentoring cohorts and school visits — with an annual impact report.</p>', s, flags=re.S)
s = s.replace('<div><span>Impact</span><b>The Foundation</b><small>Coach Ken Carter Foundation</small></div>', '<div><span>Impact</span><b>The Foundation</b><small>Relaunching as the nonprofit arm</small></div>')
(R / P).write_text(s)

B = "src/brand.html"
s = (R / B).read_text()
s = s.replace("founder and chairman of the Coach Ken Carter Foundation,", "founder of the Coach Ken Carter Foundation,")
(R / B).write_text(s)
print("patch_10 ok")
