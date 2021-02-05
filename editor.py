import pygame

import constants as const
import events
import grid
import debug


basic_tiles = [grid.Wall, grid.Deathlock]
selections = [None, grid.Wall, grid.Deathlock, grid.PunchBox, grid.Checkpoint,
              grid.PlayerSpawn, grid.PlayerGoal]


def mouse_col():
    return grid.col_at(events.mouse.position[0])


def mouse_row():
    return grid.row_at(events.mouse.position[1])


class Editor:
    PLACE = 0
    RECT = 1

    left_key = events.Keybind([pygame.K_a, pygame.K_LEFT])
    right_key = events.Keybind([pygame.K_d, pygame.K_RIGHT])
    up_key = events.Keybind([pygame.K_w, pygame.K_UP])
    down_key = events.Keybind([pygame.K_s, pygame.K_DOWN])
    save_key = events.Keybind([pygame.K_u])

    def __init__(self, level):
        self.level = level
        self.mode = self.PLACE
        self._direction = const.LEFT
        self._tile = None

        self.rect_start_col = 0
        self.rect_start_row = 0

    @property
    def _mode_string(self):
        if self.mode == self.PLACE:
            return "PLACE"
        elif self.mode == self.RECT:
            return "RECT"

    def _input_direction(self):
        if self.left_key.is_pressed:
            self._direction = const.LEFT
        elif self.right_key.is_pressed:
            self._direction = const.RIGHT
        elif self.up_key.is_pressed:
            self._direction = const.UP
        elif self.down_key.is_pressed:
            self._direction = const.DOWN

    def _input_selected_tile(self):
        if events.keys.pressed_key in events.number_keys:
            number = int(pygame.key.name(events.keys.pressed_key)) - 1
            if 0 <= number < len(selections):
                self._tile = selections[number]

    def _input_place_block(self):
        if events.mouse.held:
            col = mouse_col()
            row = mouse_row()
            self.level.clear_point(col, row)
            if self._tile in basic_tiles:
                self.level.add_tile(col, row, self._tile())
            elif self._tile == grid.PunchBox:
                self.level.add_tile(col, row, self._tile(self._direction))
            elif self._tile == grid.Checkpoint:
                self.level.add_checkpoint(col, row, self._direction)
            elif self._tile == grid.PlayerSpawn:
                self.level.move_player_spawn(col, row)
            elif self._tile == grid.PlayerGoal:
                self.level.move_player_goal(col, row)

    def _input_switch_mode(self):
        if events.keys.pressed_key == pygame.K_TAB:
            if self.mode == self.PLACE:
                self.mode = self.RECT
            elif self.mode == self.RECT:
                self.mode = self.PLACE

    def _input_place_rect(self):
        if events.mouse.clicked:
            self.rect_start_col = mouse_col()
            self.rect_start_row = mouse_row()
        if events.mouse.released:
            left = min(self.rect_start_col, mouse_col())
            top = min(self.rect_start_row, mouse_row())
            right = max(self.rect_start_col, mouse_col())
            bottom = max(self.rect_start_row, mouse_row())
            width = right - left + 1
            height = bottom - top + 1

            self.level.clear_rect(left, top, width, height)
            if self._tile in basic_tiles:
                self.level.add_rect(left, top, width, height, self._tile)
            elif self._tile == grid.PunchBox:
                constructor = lambda: grid.PunchBox(self._direction)
                self.level.add_rect(left, top, width, height, constructor)
            elif self._tile == grid.Checkpoint:
                constructor = lambda: grid.Checkpoint(left, top, self._direction)
                self.level.add_rect(left, top, width, height, constructor)

    def _take_inputs(self):
        self._input_direction()
        self._input_selected_tile()
        self._input_switch_mode()
        if self.mode == self.PLACE:
            self._input_place_block()
        elif self.mode == self.RECT:
            self._input_place_rect()

        if self.save_key.is_pressed:
            self.level.save()

    def update(self):
        self._take_inputs()

    def _draw_selections(self, surf):
        mode = self._mode_string
        direction = const.direction_string(self._direction)
        if self._tile:
            tile = str(self._tile.__name__)
        else:
            tile = "Erase"
        string = "%-6s %-6s %s" % (mode, direction, tile)

        text = debug.TAHOMA_LARGE.render(string, False, const.WHITE, const.BLACK)
        surf.blit(text, (10, 10))

    def _draw_rect_marker(self, surf):
        x = grid.x_of(self.rect_start_col)
        y = grid.y_of(self.rect_start_row)
        rect = (x, y, grid.TILE_W, grid.TILE_H)
        pygame.draw.rect(surf, const.MAGENTA, rect)

    def _draw_mouse_marker(self, surf):
        x = grid.x_of(mouse_col())
        y = grid.y_of(mouse_row())
        rect = (x, y, grid.TILE_W, grid.TILE_H)
        pygame.draw.rect(surf, const.MAGENTA, rect)

    def draw(self, surf):
        self._draw_mouse_marker(surf)
        if self.mode == self.RECT and events.mouse.held:
            self._draw_rect_marker(surf)
        self._draw_selections(surf)
