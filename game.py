import pygame
# import sys

import constants as const
import events
import debug

import camera
import grid

import spikes


# INITIALIZATION
pygame.init()
post_surf = pygame.display.set_mode((const.SCRN_W, const.SCRN_H))

clock = pygame.time.Clock()


def screen_update(fps):
    pygame.display.flip()
    post_surf.fill(const.BLACK)
    clock.tick(fps)


class Player:
    CHECK_STEPS = 4
    TERMINAL_VELOCITY = 20.0

    MAX_HEALTH = 3
    JUMP_SPEED = 9
    MOVE_SPEED = 4
    MOVE_ACC = 0.8
    MOVE_DEC = 1.5
    EXT_DEC = 0.5

    INVULN_LENGTH = 10

    HEALTH_SPACING = 5

    def __init__(self, x, y, w, h, extend_x=0, extend_y=0):
        self.health = self.MAX_HEALTH
        self.dead = False
        self.offscreen_direction = 0

        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = 0

        # external velocities - caused by non-player forces
        self.ext_x_vel = 0

        self.x_dir = 0
        self.y_dir = 0

        self.w = w
        self.h = h
        self.extend_x = extend_x
        self.extend_y = extend_y
        self.gridbox = pygame.Rect(x, y, w, h)
        self.hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                  w + extend_x * 2, h + extend_y * 2)

        self.grounded = False
        self.level = level  # reference to the level layout

        self.hitstun = False
        self.invuln_frames = 0

    def draw(self, surf, cam):
        x = self.gridbox.x - cam.x
        y = self.gridbox.y - cam.y
        w = self.gridbox.w
        h = self.gridbox.h
        if self.dead:
            pygame.draw.rect(surf, const.RED, (x, y, w, h))
        else:
            pygame.draw.rect(surf, const.CYAN, (x, y, w, h))

    def check_offscreen(self):
        center_x = self.x + (self.w // 2)
        center_y = self.y + (self.h // 2)

        grid_left = grid.Room.PIXEL_W * level.active_column
        grid_right = grid_left + grid.Room.PIXEL_W
        grid_top = grid.Room.PIXEL_H * level.active_row
        grid_bottom = grid_top + grid.Room.PIXEL_H

        if center_x > grid_right:
            self.offscreen_direction = const.RIGHT
        elif center_x < grid_left:
            self.offscreen_direction = const.LEFT
        elif center_y > grid_bottom:
            self.offscreen_direction = const.DOWN
        elif center_y < grid_top:
            self.offscreen_direction = const.UP
        else:
            self.offscreen_direction = 0

    def move(self, void_solid=True):
        """moves body based on velocity and acceleration"""
        if self.grounded:
            self.hitstun = False
        else:
            self.y_acc = const.GRAVITY

        if self.x_vel > self.MOVE_SPEED:
            self.x_vel = self.MOVE_SPEED
        elif self.x_vel < -self.MOVE_SPEED:
            self.x_vel = -self.MOVE_SPEED
        self.collide_stage(not self.dead)

        self.x_vel += self.x_acc
        self.y_vel += self.y_acc
        if self.y_vel > self.TERMINAL_VELOCITY:
            self.y_vel = self.TERMINAL_VELOCITY

        self.x += self.x_vel + self.ext_x_vel
        self.y += self.y_vel

        # Determines direction of movement
        if self.x_vel < 0:
            self.x_dir = const.LEFT
        elif self.x_vel > 0:
            self.x_dir = const.RIGHT
        else:
            self.x_dir = 0

        if self.y_vel < 0:
            self.y_dir = const.UP
        elif self.y_vel > 0:
            self.y_dir = const.DOWN
        else:
            self.y_dir = 0

        self.check_ground(void_solid)

        self.goto(self.x, self.y)

        self.check_offscreen()

    def change_health(self, amount):
        self.health += amount
        if self.health <= 0:
            self.dead = True
        else:
            self.dead = False

    def set_health(self, amount):
        self.health = amount
        if self.health <= 0:
            self.dead = True
        else:
            self.dead = False

    # Body
    def goto(self, x, y):
        """instantly moves the body to a specific position"""
        x = int(x)
        y = int(y)
        self.x = x
        self.y = y
        self.gridbox.x = x
        self.gridbox.y = y
        self.hitbox.x = x - self.extend_x
        self.hitbox.y = y - self.extend_y

    def next_x(self):
        """returns the x position of the body on the next frame"""
        return self.x + self.x_vel + self.ext_x_vel + self.x_acc

    def next_y(self):
        """returns the y position of the body on the next frame"""
        return self.y + self.y_vel + self.y_acc

    def stop_x(self):
        self.x_dir = 0
        self.x_vel = 0
        self.ext_x_vel = 0
        self.x_acc = 0

    def stop_y(self):
        self.y_dir = 0
        self.y_vel = 0
        self.y_acc = 0

    def snap_x(self, col, side=const.LEFT):
        """snaps you to either the left side or right side of a tile"""
        if side == const.LEFT:
            self.goto(grid.x_of(col, const.LEFT) - self.w, self.y)
            self.stop_x()

        elif side == const.RIGHT:
            self.goto(grid.x_of(col, const.RIGHT), self.y)
            self.stop_x()

    def snap_y(self, row, side=const.TOP):
        """snaps you to either the top or bottom of a tile"""
        if side == const.TOP:
            self.goto(self.x, grid.y_of(row, const.TOP) - self.h)
            self.stop_y()

        elif side == const.BOTTOM:
            self.goto(self.x, grid.y_of(row, const.BOTTOM))
            self.stop_y()

    def collide_stage(self, void_solid=True):
        """checks collision with stage and updates movement accordingly

        if screen_edge is True, then the edge of the screen acts as a wall."""

        for step in range(1, self.CHECK_STEPS + 1):
            diff_x = self.next_x() - self.x
            diff_y = self.next_y() - self.y

            if diff_x < 0:
                dir_x = const.LEFT
            elif diff_x > 0:
                dir_x = const.RIGHT
            else:
                dir_x = 0

            if diff_y < 0:
                dir_y = const.UP
            elif diff_y > 0:
                dir_y = const.DOWN
            else:
                dir_y = 0

            left_x = self.x
            right_x = left_x + self.w - 1
            top_y = int(self.y + (diff_y * (step / self.CHECK_STEPS)))
            bottom_y = top_y + self.h - 1

            if dir_y == const.UP:
                if self.level.collide_horiz(left_x, right_x, top_y, void_solid):
                    self.snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self.level.collide_horiz(left_x, right_x, bottom_y, void_solid):
                    self.snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self.x + (diff_x * (step / 4)))
            right_x = left_x + self.w - 1
            top_y = self.y
            bottom_y = top_y + self.h - 1

            if dir_x == const.LEFT:
                if self.level.collide_vert(left_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(left_x), const.RIGHT)
            elif dir_x == const.RIGHT:
                if self.level.collide_vert(right_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(right_x), const.LEFT)

            if not self.dead and not self.invuln_frames:
                center_col = grid.col_at(self.x + (self.w // 2))
                center_row = grid.row_at(self.y + (self.h // 2))
                tile = self.level.tile_at(center_col, center_row)
                if tile == grid.SPIKE_LEFT:
                    self.get_hit()
                    spikes.add(center_col, center_row, const.LEFT)
                    self.ext_x_vel = -8

                elif tile == grid.SPIKE_UP:
                    self.get_hit()
                    spikes.add(center_col, center_row, const.UP)
                    self.y_vel = -12

                elif tile == grid.SPIKE_RIGHT:
                    self.get_hit()
                    spikes.add(center_col, center_row, const.RIGHT)
                    self.ext_x_vel = 8

                elif tile == grid.SPIKE_DOWN:
                    self.get_hit()
                    spikes.add(center_col, center_row, const.DOWN)
                    self.y_vel = 7

            elif self.invuln_frames:
                self.invuln_frames -= 1

    def draw_health(self, surf):
        for pip in range(self.health):
            x = pip * (self.w + self.HEALTH_SPACING) + 10
            y = 10

            pygame.draw.rect(surf, const.CYAN, (x, y, self.w, self.h))

    def get_hit(self):
        self.hitstun = True
        self.change_health(-1)
        self.invuln_frames = self.INVULN_LENGTH

    def check_ground(self, screen_edge):
        x1 = self.x
        x2 = x1 + self.w - 1
        y = self.y + self.h
        if self.level.collide_horiz(x1, x2, y, screen_edge):
            self.grounded = True
        else:
            self.grounded = False


level = grid.Level(3, 3)

room_0 = grid.Room(1, 0)
room_0.change_rect(0, 10, 20, 10, grid.WALL)
room_0.change_rect(12, 10, 4, 1, grid.SPIKE_EMIT_UP)
room_0.change_point(19, 9, grid.SPIKE_EMIT_LEFT)
level.add_room(room_0)

room_1 = grid.Room(2, 0)
room_1.change_rect(0, 10, 11, 2, grid.WALL)
room_1.change_rect(8, 6, 3, 1, grid.SPIKE_EMIT_DOWN)
level.add_room(room_1)

room_2 = grid.Room(2, 2)
room_2.change_rect(5, 10, 10, 3, grid.WALL)
level.add_room(room_2)

room_3 = grid.Room(0, 0)
room_3.change_rect(0, 10, 20, 1, grid.WALL)
room_3.change_point(0, 7, grid.SPIKE_EMIT_RIGHT)
room_3.change_point(5, 6, grid.SPIKE_EMIT_DOWN)
level.add_room(room_3)

level.active_row = 0
level.active_column = 1

player = Player(750, 250, 25, 25, -2, -2)
main_cam = camera.Camera()
main_cam.x = level.active_column * grid.Room.PIXEL_W
main_cam.y = level.active_row * grid.Room.PIXEL_H

while True:
    events.update()

    # Jumping
    if pygame.K_UP in events.keys.held_keys or pygame.K_w in events.keys.held_keys:
        if player.grounded and not player.dead:
            player.grounded = False
            player.y_vel = -player.JUMP_SPEED

    # Moving left & right
    if not player.hitstun and not player.dead:
        if (pygame.K_LEFT in events.keys.held_keys or
                pygame.K_a in events.keys.held_keys):
            player.x_vel += -player.MOVE_ACC

            if player.ext_x_vel > 0:
                player.ext_x_vel -= player.EXT_DEC
                if player.ext_x_vel < 0:
                    player.ext_x_vel = 0

        elif (pygame.K_RIGHT in events.keys.held_keys or
                pygame.K_d in events.keys.held_keys):
            player.x_vel += player.MOVE_ACC

            if player.ext_x_vel < 0:
                player.ext_x_vel += player.EXT_DEC
                if player.ext_x_vel > 0:
                    player.ext_x_vel = 0

        # Decelerate when you stop moving
        else:
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

    # Resetting level
    if events.keys.pressed_key == pygame.K_r:
        player.set_health(player.MAX_HEALTH)
        player.goto(level.current_center_x(), level.current_center_y() - 50)
        player.hitstun = False
        player.stop_x()
        player.stop_y()

    player.move(not player.dead)
    spikes.update()

    main_cam.update()
    # Resets the camera in case it decenters
    if main_cam.last_slide_frame:
        main_cam.x = level.active_column * grid.Room.PIXEL_W
        main_cam.y = level.active_row * grid.Room.PIXEL_H
        main_cam.last_slide_frame = False

    if player.offscreen_direction != 0:
        main_cam.slide(player.offscreen_direction)
        level.change_room(player.offscreen_direction)

    # Drawing everything
    spikes.draw(post_surf, main_cam)
    level.draw(post_surf, main_cam)
    player.draw(post_surf, main_cam)
    player.draw_health(post_surf)

    # Deathlock border
    if not player.dead:
        pygame.draw.rect(post_surf, const.RED, (0, 0, const.SCRN_W, const.SCRN_H), 5)

    #debug.debug(clock.get_fps())

    #debug.debug(player.y_vel)
    #debug.debug(player.health, player.dead)

    debug.draw(post_surf)

    if pygame.K_f in events.keys.held_keys:
        screen_update(2)
    else:
        screen_update(60)

    if events.quit_program:
        break
