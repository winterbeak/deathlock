import pygame

import constants as const
import events
import grid
import debug


basic_tiles = [grid.Wall, grid.Deathlock]
selections = [None, grid.Wall, grid.Deathlock, grid.PunchBox, grid.Checkpoint]


class Editor:
    PLACE = 0
    ERASE = 1

    left_key = events.Keybind([pygame.K_a, pygame.K_LEFT])
    right_key = events.Keybind([pygame.K_d, pygame.K_RIGHT])
    up_key = events.Keybind([pygame.K_w, pygame.K_UP])
    down_key = events.Keybind([pygame.K_s, pygame.K_DOWN])

    def __init__(self, level):
        self.level = level
        self.mode = self.PLACE
        self._direction = const.LEFT
        self._tile = None

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
            col = grid.col_at(events.mouse.position[0])
            row = grid.row_at(events.mouse.position[1])
            self.level.clear_point(col, row)
            if self._tile in basic_tiles:
                self.level.add_tile(col, row, self._tile())
            elif self._tile == grid.PunchBox:
                self.level.add_tile(col, row, self._tile(self._direction))
            elif self._tile == grid.Checkpoint:
                self.level.add_checkpoint(col, row, self._direction)

    def _input_erase_tile(self):
        if events.mouse.held:
            col = grid.col_at(events.mouse.position[0])
            row = grid.row_at(events.mouse.position[1])
            self.level.clear_point(col, row)

    def _take_inputs(self):
        self._input_direction()
        self._input_selected_tile()
        if self.mode == self.PLACE:
            self._input_place_block()
        else:
            self._input_erase_tile()

    def update(self):
        self._take_inputs()

    def _draw_selections(self, surf):
        direction = const.direction_string(self._direction)
        if self._tile:
            tile = str(self._tile.__name__)
        else:
            tile = "Erase"
        string = "%-6s %s" % (direction, tile)

        text = debug.TAHOMA_LARGE.render(string, False, const.WHITE, const.BLACK)
        surf.blit(text, (10, 10))

    def draw(self, surf):
        self._draw_selections(surf)
