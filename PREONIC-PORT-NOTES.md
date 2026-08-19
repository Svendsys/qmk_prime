# Preonic keymap port — analysis and plan

Porting the `DoorOfLife` keymap from [Svendsys/qmk_preonic](https://github.com/Svendsys/qmk_preonic)
(QMK @ Nov 2021) onto this fork (QMK @ Aug 2026).

Board: Preonic rev3, STM32F303, layout `LAYOUT_preonic_1x2uC`.

## Verdict

**The 2021 rewrite never compiled.** Both refactor commits contain hard C syntax
errors, so whatever was flashed at the time was not the code at that repo's HEAD.
This was a build problem, not a hardware or flashing problem.

Confirmed by extracting the offending patterns and running `gcc -fsyntax-only`:

```
commit fe1a798f — keyboard_post_init_user():
    layer_on(_FUNCTION)          <- missing semicolon
    error: expected ';' before '}' token

commit a2932aae — [_BIGMAC] sits outside the keymaps[] array,
                  which was already closed with `};` 15 lines earlier:
    error: expected identifier or '(' before '[' token
```

## The three commits

| # | Commit | Date | Status |
|---|--------|------|--------|
| 1 | `69bd56e6` adding dooroflife keymap | 2021-11-29 | **Builds. Keep this.** `qmk json2c` dump of the working Configurator layout. |
| 2 | `fe1a798f` updating keymap | 2021-11-30 | Does not compile. Missing semicolon. |
| 3 | `a2932aae` updating personal keymap | 2021-12-05 | Does not compile. 5 independent errors. |

Commit 1 is the ground truth of what is on the keyboard today: 8 layers,
Colemak base, thumb/pinky keys as `LT()` holds.

| Layer | Reached by | Contents |
|-------|-----------|----------|
| 0 | base | Colemak alphas, number row, `SFTENT`, `RALT_T(APP)`, `LALT_T(DEL)` |
| 1 | `LT(1, KC_HOME)` | F1–F12, PgUp/PgDn/Home/End, Insert |
| 2 | `LT(2, KC_COMM)` | Arrows, brackets, parens + full numpad |
| 3 | `LT(3, KC_RCTL)` | Settings: RGB, `NK_ON`, `RESET`, `EEP_RST` |
| 4 | `LT(4, KC_END)` | Mouse keys |
| 5 | `LT(5, KC_GRV)` | Media |
| 6 | `LT(6, KC_F6)` from L1 | F-keys again, reversed (looks vestigial) |
| 7 | `LT(7, KC_F7)` | Second scattered numpad (looks vestigial) |

## The architectural trap

The rewrite strips base layers to alphas only and keeps `_FUNCTION` permanently
on above them, holding every modifier, number and symbol. Good design — but it
makes `_FUNCTION` load-bearing: if it fails to stay on, letters work and
*nothing else does*, not even space. That matches "it wouldn't work after
flashing" precisely.

And the code keeping it on is the classic QMK footgun — `layer_on()` and
`update_tri_layer()` called from inside `layer_state_set_user()` are silently
undone, because QMK assigns the hook's *return value* to `layer_state`
afterwards:

```c
/* wrong — the layer_on() is overwritten */
layer_state_t layer_state_set_user(layer_state_t state) {
    ensure_function_layer_enabled();               /* calls layer_on(_FUNCTION) */
    update_tri_layer(_NAVIGATION, _FUN, _BIGMAC);
    return state;
}

/* right — fold the change into the returned state */
layer_state_t layer_state_set_user(layer_state_t state) {
    state |= (1UL << _FUNCTION);
    return update_tri_layer_state(state, _NAVIGATION, _FUN, _BIGMAC);
}
```

This bug survives fixing every syntax error. Getting it to compile was never
going to be enough.

## Bug inventory (commit 3)

Build-blocking:

1. `[_BIGMAC]` defined outside the `keymaps[]` array.
2. `combo_t key_combos[COMBO_COUNT]` — `COMBO_COUNT` never defined.
3. Enum declares `RCRD_MCR02`/`PL_MCR02` (digit zero); initialiser uses
   `[RCRD_MCRO2]`/`[PL_MCRO2]` (letter O).
