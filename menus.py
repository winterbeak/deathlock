import os

import pygame
import constants as const
import events
import entities.player

start_key = entities.player.Player.jump_key
rebind_key = entities.player.Player.respawn_key

rebind_order = [entities.player.Player.left_key,
                entities.player.Player.right_key,
                entities.player.Player.jump_key,
                entities.player.Player.respawn_key,
                entities.player.Player.hard_respawn_key]
rebind_descriptions = ["Left", "Right", "Jump", "Action", "Reset level"]


m3x6 = pygame.font.Font(os.path.join("text", "m3x6.ttf"), 64)


def render_menu_text(surf, string, y):
    text = m3x6.render(string, False, const.WHITE)
    x = const.SCRN_W // 2 - text.get_width() // 2
    surf.blit(text, (x, y))


class MainMenu:
    def __init__(self):
        self.switch_to_game = False
        self._rebinding = False
        self._rebind_stage = 0
        self._rebind_end_wait_frame = 0

    def update(self):
        if self._rebinding:
            if self._rebind_stage == len(rebind_order):
                self._final_bind_delay()
            else:
                self._bind_current_stage()

            if self._rebind_stage > len(rebind_order):
                self._end_rebinding()

        else:
            if rebind_key.is_pressed:
                self._rebinding = True

            elif start_key.is_pressed:
                self.switch_to_game = True

    def draw(self, surf):
        if self._rebinding:
            for i, key in enumerate(rebind_order):
                key_name = pygame.key.name(key.list[0])
                key_description = rebind_descriptions[i]

                if i == self._rebind_stage:
                    string = "> %s key: %s" % (key_description, key_name)
                else:
                    string = "%s key: %s" % (key_description, key_name)

                render_menu_text(surf, string, i * 50 + 210)
        else:
            start_string = "Press %s to start" % pygame.key.name(start_key.list[0])
            render_menu_text(surf, start_string, 400)

            rebind_string = "Press %s to bind keys" % pygame.key.name(rebind_key.list[0])
            render_menu_text(surf, rebind_string, 450)

    def _bind_current_stage(self):
        if events.keys.pressed:
            rebind_order[self._rebind_stage].list = [events.keys.pressed_keys[0]]
            self._rebind_stage += 1

    def _final_bind_delay(self):
        # Little delay after binding the last key, so that the player can see
        # what they bound the final key to
        self._rebind_end_wait_frame += 1
        if self._rebind_end_wait_frame >= 30:
            self._end_rebinding()

    def _end_rebinding(self):
        self._rebinding = False
        self._rebind_stage = 0
        self._rebind_end_wait_frame = 0
