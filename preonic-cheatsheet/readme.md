# Printable keymap cheatsheet

A five-page A4 reference for the `dooroflife_v2` keymap, designed for a
black-and-white laser printer. Nothing is encoded in colour — key kinds are
told apart by fill level, border weight and the position of the label — so
nothing is lost in monochrome.

| File | |
|---|---|
| `preonic-dooroflife-v2.pdf` | **Print this.** |
| `preonic-dooroflife-v2.md` | The source. Readable on GitHub, generated from the keymap. |
| `make_cheatsheet.py` | Reads `keymap.c`, writes the Markdown, renders the PDF. |
| `keylabels.py` | How each keycode is worded. **Edit this** when a key reads badly. |
| `print.css` | Page design. **Edit this** to change how it looks. |

## Regenerating

```sh
cd preonic-cheatsheet
python3 make_cheatsheet.py           # Markdown, then PDF
python3 make_cheatsheet.py --md      # Markdown only — no dependencies
python3 make_cheatsheet.py --pdf     # PDF only, from the Markdown on disk
```

The PDF step needs `pip install markdown` and a Chromium binary. It defaults
to the one Playwright installs; point `CHROMIUM` elsewhere if yours differs:

```sh
CHROMIUM=/usr/bin/chromium python3 make_cheatsheet.py --pdf
```

## Why it is generated

The layout grids are parsed straight out of
`keyboards/preonic/keymaps/dooroflife_v2/keymap.c`, so the sheet cannot drift
away from the firmware — which is exactly what went wrong with the hand-written
ASCII diagrams in the 2021 keymap, where several comments no longer matched the
arrays beneath them.

CI regenerates the Markdown on every push and fails if it differs from what is
committed, so a keymap change without a matching cheatsheet update is caught
before it reaches paper.

**So: change the keymap, then re-run this.** Hand-edits to the `.md` are
overwritten. Wording belongs in `keylabels.py`, design in `print.css`, and
document structure in `build_markdown()` inside `make_cheatsheet.py`.

## Printing

Straight duplex or single-sided both work; there are no facing-page spreads.
Print at 100% / "actual size" rather than "fit to page", or the 12.5 mm key
caps shrink and the small hold labels start to fill in.
