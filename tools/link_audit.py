#!/usr/bin/env python3
"""Read-only link / control audit for the built site (site/*.html).

Writes tracking/link_audit.json and tracking/LINK_AUDIT.md.
Exit code 1 if categories 1/2/4/5 (links, dead hrefs, assets, modals) have failures.
Python 3 stdlib only.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
TRACK = os.path.join(ROOT, "tracking")
JS_DIR = os.path.join(SITE, "assets", "js")
PRODUCTS_JSON = os.path.join(SITE, "assets", "data", "academy-products.json")
STORE_JS = os.path.join(JS_DIR, "store.js")
PRODUCT_JS = os.path.join(JS_DIR, "academy-product.js")

LABEL_WORDS = ["Book", "Shop", "Store", "Watch", "Preview", "Partner", "Investor",
               "Lookbook", "Archive", "Record", "Story"]
LABEL_RE = re.compile("|".join(LABEL_WORDS), re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.names = set()
        self.anchors = []
        self.buttons = []
        self.assets = []       # (kind, attr, value, extra, line)
        self.modals = []       # (value, tag, line)
        self.inline_scripts = []
        self._stack = []       # open elements: (tag, record or None)
        self._form_depth = 0
        self._in_script = False
        self._script_buf = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.names.add(a["name"])
        line = self.getpos()[0]
        rec = None
        if tag == "form":
            self._form_depth += 1
        if tag == "a":
            rec = {"tag": "a", "attrs": a, "text": [], "line": line,
                   "in_template": any(t == "template" for t, _r, _i in self._stack),
                   "anc_ids": [i for _t, _r, i in self._stack if i]}
            self.anchors.append(rec)
        elif tag == "button":
            rec = {"tag": "button", "attrs": a, "text": [], "line": line,
                   "in_form": self._form_depth > 0,
                   "anc_ids": [i for _t, _r, i in self._stack if i]}
            self.buttons.append(rec)
        if tag == "script":
            if a.get("src"):
                self.assets.append(("script", "src", a["src"], "", line))
            else:
                self._in_script = True
                self._script_buf = []
        if tag == "link" and a.get("href"):
            self.assets.append(("link", "href", a["href"], a.get("rel", ""), line))
        if tag == "img":
            for k in ("src", "data-src"):
                if a.get(k):
                    self.assets.append(("img", k, a[k], "", line))
            if a.get("srcset"):
                for part in a["srcset"].split(","):
                    u = part.strip().split(" ")[0]
                    if u:
                        self.assets.append(("img", "srcset", u, "", line))
            alt = a.get("alt", "")
            if alt:
                for _, r, _i in self._stack:
                    if r is not None:
                        r["text"].append(" [img:" + alt + "] ")
        if tag == "source":
            for k in ("src", "data-src", "srcset"):
                if a.get(k):
                    self.assets.append(("source", k, a[k].split(",")[0].strip().split(" ")[0], "", line))
        if tag == "video":
            for k in ("src", "data-src", "poster", "data-poster"):
                if a.get(k):
                    self.assets.append(("video", k, a[k], "", line))
        if tag not in ("img", "source", "video"):
            for k in ("data-video", "data-poster", "data-src"):
                if a.get(k):
                    self.assets.append((tag, k, a[k], "", line))
        if a.get("data-modal"):
            self.modals.append((a["data-modal"], tag, line))
        if tag not in VOID:
            self._stack.append((tag, rec, a.get('id', '')))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self._stack and self._stack[-1][0] == tag:
            self._stack.pop()

    def handle_endtag(self, tag):
        if tag == "script":
            if self._in_script:
                self.inline_scripts.append("".join(self._script_buf))
            self._in_script = False
        if tag == "form" and self._form_depth:
            self._form_depth -= 1
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break

    def handle_data(self, data):
        if self._in_script:
            self._script_buf.append(data)
            return
        for _, rec, _i in self._stack:
            if rec is not None:
                rec["text"].append(data)


def clean(txt):
    return re.sub(r"\s+", " ", "".join(txt)).strip()


def is_external(u):
    return u.lower().startswith(("http://", "https://", "//"))


def is_other_scheme(u):
    return bool(re.match(r"^(mailto|tel|sms|data|blob):", u, re.I))


def camel(attr):
    return re.sub(r"-([a-z])", lambda m: m.group(1).upper(), attr[5:])


def main():
    pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
    parsed = {}
    for f in pages:
        p = Page()
        p.feed(read(os.path.join(SITE, f)))
        parsed[f] = p

    js_files = sorted(f for f in os.listdir(JS_DIR) if f.endswith(".js"))
    js_text = {f: read(os.path.join(JS_DIR, f)) for f in js_files}
    inline_js = "\n".join(s for p in parsed.values() for s in p.inline_scripts)
    corpus = "\n".join(js_text.values()) + "\n" + inline_js
    data_text = ""
    ddir = os.path.join(SITE, "assets", "data")
    for f in os.listdir(ddir):
        if f.endswith(".json"):
            data_text += read(os.path.join(ddir, f))

    # product keys
    prod = json.loads(read(PRODUCTS_JSON))
    product_ids = {p["id"] for p in prod["products"]}
    pjs = read(PRODUCT_JS)
    alias_keys = set()
    for obj in ("jerseyStyles", "productAliases"):
        m = re.search(obj + r"\s*=\s*\{(.*?)\};", pjs, re.S)
        if m:
            alias_keys |= set(re.findall(r'"([^"]+)"\s*:', m.group(1)))
    valid_products = product_ids | alias_keys

    # store ?cat= handling: chip data-cat values + the scroll-only list in store.js
    store_html = read(os.path.join(SITE, "store.html"))
    chip_cats = set()
    for tag in re.findall(r"<button[^>]*>", store_html):
        if "chip" in tag:
            chip_cats |= set(re.findall(r'data-cat="([^"]+)"', tag))
    sjs = read(STORE_JS)
    m = re.search(r'\[([^\]]*)\]\.includes\(category\)', sjs)
    scroll_only = set(re.findall(r'"([a-z-]+)"', m.group(1))) if m else set()
    handled_cats = chip_cats | scroll_only
    cat_notes = {
        "chips (filter grid + scroll to #editions)": sorted(chip_cats),
        "scroll-only in store.js (no chip; scrolls to #academy-store-title, grid shows All)": sorted(scroll_only - chip_cats),
    }

    def resolve(page_file, href):
        sp = urlsplit(href)
        path = unquote(sp.path)
        if path == "":
            return os.path.join(SITE, page_file), sp.fragment, sp.query
        if path.startswith("/"):
            full = os.path.join(SITE, path.lstrip("/"))
        else:
            full = os.path.join(SITE, os.path.dirname(page_file), path)
        return os.path.normpath(full), sp.fragment, sp.query

    def target_exists(full):
        if os.path.isdir(full):
            idx = os.path.join(full, "index.html")
            return idx if os.path.isfile(idx) else None
        return full if os.path.isfile(full) else None

    page_cache = {os.path.join(SITE, f): p for f, p in parsed.items()}

    def page_of(fullpath):
        if fullpath in page_cache:
            return page_cache[fullpath]
        if fullpath.endswith(".html") and os.path.isfile(fullpath):
            p = Page()
            p.feed(read(fullpath))
            page_cache[fullpath] = p
            return p
        return None

    broken_files, broken_anchors, dead_cat, dead_hrefs = [], [], [], []
    runtime_hrefs = []
    runtime_anchors = []
    missing_assets, bad_modals, dead_buttons = [], [], []
    externals = defaultdict(Counter)
    label_rows = []
    anchor_total = 0

    for f, p in parsed.items():
        for rec in p.anchors:
            anchor_total += 1
            a = rec["attrs"]
            text = clean(rec["text"]) or a.get("aria-label", "") or a.get("title", "")
            href = a.get("href")
            row = {"page": f, "line": rec["line"], "text": text, "href": href}
            if href is None:
                aid = a.get("id", "")
                if aid and re.search(r"#" + re.escape(aid) + r"\b", corpus) and re.search(r"\.href\s*=|setAttribute\(.href.", corpus):
                    runtime_hrefs.append({**row, "reason": "no static href; JS targets #%s and assigns .href at runtime" % aid})
                    continue
                if rec["in_template"] and re.search(r"template\.content|\.content\.firstElementChild", corpus) and re.search(r"\.href\s*=", corpus):
                    runtime_hrefs.append({**row, "reason": "anchor inside <template>; JS clones it and assigns .href at runtime"})
                    continue
                dead_hrefs.append({**row, "reason": "<a> with no href attribute"})
                continue
            h = href.strip()
            if h == "":
                dead_hrefs.append({**row, "reason": "empty href"})
                continue
            if h == "#":
                dead_hrefs.append({**row, "reason": 'href="#"'})
                continue
            if h.lower().startswith("javascript:"):
                dead_hrefs.append({**row, "reason": "javascript: link"})
                continue
            if LABEL_RE.search(text) or LABEL_RE.search(a.get("aria-label", "")):
                label_rows.append({"page": f, "line": rec["line"], "kind": "a", "text": text, "target": h})
            if is_external(h) or is_other_scheme(h):
                externals[f][h] += 1
                continue
            full, frag, query = resolve(f, h)
            tgt = target_exists(full)
            if tgt is None:
                broken_files.append({**row, "reason": "file not found: " + os.path.relpath(full, ROOT)})
                continue
            tgt_name = os.path.relpath(tgt, SITE)
            q = parse_qs(query)
            if tgt_name == "academy-product.html" and "product" in q:
                key = q["product"][0]
                if key not in valid_products:
                    broken_files.append({**row, "reason": "?product=%s is not an id in academy-products.json nor an alias in academy-product.js" % key})
            if tgt_name == "store.html" and "cat" in q:
                c = q["cat"][0]
                if c not in handled_cats:
                    dead_cat.append({**row, "reason": "?cat=%s is not a chip value nor handled in store.js" % c})
            if frag:
                tp = page_of(tgt)
                if tp is not None:
                    fr = unquote(frag)
                    view_ok = False
                    if tgt_name == "academy-product.html" and "product" in q:
                        pr = [x for x in prod["products"] if x["id"] == q["product"][0]]
                        if pr:
                            vids = {v.get("id") for v in pr[0].get("views", [])} | {v.get("id") for v in [pr[0].get("overview") or {}]}
                            vids |= {x.get("id") for x in pr[0].get("styles", [])}
                            view_ok = fr in vids
                    if view_ok:
                        runtime_anchors.append({**row, "reason": "#%s is a view id of this product in academy-products.json; academy-product.js selects it from location.hash" % fr})
                    elif fr not in tp.ids and fr not in tp.names:
                        broken_anchors.append({**row, "reason": "no element with id='%s' in %s" % (fr, tgt_name),
                                               "frag_string_found_in_js_or_json": (fr in corpus) or (fr in data_text)})

        for rec in p.buttons:
            a = rec["attrs"]
            text = clean(rec["text"]) or a.get("aria-label", "") or a.get("title", "")
            btn_type = a.get("type", "submit" if rec["in_form"] else "")
            attrs = {k: v for k, v in a.items() if k in ("id", "class", "type", "aria-controls") or k.startswith("data-")}
            row = {"page": f, "line": rec["line"], "text": text, "attrs": attrs}
            if LABEL_RE.search(text):
                label_rows.append({"page": f, "line": rec["line"], "kind": "button", "text": text,
                                   "target": "(button) " + json.dumps(attrs, ensure_ascii=False)})
            if rec["in_form"] and btn_type == "submit":
                continue
            hooks = []
            if "onclick" in a:
                hooks.append("inline onclick")
            for k in a:
                if k.startswith("data-"):
                    if re.search(r"\[" + re.escape(k) + r"\b|['\"`]" + re.escape(k) + r"|" + re.escape(k) + r"\s*=", corpus) \
                            or re.search(r"dataset\.%s\b|dataset\[['\"]%s['\"]\]" % (camel(k), camel(k)), corpus):
                        hooks.append("attr:" + k)
            if a.get("id") and re.search(r"#" + re.escape(a["id"]) + r"\b|getElementById\(['\"]" + re.escape(a["id"]), corpus):
                hooks.append("id:" + a["id"])
            for c in a.get("class", "").split():
                if re.search(r"\." + re.escape(c) + r"(?![\w-])|classList\.\w+\(['\"]" + re.escape(c) + r"['\"]", corpus):
                    hooks.append("class:" + c)
            if a.get("aria-controls") and re.search(re.escape(a["aria-controls"]), corpus):
                hooks.append("aria-controls:" + a["aria-controls"])
            if not hooks and re.search(r"querySelector(All)?\(['\"]button['\"]\)", corpus):
                for aid in rec["anc_ids"]:
                    if re.search(r"#" + re.escape(aid) + r"\b|getElementById\(['\"]" + re.escape(aid), corpus):
                        hooks.append("ancestor #%s + querySelector('button') in JS" % aid)
                        break
            row["hooks"] = hooks
            if not hooks:
                dead_buttons.append({**row, "reason": "no data-*/id/class/onclick hook found in any JS"})

        for kind, attr, val, extra, line in p.assets:
            v = val.strip()
            if not v:
                continue
            if is_external(v) or is_other_scheme(v):
                if is_external(v):
                    externals[f][v] += 1
                continue
            if kind == "link" and "canonical" in extra:
                continue
            path = unquote(urlsplit(v).path)
            if path == "":
                continue
            full = os.path.join(SITE, path.lstrip("/")) if path.startswith("/") else os.path.join(SITE, os.path.dirname(f), path)
            full = os.path.normpath(full)
            if not os.path.isfile(full):
                missing_assets.append({"page": f, "line": line, "element": kind + "[" + attr + "]",
                                       "target": v, "reason": "file not found: " + os.path.relpath(full, ROOT)})

        for val, tag, line in p.modals:
            ident = val[1:] if val.startswith("#") else val
            if ident not in p.ids:
                bad_modals.append({"page": f, "line": line, "element": tag, "target": val,
                                   "reason": "no element with that id on this page"})

    handler_attrs = Counter()
    for p in parsed.values():
        for rec in p.buttons:
            for k in rec["attrs"]:
                if k.startswith("data-") and (
                        re.search(r"\[" + re.escape(k) + r"\b|['\"`]" + re.escape(k) + r"|" + re.escape(k) + r"\s*=", corpus)
                        or re.search(r"dataset\.%s\b" % camel(k), corpus)):
                    handler_attrs[k] += 1
    handler_files = {}
    for k in handler_attrs:
        handler_files[k] = [fn for fn, t in list(js_text.items()) + [("(inline script)", inline_js)]
                            if re.search(re.escape(k) + r"|dataset\." + camel(k), t)]
    button_total = sum(len(p.buttons) for p in parsed.values())

    result = {
        "pages_scanned": pages,
        "totals": {"anchors": anchor_total, "buttons": button_total},
        "cat1_broken_file_links": broken_files,
        "cat1_broken_anchors": broken_anchors,
        "cat1_dead_cat_links": dead_cat,
        "cat1_store_cat_handling": cat_notes,
        "cat1_valid_product_keys_count": len(valid_products),
        "cat2_dead_hrefs": dead_hrefs,
        "info_runtime_resolved_hrefs": runtime_hrefs,
        "info_runtime_resolved_anchors": runtime_anchors,
        "cat3_dead_buttons": dead_buttons,
        "cat3_handler_attrs_found": {k: {"buttons_on_site": handler_attrs[k], "js_files": handler_files[k]} for k in sorted(handler_attrs)},
        "cat4_missing_assets": missing_assets,
        "cat5_bad_modals": bad_modals,
        "cat6_externals": {f: dict(c.most_common()) for f, c in externals.items()},
        "cat7_label_target": label_rows,
    }
    os.makedirs(TRACK, exist_ok=True)
    with open(os.path.join(TRACK, "link_audit.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    def esc(s):
        return str(s).replace("|", "\\|").replace("\n", " ")

    def table(rows, cols):
        if not rows:
            return "_none_\n"
        out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for r in rows:
            out.append("| " + " | ".join(esc(r.get(c, "")) for c in cols) + " |")
        return "\n".join(out) + "\n"

    md = ["# Link audit", "",
          "Generated by `tools/link_audit.py` (read-only; scans `site/*.html`: %d pages, %d `<a>`, %d `<button>`)." % (len(pages), anchor_total, button_total), "",
          "## Counts", "", "| Category | Failures |", "|---|---|",
          "| 1 broken file links (incl. unknown ?product=) | %d |" % len(broken_files),
          "| 1 broken anchors | %d |" % len(broken_anchors),
          "| 1 dead ?cat= links | %d |" % len(dead_cat),
          "| 2 dead hrefs (#, empty, javascript:, no href) | %d |" % len(dead_hrefs),
          "| 3 dead buttons (no handler found) | %d |" % len(dead_buttons),
          "| 4 missing assets | %d |" % len(missing_assets),
          "| 5 data-modal targets missing | %d |" % len(bad_modals),
          "", "## Broken file links", "", table(broken_files, ["page", "line", "text", "href", "reason"]),
          "## Broken anchors", "",
          "`frag_string_found_in_js_or_json` true means the id string also appears in JS/JSON, so it may be created at runtime.", "",
          table(broken_anchors, ["page", "line", "text", "href", "reason", "frag_string_found_in_js_or_json"]),
          "## Dead ?cat= links", "", "Store handles: " + json.dumps(cat_notes, ensure_ascii=False), "",
          table(dead_cat, ["page", "line", "text", "href", "reason"]),
          "### Not counted: resolved at runtime (verified in JS/JSON)", "",
          table(runtime_anchors + runtime_hrefs, ["page", "line", "text", "href", "reason"]),
          "## Dead hrefs", "", table(dead_hrefs, ["page", "line", "text", "href", "reason"]),
          "## Dead buttons", "",
          "Method: a button is live if it is a submit button in a form, or any of its data-* attribute names / id / classes is referenced in `site/assets/js/*.js` or an inline script (or it has inline onclick). Class-only matches are weak evidence; see `hooks` in the JSON.", "",
          table([{**b, "attrs": json.dumps(b["attrs"], ensure_ascii=False)} for b in dead_buttons], ["page", "line", "text", "attrs", "reason"]),
          "### data-* hooks that DO have handlers", "",
          table([{"attr": k, "buttons": v["buttons_on_site"], "js": ", ".join(v["js_files"])} for k, v in result["cat3_handler_attrs_found"].items()], ["attr", "buttons", "js"]),
          "## Missing assets", "", table(missing_assets, ["page", "line", "element", "target", "reason"]),
          "## data-modal targets", "", table(bad_modals, ["page", "line", "element", "target", "reason"]),
          "## External links (count per page)", ""]
    for f in sorted(externals):
        md += ["**%s**" % f, ""]
        md += ["- %d x %s" % (n, u) for u, n in externals[f].most_common()]
        md.append("")
    md += ["## Label to target", "", table(label_rows, ["page", "line", "kind", "text", "target"])]
    with open(os.path.join(TRACK, "LINK_AUDIT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))

    print("cat1 broken file links:    %d" % len(broken_files))
    print("cat1 broken anchors:       %d" % len(broken_anchors))
    print("cat1 dead ?cat= links:     %d" % len(dead_cat))
    print("cat2 dead hrefs:           %d" % len(dead_hrefs))
    print("info runtime-resolved links (not failures): %d" % (len(runtime_hrefs) + len(runtime_anchors)))
    print("cat3 dead buttons:         %d (informational)" % len(dead_buttons))
    print("cat4 missing assets:       %d" % len(missing_assets))
    print("cat5 bad data-modal:       %d" % len(bad_modals))
    print("cat6 pages with externals: %d (unique urls: %d)" % (len(externals), len({u for c in externals.values() for u in c})))
    print("cat7 label rows:           %d" % len(label_rows))
    fail = len(broken_files) + len(broken_anchors) + len(dead_cat) + len(dead_hrefs) + len(missing_assets) + len(bad_modals)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
