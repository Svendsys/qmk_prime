"""Prove the ported keymap is keycode-for-keycode identical to the 2021
QMK Configurator layout it came from, once the QMK renames since Nov 2021
are accounted for.

    python3 verify_verbatim.py [path to a clone of Svendsys/qmk_preonic]

Re-run this after any change to the base layout that is meant to preserve
behaviour. It compares all 8 layers x 59 key positions.
"""

import os, re, subprocess, sys

RENAME = {
    'KC_SFTENT':'SC_SENT', 'KC_NLCK':'KC_NUM', 'RESET':'QK_BOOT', 'EEP_RST':'EE_CLR',
    'KC_BTN1':'MS_BTN1','KC_BTN2':'MS_BTN2',
    'KC_MS_U':'MS_UP','KC_MS_D':'MS_DOWN','KC_MS_L':'MS_LEFT','KC_MS_R':'MS_RGHT',
    'KC_WH_U':'MS_WHLU','KC_WH_D':'MS_WHLD',
    'KC_ACL0':'MS_ACL0','KC_ACL1':'MS_ACL1','KC_ACL2':'MS_ACL2',
    'RGB_TOG':'UG_TOGG','RGB_MOD':'UG_NEXT','RGB_RMOD':'UG_PREV',
    'RGB_SAI':'UG_SATU','RGB_SAD':'UG_SATD','RGB_VAI':'UG_VALU','RGB_VAD':'UG_VALD',
    'RGB_SPI':'UG_SPDU','RGB_SPD':'UG_SPDD',
    # pure aliases, identical values
    'KC_TRNS':'_______', 'KC_NO':'XXXXXXX',
}
# layer-name enum in the new file maps back to the original numeric indices
LAYERNAME = {'_BASE':'0','_FKEYS':'1','_NAV':'2','_SETTINGS':'3',
             '_MOUSE':'4','_MEDIA':'5','_FKEYS2':'6','_NUMPAD2':'7'}

def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)

def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def layers(src):
    src = strip_comments(src)
    res = {}
    for m in re.finditer(r'\[\s*([A-Za-z0-9_]+)\s*\]\s*=\s*LAYOUT_preonic_1x2uC\s*\(', src):
        idx, start, depth = m.group(1), m.end(), 1
        i = start
        while depth:
            if src[i] == '(': depth += 1
            elif src[i] == ')': depth -= 1
            i += 1
        body = src[start:i-1]
        toks = [re.sub(r'\s+', '', t) for t in split_top(body)]
        res[LAYERNAME.get(idx, idx)] = toks
    return res

def normalize(toks):
    out = []
    for t in toks:
        for old, new in RENAME.items():
            t = re.sub(r'\b%s\b' % re.escape(old), new, t)
        out.append(t)
    return out

OLD_REPO = sys.argv[1] if len(sys.argv) > 1 else '../qmk_preonic'
OLD_REF  = '69bd56e6:keyboards/preonic/keymaps/DoorOfLife/keymap.c'

try:
    old_src = subprocess.run(['git', '-C', OLD_REPO, 'show', OLD_REF],
                             capture_output=True, text=True, check=True).stdout
except (subprocess.CalledProcessError, FileNotFoundError):
    sys.exit(f"could not read {OLD_REF} from {OLD_REPO}\n"
             f"usage: {sys.argv[0]} [path to a clone of Svendsys/qmk_preonic]")

new_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keymap.c')).read()

O, N = layers(old_src), layers(new_src)
fail = 0
print(f"layers: original={sorted(O, key=int)}  ported={sorted(N, key=int)}")
if sorted(O) != sorted(N):
    print("!! layer set differs"); fail = 1

for k in sorted(O, key=int):
    o = normalize(O[k])
    # resolve the ported file's layer-enum names back to their numeric values,
    # so LT(_NAV,..) and LT(2,..) compare equal only if the enum really is 2
    n = [re.sub(r'\b(%s)\b' % '|'.join(LAYERNAME), lambda m: LAYERNAME[m.group(1)], t)
         for t in N.get(k, [])]
    if len(o) != 59 or len(n) != 59:
        print(f"!! layer {k}: key count {len(o)} vs {len(n)} (expected 59)"); fail = 1; continue
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(o, n)) if a != b]
    if diffs:
        fail = 1
        print(f"!! layer {k}: {len(diffs)} differing position(s)")
        for i, a, b in diffs[:10]:
            print(f"     pos {i:2d}  original->{a:<24} ported->{b}")
    else:
        print(f"   layer {k}: 59/59 keys identical")

print()
print("VERBATIM PORT CONFIRMED" if not fail else "MISMATCH — port is NOT verbatim")
sys.exit(fail)
