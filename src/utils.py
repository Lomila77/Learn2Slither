import random
import pickle
from pygame.math import Vector2
from src.config import LOAD_WEIGHTS

UP = Vector2(0, -1)
DOWN = Vector2(0, 1)
RIGHT = Vector2(1, 0)
LEFT = Vector2(-1, 0)

EMPTY_CASE = 0
SNAKE_HEAD = 1
SNAKE_BODY = 2
GREEN_APPLE = 3
RED_APPLE = 4
WALL = 5

DIRECTIONS_ICON = [
    '⬆️',
    '⬇️',
    '⬅️',
    '➡️',
]

SYMBOLS = {
    0: '⬛',
    1: '🟢',
    2: '🟩',
    3: '🍏',
    4: '🍎',
    5: '🌊',
    6: '  ',
    7: '⬆️',
    8: '⬇️',
    9: '⬅️',
    10: '➡️',
}


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


if __name__ == "__main__":
    with open(LOAD_WEIGHTS, "rb") as f:
        q_table = pickle.load(f)
    print(f"Q_TABLE: {q_table}")
