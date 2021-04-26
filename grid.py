import os
import pygame

import graphics
import constants as const

TILE_W = 20
TILE_H = 20


def level_path(name):
    return os.path.join("levels", name)


def id_of(tiles):
    """These ids are only used for writing and reading levels."""
    if len(tiles) == 0:
        return 0

    tile = tiles[0]
    if type(tile) == Wall:
        return 1
    if type(tile) == Deathlock:
        return 2
    if type(tile) == PunchBox:
        if tile.direction == const.LEFT:
            return 3
        if tile.direction == const.UP:
            return 4
        if tile.direction == const.RIGHT:
            return 5
        if tile.direction == const.DOWN:
            return 6
    if type(tile) == Checkpoint:
        if tile.direction == const.LEFT:
            return 7
        if tile.direction == const.UP:
            return 8
        if tile.direction == const.RIGHT:
            return 9
        if tile.direction == const.DOWN:
            return 10
    if type(tile) == PlayerSpawn:
        return 11
    if type(tile) == PlayerGoal:
        return 12
    return 0


class Tile:
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self):
        pass


class Void(Tile):
    SOLID = True
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self):
        super().__init__()


class Wall(Tile):
    SOLID = True
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self):
        super().__init__()


class PunchBox(Tile):
    SOLID = True
    EMITTED = False
    DRAWN_STATICALLY = False

    def __init__(self, direction):
        super().__init__()
        self.direction = direction


class PunchZone(Tile):
    SOLID = False
    EMITTED = True
    DRAWN_STATICALLY = True

    def __init__(self, direction):
        super().__init__()
        self.direction = direction


class Deathlock(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self):
        super().__init__()


