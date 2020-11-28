import pygame

import graphics
import constants as const

TILE_W = 20
TILE_H = 20


class Tile:
    def __init__(self, solid):
        self.solid = solid


class Void(Tile):
    def __init__(self):
        super().__init__(True)


class Wall(Tile):
    def __init__(self):
        super().__init__(True)


class PunchBox(Tile):
    def __init__(self, direction):
        super().__init__(True)
        self.direction = direction


class PunchZone(Tile):
    def __init__(self, direction):
        super().__init__(False)
        self.direction = direction


class Deathlock(Tile):
    def __init__(self):
        super().__init__(False)


class Checkpoint(Tile):
    def __init__(self, direction, col, row):
        super().__init__(False)
        self.direction = direction
        self.col = col
        self.row = row


class CheckpointRay(Tile):
    def __init__(self, checkpoint, orientation):
        super().__init__(False)

        self.orientation = orientation
        self.checkpoint = checkpoint


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

    def out_of_bounds(self, col, row):
        """returns whether or not a tile is outside of the grid"""
        if 0 <= col < self.WIDTH:
            if 0 <= row < self.HEIGHT:
                return False

        return True

    def add_tile(self, col, row, tile):
        if not self.out_of_bounds(col, row):
            self.grid[col][row].append(tile)

        else:
            print("add_tile() tried to add a tile out of bounds")

    def clear_point(self, col, row):
        if not self.out_of_bounds(col, row):
            self.grid[col][row] = []

        else:
            print("clear_point() tried to add a tile out of bounds")

    def add_rect(self, col, row, w, h, constructor):
        """places a rectangle of tiles at the given coordinates

        the tiles changed are relative to the current room,
        not the entire level
        """
        for col in range(col, col + w):
            for row in range(row, row + h):
                self.add_tile(col, row, constructor())

    def add_checkpoint(self, col, row, direction):
        self.add_tile(col, row, Checkpoint(direction, col, row))

    def tiles_at(self, col, row):
        """returns the tiles at a given point"""
        if not self.out_of_bounds(col, row):
            return self.grid[col][row]

        return [Void()]

    def has_tile(self, type_, col, row):
        """determines if a certain space contains a tile"""
        if not self.out_of_bounds(col, row):
            for tile in self.tiles_at(col, row):
                if type(tile) == type_:
                    return True
            return False

        return type_ == Void

    def get_tile(self, type_, col, row):
        """gets the first tile with a given type on this space"""
        for tile in self.tiles_at(col, row):
            if type(tile) == type_:
                return tile

        raise("There is not tile of type %s there!" % str(type_))

    def has_listed_tile(self, types, col, row):
        """determines if a certain space contains any tiles in the list"""
        for type_ in types:
            if self.has_tile(type_, col, row):
                return True

        return False

    def is_empty(self, col, row):
        return not self.tiles_at(col, row)

    def has_solid(self, col, row):
        """returns whether a tile is solid or not"""
        for tile in self.tiles_at(col, row):
            if tile.solid:
                return True

        return False

    def emit(self):
        """Emits PunchZones from all PunchBoxes"""
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in self.tiles_at(col, row):
                    if type(tile) == PunchBox:
                        self.emit_punch_zone(col, row, tile)

                    elif type(tile) == Checkpoint:
                        self.emit_checkpoint_ray(col, row, tile)

    def emit_punch_zone(self, col, row, tile):
        if tile.direction == const.LEFT:
            self.add_tile(col - 1, row, PunchZone(const.LEFT))
        elif tile.direction == const.UP:
            self.add_tile(col, row - 1, PunchZone(const.UP))
        elif tile.direction == const.RIGHT:
            self.add_tile(col + 1, row, PunchZone(const.RIGHT))
        elif tile.direction == const.DOWN:
            self.add_tile(col, row + 1, PunchZone(const.DOWN))

    def emit_checkpoint_ray(self, col, row, tile):
        if tile.direction == const.LEFT:
            ray_col = col
            while not self.stops_checkpoint_ray(ray_col, row):
                self.add_tile(ray_col, row, CheckpointRay(tile, const.HORIZ))
                ray_col -= 1
        elif tile.direction == const.RIGHT:
            ray_col = col
            while not self.stops_checkpoint_ray(ray_col, row):
                self.add_tile(ray_col, row, CheckpointRay(tile, const.HORIZ))
                ray_col += 1
        elif tile.direction == const.UP:
            ray_row = row
            while not self.stops_checkpoint_ray(col, ray_row):
                self.add_tile(col, ray_row, CheckpointRay(tile, const.VERT))
                ray_row -= 1
        elif tile.direction == const.DOWN:
            ray_row = row
            while not self.stops_checkpoint_ray(col, ray_row):
                self.add_tile(col, ray_row, CheckpointRay(tile, const.VERT))
                ray_row += 1

    def stops_checkpoint_ray(self, col, row):
        if self.has_solid(col, row):
            return True
        if self.has_tile(Void, col, row):
            return True
        return False

    def collide_vert(self, x, y1, y2, collide_deathlock):
        col = col_at(x)
        start_row = row_at(y1)
        end_row = row_at(y2)
        for row in range(start_row, end_row + 1):
            if collide_deathlock and self.has_tile(Deathlock, col, row):
                return True
            if self.has_solid(col, row):
                return True

        return False

    def collide_horiz(self, x1, x2, y, collide_deathlock):
        start_col = col_at(x1)
        end_col = col_at(x2)
        row = row_at(y)
        for col in range(start_col, end_col + 1):
            if collide_deathlock and self.has_tile(Deathlock, col, row):
                return True
            if self.has_solid(col, row):
                return True

        return False

    def draw(self, surf, camera):
        """draws the entire stage"""
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.is_empty(col, row):
                    continue

                full_col = self.column * self.WIDTH + col
                full_row = self.row * self.HEIGHT + row
                x = full_col * TILE_W - camera.x
                y = full_row * TILE_H - camera.y
                rect = (x, y, TILE_W, TILE_H)

                if self.has_tile(Wall, col, row):
                    pygame.draw.rect(surf, const.BLACK, rect)

                if self.has_tile(Deathlock, col, row):
                    pygame.draw.rect(surf, const.RED, rect)

                if self.has_tile(PunchBox, col, row):
                    punch_box = self.get_tile(PunchBox, col, row)
                    if punch_box.direction == const.LEFT:
                        surf.blit(punch_box_left, (x, y))
                    elif punch_box.direction == const.UP:
                        surf.blit(punch_box_up, (x, y))
                    elif punch_box.direction == const.RIGHT:
                        surf.blit(punch_box_right, (x, y))
                    elif punch_box.direction == const.DOWN:
                        surf.blit(punch_box_down, (x, y))

                if self.has_tile(Checkpoint, col, row):
                    checkpoint_pos = (x + TILE_W // 2, y + TILE_H // 2)
                    pygame.draw.circle(surf, const.GREEN, checkpoint_pos, 10)

                if self.has_tile(CheckpointRay, col, row):
                    tile = self.get_tile(CheckpointRay, col, row)
                    if tile.orientation == const.HORIZ:
                        ray_rect = (x, y + TILE_H // 3, TILE_W, TILE_H // 3)
                        pygame.draw.rect(surf, const.GREEN, ray_rect)
                    elif tile.orientation == const.VERT:
                        ray_rect = (x + TILE_W // 3, y, TILE_W // 3, TILE_H)
                        pygame.draw.rect(surf, const.GREEN, ray_rect)
