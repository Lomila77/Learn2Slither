import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
from src.utils import get_random_position
from src.config import GREEN_APPLE, RED_APPLE, SNAKE_HEAD, CELL_SIZE


class Object(ABC):
    def __init__(self, board: list[list[int]]) -> None:
        super().__init__()

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class Apple(Object, ABC):
    def __init__(self, board: list[list[int]], id: int):
        self.id = id
        forbidden_ids = [SNAKE_HEAD, GREEN_APPLE, RED_APPLE]
        self.x, self.y = get_random_position(board, forbidden_ids)
        self.pos = Vector2(self.x, self.y)

    @abstractmethod
    def nourrish(self):
        pass


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

    def nourrish(self):
        return self.nutrients

    def get_position(self):
        return self.x, self.y


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

    def nourrish(self):
        return self.nutrients

    def get_position(self):
        return self.x, self.y
