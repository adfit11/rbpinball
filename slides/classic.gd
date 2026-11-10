extends MPFSlide

const ACTIVE_COLOR := Color("#ffd08a")
const INACTIVE_COLOR := Color("#b0bac6")

@onready var turn: Label = %Turn
@onready var scores: HBoxContainer = %Scores
@onready var bonus: Label = %Bonus
@onready var multiplier: Label = %Multiplier
@onready var locks: Label = %Locks


func _ready() -> void:
	for player: Dictionary in MPF.game.players:
		var label := Label.new()
		label.custom_minimum_size.x = 220
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.add_theme_font_size_override("font_size", 34)
		scores.add_child(label)
	MPF.game.player_update.connect(_on_player_update)
	_render_scoreboard()


func _exit_tree() -> void:
	MPF.game.player_update.disconnect(_on_player_update)
	super()


func _on_player_update(_variable: String, _value: Variant) -> void:
	_render_scoreboard()


func _render_scoreboard() -> void:
	var active: Dictionary = MPF.game.player
	var active_number := int(active.get("number", 1))
	turn.text = "Player %d  •  Ball %d" % [active_number, int(active.get("ball", 1))]

	for index in range(scores.get_child_count()):
		var player: Dictionary = MPF.game.players[index]
		var label: Label = scores.get_child(index)
		var number := index + 1
		label.text = "Player %d\n%s" % [number, MPF.util.comma_sep(int(player.get("score", 0)))]
		label.add_theme_color_override(
			"font_color", ACTIVE_COLOR if number == active_number else INACTIVE_COLOR
		)

	var lava := int(active.get("classic_playfield_multiplier", 1))
	multiplier.text = "%d× Lava Flow" % lava if lava > 1 else ""
	locks.text = "Multiball" if active.get("classic_multiball", 0) else "Locks  %d / 3" % int(active.get("classic_locks", 0))
	bonus.text = ""
	if active.get("classic_counting_bonus", 0):
		bonus.text = "Bonus remaining  %d × %d,000" % [
			int(active.get("classic_bonus_units", 0)),
			int(active.get("classic_bonus_multiplier", 1))
		]
