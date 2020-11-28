import pygame

import graphics
import constants as const

TILE_W = 20
TILE_H = 20

# TILE TYPES
VOID = 0
EMPTY = 1
WALL = 2
PUNCHER_EMIT_LEFT = 3
PUNCHER_EMIT_UP = 4
PUNCHER_EMIT_RIGHT = 5
PUNCHER_EMIT_DOWN = 6
PUNCHER_LEFT = 7
PUNCHER_UP = 8
PUNCHER_RIGHT = 9
PUNCHER_DOWN = 10
DEATHLOCK = 11
CHECKPOINT_EMIT_LEFT = 12
CHECKPOINT_EMIT_UP = 13
CHECKPOINT_EMIT_RIGHT = 14
CHECKPOINT_EMIT_DOWN = 15
CHECKPOINT_RAY_VERT = 16
CHECKPOINT_RAY_HORIZ = 17

PUNCHER_EMITS = [PUNCHER_EMIT_LEFT, PUNCHER_EMIT_UP,
                 PUNCHER_EMIT_DOWN, PUNCHER_EMIT_RIGHT]
PUNCHERS = [PUNCHER_LEFT, PUNCHER_UP, PUNCHER_RIGHT, PUNCHER_DOWN]
SOLIDS = [WALL] + PUNCHER_EMITS
CHECKPOINT_EMITS = [CHECKPOINT_EMIT_LEFT, CHECKPOINT_EMIT_UP,
                    CHECKPOINT_EMIT_DOWN, CHECKPOINT_EMIT_RIGHT]


punch_box_left = graphics.load_image("punch_box", 2)
punch_box_up = pygame.transform.rotate(punch_box_left, -90)
punch_box_right = pygame.transform.rotate(punch_box_left, 180)
punch_box_down = pygame.transform.rotate(punch_box_left, 90)


