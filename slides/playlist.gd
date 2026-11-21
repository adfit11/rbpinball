extends RefCounted
## A numbered set of tracks (<prefix>_1.mp3 ... <prefix>_N.mp3) played in random order, never the same twice running.

var paths: PackedStringArray = []
var last := -1


func _init(prefix: String, count: int) -> void:
	for i in count:
		paths.append("%s_%d.mp3" % [prefix, i + 1])


func next_stream() -> AudioStream:
	var choices: Array = range(paths.size()).filter(func(i): return i != last)
	choices.shuffle()
	for i in choices + ([last] if last >= 0 else []):
		var stream := _load(paths[i])
		if stream:
			last = i
			if stream is AudioStreamMP3:
				stream.loop = false
			return stream
	return null


static func _load(path: String) -> AudioStream:
	if ResourceLoader.exists(path):
		return load(path)
	var file := ProjectSettings.globalize_path(path)
	if FileAccess.file_exists(file):
		return AudioStreamMP3.load_from_file(file)
	return null
