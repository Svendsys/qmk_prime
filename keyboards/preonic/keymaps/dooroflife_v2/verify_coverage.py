"""Compose each base layer with the always-on _FUNCTION layer and report any
position that resolves to nothing. A dead key here is the 2021 failure mode."""
import os, re, sys

SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keymap.c')).read()

def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)

def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def layers(src):
    src, res = strip_comments(src), {}
    for m in re.finditer(r'\[\s*(_[A-Z0-9]+)\s*\]\s*=\s*LAYOUT_preonic_1x2uC\s*\(', src):
        start, depth, i = m.end(), 1, m.end()
        while depth:
            if src[i] == '(': depth += 1
            elif src[i] == ')': depth -= 1
            i += 1
        res[m.group(1)] = [re.sub(r'\s+', '', t) for t in split_top(src[start:i-1])]
    return res

L = layers(SRC)
ROWS = [12, 12, 12, 12, 11]
fail = 0

for name in ('_COLEMAK', '_QWERTY'):
    base, fn = L[name], L['_FUNCTION']
    if len(base) != 59 or len(fn) != 59:
        print(f"!! {name}: {len(base)} keys, _FUNCTION {len(fn)} (expected 59)"); fail = 1; continue

    eff, dead = [], []
    for i, (b, f) in enumerate(zip(base, fn)):
        e = b if f == '_______' else f
        eff.append(e)
        if e in ('XXXXXXX', '_______'):
            dead.append(i)

    print(f"\n{name} composed with _FUNCTION")
    i = 0
    for r, n in enumerate(ROWS):
        cells = [('.....' if eff[i+c] in ('XXXXXXX','_______') else eff[i+c])[:13] for c in range(n)]
        print('   ' + ' '.join(f'{c:<13}' for c in cells))
        i += n
    if dead:
        fail = 1
        print(f"   !! {len(dead)} DEAD position(s) at index {dead}")
    else:
        print(f"   59/59 positions resolve to a key — no dead spots")

# a base layer must never shadow a _FUNCTION key, and vice versa
print()
for name in ('_COLEMAK', '_QWERTY'):
    clash = [i for i, (b, f) in enumerate(zip(L[name], L['_FUNCTION']))
             if b != 'XXXXXXX' and f != '_______']
    if clash:
        fail = 1
        print(f"!! {name}: {len(clash)} position(s) where _FUNCTION masks a base key: {clash}")
    else:
        print(f"   {name}: no base key is masked by _FUNCTION")

# every momentary layer must sit above _FUNCTION or it can never be reached
order = re.search(r'enum layers\s*\{(.*?)\}', strip_comments(SRC), re.S).group(1)
names = [m.group(1) for m in re.finditer(r'(_[A-Z0-9]+)\s*(?:=\s*\d+\s*)?,', order)]
fn_idx = names.index('_FUNCTION')
below = [n for n in names[:fn_idx] if n not in ('_COLEMAK', '_QWERTY')]
print()
print(f"   layer order: {' < '.join(names)}")
if below:
    fail = 1; print(f"!! these momentary layers sit BELOW _FUNCTION and are unreachable: {below}")
else:
    print(f"   every momentary layer sits above _FUNCTION")

print()
print("COVERAGE OK" if not fail else "COVERAGE FAILED")
sys.exit(fail)
