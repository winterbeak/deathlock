import pygame
import os

import grid
import flicker
import constants as const


def load_story():
    with open(os.path.join("text", "story.txt"), "r") as file:
        data = file.read()
    lines = data.split("\n")
    return lines


story = load_story()

font = pygame.font.Font(os.path.join("text", "m5x7.ttf"), 32)


class Sequence:
    def __init__(self, level_names):
        self.level_names = level_names
        self._level_num = 0
        self.current = grid.Room(level_names[0])
        self.next = grid.Room(level_names[1])
        self.transitioning = False
        self.done_transitioning = False
        self._frame = 0

    @property
    def frame(self):
        return self._frame

    def next_level(self):
        self._level_num += 1
        self.current = self.next
        self.next = grid.Room(self.level_names[self._level_num + 1])

    def start_transition(self, static_level_surf):
        self._frame = 0
        self.transitioning = True

        static_level_surf.fill(const.TRANSPARENT)
        self.next.draw_silhouette(static_level_surf)

    def _end_transition(self):
        self.transitioning = False
        self.done_transitioning = True

    def update(self):
        if self._frame >= flicker.TOTAL_LENGTH:
            self._end_transition()
            self.next_level()

        self._frame += 1

    def draw_text(self, surf, cam):
        level_num = len(self.level_names) - self._level_num
        string = str(level_num) + ": " + story[self._level_num]
        text = font.render(string, False, const.WHITE)

        x = self.current.text_x - text.get_width() // 2 - cam.x
        y = self.current.text_y - cam.y

        surf.blit(text, (x, y))
