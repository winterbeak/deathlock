import sound

import pygame
# import sys

import constants as const
import events
import debug

import menus
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


goal_light_activate = sound.load_numbers("level_start%i", 3)
goal_light_activate.set_volumes(0.14)

hum = sound.load("hum")
MAX_HUM_VOLUME = 1.0
hum.set_volume(0)
hum.play(-1)

music = [sound.load("music%i" % x) for x in range(1, 4)]
for m in music[1:]:
    m.set_volume(0)
for m in music:
    m.play(-1)


background = graphics.load_image("background", 1)
player_glow = graphics.load_image("player_gradient", 1)


def draw_background(surf):
    surf.fill((20, 20, 20))
    surf.blit(background, (0, 0))


def screen_update(fps):
    pygame.display.flip()
    main_surf.fill(const.BLACK)
    clock.tick(fps)


def levels_with_number(shared_name, first, last):
    """Returns a list of levels with increasing numbers attached.

    levels_with_number("Intro", 2, 5) returns the list
    ["Intro2", "Intro3", "Intro4", "Intro5"]
    """
    shared_name += "%i"
    return [shared_name % x for x in range(first, last + 1)]


level_names = (
    levels_with_number("Intro", 1, 4) +

    levels_with_number("PunchersIntro", 1, 5) +
    levels_with_number("PunchersMomentum", 1, 6) +
    ["PuncherParkour"] +
    levels_with_number("RespawnMomentum", 1, 6) +
    levels_with_number("FallPunch", 1, 2) +
    ["RespawnPuzzle"] +

    levels_with_number("CheckpointsIntro", 1, 3) +
    ["CheckpointTiming"] +
    levels_with_number("CheckpointsMomentum", 1, 4) +
    ["CheckpointsClimb", "Teleport1", "TeleportDown", "SpamRespawn",
     "SpamRespawnFall", "LaserMaze", "EarlyJump"] +
    levels_with_number("Escalator", 1, 3) +

    levels_with_number("DeathlockIntro", 1, 4) +
    ["DeathlockTiming"] +
    levels_with_number("DeathlockMomentum", 1, 5) +
    ["DeathlockBlock"] +
    ["DeadMansTrampoline", "DeadMansRightPuncher", "AvoidTheFirst"] +
    levels_with_number("Pole", 1, 2) +
    levels_with_number("DoubleFallPunch", 1, 2) +
    levels_with_number("Ledge", 1, 2) +
    ["DeathlockHeadBonk", "DoubleTriple", "EverythingClimb"] +
    levels_with_number("Haul", 1, 4) +
    ["DoublePunchHaul", "CheckpointHaul", "BackAndForthHaul", "UsefulSpawnHaul"] +
    levels_with_number("End", 1, 6)
)
sequence = sequences.Sequence(level_names)

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

static_level_surf = pygame.Surface((const.SCRN_W, const.SCRN_H))
static_level_surf.set_colorkey(const.TRANSPARENT)
draw_background(static_level_surf)
sequence.current.draw_static(static_level_surf, main_cam)

# sound.play_music()


editor_key = events.Keybind([pygame.K_ESCAPE])

main_menu = menus.MainMenu()

GAME = 0
EDITOR = 1
MENU = 2
state = MENU


def hard_reset():
    player.hard_respawn()


def game_update():
    if not sequence.transitioning:
        entity_handler.update_all()
        punchers.update()

    main_cam.update()

    if player.hard_respawn_key.is_pressed:
        hard_reset()

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

    # if sequence.transitioning and sequence.frame < flicker.START_DELAY:
    #     hum.set_volume(max(0, hum.get_volume() - 0.05))
    # else:
    #     hum.set_volume(min(MAX_HUM_VOLUME, hum.get_volume() + 0.02))
    sequence.current.update_goal_sound(player, sequence.transitioning)


