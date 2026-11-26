extends MPFSlide
## The new entry pinned up on the Hall of Fame board.

const Handbill := preload("res://slides/handbill/handbill.gd")

var title: Label
var name_label: Label
var detail: Label


func _ready() -> void:
	Handbill.backdrop(self, Handbill.HALL_OF_FAME)
	var area := Handbill.BOARD
	title = Handbill.label(self, "INTO THE HALL OF FAME", Rect2(area.position.x, area.position.y + 20, area.size.x, 50), 34)
	name_label = Handbill.label(self, "", Rect2(area.position.x, area.position.y + 90, area.size.x, 120), 110)
	detail = Handbill.label(self, "", Rect2(area.position.x, area.position.y + 220, area.size.x, 40), 28, Handbill.TEAL)
	var thanks := Handbill.label(self, "THANKS FOR PLAYING", Rect2(area.position.x, Handbill.BOARD_FOOTER_Y - 16,
			area.size.x, 32), 22)
	Handbill.footer_rules(self, thanks)
	var pop := create_tween()
	name_label.pivot_offset = name_label.size / 2
	name_label.scale = Vector2(1.4, 1.4)
	pop.tween_property(name_label, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func action_update(settings: Dictionary, kwargs: Dictionary = {}) -> void:
	super(settings, kwargs)
	var values: Dictionary = settings.get("tokens", {}).duplicate()
	values.merge(kwargs, true)
	if values.has("title"):
		title.text = str(values.title)
	if values.has("player_name"):
		name_label.text = str(values.player_name) if str(values.player_name) else "???"
	if values.has("award"):
		detail.text = "%s  —  %s" % [str(values.award).to_upper(), Handbill.comma(values.get("value", 0))]
