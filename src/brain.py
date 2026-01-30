from typing import Any
import numpy as np
from random import randint, uniform
from pygame.math import Vector2
from src.config import LEARNING_RATE, EPSILON_GREEDY
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
    WALL,
    load_q_table
)


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
        self.lr = LEARNING_RATE
        self.gamma = LEARNING_RATE - 0.01
        self.epsilon_greedy: float = EPSILON_GREEDY
        self.prev_state: tuple = None
        self.prev_action: int = 0
        self.prev_reward: int = 0
        self.prev_terminal: bool = False

    def get_length_q_table(self):
        return len(self.q_table)

    def reset(self):
        self.prev_state = None
        self.lr = LEARNING_RATE
        self.epsilon_greedy = 0.1
        self.prev_terminal = False

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
            # Si ce n'est pas le dernier element du corps
            # Le dernier elements du corps bougera avec l'action
            # if not head_pos + action == pos[-1]:
            #     self.prev_terminal = True
            #     return -11
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
            action = randint(0, 3)
        else:
            action = np.argmax(self.q_table[state])
        if self.epsilon_greedy > 0.01:
            self.epsilon_greedy = max(0.01, self.epsilon_greedy - 0.01)
        return action

    def get_state(self, x_axis: list[int], y_axis: list[int], pos: Vector2):
        def get_obj(array: list[int]):
            for i, obj in enumerate(array):
                if obj != EMPTY_CASE:
                    return (i, obj)
        axis = y_axis[:int(pos.y)]
        top = get_obj(axis[:: -1])
        bot = get_obj(y_axis[int(pos.y) + 1:])
        axis = x_axis[:int(pos.x)]
        left = get_obj(axis[:: -1])
        right = get_obj(x_axis[int(pos.x) + 1:])
        return (top, bot, left, right)

    def call_brain(
        self,
        x_axis: list[int],
        y_axis: list[int],
        pos: list[Vector2]
    ) -> Vector2:
        head_pos = pos[0]
        state = self.get_state(x_axis, y_axis, head_pos)
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        if self.prev_state is not None:
            self.q_table[self.prev_state][self.prev_action] = self.q_function(
                prev_q_sa=self.q_table[self.prev_state][self.prev_action],
                prev_reward=self.prev_reward,
                q_sa=max(self.q_table[state])
            )
        action_index: int = self.take_action(state)
        reward: int = self.get_reward(
            x_axis, y_axis, pos, self.actions[action_index])
        self.prev_state = state
        self.prev_action = action_index
        self.prev_reward = reward
        return self.prev_terminal, self.actions[action_index]