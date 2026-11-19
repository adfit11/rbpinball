extends MPFSlide
## Modern juke joint HUD. Builds its widgets in code, keeps the score strip visible
## under every overlay, and owns the jukebox music and voice callout playback.

const GOLD := Color("#ffcf5a")
const CREAM := Color("#f6e7c8")
const BURGUNDY := Color("#5a1020")
const TEAL := Color("#0f4a4a")
const DIM := Color("#8a7f70")
const DUCK_DB := -12.0
const LOCATIONS := ["Bar", "Kitchen", "Bandstand", "Coat Check", "Back Door"]

var title_font: Font = load("res://fonts/modern/Limelight-Regular.ttf")
var neon_font: Font = load("res://fonts/modern/Monoton-Regular.ttf")
var body_font: Font = load("res://fonts/modern/Oswald-Variable.ttf")

var scores: HBoxContainer
var ball_label: Label
var side_labels := {}
var record_row: HBoxContainer
var song_panel: PanelContainer
var song_title: Label
var song_bar: ProgressBar
var mode_banner: Label
var caption: Label
var overlay_root: Control
var selector: Control
var selector_cells: Array = []
var selector_timer: Label
var select_ring: ProgressBar
var music: AudioStreamPlayer
var voice: AudioStreamPlayer
var house_band: AudioStream
var song_length_ms := 0.0
var song_elapsed_ms := 0.0
var song_paused := false
var selector_deadline := 0.0
var overlay_queue: Array = []
var overlay_busy := false
var bonus_lines: Array = []

