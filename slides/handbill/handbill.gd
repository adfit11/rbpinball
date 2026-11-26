extends RefCounted
## Shared look for the attract posters and the high-score boards: wood type in poster ink on aged cream.

const INK := Color("#8c1c1a")
const TEAL := Color("#0f4a4a")
const UMBER := Color("#3b2414")
const CREAM := Color("#f6e7c8")
const AMBER := Color("#ffcf5a")
const WOOD_TYPE := preload("res://fonts/modern/Rye-Regular.ttf")
const GOTHIC := preload("res://fonts/modern/Oswald-Variable.ttf")
const POSTER := preload("res://images/attract/juke_joint_poster.jpg")
const HALL_OF_FAME := preload("res://images/attract/hall_of_fame.jpg")
## The blank board on the Hall of Fame poster, in 1280x720 slide space.
const BOARD := Rect2(300, 278, 720, 330)
const BOARD_FOOTER_Y := 586.0


static func backdrop(parent: Control, texture: Texture2D) -> TextureRect:
	var rect := TextureRect.new()
	rect.texture = texture
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	rect.size = Vector2(1280, 720)
	rect.pivot_offset = rect.size / 2
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(rect)
	return rect


static func label(parent: Control, text: String, rect: Rect2, size: int, color := INK,
		font: Font = WOOD_TYPE, align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new()
	l.text = text
	l.position = rect.position
	l.size = rect.size
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.clip_text = true
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l


## The red rule the poster printer runs either side of the footer words.
static func footer_rules(parent: Control, words: Label) -> void:
	for side in ["left", "right"]:
		var rule := ColorRect.new()
		rule.color = INK
		rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		parent.add_child(rule)
		words.set_meta("rule_" + side, rule)
	fit_footer_rules(words)


static func fit_footer_rules(words: Label) -> void:
	var font: Font = words.get_theme_font("font")
	var width := font.get_string_size(words.text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			words.get_theme_font_size("font_size")).x
	var centre := BOARD.position.x + BOARD.size.x / 2
	var gap := width / 2 + 18
	var y := words.position.y + words.size.y / 2 - 2
	var left: ColorRect = words.get_meta("rule_left")
	var right: ColorRect = words.get_meta("rule_right")
	left.position = Vector2(BOARD.position.x + 8, y)
	left.size = Vector2(maxf(0, centre - gap - left.position.x), 4)
	right.position = Vector2(centre + gap, y)
	right.size = Vector2(maxf(0, BOARD.end.x - 8 - right.position.x), 4)


static func comma(value: Variant) -> String:
	var digits := str(int(value if value != null else 0))
	var out := ""
	while digits.length() > 3:
		out = "," + digits.right(3) + out
		digits = digits.left(-3)
	return digits + out
