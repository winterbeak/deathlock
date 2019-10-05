import pygame
import constants as const

TILE_W = 10
TILE_H = 10

# TILE TYPES
VOID = 0
EMPTY = 1
WALL = 2


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


class Grid:
    """the grid where all the tiles in the level are placed"""
    GRID_W = 50  # the amount of tiles across the grid
    GRID_H = 50
    PIXEL_W = GRID_W * TILE_W
    PIXEL_H = GRID_H * TILE_H

    def __init__(self, column, row):
        self.column = column
        self.row = row
        self.leftmost_tile = column * self.GRID_W
        self.topmost_tile = row * self.GRID_H
        self.rightmost_tile = self.leftmost_tile + self.GRID_W - 1
        self.bottommost_tile = self.topmost_tile + self.GRID_H - 1

        self.x = column * self.PIXEL_W
        self.y = row * self.PIXEL_H

        self.grid = [[EMPTY for _ in range(self.GRID_H)] for _ in range(self.GRID_W)]

    def out_of_bounds(self, rel_col, rel_row):
        """returns whether or not a tile is outside of the grid"""
        if 0 <= rel_col <= self.GRID_W:
            if 0 <= rel_row <= self.GRID_H:
                return False

        return True

    def change_point(self, rel_col, rel_row, kind):
        """changes a rectangle of tiles

        the tiles changed are relative to the current grid,
        not the entire level
        """
        if not self.out_of_bounds(rel_col, rel_row):
            self.grid[rel_col][rel_row] = kind
        else:
            print("change_point() tried to add a tile out of bounds")

    def change_rect(self, rel_col, rel_row, w, h, kind):
        """places a rectangle of tiles at the given coordinates

        the tiles changed are relative to the current grid,
        not the entire level
        """
        for col in range(rel_col, rel_col + w):
            for row in range(rel_row, rel_row + h):
                if not self.out_of_bounds(col, row):
                    self.grid[col][row] = kind
                else:
                    print("change_rect() tried to add a tile out of bounds.")

    def tile_at(self, rel_col, rel_row):
        """returns the tile type at a certain position
        all tiles out of bounds return VOID"""
        if not self.out_of_bounds(rel_col, rel_row):
            return self.grid[rel_col][rel_row]

        return VOID

    def is_solid(self, rel_col, rel_row):
        """returns whether a tile is solid or not
        currently, the only non-solid tile is the empty tile"""
        if self.tile_at(rel_col, rel_row) == EMPTY:
            return False

        return True

    def draw(self, surf, camera):
        """draws the entire stage"""
        for rel_row in range(self.GRID_H):
            for rel_col in range(self.GRID_W):
                if self.tile_at(rel_col, rel_row) == WALL:
                    col = self.column * self.GRID_W + rel_col
                    row = self.row * self.GRID_H + rel_row
                    x = col * TILE_W - camera.x
                    y = row * TILE_H - camera.y
                    rect = (x, y, TILE_W, TILE_H)
                    pygame.draw.rect(surf, const.WHITE, rect)


class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_grid = [[Grid(x, y) for y in range(height)] for x in range(width)]
        self.active_row = 0
        self.active_column = 0
        self.previous_row = 0
        self.previous_column = 0

        self.rightmost_tile = width * Grid.GRID_W - 1
        self.bottommost_tile = height * Grid.GRID_H - 1

    def draw(self, surf, camera):
        if camera.slide_frame < camera.SLIDE_LENGTH:
            self.draw_grid(surf, camera, self.previous_column, self.previous_row)

        self.draw_grid(surf, camera, self.active_column, self.active_row)

    def draw_grid(self, surf, camera, col, row):
        if not self.out_of_bounds_grid(col, row):
            self.grid_grid[col][row].draw(surf, camera)

    def out_of_bounds_grid(self, col, row):
        """returns whether a given grid is out of bounds or not"""
        if 0 <= col < self.width:
            if 0 <= row < self.height:
                return False

        return True

    def out_of_bounds_tile(self, col, row):
        """returns whether a given tile is out of bounds or not"""
        if 0 <= col <= self.rightmost_tile:
            if 0 <= row <= self.bottommost_tile:
                return False

        return True

    def tile_at(self, col, row):
        if not self.out_of_bounds_tile(col, row):
            grid_col = col // Grid.GRID_W
            grid_row = row // Grid.GRID_H
            rel_col = col % Grid.GRID_W
            rel_row = row % Grid.GRID_H

            grid = self.grid_grid[grid_col][grid_row]
            return grid.tile_at(rel_col, rel_row)

        return VOID

    def collide_vert(self, x, y1, y2, screen_edge):
        col = col_at(x)
        start_row = row_at(y1)
        end_row = row_at(y2)
        for row in range(start_row, end_row + 1):
            tile = self.tile_at(col, row)
            if screen_edge and tile != EMPTY:
                return True
            elif not screen_edge and (tile != EMPTY and tile != VOID):
                return True

        return False

    def collide_horiz(self, x1, x2, y, screen_edge):
        start_col = col_at(x1)
        end_col = col_at(x2)
        row = row_at(y)
        for col in range(start_col, end_col + 1):
            tile = self.tile_at(col, row)
            if screen_edge and tile != EMPTY:
                return True
            elif not screen_edge and (tile != EMPTY and tile != VOID):
                return True

        return False

    def change_room(self, direction):
        self.previous_column = self.active_column
        self.previous_row = self.active_row

        if direction == const.LEFT:
            self.active_column -= 1
        elif direction == const.RIGHT:
            self.active_column += 1
        elif direction == const.UP:
            self.active_row -= 1
        elif direction == const.DOWN:
            self.active_row += 1
        else:
            print("Passed an invalid direction to change_room()!")