const EVENTS := [
	"modern_splash_show", "modern_splash_hide", "modern_nickel_directed", "modern_nickel_refused",
	"modern_nickel_awarded", "modern_jukebox_no_nickel", "modern_selector_opened",
	"modern_selector_highlight", "modern_artist_chosen", "modern_selector_closed", "modern_song_started",
	"modern_song_ended", "modern_song_paused", "modern_song_resumed", "modern_voice",
	"modern_select_progress", "modern_drop_the_needle", "modern_ball_saver_ready", "modern_ball_saved",
	"modern_extra_ball_lit", "modern_award_extra_ball", "modern_special_lit", "modern_special_awarded",
	"modern_bonus_line", "modern_bonus_total", "modern_bonus_void", "tilt_warning", "tilt",
	"modern_overlay", "modern_mode_status", "modern_floor_nickel", "game_ending", "ball_started",
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

	scores = HBoxContainer.new()
	scores.add_theme_constant_override("separation", 12)
	scores.alignment = BoxContainer.ALIGNMENT_CENTER
	_place(scores, 20, 10, 1240, 70)
	for player in MPF.game.players:
		var p := _panel(Color(BURGUNDY, 0.85))
		p.custom_minimum_size = Vector2(290, 64)
		p.add_child(_label("", 34))
		scores.add_child(p)
	ball_label = _place(_label("", 24, GOLD), 540, 82, 200, 30)

	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 6)
	var side_panel := _panel(Color(TEAL, 0.85))
	side_panel.add_child(side)
	_place(side_panel, 1040, 130, 220, 400)
	for key in ["multiplier", "nickel", "target", "locks", "guests", "ovation", "saver"]:
		var l := _label("", 22)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.custom_minimum_size = Vector2(190, 0)
		side.add_child(l)
		side_labels[key] = l

	song_panel = _panel(Color(0, 0, 0, 0.6))
	var song_box := VBoxContainer.new()
	song_panel.add_child(song_box)
	song_title = _label("", 26, GOLD, title_font)
	song_box.add_child(song_title)
	song_bar = ProgressBar.new()
	song_bar.show_percentage = false
	song_bar.custom_minimum_size = Vector2(560, 14)
	song_box.add_child(song_bar)
	_place(song_panel, 330, 120, 620, 80)
	song_panel.visible = false

	mode_banner = _place(_label("", 26, CREAM), 200, 540, 840, 40)
	mode_banner.autowrap_mode = TextServer.AUTOWRAP_WORD
	caption = _place(_label("", 22, CREAM), 140, 585, 1000, 34)

	record_row = HBoxContainer.new()
	record_row.alignment = BoxContainer.ALIGNMENT_CENTER
	record_row.add_theme_constant_override("separation", 14)
	_place(record_row, 200, 632, 880, 70)
	for i in range(10):
		var rec := ColorRect.new()
		rec.custom_minimum_size = Vector2(60, 60)
		record_row.add_child(rec)

	select_ring = ProgressBar.new()
	select_ring.show_percentage = false
	select_ring.max_value = 1.0
	_place(select_ring, 1040, 540, 220, 14)
	select_ring.visible = false

	overlay_root = Control.new()
	_place(overlay_root, 0, 0, 1280, 720)
	_build_selector()

	music = AudioStreamPlayer.new()
	music.bus = "music"
	add_child(music)
	voice = AudioStreamPlayer.new()
	voice.bus = "voice"
	voice.finished.connect(func(): _set_duck(false))
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
	for i in range(scores.get_child_count()):
		var player: Dictionary = MPF.game.players[i] if i < MPF.game.players.size() else {}
		var p: PanelContainer = scores.get_child(i)
		var l: Label = p.get_child(0)
		l.text = "P%d  %s" % [i + 1, MPF.util.comma_sep(int(player.get("score", 0)))]
		l.add_theme_color_override("font_color", GOLD if i + 1 == number else CREAM)
	ball_label.text = "BALL %d" % int(active.get("ball", 1))
	side_labels.multiplier.text = "SONG ×%d" % int(active.get("modern_song_multiplier", 1))
	var held := int(active.get("modern_nickel", 0)) > 0
	side_labels.nickel.text = "NICKEL: HELD" if held else "NICKEL: %d / %d" % [
		int(active.get("modern_nickel_progress", 0)), int(active.get("modern_nickel_cost", 1))]
	side_labels.target.text = "Shoot a lit crater!" if held else _target_name(str(active.get("modern_nickel_target", "")))
	side_labels.locks.text = "LOCKS %d / 3" % int(active.get("modern_locked_balls", 0))
	var guests := int(active.get("modern_guests", 0))
	side_labels.guests.text = "GUEST LIST " + "●".repeat(guests) + "○".repeat(max(0, 5 - guests))
	if int(active.get("modern_lock_lit", 0)):
		side_labels.guests.text = "LOCK IS LIT"
	side_labels.ovation.text = "OVATION ×%d" % min(4, 1 + int(active.get("modern_ovation", 0)) + int(active.get("modern_songs_completed_ball", 0)))
	side_labels.saver.text = "BOUNCER READY" if int(active.get("modern_ball_saver_ready", 0)) else ""
	var lit := int(active.get("modern_round_songs", 0))
	for i in range(record_row.get_child_count()):
		var rec: ColorRect = record_row.get_child(i)
		rec.color = GOLD if i < lit else Color(0.08, 0.05, 0.05, 0.9)


func _target_name(key: String) -> String:
	var names := {"bar": "Bar", "kitchen": "Kitchen", "bandstand": "Bandstand", "coat_check": "Coat Check", "back_door": "Back Door"}
	return ("Go to the %s" % names[key]) if key in names else ""


func _process(delta: float) -> void:
	if song_panel.visible and not song_paused and song_length_ms > 0:
		song_elapsed_ms += delta * 1000.0
		song_bar.value = 100.0 * song_elapsed_ms / song_length_ms
	if selector.visible:
		var left: float = max(0.0, selector_deadline - Time.get_ticks_msec() / 1000.0)
		selector_timer.text = "TAP GREEN TO MOVE  •  HOLD GREEN TO PLAY  •  %d" % ceil(left)


# Overlays ---------------------------------------------------------------
func show_overlay(title: String, subtitle: String = "", ms: int = 2000, color: Color = BURGUNDY) -> void:
	overlay_queue.append([title, subtitle, ms, color])
	if not overlay_busy:
		_next_overlay()


