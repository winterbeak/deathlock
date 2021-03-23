import math
import abc


class Curve(abc.ABC):
    def __init__(self, start_value, end_value, length):
        """ An abstract base class for mathematical curves.

        When used for animation, the curve is inclusive on both extreme
        values.  That means:
        start_value occurs on frame 0.
        end_value occurs on the last frame.
        length is the amount of frames including frame 0 and self.last_frame.
        """
        self.frame = 0
        self.last_frame = length - 1
        self.length = length
        self.start = start_value
        self.end = end_value
        self.active = False

    @property
    def current_value(self):
        return self.value_at(self.frame)

    def update(self):
        if self.active:
            self.frame += 1

            if self.frame >= self.last_frame:
                self.active = False

    def restart(self):
        """ Activates the curve starting from frame 0. """
        self.frame = 0
        self.active = True

    @abc.abstractmethod
    def value_at(self, frame):
        pass


class Linear(Curve):
    def __init__(self, start_value, end_value, length):
        """ Represents a linear function. """
        super().__init__(start_value, end_value, length)
        self.b = start_value
        self.m = (end_value - self.b) / (length - 1)

    def value_at(self, frame):
        return self.m * frame + self.b


class Quadratic(Curve):
    def __init__(self, start_value, end_value, length):
        """ Abstract base class for all quadratic functions.

        This class in itself is not usable as an animation.  It simply
        implements the four variables that define a quadratic in vertex
        form: k, a, c and d.
        """
        super().__init__(start_value, end_value, length)
        self.k = 1
        self.a = 1
        self.c = 0
        self.d = 0

    def value_at(self, frame):
        inside = self.k * frame - self.d
        return self.a * (inside * inside) + self.c


class QuadraticArc(Quadratic):
    def __init__(self, start_value, peak_value, length):
        """ Represents a quadratic which rises then falls (or vice versa).

        Animations using this class will start at start_value, peak
        at peak_value, then end at start_value.
        """
        super().__init__(start_value, peak_value, length)
        self.c = peak_value
        self.d = (length - 1) / 2
        self.a = (start_value - self.c) / (self.d ** 2)


class Sine(Curve):
    def __init__(self, start_value, end_value, length):
        """ Abstract base class for all sine functions.

        This class in itself is not usable as an animation.  It simply
        implements the four variables that define a sine function in
        transformations form: k, a, c and d.
        """
        super().__init__(start_value, end_value, length)
        self.k = 1
        self.a = 1
        self.c = 0
        self.d = 0

    def value_at(self, frame):
        inside = self.k * (frame - self.d)
        return self.a * math.sin(inside) + self.c


class SineOut(Sine):
    def __init__(self, start_value, end_value, length):
        """ Represents a sine function that fades out.

        Animations using this class start by moving fast, gradually
        slowing down until the end is reached.  Sort of like the first
        quarter of the default sine function.
        """
        super().__init__(start_value, end_value, length)
        self.k = (2 * math.pi) / ((length - 1) * 4)
        self.a = end_value - start_value
        self.c = start_value


class SineIn(Sine):
    def __init__(self, start_value, end_value, length):
        """ Represents a sine function that fades in.

        Animations using this class start by moving slow, gradually
        speeding up until the end is reached.  Sort of like the second
        quarter of the default sine function.
        """
        super().__init__(start_value, end_value, length)
        self.k = (2 * math.pi) / ((length - 1) * 4)
        self.a = end_value - start_value
        self.c = start_value
        self.d = length
