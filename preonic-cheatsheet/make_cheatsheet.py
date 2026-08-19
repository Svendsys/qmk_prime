#!/usr/bin/env python3
"""Build the printable Preonic keymap cheatsheet.

    python3 make_cheatsheet.py            # regenerate the Markdown, then the PDF
    python3 make_cheatsheet.py --md       # Markdown only
    python3 make_cheatsheet.py --pdf      # PDF only, from the Markdown already on disk

The layout grids are read straight out of keymap.c, so the sheet cannot drift
away from the firmware. Wording lives in keylabels.py; page design lives in
print.css. Both are meant to be edited.

The PDF is rendered by the Chromium that ships with Playwright. Point
CHROMIUM at another binary if yours lives elsewhere.
"""

import argparse
import os
import re
import subprocess
import sys

import keylabels as KL

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KEYMAP = os.path.join(REPO, "keyboards/preonic/keymaps/dooroflife_v2/keymap.c")
CONFIG = os.path.join(REPO, "keyboards/preonic/keymaps/dooroflife_v2/config.h")
MD_OUT = os.path.join(HERE, "preonic-dooroflife-v2.md")
PDF_OUT = os.path.join(HERE, "preonic-dooroflife-v2.pdf")
CSS = os.path.join(HERE, "print.css")

