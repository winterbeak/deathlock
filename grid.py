import pygame

import graphics
import constants as const

TILE_W = 20
TILE_H = 20

# TILE TYPES
VOID = 0
EMPTY = 1
WALL = 2
SPIKE_EMIT_LEFT = 3
SPIKE_EMIT_UP = 4
SPIKE_EMIT_RIGHT = 5
SPIKE_EMIT_DOWN = 6
SPIKE_LEFT = 7
SPIKE_UP = 8
SPIKE_RIGHT = 9
SPIKE_DOWN = 10
CHECKPOINT_ZONE = [11, 12, 13]
MAX_CHECKPOINTS = 3


spike_box_left = graphics.load_image("punch_box", 2)
spike_box_up = pygame.transform.rotate(spike_box_left, -90)
spike_box_right = pygame.transform.rotate(spike_box_left, 180)
spike_box_down = pygame.transform.rotate(spike_box_left, 90)


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
    WIDTH = 25  # the amount of tiles across the room
    HEIGHT = 25
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

        self.grid = [[EMPTY for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

        self.checkpoints = []

    def out_of_bounds(self, rel_col, rel_row):
        """returns whether or not a tile is outside of the grid"""
        if 0 <= rel_col <= self.WIDTH:
            if 0 <= rel_row <= self.HEIGHT:
                return False

        return True

    def change_point(self, rel_col, rel_row, kind):
        """changes a single tile

        the tiles changed are relative to the current room,
        not the entire level
        """
        if not self.out_of_bounds(rel_col, rel_row):
            self.grid[rel_col][rel_row] = kind

            # Adds spike sensors to the spiked blocks
            if kind == SPIKE_EMIT_LEFT:
                self.change_point(rel_col - 1, rel_row, SPIKE_LEFT)
            elif kind == SPIKE_EMIT_UP:
                self.change_point(rel_col, rel_row - 1, SPIKE_UP)
            elif kind == SPIKE_EMIT_RIGHT:
                self.change_point(rel_col + 1, rel_row, SPIKE_RIGHT)
            elif kind == SPIKE_EMIT_DOWN:
                self.change_point(rel_col, rel_row + 1, SPIKE_DOWN)

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

    def add_checkpoint(self, rel_col, rel_row):
        """note: the checkpoint will stay relative until
        the room is added to a level"""
        self.checkpoints.append([rel_col, rel_row])

    def tile_at(self, rel_col, rel_row):
        """returns the tile type at a certain position
        all tiles out of bounds return VOID"""
        if not self.out_of_bounds(rel_col, rel_row):
            return self.grid[rel_col][rel_row]

        return VOID

    def is_spike(self, rel_col, rel_row):
        tile = self.tile_at(rel_col, rel_row)
        if tile == SPIKE_LEFT:
            return True
        if tile == SPIKE_UP:
            return True
        if tile == SPIKE_RIGHT:
            return True
        if tile == SPIKE_DOWN:
            return True

        return False

    def is_checkpoint_zone(self, rel_col, rel_row):
        tile = self.tile_at(rel_col, rel_row)
        if tile in CHECKPOINT_ZONE:
            return True

        return False

    def is_solid(self, rel_col, rel_row, void_solid=True):
        """returns whether a tile is solid or not"""
        tile = self.tile_at(rel_col, rel_row)
        if tile == EMPTY:
            return False

        if not void_solid and tile == VOID:
            return False

        if tile == SPIKE_LEFT:
            return False
        if tile == SPIKE_UP:
            return False
        if tile == SPIKE_RIGHT:
            return False
        if tile == SPIKE_DOWN:
            return False

        if tile in CHECKPOINT_ZONE:
            return False

        return True

    def draw(self, surf, camera):
        """draws the entire stage"""
        for rel_row in range(self.HEIGHT):
            for rel_col in range(self.WIDTH):
                col = self.column * self.WIDTH + rel_col
                row = self.row * self.HEIGHT + rel_row
                x = col * TILE_W - camera.x
                y = row * TILE_H - camera.y
                rect = (x, y, TILE_W, TILE_H)

                if self.tile_at(rel_col, rel_row) == WALL:
                    pygame.draw.rect(surf, const.BLACK, rect)

                elif self.tile_at(rel_col, rel_row) == SPIKE_EMIT_LEFT:
                    surf.blit(spike_box_left, (x, y))

                elif self.tile_at(rel_col, rel_row) == SPIKE_EMIT_UP:
                    surf.blit(spike_box_up, (x, y))

                elif self.tile_at(rel_col, rel_row) == SPIKE_EMIT_RIGHT:
                    surf.blit(spike_box_right, (x, y))

                elif self.tile_at(rel_col, rel_row) == SPIKE_EMIT_DOWN:
                    surf.blit(spike_box_down, (x, y))

                # # Draws checkpoint zones, for debugging purposes.
                # elif self.tile_at(rel_col, rel_row) == CHECKPOINT_ZONE[0]:
                #     pygame.draw.rect(surf, const.LIGHT_BLUE, rect)
                #
                # elif self.tile_at(rel_col, rel_row) == CHECKPOINT_ZONE[1]:
                #     pygame.draw.rect(surf, const.LIGHT_GREEN, rect)
                #
                # elif self.tile_at(rel_col, rel_row) == CHECKPOINT_ZONE[2]:
                #     pygame.draw.rect(surf, const.LIGHT_MAGENTA, rect)


class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.room_grid = [[Room() for _ in range(height)] for _ in range(width)]
        self.active_row = 0
        self.active_column = 0
        self.previous_row = 0
        self.previous_column = 0

        self.rightmost_tile = width * Room.WIDTH - 1
        self.bottommost_tile = height * Room.HEIGHT - 1

    def draw(self, surf, camera):
        if camera.sliding:
            self.draw_room(surf, camera, self.previous_column, self.previous_row)

        self.draw_room(surf, camera, self.active_column, self.active_row)

    def draw_room(self, surf, camera, col, row):
        if not self.out_of_bounds_room(col, row):
            self.room_grid[col][row].draw(surf, camera)

    def out_of_bounds_room(self, col, row):
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
            room_col = col // Room.WIDTH
            room_row = row // Room.HEIGHT
            rel_col = col % Room.WIDTH
            rel_row = row % Room.HEIGHT

            room = self.room_grid[room_col][room_row]
            return room.tile_at(rel_col, rel_row)

        return VOID

    def is_solid(self, col, row, void_solid):
        if not self.out_of_bounds_tile(col, row):
            room_col = col // Room.WIDTH
            room_row = row // Room.HEIGHT

            if void_solid:
                if room_col != self.active_column or room_row != self.active_row:
                    return True

            rel_col = col % Room.WIDTH
            rel_row = row % Room.HEIGHT

            room = self.room_grid[room_col][room_row]
            return room.is_solid(rel_col, rel_row, void_solid)

        if void_solid:
            return True

        return False

    def is_spike(self, col, row):
        if not self.out_of_bounds_tile(col, row):
            room_col = col // Room.WIDTH
            room_row = row // Room.HEIGHT
            rel_col = col % Room.WIDTH
            rel_row = row % Room.HEIGHT

            room = self.room_grid[room_col][room_row]
            return room.is_spike(rel_col, rel_row)

        return False

    def collide_vert(self, x, y1, y2, void_solid):
        col = col_at(x)
        start_row = row_at(y1)
        end_row = row_at(y2)
        for row in range(start_row, end_row + 1):
            if self.is_solid(col, row, void_solid):
                return True

        return False

    def collide_horiz(self, x1, x2, y, void_solid):
        start_col = col_at(x1)
        end_col = col_at(x2)
        row = row_at(y)
        for col in range(start_col, end_col + 1):
            if self.is_solid(col, row, void_solid):
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

    def add_room(self, room, column, row):
        room.column = column
        room.row = row
        room.leftmost_tile = column * room.WIDTH
        room.topmost_tile = row * room.HEIGHT
        room.rightmost_tile = room.leftmost_tile + room.WIDTH - 1
        room.bottommost_tile = room.topmost_tile + room.HEIGHT - 1

        room.x = column * room.PIXEL_W
        room.y = row * room.PIXEL_H

        for checkpoint in room.checkpoints:
            checkpoint[0] += room.leftmost_tile
            checkpoint[1] += room.topmost_tile

        self.room_grid[room.column][room.row] = room

    def current_center_x(self):
        return self.active_column * Room.PIXEL_W + (Room.PIXEL_W // 2)

    def current_center_y(self):
        return self.active_row * Room.PIXEL_H + (Room.PIXEL_H // 2)
