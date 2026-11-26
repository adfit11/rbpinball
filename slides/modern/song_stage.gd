extends Control
## The artist-mode screen: the handbill frame, the mode's device (left) and instructions (right), the artist
## video in the 16:9 window, and the players along the bottom. The window shows the mode's instructions
## until the ball returns to play, then the video.

const GOLD := Color("#ffcf5a")
const CREAM := Color("#f6e7c8")
const OX := Color("#5a1020")
const TEAL := Color("#0f4a4a")
const WINDOW := Rect2(345, 200, 590, 332)
const LEFT := Rect2(36, 207, 277, 317)
const RIGHT := Rect2(968, 207, 277, 317)
const BOXES := [Vector2(23, 321), Vector2(333, 633), Vector2(647, 948), Vector2(958, 1258)]  # score slots, x from..to
const DEVICES := ["hurry_up", "ladder", "build_and_collect", "roving_shot", "jukebox_jackpot",
	"party_time", "order_up", "request_night", "dance_floor", "hit_me"]
const RUNGS := [0.828, 0.655, 0.479, 0.300]  # ladder rungs, bottom to top, as a share of the panel height
const COUNTS := {2: "RUNG", 4: "HITS", 5: "JACKPOTS", 8: "REQUESTS", 10: "HITS"}

var rye: Font = load("res://fonts/modern/Rye-Regular.ttf")
var oswald: Font = load("res://fonts/modern/Oswald-Variable.ttf")
var slot := 0
var video_slot: Control  # the HUD puts the artist video here, under the frame
var intro: Control
var intro_artist: Label
var intro_song: Label
var intro_title: Label
var intro_goal: Label
var intro_how: Label
var intro_count: Label
var intro_left_ms := 0.0
var device: TextureRect
var tags: Control  # the device's live values
var rung_tags: Array = []
var meter: ProgressBar
var count_tag: PanelContainer
var big_tag: PanelContainer  # the hurry-up seconds on the stopwatch, or Party Time's 2X
var side_artist: Label
var side_song: Label
var side_title: Label
var side_goal: Label
var side_status: Label
var clock: Label
var slot_labels: Array = []
var slot_values: Array = []
var slot_rings: Array = []
var ball_label: Label
var caption: Label


func label(text: String, size: int, color: Color, font: Font = null, wrap := false) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font if font else oswald)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
	return l


func box(bg: Color, border: Color, width := 3) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(width)
	return s


func put(parent: Control, node: Control, r: Rect2) -> Control:
	node.position = r.position
	node.size = r.size
	parent.add_child(node)
	return node


func tag(parent: Control, size: int) -> PanelContainer:
	## A teal ticket with amber type, as on the score strips.
	var p := PanelContainer.new()
	var s := box(TEAL, OX, 2)
	s.content_margin_left = 8
	s.content_margin_right = 8
	p.add_theme_stylebox_override("panel", s)
	p.add_child(label("", size, GOLD, rye))
	parent.add_child(p)
	p.visible = false
	return p


func set_tag(p: PanelContainer, text: String, centre: Vector2, done := false) -> void:
	var l: Label = p.get_child(0)
	l.text = text
	l.add_theme_color_override("font_color", CREAM if done else GOLD)
	(p.get_theme_stylebox("panel") as StyleBoxFlat).bg_color = OX if done else TEAL
	p.reset_size()
	p.position = centre - p.get_combined_minimum_size() / 2.0
	p.visible = text != ""


