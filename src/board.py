import pygame, time, sys
from pygame.math import Vector2
import numpy as np
from src.config import (
    CELL_SIZE,
    FRAMERATE,
    SCREEN_UPDATE,
    SPEED
)
from src.utils import UP, DOWN, LEFT, RIGHT, SYMBOLS
from src.object import GreenApple, RedApple
from src.snake import Snake


class Board:
    def __init__(self, shape: list[int], training_mode=False, ai_mode=False) -> None:
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
        if training_mode:
            self.interface = False
            self.training_mode = True
            self.ai_player = True
            print("Enter epochs: ")
            self.epochs = int(input())
            
        elif ai_mode:
            self.interface = True
            self.training_mode = False
            self.ai_player = True
        else:
            self.interface = True
            self.training_mode = False
            self.ai_player = False

        if self.interface:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            self.screen = pygame.display.set_mode(
                Vector2(CELL_SIZE * shape[0], CELL_SIZE * shape[1]))
            self.clock = pygame.time.Clock()
            self.framerate = FRAMERATE
            pygame.time.set_timer(SCREEN_UPDATE, SPEED)
            self.background_color = (175, 215, 70)
            self.game_font = pygame.font.Font('font/PoetsenOne-Regular.ttf', 25)

        self.board = np.zeros((shape[0], shape[1]))
        self.green_apple: list = self.create_green_apple()
        self.red_apple: list = self.create_red_apple()
        self.snake: Snake = self.create_snake()
        self.walls: list = self.create_wall()
        print("Starting the game")

    def play(self):
        try:
            self.display()
            while True:
                if self.training_mode:
                    action = self.snake.call_brain()
                    self.snake.move(action)
                    self.display()
                    if self.is_finished():
                        self.game_over()
                    time.sleep(SPEED / 1000)
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or self.is_finished():
                            self.game_over()
                        if event.type == SCREEN_UPDATE:
                            self.snake.move(self.snake.direction)
                        if event.type == pygame.KEYDOWN and not self.ai_player:
                            if event.key == pygame.K_ESCAPE:
                                self.game_over()
                            if event.key == pygame.K_UP:
                                if self.snake.direction.y != 1:
                                    self.snake.move(UP)
                            if event.key == pygame.K_DOWN:
                                if self.snake.direction.y != -1:
                                    self.snake.move(DOWN)
                            if event.key == pygame.K_RIGHT:
                                if self.snake.direction.x != -1:
                                    self.snake.move(RIGHT)
                            if event.key == pygame.K_LEFT:
                                if self.snake.direction.x != 1:
                                    self.snake.move(LEFT)
                        elif self.ai_player:
                            action = self.snake.call_brain()
                            self.snake.move(action)

                    self.screen.fill(self.background_color)
                    self.draw_grass()
                    self.draw_wall()
                    self.draw_object()
                    self.draw_score()
                    pygame.display.update()
                    self.display()
                    self.clock.tick(self.framerate)
                self.check_collectible()
        except KeyboardInterrupt:
            self.game_over()

    def draw_object(self):
        for apple in self.green_apple:
            apple.draw(self.screen)
        for apple in self.red_apple:
            apple.draw(self.screen)
        self.snake.draw(self.screen)

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(int(self.board.shape[0])):
            color = False
            if row % 2 == 0: 
                color = True
            for col in range(int(self.board.shape[1])):
                if col % 2 == 0 and color is True:
                    grass_rect = pygame.Rect(
                        col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, grass_color, grass_rect)
                elif col % 2 != 0 and color is False:
                    grass_rect = pygame.Rect(
                        col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, grass_color, grass_rect)

    def draw_wall(self):
        len_board = len(self.board) - 1
        len_row = len(self.board[0]) - 1
        for wall in self.walls:
            path = ''
            if wall.y == 0 and wall.x == 0:
                path = 'graphics/coin_haut_gauche.png'
            elif wall.y == 0 and wall.x == len_board:
                path = 'graphics/coin_haut_droit.png'
            elif wall.y == len_row and wall.x == 0:
                path = 'graphics/coin_bas_gauche.png'
            elif wall.y == len_row and wall.x == len_board:
                path = 'graphics/coin_bas_droit.png'
            elif wall.x == 0:
                path = 'graphics/bai_gauche.png'
            elif wall.x == len_board:
                path = 'graphics/bai_droit.png'
            elif wall.y == 0:
                path = 'graphics/bai_haut.png'
            elif wall.y == len_row:
                path = 'graphics/bai_bas.png'
            else:
                continue
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(
                        image, (CELL_SIZE, CELL_SIZE))
            wall_rect = pygame.Rect(
                wall.x * CELL_SIZE,
                wall.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            self.screen.blit(image, wall_rect)

    def draw_score(self):
        score_text = f"{len(self.snake.body) - 3}"
        score_surface = self.game_font.render(
            score_text, True, (56, 74, 12))
        score_x = int(CELL_SIZE * self.board.shape[0] - 60)
        score_y = int(CELL_SIZE * self.board.shape[1] - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        self.screen.blit(score_surface, score_rect)

    def create_wall(self):
        print("Build walls (water)")
        # self.board[0] = 5
        # self.board[-1] = 5
        # self.board[1:-1][0] = 5
        # self.board[1:-1][-1] = 5
        walls: list[Vector2] = []
        for i, row in enumerate(self.board):
            for j, _ in enumerate(self.board):
                if j == 0 or j == len(row) - 1:
                    self.board[i][j] = 5
                    walls.append(Vector2(i, j))
                if i == 0 or i == len(self.board) - 1:
                    self.board[i][j] = 5
                    walls.append(Vector2(i, j))
        return walls

    def create_green_apple(self, nb: int = 2):
        apples: list = []
        for _ in range(nb):
            apples.append(GreenApple(self.board, self.interface))
        print("Create green apple")
        return apples

    def create_red_apple(self, nb: int = 1):
        apples: list = []
        for _ in range(nb):
            apples.append(RedApple(self.board, self.interface))
        print("Create green apple")
        return apples

    def create_snake(self):
        print("Create lovely snake")
        return Snake(self.board, self.interface)

    def reset(self):
        self.board = np.zeros_like(self.board)
        print("Game reset")
        self.walls = self.create_wall()
        self.green_apple = self.create_green_apple()
        self.red_apple = self.create_red_apple()
        self.snake = self.create_snake()

    def display(self):
        #os.system('clear')
        separator = '    |    '
        symbols_len = len(SYMBOLS[0])
        width_board = len(self.board[0])
        snake_vision = self.snake.vision()
        print("BOARD".center(
            width_board * symbols_len) + separator + "SNAKE VISION".center(
                width_board * symbols_len))
        underline = "=" * width_board * symbols_len
        print(underline + separator + underline)

        board_transposed = self.board.T
        vision_transposed = snake_vision.T
        for i in range(len(board_transposed)):
            line1 = ''.join(
                SYMBOLS.get(cell, '?') for cell in board_transposed[i])
            line2 = ''.join(
                SYMBOLS.get(cell, '?') for cell in vision_transposed[i])
            print(line1 + separator + line2)
        if self.training_mode:
            snake_area = self.snake.brain.get_area(self.snake.get_head_position())
            print(f"⬆️ {[f"{val:.2f} " for val in snake_area[0]]}".center(
                width_board * symbols_len))
            print(f"⬇️ {[f"{val:.2f} " for val in snake_area[1]]}".center(
                width_board * symbols_len))
            print(f"⬅️ {[f"{val:.2f} " for val in snake_area[2]]}".center(
                    width_board * symbols_len))
            print(f"➡️ {[f"{val:.2f} " for val in snake_area[3]]}".center(
                    width_board * symbols_len))

    def is_finished(self):
        if self.snake.get_length() < 3:
            print("Snake too short...")
            return True
        if self.snake.get_head_position() in self.snake.get_body_position():
            self.snake.body.pop(0)
            print("Snake ate himself !!! Feed your snake !")
            return True
        pos = self.snake.get_head_position()
        for wall in self.walls:
            if pos.x == wall.x and pos.y == wall.y:
                print("Snake is gone, good bye snaky snakie")
                return True
        return False
    
    def game_over(self):
        print("\n=== GAME OVER ===")
        print(f"Snake Length: {self.snake.get_length()}")
        if self.interface:
            pygame.quit()
            sys.exit()
        elif self.training_mode:
            self.reset()
            self.


    def check_collectible(self):
        for apple in self.green_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                print("Snake ate yummy green apple ! Happy snake !")
        for apple in self.red_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                print("Snake ate an horrible red apple... Poor snake...")


if __name__ == "__main__":
    env = Board([30, 30], training_mode=True)
    env.play()
