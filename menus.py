import sound

import os

import pygame
import constants as const
import graphics
import events
import flicker
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

start_sound = sound.load("game_start")
start_sound.set_volume(0.4)
select_sound = sound.load_numbers("menu%i", 3)
select_sound.set_volumes(0.35)

title = graphics.load_image("title", 1)
TITLE_X = const.SCRN_W // 2 - title.get_width() // 2
TITLE_Y = 100

title_shade = pygame.Surface(title.get_size())


def render_menu_text(surf, string, y, brightness):
    color = flicker.shade_color[brightness]
    text = m3x6.render(string, False, color)
    x = const.SCRN_W // 2 - text.get_width() // 2
    surf.blit(text, (x, y))


class MainMenu:
    def __init__(self):
        self.switch_to_game = False
        self._rebinding = False
        self._rebind_stage = 0
        self._rebind_end_wait_frame = 0

        self._start_press_delaying = False
        self._start_press_delay_frame = 0

        self._flicker_frame = 0
        self._start_prompt_flicker = flicker.FlickerSequence()
        self._rebind_prompt_flicker = flicker.FlickerSequence()
        self._title_flicker = flicker.FlickerSequence()

    def update(self):
        if self._flicker_frame == 0:
            flicker.mute_sounds()
            flicker.play_sounds()

        if self._flicker_frame < flicker.STOP_FLICKERING_FRAME:
            self._flicker_frame += 1
            if self._flicker_frame == flicker.STOP_FLICKERING_FRAME:
                flicker.mute_sounds()
            else:
                brightness = self._start_prompt_flicker.brightness(self._flicker_frame)
                flicker.set_sound_volume(0, brightness, 0.7)

                brightness = self._rebind_prompt_flicker.brightness(self._flicker_frame)
                flicker.set_sound_volume(1, brightness, 0.7)

                brightness = self._title_flicker.brightness(self._flicker_frame)
                flicker.set_sound_volume(2, brightness, 1.0)

        if self._start_press_delaying:
            self._start_press_delay_frame += 1
            if self._start_press_delay_frame >= 420:
                self.switch_to_game = True
                self._start_press_delaying = False
                self._start_press_delay_frame = 0

        elif self._rebinding:
            if self._rebind_stage == len(rebind_order):
                self._final_bind_delay()
            else:
                self._bind_current_stage()

            if self._rebind_stage > len(rebind_order):
                self._end_rebinding()

        elif not self._start_press_delaying:
            if rebind_key.is_pressed:
                self._rebinding = True
                select_sound.play_random()

            elif start_key.is_pressed:
                self._start_press_delaying = True
                start_sound.play()

                # Mute flicker sounds if they're still playing
                self._flicker_frame = flicker.STOP_FLICKERING_FRAME
                flicker.mute_sounds()

    def draw(self, surf):
        if self._rebinding:
            for i, key in enumerate(rebind_order):
                key_name = pygame.key.name(key.list[0])
                key_description = rebind_descriptions[i]

                if i == self._rebind_stage:
                    string = "> %s: %s" % (key_description, key_name)
                else:
                    string = "%s: %s" % (key_description, key_name)

                render_menu_text(surf, string, i * 50 + 210, flicker.FULL)
        elif not self._start_press_delaying:
            surf.blit(title, (TITLE_X, TITLE_Y))
            brightness = self._title_flicker.brightness(self._flicker_frame)
            title_shade.fill(flicker.shade_color[brightness])
            surf.blit(title_shade, (TITLE_X, TITLE_Y), special_flags=pygame.BLEND_MULT)

            start_string = "Press %s to start" % pygame.key.name(start_key.list[0])
            brightness = self._start_prompt_flicker.brightness(self._flicker_frame)
            render_menu_text(surf, start_string, 400, brightness)

            rebind_string = "Press %s to bind keys" % pygame.key.name(rebind_key.list[0])
            brightness = self._rebind_prompt_flicker.brightness(self._flicker_frame)
            render_menu_text(surf, rebind_string, 450, brightness)

    def _bind_current_stage(self):
        if events.keys.pressed:
            rebind_order[self._rebind_stage].list = [events.keys.pressed_keys[0]]
            self._rebind_stage += 1
            select_sound.play_random()

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
