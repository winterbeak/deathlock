import pygame
import constants as const
import sequences
import entities.player

start_key = entities.player.Player.jump_key
rebind_key = entities.player.Player.respawn_key


def render_menu_text(surf, string, y):
    text = sequences.m3x6.render(string, False, const.WHITE)
    x = const.SCRN_W // 2 - text.get_width() // 2
    surf.blit(text, (x, y))


class MainMenu:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self, surf):
        start_string = "Press %s to start" % pygame.key.name(start_key.list[0])
        render_menu_text(surf, start_string, 400)

        rebind_string = "Press %s to bind keys" % pygame.key.name(rebind_key.list[0])
        render_menu_text(surf, rebind_string, 450)
