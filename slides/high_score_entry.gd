extends MPFSlide
## Initials entry on the Hall of Fame board, for either game.

const Handbill := preload("res://slides/handbill/handbill.gd")
const GREEN := "s_green_button_right_56"

var title: Label
var award: Label
var help: Label


func _ready() -> void:
	Handbill.backdrop(self, Handbill.HALL_OF_FAME)
	var area := Handbill.BOARD
	title = Handbill.label(self, "NEW HIGH SCORE", Rect2(area.position.x, area.position.y + 2, area.size.x, 40), 32)
	award = Handbill.label(self, "", Rect2(area.position.x, area.position.y + 42, area.size.x, 30), 22, Handbill.TEAL,
			Handbill.GOTHIC)
	var preview := RichTextLabel.new()
	preview.bbcode_enabled = true
	preview.fit_content = false
	preview.scroll_active = false
	preview.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	preview.position = Vector2(area.position.x, area.position.y + 74)
	preview.size = Vector2(area.size.x, 70)
	preview.add_theme_font_override("normal_font", Handbill.WOOD_TYPE)
	preview.add_theme_font_size_override("normal_font_size", 56)
	preview.add_theme_color_override("default_color", Handbill.INK)
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(preview)
	var letters := LabelSettings.new()
	letters.font = Handbill.WOOD_TYPE
	letters.font_size = 34
	letters.font_color = Handbill.UMBER
	var specials := letters.duplicate()
	specials.font = Handbill.GOTHIC
	specials.font_size = 24
	var input := MPFTextInput.new()
	input.max_length = 3
	input.grid_width = 46
	input.highlight_color = Handbill.INK
	input.character_appearance = letters
	input.special_appearance = specials
	input.display_node = preview
	input.alignment = FlowContainer.ALIGNMENT_CENTER
	input.position = Vector2(area.position.x + 10, area.position.y + 150)
	input.size = Vector2(area.size.x - 20, 130)
	add_child(input)
	help = Handbill.label(self, "", Rect2(area.position.x, Handbill.BOARD_FOOTER_Y - 14, area.size.x, 28), 19,
			Handbill.UMBER, Handbill.GOTHIC)


func action_update(settings: Dictionary, kwargs: Dictionary = {}) -> void:
	super(settings, kwargs)
	var values: Dictionary = settings.get("tokens", {}).duplicate()
	values.merge(kwargs, true)
	if values.has("title"):
		title.text = str(values.title)
	if values.has("award"):
		award.text = "PLAYER %s  •  %s  •  %s" % [values.get("player_num", 1), str(values.award).to_upper(),
				Handbill.comma(values.get("value", 0))]
	help.text = help_text(MPF.game.machine_vars)


## The select action follows Modern's remappable select switch; Classic always holds green.
static func help_text(state: Dictionary) -> String:
	var select = state.get("modern_select_switch", "")
	if state.get("session_game", "") == "modern" and select and select != GREEN:
		return "TAP GREEN: NEXT LETTER   •   SELECT: CHOOSE   •   FLIPPERS: MOVE"
	return "TAP GREEN: NEXT LETTER   •   HOLD GREEN: CHOOSE   •   FLIPPERS: MOVE"
