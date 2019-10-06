import pygame
import constants as const
import os
import copy


def pathify(string):
    return os.path.join("images", string + ".png")


def load_image(path, multiplier=1):
    actual_path = pathify(path)

    if multiplier == 1:
        image = pygame.image.load(actual_path)

    else:
        unscaled = pygame.image.load(actual_path)

        width = unscaled.get_width() * multiplier
        height = unscaled.get_height() * multiplier
        image = pygame.transform.scale(unscaled, (width, height))

    image.convert()
    image.set_colorkey((0, 0, 0))
    return image


def flip_column(column):
    unflipped = column.surface
    flipped = pygame.transform.flip(unflipped, True, False)

    frame_count = column.frame_count

    new_column = SpriteColumn("null_sprite", frame_count, 1)
    new_column.surface = flipped
    new_column.frame_w = column.frame_w
    new_column.frame_h = column.frame_h
    new_column.delays = copy.copy(column.delays)

    return new_column


class SpriteColumn:
    def __init__(self, path, frame_count, multiplier=1):
        self.surface = load_image(path, multiplier)
        self.frame_count = frame_count
        self.frame_w = self.surface.get_width()
        self.frame_h = self.surface.get_height() // frame_count
        self.delays = (1, ) * frame_count

    def set_delay(self, amount):
        """Sets a constant delay for each frame."""
        self.delays = (amount, ) * self.frame_count

    def set_delays(self, amounts):
        """Lets you specify the delay between frames."""
        self.delays = tuple(amounts)


class AnimSheet:
    def __init__(self, columns):
        width = 0
        height = 0
        frame_counts = []

        anim_x = []  # the x position of the animation in the surface
        frame_widths = []
        frame_heights = []
        anim_delays = []
        for column in columns:
            anim_x.append(width)
            frame_widths.append(column.frame_w)
            frame_heights.append(column.frame_h)

            width += column.frame_w
            height = max(height, column.surface.get_height())
            frame_counts.append(column.frame_count)

            anim_delays.append(column.delays)

        self.anim_delays = tuple(anim_delays)
        self.anim_x = tuple(anim_x)
        self.frame_widths = tuple(frame_widths)
        self.frame_heights = tuple(frame_heights)

        self.frame_counts = tuple(frame_counts)
        self.anim_count = len(columns)

        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey(const.TRANSPARENT)
        for index, column in enumerate(columns):
            self.surface.blit(column.surface, (anim_x[index], 0))

    def draw_frame(self, surface, frame, anim, x, y):
        anim_x = self.anim_x[anim]
        anim_y = self.frame_heights[anim] * frame
        rect = (anim_x, anim_y, self.frame_widths[anim], self.frame_heights[anim])
        surface.blit(self.surface, (x, y), rect)


class AnimInstance:
    def __init__(self, spritesheet):
        self.spritesheet = spritesheet
        self.frame = 0
        self.anim = 0

        self.frame_delay = 0

    def update(self):
        if self.frame_delay < self.spritesheet.anim_delays[self.anim][self.frame]:
            self.frame_delay += 1
        else:
            self.frame_delay = 0
            self.next_frame()

    def draw_frame(self, surface, x, y):
        self.spritesheet.draw_frame(surface, self.frame, self.anim, x, y)

    def next_frame(self):
        self.frame += 1
        if self.frame >= self.spritesheet.frame_counts[self.anim]:
            self.frame = 0

    def set_anim(self, anim):
        if anim != self.anim:
            self.anim = anim
            self.frame = 0
            self.frame_delay = 0
