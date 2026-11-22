"""Every tunable Modern value, kept together for cabinet tuning."""

# Club locations: name -> (display name, lamp or None, voice character)
LOCATIONS = {
    "bar": ("the Bar", "l_xxx_47", "bartender"),
    "kitchen": ("the Kitchen", "l_xxx_45", "cook"),
    "bandstand": ("the Bandstand", "l_xxx_46", "bandleader"),
    "coat_check": ("the Coat Check", "l_xxx_43", "coat_check"),
    # The Booths are the whole right drop bank, shown by its bank lamp (L29).
    "booths": ("the Booths", "booths", "hostess"),
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
SONG_READ_MS = 8000  # the jukebox holds the ball (and the record crackles) while the instructions are read
SONG_START_MS = 4000  # the artist's song starts this long after the pick, over the crackle
SELECT_PROGRESS_MS = 100

# Lamps
FLASH_MS = 250
REFUSAL_GAP_MS = 3000  # a location refuses once, not for every hit in a burst
SONG_LAMPS = tuple(f"l_xxx_{n}" for n in range(33, 43))
MULTIPLIER_LAMPS = ("l_xxx_30", "l_xxx_31", "l_xxx_32")  # song multiplier 2x-4x on in-play scores
OVATION_LAMPS = ("l_xxx_04", "l_xxx_05", "l_xxx_06", "l_xxx_07")  # Standing Ovation 2x-5x on the bonus
CRATER_LAMPS = ("l_xxx_27", "l_xxx_26", "l_xxx_25", "l_xxx_24")  # craters 1..4
DROP_LAMPS = tuple(f"l_xxx_{n}" for n in range(19, 24))  # beside the top bank, left to right
SKILL_BANK = "top_bank"  # the bank the skill-shot cascade lights
BOOTHS_LAMP = "booths"  # virtual: the lamp director maps it to L29 and the standing right-bank drop lamps
BOOTHS_BANK = "right_bank"
BANK_LAMPS = {"top_bank": "l_xxx_28", "right_bank": "l_xxx_29"}
SHOOT_AGAIN_LAMP = "l_xxx_03"  # L1 is the stock tilt relay, not a lamp
SPECIAL_LAMP = "l_xxx_44"
EXTRA_BALL_LAMP = "l_xxx_45"

# Jukebox
SELECTOR_TIMEOUT_MS = 10_000
DEFAULT_SONG_MS = 60_000
MULTIPLIER_EVERY = 5
MAX_SONG_MULTIPLIER = 4
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
MAX_OVATION = 5

# Tilt
WARNINGS_TO_TILT = 2  # one warning, then tilt

# Callouts
QUIP_GAP_MS = 20_000
TARGET_REMINDER_MS = 12_000  # repeat the nickel target callout this often while hunting
QUIP_CHANCE = 0.35
QUIP_CHECK_MS = 5_000

# Splash

# Song modes (before the song multiplier)
SONG_COMPLETION_AWARD = 250_000
HURRY_START, HURRY_END, HURRY_MS = 1_000_000, 100_000, 20_000
LADDER_RUNGS = (75_000, 150_000, 225_000, 300_000)
LADDER_HOLD_MS = 2_000  # long enough for the rung screen and callout
POT_START, POT_STEP, POT_COLLECT_BONUS, POT_COLLECTS = 5_000, 1_250, 50_000, 3
ROVE_MS, ROVE_VALUE, ROVE_HITS, ROVE_FREEZE_MS = 6_000, 250_000, 3, 6_000
JACKPOT_VALUES, JACKPOT_STEP, JACKPOTS_TO_COMPLETE = (150_000, 200_000, 250_000, 300_000), 25_000, 3
ROUND_MS = 60_000  # every song mode stops here, however long the song file is
JACKPOT_ROUND_MS = 45_000
PARTY_FACTOR, LAST_DANCE_AWARD = 2, 600_000
ORDER_PICKUP, ORDER_START, ORDER_END, ORDER_MS = 75_000, 900_000, 100_000, 20_000
REQUEST_VALUES, FINAL_REQUEST_AWARD = (50_000, 75_000, 100_000, 125_000, 150_000), 250_000
DANCE_FACTOR, DANCE_HITS, PACKED_FLOOR_AWARD = 5, 25, 550_000
DIAL_STEP_MS, DIAL_AUTO_STOP_MS, HIT_ME_VALUE, HIT_ME_HITS = 250, 5_000, 250_000, 3

# Rent Party multiball (Gate Crasher)
LOCK_BANK = "top_bank"  # completing it lights the lock for one ball
LOCKS_FOR_MULTIBALL = 3
RENT_PARTY_BUILD_UP_MS = 8_000  # the riser and announcement before the locked balls are released
SCORE_LOCK_LIT = 25_000
SCORE_BALL_LOCKED = 50_000
JACKPOT_BASE, JACKPOT_INCREMENT, JACKPOTS_FOR_SUPER = 250_000, 50_000, 3
SUPER_JACKPOT = 1_000_000

# Ambient lamp patterns: a background layer on lamps no feature is using (custom_code/modern/ambient.py).
AMBIENT_ENABLED = True
AMBIENT_MS = 50
# Playfield lamp positions from monitor/monitor.yaml (x across, y down). L8, L15 and L16 drive coils.
LAMP_XY = {
    "l_xxx_03": (0.1469, 0.906),
    "l_xxx_04": (0.4166, 0.5715),
    "l_xxx_05": (0.4993, 0.5715),
    "l_xxx_06": (0.3965, 0.5293),
    "l_xxx_07": (0.518, 0.5293),
    "l_xxx_17": (0.4579, 0.6328),
    "l_xxx_18": (0.4566, 0.6001),
    "l_xxx_19": (0.3138, 0.2132),
    "l_xxx_20": (0.3418, 0.1928),
    "l_xxx_21": (0.3645, 0.1737),
    "l_xxx_22": (0.3965, 0.158),
    "l_xxx_23": (0.4339, 0.1431),
    "l_xxx_24": (0.8678, 0.0831),
    "l_xxx_25": (0.8692, 0.1192),
    "l_xxx_26": (0.8598, 0.1553),
    "l_xxx_27": (0.8652, 0.1914),
    "l_xxx_28": (0.4393, 0.2064),
    "l_xxx_29": (0.6622, 0.4884),
    "l_xxx_30": (0.6355, 0.4067),
    "l_xxx_31": (0.6142, 0.3753),
    "l_xxx_32": (0.5861, 0.3406),
    "l_xxx_33": (0.4566, 0.7766),
    "l_xxx_34": (0.4619, 0.7459),
    "l_xxx_35": (0.4406, 0.7146),
    "l_xxx_36": (0.4873, 0.6846),
    "l_xxx_37": (0.4072, 0.6526),
    "l_xxx_38": (0.5354, 0.6226),
    "l_xxx_39": (0.3458, 0.592),
    "l_xxx_40": (0.6101, 0.5613),
    "l_xxx_41": (0.2764, 0.547),
    "l_xxx_42": (0.6769, 0.5354),
    "l_xxx_43": (0.6609, 0.3099),
    "l_xxx_44": (0.4259, 0.0586),
    "l_xxx_45": (0.1949, 0.5027),
    "l_xxx_46": (0.3071, 0.4877),
    "l_xxx_47": (0.4993, 0.0606),
}
