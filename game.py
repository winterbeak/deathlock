import sound

import pygame
# import sys

import constants as const
import events
import debug

import sequences
import editor
import graphics
import camera
import grid
import flicker
import entities.player
import entities.handler

import punchers


# INITIALIZATION
pygame.init()
main_surf = pygame.display.set_mode((const.SCRN_W, const.SCRN_H))
pygame.display.set_caption("deathlock")

clock = pygame.time.Clock()


background = graphics.load_image("background", 1)
player_glow = graphics.load_image("player_gradient", 1)


def draw_background(surf):
    surf.fill((20, 20, 20))
    surf.blit(background, (0, 0))


def screen_update(fps):
    pygame.display.flip()
    main_surf.fill(const.BLACK)
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


def levels_with_number(shared_name, first, last):
    """Returns a list of levels with increasing numbers attached.

    levels_with_number("Intro", 2, 5) returns the list
    ["Intro2", "Intro3", "Intro4", "Intro5"]
    """
    shared_name += "%i"
    return [shared_name % x for x in range(first, last + 1)]


sequence = sequences.Sequence(
    levels_with_number("Intro", 1, 4) +

    levels_with_number("PunchersIntro", 1, 5) +
    levels_with_number("PunchersMomentum", 1, 5) +
    ["PuncherParkour"] +
    levels_with_number("RespawnMomentum", 1, 5) +
    levels_with_number("FallPunch", 1, 2) +

    levels_with_number("CheckpointsIntro", 1, 3) +
    ["CheckpointTiming"] +
    levels_with_number("CheckpointsMomentum", 1, 4) +
    ["Teleport1", "TeleportDown", "Parkour", "LaserMaze", "EarlyJump",
     "SpamRespawn"] +
    levels_with_number("Escalator", 1, 3) +

    levels_with_number("DeathlockIntro", 1, 4) +
    levels_with_number("DeathlockMomentum", 1, 5) +
    ["DeadMansTrampoline", "DeadMansRightPuncher", "AvoidTheFirst"] +
    levels_with_number("Pole", 1, 2) +
    levels_with_number("DoubleFallPunch", 1, 2) +
    levels_with_number("Ledge", 1, 2) +
    ["DeathlockHeadBonk", "DeathlockPuzzle", "DeathlockBlock", "DoubleTriple"] +
    levels_with_number("Haul", 1, 4)
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

    main_cam.update()

    if player.dead:
        sound.set_music_volume(0.0)
    else:
        sound.set_music_volume(sound.MUSIC_VOLUME)

    if sequence.transitioning:
        sequence.update()
    if sequence.done_transitioning:
        end_transition()
    elif player.touching_goal:
        if level_beat_mode == SWAP_TO_EDITOR:
            swap_to_editor()
        elif level_beat_mode == NEXT_LEVEL:
            next_level()


def draw_level():
    if sequence.transitioning:
        if sequence.frame >= flicker.STOP_FLICKERING_FRAME:
            if sequence.frame == flicker.STOP_FLICKERING_FRAME:
                static_level_surf.fill(const.BLACK)
                sequence.next.draw_flicker_glow(static_level_surf, 1000)
                sequence.next.draw_silhouette(static_level_surf)
                sequence.next.draw_flicker_tiles(static_level_surf, main_cam, 1000)
            main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))
        elif sequence.frame >= flicker.START_DELAY:
            frame = sequence.frame - flicker.START_DELAY
            sequence.next.draw_flicker_glow(main_surf, frame)

            main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))

            sequence.next.draw_flicker_tiles(main_surf, main_cam, frame)

    else:
        main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))
        punchers.draw(main_surf, main_cam)
        sequence.current.draw_dynamic(main_surf, main_cam,
                                      player.dead, player.checkpoint is None)

        x = grid.x_of(sequence.current.player_goal.col) - grid.TILE_W * 2
        y = grid.y_of(sequence.current.player_goal.row) - grid.TILE_H * 2
        main_surf.blit(grid.player_goal_glow, (x, y), special_flags=pygame.BLEND_ADD)

        glow_x = int(player.center_x - player_glow.get_width() / 2)
        glow_y = int(player.center_y - player_glow.get_height() / 2)

        main_surf.blit(player_glow, (glow_x, glow_y), special_flags=pygame.BLEND_ADD)

def game_draw():
    draw_level()

    entity_handler.draw_all(main_surf, main_cam)


def editor_update():
    editor.update()


def editor_draw():
    draw_background(main_surf)
    sequence.current.draw_tiles(main_surf, main_cam, False)
    sequence.current.draw_dynamic(main_surf, main_cam,
                                  player.dead, player.checkpoint is None)
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


def next_level():
    sequence.current.unemit()
    draw_background(static_level_surf)
    sequence.start_transition(static_level_surf)
    player.hidden = True
    player.health = player.MAX_HEALTH  # Turns on music again


def end_transition():
    sequence.done_transitioning = False
    draw_background(static_level_surf)
    sequence.current.draw_static(static_level_surf, main_cam, False)
    player.level = sequence.current
    player.hidden = False
    player.hard_respawn()


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

    debug.debug(clock.get_fps())
    debug.debug(sequence.current.name)
    # debug.debug(main_cam.sliding, main_cam.last_slide_frame)
    # debug.debug(main_cam.slide_x_frame, main_cam.slide_y_frame, main_cam.SLIDE_LENGTH)
    # debug.debug(level.active_column, level.active_row)
    # debug.debug(level.previous_column, level.previous_row)

    # debug.debug(float(player.x_vel), float(player.ext_x_vel))
    # debug.debug(player.health, player.dead)

    debug.draw(main_surf)

    if pygame.K_f in events.keys.held_keys:
        screen_update(2)
    else:
        screen_update(60)

    if events.quit_program:
        break

pygame.quit()
