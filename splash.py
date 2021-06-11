import sound

import pygame

import constants as const
import events
import graphics

name = graphics.load_image("splash_name", 4)
name.set_colorkey(const.TRANSPARENT)

_logo_column = graphics.AnimColumn("splash_logo", 11, 4)
_logo_column.set_delay(9)
_logo_sheet = graphics.AnimSheet([_logo_column])
logo = graphics.AnimInstance(_logo_sheet)


LOGO_NAME_GAP = 24

WIDTH = name.get_width() + _logo_column.surface.get_width() + LOGO_NAME_GAP
HEIGHT = name.get_height() + 4

LOGO_X = const.SCRN_W // 2 - WIDTH // 2
NAME_X = LOGO_X + _logo_column.surface.get_width() + LOGO_NAME_GAP

NAME_Y = const.SCRN_H // 2 - HEIGHT // 2
LOGO_Y = NAME_Y + 12


FADE_IN_LENGTH = 60
FADE_HOLD_LENGTH = 140
FADE_OUT_LENGTH = 60

FADE_IN_END = FADE_IN_LENGTH
FADE_HOLD_END = FADE_IN_END + FADE_HOLD_LENGTH

fade_surface = pygame.Surface((WIDTH, HEIGHT))


jingle = sound.load("intro_jingle")
jingle.set_volume(0.7)


class SplashScreen:
    def __init__(self):
        self.done = False
        self.frame = 0

    def update(self):
        if self.frame == 0:
            jingle.play()

        logo.update()

        self.frame += 1

        # End animation if it finishes playing, or if any key is pressed to skip
        if self.frame >= 300 or events.keys.pressed:
            self.done = True
            jingle.stop()

    def draw(self, surf):
        logo.draw_frame(surf, LOGO_X, LOGO_Y)
        surf.blit(name, (NAME_X, NAME_Y))

        if self.frame < FADE_IN_END:
            shade = 255 / FADE_IN_LENGTH * self.frame
        elif self.frame < FADE_HOLD_END:
            shade = 255
        else:
            shade = 255 - 255 / FADE_OUT_LENGTH * (self.frame - FADE_HOLD_END)
        shade = max(0, min(255, shade))
        fade_surface.fill((shade, shade, shade))
        surf.blit(fade_surface, (LOGO_X, NAME_Y), special_flags=pygame.BLEND_MULT)
