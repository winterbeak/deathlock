import grid
import random  # don't worry, it's only for the first and final room


ROOM_W = grid.Room.WIDTH
ROOM_H = grid.Room.HEIGHT


def intro_fallway():
    room = grid.Room()

    room.change_rect(0, 0, 8, ROOM_H, grid.WALL)   # Left wall
    room.change_rect(17, 0, 8, ROOM_H, grid.WALL)  # Right wall
    room.change_rect(8, 0, 1, ROOM_H, grid.SPIKE_EMIT_RIGHT)   # Left spikes
    room.change_rect(16, 0, 1, ROOM_H, grid.SPIKE_EMIT_LEFT)   # Right spikes

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 2)

    return room


def fallway_disturbance():
    """The first room."""
    room = grid.Room()

    room.change_rect(0, 0, 9, 7, grid.WALL)  # Top left
    room.change_rect(0, 18, 9, 7, grid.WALL)  # Bottom left
    room.change_rect(16, 0, 9, 7, grid.WALL)  # Top right
    room.change_rect(16, 18, 9, 7, grid.WALL)  # Bottom right

    room.change_rect(0, 0, 3, ROOM_H, grid.WALL)  # Left wall
    room.change_rect(22, 0, 3, ROOM_H, grid.WALL)  # Right wall

    for y in range(0, 7):
        if random.randint(0, y // 4) == 0:
            room.change_point(8, y, grid.SPIKE_EMIT_RIGHT)
        if random.randint(0, y // 4) == 0:
            room.change_point(16, y, grid.SPIKE_EMIT_LEFT)

    room.change_rect(9, 12, 7, 1, grid.WALL)  # Platform
    room.change_point(8, 21, grid.SPIKE_EMIT_RIGHT)
    room.change_point(16, 21, grid.SPIKE_EMIT_LEFT)

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 10)

    return room


def fallway_disturbance_2():
    """The first room 2."""
    room = grid.Room()

    room.change_rect(0, 0, 9, 8, grid.WALL)  # Top left
    room.change_rect(0, 17, 9, 8, grid.WALL)  # Bottom left
    room.change_rect(16, 0, 9, 8, grid.WALL)  # Top right
    room.change_rect(16, 17, 9, 8, grid.WALL)  # Bottom right

    room.change_rect(0, 0, 4, ROOM_H, grid.WALL)  # Left wall
    room.change_rect(21, 0, 4, ROOM_H, grid.WALL)  # Right wall

    room.change_rect(8, 12, 9, 1, grid.SPIKE_EMIT_DOWN)  # Platform

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 10)

    return room


def lets_go_left():
    """Right is overrated."""
    room = grid.Room()

    room.change_rect(2, 15, 23, 10, grid.WALL)  # Floor
    room.change_rect(0, 20, 2, 5, grid.WALL)  # Valley
    room.change_rect(20, 0, 5, 25, grid.WALL)  # Wall
    room.change_point(2, 17, grid.SPIKE_EMIT_LEFT)

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 13)

    return room


def run_into_it():
    room = grid.Room()

    room.change_rect(0, 20, 25, 5, grid.WALL)  # Floor
    room.change_point(2, 20, grid.SPIKE_EMIT_UP)

    room.change_rect(24, 0, 1, 20, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(23, 18)

    return room


def triple_bounce():
    room = grid.Room()

    room.change_rect(0, 20, 25, 5, grid.WALL)  # Floor
    room.change_rect(0, 20, 19, 1, grid.SPIKE_EMIT_UP)

    room.change_rect(24, 0, 1, 20, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(23, 18)

    return room


def ow_my_head():
    room = grid.Room()

    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 20, 21, 5, grid.WALL)  # Floor
    room.change_rect(4, 20, 16, 1, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 0, 9, 16, grid.WALL)  # Top left protrusion

    room.change_rect(24, 0, 1, 20, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(23, 18)

    return room


def far_enough():
    room = grid.Room()

    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 0, 6, 14, grid.WALL)  # Right wall
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Rightmost wall
    room.change_rect(0, 17, 21, 8, grid.WALL)  # Floor

    room.change_point(15, 17, grid.SPIKE_EMIT_UP)

    room.change_rect(1, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 15)

    return room


def spike_spike():
    room = grid.Room()

    room.change_rect(24, 0, 1, 25, grid.WALL)  # Rightmost wall
    room.change_rect(15, 0, 6, 14, grid.WALL)  # Left wall
    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 24, 21, 1, grid.WALL)  # Low floor
    room.change_rect(13, 17, 12, 8, grid.WALL)  # High floor
    room.change_rect(8, 17, 1, 8, grid.WALL)  # Pillar

    room.change_point(8, 17, grid.SPIKE_EMIT_UP)

    room.change_rect(21, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(22, 15)

    return room


def not_far_enough():
    room = grid.Room()

    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 0, 6, 14, grid.WALL)  # Right wall
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Rightmost wall
    room.change_rect(0, 17, 21, 8, grid.WALL)  # Floor

    room.change_point(11, 17, grid.SPIKE_EMIT_UP)
    room.change_point(9, 13, grid.SPIKE_EMIT_RIGHT)

    room.change_rect(1, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 15)

    return room


