import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
from src.utils import get_random_position
from src.config import EMPTY_CASE, GREEN_APPLE, RED_APPLE, SNAKE_HEAD, CELL_SIZE


class Object(ABC):
    def __init__(self, board: list[list[int]]) -> None:
        super().__init__()

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass


class Apple(Object, ABC):
    forbidden_ids = [SNAKE_HEAD, GREEN_APPLE, RED_APPLE]

    def __init__(self, board: list[list[int]], id: int):
        super().__init__(board)
        self.id = id
        self.x, self.y = get_random_position(board, self.forbidden_ids)
        board[self.x][self.y] = id
        self.pos = Vector2(self.x, self.y)
        self.nutrients = 0

    def nourrish(self, board):
        board[int(self.pos.x)][int(self.pos.y)] = EMPTY_CASE
        x, y = get_random_position(board, self.forbidden_ids)
        self.pos = Vector2(x, y)
        board[x][y] = self.id
        return self.nutrients

    def get_position(self):
        return self.pos


class GreenApple(Apple):
    def __init__(self, board: list[list[int]]):
        super().__init__(board, GREEN_APPLE)
        self.nutrients: int = 1

    def draw(self, screen):
        apple_rect = pygame.Rect(
            int(self.pos.x * CELL_SIZE),
            int(self.pos.y * CELL_SIZE),
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, pygame.Color('green'), apple_rect)


class RedApple(Apple):
    def __init__(self, board: list[list[int]]):
        super().__init__(board, RED_APPLE)
        self.nutrients: int = -1

    def draw(self, screen):
        apple_rect = pygame.Rect(
            int(self.pos.x * CELL_SIZE),
            int(self.pos.y * CELL_SIZE),
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, pygame.Color('red'), apple_rect)