func _next_overlay() -> void:
	if overlay_queue.is_empty():
		overlay_busy = false
		return
	overlay_busy = true
	var item: Array = overlay_queue.pop_front()
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


func _play_house_band() -> void:
	if house_band == null:
		house_band = _load_audio("res://sounds/modern_music/house_band.mp3")
	if house_band:
		if house_band is AudioStreamMP3:
			house_band.loop = true
		music.stream = house_band
		music.volume_db = -8.0
		music.play()


func _play_song(path: String) -> void:
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
	_set_duck(true)


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
				"Every song is a mode. Fill the guest list to lock balls for RENT PARTY multiball.\nPress START to skip.", 5800, TEAL)
		"modern_nickel_directed":
			caption.text = "Shoot the %s  (%d / %d)" % [payload.get("name", ""), int(payload.get("progress", 0)), int(payload.get("cost", 1))]
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
			_show_selector(payload)
		"modern_selector_highlight":
			_highlight(int(payload.get("highlight", 0)))
		"modern_artist_chosen":
			_highlight(int(payload.get("slot", 1)) - 1)
			var tw := create_tween()
			tw.tween_interval(0.6)
			tw.tween_callback(func(): selector.visible = false)
		"modern_selector_closed":
			selector.visible = false
		"modern_song_started":
			selector.visible = false
			song_title.text = "%s — %s" % [payload.get("title", ""), payload.get("artist", "")]
			song_length_ms = float(payload.get("length_ms", 60000))
			song_elapsed_ms = 0.0
			song_paused = false
			song_panel.visible = true
			show_overlay("NOW PLAYING", song_title.text, 1800, TEAL)
			_play_song(str(payload.get("path", "")))
		"modern_song_ended":
			song_panel.visible = false
			mode_banner.text = ""
			_play_house_band()
		"modern_song_paused":
			song_paused = true
			music.stream_paused = true
		"modern_song_resumed":
			song_paused = false
			music.stream_paused = false
		"modern_voice":
			caption.text = "%s: \"%s\"" % [payload.get("speaker", ""), payload.get("text", "")]
			_say(str(payload.get("file", "")))
		"modern_select_progress":
			var p := float(payload.get("progress", 0))
			select_ring.visible = p > 0.0 and p < 1.0
			select_ring.value = p
		"modern_drop_the_needle":
			show_overlay("DROP THE NEEDLE!", "+50,000  •  Bouncer ready  •  Ovation up", 1800)
		"modern_ball_saved":
			show_overlay("THE BOUNCER SAVED YOU!", "", 1500, TEAL)
		"modern_extra_ball_lit":
			show_overlay("EXTRA BALL IS LIT", "Shoot the Kitchen", 1500, TEAL)
		"modern_award_extra_ball":
			show_overlay("EXTRA BALL!", "Shoot again", 2000)
		"modern_special_lit":
			show_overlay("SPECIAL IS LIT", "Shoot the Bar", 1500, TEAL)
		"modern_special_awarded":
			show_overlay("SPECIAL!", "Free game  •  +%s" % MPF.util.comma_sep(int(payload.get("points", 0))), 3000)
		"modern_bonus_line":
			bonus_lines.append("%s  %d × %s" % [payload.get("label", ""), int(payload.get("count", 0)), MPF.util.comma_sep(int(payload.get("value", 0)))])
			mode_banner.text = "BONUS   " + "   ".join(bonus_lines)
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
		"ball_started":
			mode_banner.text = ""
			bonus_lines.clear()
		"modern_overlay":
			show_overlay(str(payload.get("title", "")), str(payload.get("subtitle", "")), int(payload.get("ms", 1800)),
				TEAL if payload.get("style", "") == "teal" else BURGUNDY)
		"modern_mode_status":
			mode_banner.text = str(payload.get("text", ""))
		"game_ending":
			show_overlay("LAST CALL", "Thanks for coming to the juke joint", 3000)
	_render()
