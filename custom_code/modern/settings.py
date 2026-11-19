"""Every tunable Modern value, kept together for cabinet tuning."""

# Club locations: name -> (display name, lamp or None, voice character)
LOCATIONS = {
    "bar": ("the Bar", "l_xxx_47", "bartender"),
    "kitchen": ("the Kitchen", "l_xxx_45", "cook"),
    "bandstand": ("the Bandstand", "l_xxx_46", "bandleader"),
    "coat_check": ("the Coat Check", "l_xxx_43", "coat_check"),
    # The Back Door insert's lamp output is not yet mapped, so it is screen-only.
    "back_door": ("the Back Door", None, "doorman"),
}
LOCATION_NAMES = tuple(LOCATIONS)
BANDSTAND_QUIET_MS = 1000

# Base scoring (before the song multiplier)
SCORE_SWITCH = 1_000          # bumpers, standup, rollunder, left return, outlanes
SCORE_SPIN = 500
SCORE_DROP = 5_000
SCORE_BANK = 25_000
SCORE_LOCATION = 10_000
SCORE_NICKEL = 25_000
SCORE_CRATER = 10_000
SCORE_CRATER_LIT = 25_000
SCORE_DROP_THE_NEEDLE = 50_000
SCORE_SPECIAL = 1_000_000

# Nickels
NICKEL_COSTS = (1, 2, 3, 4, 5)

# Input
SELECT_SWITCH = "s_green_button_right_56"
TAP_SWITCH = "s_green_button_right_56"
SELECT_HOLD_MS = 2000
SELECT_PROGRESS_MS = 100

# Lamps
FLASH_MS = 250
SONG_LAMPS = tuple(f"l_xxx_{n}" for n in range(33, 43))
MULTIPLIER_LAMPS = ("l_xxx_04", "l_xxx_05", "l_xxx_06", "l_xxx_07")
OVATION_LAMPS = ("l_xxx_30", "l_xxx_31", "l_xxx_32")
CRATER_LAMPS = ("l_xxx_27", "l_xxx_26", "l_xxx_25", "l_xxx_24")  # craters 1..4
DROP_LAMPS = tuple(f"l_xxx_{n}" for n in range(19, 24))
BANK_LAMPS = {"top_bank": "l_xxx_28", "right_bank": "l_xxx_29"}
SHOOT_AGAIN_LAMP = "l_xxx_01"
SPECIAL_LAMP = "l_xxx_44"
EXTRA_BALL_LAMP = "l_xxx_45"

# Jukebox
SELECTOR_TIMEOUT_MS = 10_000
DEFAULT_SONG_MS = 60_000
MULTIPLIER_EVERY = 5
MAX_SONG_MULTIPLIER = 5
SPECIAL_AFTER_SONGS = 10
EXTRA_BALL_SONGS = (3, 7)
MAX_EXTRA_BALLS = 2

# Holes
HOLE_HOLD_MS = 1000

# Bonus
BONUS_BUMPER = 100
BONUS_LOCATION = 2_500
BONUS_DROP = 1_000
BONUS_SONG = 25_000
MAX_OVATION = 4

# Tilt
WARNINGS_TO_TILT = 2  # one warning, then tilt

# Callouts
QUIP_GAP_MS = 20_000
QUIP_CHANCE = 0.35
QUIP_CHECK_MS = 5_000

# Splash
SPLASH_MS = 6_000