4. `CONFIG` used in the keymap and `music_mask_user()`, but the macro is
   `#define CONF LT(_CONFIG, KC_F4)`.
5. `DM_*` keycodes bound to combos without `DYNAMIC_MACRO_ENABLE = yes`.

Logic:

6. Layer calls inside `layer_state_set_user()` (above).
7. `BIOS`, `ENDENT`, `RMLINE`, `DUPELN`, `CUTLN` call `tap_code()` without
   checking `record->event.pressed` — each macro runs on press *and* release.
8. `#define SHENTER RSFT(KC_ENT)` is always Shift+Enter; the working layout used
   `KC_SFTENT` (Shift on hold, Enter on tap) — now `SC_SENT`.
9. `_GAME` is entirely `_______` except one `KC_ENT`, and sits *below* the
   layers it should override.
10. `BOOTMAGIC_ENABLE = no` and the only DFU route is a combo *in the firmware
    being replaced*. No escape hatch if a build misbehaves.
11. The `_SETTINGS`/RGB layer added in commit 2 was dropped in commit 3 and not
    replaced — all underglow control lost.
12. Several ASCII layer diagrams no longer match the arrays beneath them.

## QMK renames since Nov 2021

All verified against this tree.

| Was | Is now |
|-----|--------|
| `RESET` | `QK_BOOT` |
| `EEP_RST` | `EE_CLR` |
| `KC_NLCK` | `KC_NUM` |
| `KC_LOCK` | `QK_LOCK` (still needs `KEY_LOCK_ENABLE = yes`) |
| `KC_SFTENT` | `SC_SENT` |
| `CMB_TOG` | `CM_TOGG` |
| `AU_TOG` | `AU_TOGG` |
| `MU_TOG` | `MU_TOGG` |
| `MU_MOD` | `MU_NEXT` |
| `KC_BTN1` / `KC_BTN2` | `MS_BTN1` / `MS_BTN2` |
| `KC_MS_U` / `D` / `L` / `R` | `MS_UP` / `MS_DOWN` / `MS_LEFT` / `MS_RGHT` |
| `KC_WH_U` / `KC_WH_D` | `MS_WHLU` / `MS_WHLD` |
| `KC_ACL0` / `1` / `2` | `MS_ACL0` / `1` / `2` |
| `RGB_TOG` / `MOD` / `RMOD` | `UG_TOGG` / `UG_NEXT` / `UG_PREV` |
| `RGB_SAI` / `SAD` / `VAI` / `VAD` | `UG_SATU` / `UG_SATD` / `UG_VALU` / `UG_VALD` |
| `RGB_SPI` / `RGB_SPD` | `UG_SPDU` / `UG_SPDD` |

`config.h`:

| Was | Is now |
|-----|--------|
| `IGNORE_MOD_TAP_INTERRUPT` | **delete** — QMK `#error`s on it; now the default |
| `TAPPING_FORCE_HOLD` | `QUICK_TAP_TERM 0` |
| `combo_t key_combos[COMBO_COUNT]` | `combo_t key_combos[]` (count derived; drop `COMBO_LEN`) |

Still valid, unchanged: `TAPPING_TERM`, `HOLD_ON_OTHER_KEY_PRESS`,
`COMBO_NO_TIMER`, `EXTRA_SHORT_COMBOS`, `NK_ON`, `KC_MRWD`/`KC_MFFD`, the `DM_*`
keycodes, `tap_random_base64()`, `update_tri_layer_state()`,
`LAYOUT_preonic_1x2uC`.

## Build environment

Verified working in this repo — a stock `preonic/rev3` firmware links and
produces a flashable binary (70890 bytes).

```sh
apt install gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi dfu-util
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt qmk
git submodule update --init --recursive lib/chibios lib/chibios-contrib
make preonic/rev3:default
```

