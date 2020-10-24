import pygame
import constants as const

import sound
import grid
import punchers
import graphics


class Player:
    CHECK_STEPS = 4
    TERMINAL_VELOCITY = 20.0

    MAX_HEALTH = 3
    JUMP_SPEED = 9
    MOVE_SPEED = 4
    MOVE_ACC = 0.8
    MOVE_DEC = 1.5
    EXT_DEC = 0.5

    INVULN_LENGTH = 10

    HEALTH_SPACING = 5

    WIDTH = 20
    HEIGHT = 20

    RUN_LEFT = graphics.AnimColumn("run", 6, 2)
    RUN_LEFT.set_delay(4)
    RUN_LEFT_ID = 0
    RUN_RIGHT = graphics.flip_column(RUN_LEFT)
    RUN_RIGHT_ID = 1

    IDLE_LEFT = graphics.AnimColumn("idle", 4, 2)
    IDLE_LEFT.set_delays((60, 10, 45, 10))
    IDLE_LEFT_ID = 2
    IDLE_RIGHT = graphics.flip_column(IDLE_LEFT)
    IDLE_RIGHT_ID = 3

    TUMBLE_LEFT = graphics.AnimColumn("tumble", 6, 2)
    TUMBLE_LEFT.set_delay(4)
    TUMBLE_LEFT_ID = 4
    TUMBLE_RIGHT = graphics.flip_column(TUMBLE_LEFT)
    TUMBLE_RIGHT_ID = 5

    DEAD_GROUNDED_LEFT = graphics.AnimColumn("dead_grounded", 1, 2)
    DEAD_GROUNDED_LEFT.set_delay(0xbeef)
    DEAD_GROUNDED_LEFT_ID = 6
    DEAD_GROUNDED_RIGHT = graphics.flip_column(DEAD_GROUNDED_LEFT)
    DEAD_GROUNDED_RIGHT_ID = 7

    DEAD_FALL_LEFT = graphics.AnimColumn("dead_fall", 7, 2)
    DEAD_FALL_LEFT.set_delay(0xbeef)
    DEAD_FALL_LEFT_ID = 8
    DEAD_FALL_RIGHT = graphics.flip_column(DEAD_FALL_LEFT)
    DEAD_FALL_RIGHT_ID = 9

    WALL_PUSH_LEFT = graphics.AnimColumn("wall_push", 1, 2)
    WALL_PUSH_LEFT.set_delay(0xbeef)
    WALL_PUSH_LEFT_ID = 10
    WALL_PUSH_RIGHT = graphics.flip_column(WALL_PUSH_LEFT)
    WALL_PUSH_RIGHT_ID = 11

    JUMP_LEFT = graphics.AnimColumn("jump", 6, 2)
    JUMP_LEFT.set_delay(0xbeef)
    JUMP_LEFT_ID = 12
    JUMP_RIGHT = graphics.flip_column(JUMP_LEFT)
    JUMP_RIGHT_ID = 13

    ANIMSHEET = graphics.AnimSheet((RUN_LEFT, RUN_RIGHT,
                                    IDLE_LEFT, IDLE_RIGHT,
                                    TUMBLE_LEFT, TUMBLE_RIGHT,
                                    DEAD_GROUNDED_LEFT, DEAD_GROUNDED_RIGHT,
                                    DEAD_FALL_LEFT, DEAD_FALL_RIGHT,
                                    WALL_PUSH_LEFT, WALL_PUSH_RIGHT,
                                    JUMP_LEFT, JUMP_RIGHT))

    MIDDLE_HEART = graphics.AnimColumn("heart_middle", 2, 2)
    LEFT_HEART = graphics.AnimColumn("heart_left", 2, 2)
    RIGHT_HEART = graphics.flip_column(LEFT_HEART)
    MIDDLE_HEART.set_delays((62, 16))
    LEFT_HEART.set_delays((62, 16))
    RIGHT_HEART.set_delays((62, 16))

    HEART_SHEET = graphics.AnimSheet((MIDDLE_HEART, LEFT_HEART, RIGHT_HEART))

    MIDDLE_HEART_X = (const.SCRN_W - MIDDLE_HEART.frame_w) // 2
    HEART_X = [MIDDLE_HEART_X, MIDDLE_HEART_X - 50, MIDDLE_HEART_X + 50]
    HEART_Y = -3

    RUN_SOUNDS = sound.load_numbers("run%i", 5)
    RUN_SOUND_DELAY = 5

    REVIVE_SOUNDS = sound.load_numbers("revive%i", 3)

    HIT_SOUNDS = sound.load_numbers("hit%i", 3)

    # ROOM_CHANGE_SOUNDS = sound.load_numbers("room_change%i", 1)

    JUMP_SOUNDS = sound.load_numbers("jump%i", 3)

    LAND_SOUNDS = sound.load_numbers("land%i", 3)

    def __init__(self, level, x, y, camera, extend_x=0, extend_y=0):
        self.health = self.MAX_HEALTH
        self.dead = False
        self.offscreen_direction = 0

        self.x = x
        self.y = y
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.x_acc = 0.0
        self.y_acc = 0.0

        # external velocities - caused by non-player forces
        self.ext_x_vel = 0.0

        self.x_dir = 0
        self.y_dir = 0

        self.extend_x = extend_x
        self.extend_y = extend_y
        self.gridbox = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                  self.WIDTH + extend_x * 2, self.HEIGHT + extend_y * 2)

        self.grounded = False
        self.level = level  # reference to the level layout
        self.camera = camera

        self.tumble = False
        self.invuln_frames = 0

        self.respawn_x = 0.0
        self.respawn_y = 0.0

        self.sprite = graphics.AnimInstance(self.ANIMSHEET)
        self.facing = const.LEFT

        self.heart_sprites = [graphics.AnimInstance(self.HEART_SHEET) for _ in range(self.MAX_HEALTH)]
        for heart_sprite in range(1, self.MAX_HEALTH):
            self.heart_sprites[heart_sprite].set_anim(heart_sprite)

        self.run_sound_frame = self.RUN_SOUND_DELAY

    def draw(self, surf, cam):
        self.sprite.update()

        x = self.gridbox.x - cam.x
        y = self.gridbox.y - cam.y
        self.sprite.draw_frame(surf, x, y)

    def check_offscreen(self):
        center_x = self.x + (self.WIDTH // 2)
        center_y = self.y + (self.HEIGHT // 2)

        grid_left = grid.Room.PIXEL_W * self.level.active_column
        grid_right = grid_left + grid.Room.PIXEL_W
        grid_top = grid.Room.PIXEL_H * self.level.active_row
        grid_bottom = grid_top + grid.Room.PIXEL_H

        if center_x > grid_right:
            self.offscreen_direction = const.RIGHT
        elif center_x < grid_left:
            self.offscreen_direction = const.LEFT
        elif center_y > grid_bottom:
            self.offscreen_direction = const.DOWN
        elif center_y < grid_top:
            self.offscreen_direction = const.UP
        else:
            self.offscreen_direction = 0

    def move(self, void_solid=True):
        """moves body based on velocity and acceleration"""
        if not self.grounded:
            self.y_acc = const.GRAVITY

        if self.x_vel > self.MOVE_SPEED:
            self.x_vel = self.MOVE_SPEED
        elif self.x_vel < -self.MOVE_SPEED:
            self.x_vel = -self.MOVE_SPEED
        self.collide_stage(not self.dead)

        self.x_vel += self.x_acc
        self.y_vel += self.y_acc
        if self.y_vel > self.TERMINAL_VELOCITY:
            self.y_vel = self.TERMINAL_VELOCITY

        self.x += self.x_vel + self.ext_x_vel
        self.y += self.y_vel

        # Determines direction of movement
        if self.x_vel < 0:
            self.x_dir = const.LEFT
        elif self.x_vel > 0:
            self.x_dir = const.RIGHT
        else:
            self.x_dir = 0

        if self.y_vel < 0:
            self.y_dir = const.UP
        elif self.y_vel > 0:
            self.y_dir = const.DOWN
        else:
            self.y_dir = 0

        self.check_ground(void_solid)

        self.goto(self.x, self.y)

        self.check_offscreen()

    def change_health(self, amount):
        self.health += amount
        if self.health <= 0:
            self.dead = True
        else:
            self.dead = False

    def set_health(self, amount):
        self.health = amount
        if self.health <= 0:
            self.dead = True
        else:
            self.dead = False

    # Body
    def goto(self, x, y):
        """instantly moves the body to a specific position"""
        x = int(x)
        y = int(y)
        self.x = x
        self.y = y
        self.gridbox.x = x
        self.gridbox.y = y
        self.hitbox.x = x - self.extend_x
        self.hitbox.y = y - self.extend_y

    def next_x(self):
        """returns the x position of the body on the next frame"""
        return self.x + self.x_vel + self.ext_x_vel + self.x_acc

    def next_y(self):
        """returns the y position of the body on the next frame"""
        return self.y + self.y_vel + self.y_acc

    def stop_x(self):
        self.x_dir = 0
        self.x_vel = 0
        self.ext_x_vel = 0
        self.x_acc = 0

    def stop_y(self):
        self.y_dir = 0
        self.y_vel = 0
        self.y_acc = 0

    def snap_x(self, col, side=const.LEFT):
        """snaps you to either the left side or right side of a tile"""
        if side == const.LEFT:
            self.goto(grid.x_of(col, const.LEFT) - self.WIDTH, self.y)
            self.stop_x()

        elif side == const.RIGHT:
            self.goto(grid.x_of(col, const.RIGHT), self.y)
            self.stop_x()

    def snap_y(self, row, side=const.TOP):
        """snaps you to either the top or bottom of a tile"""
        if side == const.TOP:
            self.goto(self.x, grid.y_of(row, const.TOP) - self.HEIGHT)
            self.stop_y()

        elif side == const.BOTTOM:
            self.goto(self.x, grid.y_of(row, const.BOTTOM))
            self.stop_y()

    def collide_stage(self, void_solid=True):
        """checks collision with stage and updates movement accordingly

        if screen_edge is True, then the edge of the screen acts as a wall."""

        for step in range(1, self.CHECK_STEPS + 1):
            diff_x = self.next_x() - self.x
            diff_y = self.next_y() - self.y

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

            left_x = self.x
            right_x = left_x + self.WIDTH - 1
            top_y = int(self.y + (diff_y * (step / self.CHECK_STEPS)))
            bottom_y = top_y + self.HEIGHT - 1

            if dir_y == const.UP:
                if self.level.collide_horiz(left_x, right_x, top_y, void_solid):
                    self.snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self.level.collide_horiz(left_x, right_x, bottom_y, void_solid):
                    self.snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self.x + (diff_x * (step / 4)))
            right_x = left_x + self.WIDTH - 1
            top_y = self.y
            bottom_y = top_y + self.HEIGHT - 1

            if dir_x == const.LEFT:
                if self.level.collide_vert(left_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(left_x), const.RIGHT)

            elif dir_x == const.RIGHT:
                if self.level.collide_vert(right_x, top_y, bottom_y, void_solid):
                    self.snap_x(grid.col_at(right_x), const.LEFT)

            if not self.dead and not self.invuln_frames:
                center_col = grid.col_at(self.x + (self.WIDTH // 2))
                center_row = grid.row_at(self.y + (self.HEIGHT // 2))
                tile = self.level.tile_at(center_col, center_row)
                if tile == grid.PUNCHER_LEFT:
                    self.get_hit()
                    punchers.add(center_col, center_row, const.LEFT)
                    self.ext_x_vel = -7

                    if self.x_vel > 0:
                        self.x_vel = 0

                elif tile == grid.PUNCHER_UP:
                    self.get_hit()
                    punchers.add(center_col, center_row, const.UP)
                    self.y_vel = -12

                elif tile == grid.PUNCHER_RIGHT:
                    self.get_hit()
                    punchers.add(center_col, center_row, const.RIGHT)
                    self.ext_x_vel = 7

                    if self.x_vel < 0:
                        self.x_vel = 0

                elif tile == grid.PUNCHER_DOWN:
                    self.get_hit()
                    punchers.add(center_col, center_row, const.DOWN)
                    self.y_vel = 7

            elif self.invuln_frames:
                self.invuln_frames -= 1

    def update_wall_push(self, direction):
        top_y = self.y
        bottom_y = top_y + self.HEIGHT - 1

        if direction == const.LEFT:
            x = self.x - 1
            if self.level.collide_vert(x, top_y, bottom_y, not self.dead):
                self.sprite.set_anim(self.WALL_PUSH_LEFT_ID)

        elif direction == const.RIGHT:
            x = self.x + self.WIDTH
            if self.level.collide_vert(x, top_y, bottom_y, not self.dead):
                self.sprite.set_anim(self.WALL_PUSH_RIGHT_ID)

    def update_hearts(self):
        for heart in self.heart_sprites:
            heart.update()

    def draw_hearts(self, surf):
        for heart in range(self.health):
            heart_sprite = self.heart_sprites[heart]
            heart_sprite.draw_frame(surf, self.HEART_X[heart], self.HEART_Y)

    def get_hit(self):
        self.tumble = True
        self.change_health(-1)
        self.invuln_frames = self.INVULN_LENGTH
        self.HIT_SOUNDS.play_random()
        self.camera.shake(6, 1)

    def check_ground(self, screen_edge):
        x1 = self.x
        x2 = x1 + self.WIDTH - 1
        y = self.y + self.HEIGHT
        if self.level.collide_horiz(x1, x2, y, screen_edge):
            if not self.grounded:
                self.LAND_SOUNDS.play_random(0.3)
            self.grounded = True
        else:
            self.grounded = False

    def set_checkpoint(self):
        room = self.level.room_grid[self.level.active_column][self.level.active_row]

        center_col = grid.col_at(self.x + (self.WIDTH // 2))
        center_row = grid.row_at(self.y + (self.HEIGHT // 2))
        tile = self.level.tile_at(center_col, center_row)

        if tile in grid.CHECKPOINT_ZONE:
            checkpoint_num = grid.CHECKPOINT_ZONE.index(tile)
            col, row = room.checkpoints[checkpoint_num]

            x_offset = (grid.TILE_W - self.WIDTH) // 2  # centers the player on the tile
            y_offset = (grid.TILE_H - self.HEIGHT) // 2
            self.respawn_x = grid.x_of(col) + x_offset
            self.respawn_y = grid.y_of(row) + y_offset

        else:
            print("Player entered level without setting checkpoint!")

            for y in range(-1, 2, 1):
                for x in range(-1, 2, 1):
                    print(self.level.tile_at(center_col + x, center_row + y), end=" ")

                print()
