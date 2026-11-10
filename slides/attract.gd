extends MPFSlide

const SELECTED_COLOR := Color("#ffd08a")
const UNSELECTED_COLOR := Color("#b0bac6")

@onready var game_selection: VBoxContainer = %GameSelection
@onready var player_selection: VBoxContainer = %PlayerSelection
@onready var classic_choice: Label = %Classic
@onready var modern_choice: Label = %Modern
@onready var selected_game: Label = %SelectedGame
@onready var player_count: Label = %PlayerCount


func _ready() -> void:
	MPF.game.machine_update.connect(_on_machine_update)
	_render_selection()


func _exit_tree() -> void:
	MPF.game.machine_update.disconnect(_on_machine_update)
	super()


func _on_machine_update(variable: String, _value: Variant) -> void:
	if variable in ["selection_stage", "selection_game", "selection_players"]:
		_render_selection()


func _render_selection() -> void:
	var state: Dictionary = MPF.game.machine_vars
	var classic_selected: bool = state.get("selection_game", "modern") == "classic"
	var choosing_players: bool = state.get("selection_stage", "game") == "players"
	var count := int(state.get("selection_players", 1))
	game_selection.visible = not choosing_players
	player_selection.visible = choosing_players
	_show_choice(classic_choice, "Classic", classic_selected)
	_show_choice(modern_choice, "Modern", not classic_selected)
	selected_game.text = "Classic" if classic_selected else "Modern"
	player_count.text = "1 player" if count == 1 else "%d players" % count


func _show_choice(label: Label, title: String, selected: bool) -> void:
	label.text = "[ %s ]" % title if selected else title
	label.add_theme_color_override("font_color", SELECTED_COLOR if selected else UNSELECTED_COLOR)
