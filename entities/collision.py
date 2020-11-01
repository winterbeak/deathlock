import pygame
import constants as const

import sound
import grid
import punchers


class Collision:
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
        x = int(value)
        self._x = x
        self._gridbox.x = x
        self._hitbox.x = x - self._extend_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        y = int(value)
        self._y = y
        self._gridbox.y = y
        self._hitbox.y = y - self._extend_y

    def update(self):
        self._collide_stage()
        self._update_kinematics()
        self._update_direction()

    def _update_kinematics(self):
        self.x_vel += self.x_acc
        self.y_vel += self.y_acc

        self.x += self.x_vel
        self.y += self.y_vel

    def _update_direction(self):
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

    def _against_floor(self):
        x1 = self._x
        x2 = x1 + self._width - 1
        y = self._y + self._height
        return self._level.collide_horiz(x1, x2, y, self.collide_void)

    def draw_gridbox(self, surface, cam, color=const.RED):
        pygame.draw.rect(surface, color, cam.move_rect(self._gridbox))

    def draw_hitbox(self, surface, cam, color=const.BLUE):
        pygame.draw.rect(surface, color, cam.move_rect(self._hitbox))


class GravityCollision(Collision):
    def __init__(self, level, width, height, terminal_velocity,
                 x=0, y=0, extend_x=0, extend_y=0):
        super().__init__(level, width, height, x, y, extend_x, extend_y)
        self._terminal_velocity = terminal_velocity

    @property
    def grounded(self):
        if self.y_vel < 0:
            return False
        return self._against_floor()

    def update(self):
        if not self.grounded:
            self.y_acc = const.GRAVITY
        super().update()
        self.y_vel = min(self.y_vel, self._terminal_velocity)


class PunchableGravityCollision(GravityCollision):
    HIT_SOUNDS = sound.load_numbers("hit%i", 3)
    INVULN_LENGTH = 10

    def __init__(self, level, width, height, terminal_velocity,
                 x=0, y=0, extend_x=0, extend_y=0):
        super().__init__(level, width, height, terminal_velocity,
                         x, y, extend_x, extend_y)

        self.invuln_frames = 0
        self.puncher_x_vel = 0
        self.puncher_deceleration = 0.5

    def update(self):
        super().update()
        self.collide_punchers()

    def _stop_x(self):
        super()._stop_x()
        self.puncher_x_vel = 0

    def _next_x(self):
        return super()._next_x() + self.puncher_x_vel

    def _update_kinematics(self):
        super()._update_kinematics()
        self._update_puncher_vel()
        self.x += self.puncher_x_vel

    def _update_puncher_vel(self):
        if self.grounded:
            if self.puncher_x_vel < 0:
                self.puncher_x_vel += self.puncher_deceleration
                if self.puncher_x_vel > 0:
                    self.puncher_x_vel = 0

            elif self.puncher_x_vel > 0:
                self.puncher_x_vel -= self.puncher_deceleration
                if self.puncher_x_vel < 0:
                    self.puncher_x_vel = 0

    def _get_hit(self):
        self.invuln_frames = self.INVULN_LENGTH
        self.HIT_SOUNDS.play_random()

    def collide_punchers(self):
        if not self.invuln_frames:
            center_col = grid.col_at(self.x + (self._width // 2))
            center_row = grid.row_at(self.y + (self._height // 2))
            tile = self._level.tile_at(center_col, center_row)
            if tile == grid.PUNCHER_LEFT:
                self._get_hit()
                punchers.add(center_col, center_row, const.LEFT)
                self.puncher_x_vel = -7

                if self.x_vel > 0:
                    self.x_vel = 0

            elif tile == grid.PUNCHER_UP:
                self._get_hit()
                punchers.add(center_col, center_row, const.UP)
                self.y_vel = -12

            elif tile == grid.PUNCHER_RIGHT:
                self._get_hit()
                punchers.add(center_col, center_row, const.RIGHT)
                self.puncher_x_vel = 7

                if self.x_vel < 0:
                    self.x_vel = 0

            elif tile == grid.PUNCHER_DOWN:
                self._get_hit()
                punchers.add(center_col, center_row, const.DOWN)
                self.y_vel = 7

        elif self.invuln_frames:
            self.invuln_frames -= 1
