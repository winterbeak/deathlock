import constants as const
import math


class Camera:
    SLIDE_LENGTH = 24
    SLIDE_A = const.SCRN_W  # assumes square screen
    SLIDE_K = ((2 * math.pi) / SLIDE_LENGTH) / 4

    def __init__(self):
        self.x = 0.0
        self.y = 0.0

        self.slide_direction = 0
        self.slide_frame = self.SLIDE_LENGTH
        self.slide_c = 0.0

        self.last_slide_frame = False

    def update(self):
        if self.slide_frame < self.SLIDE_LENGTH:
            self.slide_frame += 1

            if self.slide_direction == const.LEFT:
                self.x = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c
            elif self.slide_direction == const.RIGHT:
                self.x = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c

            elif self.slide_direction == const.UP:
                self.y = -self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c
            elif self.slide_direction == const.DOWN:
                self.y = self.SLIDE_A * math.sin(self.SLIDE_K * self.slide_frame) + self.slide_c

            if self.slide_frame == self.SLIDE_LENGTH:
                self.last_slide_frame = True

    def slide(self, direction):
        self.slide_direction = direction
        self.slide_frame = 0
        if direction == const.LEFT or direction == const.RIGHT:
            self.slide_c = self.x
        elif direction == const.UP or direction == const.DOWN:
            self.slide_c = self.y
        else:
            print("Invalid direction to camera.slide()!")
