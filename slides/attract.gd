extends MPFSlide
## The Juke Joint handbill: choose a game and players on the poster; when idle, rotate the poster with each
## game's Hall of Fame board.

const Handbill := preload("res://slides/handbill/handbill.gd")
const Playlist := preload("res://slides/playlist.gd")
const PAGE_SECONDS := 8.0
const FADE_SECONDS := 0.8
const BOARDS := {"classic": "CLASSIC VOLCANO", "modern": "MODERN JUKE JOINT"}
## The "1 TO 4 PLAYERS" band and the foot of the PRESS START block on the poster, in slide space.
const CHOICE_BAND := Rect2(662, 521, 462, 40)
const HELP_STRIP := Rect2(530, 667, 715, 26)

var playlist := Playlist.new("res://sounds/modern_music/attract", 5)
var music: AudioStreamPlayer
var pages: Array[Control] = []
var page := 0
var selection: Control
var choices: Array[Label] = []
var help: Label
var rows := {}
var page_timer: Timer
var fade: Tween


func _ready() -> void:
	pages.append(_poster_page())
	for board in BOARDS:
		pages.append(_hall_page(board))
	page_timer = Timer.new()
	page_timer.wait_time = PAGE_SECONDS
	page_timer.timeout.connect(_next_page)
	add_child(page_timer)
	MPF.game.machine_update.connect(_on_machine_update)
	_render_selection()
	for board in BOARDS:
		_render_board(board)
	_render_showcase()
	music = AudioStreamPlayer.new()
	music.bus = "music"
	music.volume_db = -6.0
	add_child(music)
	music.finished.connect(_play_next_track)
	_play_next_track()


func _play_next_track() -> void:
	## One of five attract tracks at random; another random one follows when it ends.
	var stream := playlist.next_stream()
	if stream:
		music.stream = stream
		music.play()


func _exit_tree() -> void:
	MPF.game.machine_update.disconnect(_on_machine_update)
	super()


func _on_machine_update(variable: String, _value: Variant) -> void:
	if variable in ["selection_stage", "selection_game", "selection_players"]:
		_render_selection()
	elif variable == "attract_showcase":
		_render_showcase()
	else:
		for board in BOARDS:
			if variable.begins_with(board + "_score"):
				_render_board(board)


func _page(texture: Texture2D) -> Control:
	var root := Control.new()
	root.size = Vector2(1280, 720)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	var art := Handbill.backdrop(root, texture)
	# A slow push-in, as if walking up to the wall.
	var drift := create_tween().set_loops()
	drift.tween_property(art, "scale", Vector2(1.03, 1.03), 12.0).set_trans(Tween.TRANS_SINE)
	drift.tween_property(art, "scale", Vector2.ONE, 12.0).set_trans(Tween.TRANS_SINE)
	return root


func _poster_page() -> Control:
	var root := _page(Handbill.POSTER)
	selection = Control.new()
	selection.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(selection)
	var paper := ColorRect.new()
	paper.color = Color("#fbdcaa")
	paper.position = CHOICE_BAND.position
	paper.size = CHOICE_BAND.size
	selection.add_child(paper)
	var half := CHOICE_BAND.size.x / 2
	for i in 2:
		var cell := Rect2(CHOICE_BAND.position + Vector2(half * i + 6, 2), Vector2(half - 12, CHOICE_BAND.size.y - 4))
		var chip := ColorRect.new()
		chip.color = Handbill.INK
		chip.position = cell.position
		chip.size = cell.size
		selection.add_child(chip)
		var choice := Handbill.label(selection, "", cell, 28)
		choice.set_meta("chip", chip)
		choices.append(choice)
	help = Handbill.label(selection, "", HELP_STRIP, 19, Handbill.CREAM, Handbill.GOTHIC)
	return root


