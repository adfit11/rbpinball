"""Modern crater passages, reusing Classic's debounced subway inference."""

from custom_code.classic_subway import ClassicSubway


class ModernSubway(ClassicSubway):

    def _crater_passed(self, crater):
        self.machine.modes["modern_jukebox"].crater_entered(crater)
