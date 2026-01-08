import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
from src.utils import get_random_position
from src.utils import (
    EMPTY_CASE, GREEN_APPLE, RED_APPLE, SNAKE_HEAD, SNAKE_BODY, WALL
)
from src.config import CELL_SIZE


class Object(ABC):
    def __init__(self, board: list[list[int]]) -> None:
        super().__init__()
        self.game_board = board

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass


class Apple(Object, ABC):
    forbidden_ids = [SNAKE_HEAD, GREEN_APPLE, SNAKE_BODY, RED_APPLE, WALL]

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
    def __init__(self, board: list[list[int]], interface: bool = True):
        super().__init__(board, GREEN_APPLE)
        self.interface = interface
        self.nutrients: int = 1
        if self.interface:
            image = pygame.image.load(
                'graphics/green_apple.png').convert_alpha()
            self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def draw(self, screen):
        apple_rect = pygame.Rect(
            int(self.pos.x * CELL_SIZE),
            int(self.pos.y * CELL_SIZE),
            CELL_SIZE,
            CELL_SIZE
        )
        screen.blit(self.image, apple_rect)


class RedApple(Apple):
    def __init__(self, board: list[list[int]], interface: bool = True):
        super().__init__(board, RED_APPLE)
        self.nutrients: int = -1
        self.interface = interface
        if self.interface:
            image = pygame.image.load('graphics/red_apple.png').convert_alpha()
            self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def draw(self, screen):
        apple_rect = pygame.Rect(
            int(self.pos.x * CELL_SIZE),
            int(self.pos.y * CELL_SIZE),
            CELL_SIZE,
            CELL_SIZE
        )
        screen.blit(self.image, apple_rect)

