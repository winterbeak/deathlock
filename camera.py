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

        self.slide_x_direction = 0
        self.slide_y_direction = 0
        self.slide_x_frame = self.SLIDE_LENGTH
        self.slide_y_frame = self.SLIDE_LENGTH
        self.slide_x_c = 0.0
        self.slide_y_c = 0.0

        self.last_slide_frame = False

        self.shake_frame = 0
        self.shake_length = 0
        self.shake_intensity = 0

        self.sliding = False

    def update(self):
        if self.last_slide_frame:
            self.last_slide_frame = False

            # If statements fix a bug where you enter another room
            # and the camera stops sliding on the same frame
            if self.slide_x_frame >= self.SLIDE_LENGTH:
                if self.slide_y_frame >= self.SLIDE_LENGTH:
                    self.sliding = False

        if self.slide_x_frame < self.SLIDE_LENGTH:
            self.slide_x_frame += 1

            if self.slide_x_direction == const.LEFT:
                self.base_x = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_x_frame) + self.slide_x_c
            elif self.slide_x_direction == const.RIGHT:
                self.base_x = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_x_frame) + self.slide_x_c

            if self.slide_x_frame >= self.SLIDE_LENGTH:
                if self.slide_y_frame >= self.SLIDE_LENGTH:
                    self.last_slide_frame = True

        if self.slide_y_frame < self.SLIDE_LENGTH:
            self.slide_y_frame += 1

            if self.slide_y_direction == const.UP:
                self.base_y = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_y_frame) + self.slide_y_c
            elif self.slide_y_direction == const.DOWN:
                self.base_y = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_y_frame) + self.slide_y_c

            if self.slide_y_frame >= self.SLIDE_LENGTH:
                if self.slide_x_frame >= self.SLIDE_LENGTH:
                    self.last_slide_frame = True

        if self.shake_frame < self.shake_length:
            self.shake_frame += 1
            self.x = self.base_x + random.randint(-self.shake_intensity, self.shake_intensity)
            self.y = self.base_y + random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.x = self.base_x
            self.y = self.base_y

    def slide(self, direction):
        self.sliding = True

        if direction == const.LEFT or direction == const.RIGHT:
            self.slide_x_direction = direction
            self.slide_x_frame = 0
            self.slide_x_c = self.base_x

        elif direction == const.UP or direction == const.DOWN:
            self.slide_y_direction = direction
            self.slide_y_frame = 0
            self.slide_y_c = self.base_y

        else:
            print("Invalid direction to camera.slide()!")

    def shake(self, length, intensity):
        self.shake_frame = 0
        self.shake_length = length
        self.shake_intensity = intensity

    def move_point(self, point):
        return (point[0] - self.x, point[1] - self.y)

    def move_rect(self, rect):
        return (rect.x - self.x, rect.y - self.y, rect.w, rect.h)
