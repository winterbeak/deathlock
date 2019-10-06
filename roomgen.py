import grid


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

    room.change_rect(1, 18, 8, 1, grid.SPIKE_EMIT_UP)
    room.change_rect(16, 18, 8, 1, grid.SPIKE_EMIT_UP)
    room.change_rect(0, 0, 3, ROOM_H, grid.WALL)  # Left wall
    room.change_rect(22, 0, 3, ROOM_H, grid.WALL)  # Right wall

    room.change_rect(10, 12, 5, 1, grid.WALL)  # Platform
    room.change_point(8, 21, grid.SPIKE_EMIT_RIGHT)
    room.change_point(16, 21, grid.SPIKE_EMIT_LEFT)

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 2)

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
    room.add_checkpoint(12, 2)

    return room


def lets_go_left():
    """Right is overrated."""
    room = grid.Room()

    room.change_rect(0, 20, 25, 5, grid.WALL)  # Floor
    room.change_rect(20, 0, 5, 25, grid.WALL)  # Wall
    room.change_point(2, 20, grid.SPIKE_EMIT_UP)

    room.change_rect(9, 0, 7, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(12, 2)

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

    room.change_point(14, 17, grid.SPIKE_EMIT_UP)

    room.change_rect(1, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 15)

    return room


def too_far():
    room = grid.Room()

    room.change_rect(24, 0, 1, 25, grid.WALL)  # Rightmost wall
    room.change_rect(15, 0, 6, 14, grid.WALL)  # Left wall
    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 17, 21, 8, grid.WALL)  # Floor

    room.change_point(4, 17, grid.SPIKE_EMIT_UP)

    room.change_rect(21, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(22, 15)

    return room


def not_far_enough():
    room = grid.Room()

    room.change_rect(0, 0, 1, 25, grid.WALL)  # Leftmost wall
    room.change_rect(4, 0, 6, 14, grid.WALL)  # Right wall
    room.change_rect(24, 0, 1, 25, grid.WALL)  # Rightmost wall
    room.change_rect(0, 17, 21, 8, grid.WALL)  # Floor

    room.change_point(12, 17, grid.SPIKE_EMIT_UP)
    room.change_point(9, 11, grid.SPIKE_EMIT_RIGHT)

    room.change_rect(1, 0, 3, 1, grid.CHECKPOINT_ZONE[0])
    room.add_checkpoint(2, 15)

    return room
