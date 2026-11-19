extends Node
## Scales the parent Control (laid out for 1280x720) to fill the window, letterboxed and centered.

const DESIGN := Vector2(1280, 720)


func _ready() -> void:
	get_viewport().size_changed.connect(_fit)
	_fit()


func _fit() -> void:
	var parent := get_parent() as Control
	if parent == null:
		return
	var screen := get_viewport().get_visible_rect().size
	var factor := minf(screen.x / DESIGN.x, screen.y / DESIGN.y)
	parent.scale = Vector2(factor, factor)
	parent.position = (screen - DESIGN * factor) / 2.0
