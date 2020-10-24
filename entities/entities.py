import pygame
import constants as const

import grid


class CollisionEntity:
    CHECK_STEPS = 4

    def __init__(self, level, width, height, x=0, y=0, extend_x=0, extend_y=0):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        self.x_vel = 0.0
        self.y_vel = 0.0
        self.x_acc = 0.0
        self.y_acc = 0.0

        self._x_dir = 0
        self._y_dir = 0

        self._extend_x = extend_x
        self._extend_y = extend_y
        self._gridbox = pygame.Rect(x, y, width, height)
        self._hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                   width + extend_x * 2, height + extend_y * 2)

        self.collide_void = True

        self._level = level  # reference to the level layout

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._gridbox.x = value
        self._hitbox.x = value - self._extend_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._gridbox.y = value
        self._hitbox.y = value

    def update(self):
        self._collide_stage()

        self.x_vel += self.x_acc
        self.y_vel += self.y_acc

        self._x += self.x_vel
        self._y += self.y_vel

        # Determines direction of movement
        if self.x_vel < 0:
            self._x_dir = const.LEFT
        elif self.x_vel > 0:
            self._x_dir = const.RIGHT
        else:
            self._x_dir = 0

        if self.y_vel < 0:
            self._y_dir = const.UP
        elif self.y_vel > 0:
            self._y_dir = const.DOWN
        else:
            self._y_dir = 0

    def _next_x(self):
        """returns the x position of the body on the next frame"""
        return self._x + self.x_vel + self.x_acc

    def _next_y(self):
        """returns the y position of the body on the next frame"""
        return self._y + self.y_vel + self.y_acc

    def _stop_x(self):
        self._x_dir = 0
        self.x_vel = 0
        self.x_acc = 0

    def _stop_y(self):
        self._y_dir = 0
        self.y_vel = 0
        self.y_acc = 0

    def _snap_x(self, col, side=const.LEFT):
        """snaps you to either the left side or right side of a tile"""
        if side == const.LEFT:
            self.x = grid.x_of(col, const.LEFT) - self._width
            self._stop_x()

        elif side == const.RIGHT:
            self.x = grid.x_of(col, const.RIGHT)
            self._stop_x()

    def _snap_y(self, row, side=const.TOP):
        """snaps you to either the top or bottom of a tile"""
        if side == const.TOP:
            self.y = grid.y_of(row, const.TOP) - self._height
            self._stop_y()

        elif side == const.BOTTOM:
            self.y = grid.y_of(row, const.BOTTOM)
            self._stop_y()

    def _collide_stage(self):
        """checks collision with stage and updates movement accordingly

        if screen_edge is True, then the edge of the screen acts as a wall."""

        for step in range(1, self.CHECK_STEPS + 1):
            diff_x = self._next_x() - self._x
            diff_y = self._next_y() - self._y

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

            left_x = self._x
            right_x = left_x + self._width - 1
            top_y = int(self._y + (diff_y * (step / self.CHECK_STEPS)))
            bottom_y = top_y + self._height - 1

            if dir_y == const.UP:
                if self._level.collide_horiz(left_x, right_x, top_y, self.collide_void):
                    self._snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self._level.collide_horiz(left_x, right_x, bottom_y, self.collide_void):
                    self._snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self._x + (diff_x * (step / 4)))
            right_x = left_x + self._width - 1
            top_y = self._y
            bottom_y = top_y + self._height - 1

            if dir_x == const.LEFT:
                if self._level.collide_vert(left_x, top_y, bottom_y, self.collide_void):
                    self._snap_x(grid.col_at(left_x), const.RIGHT)

            elif dir_x == const.RIGHT:
                if self._level.collide_vert(right_x, top_y, bottom_y, self.collide_void):
                    self._snap_x(grid.col_at(right_x), const.LEFT)

    def _against_wall(self):
        top_y = self._y
        bottom_y = top_y + self._height - 1

        if self._x_dir == const.LEFT:
            x = self._x - 1
            return self._level.collide_vert(x, top_y, bottom_y, self.collide_void)

        elif self._x_dir == const.RIGHT:
            x = self._x + self._width
            return self._level.collide_vert(x, top_y, bottom_y, self.collide_void)

    def _against_floor(self, screen_edge):
        x1 = self._x
        x2 = x1 + self._width - 1
        y = self._y + self._height
        if self._level.collide_horiz(x1, x2, y, screen_edge):
            return True
        else:
            return False
