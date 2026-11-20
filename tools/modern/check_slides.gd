extends SceneTree
## Load and instance every Modern slide headlessly: godot --headless --path . -s tools/modern/check_slides.gd

func _initialize() -> void:
	var failed := 0
	for path in ["res://slides/modern/modern_hud.tscn", "res://slides/modern/modern_high_score.tscn",
			"res://slides/modern/modern_high_score_award.tscn", "res://slides/modern/modern_game_over.tscn", "res://slides/modern/modern_splash.tscn"]:
		var scene: PackedScene = load(path)
		if scene == null:
			push_error("Cannot load %s" % path)
			failed += 1
			continue
		var node := scene.instantiate()
		root.add_child(node)
		print("OK ", path)
	for path in ["res://sounds/modern_music/house_band.mp3", "res://sounds/modern_music/between_balls.mp3", "res://sounds/music/jukebox/10_hit_me/song_12.mp3",
			"res://sounds/modern_voice/mc/mc_game_start_01.mp3"]:
		if load(path) == null:
			push_error("Cannot load %s" % path)
			failed += 1
	var hud_script: GDScript = load("res://slides/modern/modern_hud.gd")
	var paths: PackedStringArray = hud_script.artist_video_paths("res://sounds/music/jukebox/03_big_joe_turner/song_2.mp3")
	if paths[0] != "res://videos/modern/jukebox/03_big_joe_turner/video_2.ogv" or paths[2] != "res://videos/modern/jukebox/club.ogv":
		push_error("Bad artist video paths %s" % [paths])
		failed += 1
	var dir := DirAccess.open("res://videos/modern/jukebox")
	for folder in dir.get_directories():
		if not (load("res://videos/modern/jukebox/%s/video.ogv" % folder) is VideoStream):
			push_error("Cannot load video for %s" % folder)
			failed += 1
	if not (load("res://videos/modern/jukebox/club.ogv") is VideoStream):
		push_error("Cannot load club video")
		failed += 1
	print("FAILED %d" % failed)
	quit(failed)
