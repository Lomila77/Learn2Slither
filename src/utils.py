import random
from pygame.math import Vector2

UP = Vector2(0, -1)
DOWN = Vector2(0, 1)
RIGHT = Vector2(1, 0)
LEFT = Vector2(-1, 0)


def get_random_position(board: list[list[int]], forbidden_ids: list[int] = []):
    valid_positions: list[tuple[int, int]] = []
    for i, row in enumerate(board):
        for j, pos in enumerate(row):
            if pos not in forbidden_ids:
                valid_positions.append((i, j))

    if not valid_positions:
        raise ValueError("No place for object")

    x, y = random.choice(valid_positions)
    return x, y
