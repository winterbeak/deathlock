import pygame
import constants as const

import grid


class CollisionEntity:
    CHECK_STEPS = 4

    def __init__(self, level, width, height, x=0, y=0, extend_x=0, extend_y=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.x_vel = 0.0
        self.y_vel = 0.0
        self.x_acc = 0.0
        self.y_acc = 0.0

        self.x_dir = 0
        self.y_dir = 0

        self.extend_x = extend_x
        self.extend_y = extend_y
        self.gridbox = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                  width + extend_x * 2, height + extend_y * 2)

        self.level = level  # reference to the level layout

    def move(self, void_solid=True):
        """moves body based on velocity and acceleration"""
        self.collide_stage(void_solid)

        self.x_vel += self.x_acc
        self.y_vel += self.y_acc

        self.x += self.x_vel
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

        self.goto(self.x, self.y)

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
            self.goto(grid.x_of(col, const.LEFT) - self.width, self.y)
            self.stop_x()

        elif side == const.RIGHT:
            self.goto(grid.x_of(col, const.RIGHT), self.y)
            self.stop_x()

    def snap_y(self, row, side=const.TOP):
        """snaps you to either the top or bottom of a tile"""
        if side == const.TOP:
            self.goto(self.x, grid.y_of(row, const.TOP) - self.height)
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
            right_x = left_x + self.width - 1
            top_y = int(self.y + (diff_y * (step / self.CHECK_STEPS)))
            bottom_y = top_y + self.height - 1

            if dir_y == const.UP:
                if self.level.collide_horiz(left_x, right_x, top_y, void_solid):
                    self.snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self.level.collide_horiz(left_x, right_x, bottom_y, void_solid):
                    self.snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self.x + (diff_x * (step / 4)))
            right_x = left_x + self.width - 1
            top_y = self.y
            bottom_y = top_y + self.height - 1

            if dir_x == const.LEFT:
                if self.level.collide_vert(left_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(left_x), const.RIGHT)

            elif dir_x == const.RIGHT:
                if self.level.collide_vert(right_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(right_x), const.LEFT)

    def against_wall(self, void_solid=True):
        top_y = self.y
        bottom_y = top_y + self.height - 1

        if self.x_dir == const.LEFT:
            x = self.x - 1
            return self.level.collide_vert(x, top_y, bottom_y, void_solid)

        elif self.x_dir == const.RIGHT:
            x = self.x + self.width
            return self.level.collide_vert(x, top_y, bottom_y, void_solid)

    def against_floor(self, screen_edge):
        x1 = self.x
        x2 = x1 + self.width - 1
        y = self.y + self.height
        if self.level.collide_horiz(x1, x2, y, screen_edge):
            return True
        else:
            return False
