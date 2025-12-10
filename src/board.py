
import pygame
import sys
import numpy as np
from src.config import (
    SNAKE_HEAD,
    SNAKE_BODY,
    GREEN_APPLE,
    RED_APPLE,
    EMPTY_CASE,
    CELL_SIZE,
    FRAMERATE,
    SCREEN_UPDATE,
    SPEED
)
from src.object import GreenApple, RedApple
from src.snake import Snake


class Board:
    def __init__(self, shape: list[int]) -> None:
        if len(shape) != 2:
            raise ValueError("Need to be a 2d map")
        if not isinstance(
            shape[0], (int, np.int64)
        ) or not isinstance(
            shape[1], (int, np.int64)
        ):
            raise ValueError("Shape must be 2d int array")
        if shape[0] < 10 and shape[1] < 10:
            raise ValueError("Too small, higher than 10 pls")
        # TODO: TEST
        pygame.init()
        self.screen = pygame.display.set_mode(
            (CELL_SIZE * shape[0], CELL_SIZE * shape[1])
        )
        self.clock = pygame.time.Clock()
        self.framerate = FRAMERATE
        pygame.time.set_timer(SCREEN_UPDATE, SPEED)
        self.background_color = (175, 215, 70)
        #

        self.board = np.zeros((shape[0], shape[1]))
        self.object: tuple = []
        self.create_object(SNAKE_HEAD)
        self.create_object(GREEN_APPLE)
        self.create_object(GREEN_APPLE)
        self.create_object(RED_APPLE)

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # TODO: AI input ?
                if event.type == SCREEN_UPDATE:
                    self.object[0].move(pygame.Vector2(1, 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.object[0].move(pygame.Vector2(0, -1))
                    if event.key == pygame.K_DOWN:
                        self.object[0].move(pygame.Vector2(0, 1))
                    if event.key == pygame.K_RIGHT:
                        self.object[0].move(pygame.Vector2(1, 0))
                    if event.key == pygame.K_LEFT:
                        self.object[0].move(pygame.Vector2(-1, 0))
            self.screen.fill(self.background_color)
            for obj in self.object:
                obj.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.framerate)

    def create_object(self, id: int = EMPTY_CASE) -> None:
        if id == SNAKE_HEAD:
            object = Snake(self.board)
            for x, y in object.body:
                self.board[int(x)][int(y)] = SNAKE_BODY
        if id == GREEN_APPLE:
            object = GreenApple(self.board)
        if id == RED_APPLE:
            object = RedApple(self.board)
        x, y = object.get_position()
        self.object.append(object)
        self.board[x][y] = id

    def reset(self):
        self.board = np.zeros_like(self.board)
        self.object: tuple = []
        self.create_object(SNAKE_HEAD)
        self.create_object(GREEN_APPLE)
        self.create_object(GREEN_APPLE)
        self.create_object(RED_APPLE)

    # TODO: Show via pygame ou en terminal ? Je crois que le sujet en parle
    def show(self):
        board = ""
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                board += f"[{self.board[row][col]}] "
            board += "\n"
        print(board)

    def is_finished(self):
        pass


if __name__ == "__main__":
    env = Board([50, 50])
    env.play()