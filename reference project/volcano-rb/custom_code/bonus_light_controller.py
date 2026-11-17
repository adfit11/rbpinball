from mpf.core.custom_code import CustomCode


class BonusLightController(CustomCode):

    def on_load(self):
        self.info_log("Bonus Light Controller custom code started successfully.")
        self._lights = self.machine.lights.items_tagged('bonus_light')
        self.machine.events.add_handler('player_bonus_val', self._handle_bonus_change)
        for light in self._lights:
            self.info_log(light.tags)

    def _handle_bonus_change(self, **kwargs):
        val = kwargs.get("value")
        change = kwargs.get("change")
        self.info_log("Bonus Light Event --> value: " + str(val) + ", change: " + str(change))

        if change > 0:
            if val < 11:
                for x in range(change):
                    self._get_bonus_light_by_number(val - x).on(fade_ms=50)
            elif val == 11:
                for x in range(2, 10):
                    self._get_bonus_light_by_number(x).off(fade_ms=50)
                self._get_bonus_light_by_number(10).on(fade_ms=50)
            elif val > 11:
                self._get_bonus_light_by_number(10).on(fade_ms=50)
                for x in range(1, 10):
                    self._get_bonus_light_by_number(x).off(fade_ms=50)
                # TODO: if off/on flicker is visible, batch these into a single update
                for x in range(1, val - 10 + 1):
                    self._get_bonus_light_by_number(x).on(fade_ms=50)

        elif change < 0:
            if val == 10:
                for x in range(1, 11):
                    self._get_bonus_light_by_number(x).on(fade_ms=50)
            if val > 10:
                self._get_bonus_light_by_number(val - 10 + 1).off(fade_ms=50)
            if val < 10:
                self._get_bonus_light_by_number(val + 1).off(fade_ms=50)

    def _get_bonus_light_by_number(self, num: int):
        for light in self._lights:
            if 'bonus{}'.format(num) in light.tags:
                return light
