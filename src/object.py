import pygame
from pygame.math import Vector2
from abc import ABC, abstractmethod
from src.utils import get_random_position
from src.utils import (
    EMPTY_CASE, GREEN_APPLE, RED_APPLE, SNAKE_HEAD, SNAKE_BODY, WALL
)


class Object(ABC):

    def __init__(self, board: list[list[int]], cell_size: int) -> None:
        super().__init__()
        self.game_board = board
        self.cell_size = cell_size

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass


class Apple(Object, ABC):
    forbidden_ids = [SNAKE_HEAD, GREEN_APPLE, SNAKE_BODY, RED_APPLE, WALL]

    def __init__(self, board: list[list[int]], cell_size: int, id: int):
        super().__init__(board, cell_size)
        self.id = id
        row, col = get_random_position(board, self.forbidden_ids)
        board[row][col] = id
        self.pos = Vector2(col, row)
        self.nutrients = 0

    def nourrish(self, board):
        board[int(self.pos.y)][int(self.pos.x)] = EMPTY_CASE
        row, col = get_random_position(board, self.forbidden_ids)
        self.pos = Vector2(col, row)
        board[row][col] = self.id
        return self.nutrients

    def get_position(self):
        return self.pos

    def draw(self, screen):
        apple_rect = pygame.Rect(
            int(self.pos.x * self.cell_size),
            int(self.pos.y * self.cell_size),
            self.cell_size,
            self.cell_size
        )
        screen.blit(self.image, apple_rect)


class GreenApple(Apple):
    def __init__(
        self, board: list[list[int]], cell_size: int, interface: bool = True
    ):
        super().__init__(board, cell_size, GREEN_APPLE)
        self.interface = interface
        self.nutrients: int = 1
        if self.interface:
            image = pygame.image.load(
                'graphics/green_apple.png').convert_alpha()
            self.image = pygame.transform.scale(
                image, (self.cell_size, self.cell_size))


class RedApple(Apple):
    def __init__(
        self, board: list[list[int]], cell_size: int, interface: bool = True
    ):
        super().__init__(board, cell_size, RED_APPLE)
        self.nutrients: int = -1
        self.interface = interface
        if self.interface:
            image = pygame.image.load('graphics/red_apple.png').convert_alpha()
            self.image = pygame.transform.scale(
                image, (self.cell_size, self.cell_size))