def col_at(x):
    """returns the tile column at pixel position x"""
    return int(x // TILE_W)


def row_at(y):
    """returns the tile row at pixel position y"""
    return int(y // TILE_H)


def x_of(col, direction=const.LEFT):
    """returns the pixel position x of a column
    choose either the LEFT of the column or the RIGHT of the column"""
    if direction == const.LEFT:
        return col * TILE_W

    elif direction == const.RIGHT:
        return col * TILE_W + TILE_W


def y_of(row, direction=const.UP):
    """returns the pixel position y of a row
    choose either UP of the row or the DOWN of the row"""
    if direction == const.UP:
        return row * TILE_H

    elif direction == const.DOWN:
        return row * TILE_H + TILE_H


class Room:
    """the grid where all the tiles on a single screen are placed"""
    WIDTH = const.SCRN_W // TILE_W  # the amount of tiles across the room
    HEIGHT = const.SCRN_H // TILE_H
    PIXEL_W = WIDTH * TILE_W
    PIXEL_H = HEIGHT * TILE_H

    def __init__(self):
        # These values are all default values.
        # Only once the room is added to a level will they be set.
        self.column = 0
        self.row = 0
        self.leftmost_tile = 0
        self.topmost_tile = 0
        self.rightmost_tile = self.leftmost_tile + self.WIDTH - 1
        self.bottommost_tile = self.topmost_tile + self.HEIGHT - 1

        self.x = 0
        self.y = 0

        self.grid = [[[] for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    def out_of_bounds(self, rel_col, rel_row):
        """returns whether or not a tile is outside of the grid"""
        if 0 <= rel_col < self.WIDTH:
            if 0 <= rel_row < self.HEIGHT:
                return False

        return True

    def change_point(self, rel_col, rel_row, kind):
        """changes a single tile

        the tiles changed are relative to the current room,
        not the entire level
        """
        if not self.out_of_bounds(rel_col, rel_row):
            self.grid[rel_col][rel_row] = [kind]

            # Adds punch sensors to the punch blocks
            if kind == PUNCHER_EMIT_LEFT:
                self.change_point(rel_col - 1, rel_row, PUNCHER_LEFT)
            elif kind == PUNCHER_EMIT_UP:
                self.change_point(rel_col, rel_row - 1, PUNCHER_UP)
            elif kind == PUNCHER_EMIT_RIGHT:
                self.change_point(rel_col + 1, rel_row, PUNCHER_RIGHT)
            elif kind == PUNCHER_EMIT_DOWN:
                self.change_point(rel_col, rel_row + 1, PUNCHER_DOWN)

        else:
            print("change_point() tried to add a tile out of bounds")

    def change_rect(self, rel_col, rel_row, w, h, kind):
        """places a rectangle of tiles at the given coordinates

        the tiles changed are relative to the current room,
        not the entire level
        """
        for col in range(rel_col, rel_col + w):
            for row in range(rel_row, rel_row + h):
                self.change_point(col, row, kind)

    def tiles_at(self, rel_col, rel_row):
        """returns the tiles at a given point"""
        if not self.out_of_bounds(rel_col, rel_row):
            return self.grid[rel_col][rel_row]

        return [VOID]

    def has_tile(self, kind, rel_col, rel_row):
        """determines if a certain space contains a tile"""
        if not self.out_of_bounds(rel_col, rel_row):
            return kind in self.grid[rel_col][rel_row]

        return kind == VOID

    def has_listed_tile(self, kinds, rel_col, rel_row):
        """determines if a certain space contains any tiles in the list"""
        if not self.out_of_bounds(rel_col, rel_row):
            for kind in kinds:
                if kind in self.grid[rel_col][rel_row]:
                    return True

            return False

        return VOID in kinds

    def is_puncher(self, rel_col, rel_row):
        return self.has_listed_tile(PUNCHERS, rel_col, rel_row)

    def is_empty(self, rel_col, rel_row):
        return not self.tiles_at(rel_col, rel_row)

    def is_solid(self, rel_col, rel_row, deathlock_solid=True, void_solid=True):
        """returns whether a tile is solid or not"""
        if self.is_empty(rel_col, rel_row):
            return False

        if self.has_listed_tile(SOLIDS, rel_col, rel_row):
            return True

        if void_solid and self.has_tile(VOID, rel_col, rel_row):
            return True

        if deathlock_solid and self.has_tile(DEATHLOCK, rel_col, rel_row):
            return True

        return False

    def collide_vert(self, x, y1, y2, deathlock_solid, void_solid):
        col = col_at(x)
        start_row = row_at(y1)
        end_row = row_at(y2)
        for row in range(start_row, end_row + 1):
            if self.is_solid(col, row, deathlock_solid, void_solid):
                return True

        return False

    def collide_horiz(self, x1, x2, y, deathlock_solid, void_solid):
        start_col = col_at(x1)
        end_col = col_at(x2)
        row = row_at(y)
        for col in range(start_col, end_col + 1):
            if self.is_solid(col, row, deathlock_solid, void_solid):
                return True

        return False

    def draw(self, surf, camera):
        """draws the entire stage"""
        for rel_row in range(self.HEIGHT):
            for rel_col in range(self.WIDTH):
                col = self.column * self.WIDTH + rel_col
                row = self.row * self.HEIGHT + rel_row
                x = col * TILE_W - camera.x
                y = row * TILE_H - camera.y
                rect = (x, y, TILE_W, TILE_H)

                if self.has_tile(WALL, rel_col, rel_row):
                    pygame.draw.rect(surf, const.BLACK, rect)

                if self.has_tile(DEATHLOCK, rel_col, rel_row):
                    pygame.draw.rect(surf, const.RED, rect)

                if self.has_tile(PUNCHER_EMIT_LEFT, rel_col, rel_row):
                    surf.blit(punch_box_left, (x, y))

                if self.has_tile(PUNCHER_EMIT_UP, rel_col, rel_row):
                    surf.blit(punch_box_up, (x, y))

                if self.has_tile(PUNCHER_EMIT_RIGHT, rel_col, rel_row):
                    surf.blit(punch_box_right, (x, y))

                if self.has_tile(PUNCHER_EMIT_DOWN, rel_col, rel_row):
                    surf.blit(punch_box_down, (x, y))
