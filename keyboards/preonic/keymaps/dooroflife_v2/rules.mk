# Audio is the "something just changed" cue for base-layout switching, and
# muse.c backs the audio/music support the board ships with.
SRC += muse.c

# QK_BOOT lives on the settings layer, but bootmagic is the escape hatch that
# does not depend on this firmware working: hold the top-left key while
# plugging the board in to land in the bootloader.
BOOTMAGIC_ENABLE = yes
