extends MPFSlide
## Modern juke joint HUD. Builds its widgets in code, keeps the score strip visible
## under every overlay, and owns the jukebox music and voice callout playback.

const GOLD := Color("#ffcf5a")
const CREAM := Color("#f6e7c8")
const BURGUNDY := Color("#5a1020")
const TEAL := Color("#0f4a4a")
const DIM := Color("#8a7f70")
const BRASS := Color("#7a5a12")
const RED := Color("#8a1010")
const OVERLAY_STYLES := {"teal": TEAL, "gold": BRASS, "red": RED}
const DUCK_DB := -12.0
const VOICE_CUT_MS := 600  # lines posted together play one after another instead of cutting each other off
const LOCATIONS := ["Bar", "Kitchen", "Bandstand", "Coat Check", "Booths"]
const SONG_FADE_S := 2.0  # a song fades out when its round ends instead of cutting off

var title_font: Font = load("res://fonts/modern/Limelight-Regular.ttf")
var neon_font: Font = load("res://fonts/modern/Monoton-Regular.ttf")
var body_font: Font = load("res://fonts/modern/Oswald-Variable.ttf")

const NAMES := {"bar": "Bar", "kitchen": "Kitchen", "bandstand": "Bandstand", "coat_check": "Coat Check", "booths": "Booths"}
var score_label: Label  # the current player's score, as big as the screen allows
var sub_line: RichTextLabel  # player, ball and the other players' scores
var card: PanelContainer  # the one goal card: the nickel hunt, a mode, Rent Party or the bonus
var card_bar: ProgressBar  # time left in the song, along the top of the card
var card_label: Label
var card_title: RichTextLabel
var card_pips: Pips
var card_line: Label
var card_detail: Label
var lock_chip: PanelContainer
var lock_pips: Pips
var lock_state: Label
var caption: Label
var song_live := false
var song_artist := ""
var task_title_text := ""
var task_detail_text := ""
var mode_status := ""
var mode_done := 0
var mode_goal := 0
var rent_live := false
var rent_text := ""
var rent_done := 0
var rent_goal := 0
var bonus_text := ""
var overlay_root: Control
var selector: Control
var selector_cells: Array = []
var selector_timer: Label
var select_ring: ProgressBar
var music: AudioStreamPlayer
var effects: AudioStreamPlayer  # one-shot effects such as the Rent Party riser
var rent_party_song: AudioStream
var music_fade: Tween  # fades the house band out while the record crackles, and a song out when its round ends
var voice: AudioStreamPlayer
var artist_video: VideoStreamPlayer  # muted performer loop behind the HUD while a song is live
var artist_clips := PackedStringArray()
var artist_clip_last := -1
var voice_queue: Array = []  # [caption, file] lines waiting for the current voice to finish
var voice_started_ms := -VOICE_CUT_MS
const Playlist := preload("res://slides/playlist.gd")
var house_band := Playlist.new(Playlist.HOUSE_BAND_PREFIX, Playlist.HOUSE_BAND_COUNT)
var playing_house_band := false
var between_balls_song: AudioStream
var artist_pick_song: AudioStream  # loops while the jukebox artist selector is open
var between_balls := false  # a drained ball plays its own song until the next ball starts
var song_length_ms := 0.0
var song_elapsed_ms := 0.0
var song_paused := false
var selector_deadline := 0.0
var overlay_queue: Array = []
var overlay_busy := false
var bonus_lines: Array = []
var spin_root: Control  # Big Joe Turner's spinning record: shows while the spinner builds the pot
var spin_record: SpinRecord
var spin_pot: Label
var spin_gain: Label
var spin_hide_ms := 0
const SPIN_SHOW_MS := 1500
var hurry_root: Control  # Louis Jordan's hurry-up clock: a ring and the value draining as time runs out
var hurry_clock: HurryClock
var hurry_target: Label
var hurry_secs: Label
var hurry_value: Label
var hurry_live := false
var hurry_total_ms := 1.0
var hurry_elapsed_ms := 0.0
var hurry_start := 0
var hurry_end := 0
const HURRY_GREEN := Color("#5ad65a")
const HURRY_RED := Color("#ff3b30")
const HURRY_PANIC_MS := 5000.0

const EVENTS := [
	"modern_splash_show", "modern_splash_hide", "modern_nickel_directed", "modern_nickel_refused",
	"modern_nickel_awarded", "modern_jukebox_no_nickel", "modern_selector_opened",
	"modern_selector_highlight", "modern_artist_chosen", "modern_selector_closed", "modern_song_started",
	"modern_song_ended", "modern_song_paused", "modern_song_resumed", "modern_voice",
	"modern_select_progress", "modern_drop_the_needle", "modern_ball_saver_ready", "modern_ball_saved",
	"modern_extra_ball_lit", "modern_award_extra_ball", "modern_ball_locked", "modern_special_lit", "modern_special_awarded",
	"modern_bonus_line", "modern_bonus_total", "modern_bonus_void", "tilt_warning", "tilt",
	"modern_overlay", "modern_mode_status", "modern_task", "ball_will_end", "modern_floor_nickel", "game_ending", "ball_started",
	"modern_pot_spin", "modern_rent_party_build_up", "modern_rent_party_started", "modern_song_shot", "modern_jackpot", "modern_super_jackpot_lit", "modern_super_jackpot", "modern_rent_party_ended",
	"modern_hurry_up_started", "modern_hurry_up_ended",
]


func _ready() -> void:
	_build()
	for e in EVENTS:
		MPF.server.add_event_handler(e, _on_event)
	MPF.game.player_update.connect(_on_player_update)
	_render()
	_play_house_band()


