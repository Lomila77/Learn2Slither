
import pygame
from pygame.math import Vector2
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

# TODO: parfois quand le jeu commence le snake est mal positionner et se marche dessus directe
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
        self.shape = Vector2(shape[0], shape[1])
        self.screen = pygame.display.set_mode(
            Vector2(CELL_SIZE * shape[0], CELL_SIZE * shape[1]))
        self.clock = pygame.time.Clock()
        self.framerate = FRAMERATE
        pygame.time.set_timer(SCREEN_UPDATE, SPEED)
        self.background_color = (175, 215, 70)
        #

        self.board = np.zeros((shape[0], shape[1]))
        self.green_apple: list = self.create_green_apple()
        self.red_apple: list = self.create_red_apple()
        self.snake: Snake = self.create_snake()
        print("Starting the game")

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.is_finished():
                    self.game_over()
                # TODO: AI input ?
                if event.type == SCREEN_UPDATE:
                    self.snake.move(self.snake.direction)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_over()
                    if event.key == pygame.K_UP:
                        self.snake.move(pygame.Vector2(0, -1))
                    if event.key == pygame.K_DOWN:
                        self.snake.move(pygame.Vector2(0, 1))
                    if event.key == pygame.K_RIGHT:
                        self.snake.move(pygame.Vector2(1, 0))
                    if event.key == pygame.K_LEFT:
                        self.snake.move(pygame.Vector2(-1, 0))
            self.check_collision()
            self.screen.fill(self.background_color)
            for apple in self.green_apple:
                apple.draw(self.screen)
            for apple in self.red_apple:
                apple.draw(self.screen)
            self.snake.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.framerate)
    
    def create_green_apple(self, nb: int = 2):
        apples: list = []
        for _ in range(nb):
            apples.append(GreenApple(self.board))
        print("Create green apple")
        return apples

    def create_red_apple(self, nb: int = 1):
        apples: list = []
        for _ in range(nb):
            apples.append(RedApple(self.board))
        print("Create green apple")
        return apples

    def create_snake(self):
        print("Create lovely snake")
        return Snake(self.board)

    def reset(self):
        self.board = np.zeros_like(self.board)
        print("Game reset")
        self.green_apple = self.create_green_apple()
        self.red_apple = self.create_red_apple()
        self.snake = self.create_snake()

    # TODO: Show via pygame ou en terminal ? Je crois que le sujet en parle
    def show(self):
        board = ""
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                board += f"[{self.board[row][col]}] "
            board += "\n"
        print(board)

    def is_finished(self):
        if self.snake.get_length() < 3:
            print("Snake too short...")
            return True
        if not 0 <= self.snake.get_head_position().x <  self.shape.x:
            print("Snake is gone, good bye snaky snakie")
            return True
        if not 0 <= self.snake.get_head_position().y <  self.shape.y:
            print("Snake is gone, good bye snaky snakie")
            return True
        if self.snake.get_head_position() in self.snake.get_body_position():
            print("Snake ate himself !!! Feed your snake !")
            return True
        return False
    
    def game_over(self):
        print("\n=== GAME OVER ===")
        print(f"Snake Length: {self.snake.get_length()}")
        pygame.quit()
        sys.exit()


    def check_collision(self):
        for apple in self.green_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                print("Snake ate yummy green apple ! Happy snake !")
        for apple in self.red_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                print("Snake ate an horrible red apple... Poor snake...")


if __name__ == "__main__":
    env = Board([50, 50])
    env.play()