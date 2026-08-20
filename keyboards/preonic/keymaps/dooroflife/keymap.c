/* DoorOfLife — Preonic rev3
 *
 * PHASE 2: verbatim port.
 *
 * This is the layout exported from the QMK Configurator in Nov 2021 and in
 * daily use ever since (Svendsys/qmk_preonic @ 69bd56e6), carried forward to
 * modern QMK with *only* the mechanical keycode renames applied. No keys were
 * moved, added or removed. If this build feels different from the firmware
 * currently on the board, the port is wrong — say so before we build on it.
 *
 * Base is Colemak. Every thumb and pinky layer key is a layer-tap, so it still
 * types its own legend when tapped and only shifts layer when held.
 *
 * Renames applied vs. the 2021 original:
 *   KC_SFTENT  -> SC_SENT         KC_BTN1/2   -> MS_BTN1/2
 *   KC_NLCK    -> KC_NUM          KC_MS_U/D/L/R -> MS_UP/DOWN/LEFT/RGHT
 *   RESET      -> QK_BOOT         KC_WH_U/D   -> MS_WHLU/MS_WHLD
 *   EEP_RST    -> EE_CLR          KC_ACL0/1/2 -> MS_ACL0/1/2
 *   RGB_*      -> UG_*            (underglow keycodes moved prefix)
 */

#include QMK_KEYBOARD_H

/* Explicit values: these are the same indices the Configurator emitted, so the
 * LT() targets below are provably identical to the original numeric keymap. */
enum layers {
    _BASE     = 0,  /* Colemak + number row                                  */
    _FKEYS    = 1,  /* F1-F12, page/home/end, insert       — hold KC_HOME    */
    _NAV      = 2,  /* arrows, brackets, parens + numpad   — hold KC_COMM    */
    _SETTINGS = 3,  /* underglow, NKRO, bootloader, EEPROM — hold KC_RCTL    */
    _MOUSE    = 4,  /* mouse movement, buttons, wheel      — hold KC_END     */
    _MEDIA    = 5,  /* volume, transport                   — hold KC_GRV     */
    _FKEYS2   = 6,  /* F-keys again, reversed              — hold KC_F6 on L1 */
    _NUMPAD2  = 7,  /* second scattered numpad             — hold KC_F7      */
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    /* Base — Colemak. Number row across the top, Shift/Enter dual-role on the
     * right pinky, Alt/Del and the five layer-taps along the bottom row. */
    [_BASE] = LAYOUT_preonic_1x2uC(
        KC_ESC,             KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_EQL,
        LT(_NUMPAD2,KC_F7), KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    KC_J,    KC_L,    KC_U,    KC_Y,    KC_MINS, RALT_T(KC_APP),
        KC_TAB,             KC_A,    KC_R,    KC_S,    KC_T,    KC_D,    KC_H,    KC_N,    KC_E,    KC_I,    KC_O,    KC_BSPC,
        KC_LSFT,            KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_K,    KC_M,    KC_SCLN, KC_BSLS, KC_SLSH, SC_SENT,
        KC_LCTL, KC_LGUI, LALT_T(KC_DEL), LT(_MEDIA,KC_GRV), LT(_FKEYS,KC_HOME),   KC_SPC,   LT(_MOUSE,KC_END), LT(_NAV,KC_COMM), KC_DOT, KC_QUOT, LT(_SETTINGS,KC_RCTL)),

    /* F-keys — F1-F12 along the top, page/home/end clustered on the left hand.
     * Holding KC_F6 here reaches _FKEYS2. */
    [_FKEYS] = LAYOUT_preonic_1x2uC(
        KC_F1,              KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
        LT(_FKEYS2,KC_F6),  KC_PGDN, _______, KC_PGUP, KC_HOME, _______, _______, _______, _______, _______, _______, _______,
        KC_INS,             _______, _______, _______, KC_END,  _______, _______, _______, _______, _______, _______, _______,
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,       _______,      _______, _______, _______, _______, _______),

