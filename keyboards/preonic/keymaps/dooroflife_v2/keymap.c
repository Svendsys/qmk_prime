/* DoorOfLife v2 — Preonic rev3
 *
 * PHASE 3: the 2021 redesign, rebuilt so it actually compiles and actually
 * works. Kept from the original attempt: the always-on _FUNCTION layer, the
 * Colemak/QWERTY split, and per-layer underglow. Dropped at the owner's
 * request: combos, dynamic macros, and the text-editing macros.
 *
 * ── The architecture ────────────────────────────────────────────────────────
 *
 * The base layers hold *nothing but alphas*. Every modifier, number, symbol
 * and layer key lives on _FUNCTION, which is permanently switched on above
 * them. Swapping Colemak <-> QWERTY therefore moves letters and nothing else.
 *
 *   _COLEMAK / _QWERTY   alphas, KC_NO everywhere else
 *   _FUNCTION            always on; transparent over the alphas
 *   everything above     momentary, reached by holding a key
 *
 * Every momentary layer MUST sit above _FUNCTION in the enum, or _FUNCTION
 * would mask it.
 *
 * ── Knowing where you are ───────────────────────────────────────────────────
 *
 * Two independent signals, because they answer different questions:
 *
 *   Underglow  = what mode am I in *right now*. At rest the colour shows the
 *                base layer (cyan Colemak / amber QWERTY); while a layer key
 *                is held it shows that layer.
 *   Sound      = something just changed. Switching base layer plays a
 *                distinct tune per layout (DEFAULT_LAYER_SONGS in config.h).
 *
 * The underglow deliberately yields to your own controls: if you switch the
 * underglow off, or pick an animation instead of a static colour, the layer
 * colouring stops touching it until you set it back to static.
 *
 * ── Why layer_on() is nowhere in this file ─────────────────────────────────
 *
 * The 2021 version kept _FUNCTION on by calling layer_on() from inside
 * layer_state_set_user(). QMK assigns that hook's *return value* to
 * layer_state afterwards, so the inner call was silently undone — leaving a
 * keyboard where letters worked and nothing else did. The fix is to fold the
 * layer into the state we return. See layer_state_set_user() below.
 */

#include QMK_KEYBOARD_H

enum layers {
    _COLEMAK = 0,   /* base — alphas only                                  */
    _QWERTY,        /* base — alphas only, for games that assume QWERTY    */
    _FUNCTION,      /* ALWAYS ON — mods, numbers, symbols, layer keys      */
    _FKEYS,         /* hold KC_HOME                                        */
    _NAV,           /* hold KC_COMM — arrows, brackets, numpad             */
    _MOUSE,         /* hold KC_END                                         */
    _MEDIA,         /* hold KC_GRV                                         */
    _SETTINGS,      /* hold KC_RCTL — layout switch, underglow, audio, boot */
};

enum keycodes {
    BASE_CM = SAFE_RANGE,  /* set base layout to Colemak (persists)  */
    BASE_QW,               /* set base layout to QWERTY  (persists)  */
    BASE_TG,               /* flip between the two       (persists)  */
};

/* Layer keys, named so the keymap grid stays readable. */
#define L_SET   LT(_SETTINGS, KC_RCTL)
#define L_MED   LT(_MEDIA,    KC_GRV)
#define L_FN    LT(_FKEYS,    KC_HOME)
#define L_MSE   LT(_MOUSE,    KC_END)
#define L_NAV   LT(_NAV,      KC_COMM)
#define ALT_DEL LALT_T(KC_DEL)
#define ALT_APP RALT_T(KC_APP)

/* Underglow hues, 0-255. Chosen so neighbouring modes never look alike, and
 * so the two base layouts sit on opposite sides of the wheel — you should be
 * able to tell Colemak from QWERTY out of the corner of your eye. */
