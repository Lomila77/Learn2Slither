import pygame
from pygame.math import Vector2
from src.config import SNAKE_HEAD, SNAKE_BODY, EMPTY_CASE, CELL_SIZE
from src.brain import Brain
from src.object import Object
from src.utils import get_random_position


class Snake(Object):
    def __init__(self, board: list[list[int]]) -> None:
        self.head_id = SNAKE_HEAD
        self.body_id = SNAKE_BODY
        self.brain = Brain(board.shape)

        x, y = get_random_position(board)
        self.body: list[tuple[int, int]] = [Vector2(x, y)]
        for _ in range(2):
            last_pos = self.body[-1]
            for action in self.brain.actions:
                new_place = last_pos + action
                if (
                    0 <= new_place.x < board.shape[0] and
                    0 <= new_place.y < board.shape[1] and
                    board[int(new_place.x)][int(new_place.y)] == EMPTY_CASE and
                    new_place not in self.body
                ):
                    self.body.append(new_place)
                    break

        if self.get_length() != 3:
            print(self.body)
            raise ValueError("The snake is too short... No place available")

    def draw(self, screen):
        for i, pos in enumerate(self.body):
            rect = pygame.Rect(
                int(pos.x * CELL_SIZE),
                int(pos.y * CELL_SIZE),
                CELL_SIZE,
                CELL_SIZE
            )
            if i == 0:
                color = pygame.Color("white")
            else:
                color = pygame.Color("grey")
            pygame.draw.rect(screen, color, rect)

    def get_position(self):
        return int(self.body[0].x), int(self.body[0].y)

    def get_body_position(self):
        return self.body[1:]

    def get_length(self):
        return len(self.body)

    def move(self, action):
        body_copy = self.body[:-1]
        body_copy.insert(0, body_copy[0] + action)
        self.body = body_copy[:]

    # TODO: Comment ralonger la queue du serpent ?
    def eat(self, nutrient: int = 0):
        if nutrient == 1:
            self.body.insert(1, tuple(self.head_pos))
        else:
            self.body.pop()

    def watch(self, board):
        head_x, head_y = self.get_position()
        x_axis: list[tuple[int, int]] = []
        y_axis: list[tuple[int, int]] = []
        for row in board:
            for col in row:
                if row == head_x:
                    x_axis.append((row, col))
                elif col == head_y:
                    y_axis.append((row, col))
        return x_axis, y_axis

    def call_brain(self, board):
        x_axis, y_axis = self.watch(board)
        