def draw_level():
    if sequence.transitioning:
        if sequence.frame >= flicker.STOP_FLICKERING_FRAME:
            if sequence.frame == flicker.STOP_FLICKERING_FRAME:
                static_level_surf.fill(const.BLACK)
                sequence.next.draw_flicker_glow(static_level_surf, 1000)
                sequence.next.draw_silhouette(static_level_surf)
                sequence.next.draw_flicker_tiles(static_level_surf, main_cam, 1000)
            main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))

            flicker.mute_sounds()

        elif sequence.frame >= flicker.START_DELAY:
            frame = sequence.frame - flicker.START_DELAY
            sequence.next.draw_flicker_glow(main_surf, frame)

            main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))

            sequence.next.draw_flicker_tiles(main_surf, main_cam, frame)

            adjust_flicker_volumes(frame)
    else:
        if player.checkpoint_swapped:
            if player.checkpoint:
                sequence.current.draw_checkpoint_and_ray(static_level_surf, player.checkpoint)
            if player.prev_frame_checkpoint:
                sequence.current.draw_checkpoint_and_ray(static_level_surf, player.prev_frame_checkpoint)

        if player.just_respawned or player.just_died:
            sequence.current.draw_deathlock(static_level_surf, camera.zero_camera, player.dead)

        main_surf.blit(static_level_surf, (int(-main_cam.x), int(-main_cam.y)))
        punchers.draw(main_surf, main_cam)
        sequence.current.draw_dynamic(main_surf, main_cam,
                                      player.dead, player.checkpoint is None)

        x = grid.x_of(sequence.current.player_goal.col) - grid.TILE_W * 2 - main_cam.x
        y = grid.y_of(sequence.current.player_goal.row) - grid.TILE_H * 2 - main_cam.y
        main_surf.blit(grid.player_goal_glow, (x, y), special_flags=pygame.BLEND_ADD)

        glow_x = int(player.center_x - player_glow.get_width() / 2) - main_cam.x
        glow_y = int(player.center_y - player_glow.get_height() / 2) - main_cam.y

        main_surf.blit(player_glow, (glow_x, glow_y), special_flags=pygame.BLEND_ADD)

        sequence.draw_text(main_surf, main_cam)
        sequence.draw_hearts(main_surf, main_cam, player)

        if sequence.level_num == sequences.TUTORIAL_TEXT_LEVEL:
            sequence.draw_respawn_text(main_surf, main_cam)

        if player.dead_no_horizontal_frames > 60 and sequence.level_num < sequences.FIRST_CHECKPOINT_LEVEL:
            sequence.draw_hard_respawn_popup(main_surf, main_cam, player)

    handle_music_fade()


def handle_music_fade():
    # Note: START_MUSIC_FADE_LEVEL fadeout is handled in next_level() method
    if sequence.level_num >= sequences.FIRST_CHECKPOINT_LEVEL:
        sound.lower_volume(music[1], 0.005)
        if sequence.level_num < sequences.START_MUSIC_FADE_LEVEL:
            sound.raise_volume(music[2], 0.02)

    if sequence.level_num >= sequences.TUTORIAL_TEXT_LEVEL:
        sound.lower_volume(music[0], 0.005)
        if sequence.level_num < sequences.FIRST_CHECKPOINT_LEVEL:
            sound.raise_volume(music[1], 0.02)


def adjust_flicker_volumes(frame):
    flickers = sequence.next.unique_flickers[:flicker.SOUND_COUNT]
    for i, flicker_sequence in enumerate(flickers):
        if i == 0:
            volume_mult = 0.7
        else:
            volume_mult = 0.56 / len(sequence.next.unique_flickers) + 0.2
        brightness = flicker_sequence.brightness(frame)
        if brightness == flicker.SOFT:
            flicker.turn_on_sounds[i].set_volume(0.02 * volume_mult)
        elif brightness == flicker.MEDIUM:
            flicker.turn_on_sounds[i].set_volume(0.05 * volume_mult)
        elif brightness == flicker.BRIGHT:
            flicker.turn_on_sounds[i].set_volume(0.1 * volume_mult)
        else:
            flicker.turn_on_sounds[i].set_volume(0)


def game_draw():
    draw_level()

    entity_handler.draw_all(main_surf, main_cam)


def editor_update():
    editor.update()


def editor_draw():
    draw_background(main_surf)
    sequence.current.draw_tiles(main_surf, main_cam)
    sequence.current.draw_dynamic(main_surf, main_cam,
                                  player.dead, player.checkpoint is None)
    editor.draw(main_surf)
    sequence.draw_text(main_surf, main_cam)
    sequence.draw_hearts(main_surf, main_cam, player)


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
    sequence.current.draw_static(static_level_surf, main_cam)


def next_level():
    sequence.current.unemit()
    sequence.start_transition(static_level_surf)
    player.hidden = True
    player.health = player.MAX_HEALTH  # Turns on music again
    player.checkpoint = None
    punchers.punchers = []
    flicker.play_sounds()

    if sequence.level_num >= sequences.START_MUSIC_FADE_LEVEL:
        sound.lower_volume(music[2], 0.1)


def end_transition():
    sequence.done_transitioning = False
    draw_background(static_level_surf)
    sequence.current.draw_static(static_level_surf, main_cam)
    player.level = sequence.current
    player.hidden = False
    player.hard_respawn(False)
    goal_light_activate.play_random()


while True:
    events.update()

    if editor_key.is_pressed:
        if state == GAME:
            swap_to_editor()
        elif state == EDITOR:
            swap_to_game()

    if state == MENU:
        main_menu.update()
        main_menu.draw(main_surf)

        if main_menu.switch_to_game:
            main_menu.switch_to_game = False
            state = GAME

    elif state == GAME:
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
