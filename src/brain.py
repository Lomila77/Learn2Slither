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
    EMPTY_CASE
)


# QUESTION :
    # Comment on place les rewards ?

#TODO: Rajouter un "WALL" ?

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

    def get_reward(self, state: Vector2) -> int:
        id = self.board[int(state.x)][int(state.y)]
        if id == EMPTY_CASE or id == SNAKE_HEAD:
            return 0
        elif id == RED_APPLE:
            return -10
        elif id == GREEN_APPLE:
            return +10
        elif id == SNAKE_BODY:
            return -20
        print(f"ID = {id}")
        # elif id == WALL:
        #     return -20
    
    def get_state(self, position: Vector2) -> list[int]:
        return self.q_table[position.x][position.y]

    def q_function(
        self,
        reward: float,
        state: ,
        action: Vector2,
        next_state: Vector2,
    ) -> float:
        # Cherche a maximiser l'esperance
        # r + learning_rate * max(action[t + 1]) * q_function(state[t + 1], action[t+1])
        esperance = state + self.lr * (reward + (self.lr - 0.01) * next_state - state)
        self.lr -= 0.01
        return esperance

    def is_finished(self):
        return False

    def take_action(self, state):
        if uniform(0, 1) < self.epsilon_greedy:
            return randint(0, 3)
        return np.argmax(self.q_table[int(state.x)][int(state.y)])

    # TODO: rename par actionS
    def call_brain(
        self, x_axis: list[int], y_axis: list[int], state: Vector2
    ) -> Vector2:
        if not self.is_finished():
            self.update_board(x_axis, y_axis, state)
            reward: int = self.get_reward(state)
            action_index: int = self.take_action(state)
            self.movements.append(self.actions[action_index])
            tmp_next = state + self.actions[action_index]
            next_state: Vector2 = np.argmax(
                self.q_table[int(tmp_next.x)][int(tmp_next.y)])
            print(f"TYPE: {type(next_state)}")
            self.q_table[int(state.x)][int(state.y)][action_index] = self.q_function(
                reward, self.board[state.x][state.y], action_index, next_state)
            return self.actions[action_index]