def elbow():
    room = grid.Room()

    room.change_rect(20, 0, 1, 5, grid.WALL)  # Left wall
    room.change_rect(20, 4, 5, 1, grid.WALL)  # Floor

    room.change_point(20, 2, grid.SPIKE_EMIT_RIGHT)

    room.change_rect(21, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(22, 2)

    return room


def ready_for_launch():
    room = grid.Room()

    room.change_rect(0, 4, 1, 20, grid.WALL)  # Left wall
    room.change_rect(0, 12, 11, 13, grid.WALL)  # Left ledge (lower)
    room.change_rect(7, 9, 4, 3, grid.WALL)  # Left ledge (higher)
    room.change_rect(20, 9, 5, 16, grid.WALL)  # Right ledge
    room.change_rect(0, 24, 25, 1, grid.WALL)  # Floor

    room.change_point(0, 9, grid.SPIKE_EMIT_RIGHT)
    room.change_point(10, 9, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 0, 1, 4, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 10)

    return room


def ready_for_landing():
    room = grid.Room()

    room.change_rect(0, 9, 1, 14, grid.WALL)  # Left wall
    room.change_rect(0, 14, 11, 11, grid.WALL)  # Left ledge
    room.change_rect(12, 0, 2, 1, grid.WALL)  # Overhang ceiling
    room.change_rect(7, 0, 5, 13, grid.WALL)  # Overhang left
    room.change_rect(11, 12, 9, 1, grid.WALL)  # Overhang floor

    room.change_rect(12, 9, 3, 3, grid.WALL)  # Square
    room.change_rect(18, 6, 3, 3, grid.WALL)  # L-bottom
    room.change_rect(21, 3, 3, 6, grid.WALL)  # L-right

    room.change_rect(24, 0, 1, 9, grid.WALL)  # Low-middle square

    for x in range(20, 25):  # Overhang staircase
        y = (x - 8)
        room.change_rect(x, y, 1, 2, grid.WALL)

    room.change_rect(0, 24, 25, 1, grid.WALL)  # Floor

    room.change_point(0, 11, grid.SPIKE_EMIT_RIGHT)
    room.change_point(11, 12, grid.SPIKE_EMIT_DOWN)

    room.change_rect(21, 3, 3, 1, grid.SPIKE_EMIT_UP)  # Spikes in top right

    # Left entrance
    room.change_rect(0, 0, 1, 9, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 12)

    # Right entrance
    room.change_rect(24, 9, 1, 7, grid.CHECKPOINT_ZONE[1])
    room.add_checkpoint(23, 13)

    # Top entrance
    room.change_rect(14, 0, 10, 1, grid.CHECKPOINT_ZONE[2])
    room.add_checkpoint(19, 4)

    return room


def up_and_up_and_up():
    room = grid.Room()

    room.change_rect(0, 24, 25, 1, grid.WALL)  # Floor
    room.change_rect(22, 8, 3, 17, grid.WALL)  # Right wall
    room.change_point(0, 17, grid.WALL)  # Leftmost ledge

    room.change_point(9, 24, grid.SPIKE_EMIT_UP)
    room.change_point(14, 18, grid.SPIKE_EMIT_UP)
    room.change_point(19, 12, grid.SPIKE_EMIT_UP)

    # Left entrance
    room.change_rect(0, 18, 1, 6, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 22)

    # Right entrance
    room.change_rect(24, 0, 1, 8, grid.CHECKPOINT_ZONE[1])
    room.add_checkpoint(23, 6)

    return room


def crossing_rooms():
    room = grid.Room()

    room.change_rect(0, 8, 10, 17, grid.WALL)  # Launcher floor
    room.change_rect(10, 0, 1, 25, grid.WALL)  # Launcher wall
    room.change_rect(0, 0, 10, 1, grid.WALL)  # Launcher ceiling

    room.change_rect(0, 12, 25, 13, grid.WALL)  # Triple floor
    room.change_rect(11, 4, 3, 1, grid.WALL)  # Triple spike platforms
    room.change_rect(14, 8, 3, 1, grid.WALL)

    room.change_point(1, 8, grid.SPIKE_EMIT_UP)  # Launcher spikes
    room.change_point(10, 7, grid.SPIKE_EMIT_LEFT)

    room.change_point(12, 4, grid.SPIKE_EMIT_UP)  # Triple spikes
    room.change_point(15, 8, grid.SPIKE_EMIT_UP)
    room.change_point(18, 12, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 1, 1, 7, grid.CHECKPOINT_ZONE[0])  # Launcher entrance
    room.add_checkpoint(3, 6)

    room.change_rect(11, 0, 14, 1, grid.CHECKPOINT_ZONE[1])
    room.change_rect(24, 0, 1, 12, grid.CHECKPOINT_ZONE[1])
    room.add_checkpoint(20, 11)

    return room


def climber():
    room = grid.Room()

    room.change_rect(24, 5, 1, 20, grid.WALL)  # Right wall
    room.change_rect(13, 0, 12, 1, grid.WALL)  # Ceiling
    room.change_rect(13, 0, 1, 6, grid.WALL)  # Top left wall

    room.change_rect(20, 5, 5, 1, grid.WALL)  # Ledge

    for y in range(6, 20, 6):
        room.change_rect(10, y, 4, 1, grid.WALL)
        room.change_rect(10, y, 1, 5, grid.WALL)
        room.change_rect(10, y + 4, 4, 1, grid.WALL)
        room.change_point(13, y + 5, grid.WALL)

        room.change_rect(17, y + 1, 3, 3, grid.WALL)

    room.change_point(13, 24, grid.WALL)

    room.change_point(23, 5, grid.SPIKE_EMIT_UP)

    room.change_rect(14, 24, 10, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(22, 21)

    return room


def uncrossable_chasm():
    room = grid.Room()

    room.change_rect(0, 5, 7, 20, grid.WALL)  # Left ledge
    room.change_rect(18, 9, 7, 15, grid.WALL)  # Right ledge
    room.change_rect(0, 24, 25, 1, grid.WALL)  # Floor
    room.change_point(0, 0, grid.WALL)  # Top left corner

    room.change_point(6, 5, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 1, 1, 4, grid.CHECKPOINT_ZONE[0])  # Left entrance
    room.change_rect(1, 0, 24, 1, grid.CHECKPOINT_ZONE[0])  # Top entrance
    room.add_checkpoint(2, 4)

    return room


def secret_ceiling():
    room = grid.Room()

    room.change_rect(0, 0, 1, 25, grid.WALL)  # Left wall
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Right wall

    room.change_point(13, 21, grid.SPIKE_EMIT_RIGHT)

    room.change_rect(1, 24, 23, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 22)

    return room


def stand_in_weird_places():
    room = grid.Room()

    room.change_rect(0, 9, 1, 16, grid.WALL)  # Left wall
    room.change_rect(0, 14, 11, 11, grid.WALL)  # Left ledge
    room.change_rect(10, 4, 1, 10, grid.WALL)  # Blocker

    room.change_rect(19, 22, 6, 3, grid.WALL)  # Right ledge

    room.change_point(3, 14, grid.SPIKE_EMIT_UP)  # Lower initial launcher
    room.change_point(6, 9, grid.SPIKE_EMIT_UP)  # Higher initial launcher
    room.change_point(23, 22, grid.SPIKE_EMIT_UP)  # Solution launcher
    room.change_point(10, 22, grid.SPIKE_EMIT_RIGHT)  # Right launcher

    room.change_rect(0, 0, 1, 9, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(5, 11)

    room.change_rect(11, 24, 8, 1, grid.CHECKPOINT_ZONE[1])
    room.add_checkpoint(12, 23)

    return room


def the_big_jump():
    room = grid.Room()

    room.change_rect(24, 22, 1, 3, grid.WALL)
    room.change_point(24, 22, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 0, 1, 25, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(1, 23)

    return room


def safety_net():
    room = grid.Room()

    room.change_rect(2, 7, 23, 5, grid.WALL)  # Floor
    room.change_rect(0, 12, 25, 13, grid.WALL)  # Valley
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Wall

    room.change_point(2, 9, grid.SPIKE_EMIT_LEFT)

    room.change_rect(0, 0, 24, 1, grid.CHECKPOINT_ZONE[0])
    room.change_rect(0, 1, 1, 11, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(3, 6)

    return room


def fall_the_right_way():
    room = grid.Room()

    # Left stairs
    for step in range(3):
        room.change_rect(0, 22 + step, step * 5 + 5, 1, grid.WALL)

    # Right stairs
    for step in range(7):
        room.change_rect(18 + step, 22 - step * 3, 1, step * 3 + 3, grid.WALL)

    room.change_point(22, 0, grid.SPIKE_EMIT_RIGHT)

    room.change_rect(0, 0, 1, 22, grid.CHECKPOINT_ZONE[0])  # Left zone
    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])  # Top zone
    room.add_checkpoint(1, 20)

    return room


def run_run_jump():
    room = grid.Room()

    room.change_rect(0, 5, 9, 1, grid.WALL)  # Left floor
    room.change_rect(16, 3, 9, 1, grid.WALL)  # Right floor

    room.change_rect(0, 24, 25, 1, grid.WALL)  # Net bottom
    room.change_rect(0, 6, 1, 19, grid.WALL)  # Net left
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Net right

    room.change_point(0, 4, grid.SPIKE_EMIT_RIGHT)
    room.change_point(16, 3, grid.SPIKE_EMIT_UP)
    room.change_point(24, 2, grid.SPIKE_EMIT_LEFT)

    room.change_rect(0, 0, 1, 4, grid.CHECKPOINT_ZONE[0])  # Left
    room.change_rect(0, 0, 24, 1, grid.CHECKPOINT_ZONE[0])  # Right
    room.add_checkpoint(2, 3)

    return room


def wrong():
    room = grid.Room()

    room.change_rect(24, 0, 1, 25, grid.WALL)  # Right wall
    room.change_rect(0, 0, 25, 1, grid.WALL)  # Ceiling

    room.change_point(24, 24, grid.SPIKE_EMIT_LEFT)

    room.change_rect(0, 24, 23, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 23)

    return room


def extra_gravity():
    room = grid.Room()

    room.change_rect(0, 24, 9, 1, grid.WALL)  # Floor left
    room.change_rect(16, 24, 9, 1, grid.WALL)  # Floor right
    room.change_rect(0, 0, 25, 1, grid.WALL)  # Ceiling
    room.change_rect(0, 0, 1, 25, grid.WALL)  # Left wall

    room.change_rect(8, 19, 9, 1, grid.SPIKE_EMIT_DOWN)

    room.change_rect(24, 1, 1, 23, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(23, 22)

    return room


def left_down_town():
    room = grid.Room()

    room.change_rect(6, 10, 13, 15, grid.WALL)  # Floor
    room.change_rect(6, 5, 1, 5, grid.WALL)  # Left blocker
    room.change_rect(0, 0, 1, 25, grid.WALL)  # Left wall
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Right wall

    for step in range(2):
        room.change_point(19, step * 6 + 10, grid.WALL)
        room.change_point(23, step * 6 + 13, grid.WALL)

    room.change_point(19, 22, grid.WALL)

    room.change_point(6, 21, grid.SPIKE_EMIT_LEFT)
    room.change_point(8, 10, grid.SPIKE_EMIT_UP)

    room.change_rect(1, 0, 23, 1, grid.CHECKPOINT_ZONE[0])  # Top entrance
    room.add_checkpoint(16, 7)

    room.change_rect(19, 24, 5, 1, grid.CHECKPOINT_ZONE[1])  # Right entrance
    room.add_checkpoint(22, 23)

    return room


def how_to_go_left():
    room = grid.Room()

    room.change_rect(0, 17, 25, 8, grid.WALL)  # Floor
    room.change_rect(24, 0, 1, 17, grid.WALL)  # Right wall

    for step in range(7):
        x = step * 3 + 3
        y = 25 - (step * 2 + 10)
        h = step * 2 + 2
        room.change_rect(x, y, 3, h, grid.WALL)

    room.change_rect(21, 3, 3, 1, grid.SPIKE_EMIT_UP)

    room.change_rect(0, 0, 12, 1, grid.CHECKPOINT_ZONE[0])  # Left entrance
    room.add_checkpoint(1, 15)

    room.change_rect(12, 0, 12, 1, grid.CHECKPOINT_ZONE[1])  # Right entrance
    room.add_checkpoint(19, 3)

    return room


def mysteriously_easy():
    room = grid.Room()

    room.change_rect(0, 0, 12, 25, grid.WALL)  # Wall left
    room.change_rect(13, 17, 12, 8, grid.WALL)  # Floor right

    room.change_point(13, 17, grid.SPIKE_EMIT_UP)

    room.change_rect(24, 0, 1, 17, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(23, 15)

    return room


def funnel_vision():
    room = grid.Room()

    for step in range(4):
        w = 12 - step
        room.change_rect(0, step * 6, w, 6, grid.WALL)
        room.change_rect(13 + step, step * 6, w, 6, grid.WALL)

        for y in range(6):
            if random.randint(0, 4 - step) == 0:
                room.change_point(11 - step, step * 6 + y, grid.SPIKE_EMIT_RIGHT)

        for y in range(6):
            if random.randint(0, 4 - step) == 0:
                room.change_point(13 + step, step * 6 + y, grid.SPIKE_EMIT_LEFT)

    room.change_rect(0, 24, 9, 1, grid.WALL)
    room.change_rect(16, 24, 9, 1, grid.WALL)

    room.change_point(8, 24, grid.SPIKE_EMIT_RIGHT)
    room.change_point(16, 24, grid.SPIKE_EMIT_LEFT)

    room.change_point(12, 0, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 1)

    return room