CHROMIUM = os.environ.get(
    "CHROMIUM",
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")

ROWS = [12, 12, 12, 12, 11]          # LAYOUT_preonic_1x2uC, 59 keys
SPACE_INDEX = 53                     # the 2u key, flat index into the 59


# ── parsing ────────────────────────────────────────────────────────────────

def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def split_top(body):
    """Split on commas that are not inside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_keymap(path):
    """-> (ordered layer names, {layer: [59 keycode strings]}, {macro: expansion})"""
    raw = open(path).read()
    src = strip_comments(raw)

    defines = dict(re.findall(r"^\s*#define\s+(\w+)\s+(.+?)\s*$", src, re.M))

    order = re.search(r"enum layers\s*\{(.*?)\}", src, re.S).group(1)
    names = [m.group(1) for m in re.finditer(r"(_[A-Z0-9]+)\s*(?:=\s*\d+\s*)?,", order)]

    layers = {}
    for m in re.finditer(r"\[\s*(_[A-Z0-9]+)\s*\]\s*=\s*LAYOUT_preonic_1x2uC\s*\(", src):
        i, depth = m.end(), 1
        while depth:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        keys = [re.sub(r"\s+", "", k) for k in split_top(src[m.end():i - 1])]
        if len(keys) != sum(ROWS):
            sys.exit(f"{path}: layer {m.group(1)} has {len(keys)} keys, expected {sum(ROWS)}")
        layers[m.group(1)] = keys

    missing = [n for n in names if n not in layers]
    if missing:
        sys.exit(f"{path}: enum declares {missing} but no such layer array exists")
    return names, layers, defines


def parse_hues(path):
    src = strip_comments(open(path).read())
    return dict(re.findall(r"#define\s+(HUE_\w+)\s+(\d+)", src))


def parse_tapping_term(path):
    m = re.search(r"#define\s+TAPPING_TERM\s+(\d+)", strip_comments(open(path).read()))
    return m.group(1) if m else "?"


# ── keycode -> drawable cap ────────────────────────────────────────────────

def expand(code, defines):
    """Resolve keymap #define aliases such as L_NAV or ALT_DEL."""
    seen = set()
    while code in defines and code not in seen:
        seen.add(code)
        code = re.sub(r"\s+", "", defines[code])
    return code


def cap(code, defines):
    """-> dict(hold=str|None, tap=str, cls=str) describing one printed key."""
    code = expand(code, defines)

    if code == "XXXXXXX":
        return {"hold": None, "tap": "", "cls": "off"}
    if code == "_______":
        return {"hold": None, "tap": "", "cls": "thru"}

    m = re.fullmatch(r"LT\((\w+),(\w+)\)", code)
    if m:
        layer, tap = m.group(1), m.group(2)
        return {"hold": KL.LAYER_SHORT.get(layer, layer.lstrip("_")),
                "tap": label(tap), "cls": "lt"}

    m = re.fullmatch(r"(LALT|RALT|LCTL|RCTL|LSFT|RSFT|LGUI|RGUI)_T\((\w+)\)", code)
    if m:
        holds = {"LALT": "L-Alt", "RALT": "R-Alt", "LCTL": "Ctrl", "RCTL": "R-Ctrl",
                 "LSFT": "Shift", "RSFT": "Shift", "LGUI": "Super", "RGUI": "Super"}
        return {"hold": holds[m.group(1)], "tap": label(m.group(2)), "cls": "mt"}

    if code == "SC_SENT":
        return {"hold": "Shift", "tap": "Enter", "cls": "mt"}

    cls = "key"
    if code in KL.DANGER:
        cls = "danger"
    elif code in KL.STRONG:
        cls = "strong"
    return {"hold": None, "tap": label(code), "cls": cls}


def label(code):
    if code in KL.LABEL:
        return KL.LABEL[code]
    m = re.fullmatch(r"KC_([A-Z])", code)          # letters
    if m:
        return m.group(1)
    m = re.fullmatch(r"KC_(\d)", code)             # digits
    if m:
        return m.group(1)
    m = re.fullmatch(r"KC_P(\d)", code)            # numpad digits
    if m:
        return m.group(1)
    m = re.fullmatch(r"KC_(F\d{1,2})", code)       # F-keys
    if m:
        return m.group(1)
    return code.replace("KC_", "")


# ── rendering ──────────────────────────────────────────────────────────────

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def grid(keys, defines, origins=None, size=""):
    """Render 59 keycodes as an HTML keyboard.

    origins: optional list of 59 extra CSS classes, used by the composed view
    to show which layer each key actually came from.
    """
    out = [f'<table class="kb {size}">'.rstrip() + "<tbody>"]
    i = 0
    for n in ROWS:
        out.append("<tr>")
        for c in range(n):
            k = cap(keys[i], defines)
            cls = k["cls"] + ((" " + origins[i]) if origins and origins[i] else "")
            span = ' colspan="2"' if i == SPACE_INDEX else ""
            hold = f'<b>{esc(k["hold"])}</b>' if k["hold"] else ""
            tap = esc(k["tap"]) or "&nbsp;"
            out.append(f'<td class="{cls}"{span}>{hold}<span>{tap}</span></td>')
            i += 1
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def compose(base, fn):
    """Base layer under the always-on Function layer -> (keys, origin classes)."""
    keys, origins = [], []
    for b, f in zip(base, fn):
        if f == "_______":
            keys.append(b)
            origins.append("from-base")
        else:
            keys.append(f)
            origins.append("from-fn")
    return keys, origins


def html_table(headers, rows, cls=""):
    attr = f' class="{cls}"' if cls else ""
    out = [f"<table{attr}>"]
    if headers:
        out.append("<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>")
    out.append("<tbody>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def split_table(headers, rows):
    """Two tables side by side — long reference lists waste a page otherwise."""
    half = (len(rows) + 1) // 2
    return ('<div class="sbs">'
            + html_table(headers, rows[:half])
            + html_table(headers, rows[half:])
            + "</div>")


def layer_keys_table(fn, defines):
    rows = []
    for i, code in enumerate(fn):
        m = re.fullmatch(r"LT\((\w+),(\w+)\)", expand(code, defines))
        if m:
            tapcode = m.group(2)
            name = KL.PROSE.get(tapcode, label(tapcode))
            rows.append((name, KL.LAYER_TITLES.get(m.group(1), m.group(1))))
    return html_table(["Hold this", "To reach"],
                      [(f"<b>{esc(t)}</b>", esc(n)) for t, n in rows])


def tap_code_of(expanded):
    """The keycode a dual-role key sends when tapped."""
    m = re.fullmatch(r"LT\(\w+,(\w+)\)", expanded)
    if m:
        return m.group(1)
    m = re.fullmatch(r"\w+_T\((\w+)\)", expanded)
    if m:
        return m.group(1)
    return "KC_ENT" if expanded == "SC_SENT" else expanded


def dual_role_table(layers, defines):
    """Every tap/hold key on the board, gathered from every layer."""
    seen, rows = set(), []
    for keys in layers.values():
        for code in keys:
            e = expand(code, defines)
            k = cap(code, defines)
            if k["cls"] in ("lt", "mt") and e not in seen:
                seen.add(e)
                tapcode = tap_code_of(e)
                rows.append((KL.PROSE.get(tapcode, k["tap"]), k["hold"]))
    return split_table(["Tap for", "Hold for"],
                       [(f"<b>{esc(t)}</b>", esc(h)) for t, h in rows])


# ── the document ───────────────────────────────────────────────────────────

def build_markdown():
    names, layers, defines = parse_keymap(KEYMAP)
    hues = parse_hues(KEYMAP)
    term = parse_tapping_term(CONFIG)

    fn = layers["_FUNCTION"]
    comp_keys, comp_origin = compose(layers["_COLEMAK"], fn)
    qwe_keys, qwe_origin = compose(layers["_QWERTY"], fn)

    momentary = [n for n in names if n not in ("_COLEMAK", "_QWERTY", "_FUNCTION")]

    d = []
    A = d.append

    A("<!-- Generated by make_cheatsheet.py from keymap.c — run it again after")
    A("     changing the keymap. Wording lives in keylabels.py. -->")
    A("")
    A('<div class="titleblock">')
    A("<h1>Preonic — DoorOfLife v2</h1>")
    A("<p>Drop + OLKB Preonic rev3 &middot; <code>preonic/rev3_drop</code>"
      " &middot; layout <code>LAYOUT_preonic_1x2uC</code></p>")
    A("</div>")
    A("")

    # ── page 1 ────────────────────────────────────────────────────────────
    A("## What you actually type on")
    A("")
    A("Colemak at rest, with the always-on Function layer already applied.")
    A("**This is the board in front of you when nothing is held.**")
    A("")
    A(grid(comp_keys, defines, comp_origin))
    A("")
    A(html_table(None, [
        ('<span class="sw from-base"></span>',
         "Comes from the <b>letter layer</b>. These are the only keys that move "
         "when you swap Colemak &harr; QWERTY."),
        ('<span class="sw from-fn"></span>',
         "Comes from the <b>Function layer</b>. Identical in both layouts."),
        ('<span class="sw lt"></span>',
         "<b>Layer key</b> &mdash; the black bar names the layer you reach by holding it."),
        ('<span class="sw mt"></span>',
         "<b>Dual-role</b> &mdash; taps as the big label, acts as the small one when held."),
    ], cls="legend"))
    A("")
    A("## Reaching the other layers")
    A("")
    A("Five keys along the bottom edge and right side. Each still types its own")
    A(f"legend when tapped; hold it past **{term} ms** and it switches layer instead.")
    A("")
    A(layer_keys_table(fn, defines))
    A("")
    A("## Swapping Colemak and QWERTY")
    A("")
    A("Hold **right Ctrl**, then press **A** for Colemak, **R** to swap, or **S**")
    A("for QWERTY — the three heavy-bordered keys on the Settings layer. The board")
    A("plays that layout's own tune so you know it took, and remembers the choice")
    A("across unplugging.")
    A("")
    A('<div class="pagebreak"></div>')
    A("")

    # ── page 2: the always-on layer, then what sits under it ─────────────
    A(f"## {KL.LAYER_TITLES['_FUNCTION']} layer — always on")
    A("")
    A(KL.LAYER_BLURB["_FUNCTION"])
    A("Dotted cells are where the letter layer shows through.")
    A("")
    A(grid(fn, defines))
    A("")
    A("## The two letter layers")
    A("")
    A("Only letters live here. Everything else is dotted, because the Function")
    A("layer above supplies it — which is why swapping layouts cannot disturb")
    A("your modifiers, numbers or layer keys.")
    A("")
    for n in ("_COLEMAK", "_QWERTY"):
        A(f"### {KL.LAYER_TITLES[n]}")
        A("")
        A(KL.LAYER_BLURB[n])
        A("")
        A(grid(layers[n], defines, size="small"))
        A("")
    A("> **QWERTY puts P on the home row**, not the top row — the top-row spot it")
    A("> would want is `−` on the Function layer. WASD, the number row and the")
    A("> modifiers are all where a game expects them, which is the point.")
    A("")
    A('<div class="pagebreak"></div>')
    A("")

    # ── pages 4+: momentary layers, two per page ──────────────────────────
    for idx, n in enumerate(momentary):
        A(f"## {KL.LAYER_TITLES[n]} layer")
        A("")
        A(KL.LAYER_BLURB[n])
        A("")
        A(grid(layers[n], defines, size="small"))
        A("")
        if any(k in KL.NUMPAD for k in layers[n]):
            A("> The right-hand block is the **numeric keypad**, not the number row —")
            A("> it sends keypad codes, so it works with Num Lock as you'd expect.")
            A("")
        if idx % 3 == 2 and idx != len(momentary) - 1:
            A('<div class="pagebreak"></div>')
            A("")

    # ── reference ────────────────────────────────────────────────────
    A("## Every dual-role key")
    A("")
    A(f"Tap is under **{term} ms**. Press another key while holding and it commits")
    A("to the hold immediately, so fast typing does not produce stray letters.")
    A("")
    A(dual_role_table(layers, defines))
    A("")
    A("## Knowing which mode you are in")
    A("")
    A("Two signals, answering two different questions.")
    A("")
    A("**The underglow says where you are.** At rest it shows the letter layout;")
    A("while a layer key is held it shows that layer.")
    A("")
    A("| Underglow | Means |")
    A("|---|---|")
    for n in ("_COLEMAK", "_QWERTY"):
        key = "HUE_" + n.lstrip("_")
        if key in hues:
            A(f"| **{KL.HUE_NAMES.get(key, key)}** | {KL.LAYER_TITLES[n]} — at rest |")
    for n in momentary:
        key = "HUE_" + n.lstrip("_")
        if key in hues:
            A(f"| {KL.HUE_NAMES.get(key, key)} | {KL.LAYER_TITLES[n]} — while held |")
    A("")
    A("**A sound says something changed.** Swapping letter layout plays that")
    A("layout's own short tune, so you know it took effect without looking.")
    A("")
    A("> Layer colouring stands aside if you turn the light off or pick an")
    A("> animation, and it keeps whatever brightness you set. It is an indicator,")
    A("> not a hijack.")
    A("")
    A("## If something goes wrong")
    A("")
    A("Three ways into the bootloader, most convenient first. The last one works")
    A("even if the firmware is completely broken.")
    A("")
    A("1. **Hold right Ctrl, then the top-right key** — that is `BOOTLOADER` on the")
    A("   Settings layer.")
    A("2. **Hold the top-left key while plugging in.** Built into the keyboard, so")
    A("   it works whatever keymap is loaded.")
    A("3. **The `reset` pinhole** on the back plate, top right. A paperclip reaches")
    A("   it with the case assembled; it depends on no firmware at all.")
    A("")
    A("```")
    A("make preonic/rev3_drop:dooroflife_v2:flash     # this layout")
    A("make preonic/rev3_drop:dooroflife:flash        # the 2021 layout, unchanged")
    A("```")
    A("")
    A('<div class="colophon">')
    A("<p>Generated from <code>keyboards/preonic/keymaps/dooroflife_v2/keymap.c</code>."
      " Re-run <code>preonic-cheatsheet/make_cheatsheet.py</code> after changing"
      " the keymap.</p>")
    A("</div>")
    A("")

    return "\n".join(d)


# ── output ─────────────────────────────────────────────────────────────────

def write_md():
    md = build_markdown()
    with open(MD_OUT, "w") as f:
        f.write(md)
    print(f"wrote {os.path.relpath(MD_OUT, REPO)} ({len(md.splitlines())} lines)")


def write_pdf():
    try:
        import markdown
    except ImportError:
        sys.exit("need the markdown package: pip install markdown")

    if not os.path.exists(CHROMIUM):
        sys.exit(f"no Chromium at {CHROMIUM} — set CHROMIUM=/path/to/chrome")

    body = markdown.markdown(
        open(MD_OUT).read(),
        extensions=["tables", "fenced_code", "attr_list"],
    )
    html = (f"<!doctype html><meta charset=utf-8>\n<style>\n{open(CSS).read()}\n</style>\n"
            f"<body>\n{body}\n</body>")

    tmp = os.path.join(HERE, ".cheatsheet.html")
    with open(tmp, "w") as f:
        f.write(html)
    try:
        subprocess.run(
            [CHROMIUM, "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={PDF_OUT}", tmp],
            check=True, capture_output=True)
    finally:
        os.remove(tmp)

    size = os.path.getsize(PDF_OUT)
    pages = open(PDF_OUT, "rb").read().count(b"/Type /Page\n") or \
        open(PDF_OUT, "rb").read().count(b"/Type /Page")
    print(f"wrote {os.path.relpath(PDF_OUT, REPO)} ({size:,} bytes, ~{pages} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="regenerate the Markdown only")
    ap.add_argument("--pdf", action="store_true", help="render the PDF only")
    args = ap.parse_args()

    if not args.pdf:
        write_md()
    if not args.md:
        write_pdf()