    /* Navigation — arrow cluster and brackets on the left hand, full numpad on
     * the right. */
    [_NAV] = LAYOUT_preonic_1x2uC(
        KC_BSPC,            KC_LBRC, KC_ENT,  KC_RBRC, KC_INS,  _______, _______, _______, KC_NUM,  KC_PSLS, KC_PAST, KC_PMNS,
        KC_DEL,             KC_HOME, KC_UP,   KC_END,  KC_LPRN, KC_PGUP, _______, _______, KC_P7,   KC_P8,   KC_P9,   KC_PPLS,
        _______,            KC_LEFT, KC_DOWN, KC_RGHT, KC_RPRN, KC_PGDN, _______, _______, KC_P4,   KC_P5,   KC_P6,   KC_PCMM,
        _______,            KC_PSCR, KC_NUM,  KC_CAPS, _______, _______, _______, _______, KC_P1,   KC_P2,   KC_P3,   KC_PEQL,
        _______, _______, _______, _______, _______,       _______,      _______, KC_P0,   KC_P0,   KC_PDOT, KC_PENT),

    /* Settings — underglow control, NKRO toggle, and the two destructive keys.
     * QK_BOOT enters the bootloader; EE_CLR wipes stored settings. */
    [_SETTINGS] = LAYOUT_preonic_1x2uC(
        NK_ON,              XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, QK_BOOT,
        UG_TOGG,            XXXXXXX, UG_SATU, XXXXXXX, UG_VALU, UG_SPDU, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, EE_CLR,
        XXXXXXX,            UG_PREV, UG_SATD, UG_NEXT, UG_VALD, UG_SPDD, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX,            XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,       XXXXXXX,      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, _______),

    /* Mouse — movement on the home position, buttons either side, wheel and
     * acceleration alongside. */
    [_MOUSE] = LAYOUT_preonic_1x2uC(
        _______,            MS_ACL0, MS_ACL1, MS_ACL2, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            MS_BTN1, MS_UP,   MS_BTN2, MS_WHLU, _______, _______, _______, _______, _______, _______, _______,
        _______,            MS_LEFT, MS_DOWN, MS_RGHT, MS_WHLD, _______, _______, _______, _______, _______, _______, _______,
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,       _______,      _______, _______, _______, _______, _______),

    /* Media — volume and transport on the left hand. */
    [_MEDIA] = LAYOUT_preonic_1x2uC(
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            KC_VOLD, KC_MPLY, KC_VOLU, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            KC_MRWD, KC_MSTP, KC_MFFD, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            KC_MPRV, KC_MUTE, KC_MNXT, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,       _______,      _______, _______, _______, _______, _______),

    /* F-keys, reversed — F12 on the left through F1 on the right. */
    [_FKEYS2] = LAYOUT_preonic_1x2uC(
        KC_F12,             KC_F11,  KC_F10,  KC_F9,   KC_F8,   KC_F7,   KC_F6,   KC_F5,   KC_F4,   KC_F3,   KC_F2,   KC_F1,
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______,            _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,       _______,      _______, _______, _______, _______, _______),

    /* Second numpad — digits scattered across the left hand. */
    [_NUMPAD2] = LAYOUT_preonic_1x2uC(
        KC_PPLS,            KC_EQL,  KC_0,    KC_9,    KC_8,    KC_7,    _______, _______, _______, _______, _______, _______,
        _______,            KC_P1,   _______, KC_P2,   KC_P6,   KC_P9,   _______, _______, _______, _______, _______, _______,
        KC_PAST,            _______, _______, _______, KC_P7,   KC_P0,   _______, _______, _______, _______, _______, _______,
        _______,            KC_P3,   KC_P4,   KC_P5,   KC_P8,   KC_PDOT, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, KC_LBRC, KC_RBRC,       _______,      _______, _______, _______, _______, _______),
};