func _init() -> void:
	size = Vector2(1280, 720)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	video_slot = put(self, ColorRect.new(), WINDOW)
	(video_slot as ColorRect).color = Color.BLACK
	video_slot.clip_contents = true
	_build_intro()
	var frame := put(self, TextureRect.new(), Rect2(0, 0, 1280, 720)) as TextureRect
	frame.texture = load("res://images/modern/stage/frame.png")
	frame.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	device = put(self, TextureRect.new(), LEFT)
	device.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	device.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	tags = put(self, Control.new(), LEFT)
	for i in 4:
		rung_tags.append(tag(tags, 15))
	count_tag = tag(tags, 19)
	big_tag = tag(tags, 38)
	meter = put(tags, ProgressBar.new(), Rect2(16, LEFT.size.y - 26, LEFT.size.x - 32, 16)) as ProgressBar
	meter.show_percentage = false
	meter.add_theme_stylebox_override("background", box(TEAL, OX, 2))
	meter.add_theme_stylebox_override("fill", box(GOLD, OX, 2))
	_build_side()
	for i in 4:
		var x: Vector2 = BOXES[i]
		slot_labels.append(put(self, label("", 18, OX, rye), Rect2(x.x + 8, 553, x.y - x.x - 16, 29)))
		slot_values.append(put(self, label("", 34, CREAM, rye), Rect2(x.x + 8, 586, x.y - x.x - 17, 70)))
		var ring := put(self, Panel.new(), Rect2(x.x + 7, 586, x.y - x.x - 16, 70)) as Panel
		ring.add_theme_stylebox_override("panel", box(Color(0, 0, 0, 0), GOLD, 4))
		slot_rings.append(ring)
	var ticket := put(self, Panel.new(), Rect2(570, 671, 140, 30)) as Panel
	ticket.add_theme_stylebox_override("panel", box(CREAM, OX, 2))
	ball_label = put(self, label("", 21, OX, rye), Rect2(570, 671, 140, 30))
	caption = put(self, label("", 19, CREAM), Rect2(WINDOW.position.x + 10, WINDOW.end.y - 40, WINDOW.size.x - 20, 34))
	caption.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	caption.add_theme_constant_override("shadow_offset_x", 2)
	caption.add_theme_constant_override("shadow_offset_y", 2)
	caption.autowrap_mode = TextServer.AUTOWRAP_WORD
	visible = false


func _build_intro() -> void:
	## A handbill for the mode, filling the video window while the record crackles and the ball is held.
	intro = put(self, Panel.new(), WINDOW)
	var s := box(CREAM, OX, 5)
	intro.add_theme_stylebox_override("panel", s)
	var w := WINDOW.size.x
	put(intro, label("TONIGHT ON THE JUKEBOX", 15, OX), Rect2(0, 10, w, 20))
	intro_artist = put(intro, label("", 32, OX, rye), Rect2(0, 30, w, 40))
	intro_song = put(intro, label("", 18, OX), Rect2(0, 70, w, 24))
	var band := put(intro, ColorRect.new(), Rect2(5, 100, w - 10, 58)) as ColorRect
	band.color = OX
	intro_title = put(intro, label("", 44, GOLD, rye), Rect2(0, 100, w, 58))
	intro_goal = put(intro, label("", 22, OX, null, true), Rect2(30, 164, w - 60, 56))
	intro_how = put(intro, label("", 19, TEAL, null, true), Rect2(30, 222, w - 60, 72))
	intro_count = put(intro, label("", 17, OX), Rect2(0, 296, w, 26))


func _build_side() -> void:
	var r := RIGHT
	var w := r.size.x
	var side := put(self, Control.new(), r)
	put(side, label("NOW PLAYING", 13, OX), Rect2(0, 4, w, 18))
	side_artist = put(side, label("", 20, OX, rye), Rect2(0, 22, w, 28))
	side_song = put(side, label("", 14, OX), Rect2(0, 50, w, 20))
	var band := put(side, ColorRect.new(), Rect2(0, 76, w, 42)) as ColorRect
	band.color = OX
	side_title = put(side, label("", 26, GOLD, rye), Rect2(0, 76, w, 42))
	side_goal = put(side, label("", 17, OX, null, true), Rect2(14, 124, w - 28, 66))
	var rule := put(side, ColorRect.new(), Rect2(26, 196, w - 52, 2)) as ColorRect
	rule.color = OX
	side_status = put(side, label("", 17, TEAL, null, true), Rect2(12, 202, w - 24, 56))
	var bar := put(side, ColorRect.new(), Rect2(0, r.size.y - 52, w, 52)) as ColorRect
	bar.color = TEAL
	put(side, label("ROUND", 15, CREAM), Rect2(10, r.size.y - 52, 80, 52))
	clock = put(side, label("", 34, GOLD, rye), Rect2(80, r.size.y - 52, w - 90, 52))


static func short_title(text: String, limit: int) -> String:
	return text if text.length() <= limit else text.left(limit - 1).strip_edges() + "…"


