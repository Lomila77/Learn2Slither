import numpy as np
from random import randint, uniform
from pygame.math import Vector2
from src.config import LEARNING_RATE
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
        y_axis: list[int]
    ) -> None:
        self.actions = [
            UP,
            DOWN,
            LEFT,
            RIGHT
        ]

        self.q_table = np.zeros((shape[0], shape[1], len(self.actions)))
        self.lr = LEARNING_RATE
        self.board = np.zeros((shape[0], shape[1]))
        self.epsilon_greedy: float = 0.1
        self.movements: list[Vector2] = []

    def update_board(
        self, x_axis: list[int], y_axis: list[int], state: Vector2
    ) -> None:
        self.board = np.zeros_like(self.board)
        self.board[int(state.x)] = x_axis
        for x in range(self.board.shape[0]):
            self.board[x][int(state.y)] = y_axis[x]

    def get_area(self, state: Vector2) -> list[list[float]]:
        area = []
        up = state + UP
        area.append(self.q_table[int(up.x)][int(up.y)])
        down = state + DOWN
        area.append(self.q_table[int(down.x)][int(down.y)])
        left = state + LEFT
        area.append(self.q_table[int(left.x)][int(left.y)])
        right = state + RIGHT
        area.append(self.q_table[int(right.x)][int(right.y)])
        return area

    def get_reward(self, state: Vector2) -> int:
        id = self.board[int(state.x)][int(state.y)]
        if id == EMPTY_CASE or id == SNAKE_HEAD:
            return -1
        elif id == RED_APPLE:
            return -10
        elif id == GREEN_APPLE:
            return +10
        elif id == SNAKE_BODY:
            return -20
        elif id == WALL:
            return -20
        print(f"ID = {id}")

    def q_function(
        self,
        reward: float,
        state: float,
        next_state: float,
    ) -> float:
        esperance = state + self.lr * (reward + (self.lr - 0.01) * next_state - state)
        self.lr -= 0.01
        return esperance

    def take_action(self, state):
        if uniform(0, 1) < self.epsilon_greedy:
            return randint(0, 3)
        return np.argmax(self.q_table[int(state.x)][int(state.y)])

    def call_brain(
        self, x_axis: list[int], y_axis: list[int], state: Vector2
    ) -> Vector2:
        if not self.is_finished():
            self.update_board(x_axis, y_axis, state)
            action_index: int = self.take_action(state)
            reward: int = self.get_reward(state) # next_etat pas current
            self.movements.append(self.actions[action_index])
            tmp_next = state + self.actions[action_index]
            next_state: Vector2 = np.argmax(
                self.q_table[int(tmp_next.x)][int(tmp_next.y)])
            print(f"TYPE: {type(next_state)}")
            self.q_table[int(state.x)][int(state.y)][action_index] = self.q_function(
                reward, self.board[int(state.x)][int(state.y)], next_state)
            return self.actions[action_index]
