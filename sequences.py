import camera
import grid


class Sequence:
    def __init__(self, level_names):
        self.level_names = level_names
        self._level_num = 0
        self.current = grid.Room(level_names[0])
        self.next = grid.Room(level_names[1])
        self.transitioning = False
        self.done_transitioning = False
        self._frame = 0

    def next_level(self):
        self._level_num += 1
        self.current = self.next
        self.next = grid.Room(self.level_names[self._level_num + 1])

    def start_transition(self, static_level_surf):
        self.transitioning = True

        self.next.draw_static(static_level_surf, camera.zero_camera, False)

    def _end_transition(self):
        self.transitioning = False
        self.done_transitioning = True

    def update(self):
        if self._frame > 20:
            self._end_transition()
            self.next_level()

        self._frame += 1
