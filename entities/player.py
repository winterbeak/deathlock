import pygame
import constants as const

from entities import collision
import events
import sound
import grid
import random
import graphics


class Player(collision.PunchableGravityCollision):
    jump_key = events.Keybind([pygame.K_p, pygame.K_z, pygame.K_w,
                               pygame.K_UP, pygame.K_SPACE])
    left_key = events.Keybind([pygame.K_a, pygame.K_LEFT])
    right_key = events.Keybind([pygame.K_d, pygame.K_RIGHT])
    respawn_key = events.Keybind([pygame.K_o])

    TERMINAL_VELOCITY = 20.0

    COYOTE_TIME = 5
    JUMP_BUFFER = 5

    MAX_HEALTH = 3
    JUMP_SPEED = 9
    MOVE_SPEED = 4.5
    MOVE_ACC = 0.8
    MOVE_DEC = 1.5

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

    def __init__(self, level, camera):
        x = grid.x_of(level.player_spawn.col)
        y = grid.y_of(level.player_spawn.row)
        super().__init__(level, self.WIDTH, self.HEIGHT, self.TERMINAL_VELOCITY,
                         x, y)
        self._health = self.MAX_HEALTH
        self.dead = False
        self.offscreen_direction = 0

        self.level = level  # reference to the level layout
        self.camera = camera

        self.tumble = False

        self.checkpoint = None

        self._coyote_timer = 0
        self._jump_buffer = 0

        self.sprite = graphics.AnimInstance(self.ANIMSHEET)
        self.facing = const.LEFT

        self.heart_sprites = [graphics.AnimInstance(self.HEART_SHEET) for _ in range(self.MAX_HEALTH)]
        for heart_sprite in range(1, self.MAX_HEALTH):
            self.heart_sprites[heart_sprite].set_anim(heart_sprite)

        self.run_sound_frame = self.RUN_SOUND_DELAY

    @property
    def respawn_x(self):
        if self.checkpoint:
            return grid.x_of(self.checkpoint.col)
        return self.hard_respawn_x

    @property
    def respawn_y(self):
        if self.checkpoint:
            return grid.y_of(self.checkpoint.row)
        return self.hard_respawn_y

    @property
    def hard_respawn_x(self):
        return grid.x_of(self.level.player_spawn.col)

    @property
    def hard_respawn_y(self):
        return grid.y_of(self.level.player_spawn.row)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
        if self._health <= 0:
            self.dead = True
        else:
            self.dead = False

    def draw(self, surf, cam):
        self.sprite.update()

        x = self._gridbox.x - cam.x
        y = self._gridbox.y - cam.y
        self.sprite.draw_frame(surf, x, y)

    def update(self):
        self.collide_deathlock = not self.dead
        self._update_timers()
        self._take_inputs()
        self._update_animation()
        self._collide_checkpoints()
        super().update()

    def _update_timers(self):
        if self.grounded:
            self._coyote_timer = self.COYOTE_TIME
        elif self._coyote_timer > 0:
            self._coyote_timer -= 1

        if self.jump_key.is_pressed and not self.dead:
            self._jump_buffer = self.JUMP_BUFFER
        elif self._jump_buffer > 0:
            self._jump_buffer -= 1

    def _take_inputs(self):
        if not self.dead:
            if self.jump_key.is_pressed and self._coyote_timer > 0:
                self.jump()

            if self.grounded and self._jump_buffer > 0:
                self.jump()

            if self.left_key.is_held:
                self._move_left()

            elif self.right_key.is_held:
                self._move_right()

            # Decelerate when you stop moving
            else:
                self._stay_still()

        elif self.dead and self.grounded:
            self.x_vel = 0
            self.puncher_x_vel = 0

        if self.respawn_key.is_pressed:
            self.respawn()

    def _move_left(self):
        self.x_vel += -self.MOVE_ACC
        self.x_vel = max(self.x_vel, -self.MOVE_SPEED)

        if self.puncher_x_vel > 0:
            self.puncher_x_vel -= self.puncher_deceleration
            if self.puncher_x_vel < 0:
                self.puncher_x_vel = 0

    def _move_right(self):
        self.x_vel += self.MOVE_ACC
        self.x_vel = min(self.x_vel, self.MOVE_SPEED)

        if self.puncher_x_vel < 0:
            self.puncher_x_vel += self.puncher_deceleration
            if self.puncher_x_vel > 0:
                self.puncher_x_vel = 0

    def _stay_still(self):
        self.run_sound_frame = self.RUN_SOUND_DELAY

        if self.x_vel < 0:
            self.x_vel += self.MOVE_DEC
            if self.x_vel > 0:
                self.x_vel = 0

        elif self.x_vel > 0:
            self.x_vel -= self.MOVE_DEC
            if self.x_vel < 0:
                self.x_vel = 0

    def jump(self):
        self._coyote_timer = 0
        self.y_vel = -self.JUMP_SPEED
        self.JUMP_SOUNDS.play_random(0.3)
        self.tumble = False

    def respawn(self):
        self.REVIVE_SOUNDS.play_random(0.15)
        self.health = self.MAX_HEALTH
        self.tumble = False
        self.x = self.respawn_x
        self.y = self.respawn_y

    def hard_respawn(self):
        self._deactivate_checkpoint()
        self._stop_x()
        self._stop_y()
        self.respawn()

    def _deactivate_checkpoint(self):
        if self.checkpoint:
            self.checkpoint.active = False
            self.checkpoint = None

    def _update_animation(self):
        if not self.dead:
            if not self.grounded:
                if self.tumble:
                    if self.facing == const.LEFT:
                        self.sprite.set_anim(self.TUMBLE_LEFT_ID)
                    else:
                        self.sprite.set_anim(self.TUMBLE_RIGHT_ID)

                # Jumping
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

            # Moving left
            if self.left_key.is_held:

                if self.grounded:
                    self.sprite.set_anim(self.RUN_LEFT_ID)

                if not self.tumble:
                    self.facing = const.LEFT

                self._update_wall_push(const.LEFT)

                # Plays running sound
                if self.sprite.anim != self.WALL_PUSH_LEFT_ID:
                    if self.grounded:
                        if self.run_sound_frame < self.RUN_SOUND_DELAY:
                            self.run_sound_frame += 1
                        else:
                            self.run_sound_frame = 0
                            self.RUN_SOUNDS.play_random(random.random() / 4 + 0.75)

            elif self.right_key.is_held:

                if self.grounded:
                    self.sprite.set_anim(self.RUN_RIGHT_ID)

                if not self.tumble:
                    self.facing = const.RIGHT

                self._update_wall_push(const.RIGHT)

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

    def _update_wall_push(self, direction):
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

    def _get_hit(self):
        super()._get_hit()
        self.tumble = True
        self.health -= 1
        self.camera.shake(6, 1)

    def _collide_checkpoints(self):
        col = grid.col_at(self.center_x)
        row = grid.row_at(self.center_y)
        if self._level.has_tile(grid.CheckpointRay, col, row):
            self._deactivate_checkpoint()

            ray = self._level.get_tile(grid.CheckpointRay, col, row)
            checkpoint = ray.checkpoint
            checkpoint.active = True

            self.checkpoint = checkpoint

    def _update_puncher_vel(self):
        if self.grounded:
            if self.puncher_x_vel < 0 and not self.left_key.is_held:
                self.puncher_x_vel += self.puncher_deceleration
                if self.puncher_x_vel > 0:
                    self.puncher_x_vel = 0

            elif self.puncher_x_vel > 0 and not self.right_key.is_held:
                self.puncher_x_vel -= self.puncher_deceleration
                if self.puncher_x_vel < 0:
                    self.puncher_x_vel = 0

    @property
    def touching_goal(self):
        col = grid.col_at(self.center_x)
        row = grid.row_at(self.center_y)
        return self._level.has_tile(grid.PlayerGoalZone, col, row)
