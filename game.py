import sound

import random
import pygame
# import sys

import constants as const
import events
# import debug

import graphics
import camera
import grid
import entities.player

import roomgen
import punchers


# INITIALIZATION
pygame.init()
post_surf = pygame.display.set_mode((const.SCRN_W, const.SCRN_H))
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


def draw_background(surf, cam):
    x = -(cam.x % (grid.TILE_W * 2)) - 10
    y = -(cam.y % (grid.TILE_H * 2)) - 10
    surf.blit(background, (x, y))


background = init_background()


def screen_update(fps):
    pygame.display.flip()
    post_surf.fill(const.WHITE)
    clock.tick(fps)



def current_room_is_silent():
    column = level.active_column
    row = level.active_row

    if column == START_COL and START_ROW <= row <= START_ROW + 2:
        return True

    if column == START_COL + 2 and START_ROW + 10 <= row <= START_ROW + 12:
        return True


level = grid.Level(10, 20)

START_COL = 3
START_ROW = 3
DEBUG_START_COL = START_COL
DEBUG_START_ROW = START_ROW
level.active_column = DEBUG_START_COL
level.active_row = DEBUG_START_ROW

PLAYER_START_X = DEBUG_START_COL * grid.Room.PIXEL_W + (grid.Room.PIXEL_W - entities.player.Player.WIDTH) // 2
PLAYER_START_Y = DEBUG_START_ROW * grid.Room.PIXEL_H

level.add_room(roomgen.intro_fallway(), START_COL, START_ROW)
level.add_room(roomgen.intro_fallway(), START_COL, START_ROW + 1)
level.add_room(roomgen.intro_fallway(), START_COL, START_ROW + 2)
level.add_room(roomgen.fallway_disturbance(), START_COL, START_ROW + 3)
level.add_room(roomgen.fallway_disturbance_2(), START_COL, START_ROW + 4)

level.add_room(roomgen.lets_go_left(), START_COL, START_ROW + 5)
level.add_room(roomgen.run_into_it(), START_COL - 1, START_ROW + 5)
level.add_room(roomgen.triple_bounce(), START_COL - 2, START_ROW + 5)
level.add_room(roomgen.ow_my_head(), START_COL - 3, START_ROW + 5)

level.add_room(roomgen.far_enough(), START_COL - 3, START_ROW + 6)
level.add_room(roomgen.spike_spike(), START_COL - 3, START_ROW + 7)
level.add_room(roomgen.not_far_enough(), START_COL - 3, START_ROW + 8)

level.add_room(roomgen.elbow(), START_COL - 3, START_ROW + 9)
level.add_room(roomgen.ready_for_launch(), START_COL - 2, START_ROW + 9)
level.add_room(roomgen.ready_for_landing(), START_COL - 1, START_ROW + 9)

level.add_room(roomgen.up_and_up_and_up(), START_COL, START_ROW + 9)
level.add_room(roomgen.crossing_rooms(), START_COL + 1, START_ROW + 9)

level.add_room(roomgen.climber(), START_COL - 1, START_ROW + 8)
level.add_room(roomgen.uncrossable_chasm(), START_COL, START_ROW + 8)
level.add_room(roomgen.secret_ceiling(), START_COL, START_ROW + 7)
level.add_room(roomgen.stand_in_weird_places(), START_COL + 1, START_ROW + 8)
level.add_room(roomgen.the_big_jump(), START_COL + 2, START_ROW + 8)
level.add_room(roomgen.safety_net(), START_COL + 2, START_ROW + 9)

level.add_room(roomgen.fall_the_right_way(), START_COL + 3, START_ROW + 8)
level.add_room(roomgen.run_run_jump(), START_COL + 4, START_ROW + 8)
level.add_room(roomgen.wrong(), START_COL + 4, START_ROW + 7)
level.add_room(roomgen.extra_gravity(), START_COL + 3, START_ROW + 7)

level.add_room(roomgen.left_down_town(), START_COL + 3, START_ROW + 9)
level.add_room(roomgen.how_to_go_left(), START_COL + 3, START_ROW + 10)
level.add_room(roomgen.mysteriously_easy(), START_COL + 2, START_ROW + 10)
level.add_room(roomgen.funnel_vision(), START_COL + 2, START_ROW + 11)
level.add_room(roomgen.intro_fallway(), START_COL + 2, START_ROW + 12)

main_cam = camera.Camera()
main_cam.base_x = level.active_column * grid.Room.PIXEL_W
main_cam.base_y = level.active_row * grid.Room.PIXEL_H

player = entities.player.Player(level, PLAYER_START_X, PLAYER_START_Y, main_cam)
player.set_health(0)

