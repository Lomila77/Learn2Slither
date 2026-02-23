from typing import Any
import numpy as np
from random import randint, uniform
from pygame.math import Vector2
from src.utils import (
    _cfg,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    SNAKE_HEAD,
    SNAKE_BODY,
    GREEN_APPLE,
    RED_APPLE,
    EMPTY_CASE,
    WALL,
    load_q_table
)


# TODO: Changer la gestion des states
class Brain:
    def __init__(
        self,
        shape: list[int],
        starting_position: Vector2,
        x_axis: list[int],
        y_axis: list[int],
        snake: Any,
        q_table: bool = False
    ) -> None:
        self.actions = [
            UP,
            DOWN,
            LEFT,
            RIGHT
        ]
        self.q_table: tuple = {}
        if q_table:
            self.q_table = load_q_table()
        self.lr = _cfg["learning_rate"]
        self.gamma = self.lr - 0.01
        self.epsilon_greedy: float = _cfg["epsilon_greedy"]
        self.force_exploration = _cfg["force_exploration"]
        self.prev_state: tuple = None
        self.prev_action: int = 0
        self.prev_reward: int = 0
        self.prev_terminal: bool = False

    def get_length_q_table(self):
        return len(self.q_table)

    def reset(self):
        self.prev_state: tuple = None
        self.prev_action: int = 0
        self.prev_reward: int = 0
        self.prev_terminal: bool = False
        self.lr = _cfg["learning_rate"]
        self.epsilon_greedy = _cfg["epsilon_greedy"]

    def get_reward(
        self,
        x_axis: list[int],
        y_axis: list[int],
        pos: list[Vector2],
        action: Vector2
    ) -> int:
        head_pos = pos[0]
        if action.x != 0:
            id = x_axis[int(head_pos.x + action.x)]
        if action.y != 0:
            id = y_axis[int(head_pos.y + action.y)]
        if id == EMPTY_CASE or id == SNAKE_HEAD:
            return -1
        elif id == RED_APPLE:
            return -8
        elif id == GREEN_APPLE:
            return +15  # +10 ?
        elif id == SNAKE_BODY:
            self.prev_terminal = True
            return -10
        elif id == WALL:
            self.prev_terminal = True
            return -10
        return -1

    def q_function(
        self,
        prev_q_sa: float,
        prev_reward: float,
        q_sa: float,
    ) -> float:
        if self.prev_terminal:
            esperance = prev_q_sa + self.lr * (
                prev_reward - prev_q_sa)

        else:
            esperance = prev_q_sa + self.lr * (
                prev_reward + self.gamma * q_sa - prev_q_sa)
        self.lr = max(self.lr * 0.9999, 0.01)
        return esperance

    def take_action(self, state):
        if uniform(0, 1) < self.epsilon_greedy:
            if self.force_exploration:
                zero_actions = [
                    idx for idx, value in enumerate(self.q_table[state])
                    if value == 0
                ]
                if zero_actions:
                    action = zero_actions[randint(0, len(zero_actions) - 1)]
                else:
                    action = randint(0, 3)

            else:
                action = randint(0, 3)
        else:
            action = np.argmax(self.q_table[state])
        if self.epsilon_greedy > 0.01:
            self.epsilon_greedy = max(0.01, self.epsilon_greedy - 0.01)
        return action

    def get_state(self, x_axis: list[int], y_axis: list[int], pos: Vector2):
    # TODO: avoir une gestion de state comme cela:
        # premiere serie pour detecter un danger a proximite directe
        def get_obj(array: list[int], name: str):
            for i, obj in enumerate(array):
                if i == 0:
                    if obj == WALL or obj == SNAKE_BODY:
                        danger = ("close_danger_" + name, True)
                    else:
                        danger = ("close_danger_" + name, False)
                    if obj == GREEN_APPLE:
                        reward = ("close_reward_" + name, True)
                    else:
                        reward = ("close_reward_" + name, False)
                    if obj == RED_APPLE:
                        punish = ("close_punish_" + name, True)
                    else:
                        punish = ("close_punish_" + name, False)
                break
            for i, obj in enumerate(array):
                if obj == GREEN_APPLE:
                    green_apple: tuple = ("green_apple_on_" + name, True)
                    break
                if i == len(array) - 1 and obj != GREEN_APPLE:
                    green_apple: tuple = ("green_apple_on_" + name, False)
            for i, obj in enumerate(array):
                if obj == RED_APPLE:
                    red_apple = ("red_apple_on_" + name, True)
                    break
                if i == len(array) - 1 and obj != RED_APPLE:
                    red_apple: tuple = ("red_apple_on_" + name, False)
            return (danger, green_apple, red_apple, reward, punish)
        # def get_obj(array: list[int]):
        #     for i, obj in enumerate(array):
        #         if i == len(array) - 1:
        #             return (i, np.float64(WALL))
        #         if obj != EMPTY_CASE:
        #             return (i, obj)
        axis = y_axis[:int(pos.y)]
        top = get_obj(axis[:: -1], "top")
        bot = get_obj(y_axis[int(pos.y) + 1:], "bot")
        axis = x_axis[:int(pos.x)]
        left = get_obj(axis[:: -1], "left")
        right = get_obj(x_axis[int(pos.x) + 1:], "right")
        print("NEW Q_TABLES")
        print(top)
        print(bot)
        print(left)
        print(right)
        return (top, bot, left, right)

    def call_brain(
        self,
        x_axis: list[int],
        y_axis: list[int],
        pos: list[Vector2],
        training: bool = False
    ) -> Vector2:
        head_pos = pos[0]
        state = self.get_state(x_axis, y_axis, head_pos)
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        if self.prev_state is not None and training:
            self.q_table[self.prev_state][self.prev_action] = self.q_function(
                prev_q_sa=self.q_table[self.prev_state][self.prev_action],
                prev_reward=self.prev_reward,
                q_sa=max(self.q_table[state])
            )
        self.prev_action: int = self.take_action(state)
        print(f"FUTUR ACTION: {self.prev_action}")
        if not self.prev_terminal:
            self.prev_reward: int = self.get_reward(
                x_axis, y_axis, pos, self.actions[self.prev_action])
        self.prev_state = state
        return self.prev_terminal, self.actions[self.prev_action]
