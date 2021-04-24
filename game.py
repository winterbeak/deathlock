import sound

import pygame
# import sys

import constants as const
import events
# import debug

import sequences
import editor
import graphics
import camera
import grid
import entities.player
import entities.handler

import punchers


# INITIALIZATION
pygame.init()
main_surf = pygame.display.set_mode((const.SCRN_W, const.SCRN_H))
pygame.display.set_caption("deathlock")

clock = pygame.time.Clock()


TUTORIAL_TEXT = graphics.load_image("tutorial", 2)
TUTORIAL_TEXT.set_colorkey(const.TRANSPARENT)
CREDITS_TEXT = graphics.load_image("credits", 2)
CREDITS_TEXT.set_colorkey(const.TRANSPARENT)


def init_background():
    surf = pygame.Surface((const.SCRN_W + grid.TILE_W * 2,
                           const.SCRN_H + grid.TILE_H * 2))
    width = grid.TILE_W
    height = grid.TILE_H
    for row in range(surf.get_height() // height):
        for col in range(surf.get_width() // width):
            x = col * width
            y = row * height

            if (col + row) % 2 == 0:
                pygame.draw.rect(surf, const.BACKGROUND_GREY, (x, y, width, height))
            else:
                pygame.draw.rect(surf, const.WHITE, (x, y, width, height))

    return surf


def draw_background(surf):
    surf.blit(background, (0, 0))


background = init_background()


def screen_update(fps):
    pygame.display.flip()
    main_surf.fill(const.WHITE)
    clock.tick(fps)


def test_level():
    room = grid.Room("Test Level")
    room.add_rect(0, 20, 40, 1, grid.Wall)
    room.add_rect(20, 0, 1, 20, grid.Deathlock)
    room.add_tile(17, 17, grid.PunchBox(const.RIGHT))

    room.add_tile(5, 17, grid.PunchBox(const.UP))

    room.add_tile(11, 18, grid.PunchBox(const.UP))
    room.add_tile(10, 17, grid.PunchBox(const.RIGHT))

    room.add_tile(11, 17, grid.Deathlock())
    room.add_tile(11, 13, grid.PunchBox(const.DOWN))
    room.add_rect(0, 30, 40, 1, lambda: grid.PunchBox(const.UP))

    room.add_checkpoint(23, 3, const.DOWN)
    room.add_checkpoint(26, 16, const.RIGHT)
    room.add_checkpoint(30, 25, const.LEFT)
    room.add_checkpoint(30, 24, const.UP)

    room.emit()

    return room


# Current order: Intro, Punchers, RespawnMomentum, FallPunch
sequence = sequences.Sequence(
    ["Haul2"] +
    ["Intro%i" % x for x in range(1, 5)] +
    ["Punchers%i" % x for x in range(1, 11)] +
    ["Parkour", "PuncherParkour"]
)
editor = editor.Editor(sequence)

SWAP_TO_EDITOR = 0
NEXT_LEVEL = 1
level_beat_mode = NEXT_LEVEL

main_cam = camera.Camera()
main_cam.base_x = 0
main_cam.base_y = 0

player = entities.player.Player(sequence.current, main_cam)

entity_handler = entities.handler.Handler()
entity_handler.list = [player]

hard_reset_key = events.Keybind([pygame.K_r])

static_level_surf = pygame.Surface((const.SCRN_W, const.SCRN_H))
static_level_surf.set_colorkey(const.TRANSPARENT)
draw_background(static_level_surf)
sequence.current.draw_static(static_level_surf, main_cam, False)

sound.play_music()


editor_key = events.Keybind([pygame.K_ESCAPE])

GAME = 0
EDITOR = 1
state = GAME


def hard_reset():
    player.hard_respawn()


def game_update():
    if hard_reset_key.is_pressed:
        hard_reset()

    entity_handler.update_all()
    punchers.update()

    sequence.current.update()

    main_cam.update()

    if player.dead:
        sound.set_music_volume(0.0)
    else:
        sound.set_music_volume(sound.MUSIC_VOLUME)

    if sequence.transitioning:
        sequence.update()
    elif sequence.done_transitioning:
        sequence.done_transitioning = False
        player.level = sequence.current
        player.hidden = False
        player.hard_respawn()
    elif player.touching_goal:
        if level_beat_mode == SWAP_TO_EDITOR:
            swap_to_editor()
        elif level_beat_mode == NEXT_LEVEL:
            sequence.current.unemit()
            draw_background(sequence.pinhole_surf)
            draw_background(static_level_surf)
            sequence.start_transition(player, static_level_surf)
            player.hidden = True
            player.health = player.MAX_HEALTH  # Turns on music again


def draw_level():
    if sequence.transitioning:
        main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))
        punchers.draw(main_surf, main_cam)
        sequence.draw_pinhole(main_surf)
        sequence.draw_player_circle(main_surf)
    else:
        main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))
        punchers.draw(main_surf, main_cam)
        sequence.current.draw_dynamic(main_surf, main_cam)


def game_draw():
    draw_level()

    entity_handler.draw_all(main_surf, main_cam)


def editor_update():
    editor.update()


def editor_draw():
    draw_background(main_surf)
    sequence.current.draw_static(main_surf, main_cam, False)
    sequence.current.draw_dynamic(main_surf, main_cam)
    editor.draw(main_surf)


def swap_to_editor():
    global state
    state = EDITOR
    sequence.current.unemit()


def swap_to_game():
    global state
    state = GAME
    player.hard_respawn()
    sequence.current.emit()
    draw_background(static_level_surf)
    sequence.current.draw_static(static_level_surf, main_cam, False)


while True:
    events.update()

    if editor_key.is_pressed:
        if state == GAME:
            swap_to_editor()
        elif state == EDITOR:
            swap_to_game()

    if state == GAME:
        game_update()
        game_draw()

    elif state == EDITOR:
        editor_update()
        editor_draw()

    # debug.debug(clock.get_fps())
    # debug.debug(main_cam.sliding, main_cam.last_slide_frame)
    # debug.debug(main_cam.slide_x_frame, main_cam.slide_y_frame, main_cam.SLIDE_LENGTH)
    # debug.debug(level.active_column, level.active_row)
    # debug.debug(level.previous_column, level.previous_row)

    # debug.debug(float(player.x_vel), float(player.ext_x_vel))
    # debug.debug(player.health, player.dead)

    # debug.draw(post_surf)

    if pygame.K_f in events.keys.held_keys:
        screen_update(2)
    else:
        screen_update(60)

    if events.quit_program:
        break

pygame.quit()