func _exit_tree() -> void:
	for e in EVENTS:
		MPF.server.remove_event_handler(e, _on_event)
	if MPF.game.player_update.is_connected(_on_player_update):
		MPF.game.player_update.disconnect(_on_player_update)
	_set_duck(false)
	super()


# Layout -----------------------------------------------------------------
func _label(text: String, size: int, color: Color = CREAM, font: Font = null) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font if font else body_font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	l.add_theme_constant_override("shadow_offset_x", 2)
	l.add_theme_constant_override("shadow_offset_y", 2)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return l


func _panel(color: Color, border: Color = GOLD) -> PanelContainer:
	var p := PanelContainer.new()
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.border_color = border
	box.set_border_width_all(3)
	box.set_corner_radius_all(10)
	box.content_margin_left = 14
	box.content_margin_right = 14
	box.content_margin_top = 6
	box.content_margin_bottom = 6
	p.add_theme_stylebox_override("panel", box)
	return p


func _rich(size: int, font: Font = null) -> RichTextLabel:
	var r := RichTextLabel.new()
	r.bbcode_enabled = true
	r.fit_content = true
	r.scroll_active = false
	r.autowrap_mode = TextServer.AUTOWRAP_OFF
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.add_theme_font_override("normal_font", font if font else body_font)
	r.add_theme_font_size_override("normal_font_size", size)
	r.add_theme_color_override("default_color", CREAM)
	r.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	r.add_theme_constant_override("shadow_offset_x", 2)
	r.add_theme_constant_override("shadow_offset_y", 2)
	return r


class Pips extends Control:
	## Progress dots: filled gold for each step done, an empty ring for each to go.
	var done := 0
	var total := 0
	var radius := 16.0

	func set_count(d: int, t: int) -> void:
		done = d
		total = t
		visible = t > 0
		custom_minimum_size = Vector2(t * (radius * 2.0 + 12.0), radius * 2.0 + 8.0)
		queue_redraw()

	func _draw() -> void:
		for i in total:
			var c := Vector2(radius + 4.0 + i * (radius * 2.0 + 12.0), size.y / 2.0)
			if i < done:
				draw_circle(c, radius + 4.0, Color(1.0, 0.81, 0.35, 0.3))
				draw_circle(c, radius, Color("#ffcf5a"))
			else:
				draw_arc(c, radius - 1.5, 0, TAU, 40, Color("#ffcf5a"), 3.0)


func _place(node: Control, x: float, y: float, w: float, h: float) -> Control:
	node.position = Vector2(x, y)
	node.size = Vector2(w, h)
	add_child(node)
	return node


func _build() -> void:
	size = Vector2(1280, 720)
	var bg := TextureRect.new()
	bg.texture = load("res://images/modern/club_background.jpg")
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.modulate = Color(0.55, 0.5, 0.5)
	_place(bg, 0, 0, 1280, 720)

	_new_artist_video(bg)

	score_label = _place(_label("", 150, GOLD, title_font), 0, 0, 1280, 170)
	score_label.add_theme_color_override("font_outline_color", Color(GOLD, 0.22))
	score_label.add_theme_constant_override("outline_size", 16)
	score_label.add_theme_constant_override("shadow_offset_x", 3)
	score_label.add_theme_constant_override("shadow_offset_y", 3)
	sub_line = _place(_rich(30), 0, 176, 1280, 44)

	card = _panel(Color(BURGUNDY, 0.9))
	card.custom_minimum_size = Vector2(800, 0)
	var card_box := VBoxContainer.new()
	card_box.add_theme_constant_override("separation", 4)
	card.add_child(card_box)
	card_bar = ProgressBar.new()
	card_bar.show_percentage = false
	card_bar.custom_minimum_size = Vector2(0, 10)
	var fill := StyleBoxFlat.new()
	fill.bg_color = GOLD
	fill.set_corner_radius_all(5)
	var back := StyleBoxFlat.new()
	back.bg_color = Color(1, 1, 1, 0.15)
	back.set_corner_radius_all(5)
	card_bar.add_theme_stylebox_override("fill", fill)
	card_bar.add_theme_stylebox_override("background", back)
	card_box.add_child(card_bar)
	card_label = _label("", 20, GOLD)
	card_box.add_child(card_label)
	card_title = _rich(66, title_font)
	card_box.add_child(card_title)
	var line := HBoxContainer.new()
	line.alignment = BoxContainer.ALIGNMENT_CENTER
	line.add_theme_constant_override("separation", 14)
	card_pips = Pips.new()
	line.add_child(card_pips)
	card_line = _label("", 30)
	line.add_child(card_line)
	card_box.add_child(line)
	card_detail = _label("", 24, Color("#d8ccb4"))
	card_detail.autowrap_mode = TextServer.AUTOWRAP_WORD
	card_box.add_child(card_detail)
	_place(card, 240, 250, 800, 0)

	lock_chip = _panel(Color(0.03, 0.02, 0.02, 0.82), Color(GOLD, 0.55))
	var lock_box := HBoxContainer.new()
	lock_box.add_theme_constant_override("separation", 14)
	lock_chip.add_child(lock_box)
	lock_box.add_child(_label("LOCKS", 30, GOLD))
	lock_pips = Pips.new()
	lock_pips.radius = 13.0
	lock_box.add_child(lock_pips)
	lock_state = _label("", 28)
	lock_box.add_child(lock_state)
	_place(lock_chip, 440, 530, 0, 0)

	caption = _place(_label("", 26, CREAM), 90, 640, 1100, 40)

	select_ring = ProgressBar.new()
	select_ring.show_percentage = false
	select_ring.max_value = 1.0
	_place(select_ring, 1040, 540, 220, 14)
	select_ring.visible = false

	spin_root = Control.new()
	_place(spin_root, 30, 120, 260, 300)
	spin_pot = _label("", 30, GOLD, title_font)
	spin_pot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	spin_root.add_child(spin_pot)
	spin_pot.position = Vector2(0, 0)
	spin_pot.size = Vector2(260, 44)
	spin_record = SpinRecord.new()
	spin_record.position = Vector2(30, 50)
	spin_record.size = Vector2(200, 200)
	spin_record.pivot_offset = Vector2(100, 100)
	spin_root.add_child(spin_record)
	spin_gain = _label("", 34, CREAM, title_font)
	spin_gain.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	spin_root.add_child(spin_gain)
	spin_gain.position = Vector2(0, 256)
	spin_gain.size = Vector2(260, 44)
	spin_gain.pivot_offset = Vector2(130, 22)
	spin_root.visible = false

	hurry_root = Control.new()
	_place(hurry_root, 30, 110, 280, 360)
	hurry_root.pivot_offset = Vector2(140, 180)
	hurry_target = _label("", 30, CREAM, title_font)
	hurry_root.add_child(hurry_target)
	hurry_target.position = Vector2(0, 0)
	hurry_target.size = Vector2(280, 44)
	hurry_clock = HurryClock.new()
	hurry_clock.position = Vector2(30, 50)
	hurry_clock.size = Vector2(220, 220)
	hurry_root.add_child(hurry_clock)
	hurry_secs = _label("", 84, CREAM, title_font)
	hurry_clock.add_child(hurry_secs)
	hurry_secs.position = Vector2.ZERO
	hurry_secs.size = Vector2(220, 220)
	hurry_value = _label("", 40, GOLD, title_font)
	hurry_root.add_child(hurry_value)
	hurry_value.position = Vector2(0, 282)
	hurry_value.size = Vector2(280, 56)
	hurry_root.visible = false

	overlay_root = Control.new()
	_place(overlay_root, 0, 0, 1280, 720)
	_build_selector()

	music = AudioStreamPlayer.new()
	music.bus = "music"
	add_child(music)
	music.finished.connect(_on_music_finished)
	effects = AudioStreamPlayer.new()
	effects.bus = "effects"
	add_child(effects)
	voice = AudioStreamPlayer.new()
	voice.bus = "voice"
	voice.finished.connect(_voice_done)
	add_child(voice)


