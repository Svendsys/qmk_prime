"""How each keycode is drawn on the cheatsheet.

This is the file to edit when a key reads badly on paper. Everything else is
derived from keymap.c, so it cannot drift; only the wording lives here.
"""

# Layer enum name -> the name printed on the sheet.
LAYER_TITLES = {
    "_COLEMAK":  "Colemak",
    "_QWERTY":   "QWERTY",
    "_FUNCTION": "Function",
    "_FKEYS":    "F-keys",
    "_NAV":      "Navigation",
    "_MOUSE":    "Mouse",
    "_MEDIA":    "Media",
    "_SETTINGS": "Settings",
}

# Short form used inside a key cap when a hold reaches this layer.
LAYER_SHORT = {
    "_FKEYS":    "F-KEYS",
    "_NAV":      "NAV",
    "_MOUSE":    "MOUSE",
    "_MEDIA":    "MEDIA",
    "_SETTINGS": "SETTINGS",
}

# One-line description under each layer heading.
LAYER_BLURB = {
    "_COLEMAK":  "Your normal typing layout. Letters only — everything else comes from Function.",
    "_QWERTY":   "Same board, QWERTY letters, for games that read key positions as QWERTY.",
    "_FUNCTION": "Always on. Every modifier, number, symbol and layer key lives here.",
    "_FKEYS":    "Hold Home.",
    "_NAV":      "Hold comma. Arrows and brackets left, numeric keypad right.",
    "_MOUSE":    "Hold End. Move the pointer without leaving the keyboard.",
    "_MEDIA":    "Hold backtick.",
    "_SETTINGS": "Hold right Ctrl. Layout switching, lighting, sound, and the bootloader.",
}

# keycode -> label. Letters, digits and F-keys are handled by pattern.
LABEL = {
    "KC_ESC": "Esc", "KC_TAB": "Tab", "KC_BSPC": "Bksp", "KC_DEL": "Del",
    "KC_ENT": "Enter", "KC_SPC": "Space", "KC_LSFT": "Shift", "KC_LCTL": "Ctrl",
    "KC_RCTL": "R-Ctrl", "KC_LGUI": "Super", "KC_APP": "Menu",

    "KC_EQL": "=", "KC_MINS": "−", "KC_SCLN": ";", "KC_BSLS": "\\",
    "KC_SLSH": "/", "KC_DOT": ".", "KC_QUOT": "'", "KC_GRV": "`",
    "KC_COMM": ",", "KC_LBRC": "[", "KC_RBRC": "]", "KC_LPRN": "(", "KC_RPRN": ")",

    "KC_INS": "Ins", "KC_HOME": "Home", "KC_END": "End",
    "KC_PGUP": "PgUp", "KC_PGDN": "PgDn",
    "KC_UP": "↑", "KC_DOWN": "↓", "KC_LEFT": "←", "KC_RGHT": "→",
    "KC_PSCR": "PrtSc", "KC_CAPS": "Caps", "KC_NUM": "NumLk",

    # numeric keypad
    "KC_PSLS": "/", "KC_PAST": "*", "KC_PMNS": "−", "KC_PPLS": "+",
    "KC_PCMM": ",", "KC_PEQL": "=", "KC_PDOT": ".", "KC_PENT": "Enter",

    "KC_VOLD": "Vol −", "KC_VOLU": "Vol +", "KC_MPLY": "Play", "KC_MSTP": "Stop",
    "KC_MUTE": "Mute", "KC_MPRV": "Prev", "KC_MNXT": "Next",
    "KC_MRWD": "Rew", "KC_MFFD": "Fwd",

    "MS_UP": "↑", "MS_DOWN": "↓", "MS_LEFT": "←", "MS_RGHT": "→",
    "MS_BTN1": "L-click", "MS_BTN2": "R-click",
    "MS_WHLU": "Wheel ↑", "MS_WHLD": "Wheel ↓",
    "MS_ACL0": "Slow", "MS_ACL1": "Medium", "MS_ACL2": "Fast",

    "NK_ON": "NKRO on", "EE_CLR": "Wipe settings", "QK_BOOT": "BOOTLOADER",
    "AU_TOGG": "Sound on/off",
    "UG_TOGG": "Light on/off", "UG_NEXT": "Mode +", "UG_PREV": "Mode −",
    "UG_SATU": "Colour +", "UG_SATD": "Colour −",
    "UG_VALU": "Bright +", "UG_VALD": "Bright −",
    "UG_SPDU": "Speed +", "UG_SPDD": "Speed −",

    "BASE_CM": "COLEMAK", "BASE_TG": "SWAP", "BASE_QW": "QWERTY",
}

# Longer names for symbol keys, used in prose tables where a lone glyph such
# as ` or , is too easy to miss.
PROSE = {
    "KC_GRV":  "`  (backtick)",
    "KC_COMM": ",  (comma)",
    "KC_DOT":  ".  (full stop)",
    "KC_SLSH": "/  (slash)",
    "KC_QUOT": "'  (apostrophe)",
    "KC_SCLN": ";  (semicolon)",
    "KC_MINS": "−  (minus)",
    "KC_EQL":  "=  (equals)",
}

# Keys drawn with a heavy warning border.
DANGER = {"QK_BOOT", "EE_CLR"}

# Keys drawn emphasised — the ones you actively reach for.
STRONG = {"BASE_CM", "BASE_TG", "BASE_QW"}

# Numpad keycodes, flagged so the sheet can say so once rather than per key.
NUMPAD = {"KC_P0", "KC_P1", "KC_P2", "KC_P3", "KC_P4", "KC_P5", "KC_P6",
          "KC_P7", "KC_P8", "KC_P9", "KC_PSLS", "KC_PAST", "KC_PMNS",
          "KC_PPLS", "KC_PCMM", "KC_PEQL", "KC_PDOT", "KC_PENT"}

# Underglow hue constant -> how to describe the colour in words, since the
# sheet is printed in black and white.
HUE_NAMES = {
    "HUE_COLEMAK":  "Cyan",
    "HUE_QWERTY":   "Amber",
    "HUE_FKEYS":    "Pink",
    "HUE_NAV":      "Violet",
    "HUE_MOUSE":    "Green",
    "HUE_MEDIA":    "Red",
    "HUE_SETTINGS": "Blue",
}
