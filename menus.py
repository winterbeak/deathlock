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
                entities.player.Player.hard_respawn_key,
                entities.player.Player.pause_key]
rebind_descriptions = ["Left", "Right", "Jump", "Action", "Reset level", "Pause"]


m3x6 = pygame.font.Font(os.path.join("text", "m3x6.ttf"), 64)

main_menu_music = sound.load("menu_music")

start_sound = sound.load("game_start")
start_sound.set_volume(0.4)
select_sound = sound.load_numbers("menu%i", 3)
select_sound.set_volumes(0.35)

title = graphics.load_image("title", 1)

title_shade = pygame.Surface(title.get_size())


def render_menu_text(surf, string, y, brightness):
    color = flicker.shade_color[brightness]
    text = m3x6.render(string, False, color)
    x = const.SCRN_W // 2 - text.get_width() // 2
    surf.blit(text, (x, y))


class MainMenu:
    TITLE_X = const.SCRN_W // 2 - title.get_width() // 2
    TITLE_Y = 100

    KEYBIND_TEXT_Y = 190

    START_TEXT_Y = 400
    REBIND_TEXT_Y = 450

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

        self.start_action = "start"

    def update(self):
        if self._flicker_frame == 0:
            flicker.mute_sounds()
            flicker.play_sounds()

        if self._flicker_frame < flicker.STOP_FLICKERING_FRAME:
            self._flicker_frame += 1
            if self._flicker_frame == flicker.STOP_FLICKERING_FRAME:
                main_menu_music.play(-1)
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
            main_menu_music.fadeout(1000)
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
                self._start_key_pressed()

    def _start_key_pressed(self):
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

                render_menu_text(surf, string, i * 50 + self.KEYBIND_TEXT_Y, flicker.FULL)
        elif not self._start_press_delaying:
            self._draw_title(surf)

            start_string = ("Press %s to " + self.start_action) % pygame.key.name(start_key.list[0])
            brightness = self._start_prompt_flicker.brightness(self._flicker_frame)
            render_menu_text(surf, start_string, self.START_TEXT_Y, brightness)

            rebind_string = "Press %s to edit controls" % pygame.key.name(rebind_key.list[0])
            brightness = self._rebind_prompt_flicker.brightness(self._flicker_frame)
            render_menu_text(surf, rebind_string, self.REBIND_TEXT_Y, brightness)

    def _draw_title(self, surf):
        surf.blit(title, (self.TITLE_X, self.TITLE_Y))
        brightness = self._title_flicker.brightness(self._flicker_frame)
        title_shade.fill(flicker.shade_color[brightness])
        surf.blit(title_shade, (self.TITLE_X, self.TITLE_Y), special_flags=pygame.BLEND_MULT)

    def _bind_current_stage(self):
        if events.keys.pressed:
            rebind_order[self._rebind_stage].list = [events.keys.pressed_keys[0]]
            self._rebind_stage += 1
            if self._rebind_stage == len(rebind_order):
                select_sound.play(0)
            else:
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
        save_controls()


def save_controls():
    string = " ".join([str(key.list[0]) for key in rebind_order])
    string += "\n"
    with open(os.path.join("data", "controls.txt"), "w") as file:
        file.write(string)


class PauseMenu(MainMenu):
    START_TEXT_Y = 300
    REBIND_TEXT_Y = 350

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.paused_screen = pygame.Surface((const.SCRN_W, const.SCRN_H))
        self._flicker_frame = flicker.STOP_FLICKERING_FRAME

        self.start_action = "resume"

    def update(self):
        super().update()
        if self.player.pause_key.is_pressed and not self._rebinding:
            self.switch_to_game = True

    def draw(self, surf):
        surf.blit(self.paused_screen, (0, 0))
        super().draw(surf)

    def initialize(self, paused_screen):
        self.paused_screen.blit(paused_screen, (0, 0))
        shading = pygame.Surface((const.SCRN_W, const.SCRN_H))
        shading.fill((150, 150, 150))
        self.paused_screen.blit(shading, (0, 0), special_flags=pygame.BLEND_MULT)

    def _draw_title(self, surf):
        pass

    def _start_key_pressed(self):
        self.switch_to_game = True


class Credits:
    TEXT = [
        ("",),
        ("TESTING", "ThatOneGuy", "timurichk", "Horiph"),
        ("FONTS", "m3x6 and m5x7", "by Daniel Linssen"),
        ("SOUNDS",
         "Electricity 4 by PureAudioNinja",
         "Circuit Breaker Reverb.wav by DCElliott",
         "Hum1.wav by jameswrowles",
         "Metal Impact Railing Hit Deep Reverb 4 by Sheyvan",
         "Electrical Noise by _MC5_"),
        ("a game by winterbeak",),
        ("",)
    ]
    TEXT_HEIGHT = m3x6.get_height()

    START_DELAY = 240

    # Milliseconds each chord plays for
    LENGTHS = [0, 2667, 2736, 3421, 6000, 4000]

    def __init__(self):
        self._frame = 0
        self._counting_towards_end = False
        self._end_frame = 0
        self.done = False

        self.STARTS = []
        acc = 0
        for length in self.LENGTHS:
            acc += length
            self.STARTS.append(acc)

    def update(self):
        self._frame += 1
        if self._frame == self.START_DELAY:
            pygame.mixer.music.load(os.path.join("sounds", "credits.ogg"))
            pygame.mixer.music.play()
        if self._frame > self.START_DELAY:
            if not pygame.mixer.music.get_busy():
                self._counting_towards_end = True
        if self._counting_towards_end:
            self._end_frame += 1
            if self._end_frame == 60:
                self.done = True

    def draw(self, surf):
        if self._frame >= self.START_DELAY:
            for i, start in enumerate(self.STARTS):
                if pygame.mixer.music.get_pos() < start:
                    self._draw_credit(surf, i)
                    break

    def _draw_credit(self, surf, credit_num):
        lines = self.TEXT[credit_num]
        height = len(lines) * self.TEXT_HEIGHT
        y = const.SCRN_H // 2 - height // 2

        for line in lines:
            render_menu_text(surf, line, y, flicker.FULL)
            y += self.TEXT_HEIGHT
