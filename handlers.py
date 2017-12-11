class PlayerEventHandler:
    # flake8: noqa
    def join(self, time, new_team): pass
    def quit(self, time, old_flag, old_powers, old_team): pass
    def switch(self, time, old_flag, powers, new_team): pass
    def grab(self, time, new_flag, powers, team): pass
    def capture(self, time, old_flag, powers, team): pass
    def flagless_capture(self, time, flag, powers, team): pass
    def powerup(self, time, flag, power_up, new_powers, team): pass
    def duplicate_powerup(self, time, flag, powers, team): pass
    def powerdown(self, time, flag, power_down, new_powers, team): pass
    def return_(self, time, flag, powers, team): pass
    def drop(self, time, old_flag, powers, team): pass
    def pop(self, time, powers, team): pass
    def start_prevent(self, time, flag, powers, team): pass
    def stop_prevent(self, time, flag, powers, team): pass
    def start_button(self, time, flag, powers, team): pass
    def stop_button(self, time, flag, powers, team): pass
    def start_block(self, time, flag, powers, team): pass
    def stop_block(self, time, flag, powers, team): pass
    def end(self, time, flag, powers, team): pass
