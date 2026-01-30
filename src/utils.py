import random
import pickle
import json
from pygame.math import Vector2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator
from src.config import (
    LEARNING_RATE,
    LOAD_WEIGHTS,
    MAP_SHAPE,
    FILENAME,
    DIRECTORY,
    LOAD_DATA,
    EPSILON_GREEDY,
    FORCE_EXPLORATION
)

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


def get_name(epochs, add_to_name: str):
    shape = f"{MAP_SHAPE[0]}*{MAP_SHAPE[1]}_"
    epoch = f"epochs_{epochs}_"
    filename = f"{FILENAME}_"
    return DIRECTORY + shape + epoch + filename + add_to_name


def smooth(values: list[int], window=200):
    return pd.Series(values).rolling(
        window=window, min_periods=1
    ).mean().tolist()


def draw_step_graph(epochs: int, nb_steps: list[int], name: str):
    length = min(epochs, len(nb_steps))
    df = pd.DataFrame({
        "epoch": range(length),
        "steps": smooth(nb_steps[:length], 1000),
    })
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 4))

    sns.lineplot(data=df, x="epoch", y="steps",
                 ax=ax, color="steelblue", linewidth=1,
                 label="Pas")

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Pas")
    ax.xaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_minor_locator(MultipleLocator(1000))

    ax.set_xlim(0, epochs)
    y_max = df[["steps"]].max().max()
    ax.set_ylim(0, y_max + 1)

    ax.legend()
    plt.tight_layout()
    plt.savefig(name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def draw_object_graph(
    epochs: int,
    nb_green_apples_ate: list[int],
    nb_red_apples_ate: list[int],
    snake_sizes: list[int],
    name: str
):
    length = min(
        epochs,
        len(nb_green_apples_ate),
        len(nb_red_apples_ate),
        len(snake_sizes)
    )
    df = pd.DataFrame({
        "epoch": range(length),
        "green_apple": smooth(nb_green_apples_ate[:length], 1000),
        "red_apple": smooth(nb_red_apples_ate[:length], 1000),
        "snake_size": smooth(snake_sizes[:length], 1000),
    })
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 4))

    sns.lineplot(data=df, x="epoch", y="green_apple",
                 ax=ax, color="green", linewidth=1,
                 label="Pommes vertes")

    sns.lineplot(data=df, x="epoch", y="red_apple",
                 ax=ax, color="red", linewidth=1,
                 label="Pommes rouges")

    sns.lineplot(data=df, x="epoch", y="snake_size",
                 ax=ax, color="black", linewidth=1,
                 label="Taille serpent")

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Valeur")
    ax.xaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_minor_locator(MultipleLocator(1000))

    ax.set_xlim(0, epochs)
    y_max = df[["green_apple", "red_apple", "snake_size"]].max().max()
    ax.set_ylim(0, y_max + 1)

    ax.legend()
    plt.tight_layout()
    plt.savefig(name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def load_q_table():
    with open(LOAD_WEIGHTS, "rb") as f:
        q_table = pickle.load(f)
    return q_table


def save_data(epochs: int, q_table):
    data: dict = {
        "shape": MAP_SHAPE,
        "epochs": epochs,
        "q_table_len": len(q_table),
        "learning_rate": LEARNING_RATE,
        "epsilon_greedy": EPSILON_GREEDY,
        "force_exploration": FORCE_EXPLORATION
    }
    with open(get_name(epochs, "weights") + ".pck", "wb") as f:
        pickle.dump(q_table, f)
    with open(get_name(epochs, "config") + ".json", "w") as f:
        json.dump(data, f)


def load_data():
    with open(LOAD_DATA, "r") as f:
        data = json.load(f)
    return data


def print_q_table(q_table: dict[tuple]):
    def format_state(state, width):
        labels = [
            DIRECTIONS_ICON[0],
            DIRECTIONS_ICON[1],
            DIRECTIONS_ICON[2],
            DIRECTIONS_ICON[3]
        ]
        parts = []
        for (dist, obj), label in zip(state, labels):
            sym = SYMBOLS.get(obj, "?")
            parts.append(f"{label} : ({dist} - {sym})".center(width))
        return " | ".join(parts)
    
    def format_action(values, width):
        labels = [
            DIRECTIONS_ICON[0],
            DIRECTIONS_ICON[1],
            DIRECTIONS_ICON[2],
            DIRECTIONS_ICON[3]
        ]  
        parts = []
        for value, label in zip(values, labels):
            parts.append(f"{label} :  {value:.2f}  ".center(width))
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

    width = 10
    new_states = 0
    for state, values in q_table.items():
        # if not all(v == 0 for v in values):
        if not 0 in values:
            state_str = format_state(state, width)
            actions_str = format_action(values, width)
            # actions_str = " | ".join(f"{float(v):.2f}" for v in values)
            print(f"{state_str}\n{actions_str}")
            print("---------------------------------------------------------")
        else:
            new_states += 1
    print(f"State unexplored: {new_states} / {len(q_table)}")


if __name__ == "__main__":
    with open(LOAD_WEIGHTS, "rb") as f:
        q_table = pickle.load(f)
    print_q_table(q_table)