**Confirm the target before flashing.** QMK now ships two rev3 targets:
`preonic/rev3` (OLKB) and `preonic/rev3_drop` (Drop-manufactured, declares
`CUSTOM_MATRIX = yes` and ships its own `matrix.c`). They are not
interchangeable. The split did not exist in 2021, when a single `preonic/rev3`
covered both.

## Decisions

- **Board is the Drop-manufactured Preonic**, so the build target is
  `preonic/rev3_drop`, not `preonic/rev3`. Both are kept building in CI in case
  that turns out to be wrong.
- **Verbatim port first**, then the redesign, so any misbehaviour can be
  attributed to one deliberate change rather than to the port.
- **Keep:** the always-on `_FUNCTION` layer, Colemak/QWERTY switching, per-layer
  underglow.
- **Drop:** combos, dynamic macros, text-editing macros.
- **Mode indication is a first-class requirement**, not a nicety. Two signals:
  underglow colour for *where you are*, a per-layout tune for *something just
  changed*.

## What is on this branch

| Keymap | What it is |
|--------|-----------|
| `dooroflife` | The layout in daily use since 2021, renames only. Proven identical by `verify_verbatim.py` — all 8 layers x 59 positions. |
| `dooroflife_v2` | The redesign: always-on `_FUNCTION`, Colemak/QWERTY switching, per-layer underglow. Guarded by `verify_coverage.py`. |

Both build clean on `preonic/rev3_drop` and `preonic/rev3`, and both are built
in CI on every push by `.github/workflows/build_preonic.yml`.

### How v2 differs from what you use today

At rest, `dooroflife_v2` in Colemak is identical to the current layout at 58 of
59 key positions. The single difference: the top-left key keeps its `KC_F7` tap
but no longer reaches the vestigial second numpad. The settings layer stays on
right Ctrl, where it has been since 2021.

New in v2:

- `BASE_CM` / `BASE_QW` / `BASE_TG` on the settings-layer home row (hold right
  Ctrl, then `A` / `R` / `S` in Colemak) set Colemak, toggle, or set QWERTY.
  The choice persists to EEPROM, so it survives unplugging.
- Underglow at rest shows the base layout — cyan for Colemak, amber for QWERTY.
  Holding a layer key shows that layer's colour instead.
- Switching layout plays that layout's tune.
- Underglow colouring stands down entirely while the lighting is off or running
  an animation, and preserves the brightness set with `UG_VALU`/`UG_VALD`.

## Flashing

```sh
make preonic/rev3_drop:dooroflife          # or :dooroflife_v2
make preonic/rev3_drop:dooroflife:flash    # build and flash in one step
```

Three ways into the bootloader, in order of preference:

1. **Bootmagic** — hold the top-left key (Esc position) while plugging the board
   in. Enabled at the keyboard level, so it works regardless of the keymap.
2. **`QK_BOOT`** — hold right Ctrl, then the top-right key.
3. **The physical reset button** on the underside of the PCB. This one does not
   depend on the firmware working at all, which is the point.

## Verification

```sh
# prove the verbatim port still matches the 2021 Configurator layout
python3 keyboards/preonic/keymaps/dooroflife/verify_verbatim.py ../qmk_preonic

# prove _FUNCTION leaves no dead keys and no momentary layer is unreachable
python3 keyboards/preonic/keymaps/dooroflife_v2/verify_coverage.py
```

## Remaining

1. **Flash `dooroflife` and use it for a day.** This is the checkpoint that
   matters: if it feels different from what is on the board now, the port is
   wrong and that must be resolved before building on it.
2. **Then flash `dooroflife_v2`.** Confirm the always-on `_FUNCTION` layer holds
   — every key working, not just the letters — and that the underglow tracks the
   mode clearly enough to be useful.
3. **Tune from there.** Whether `_FKEYS2`/`_NUMPAD2` are genuinely unused, and
   whether the QWERTY layer's displaced `P` matters in practice.

Deliberately not done, per the decisions above: combos, dynamic macros, the
text-editing macros, and the `_GAME` layer.
