import constants as const
import random
import math


class Camera:
    SLIDE_LENGTH = 24
    SLIDE_A = const.SCRN_W  # assumes square screen
    SLIDE_K = ((2 * math.pi) / SLIDE_LENGTH) / 4

    def __init__(self):
        self.base_x = 0.0  # pre shake position
        self.base_y = 0.0
        self.x = 0.0
        self.y = 0.0

        self.slide_direction = 0
        self.slide_frame = self.SLIDE_LENGTH
        self.slide_c = 0.0

        self.last_slide_frame = False

        self.shake_frame = 0
        self.shake_length = 0
        self.shake_intensity = 0

    def update(self):
        if self.slide_frame < self.SLIDE_LENGTH:
            self.slide_frame += 1

            if self.slide_direction == const.LEFT:
                self.base_x = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c
            elif self.slide_direction == const.RIGHT:
                self.base_x = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c

            elif self.slide_direction == const.UP:
                self.base_y = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c
            elif self.slide_direction == const.DOWN:
                self.base_y = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c

            if self.slide_frame == self.SLIDE_LENGTH:
                self.last_slide_frame = True

        if self.shake_frame < self.shake_length:
            self.shake_frame += 1
            self.x = self.base_x + random.randint(-self.shake_intensity, self.shake_intensity)
            self.y = self.base_y + random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.x = self.base_x
            self.y = self.base_y

    def slide(self, direction):
        self.slide_direction = direction
        self.slide_frame = 0
        if direction == const.LEFT or direction == const.RIGHT:
            self.slide_c = self.base_x
        elif direction == const.UP or direction == const.DOWN:
            self.slide_c = self.base_y
        else:
            print("Invalid direction to camera.slide()!")

    def shake(self, length, intensity):
        self.shake_frame = 0
        self.shake_length = length
        self.shake_intensity = intensity
