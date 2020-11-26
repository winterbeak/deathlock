import sound

import pygame
# import sys

import constants as const
import events
# import debug

import graphics
import camera
import grid
import entities.player
import entities.handler

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


def test_level():
    room = grid.Room()
    room.change_rect(0, 20, 40, 1, grid.WALL)
    room.change_rect(20, 0, 1, 20, grid.DEATHLOCK)
    room.change_point(17, 17, grid.PUNCHER_EMIT_RIGHT)
    return room


level = test_level()

main_cam = camera.Camera()
main_cam.base_x = 0
main_cam.base_y = 0

player = entities.player.Player(level, 10, 10, main_cam)

entity_handler = entities.handler.Handler()
entity_handler.list = [player]

first_revive = True
beat_once = False

while True:
    events.update()

    # Resetting level
    if events.keys.pressed_key == pygame.K_r:
        if first_revive:
            first_revive = False
            sound.play_music()
            for sprite in player.heart_sprites:
                sprite.frame = 0
                sprite.frame_delay = 22

    entity_handler.update_all()
    punchers.update()

    main_cam.update()

    if player.dead:
        sound.set_music_volume(0.0)
    else:
        sound.set_music_volume(sound.MUSIC_VOLUME)

    # Drawing everything
    draw_background(post_surf, main_cam)
    punchers.draw(post_surf, main_cam)
    level.draw(post_surf, main_cam)

    entity_handler.draw_all(post_surf, main_cam)

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