class Checkpoint(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = False

    def __init__(self, direction, col, row):
        super().__init__()
        self.direction = direction
        self.col = col
        self.row = row
        self.active = False


class CheckpointRay(Tile):
    SOLID = False
    EMITTED = True
    DRAWN_STATICALLY = False

    def __init__(self, checkpoint, orientation):
        super().__init__()

        self.orientation = orientation
        self.checkpoint = checkpoint


class PlayerSpawn(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self, col, row):
        super().__init__()
        self.col = col
        self.row = row


class PlayerGoal(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self, col, row):
        super().__init__()
        self.col = col
        self.row = row


class PlayerGoalZone(Tile):
    SOLID = False
    EMITTED = True
    DRAWN_STATICALLY = True

    def __init__(self):
        super().__init__()


punch_box_left = graphics.load_image("punch_box", 2)
punch_box_left.set_colorkey(const.TRANSPARENT)
punch_box_up = pygame.transform.rotate(punch_box_left, -90)
punch_box_right = pygame.transform.rotate(punch_box_left, 180)
punch_box_down = pygame.transform.rotate(punch_box_left, 90)
punch_box_gradient = graphics.load_image("punch_box_gradient", 1)
punch_box_glow = graphics.load_image("punch_box_glow", 1)

checkpoint_activated = graphics.load_image("checkpoint_activated", 2)
checkpoint_activated.set_colorkey(const.TRANSPARENT)
checkpoint_deactivated = graphics.load_image("checkpoint_deactivated", 2)
checkpoint_deactivated.set_colorkey(const.TRANSPARENT)
checkpoint_gradient = graphics.load_image("checkpoint_gradient", 1)
checkpoint_glow = graphics.load_image("checkpoint_glow", 1)

checkpoint_ray_horiz_gradient = graphics.load_image("checkpoint_ray_horiz_gradient", 1)
checkpoint_ray_vert_gradient = pygame.transform.rotate(checkpoint_ray_horiz_gradient, 90)
checkpoint_ray_horiz_glow = graphics.load_image("checkpoint_ray_horiz_glow", 1)
checkpoint_ray_vert_glow = pygame.transform.rotate(checkpoint_ray_horiz_glow, 90)

player_goal_glow = graphics.load_image("player_goal_glow", 1)
player_goal_gradient = graphics.load_image("player_goal_gradient", 1)

deathlock_glow = graphics.load_image("deathlock_glow", 1)
deathlock_gradient = graphics.load_image("deathlock_gradient", 1)

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


def center_x_of(col):
    return x_of(col) + (TILE_W / 2)


def center_y_of(row):
    return y_of(row) + (TILE_H / 2)


def draw_glow_centered(surf, glow, center_x, center_y):
    glow_x = int(center_x - (glow.get_width() / 2))
    glow_y = int(center_y - (glow.get_height() / 2))
    surf.blit(glow, (glow_x, glow_y), special_flags=pygame.BLEND_MAX)


class Room:
    """the grid where all the tiles on a single screen are placed"""
    WIDTH = const.SCRN_W // TILE_W  # the amount of tiles across the room
    HEIGHT = const.SCRN_H // TILE_H
    PIXEL_W = WIDTH * TILE_W
    PIXEL_H = HEIGHT * TILE_H

    def __init__(self, name):
        """name is the name of the file in the levels folder"""
        self.grid = [[[] for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

        self.player_spawn = PlayerSpawn(0, 0)
        self.player_goal = PlayerGoal(0, 0)
        self.grid[0][0].append(self.player_spawn)
        self.grid[0][0].append(self.player_goal)

        self.name = name
        self.load()

    def out_of_bounds(self, col, row):
        """returns whether or not a tile is outside of the grid"""
        if 0 <= col < self.WIDTH:
            if 0 <= row < self.HEIGHT:
                return False

        return True

    def clear(self):
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                self.clear_point(col, row)

    def add_tile(self, col, row, tile):
        if not self.out_of_bounds(col, row):
            self.grid[col][row].append(tile)

        else:
            print("add_tile() tried to add a tile out of bounds")

    def clear_point(self, col, row):
        if not self.out_of_bounds(col, row):
            new_tile = []

            # Spawn and goal shouldn't be erasable
            if self.has_tile(PlayerSpawn, col, row):
                spawn = self.get_tile(PlayerSpawn, col, row)
                new_tile.append(spawn)
            if self.has_tile(PlayerGoal, col, row):
                goal = self.get_tile(PlayerGoal, col, row)
                new_tile.append(goal)

            self.grid[col][row] = new_tile

        else:
            print("clear_point() tried to clear a tile out of bounds")

    def add_rect(self, col, row, w, h, constructor):
        """places a rectangle of tiles at the given coordinates

        the tiles changed are relative to the current room,
        not the entire level
        """
        for col_index in range(col, col + w):
            for row_index in range(row, row + h):
                self.add_tile(col_index, row_index, constructor())

    def clear_rect(self, col, row, w, h):
        for col_index in range(col, col + w):
            for row_index in range(row, row + h):
                self.clear_point(col_index, row_index)

    def add_checkpoint(self, col, row, direction):
        self.add_tile(col, row, Checkpoint(direction, col, row))

    def move_player_spawn(self, col, row):
        # Remove old spawn
        old_col = self.player_spawn.col
        old_row = self.player_spawn.row
        if self.player_spawn in self.grid[old_col][old_row]:
            self.grid[old_col][old_row].remove(self.player_spawn)

        # Place new spawn
        self.player_spawn = PlayerSpawn(col, row)
        self.add_tile(col, row, self.player_spawn)

    def move_player_goal(self, col, row):
        # Remove old goal
        old_col = self.player_goal.col
        old_row = self.player_goal.row
        if self.player_goal in self.grid[old_col][old_row]:
            self.grid[old_col][old_row].remove(self.player_goal)

        # Place new goal
        self.player_goal = PlayerGoal(col, row)
        self.add_tile(col, row, self.player_goal)

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
            if tile.SOLID:
                return True

        return False

    def emit(self):
        """Emits PunchZones from all PunchBoxes and CheckpointRays from
        all Checkpoints"""
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in self.tiles_at(col, row):
                    if type(tile) == PunchBox:
                        self.emit_punch_zone(col, row, tile)

                    elif type(tile) == Checkpoint:
                        self.emit_checkpoint_ray(col, row, tile)

                    elif type(tile) == PlayerGoal:
                        self.emit_player_goal_zone(col, row)

    def unemit(self):
        """Emits PunchZones from all PunchBoxes"""
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in reversed(self.tiles_at(col, row)):
                    if tile.EMITTED:
                        self.tiles_at(col, row).remove(tile)

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

    def emit_player_goal_zone(self, col, row):
        # Place goal zones in a 3x3 area around the goal tile
        for x in range(col - 1, col + 2):
            for y in range(row - 1, row + 2):
                if not self.out_of_bounds(x, y):
                    self.add_tile(x, y, PlayerGoalZone())

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

    def _shift_location_tiles(self, col_change, row_change):
        """Change the position of all things that store their own position.

        Currently, that would only be checkpoints and spawns."""
        self.player_spawn.col += col_change
        self.player_spawn.row += row_change
        self.player_goal.col += col_change
        self.player_goal.row += row_change
        for col in range(0, self.WIDTH):
            for row in range(0, self.HEIGHT):
                for tile in self.grid[col][row]:
                    if type(tile) == Checkpoint:
                        tile.col += col_change
                        tile.row += row_change

    # Note: these shift functions currently don't erase the very last row/col
    # so it just becomes a "copy".  This is fine for my purposes since all my
    # levels never directly touch edge.
    def shift_left(self):
        for col in range(0, self.WIDTH - 1):
            for row in range(0, self.HEIGHT):
                self.grid[col][row] = self.grid[col + 1][row]
        self._shift_location_tiles(-1, 0)

    def shift_right(self):
        for col in range(self.WIDTH - 1, 0, -1):
            for row in range(0, self.HEIGHT):
                self.grid[col][row] = self.grid[col - 1][row]
        self._shift_location_tiles(1, 0)

    def shift_up(self):
        for row in range(0, self.HEIGHT - 1):
            for col in range(0, self.WIDTH):
                self.grid[col][row] = self.grid[col][row + 1]
        self._shift_location_tiles(0, -1)

    def shift_down(self):
        for row in range(self.HEIGHT - 1, 0, -1):
            for col in range(0, self.WIDTH):
                self.grid[col][row] = self.grid[col][row - 1]
        self._shift_location_tiles(0, 1)

    def draw_tile_at(self, surf, camera, col, row, transparent_background=True):
        x = col * TILE_W - int(camera.x)
        y = row * TILE_H - int(camera.y)
        rect = (x, y, TILE_W, TILE_H)

        if transparent_background:
            pygame.draw.rect(surf, const.TRANSPARENT, rect)

        if self.has_tile(Wall, col, row):
            pygame.draw.rect(surf, const.BLACK, rect)

        elif self.has_tile(PlayerSpawn, col, row):
            pygame.draw.rect(surf, const.YELLOW, rect)

        elif self.has_tile(Deathlock, col, row):
            pygame.draw.rect(surf, (109, 112, 255), rect)

        elif self.has_tile(PunchBox, col, row):
            punch_box = self.get_tile(PunchBox, col, row)
            if punch_box.direction == const.LEFT:
                surf.blit(punch_box_left, (x, y))
            elif punch_box.direction == const.UP:
                surf.blit(punch_box_up, (x, y))
            elif punch_box.direction == const.RIGHT:
                surf.blit(punch_box_right, (x, y))
            elif punch_box.direction == const.DOWN:
                surf.blit(punch_box_down, (x, y))

        elif self.has_tile(Checkpoint, col, row):
            checkpoint = self.get_tile(Checkpoint, col, row)
            if checkpoint.active:
                surf.blit(checkpoint_activated, (x, y))
            else:
                surf.blit(checkpoint_deactivated, (x, y))

        elif self.has_tile(CheckpointRay, col, row):
            tile = self.get_tile(CheckpointRay, col, row)
            if tile.checkpoint.active:
                color = (66, 150, 66)
            else:
                color = (81, 255, 113)
            if tile.orientation == const.HORIZ:
                ray_rect = (x, y + TILE_H // 3, TILE_W, TILE_H // 3 + 2)
                pygame.draw.rect(surf, color, ray_rect)
            elif tile.orientation == const.VERT:
                ray_rect = (x + TILE_W // 3, y, TILE_W // 3 + 2, TILE_H)
                pygame.draw.rect(surf, color, ray_rect)

        elif self.has_tile(PlayerGoalZone, col, row):
            pygame.draw.rect(surf, (250, 250, 250), rect)

    def draw_glow_at(self, surf, col, row):
        center_x = center_x_of(col)
        center_y = center_y_of(row)

        if self.has_tile(PunchBox, col, row):
            draw_glow_centered(surf, punch_box_glow, center_x, center_y)
            draw_glow_centered(surf, punch_box_gradient, center_x, center_y)

        elif self.has_tile(Deathlock, col, row):
            draw_glow_centered(surf, deathlock_glow, center_x, center_y)
            draw_glow_centered(surf, deathlock_gradient, center_x, center_y)

        elif self.has_tile(Checkpoint, col, row):
            draw_glow_centered(surf, checkpoint_glow, center_x, center_y)
            draw_glow_centered(surf, checkpoint_gradient, center_x, center_y)

        elif self.has_tile(CheckpointRay, col, row):
            tile = self.get_tile(CheckpointRay, col, row)
            if tile.orientation == const.HORIZ:
                draw_glow_centered(surf, checkpoint_ray_horiz_glow, center_x, center_y)
                draw_glow_centered(surf, checkpoint_ray_horiz_gradient, center_x, center_y)

            elif tile.orientation == const.VERT:
                draw_glow_centered(surf, checkpoint_ray_vert_glow, center_x, center_y)
                draw_glow_centered(surf, checkpoint_ray_vert_gradient, center_x, center_y)

    def draw_goal_glow(self, surf):
        glow_surf = pygame.Surface(surf.get_size())
        for col in range(self.player_goal.col - 1, self.player_goal.col + 2):
            for row in range(self.player_goal.row - 1, self.player_goal.row + 2):
                center_x = center_x_of(col)
                center_y = center_y_of(row)
                glow_x = int(center_x - (player_goal_glow.get_width() / 2))
                glow_y = int(center_y - (player_goal_glow.get_height() / 2))
                glow_surf.blit(player_goal_glow, (glow_x, glow_y), special_flags=pygame.BLEND_MAX)

                gradient_x = int(center_x - (player_goal_gradient.get_width() / 2))
                gradient_y = int(center_y - (player_goal_gradient.get_height() / 2))
                glow_surf.blit(player_goal_gradient, (gradient_x, gradient_y), special_flags=pygame.BLEND_MAX)
        surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    def draw_static(self, surf, camera, transparent_background=True):
        """draws the entire stage"""
        glow_surf = pygame.Surface(surf.get_size())
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                self.draw_glow_at(glow_surf, col, row)
        surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                self.draw_tile_at(surf, camera, col, row, transparent_background)

        self.draw_goal_glow(surf)

    def draw_dynamic(self, surf, camera):
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row] and not self.grid[col][row][0].DRAWN_STATICALLY:
                    self.draw_tile_at(surf, camera, col, row, False)

    def place_tile_from_id(self, col, row, tile_id):
        """These ids are only used for writing and reading levels."""
        if tile_id == 1:
            tile = Wall()
        elif tile_id == 2:
            tile = Deathlock()
        elif tile_id == 3:
            tile = PunchBox(const.LEFT)
        elif tile_id == 4:
            tile = PunchBox(const.UP)
        elif tile_id == 5:
            tile = PunchBox(const.RIGHT)
        elif tile_id == 6:
            tile = PunchBox(const.DOWN)
        elif tile_id == 7:
            tile = Checkpoint(const.LEFT, col, row)
        elif tile_id == 8:
            tile = Checkpoint(const.UP, col, row)
        elif tile_id == 9:
            tile = Checkpoint(const.RIGHT, col, row)
        elif tile_id == 10:
            tile = Checkpoint(const.DOWN, col, row)
        elif tile_id == 11:
            self.move_player_spawn(col, row)
            return
        elif tile_id == 12:
            self.move_player_goal(col, row)
            return
        else:
            return

        self.add_tile(col, row, tile)

    def save(self):
        strings = []
        for row in range(self.HEIGHT):
            row_of_ids = []
            for col in range(self.WIDTH):
                tiles = self.tiles_at(col, row)
                id = id_of(tiles)
                row_of_ids.append(str(id))
            strings.append(" ".join(row_of_ids))
        data = "\n".join(strings)

        with open(level_path(self.name), "w") as file:
            file.write(data)

    def load(self):
        self.clear()

        path = level_path(self.name)
        if not os.path.exists(path):
            return

        with open(path, "r") as file:
            data = file.read()

        for row_index, row in enumerate(data.split("\n")):
            for col_index, tile in enumerate(row.split(" ")):
                self.place_tile_from_id(col_index, row_index, int(tile))

        self.emit()
