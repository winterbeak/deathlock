import sound

import math
import os
import pygame

import graphics
import constants as const

import flicker

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
        self.flicker_sequence = flicker.FlickerSequence()


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
        self.flicker_sequence = None

    @property
    def flicker_initiated(self):
        return self.flicker_sequence is not None


class Checkpoint(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = True

    def __init__(self, direction, col, row):
        super().__init__()
        self.direction = direction
        self.col = col
        self.row = row
        self.active = False
        self.flicker_sequence = flicker.FlickerSequence()


class CheckpointRay(Tile):
    SOLID = False
    EMITTED = True
    DRAWN_STATICALLY = True

    def __init__(self, checkpoint, orientation):
        super().__init__()

        self.orientation = orientation
        self.checkpoint = checkpoint


class PlayerSpawn(Tile):
    SOLID = False
    EMITTED = False
    DRAWN_STATICALLY = False

    def __init__(self, col, row):
        super().__init__()
        self.col = col
        self.row = row
        self.flicker_sequence = flicker.FlickerSequence()


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

player_spawn_gradient = checkpoint_gradient
player_spawn_glow = graphics.load_image("player_spawn_glow", 1)


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

    goal_sound = sound.load("goal")
    goal_sound.set_volume(0)
    goal_sound_playing = False

    def __init__(self, name):
        """name is the name of the file in the levels folder"""
        self.grid = [[[] for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

        self.player_spawn = PlayerSpawn(0, 0)
        self.player_goal = PlayerGoal(0, 0)
        self.grid[0][0].append(self.player_spawn)
        self.grid[0][0].append(self.player_goal)

        self.unique_flickers = []

        self.text_x = 0
        self.text_y = 0

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

    def _initiate_deathlock_flicker(self):
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.has_tile(Deathlock, col, row):
                    self._initiate_deathlock_flicker_recursion(flicker.FlickerSequence(), col, row)

    def _initiate_deathlock_flicker_recursion(self, flicker_sequence, col, row):
        tile = self.get_tile(Deathlock, col, row)
        if tile.flicker_initiated:
            return

        tile.flicker_sequence = flicker_sequence
        if self.has_tile(Deathlock, col - 1, row):
            self._initiate_deathlock_flicker_recursion(flicker_sequence, col - 1, row)
        if self.has_tile(Deathlock, col + 1, row):
            self._initiate_deathlock_flicker_recursion(flicker_sequence, col + 1, row)
        if self.has_tile(Deathlock, col, row - 1):
            self._initiate_deathlock_flicker_recursion(flicker_sequence, col, row - 1)
        if self.has_tile(Deathlock, col, row + 1):
            self._initiate_deathlock_flicker_recursion(flicker_sequence, col, row + 1)

    def _record_unique_flickers(self):
        self.unique_flickers = [self.player_spawn.flicker_sequence]
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row]:
                    tile = self.grid[col][row][0]
                    if hasattr(tile, "flicker_sequence"):
                        for flicker_sequence in self.unique_flickers:
                            if flicker_sequence.sequence_list is tile.flicker_sequence.sequence_list:
                                break
                        else:
                            self.unique_flickers.append(tile.flicker_sequence)

    def emit(self):
        """Emits PunchZones from all PunchBoxes and CheckpointRays from
        all Checkpoints"""
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in self.tiles_at(col, row):
                    if type(tile) == PlayerGoal:
                        self.emit_player_goal_zone(col, row)
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in self.tiles_at(col, row):
                    if type(tile) == Checkpoint:
                        self.emit_checkpoint_ray(col, row, tile)
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                for tile in self.tiles_at(col, row):
                    if type(tile) == PunchBox:
                        self.emit_punch_zone(col, row, tile)

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
        if self.has_tile(Deathlock, col, row):
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

    def draw_silhouette(self, surf):
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                x = col * TILE_W
                y = row * TILE_H
                rect = (x, y, TILE_W, TILE_H)
                if self.has_solid(col, row):
                    pygame.draw.rect(surf, const.BLACK, rect)

    def draw_tile_at(self, surf, camera, col, row,
                     player_dead=False, original_spawn=False):
        x = col * TILE_W - int(camera.x)
        y = row * TILE_H - int(camera.y)
        rect = (x, y, TILE_W, TILE_H)

        if self.has_tile(Wall, col, row):
            pygame.draw.rect(surf, const.BLACK, rect)

        elif self.has_tile(PlayerSpawn, col, row):
            if original_spawn:
                color = (81, 255, 113)
            else:
                color = (71, 158, 71)
            pygame.draw.rect(surf, color, rect)

        elif self.has_tile(Deathlock, col, row):
            if player_dead:
                color = (88, 91, 173)
            else:
                color = (109, 112, 255)
            pygame.draw.rect(surf, color, rect)

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
            self.draw_checkpoint_and_ray(surf, checkpoint)

        elif self.has_tile(PlayerGoalZone, col, row):
            pygame.draw.rect(surf, (250, 250, 250), rect)

    def draw_deathlock(self, surf, camera, player_dead):
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                if self.has_tile(Deathlock, col, row):
                    x = col * TILE_W - int(camera.x)
                    y = row * TILE_H - int(camera.y)
                    rect = (x, y, TILE_W, TILE_H)

                    if player_dead:
                        color = (88, 91, 173)
                    else:
                        color = (109, 112, 255)
                    pygame.draw.rect(surf, color, rect)

    def draw_flicker_glow(self, surf, frame):
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self._flicker_bright_enough_for_gradient(col, row, frame):
                    self.draw_glow_at(surf, col, row, frame)

    def _flicker_bright_enough_for_gradient(self, col, row, frame):
        if self.grid[col][row]:
            tile = self.grid[col][row][0]
            is_ray = type(tile) is CheckpointRay
            if hasattr(tile, "flicker_sequence") or is_ray:
                if is_ray:
                    brightness = tile.checkpoint.flicker_sequence.brightness(frame)
                else:
                    brightness = tile.flicker_sequence.brightness(frame)
                if brightness >= flicker.BRIGHT:
                    return True

        return False

    def _stops_flicker_gradient(self, type_, col, row, frame):
        if self.out_of_bounds(col, row):
            return True

        if self.grid[col][row]:
            if type(self.grid[col][row][0]) is type_:
                return self._flicker_bright_enough_for_gradient(col, row, frame)

        return False

    shade_soft = pygame.Surface((TILE_W, TILE_H))
    shade_soft.fill((25, 25, 25))
    shade_medium = pygame.Surface((TILE_W, TILE_H))
    shade_medium.fill((50, 50, 50))
    shade_bright = pygame.Surface((TILE_W, TILE_H))
    shade_bright.fill((100, 100, 100))
    checkpoint_shade_soft = graphics.load_image("checkpoint_shade_soft", 2)
    checkpoint_shade_medium = graphics.load_image("checkpoint_shade_medium", 2)
    checkpoint_shade_bright = graphics.load_image("checkpoint_shade_bright", 2)

    def draw_flicker_tiles(self, surf, camera, frame):
        # Draw all checkpoints first, so that the rays can be shaded later
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row]:
                    tile = self.grid[col][row][0]
                    if type(tile) is Checkpoint:
                        if tile.flicker_sequence.brightness(frame) > flicker.NONE:
                            self.draw_tile_at(surf, camera, col, row)

        # Draw other tiles and shade them all
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row]:
                    tile = self.grid[col][row][0]
                    is_ray = type(tile) is CheckpointRay
                    if hasattr(tile, "flicker_sequence") or is_ray:
                        if is_ray:
                            brightness = tile.checkpoint.flicker_sequence.brightness(frame)
                        else:
                            brightness = tile.flicker_sequence.brightness(frame)

                        if brightness != flicker.NONE and not type(tile) is Checkpoint and not is_ray:
                            self.draw_tile_at(surf, camera, col, row)
                        if brightness == flicker.SOFT:
                            shade = self.shade_soft
                        elif brightness == flicker.MEDIUM:
                            shade = self.shade_medium
                        elif brightness == flicker.BRIGHT:
                            shade = self.shade_bright
                        else:  # Skip FULL brightness, since no shade is drawn
                            continue

                        if is_ray:
                            if tile.orientation == const.HORIZ:
                                pos = (x_of(col), y_of(row) + TILE_H // 3)
                                rect = (0, 0, TILE_W, TILE_H // 3 + 2)
                            else:
                                pos = (x_of(col) + TILE_W // 3, y_of(row))
                                rect = (0, 0, TILE_W // 3 + 2, TILE_H)
                            surf.blit(shade, pos, rect, special_flags=pygame.BLEND_MULT)
                        else:
                            if type(tile) is Checkpoint:
                                if brightness == flicker.SOFT:
                                    shade = self.checkpoint_shade_soft
                                elif brightness == flicker.MEDIUM:
                                    shade = self.checkpoint_shade_medium
                                elif brightness == flicker.BRIGHT:
                                    shade = self.checkpoint_shade_bright
                            pos = (x_of(col), y_of(row))
                            surf.blit(shade, pos, special_flags=pygame.BLEND_MULT)

    glow_surf = pygame.Surface((const.SCRN_W, const.SCRN_H))

    def draw_glow(self, surf):
        self.glow_surf.fill(const.BLACK)
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                self.draw_glow_at(self.glow_surf, col, row)
        surf.blit(self.glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    def draw_glow_at(self, surf, col, row, flicker_frame=-1):
        center_x = center_x_of(col)
        center_y = center_y_of(row)

        if self.has_tile(PunchBox, col, row):
            draw_glow_centered(surf, punch_box_glow, center_x, center_y)
            if flicker_frame == -1:
                self._draw_gradient_efficient(surf, PunchBox, punch_box_gradient, col, row)
            else:
                self._draw_flicker_gradient_efficient(surf, PunchBox, punch_box_gradient, col, row, flicker_frame)
        elif self.has_tile(Deathlock, col, row):
            draw_glow_centered(surf, deathlock_glow, center_x, center_y)
            if flicker_frame == -1:
                self._draw_gradient_efficient(surf, Deathlock, deathlock_gradient, col, row)
            else:
                self._draw_flicker_gradient_efficient(surf, Deathlock, deathlock_gradient, col, row, flicker_frame)

        elif self.has_tile(Checkpoint, col, row):
            draw_glow_centered(surf, checkpoint_glow, center_x, center_y)
            if flicker_frame == -1:
                self._draw_gradient_efficient(surf, Checkpoint, checkpoint_gradient, col, row)
            else:
                self._draw_flicker_gradient_efficient(surf, Checkpoint, checkpoint_gradient, col, row, flicker_frame)

        elif self.has_tile(CheckpointRay, col, row):
            tile = self.get_tile(CheckpointRay, col, row)
            if tile.orientation == const.HORIZ:
                draw_glow_centered(surf, checkpoint_ray_horiz_glow, center_x, center_y)
                draw_glow_centered(surf, checkpoint_ray_horiz_gradient, center_x, center_y)

            elif tile.orientation == const.VERT:
                draw_glow_centered(surf, checkpoint_ray_vert_glow, center_x, center_y)
                draw_glow_centered(surf, checkpoint_ray_vert_gradient, center_x, center_y)

        elif self.has_tile(PlayerSpawn, col, row):
            draw_glow_centered(surf, player_spawn_glow, center_x, center_y)
            draw_glow_centered(surf, player_spawn_gradient, center_x, center_y)

    def _draw_gradient_efficient(self, surf, type_, gradient, col, row):
        gradient_width = gradient.get_width()
        gradient_height = gradient.get_height()
        x_to_center = gradient_width // 2 - TILE_W // 2
        y_to_center = gradient_height // 2 - TILE_H // 2
        x_remainder = gradient_width - x_to_center
        y_remainder = gradient_height - y_to_center

        if self.has_tile(type_, col - 1, row):
            x = x_of(col)
            slice_x = x_to_center
            slice_width = x_remainder
        else:
            x = x_of(col) - x_to_center
            slice_x = 0
            slice_width = gradient_width
        if self.has_tile(type_, col + 1, row):
            slice_width -= x_to_center

        if self.has_tile(type_, col, row - 1):
            y = y_of(row)
            slice_y = y_to_center
            slice_height = y_remainder
        else:
            y = y_of(row) - y_to_center
            slice_y = 0
            slice_height = gradient_height
        if self.has_tile(type_, col, row + 1):
            slice_height -= y_to_center

        rect = (slice_x, slice_y, slice_width, slice_height)
        surf.blit(gradient, (x, y), rect, special_flags=pygame.BLEND_MAX)

    MAX_SEARCH_PUNCH_BOX = (punch_box_gradient.get_width() // TILE_W - 1) // 2 + 1
    MAX_SEARCH_CHECKPOINT = (checkpoint_gradient.get_width() // TILE_W - 1) // 2 + 1
    MAX_SEARCH_DEATHLOCK = (deathlock_gradient.get_width() // TILE_W - 1) // 2 + 1

    def _draw_flicker_gradient_efficient(self, surf, type_, gradient, col, row, frame):
        if type_ is PunchBox:
            max_search = self.MAX_SEARCH_PUNCH_BOX
        elif type_ is Checkpoint:
            max_search = self.MAX_SEARCH_CHECKPOINT
        else:
            max_search = self.MAX_SEARCH_DEATHLOCK

        x_to_center = gradient.get_width() // 2 - TILE_W // 2
        y_to_center = gradient.get_height() // 2 - TILE_H // 2

        space_left = 0
        for c in range(1, max_search + 1):
            if self._stops_flicker_gradient(type_, col - c, row, frame):
                break
            space_left += 1

        space_right = 0
        for c in range(1, max_search + 1):
            if self._stops_flicker_gradient(type_, col + c, row, frame):
                break
            space_right += 1

        space_up = 0
        for r in range(1, max_search + 1):
            if self._stops_flicker_gradient(type_, col, row - r, frame):
                break
            space_up += 1

        space_down = 0
        for r in range(1, max_search + 1):
            if self._stops_flicker_gradient(type_, col, row + r, frame):
                break
            space_down += 1

        x = x_of(col) - space_left * TILE_W
        y = y_of(row) - space_up * TILE_H
        slice_x = x_to_center - space_left * TILE_W
        slice_y = y_to_center - space_up * TILE_H
        slice_width = (space_left + space_right + 1) * TILE_W
        slice_height = (space_up + space_down + 1) * TILE_H
        rect = (slice_x, slice_y, slice_width, slice_height)

        surf.blit(gradient, (x, y), rect, special_flags=pygame.BLEND_MAX)

    def draw_goal_glow(self, surf):
        glow_surf = pygame.Surface(surf.get_size())
        for col in range(self.player_goal.col - 1, self.player_goal.col + 2):
            for row in range(self.player_goal.row - 1, self.player_goal.row + 2):
                center_x = center_x_of(col)
                center_y = center_y_of(row)

                gradient_x = int(center_x - (player_goal_gradient.get_width() / 2))
                gradient_y = int(center_y - (player_goal_gradient.get_height() / 2))
                glow_surf.blit(player_goal_gradient, (gradient_x, gradient_y), special_flags=pygame.BLEND_MAX)
        surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    def draw_static(self, surf, camera):
        """draws the entire stage"""
        self.draw_glow(surf)
        self.draw_tiles(surf, camera)
        self.draw_goal_glow(surf)

    def draw_tiles(self, surf, camera):
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row] and self.grid[col][row][0].DRAWN_STATICALLY:
                    self.draw_tile_at(surf, camera, col, row)

    def draw_dynamic(self, surf, camera, player_dead, original_spawn):
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH):
                if self.grid[col][row] and not self.grid[col][row][0].DRAWN_STATICALLY:
                    self.draw_tile_at(surf, camera, col, row,
                                      player_dead, original_spawn)

    def draw_checkpoint_and_ray(self, surf, checkpoint):
        col = checkpoint.col
        row = checkpoint.row

        x = x_of(col)
        y = y_of(row)
        if checkpoint.active:
            surf.blit(checkpoint_activated, (x, y))
        else:
            surf.blit(checkpoint_deactivated, (x, y))

        if checkpoint.direction == const.LEFT:
            stop_col = col - 1
            while not self.stops_checkpoint_ray(stop_col, row):
                stop_col -= 1
            stop_col += 1

            if stop_col == col:
                return

            x = x_of(stop_col)
            y += TILE_H // 3
            width = (col - stop_col) * TILE_W
            height = TILE_H // 3 + 2

        elif checkpoint.direction == const.RIGHT:
            stop_col = col + 1
            while not self.stops_checkpoint_ray(stop_col, row):
                stop_col += 1
            stop_col -= 1

            if stop_col == col:
                return

            x += TILE_W
            y += TILE_H // 3
            width = (stop_col - col) * TILE_W
            height = TILE_H // 3 + 2

        elif checkpoint.direction == const.UP:
            stop_row = row - 1
            while not self.stops_checkpoint_ray(col, stop_row):
                stop_row -= 1
            stop_row += 1

            if stop_row == row:
                return

            x += TILE_W // 3
            y = y_of(stop_row)
            width = TILE_W // 3 + 2
            height = (row - stop_row) * TILE_H

        else:
            stop_row = row + 1
            while not self.stops_checkpoint_ray(col, stop_row):
                stop_row += 1
            stop_row -= 1

            if stop_row == row:
                return

            x += TILE_W // 3
            y += TILE_H
            width = TILE_W // 3 + 2
            height = (stop_row - row) * TILE_H

        if checkpoint.active:
            color = (81, 255, 113)
        else:
            color = (71, 158, 71)

        pygame.draw.rect(surf, color, (x, y, width, height))

    def update_goal_sound(self, player, is_transitioning):
        if is_transitioning:
            self.goal_sound_playing = False
            self.goal_sound.stop()
            return

        distance_x = player.center_x - center_x_of(self.player_goal.col)
        distance_y = player.center_y - center_y_of(self.player_goal.row)
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if distance < 300.0:
            if distance == 20:
                return

            if distance < 75:
                # Reciprocal rises fast as distance gets closer to 20
                mult = 2 / (distance - 20)
            else:
                # A line from where the reciprocal ends at x=75 to 0 at x=200
                connection = 2 / (75 - 20)
                m = -connection / (300 - 75)
                b = - m * 300
                mult = m * distance + b
            volume = 0.97 * mult
            self.goal_sound.set_volume(volume)

            if not self.goal_sound_playing:
                self.goal_sound_playing = True
                self.goal_sound.play(-1)

        elif self.goal_sound_playing:
            self.goal_sound_playing = False
            self.goal_sound.stop()

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
        strings = ["%i %i" % (self.text_x, self.text_y)]
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

        lines = data.split("\n")
        text_position = lines[0].split(" ")
        self.text_x = int(text_position[0])
        self.text_y = int(text_position[1])

        level_rows = lines[1:]

        for row_index, row in enumerate(level_rows):
            for col_index, tile in enumerate(row.split(" ")):
                self.place_tile_from_id(col_index, row_index, int(tile))

        self._initiate_deathlock_flicker()
        self._record_unique_flickers()
        self.emit()
