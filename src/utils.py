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
}


def get_random_position(board: list[list[int]], forbidden_ids: list[int] = []):
    valid_positions: list[tuple[int, int]] = []
    for i, row in enumerate(board):
        for j, pos in enumerate(row):
            if pos not in forbidden_ids:
                # i = row (y), j = column (x)
                valid_positions.append((i, j))

    if not valid_positions:
        raise ValueError("No place for object")

    return random.choice(valid_positions)


def print_q_table(q_table: dict[tuple]):
    def format_state(state):
        # state = ((d_top, obj_top), (d_bot, obj_bot), (d_left, obj_left), (d_right, obj_right))
        print(f"STATE={state}")
        labels = [
            DIRECTIONS_ICON[0],
            DIRECTIONS_ICON[1],
            DIRECTIONS_ICON[2],
            DIRECTIONS_ICON[3]
        ]
        parts = []
        for (dist, obj), label in zip(state, labels):
            sym = SYMBOLS.get(obj, "?")
            parts.append(f"{label}:{dist:2d} - {sym}")
        return " | ".join(parts)

    header_state = "STATE".ljust(40)
    header_actions = " ".join(f"{name:^10}" for name in [
        DIRECTIONS_ICON[0],
        DIRECTIONS_ICON[1],
        DIRECTIONS_ICON[2],
        DIRECTIONS_ICON[3]
    ])
    print(header_state + " | " + header_actions)
    print("-" * (len(header_state) + 3 + len(header_actions)))

    for state, values in q_table.items():
        state_str = format_state(state)[:40].ljust(40)
        actions_str = " ".join(f"{v:10.2f}" for v in values)
        print(f"{state_str} | {actions_str}")


if __name__ == "__main__":
    with open(LOAD_WEIGHTS, "rb") as f:
        q_table = pickle.load(f)
    print_q_table(q_table)
