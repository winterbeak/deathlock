import pygame

import constants as const
import graphics

import grid


spikes = []

spike_left = graphics.load_image("punch", 2)
spike_left.set_colorkey(const.TRANSPARENT)
spike_right = pygame.transform.flip(spike_left, True, False)
spike_up = pygame.transform.rotate(spike_right, 90)
spike_down = pygame.transform.rotate(spike_right, -90)


def add(col, row, direction):
    spikes.append(Spike(col, row, direction))


def draw(surf, camera):
    for spike in spikes:
        spike.draw(surf, camera)


def update():
    for spike in reversed(spikes):
        spike.update()

        if spike.done:
            spikes.remove(spike)


class Spike:
    OUT_LENGTH = 3
    WAIT_LENGTH = 30
    IN_LENGTH = 10

    OUT_LAST = OUT_LENGTH
    WAIT_LAST = OUT_LAST + WAIT_LENGTH
    IN_LAST = WAIT_LAST + IN_LENGTH

    def __init__(self, col, row, direction):
        self.col = col
        self.row = row
        self.base_x = col * grid.TILE_W
        self.base_y = row * grid.TILE_H
        self.direction = direction

        self.frame = 0
        self.outness = 0

        self.done = False

    def update(self):
        """assumes square tiles"""
        self.frame += 1
        if self.frame <= self.OUT_LAST:
            self.outness = self.frame * (grid.TILE_W / self.OUT_LENGTH)

        elif self.frame <= self.WAIT_LAST:
            pass

        elif self.frame <= self.IN_LAST:
            self.outness = grid.TILE_W - ((self.frame - self.WAIT_LAST) * (grid.TILE_W / self.IN_LENGTH))

        else:
            self.done = True

    def draw(self, surf, camera):
        if self.direction == const.LEFT:
            x = (self.base_x + grid.TILE_W - self.outness) - camera.x
            y = self.base_y - camera.y

            surf.blit(spike_left, (x, y))

        elif self.direction == const.UP:
            x = self.base_x - camera.x
            y = (self.base_y + grid.TILE_H - self.outness) - camera.y

            surf.blit(spike_up, (x, y))

        elif self.direction == const.RIGHT:
            x = (self.base_x - grid.TILE_W + self.outness) - camera.x
            y = self.base_y - camera.y

            surf.blit(spike_right, (x, y))

        elif self.direction == const.DOWN:
            x = self.base_x - camera.x
            y = (self.base_y - grid.TILE_H + self.outness) - camera.y

            surf.blit(spike_down, (x, y))
