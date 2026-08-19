#pragma once

#ifdef AUDIO_ENABLE
#    define STARTUP_SONG SONG(PREONIC_SOUND)

/* Indexed by base layer number, so this must stay in the same order as the
 * first two entries of `enum layers`: _COLEMAK, then _QWERTY. Switching base
 * layout plays the matching tune — the audible half of "you just changed
 * mode", with the underglow colour carrying the "you are here" half. */
#    define DEFAULT_LAYER_SONGS \
        { SONG(COLEMAK_SOUND), SONG(QWERTY_SOUND) }
#endif

/* How long a dual-role key must be held to count as a hold rather than a tap.
 * Carried over from the 2021 config. */
#define TAPPING_TERM 180

/* Once a dual-role key is held and a second key is pressed, resolve the first
 * as a hold immediately. Suits fast typing and the long-ish tapping term above.
 *
 * IGNORE_MOD_TAP_INTERRUPT used to sit alongside this. It was removed from QMK
 * in 2023 — it is now the default behaviour, and defining it is a build error.
 */
#define HOLD_ON_OTHER_KEY_PRESS

/* Lets a dual-role key be held as a modifier right after being tapped, instead
 * of repeating the tap. This is the 2021 config's TAPPING_FORCE_HOLD, renamed. */
#define QUICK_TAP_TERM 0
