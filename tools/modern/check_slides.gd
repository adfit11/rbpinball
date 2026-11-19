extends SceneTree
## Load and instance every Modern slide headlessly: godot --headless --path . -s tools/modern/check_slides.gd

func _initialize() -> void:
	var failed := 0
	for path in ["res://slides/modern/modern_hud.tscn", "res://slides/modern/modern_high_score.tscn",
			"res://slides/modern/modern_high_score_award.tscn"]:
		var scene: PackedScene = load(path)
		if scene == null:
			push_error("Cannot load %s" % path)
			failed += 1
			continue
		var node := scene.instantiate()
		root.add_child(node)
		print("OK ", path)
	for path in ["res://sounds/modern_music/house_band.mp3", "res://sounds/music/jukebox/10_hit_me/song_12.mp3",
			"res://sounds/modern_voice/mc/mc_game_start_01.mp3"]:
		if load(path) == null:
			push_error("Cannot load %s" % path)
			failed += 1
	print("FAILED %d" % failed)
	quit(failed)