func _hall_page(board: String) -> Control:
	var root := _page(Handbill.HALL_OF_FAME)
	var area := Handbill.BOARD
	Handbill.label(root, BOARDS[board], Rect2(area.position.x, area.position.y + 4, area.size.x, 40), 30, Handbill.TEAL)
	var rule := ColorRect.new()
	rule.color = Handbill.INK
	rule.position = Vector2(area.position.x + 40, area.position.y + 50)
	rule.size = Vector2(area.size.x - 80, 3)
	root.add_child(rule)
	var cells: Array = []
	for i in 4:
		var y := area.position.y + 62 + i * 56
		var big := 40 if i == 0 else 34
		cells.append([
			Handbill.label(root, "", Rect2(area.position.x + 20, y, 230, 52), 20 if i == 0 else 18,
					Handbill.INK if i == 0 else Handbill.TEAL, Handbill.GOTHIC, HORIZONTAL_ALIGNMENT_LEFT),
			Handbill.label(root, "", Rect2(area.position.x + 250, y, 180, 52), big),
			Handbill.label(root, "", Rect2(area.position.x + 430, y, 270, 52), big, Handbill.INK,
					Handbill.WOOD_TYPE, HORIZONTAL_ALIGNMENT_RIGHT),
		])
	rows[board] = cells
	var footer := Handbill.label(root, "PRESS START", Rect2(area.position.x, Handbill.BOARD_FOOTER_Y - 16, area.size.x, 32),
			22, Handbill.INK)
	Handbill.footer_rules(root, footer)
	return root


func _render_board(board: String) -> void:
	var state: Dictionary = MPF.game.machine_vars
	for i in 4:
		var base := "%s_score%d_" % [board, i + 1]
		var cells: Array = rows[board][i]
		cells[0].text = str(state.get(base + "label", "")).to_upper()
		cells[1].text = str(state.get(base + "name", ""))
		cells[2].text = Handbill.comma(state.get(base + "value", 0)) if state.has(base + "value") else ""


func _render_selection() -> void:
	var state: Dictionary = MPF.game.machine_vars
	var classic_selected: bool = state.get("selection_game", "modern") == "classic"
	var game := "CLASSIC" if classic_selected else "MODERN"
	if state.get("selection_stage", "game") == "players":
		var count := int(state.get("selection_players", 1))
		_show_choice(choices[0], game, false)
		_show_choice(choices[1], "1 PLAYER" if count == 1 else "%d PLAYERS" % count, true)
		help.text = "GREEN BUTTON: 1 TO 4 PLAYERS   •   START: PLAY %s" % game
	else:
		_show_choice(choices[0], "CLASSIC", classic_selected)
		_show_choice(choices[1], "MODERN", not classic_selected)
		help.text = "GREEN BUTTON: SWITCH GAME   •   START: CHOOSE PLAYERS"


func _show_choice(choice: Label, title: String, selected: bool) -> void:
	choice.text = title
	choice.get_meta("chip").visible = selected
	choice.add_theme_color_override("font_color", Handbill.CREAM if selected else Handbill.TEAL)


func _render_showcase() -> void:
	var showcase: bool = MPF.game.machine_vars.get("attract_showcase", false)
	selection.visible = not showcase
	if showcase:
		page_timer.start()
	else:
		page_timer.stop()
		_show_page(0, false)


func _next_page() -> void:
	_show_page((page + 1) % pages.size(), true)


func _show_page(index: int, animate: bool) -> void:
	if fade:
		fade.kill()
	page = index
	for i in pages.size():
		pages[i].visible = i == index or (animate and pages[i].visible)
		if not animate:
			pages[i].modulate.a = 1.0
	var shown := pages[index]
	move_child(shown, -1)
	if not animate:
		return
	shown.modulate.a = 0.0
	fade = create_tween()
	fade.tween_property(shown, "modulate:a", 1.0, FADE_SECONDS)
	fade.tween_callback(func():
		for p in pages:
			p.visible = p == shown)
