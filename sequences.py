import math

import pygame
import camera
import grid
import curves
import constants as const
import entities.collision


class TransitionCircle:
    def __init__(self, color):
        self.color = color
        self.radius = 0


class Sequence:
    CIRCLE_COUNT = 8
    CIRCLES_SPEEDUP_LENGTH = 30
    CIRCLES_SLOWDOWN_LENGTH = 15

    def __init__(self, level_names):
        self.level_names = level_names
        self._level_num = 0
        self.current = grid.Room(level_names[0])
        self.next = grid.Room(level_names[1])
        self.transitioning = False
        self.done_transitioning = False
        self._frame = 0
        self._circle_center = entities.collision.KinematicsPoint(0, 0)
        self._circle_slowdown_x = None
        self._circle_slowdown_y = None
        self._circles = []
        self._emitted_circles = 0

        t = 30
        self._pinhole_radius = 0
        scrn_diagonal = math.sqrt(const.SCRN_W ** 2 + const.SCRN_H ** 2)
        self._pinhole_radius_curve = curves.SineIn(0, scrn_diagonal, t)
        self.pinhole_surf = pygame.Surface((const.SCRN_W, const.SCRN_H))
        self.pinhole_surf.set_colorkey(const.TRANSPARENT)

        # Same amount of circles as grid PlayerGoal
        for i in range(self.CIRCLE_COUNT):
            color = (180 + 8 * i, 0, 0)
            self._circles.append(TransitionCircle(color))

    def next_level(self):
        self._level_num += 1
        self.current = self.next
        self.next = grid.Room(self.level_names[self._level_num + 1])

    def start_transition(self, player, static_level_surf):
        self.transitioning = True
        self._pinhole_radius_curve.restart()
        self._start_circles(player)

        self.current.draw_static(self.pinhole_surf, camera.zero_camera, False)
        self.next.draw_static(static_level_surf, camera.zero_camera)

    def _end_transition(self):
        self._circle_slowdown_x = None
        self._circle_slowdown_y = None
        self.transitioning = False
        self.done_transitioning = True

    def _start_circles(self, player):
        self._frame = 0
        self._circle_center.x = player.center_x
        self._circle_center.y = player.center_y
        self._circle_center.x_vel = player.x_vel
        self._circle_center.y_vel = player.y_vel

        target_x = grid.center_x_of(self.next.player_spawn.col)
        target_y = grid.center_y_of(self.next.player_spawn.row)
        x = target_x - self._circle_center.x
        vx = player.x_vel
        y = target_y - self._circle_center.y
        vy = player.y_vel
        t = self.CIRCLES_SPEEDUP_LENGTH + 10
        self._circle_center.x_acc = 2 * (x - vx * t) / (t ** 2)
        self._circle_center.y_acc = 2 * (y - vy * t) / (t ** 2)

        self._circles = player.level.player_goal.circles

    def update(self):
        if self._frame == self.CIRCLES_SPEEDUP_LENGTH:
            self._circle_center.x_acc = 0
            self._circle_center.y_acc = 0
            x = self._circle_center.x
            y = self._circle_center.y
            target_x = grid.center_x_of(self.next.player_spawn.col)
            target_y = grid.center_y_of(self.next.player_spawn.row)
            t = self.CIRCLES_SLOWDOWN_LENGTH
            self._circle_slowdown_x = curves.SineOut(x, target_x, t)
            self._circle_slowdown_y = curves.SineOut(y, target_y, t)
            self._circle_slowdown_x.restart()
            self._circle_slowdown_y.restart()
        elif self._circle_slowdown_x and not self._circle_slowdown_x.active:
            self._end_transition()
            self.next_level()
        elif self._frame > self.CIRCLES_SPEEDUP_LENGTH:
            self._circle_slowdown_x.update()
            self._circle_slowdown_y.update()
            self._circle_center.x = self._circle_slowdown_x.current_value
            self._circle_center.y = self._circle_slowdown_y.current_value
        self._frame += 1
        self._circle_center.update()

        if self._frame > 10:
            self._pinhole_radius_curve.update()

    def draw_pinhole(self, surf):
        goal_x = grid.center_x_of(self.current.player_goal.col)
        goal_y = grid.center_y_of(self.current.player_goal.row)

        pinhole_radius = self._pinhole_radius_curve.current_value

        center = (int(goal_x), int(goal_y))
        radius = int(pinhole_radius) + grid.TILE_W
        width = min(radius // 10 + 5 + grid.TILE_W, radius)
        pygame.draw.circle(self.pinhole_surf, const.TRANSPARENT, center, radius)
        surf.blit(self.pinhole_surf, (0, 0))

        pygame.draw.circle(surf, const.RED, center, radius, width)

    def draw_player_circle(self, surf):
        x = self._circle_center.x
        y = self._circle_center.y
        pygame.draw.circle(surf, (255, 0, 0), (int(x), int(y)), 50)
