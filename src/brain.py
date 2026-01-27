import pickle, json
from typing import Any
import numpy as np
from random import randint, uniform
from pygame.math import Vector2
from src.config import LEARNING_RATE, LOAD_WEIGHTS
from src.utils import (
    UP,
    DOWN,
    LEFT,
    RIGHT,
    SNAKE_HEAD,
    SNAKE_BODY,
    GREEN_APPLE,
    RED_APPLE,
    EMPTY_CASE,
    WALL
)


class Brain:
    def __init__(
        self,
        shape: list[int],
        starting_position: Vector2,
        x_axis: list[int],
        y_axis: list[int],
        snake: Any,
        load_q_table: bool = False
    ) -> None:
        self.actions = [
            UP,
            DOWN,
            LEFT,
            RIGHT
        ]
        self.q_table: tuple = {}
        if load_q_table:
            self.q_table = self.load_q_table()
        self.lr = LEARNING_RATE
        self.epsilon_greedy: float = 0.1
        self.prev_state: tuple = None
        self.prev_action: int = 0
        self.prev_reward: int = 0

    def get_length_q_table(self):
        return len(self.q_table)

    def reset(self):
        self.prev_state = None
        self.lr = LEARNING_RATE

    def load_q_table(self):
        with open(LOAD_WEIGHTS, "rb") as f:
            q_table = pickle.load(f)
        return q_table

    def save_q_table(self, shape: list[int], epochs: int, name: str):
        data: dict = {
            "shape": shape,
            "epochs": epochs,
            "q_table_len": self.get_length_q_table(),
            "learning_rate": self.lr,
        }
        directory: str = "./weights/"
        filename: str = f"{shape[0]}*{shape[1]}_epochs_{epochs}_{name}"
        with open(directory + filename + ".pck", "wb") as f:
            pickle.dump(self.q_table, f)
        with open(directory + filename + "_config" + ".json", "w") as f:
            json.dump(data, f)

    def get_reward(self, id: int) -> int:
        if id == EMPTY_CASE or id == SNAKE_HEAD:
            return -1
        elif id == RED_APPLE:
            return -10
        elif id == GREEN_APPLE:
            return +30  # +10 ?
        elif id == SNAKE_BODY:
            return -20
        elif id == WALL:
            return -20

    def q_function(
        self,
        prev_state: float,
        prev_reward: float,
        state: float,
    ) -> float:
        esperance = prev_state + self.lr * (
            prev_reward + (self.lr - 0.01) * state - prev_state)
        if self.lr > 0:
            self.lr -= 0.01
        return esperance

    def take_action(self, state):
        if uniform(0, 1) < self.epsilon_greedy:
            return randint(0, 3)
        return np.argmax(self.q_table[state])

    def get_state(self, x_axis: list[int], y_axis: list[int], pos: Vector2):
        def get_obj(array: list[int]):
            for i, obj in enumerate(array):
                if obj != EMPTY_CASE:
                    return (i, obj)
        axis = y_axis[:int(pos.x)]
        top = get_obj(axis[:: -1])
        bot = get_obj(y_axis[int(pos.x) + 1:])
        axis = x_axis[:int(pos.y)]
        left = get_obj(axis[:: -1])
        right = get_obj(x_axis[int(pos.y) + 1:])
        return (top, bot, left, right)

    def call_brain(
        self, x_axis: list[int], y_axis: list[int], pos: Vector2
    ) -> Vector2:
        state = self.get_state(x_axis, y_axis, pos)
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        if self.prev_state is not None:
            self.q_table[self.prev_state][self.prev_action] = self.q_function(
                self.prev_reward,
                self.q_table[self.prev_state][self.prev_action],
                max(self.q_table[state])
            )
        action_index: int = self.take_action(state)
        print(f"X_AXIS: {x_axis}")
        print(f"POS: {int(pos.x)}")
        print(f"X_AXIS[POS.X]: {x_axis[int(pos.x)]}")
        print(f"ACTION_INDEX_X: {int(self.actions[action_index].x)}")
        reward: int = self.get_reward(x_axis[int(pos.x) + int(self.actions[action_index].x)])
        self.prev_state = state
        self.prev_action = action_index
        self.prev_reward = reward
        return self.actions[action_index]