player.set_checkpoint()

first_revive = True
beat_once = False

while True:
    events.update()

    # Jumping
    if (pygame.K_p in events.keys.held_keys or pygame.K_z in events.keys.held_keys or
            pygame.K_w in events.keys.held_keys or pygame.K_UP in events.keys.held_keys or
            pygame.K_SPACE in events.keys.held_keys):
        if player.grounded and not player.dead:
            player.y_vel = -player.JUMP_SPEED
            player.JUMP_SOUNDS.play_random(0.3)
            player.tumble = False

    # Moving left & right
    if not player.dead:

        if not player.grounded:
            if player.tumble:
                if player.facing == const.LEFT:
                    player.sprite.set_anim(player.TUMBLE_LEFT_ID)
                else:
                    player.sprite.set_anim(player.TUMBLE_RIGHT_ID)

            # Jumping animation
            else:
                if player.facing == const.LEFT:
                    player.sprite.set_anim(player.JUMP_LEFT_ID)
                else:
                    player.sprite.set_anim(player.JUMP_RIGHT_ID)

                if player.y_vel < -player.JUMP_SPEED + 2.5:
                    player.sprite.frame = 0
                elif player.y_vel < -player.JUMP_SPEED + 5:
                    player.sprite.frame = 1
                elif player.y_vel < -player.JUMP_SPEED + 7.5:
                    player.sprite.frame = 2
                elif player.y_vel < 0:
                    player.sprite.frame = 3
                elif player.y_vel < 2.5:
                    player.sprite.frame = 4
                else:
                    player.sprite.frame = 5

        else:
            player.tumble = False

        if (pygame.K_LEFT in events.keys.held_keys or
                pygame.K_a in events.keys.held_keys):
            player.x_vel += -player.MOVE_ACC
            player.x_vel = max(player.x_vel, -player.MOVE_SPEED)

            if player.ext_x_vel > 0:
                player.ext_x_vel -= player.EXT_DEC
                if player.ext_x_vel < 0:
                    player.ext_x_vel = 0

            # Graphics and sounds
            if player.grounded:
                player.sprite.set_anim(player.RUN_LEFT_ID)

            if not player.tumble:
                player.facing = const.LEFT

            player.update_wall_push(const.LEFT)

            # Plays running sound
            if player.sprite.anim != player.WALL_PUSH_LEFT_ID:
                if player.grounded:
                    if player.run_sound_frame < player.RUN_SOUND_DELAY:
                        player.run_sound_frame += 1
                    else:
                        player.run_sound_frame = 0
                        player.RUN_SOUNDS.play_random(random.random() / 4 + 0.75)

        elif (pygame.K_RIGHT in events.keys.held_keys or
                pygame.K_d in events.keys.held_keys):
            player.x_vel += player.MOVE_ACC
            player.x_vel = min(player.x_vel, player.MOVE_SPEED)

            if player.ext_x_vel < 0:
                player.ext_x_vel += player.EXT_DEC
                if player.ext_x_vel > 0:
                    player.ext_x_vel = 0

            # Graphics
            if player.grounded:
                player.sprite.set_anim(player.RUN_RIGHT_ID)

            if not player.tumble:
                player.facing = const.RIGHT

            player.update_wall_push(const.RIGHT)

            if player.sprite.anim != player.WALL_PUSH_RIGHT_ID:
                if player.grounded:
                    if player.run_sound_frame < player.RUN_SOUND_DELAY:
                        player.run_sound_frame += 1
                    else:
                        player.run_sound_frame = 0
                        player.RUN_SOUNDS.play_random(random.random() / 2 + 0.5)

        # Decelerate when you stop moving
        else:
            player.run_sound_frame = player.RUN_SOUND_DELAY

            if player.grounded:
                if player.facing == const.LEFT:
                    player.sprite.set_anim(player.IDLE_LEFT_ID)
                elif player.facing == const.RIGHT:
                    player.sprite.set_anim(player.IDLE_RIGHT_ID)

            if player.x_vel < 0:
                player.x_vel += player.MOVE_DEC
                if player.x_vel > 0:
                    player.x_vel = 0

            elif player.x_vel > 0:
                player.x_vel -= player.MOVE_DEC
                if player.x_vel < 0:
                    player.x_vel = 0

            if player.ext_x_vel < 0:
                player.ext_x_vel += player.EXT_DEC
                if player.ext_x_vel > 0:
                    player.ext_x_vel = 0

            elif player.ext_x_vel > 0:
                player.ext_x_vel -= player.EXT_DEC
                if player.ext_x_vel < 0:
                    player.ext_x_vel = 0

    elif player.dead and player.grounded:
        player.x_vel = 0
        player.ext_x_vel = 0
        if player.facing == const.LEFT:
            player.sprite.set_anim(player.DEAD_GROUNDED_LEFT_ID)
        elif player.facing == const.RIGHT:
            player.sprite.set_anim(player.DEAD_GROUNDED_RIGHT_ID)

    elif player.dead:
        if player.facing == const.LEFT:
            player.sprite.set_anim(player.DEAD_FALL_LEFT_ID)
        else:
            player.sprite.set_anim(player.DEAD_FALL_RIGHT_ID)

        if player.y_vel < -player.JUMP_SPEED + 2.5:
            player.sprite.frame = 0
        elif player.y_vel < -player.JUMP_SPEED + 5:
            player.sprite.frame = 1
        elif player.y_vel < -player.JUMP_SPEED + 7.5:
            player.sprite.frame = 2
        elif player.y_vel < 0:
            player.sprite.frame = 3
        elif player.y_vel < 2.5:
            player.sprite.frame = 4
        else:
            player.sprite.frame_delay += 1
            if player.sprite.frame_delay > 1:
                player.sprite.frame_delay = 0

                if player.sprite.frame == 5:
                    player.sprite.frame = 6
                else:
                    player.sprite.frame = 5

    # Resetting level
    if events.keys.pressed_key == pygame.K_r:
        if first_revive:
            first_revive = False
            sound.play_music()
            for sprite in player.heart_sprites:
                sprite.frame = 0
                sprite.frame_delay = 22

    player.update()
    punchers.update()

    main_cam.update()
    # Resets the camera in case it decenters
    if main_cam.last_slide_frame:
        main_cam.base_x = level.active_column * grid.Room.PIXEL_W
        main_cam.base_y = level.active_row * grid.Room.PIXEL_H

    if player.offscreen_direction != 0:
        # Warp back to start at end of game
        if level.active_column == START_COL + 2 and level.active_row == START_ROW + 12:
            player.x = player.x - (grid.Room.PIXEL_W * 2)
            player.y = player.y - (grid.Room.PIXEL_H * 12)

            main_cam.base_x -= grid.Room.PIXEL_W * 2
            main_cam.base_y -= grid.Room.PIXEL_H * 12
            main_cam.x = main_cam.base_x
            main_cam.y = main_cam.base_y

            level.active_column = START_COL
            level.active_row = START_ROW
            level.previous_column = START_COL
            level.previous_row = START_ROW - 1

            sound.stop_music()

            first_revive = True
            beat_once = True

        main_cam.slide(player.offscreen_direction)
        level.change_room(player.offscreen_direction)

        player.set_checkpoint()
        # player.ROOM_CHANGE_SOUNDS.play_random(0.15)

    player.update_hearts()

    if player.dead or current_room_is_silent():
        sound.set_music_volume(0.0)
    else:
        sound.set_music_volume(sound.MUSIC_VOLUME)

    # Drawing everything
    draw_background(post_surf, main_cam)
    punchers.draw(post_surf, main_cam)
    level.draw(post_surf, main_cam)

    # Fixes the Secret Ceiling not drawing due to camera sliding two rooms at once
    # (also fixes Left Down Town for the same bug)
    if main_cam.sliding:
        if level.active_column == START_COL + 1 and level.active_row == START_ROW + 8:
            level.room_grid[START_COL][START_ROW + 7].draw(post_surf, main_cam)
        elif level.active_column == START_COL + 2 and level.active_row == START_ROW + 10:
            level.room_grid[START_COL + 3][START_ROW + 9].draw(post_surf, main_cam)
    player.draw(post_surf, main_cam)

    if ((level.active_column == START_COL and level.active_row == START_ROW + 3) or
            (level.previous_column == START_COL and level.previous_row == START_ROW + 3)):
        y = (START_ROW + 3) * grid.Room.PIXEL_H - main_cam.y + 180
        if beat_once:
            x = START_COL * grid.Room.PIXEL_W - main_cam.x
            x += (const.SCRN_W - CREDITS_TEXT.get_width()) // 2 - 2
            post_surf.blit(CREDITS_TEXT, (x, y))
        else:
            x = START_COL * grid.Room.PIXEL_W - main_cam.x
            x += (const.SCRN_W - CREDITS_TEXT.get_width()) // 2 - 2
            post_surf.blit(TUTORIAL_TEXT, (x, y))

    # Deathlock border
    if not player.dead:
        pygame.draw.rect(post_surf, const.RED, (0, 0, const.SCRN_W, const.SCRN_H), 5)

    player.draw_hearts(post_surf)

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
