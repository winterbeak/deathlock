import pygame
import constants as const

from entities import collision
import events
import sound
import grid
import punchers
import random
import graphics


class Player(collision.PunchableGravityCollision):
    CHECK_STEPS = 4
    TERMINAL_VELOCITY = 20.0

    MAX_HEALTH = 3
    JUMP_SPEED = 9
    MOVE_SPEED = 4
    MOVE_ACC = 0.8
    MOVE_DEC = 1.5
    EXT_DEC = 0.5

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

    def __init__(self, level, x, y, camera):
        super().__init__(level, self.WIDTH, self.HEIGHT, self.TERMINAL_VELOCITY,
                         x, y)
        self.health = self.MAX_HEALTH
        self.dead = False
        self.offscreen_direction = 0

        # external velocities - caused by non-player forces
        self.ext_x_vel = 0.0

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

        x = self._gridbox.x - cam.x
        y = self._gridbox.y - cam.y
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

    def update(self):
        """moves body based on velocity and acceleration"""
        self.collide_void = not self.dead
        self.take_inputs()
        self.update_animation()
        super().update()
        self.check_offscreen()

    def take_inputs(self):
        # Jumping
        if (pygame.K_p in events.keys.held_keys or pygame.K_z in events.keys.held_keys or
                pygame.K_w in events.keys.held_keys or pygame.K_UP in events.keys.held_keys or
                pygame.K_SPACE in events.keys.held_keys):
            if self.grounded and not self.dead:
                self.jump()

        # Moving left & right
        if not self.dead:
            if (pygame.K_LEFT in events.keys.held_keys or
                    pygame.K_a in events.keys.held_keys):
                self.move_left()

            elif (pygame.K_RIGHT in events.keys.held_keys or
                  pygame.K_d in events.keys.held_keys):
                self.move_right()

            # Decelerate when you stop moving
            else:
                self.stay_still()

        elif self.dead and self.grounded:
            self.x_vel = 0
            self.ext_x_vel = 0

        if events.keys.pressed_key == pygame.K_r:
            self.respawn()

    def move_left(self):
        self.x_vel += -self.MOVE_ACC
        self.x_vel = max(self.x_vel, -self.MOVE_SPEED)

        if self.ext_x_vel > 0:
            self.ext_x_vel -= self.EXT_DEC
            if self.ext_x_vel < 0:
                self.ext_x_vel = 0

    def move_right(self):
        self.x_vel += self.MOVE_ACC
        self.x_vel = min(self.x_vel, self.MOVE_SPEED)

        if self.ext_x_vel < 0:
            self.ext_x_vel += self.EXT_DEC
            if self.ext_x_vel > 0:
                self.ext_x_vel = 0

    def stay_still(self):
        self.run_sound_frame = self.RUN_SOUND_DELAY

        if self.x_vel < 0:
            self.x_vel += self.MOVE_DEC
            if self.x_vel > 0:
                self.x_vel = 0

        elif self.x_vel > 0:
            self.x_vel -= self.MOVE_DEC
            if self.x_vel < 0:
                self.x_vel = 0

        if self.ext_x_vel < 0:
            self.ext_x_vel += self.EXT_DEC
            if self.ext_x_vel > 0:
                self.ext_x_vel = 0

        elif self.ext_x_vel > 0:
            self.ext_x_vel -= self.EXT_DEC
            if self.ext_x_vel < 0:
                self.ext_x_vel = 0

    def jump(self):
        self.y_vel = -self.JUMP_SPEED
        self.JUMP_SOUNDS.play_random(0.3)
        self.tumble = False

    def respawn(self):
        self.REVIVE_SOUNDS.play_random(0.15)
        self.set_health(self.MAX_HEALTH)
        self.tumble = False
        self.x = self.respawn_x
        self.y = self.respawn_y
        self._stop_x()
        self._stop_y()

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

    def update_animation(self):
        if not self.dead:
            if not self.grounded:
                if self.tumble:
                    if self.facing == const.LEFT:
                        self.sprite.set_anim(self.TUMBLE_LEFT_ID)
                    else:
                        self.sprite.set_anim(self.TUMBLE_RIGHT_ID)

                # Jumping animation
                else:
                    if self.facing == const.LEFT:
                        self.sprite.set_anim(self.JUMP_LEFT_ID)
                    else:
                        self.sprite.set_anim(self.JUMP_RIGHT_ID)

                    if self.y_vel < -self.JUMP_SPEED + 2.5:
                        self.sprite.frame = 0
                    elif self.y_vel < -self.JUMP_SPEED + 5:
                        self.sprite.frame = 1
                    elif self.y_vel < -self.JUMP_SPEED + 7.5:
                        self.sprite.frame = 2
                    elif self.y_vel < 0:
                        self.sprite.frame = 3
                    elif self.y_vel < 2.5:
                        self.sprite.frame = 4
                    else:
                        self.sprite.frame = 5

            else:
                self.tumble = False

            if (pygame.K_LEFT in events.keys.held_keys or
                    pygame.K_a in events.keys.held_keys):

                if self.grounded:
                    self.sprite.set_anim(self.RUN_LEFT_ID)

                if not self.tumble:
                    self.facing = const.LEFT

                self.update_wall_push(const.LEFT)

                # Plays running sound
                if self.sprite.anim != self.WALL_PUSH_LEFT_ID:
                    if self.grounded:
                        if self.run_sound_frame < self.RUN_SOUND_DELAY:
                            self.run_sound_frame += 1
                        else:
                            self.run_sound_frame = 0
                            self.RUN_SOUNDS.play_random(random.random() / 4 + 0.75)

            elif (pygame.K_RIGHT in events.keys.held_keys or
                  pygame.K_d in events.keys.held_keys):

                if self.grounded:
                    self.sprite.set_anim(self.RUN_RIGHT_ID)

                if not self.tumble:
                    self.facing = const.RIGHT

                self.update_wall_push(const.RIGHT)

                if self.sprite.anim != self.WALL_PUSH_RIGHT_ID:
                    if self.grounded:
                        if self.run_sound_frame < self.RUN_SOUND_DELAY:
                            self.run_sound_frame += 1
                        else:
                            self.run_sound_frame = 0
                            self.RUN_SOUNDS.play_random(random.random() / 2 + 0.5)

            else:
                if self.grounded:
                    if self.facing == const.LEFT:
                        self.sprite.set_anim(self.IDLE_LEFT_ID)
                    elif self.facing == const.RIGHT:
                        self.sprite.set_anim(self.IDLE_RIGHT_ID)

        elif self.dead and self.grounded:
            if self.facing == const.LEFT:
                self.sprite.set_anim(self.DEAD_GROUNDED_LEFT_ID)
            elif self.facing == const.RIGHT:
                self.sprite.set_anim(self.DEAD_GROUNDED_RIGHT_ID)

        elif self.dead:
            if self.facing == const.LEFT:
                self.sprite.set_anim(self.DEAD_FALL_LEFT_ID)
            else:
                self.sprite.set_anim(self.DEAD_FALL_RIGHT_ID)

            if self.y_vel < -self.JUMP_SPEED + 2.5:
                self.sprite.frame = 0
            elif self.y_vel < -self.JUMP_SPEED + 5:
                self.sprite.frame = 1
            elif self.y_vel < -self.JUMP_SPEED + 7.5:
                self.sprite.frame = 2
            elif self.y_vel < 0:
                self.sprite.frame = 3
            elif self.y_vel < 2.5:
                self.sprite.frame = 4
            else:
                self.sprite.frame_delay += 1
                if self.sprite.frame_delay > 1:
                    self.sprite.frame_delay = 0

                    if self.sprite.frame == 5:
                        self.sprite.frame = 6
                    else:
                        self.sprite.frame = 5

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

    def _get_hit(self):
        super()._get_hit()
        self.tumble = True
        self.change_health(-1)
        self.camera.shake(6, 1)

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