func open(info: Dictionary) -> void:
	## A song mode was picked: show the frame with its instructions in the window.
	slot = clampi(int(info.get("slot", 1)), 1, DEVICES.size())
	var artist := str(info.get("artist", "")).to_upper()
	var song := str(info.get("song", ""))
	var title := str(info.get("title", ""))
	var goal := str(info.get("goal", ""))
	intro_artist.text = artist
	intro_song.text = "“%s”" % song if song != "" else ""
	intro_title.text = title
	intro_goal.text = goal
	intro_how.text = "\n".join(Array(str(info.get("how", "")).split("|", false)).map(func(s): return "•  " + s))
	side_artist.text = short_title(artist, 20)
	side_song.text = intro_song.text
	side_title.text = title
	side_title.add_theme_font_size_override("font_size", 26 if title.length() <= 11 else 19)
	side_goal.text = goal
	side_status.text = "GET READY"
	device.texture = load("res://images/modern/stage/device_%s.jpg" % DEVICES[slot - 1])
	device.visible = true
	intro_left_ms = float(info.get("ms", 8000))
	intro.visible = true
	set_status("", 0, 0)
	visible = true


func end_intro() -> bool:
	## Returns true the first time, when the window should switch to the video.
	if not intro.visible:
		return false
	intro.visible = false
	return true


func close() -> void:
	visible = false
	intro.visible = false
	caption.text = ""


func tick(delta: float) -> void:
	caption.visible = not intro.visible
	if intro.visible:
		intro_left_ms = max(0.0, intro_left_ms - delta * 1000.0)
		intro_count.text = "THE BALL COMES BACK IN %d" % int(ceil(intro_left_ms / 1000.0)) if intro_left_ms > 0 else "HERE IT COMES!"


func set_clock(seconds_left: int) -> void:
	clock.text = "%d:%02d" % [seconds_left / 60, seconds_left % 60]


func set_status(text: String, done: int, goal: int) -> void:
	if not intro.visible:
		side_status.text = text.replace("  •  ", "\n")
	var c := Vector2(LEFT.size.x / 2.0, LEFT.size.y - 22)
	for t in rung_tags:
		t.visible = false
	meter.visible = false
	set_tag(big_tag, "2X" if slot == 6 else "", Vector2(40, 34))
	if slot == 2 and goal > 0:
		var values := ["75,000", "150,000", "225,000", "300,000"]
		for i in 4:
			set_tag(rung_tags[i], ("✓ " if i < done else "") + values[i], Vector2(LEFT.size.x - 52, LEFT.size.y * RUNGS[i]), i < done)
		set_tag(count_tag, "RUNG %d OF %d" % [min(done + 1, goal), goal] if done < goal else "TOP RUNG!", Vector2(70, LEFT.size.y - 22))
	elif slot == 9 and goal > 0:
		meter.max_value = goal
		meter.value = done
		meter.visible = true
		set_tag(count_tag, "DANCERS %d / %d" % [done, goal], c - Vector2(0, 34))
	elif slot == 1:
		set_tag(count_tag, "", c)
	elif goal > 0 and slot in COUNTS:
		set_tag(count_tag, "%s %d OF %d" % [COUNTS[slot], done, goal], c)
	else:
		set_tag(count_tag, short_title(text.get_slice("  •  ", 0), 22).to_upper(), c)


func set_hurry(seconds: String, value: String) -> void:
	## Louis Jordan's stopwatch: the seconds on its face and the falling value below.
	set_tag(big_tag, seconds, Vector2(LEFT.size.x / 2.0, LEFT.size.y * 0.56))
	set_tag(count_tag, value, Vector2(LEFT.size.x / 2.0, LEFT.size.y - 22))


func set_players(scores: Array, active: int, ball: int, statuses: Array) -> void:
	## Players in the game get their score (the one up is ringed in amber); free slots show the player's status.
	var next := 0
	for i in 4:
		var playing := i < scores.size()
		var text := ""
		var value := ""
		if playing:
			text = "PLAYER %d" % (i + 1) + (" · UP" if i + 1 == active else "")
			value = commas(int(scores[i]))
		elif next < statuses.size():
			text = statuses[next][0]
			value = statuses[next][1]
			next += 1
		slot_labels[i].text = text
		slot_values[i].text = value
		slot_values[i].add_theme_font_size_override("font_size", 34 if playing else 26)
		slot_values[i].add_theme_color_override("font_color", GOLD if not playing or i + 1 == active else CREAM)
		slot_rings[i].visible = playing and i + 1 == active
	ball_label.text = "BALL %d" % ball


static func commas(n: int) -> String:
	var s := str(abs(n))
	var out := ""
	while s.length() > 3:
		out = "," + s.right(3) + out
		s = s.left(s.length() - 3)
	return ("-" if n < 0 else "") + s + out
