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

        self.body_pos: list[tuple[int, int]] = [Vector2(x, y)]
        area = self.brain.actions
        for _ in range(2):
            last_pos = self.body_pos[-1]
            for action in self.brain.actions:
                new_place = last_pos + action
                if (
                    0 <= new_place.x < board.shape[0] and
                    0 <= new_place.y < board.shape[1] and
                    board[int(new_place.x)][int(new_place.y)] == EMPTY_CASE and
                    new_place not in self.body_pos
                ):
                    self.body_pos.append(new_place)
                    break

        if self.get_length() != 3:
            print(self.body_pos)
            raise ValueError("The snake is too short... No place available")

    def draw(self, screen):
        for i, pos in enumerate(self.body_pos):
            rect = pygame.Rect(
                pos.x * CELL_SIZE,
                pos.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            if i == 0:
                color = pygame.Color("white")
            else:
                color = pygame.Color("grey")
            pygame.draw.rect(screen, color, rect)

    def get_position(self):
        return int(self.body_pos[0].x), int(self.body_pos[0].y)

    def get_body_position(self):
        return self.body_pos[1:]

    def get_length(self):
        return len(self.body_pos)

    def moove(self, action):
        for piece_of_snake in self.body_pos:
            piece_of_snake += action

    # TODO: Comment ralonger la queue du serpent ?
    def eat(self, nutrient: int = 0):
        if nutrient == 1:
            self.body_pos.insert(1, tuple(self.head_pos))
        else:
            self.body_pos.pop()

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
        
