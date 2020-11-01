import pygame

from entities import collision
import events


class TopDown(collision.Collision):
    left_key = events.Keybind([pygame.K_a, pygame.K_LEFT])
    right_key = events.Keybind([pygame.K_d, pygame.K_RIGHT])
    up_key = events.Keybind([pygame.K_w, pygame.K_UP])
    down_key = events.Keybind([pygame.K_s, pygame.K_DOWN])

    def __init__(self, level, camera, width, height, x, y):
        super().__init__(level, width, height, x, y)
        self.camera = camera
        self.collide_void = False

    def update(self):
        self._take_inputs()
        super().update()

    def _take_inputs(self):
        self.x_vel = 0
        self.y_vel = 0
        if self.left_key.is_held:
            self.x_vel -= 5
        if self.right_key.is_held:
            self.x_vel += 5
        if self.up_key.is_held:
            self.y_vel -= 5
        if self.down_key.is_held:
            self.y_vel += 5