func _build_selector() -> void:
	selector = _panel(Color(BURGUNDY, 0.95))
	selector.position = Vector2(140, 110)
	selector.size = Vector2(1000, 500)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	selector.add_child(box)
	box.add_child(_label("PICK A RECORD", 54, GOLD, title_font))
	var grid := GridContainer.new()
	grid.columns = 5
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	box.add_child(grid)
	for i in range(10):
		var cell := _panel(Color(TEAL, 0.9), CREAM)
		cell.custom_minimum_size = Vector2(178, 140)
		var l := _label("", 24)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		cell.add_child(l)
		grid.add_child(cell)
		selector_cells.append(cell)
	selector_timer = _label("", 26, CREAM)
	box.add_child(selector_timer)
	selector.visible = false
	add_child(selector)


# Rendering --------------------------------------------------------------
func _on_player_update(_variable: String, _value: Variant) -> void:
	_render()


func _render() -> void:
	var active: Dictionary = MPF.game.player
	var number := int(active.get("number", 1))
	var big := 120 if song_live or rent_live else 150
	score_label.text = commas(int(active.get("score", 0)))
	var font_size := big
	while font_size > 60 and title_font.get_string_size(score_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > 1200:
		font_size -= 6
	score_label.add_theme_font_size_override("font_size", font_size)
	score_label.size.y = big + 20
	var others := ""
	for i in range(MPF.game.players.size()):
		if i + 1 != number:
			others += "     [color=#a89a86]P%d %s[/color]" % [i + 1, commas(int(MPF.game.players[i].get("score", 0)))]
	sub_line.text = "[center]PLAYER %d  •  BALL %d%s[/center]" % [number, int(active.get("ball", 1)), others]
	sub_line.position.y = big + 26
	lock_pips.set_count(int(active.get("modern_locked_balls", 0)), 3)
	var lit := int(active.get("modern_lock_lit", 0)) == 1
	lock_state.text = "LOCK IS LIT" if lit else "Lock at the top bank"
	lock_state.add_theme_color_override("font_color", GOLD if lit else CREAM)
	lock_chip.visible = not rent_live and bonus_text == ""
	lock_chip.modulate = Color(1, 1, 1, 0.35) if song_live else Color.WHITE  # locks don't advance during a song
	_render_card(active)


func _accent(text: String) -> String:
	## The last word in gold, as on the jukebox signs.
	var cut := text.rfind(" ")
	if cut < 0:
		return "[color=#ffcf5a]%s[/color]" % text
	return "%s [color=#ffcf5a]%s[/color]" % [text.left(cut), text.substr(cut + 1)]


func _render_card(active: Dictionary) -> void:
	var label := "NEXT"
	var title := ""
	var line := ""
	var detail := ""
	var done := 0
	var goal := 0
	var song_mode := task_title_text.begins_with("SONG MODE: ")
	if bonus_text != "":
		label = "END OF BALL"
		title = _accent("BONUS")
		line = bonus_text
	elif rent_live:
		label = "MULTIBALL"
		title = _accent("RENT PARTY")
		line = rent_text
		done = rent_done
		goal = rent_goal
	elif song_live or song_mode:
		label = "UP NEXT"
		title = _accent(task_title_text.trim_prefix("SONG MODE: "))
		detail = task_detail_text.trim_suffix(" Finish before the record ends.")
		if song_live:
			line = mode_status
			done = mode_done
			goal = mode_goal
	elif int(active.get("modern_nickel", 0)) > 0:
		title = "SHOOT A " + _accent("LIT CRATER")
		line = "Nickel ready  •  play the jukebox"
	else:
		var target := str(active.get("modern_nickel_target", ""))
		if target in NAMES:
			title = "SHOOT THE " + _accent(str(NAMES[target]).to_upper())
			line = "Nickel"
			done = int(active.get("modern_nickel_progress", 0))
			goal = int(active.get("modern_nickel_cost", 1))
		else:
			title = "GET A " + _accent("NICKEL")
			line = "Visit the club staff"
	if not song_live:
		card_label.text = label
	card_title.text = "[center]%s[/center]" % title
	card_title.add_theme_font_size_override("normal_font_size", 56 if song_live or rent_live else 66)
	card_pips.set_count(done, goal if goal <= 6 else 0)  # long counts such as 25 dancers stay in the text
	card_line.text = line
	card_line.visible = line != ""
	card_detail.text = detail
	card_detail.visible = detail != ""
	card_bar.visible = song_live
	card.position.y = sub_line.position.y + 56


func _extra_ball_lit() -> bool:
	return int(MPF.game.player.get("modern_extra_ball_lit", 0)) == 1


func _process(delta: float) -> void:
	_spin_process(delta)
	_hurry_process(delta)
	if song_live and song_length_ms > 0:
		if not song_paused:
			song_elapsed_ms += delta * 1000.0
		card_bar.value = 100.0 * (1.0 - min(1.0, song_elapsed_ms / song_length_ms))
		var left := int(ceil(max(0.0, song_length_ms - song_elapsed_ms) / 1000.0))
		card_label.text = "%s  •  %d:%02d LEFT" % [song_artist.to_upper(), left / 60, left % 60]
	var side := hurry_root.visible or spin_root.visible  # Louis Jordan's clock and Big Joe's record sit on the left
	var w := 720.0 if side else 800.0
	card.custom_minimum_size.x = w
	card.size = Vector2(w, 0)
	card.position.x = 320.0 if side else (1280.0 - w) / 2.0
	lock_chip.size = Vector2.ZERO
	lock_chip.position = Vector2((1280.0 - lock_chip.size.x) / 2.0, min(card.position.y + card.size.y + 24.0, 580.0))
	if selector.visible:
		var left: float = max(0.0, selector_deadline - Time.get_ticks_msec() / 1000.0)
		selector_timer.text = "TAP GREEN TO MOVE  •  HOLD GREEN TO PLAY  •  %d" % ceil(left)


# Big Joe Turner's spinner ------------------------------------------------
class SpinRecord extends Control:
	## A 78 on the turntable: grooves, a gold label and a shine line so the spin reads.
	var speed := 0.0  # radians per second; each spin kicks it, then it coasts down

	func _draw() -> void:
		var c := size / 2.0
		var r: float = min(size.x, size.y) / 2.0
		draw_circle(c, r, Color("#111111"))
		for i in range(6):
			draw_arc(c, r * (0.92 - i * 0.08), 0, TAU, 64, Color(0.3, 0.3, 0.3, 0.8), 1.5)
		draw_circle(c, r * 0.36, Color("#ffcf5a"))
		draw_circle(c, r * 0.05, Color("#111111"))
		draw_line(c + Vector2(r * 0.4, 0), c + Vector2(r * 0.95, 0), Color(1, 1, 1, 0.6), 4.0)
		draw_line(c - Vector2(r * 0.4, 0), c - Vector2(r * 0.95, 0), Color(1, 1, 1, 0.25), 3.0)


static func commas(n: int) -> String:
	var s := str(abs(n))
	var out := ""
	while s.length() > 3:
		out = "," + s.right(3) + out
		s = s.left(s.length() - 3)
	return ("-" if n < 0 else "") + s + out


func _show_spin(payload: Dictionary) -> void:
	spin_pot.text = "POT " + commas(int(payload.get("pot", 0)))
	spin_gain.text = "+" + commas(int(payload.get("gain", 0)))
	spin_record.speed = min(spin_record.speed + 14.0, 40.0)
	spin_root.visible = true
	spin_hide_ms = Time.get_ticks_msec() + SPIN_SHOW_MS
	spin_gain.scale = Vector2(1.5, 1.5)
	create_tween().tween_property(spin_gain, "scale", Vector2.ONE, 0.2)


func _spin_process(delta: float) -> void:
	if not spin_root.visible:
		return
	spin_record.rotation += spin_record.speed * delta
	spin_record.speed *= exp(-1.2 * delta)
	if Time.get_ticks_msec() >= spin_hide_ms:
		spin_root.visible = false
		spin_record.speed = 0.0


# Louis Jordan's hurry-up -------------------------------------------------
class HurryClock extends Control:
	## A stopwatch face: the ring empties clockwise and turns green -> gold -> red as the value drains.
	var left := 1.0
	var color := Color("#5ad65a")
	var glow := 0.0

	func _draw() -> void:
		var c := size / 2.0
		var r: float = min(size.x, size.y) / 2.0
		draw_circle(c, r, Color(0.05, 0.03, 0.02, 0.85))
		if glow > 0.0:
			draw_circle(c, r, Color(color.r, color.g, color.b, 0.25 * glow))
		for i in range(20):
			var a := -PI / 2 + TAU * i / 20.0
			var d := Vector2(cos(a), sin(a))
			draw_line(c + d * r * 0.74, c + d * r * 0.82, Color(1, 1, 1, 0.35), 2.0)
		draw_arc(c, r * 0.91, 0, TAU, 96, Color(0.25, 0.2, 0.15, 0.9), 14.0)
		if left > 0.0:
			draw_arc(c, r * 0.91, -PI / 2, -PI / 2 + TAU * left, 96, color, 14.0)
			var tip := -PI / 2 + TAU * left
			draw_circle(c + Vector2(cos(tip), sin(tip)) * r * 0.91, 10.0, Color.WHITE)


func _hurry_color(left: float) -> Color:
	if left > 0.5:
		return HURRY_GREEN.lerp(GOLD, (1.0 - left) * 2.0)
	return GOLD.lerp(HURRY_RED, clamp((0.5 - left) * 4.0, 0.0, 1.0))


func _start_hurry(payload: Dictionary) -> void:
	hurry_total_ms = max(1.0, float(payload.get("ms", 20000)))
	hurry_start = int(payload.get("start", 0))
	hurry_end = int(payload.get("end", 0))
	hurry_elapsed_ms = 0.0
	hurry_target.text = "SHOOT " + str(payload.get("target", "")).to_upper()
	hurry_live = true
	hurry_root.position.x = 30.0
	hurry_root.modulate = Color.WHITE
	hurry_root.scale = Vector2(0.3, 0.3)
	hurry_root.visible = true
	create_tween().tween_property(hurry_root, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _hurry_process(delta: float) -> void:
	if not hurry_live:
		return
	if not song_paused:
		hurry_elapsed_ms = min(hurry_total_ms, hurry_elapsed_ms + delta * 1000.0)
	var remaining := hurry_total_ms - hurry_elapsed_ms
	var left := remaining / hurry_total_ms
	var color := _hurry_color(left)
	hurry_clock.left = left
	hurry_clock.color = color
	hurry_secs.text = "%d" % ceil(remaining / 1000.0)
	hurry_value.text = commas(int(max(hurry_end, hurry_start - (hurry_start - hurry_end) * (1.0 - left))))
	hurry_value.add_theme_color_override("font_color", color.lerp(GOLD, 0.4))
	var t := Time.get_ticks_msec() / 1000.0
	var warn := CREAM
	if remaining < HURRY_PANIC_MS:  # the last five seconds: the clock throbs faster and the numbers flash red
		var rate := lerpf(6.0, 16.0, 1.0 - remaining / HURRY_PANIC_MS)
		var beat := 0.5 + 0.5 * sin(t * rate)
		hurry_root.scale = Vector2.ONE * (1.0 + 0.06 * beat)
		hurry_clock.glow = beat
		warn = HURRY_RED if beat > 0.5 else CREAM
	elif hurry_elapsed_ms > 400.0:  # after the pop-in tween
		hurry_root.scale = Vector2.ONE
		hurry_clock.glow = 0.0
	hurry_secs.add_theme_color_override("font_color", warn)
	hurry_target.add_theme_color_override("font_color", warn)
	hurry_clock.queue_redraw()


func _end_hurry(payload: Dictionary) -> void:
	if not hurry_root.visible:
		return
	hurry_live = false
	hurry_clock.glow = 0.0
	hurry_clock.queue_redraw()
	var tw := create_tween()
	if payload.get("collected", false):
		hurry_target.text = "COLLECTED!"
		hurry_target.add_theme_color_override("font_color", GOLD)
		hurry_value.text = commas(int(payload.get("value", 0)))
		hurry_value.add_theme_color_override("font_color", GOLD)
		tw.tween_property(hurry_root, "scale", Vector2(1.3, 1.3), 0.25).set_trans(Tween.TRANS_BACK)
		tw.tween_interval(0.9)
	else:
		hurry_target.text = "TOO LATE!"
		hurry_target.add_theme_color_override("font_color", HURRY_RED)
		hurry_secs.text = "0"
		hurry_value.text = commas(hurry_end)
		hurry_clock.left = 0.0
		for dx in [-14.0, 12.0, -9.0, 6.0, 0.0]:
			tw.tween_property(hurry_root, "position:x", 30.0 + dx, 0.05)
		tw.tween_interval(0.8)
	tw.tween_property(hurry_root, "modulate:a", 0.0, 0.4)
	tw.tween_callback(func(): hurry_root.visible = false)


# Overlays ---------------------------------------------------------------
func flash_screen(color: Color = GOLD, pulses: int = 3) -> void:
	## Jackpot celebration: the whole screen pulses in colour behind the overlay card.
	var flash := ColorRect.new()
	flash.color = color
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_place(flash, 0, 0, 1280, 720)
	move_child(flash, overlay_root.get_index())
	flash.modulate.a = 0.0
	var tw := create_tween()
	for i in pulses:
		tw.tween_property(flash, "modulate:a", 0.55, 0.08)
		tw.tween_property(flash, "modulate:a", 0.0, 0.22)
	tw.tween_callback(flash.queue_free)


func show_overlay(title: String, subtitle: String = "", ms: int = 2000, color: Color = BURGUNDY,
		still_true: Callable = Callable()) -> void:
	## still_true is checked when a queued card reaches the screen; the card is dropped if it no longer holds.
	overlay_queue.append([title, subtitle, ms, color, still_true if overlay_busy else Callable()])
	if not overlay_busy:
		_next_overlay()


func _next_overlay() -> void:
	if overlay_queue.is_empty():
		overlay_busy = false
		return
	overlay_busy = true
	var item: Array = overlay_queue.pop_front()
	if item[4].is_valid() and not item[4].call():
		_next_overlay()
		return
	var card := _panel(Color(item[3], 0.92))
	var box := VBoxContainer.new()
	card.add_child(box)
	var t := _label(item[0], 64, GOLD, title_font)
	t.autowrap_mode = TextServer.AUTOWRAP_WORD
	t.custom_minimum_size = Vector2(760, 0)
	box.add_child(t)
	if item[1]:
		var s := _label(item[1], 30, CREAM)
		s.autowrap_mode = TextServer.AUTOWRAP_WORD
		s.custom_minimum_size = Vector2(760, 0)
		box.add_child(s)
	card.size = Vector2(820, 0)
	overlay_root.add_child(card)
	card.position = Vector2(230, 230)
	card.pivot_offset = Vector2(410, 100)
	card.scale = Vector2(0.6, 0.6)
	card.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(card, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)
	tw.parallel().tween_property(card, "modulate:a", 1.0, 0.18)
	tw.tween_interval(item[2] / 1000.0)
	tw.tween_property(card, "modulate:a", 0.0, 0.2)
	tw.tween_callback(func():
		card.queue_free()
		_next_overlay())


func _show_selector(payload: Dictionary) -> void:
	var names: PackedStringArray = str(payload.get("names", "")).split("|")
	var played := int(payload.get("played", 0))
	for i in range(selector_cells.size()):
		var l: Label = selector_cells[i].get_child(0)
		l.text = "%d\n%s" % [i + 1, names[i] if i < names.size() else ""]
		selector_cells[i].modulate = Color(0.4, 0.4, 0.4) if played & (1 << i) else Color.WHITE
	selector_deadline = Time.get_ticks_msec() / 1000.0 + float(payload.get("timeout_ms", 10000)) / 1000.0
	_highlight(int(payload.get("highlight", 0)))
	selector.visible = true
	selector.scale = Vector2(0.8, 0.8)
	selector.pivot_offset = selector.size / 2
	create_tween().tween_property(selector, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK)


func _highlight(index: int) -> void:
	for i in range(selector_cells.size()):
		var box: StyleBoxFlat = selector_cells[i].get_theme_stylebox("panel").duplicate()
		box.border_color = GOLD if i == index else CREAM
		box.set_border_width_all(8 if i == index else 2)
		box.bg_color = Color(GOLD, 0.35) if i == index else Color(TEAL, 0.9)
		selector_cells[i].add_theme_stylebox_override("panel", box)


# Audio ------------------------------------------------------------------
func _load_audio(path: String) -> AudioStream:
	if ResourceLoader.exists(path):
		return load(path)
	var file := ProjectSettings.globalize_path(path)
	if FileAccess.file_exists(file):
		return AudioStreamMP3.load_from_file(file)
	return null


func _fade_out_music(seconds: float = 1.0, then: Callable = Callable()) -> void:
	_stop_music_fade()
	if not music.playing or music.stream_paused:
		music.stop()
		if then.is_valid():
			then.call()
		return
	music_fade = create_tween()
	music_fade.tween_property(music, "volume_db", -60.0, seconds)
	music_fade.tween_callback(music.stop)
	if then.is_valid():
		music_fade.tween_callback(then)


func _stop_music_fade() -> void:
	if music_fade:
		music_fade.kill()
		music_fade = null


func _play_house_band() -> void:
	## A fresh random pick of ten house-band tracks each time base music starts (new ball, after a song, or when one ends).
	_stop_music_fade()
	var stream := house_band.next_stream()
	playing_house_band = stream != null
	if stream:
		music.stream = stream
		music.volume_db = -8.0
		music.play()


func _on_music_finished() -> void:
	if playing_house_band:
		_play_house_band()


func _play_artist_pick() -> void:
	if artist_pick_song == null:
		artist_pick_song = _load_audio("res://sounds/modern_music/artist_pick.mp3")
	if artist_pick_song is AudioStreamMP3:
		artist_pick_song.loop = true
	playing_house_band = false
	_stop_music_fade()
	music.stop()
	if artist_pick_song:
		music.stream = artist_pick_song
		music.volume_db = 0.0
		music.play()


func _play_rent_party_build_up() -> void:
	_fade_out_music(0.5)
	var stream := _load_audio("res://sounds/modern_sfx/rent_party_build_up.mp3")
	if stream:
		effects.stream = stream
		effects.volume_db = 0.0
		effects.play()


func _play_rent_party() -> void:
	## Loops for as long as the multiball is alive.
	effects.stop()
	if rent_party_song == null:
		rent_party_song = _load_audio("res://sounds/modern_music/rent_party.mp3")
		if rent_party_song is AudioStreamMP3:
			rent_party_song.loop = true
	_stop_music_fade()
	music.stop()
	playing_house_band = false
	if rent_party_song:
		music.stream = rent_party_song
		music.volume_db = 0.0
		music.play()


func _play_between_balls() -> void:
	playing_house_band = false
	if between_balls_song == null:
		between_balls_song = _load_audio("res://sounds/modern_music/between_balls.mp3")
	if between_balls_song is AudioStreamMP3:
		between_balls_song.loop = true
	_stop_music_fade()
	music.stop()
	if between_balls_song:
		music.stream = between_balls_song
		music.volume_db = -6.0
		music.play()


static func artist_clip_paths(song_path: String) -> PackedStringArray:
	## res://videos/modern/jukebox/<folder>/clip_01.ogv, clip_02.ogv ...: short sections of the artist's footage.
	var folder := song_path.get_base_dir().get_file()
	var paths := PackedStringArray()
	for i in range(1, 100):
		var path := "res://videos/modern/jukebox/%s/clip_%02d.ogv" % [folder, i]
		if not ResourceLoader.exists(path):
			break
		paths.append(path)
	return paths


static func artist_video_paths(song_path: String) -> PackedStringArray:
	## res://sounds/music/jukebox/<folder>/song_<n>.mp3 -> song video, artist video. Only the artist's own footage plays.
	var folder := song_path.get_base_dir().get_file()
	var base := "res://videos/modern/jukebox/"
	var name := song_path.get_file().get_basename().replace("song_", "video_")
	return PackedStringArray([base + folder + "/" + name + ".ogv", base + folder + "/video.ogv"])


func _new_artist_video(below: Control) -> void:
	## A fresh player per song: reusing one VideoStreamPlayer for a new Theora stream can hang Godot.
	artist_video = VideoStreamPlayer.new()
	artist_video.expand = true
	artist_video.loop = true
	artist_video.volume_db = -80.0
	artist_video.modulate = Color(0.55, 0.55, 0.55)
	artist_video.visible = false
	_place(artist_video, 0, 0, 1280, 720)
	move_child(artist_video, below.get_index() + 1)


func _play_artist_video(song_path: String) -> void:
	_stop_artist_video()
	var paths := artist_video_paths(song_path)
	if ResourceLoader.exists(paths[0]):
		_start_artist_video(load(paths[0]) as VideoStream, true)
		return
	# Godot's Theora player can't seek, so a random start is a random section, then another, for the whole song.
	artist_clips = artist_clip_paths(song_path)
	if not artist_clips.is_empty():
		artist_clip_last = -1
		_next_artist_clip()
		return
	for path in paths.slice(1):
		if ResourceLoader.exists(path):
			_start_artist_video(load(path) as VideoStream, true)
			return


func _next_artist_clip() -> void:
	if artist_clips.is_empty():
		return
	var choices: Array = range(artist_clips.size()).filter(func(i): return i != artist_clip_last)
	if choices.is_empty():
		choices = [0]
	artist_clip_last = choices.pick_random()
	if artist_video.stream != null:
		_replace_artist_video()
	_start_artist_video(load(artist_clips[artist_clip_last]) as VideoStream, false)


func _start_artist_video(stream: VideoStream, loop: bool) -> void:
	if stream == null:
		return
	artist_video.stream = stream
	artist_video.loop = loop
	if not loop:
		artist_video.finished.connect(_next_artist_clip)
	artist_video.visible = true
	artist_video.play()
	artist_video.paused = song_paused


func _stop_artist_video() -> void:
	artist_clips = PackedStringArray()
	_replace_artist_video()


func _replace_artist_video() -> void:
	## Each stream gets a fresh player: reusing one VideoStreamPlayer for a new Theora stream can hang Godot.
	if artist_video.stream == null:
		return
	var old := artist_video
	_new_artist_video(old)
	old.stop()
	old.stream = null
	old.queue_free()


func _play_song(path: String) -> void:
	_stop_music_fade()
	playing_house_band = false
	var stream := _load_audio(path)
	if stream:
		if stream is AudioStreamMP3:
			stream.loop = false
		music.stream = stream
		music.volume_db = 0.0
		music.play()


func _say(path: String) -> void:
	var stream := _load_audio(path)
	if stream == null:
		return
	if stream is AudioStreamMP3:
		stream.loop = false
	voice.stream = stream
	voice.play()
	voice_started_ms = Time.get_ticks_msec()
	_set_duck(true)


func _voice_done() -> void:
	if voice_queue.is_empty():
		_set_duck(false)
		return
	var next: Array = voice_queue.pop_front()
	caption.text = next[0]
	_say(next[1])


func _set_duck(on: bool) -> void:
	var bus := AudioServer.get_bus_index("music")
	if bus >= 0:
		AudioServer.set_bus_volume_db(bus, DUCK_DB if on else 0.0)


# Events -----------------------------------------------------------------
func _on_event(payload: Dictionary = {}) -> void:
	var e: String = payload.get("name", "")
	match e:
		"modern_splash_show":
			show_overlay("WELCOME TO THE JUKE JOINT",
				"Hit the club staff to earn a NICKEL. Shoot a lit crater to play the JUKEBOX. " +
				"Every song is a mode. Complete the top drop bank to light a lock for RENT PARTY multiball.\nPress START to skip.", 5800, TEAL)
		"modern_nickel_directed":
			caption.text = "Shoot the %s  (%d / %d)" % [payload.get("location_name", ""), int(payload.get("progress", 0)), int(payload.get("cost", 1))]
		"modern_nickel_refused":
			caption.text = "Not here! Try %s" % payload.get("target", "")
		"modern_nickel_awarded":
			show_overlay("NICKEL!", "+%s  •  Shoot a lit crater" % MPF.util.comma_sep(int(payload.get("points", 0))), 1500)
			caption.text = "Shoot a lit crater to play the jukebox"
		"modern_floor_nickel":
			show_overlay("NICKEL ON THE FLOOR!", "", 1200)
		"modern_jukebox_no_nickel":
			caption.text = "The jukebox needs a nickel"
		"modern_selector_opened":
			caption.text = ""  # the nickel hunt's direction no longer applies
			_show_selector(payload)
			_play_artist_pick()
		"modern_selector_highlight":
			selector_deadline = Time.get_ticks_msec() / 1000.0 + float(payload.get("timeout_ms", 10000)) / 1000.0
			_highlight(int(payload.get("highlight", 0)))
		"modern_artist_chosen":
			_highlight(int(payload.get("slot", 1)) - 1)
			_fade_out_music(0.25)
			var tw := create_tween()
			tw.tween_interval(0.6)
			tw.tween_callback(func(): selector.visible = false)
		"modern_selector_closed":
			selector.visible = false
			if music.stream == artist_pick_song:
				music.stop()
		"modern_song_started":
			selector.visible = false
			song_artist = str(payload.get("artist", ""))
			song_length_ms = float(payload.get("length_ms", 60000))
			song_elapsed_ms = 0.0
			song_paused = false
			song_live = true
			show_overlay("NOW PLAYING", "%s — %s" % [payload.get("title", ""), song_artist], 1800, TEAL)
			_play_song(str(payload.get("path", "")))
			_play_artist_video(str(payload.get("path", "")))
		"modern_song_ended":
			_stop_artist_video()
			if hurry_live:  # a drain or tilt ended the song mid hurry-up; a collect or miss fades out on its own
				hurry_live = false
				hurry_root.visible = false
			song_live = false
			mode_status = ""
			mode_goal = 0
			if not between_balls:
				_fade_out_music(SONG_FADE_S, func():
					if not between_balls:
						_play_house_band())
		"modern_song_paused":
			song_paused = true
			music.stream_paused = true
			artist_video.paused = true
		"modern_song_resumed":
			song_paused = false
			music.stream_paused = false
			artist_video.paused = false
		"modern_voice":
			var line := "%s: \"%s\"" % [payload.get("speaker", ""), payload.get("text", "")]
			var just_started := Time.get_ticks_msec() - voice_started_ms < VOICE_CUT_MS
			if voice.playing and (payload.get("queue", false) or just_started):
				voice_queue.append([line, str(payload.get("file", ""))])
			else:
				voice_queue.clear()
				caption.text = line
				_say(str(payload.get("file", "")))
		"modern_select_progress":
			var p := float(payload.get("progress", 0))
			select_ring.visible = p > 0.0 and p < 1.0
			select_ring.value = p
		"modern_drop_the_needle":
			show_overlay("DROP THE NEEDLE!", "+50,000  •  Ovation up", 1800)
		"modern_ball_saver_ready":
			show_overlay("BALL SAVER LIT!", "The Bouncer has your back", 2000, TEAL)
		"modern_ball_saved":
			show_overlay("THE BOUNCER SAVED YOU!", "", 1500, TEAL)
		"modern_extra_ball_lit":
			show_overlay("EXTRA BALL IS LIT", "Shoot the Kitchen", 1500, TEAL, _extra_ball_lit)
		"modern_pot_spin":
			_show_spin(payload)
		"modern_hurry_up_started":
			_start_hurry(payload)
		"modern_hurry_up_ended":
			_end_hurry(payload)
		"modern_ball_locked":
			flash_screen(GOLD, 2)
		"modern_award_extra_ball":
			flash_screen(GOLD, 4)
			show_overlay("EXTRA BALL!", "You earned another ball  •  Shoot again", 3000, BRASS)
		"modern_special_lit":
			show_overlay("SPECIAL IS LIT", "Shoot the Bar", 1500, TEAL)
		"modern_special_awarded":
			show_overlay("SPECIAL!", "Free game  •  +%s" % MPF.util.comma_sep(int(payload.get("points", 0))), 3000)
		"modern_bonus_line":
			bonus_lines.append("%s  %d × %s" % [payload.get("label", ""), int(payload.get("count", 0)), MPF.util.comma_sep(int(payload.get("value", 0)))])
			bonus_text = bonus_lines[-1]
		"modern_bonus_total":
			show_overlay("STANDING OVATION ×%d" % int(payload.get("ovation", 1)),
				"Bonus %s" % MPF.util.comma_sep(int(payload.get("points", 0))), 1600, TEAL)
			bonus_lines.clear()
		"modern_bonus_void":
			show_overlay("NO BONUS", "Tilted", 1500)
		"tilt_warning":
			show_overlay("EASY NOW!", "One more and you're out", 1500)
		"tilt":
			show_overlay("TILT", "The bouncer shows you the door", 3000)
		"ball_will_end":
			between_balls = true
			effects.stop()
			_stop_artist_video()
			song_live = false
			_play_between_balls()
		"ball_started":
			bonus_text = ""
			rent_live = false
			bonus_lines.clear()
			if between_balls:
				between_balls = false
				_play_house_band()
		"modern_overlay":
			show_overlay(str(payload.get("title", "")), str(payload.get("subtitle", "")), int(payload.get("ms", 1800)),
				OVERLAY_STYLES.get(str(payload.get("style", "")), BURGUNDY))
		"modern_rent_party_build_up":
			_play_rent_party_build_up()
		"modern_rent_party_started":
			if not between_balls:
				_play_rent_party()
			rent_live = true
			rent_text = "Lit craters pay %s" % commas(int(payload.get("jackpot", 0)))
			rent_done = 0
			rent_goal = 3
		"modern_song_shot":
			flash_screen(GOLD)
		"modern_jackpot":
			flash_screen(GOLD, 2)
			rent_text = "Next jackpot %s" % commas(int(payload.get("next_value", 0)))
			rent_done = int(payload.get("count", 0))
		"modern_super_jackpot_lit":
			rent_text = "SUPER JACKPOT AT THE BAR!"
			rent_goal = 0
		"modern_super_jackpot":
			rent_text = "SUPER JACKPOT COLLECTED!"
		"modern_rent_party_ended":
			rent_live = false
			if not between_balls and music.stream == rent_party_song:
				_fade_out_music(1.0, func():
					if not between_balls:
						_play_house_band())
		"modern_task":
			task_title_text = str(payload.get("title", ""))
			task_detail_text = str(payload.get("detail", ""))
		"modern_mode_status":
			mode_status = str(payload.get("text", ""))
			mode_done = int(payload.get("done", 0))
			mode_goal = int(payload.get("goal", 0))
		"game_ending":
			show_overlay("LAST CALL", "Thanks for coming to the juke joint", 3000)
	_render()