#define HUE_COLEMAK  128  /* cyan    */
#define HUE_QWERTY    21  /* amber   */
#define HUE_FKEYS    234  /* pink    */
#define HUE_NAV      191  /* violet  */
#define HUE_MOUSE     85  /* green   */
#define HUE_MEDIA      0  /* red     */
#define HUE_SETTINGS 170  /* blue    */

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    /* Colemak — alphas only. Everything blank here comes from _FUNCTION. */
    [_COLEMAK] = LAYOUT_preonic_1x2uC(
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    KC_J,    KC_L,    KC_U,    KC_Y,    XXXXXXX, XXXXXXX,
        XXXXXXX, KC_A,    KC_R,    KC_S,    KC_T,    KC_D,    KC_H,    KC_N,    KC_E,    KC_I,    KC_O,    XXXXXXX,
        XXXXXXX, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_K,    KC_M,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,     XXXXXXX,      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX),

    /* QWERTY — alphas only, for games that read scancodes as QWERTY.
     * Note P sits at the right of the home row, not the top row: the top-row
     * position it would occupy is KC_MINS on _FUNCTION. WASD and the number
     * row are exactly where a game expects them, which is the point. */
    [_QWERTY] = LAYOUT_preonic_1x2uC(
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,    XXXXXXX, XXXXXXX,
        XXXXXXX, KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_H,    KC_J,    KC_K,    KC_L,    KC_P,    XXXXXXX,
        XXXXXXX, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_N,    KC_M,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,     XXXXXXX,      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX),

    /* Function — ALWAYS ON. Transparent over the alpha block so the base
     * layer shows through; everything else on the board lives here. */
    [_FUNCTION] = LAYOUT_preonic_1x2uC(
        KC_ESC,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_EQL,
        KC_F7,   _______, _______, _______, _______, _______, _______, _______, _______, _______, KC_MINS, ALT_APP,
        KC_TAB,  _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, KC_BSPC,
        KC_LSFT, _______, _______, _______, _______, _______, _______, _______, KC_SCLN, KC_BSLS, KC_SLSH, SC_SENT,
        KC_LCTL, KC_LGUI, ALT_DEL, L_MED,   L_FN,        KC_SPC,       L_MSE,   L_NAV,   KC_DOT,  KC_QUOT, L_SET),

    /* F-keys — F1-F12 across the top, page/home/end on the left hand. */
    [_FKEYS] = LAYOUT_preonic_1x2uC(
        KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
        _______, KC_PGDN, _______, KC_PGUP, KC_HOME, _______, _______, _______, _______, _______, _______, _______,
        KC_INS,  _______, _______, _______, KC_END,  _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,     _______,      _______, _______, _______, _______, _______),

    /* Navigation — arrows and brackets left, full numpad right. */
    [_NAV] = LAYOUT_preonic_1x2uC(
        KC_BSPC, KC_LBRC, KC_ENT,  KC_RBRC, KC_INS,  _______, _______, _______, KC_NUM,  KC_PSLS, KC_PAST, KC_PMNS,
        KC_DEL,  KC_HOME, KC_UP,   KC_END,  KC_LPRN, KC_PGUP, _______, _______, KC_P7,   KC_P8,   KC_P9,   KC_PPLS,
        _______, KC_LEFT, KC_DOWN, KC_RGHT, KC_RPRN, KC_PGDN, _______, _______, KC_P4,   KC_P5,   KC_P6,   KC_PCMM,
        _______, KC_PSCR, KC_NUM,  KC_CAPS, _______, _______, _______, _______, KC_P1,   KC_P2,   KC_P3,   KC_PEQL,
        _______, _______, _______, _______, _______,     _______,      _______, KC_P0,   KC_P0,   KC_PDOT, KC_PENT),

    /* Mouse — movement under the home position, wheel and acceleration beside. */
    [_MOUSE] = LAYOUT_preonic_1x2uC(
        _______, MS_ACL0, MS_ACL1, MS_ACL2, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, MS_BTN1, MS_UP,   MS_BTN2, MS_WHLU, _______, _______, _______, _______, _______, _______, _______,
        _______, MS_LEFT, MS_DOWN, MS_RGHT, MS_WHLD, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,     _______,      _______, _______, _______, _______, _______),

    /* Media — volume and transport on the left hand. */
    [_MEDIA] = LAYOUT_preonic_1x2uC(
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, KC_VOLD, KC_MPLY, KC_VOLU, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, KC_MRWD, KC_MSTP, KC_MFFD, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, KC_MPRV, KC_MUTE, KC_MNXT, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,     _______,      _______, _______, _______, _______, _______),

    /* Settings — reached by holding right Ctrl, exactly where it has been
     * since 2021. Layout switching sits on the home row under your strongest
     * fingers, because it is the one thing here you reach for mid-session.
     * QK_BOOT and EE_CLR are tucked into far corners on purpose. */
    [_SETTINGS] = LAYOUT_preonic_1x2uC(
        NK_ON,   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, EE_CLR,  QK_BOOT,
        UG_TOGG, XXXXXXX, UG_SATU, XXXXXXX, UG_VALU, UG_SPDU, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, BASE_CM, BASE_TG, BASE_QW, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, UG_PREV, UG_SATD, UG_NEXT, UG_VALD, UG_SPDD, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,     AU_TOGG,      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, _______),
};

