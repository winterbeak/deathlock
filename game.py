import pygame
# import sys

import constants as const
import events
import debug

import camera
import grid


# INITIALIZATION
pygame.init()
post_surf = pygame.display.set_mode((const.SCRN_W, const.SCRN_H))

clock = pygame.time.Clock()


def screen_update(fps):
    pygame.display.flip()
    post_surf.fill(const.BLACK)
    clock.tick(fps)


class Body:
    """the skeleton of anything that moves and lives"""
    CHECK_STEPS = 4
    TERMINAL_VELOCITY = 20.0

    def __init__(self, x, y, w, h, extend_x=0, extend_y=0):
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = 0

        self.x_dir = 0
        self.y_dir = 0

        self.w = w
        self.h = h
        self.extend_x = extend_x
        self.extend_y = extend_y
        self.gridbox = pygame.Rect(x, y, w, h)
        self.hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                  w + extend_x*2, h + extend_y*2)

        self.grounded = False
        self.level = level   # reference to the level layout

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

    def move(self, screen_edge):
        """moves body based on velocity and acceleration"""
        self.x_vel += self.x_acc
        self.y_vel += self.y_acc
        if self.y_vel > self.TERMINAL_VELOCITY:
            self.y_vel = self.TERMINAL_VELOCITY
        self.x += self.x_vel
        self.y += self.y_vel

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

        self.check_ground(screen_edge)

        self.goto(self.x, self.y)

    def next_x(self):
        """returns the x position of the body on the next frame"""
        return self.x + self.x_vel + self.x_acc

    def next_y(self):
        """returns the y position of the body on the next frame"""
        return self.y + self.y_vel + self.y_acc

    def stop_x(self):
        self.x_dir = 0
        self.x_vel = 0
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

    def collide_stage(self, screen_edge=True):
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
                if self.level.collide_horiz(left_x, right_x, top_y, screen_edge):
                    self.snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self.level.collide_horiz(left_x, right_x, bottom_y, screen_edge):
                    self.snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self.x + (diff_x * (step / 4)))
            right_x = left_x + self.w - 1
            top_y = self.y
            bottom_y = top_y + self.h - 1

            debug.debug(step + 10, left_x, right_x)

            if dir_x == const.LEFT:
                if self.level.collide_vert(left_x, top_y, bottom_y, screen_edge):
                    self.snap_x(grid.col_at(left_x), const.RIGHT)
            elif dir_x == const.RIGHT:
                if self.level.collide_vert(right_x, top_y, bottom_y, screen_edge):
                    self.snap_x(grid.col_at(right_x), const.LEFT)

    def check_ground(self, screen_edge):
        x1 = self.x
        x2 = x1 + self.w - 1
        y = self.y + self.h
        if self.level.collide_horiz(x1, x2, y, screen_edge):
            self.grounded = True
        else:
            self.grounded = False


class Player:
    MAX_HEALTH = 3
    JUMP_SPEED = 7
    MOVE_SPEED = 4

    def __init__(self, x, y, w, h, extend_x=0, extend_y=0):
        self.body = Body(x, y, w, h, extend_x, extend_y)
        self.health = self.MAX_HEALTH
        self.dead = True
        self.offscreen_direction = 0

    def draw(self, surf, cam):
        x = self.body.gridbox.x - cam.x
        y = self.body.gridbox.y - cam.y
        w = self.body.gridbox.w
        h = self.body.gridbox.h
        pygame.draw.rect(surf, const.CYAN, (x, y, w, h))

    def check_offscreen(self):
        center_x = self.body.x + (self.body.w // 2)
        center_y = self.body.y + (self.body.h // 2)

        grid_left = grid.Grid.PIXEL_W * level.active_column
        grid_right = grid_left + grid.Grid.PIXEL_W
        grid_top = grid.Grid.PIXEL_H * level.active_row
        grid_bottom = grid_top + grid.Grid.PIXEL_H

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

    def move(self):
        if not self.body.grounded:
            self.body.y_acc = const.GRAVITY
        self.body.collide_stage(not self.dead)
        self.body.move(not self.dead)

        self.check_offscreen()

    def change_health(self, amount):
        self.health += amount
        if self.health <= 0:
            self.dead = True


level = grid.Level(3, 3)

room_0 = grid.Grid(0, 0)
room_0.change_rect(10, 42, 10, 1, grid.WALL)
room_0.change_rect(13, 45, 20, 1, grid.WALL)
room_0.change_rect(18, 48, 32, 1, grid.WALL)
room_0.change_rect(40, 40, 5, 10, grid.WALL)
level.grid_grid[0][0] = room_0

room_1 = grid.Grid(1, 0)
room_1.change_rect(0, 48, 5, 1, grid.WALL)
room_1.change_rect(45, 48, 5, 1, grid.WALL)
level.grid_grid[1][0] = room_1

room_2 = grid.Grid(1, 2)
room_2.change_rect(5, 44, 40, 3, grid.WALL)
level.grid_grid[1][2] = room_2

player = Player(250, 250, 25, 25, -2, -2)
main_cam = camera.Camera()


while True:
    events.update()

    # Jumping
    if ((pygame.K_UP in events.keys.held_keys or
            pygame.K_w in events.keys.held_keys) and
            player.body.grounded):
        player.body.grounded = False
        player.body.y_vel = -player.JUMP_SPEED

    # Moving left & right
    if (pygame.K_LEFT in events.keys.held_keys or
            pygame.K_a in events.keys.held_keys):
        player.body.x_vel = -player.MOVE_SPEED
    elif (pygame.K_RIGHT in events.keys.held_keys or
            pygame.K_d in events.keys.held_keys):
        player.body.x_vel = player.MOVE_SPEED
    else:
        player.body.x_vel = 0

    player.move()

    main_cam.update()
    # Resets the camera in case it decenters
    if main_cam.last_slide_frame:
        main_cam.x = level.active_column * grid.Grid.PIXEL_W
        main_cam.y = level.active_row * grid.Grid.PIXEL_H
        main_cam.last_slide_frame = False

    if player.offscreen_direction != 0:
        main_cam.slide(player.offscreen_direction)
        level.change_room(player.offscreen_direction)

    # Drawing everything
    level.draw(post_surf, main_cam)
    player.draw(post_surf, main_cam)

    debug.debug(clock.get_fps())
    debug.debug(main_cam.slide_frame)
    debug.debug(player.offscreen_direction)
    debug.debug(main_cam.x, main_cam.y)
    debug.draw(post_surf)

    if pygame.K_f in events.keys.held_keys:
        screen_update(2)
    else:
        screen_update(60)

    if events.quit_program:
        break