/* ── underglow ─────────────────────────────────────────────────────────────
 *
 * Colour follows the topmost active layer. At rest that is _FUNCTION, which
 * is not a mode you "enter" — so it shows the base layout instead, and the
 * underglow answers "Colemak or QWERTY?" whenever nothing is held.
 */
#ifdef RGBLIGHT_ENABLE
static void apply_underglow(uint8_t top, layer_state_t defaults) {
    /* Leave the lighting alone if it is off, or running an animation the
     * owner picked deliberately. Layer colouring is a static-mode feature. */
    if (!rgblight_is_enabled() || rgblight_get_mode() != RGBLIGHT_MODE_STATIC_LIGHT) {
        return;
    }

    uint8_t hue;
    switch (top) {
        case _FKEYS:    hue = HUE_FKEYS;    break;
        case _NAV:      hue = HUE_NAV;      break;
        case _MOUSE:    hue = HUE_MOUSE;    break;
        case _MEDIA:    hue = HUE_MEDIA;    break;
        case _SETTINGS: hue = HUE_SETTINGS; break;
        default:
            hue = (defaults & (1UL << _QWERTY)) ? HUE_QWERTY : HUE_COLEMAK;
            break;
    }
    /* Keep the owner's brightness — UG_VALU/UG_VALD stay meaningful. */
    rgblight_sethsv_noeeprom(hue, 255, rgblight_get_val());
}
#else
static void apply_underglow(uint8_t top, layer_state_t defaults) {
    (void)top;
    (void)defaults;
}
#endif

/* ── layer state ───────────────────────────────────────────────────────────*/

layer_state_t layer_state_set_user(layer_state_t state) {
    /* Fold _FUNCTION into the returned state. Calling layer_on() here instead
     * would be overwritten the moment this function returns — that is the bug
     * that broke the 2021 build. */
    state |= (1UL << _FUNCTION);
    apply_underglow(get_highest_layer(state), default_layer_state);
    return state;
}

layer_state_t default_layer_state_set_user(layer_state_t state) {
    /* Switching base layout does not change layer_state, so recolour here.
     * Use the incoming state, not the global — the global is not updated yet. */
    apply_underglow(get_highest_layer(layer_state | (1UL << _FUNCTION)), state);
    return state;
}

void keyboard_post_init_user(void) {
    /* layer_state_set_user() has not run yet at boot; light up correctly. */
    apply_underglow(get_highest_layer(layer_state | (1UL << _FUNCTION)), default_layer_state);
}

/* ── base layout switching ─────────────────────────────────────────────────
 *
 * set_single_persistent_default_layer() writes the choice to EEPROM (so it
 * survives unplugging) and plays that layout's tune from DEFAULT_LAYER_SONGS.
 */
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (!record->event.pressed) {
        return true;  /* act on press only — never twice per keystroke */
    }

    switch (keycode) {
        case BASE_CM:
            set_single_persistent_default_layer(_COLEMAK);
            return false;
        case BASE_QW:
            set_single_persistent_default_layer(_QWERTY);
            return false;
        case BASE_TG:
            set_single_persistent_default_layer(
                (default_layer_state & (1UL << _QWERTY)) ? _COLEMAK : _QWERTY);
            return false;
        default:
            return true;
    }
}
