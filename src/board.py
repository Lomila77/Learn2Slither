import os
import pygame
import time
import sys
from pygame.math import Vector2
import numpy as np
from src.brain import Brain
from src.config import (
    CELL_SIZE,
    FRAMERATE,
    SCREEN_UPDATE,
    SPEED,
    EPOCHS,
    TRAINING_MODE,
    AI_MODE,
    LOAD_CHECKPOINT,
    MAP_SHAPE
)
from src.utils import (
    UP, DOWN, LEFT, RIGHT, SYMBOLS, DIRECTIONS_ICON,
    draw_step_graph, draw_object_graph,
    get_name, save_data, load_data
)
from src.object import GreenApple, RedApple
from src.snake import Snake


class Board:
    def __init__(self) -> None:
        shape = MAP_SHAPE
        if TRAINING_MODE:
            self.interface = False
            self.training_mode = True
            self.ai_player = True
            if LOAD_CHECKPOINT:
                data = load_data()
                shape = data["shape"]
                self.previous_epochs = data["epochs"]
            self.total_epochs = EPOCHS
            self.epochs = EPOCHS
        elif AI_MODE:
            self.interface = True
            self.training_mode = False
            self.ai_player = True
        else:
            self.interface = True
            self.training_mode = False
            self.ai_player = False

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

        if self.interface:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            # Screen size: width = nb_cols, height = nb_rows
            self.screen = pygame.display.set_mode(
                Vector2(CELL_SIZE * shape[1], CELL_SIZE * shape[0]))
            self.clock = pygame.time.Clock()
            self.framerate = FRAMERATE
            pygame.time.set_timer(SCREEN_UPDATE, SPEED)
            self.background_color = (175, 215, 70)
            self.game_font = pygame.font.Font(
                'font/PoetsenOne-Regular.ttf', 25)
        self.max_lengths: list[int] = []
        self.movements: list[int] = []
        self.green_apples_ate: list[int] = []
        self.red_apples_ate: list[int] = []
        # board[row][col] = board[y][x]
        self.board = np.zeros((shape[0], shape[1]))
        self.walls: list = self.create_wall()
        self.snake: Snake = self.create_snake(load_checkpoint=LOAD_CHECKPOINT)
        self.green_apple: list = self.create_green_apple()
        self.red_apple: list = self.create_red_apple()
        self.green_apple_counter: int = 0
        self.red_apple_counter: int = 0
        self.movement_counter: int = 0
        print("Starting the game")

    def play(self):
        try:
            while True:
                self.display()
                if self.is_finished():
                    self.game_over()
                self.check_collectible()
                if self.training_mode:
                    action = self.snake.call_brain()
                    self.snake.move(action)
                    time.sleep(SPEED / 1000)
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
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
                    self.clock.tick(self.framerate)
                self.movement_counter += 1
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
        # height = nb_rows, width = nb_cols
        height = self.board.shape[0] - 1
        width = self.board.shape[1] - 1
        for wall in self.walls:
            path = ''
            if wall.y == 0 and wall.x == 0:
                path = 'graphics/coin_haut_gauche.png'
            elif wall.y == 0 and wall.x == width:
                path = 'graphics/coin_haut_droit.png'
            elif wall.y == height and wall.x == 0:
                path = 'graphics/coin_bas_gauche.png'
            elif wall.y == height and wall.x == width:
                path = 'graphics/coin_bas_droit.png'
            elif wall.x == 0:
                path = 'graphics/bai_gauche.png'
            elif wall.x == width:
                path = 'graphics/bai_droit.png'
            elif wall.y == 0:
                path = 'graphics/bai_haut.png'
            elif wall.y == height:
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
        # width = nb_cols, height = nb_rows
        score_x = int(CELL_SIZE * self.board.shape[1] - 60)
        score_y = int(CELL_SIZE * self.board.shape[0] - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        self.screen.blit(score_surface, score_rect)

    def create_wall(self):
        print("Build walls (water)")
        walls: list[Vector2] = []
        for row_idx, row in enumerate(self.board):
            for col_idx, _ in enumerate(row):
                # Borders: board[row][col] = board[y][x]
                if col_idx == 0 or col_idx == len(row) - 1:
                    self.board[row_idx][col_idx] = 5
                    walls.append(Vector2(col_idx, row_idx))
                if row_idx == 0 or row_idx == len(self.board) - 1:
                    self.board[row_idx][col_idx] = 5
                    walls.append(Vector2(col_idx, row_idx))
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

    def create_snake(self, brain: Brain = None, load_checkpoint: bool = False):
        print("Create lovely snake")
        return Snake(self.board, brain, self.interface, load_checkpoint)

    def reset(self):
        self.board = np.zeros_like(self.board)
        print("Game reset")
        self.walls = self.create_wall()
        brain = self.snake.brain
        self.snake = self.create_snake(brain=brain)
        self.green_apple = self.create_green_apple()
        self.red_apple = self.create_red_apple()
        self.snake.brain.reset()

    def display(self):
        os.system('clear')
        separator = '    |    '
        symbols_len = 2
        width_board = len(self.board[0])
        snake_vision = self.snake.vision()
        underline = "=" * width_board * symbols_len
        print(underline + "=" * len(separator) + underline)
        print(underline + "=" * len(separator) + underline)
        print("BOARD".center(
            width_board * symbols_len) + separator + "SNAKE VISION".center(
                width_board * symbols_len))
        print(underline + separator + underline)
        board_transposed = self.board
        vision_transposed = snake_vision
        for i in range(len(board_transposed)):
            line1 = ''.join(
                SYMBOLS.get(cell, '?') for cell in board_transposed[i])
            line2 = ''.join(
                SYMBOLS.get(cell, '?') for cell in vision_transposed[i])
            print(line1 + separator + line2)
        print(underline + "=" * len(separator) + underline)
        if self.training_mode:
            prev_action = DIRECTIONS_ICON[self.snake.brain.prev_action]
            print(f"EPOCHS: {self.epochs}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(f"SNAKE POS: {self.snake.get_head_position()}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(f"SNAKE LENGHT: {self.snake.get_length()}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(underline + "=" * len(separator) + underline)
            print("BRAIN".center(
                width_board * symbols_len) + separator + "Q_TABLE".center(
                    width_board * symbols_len))
            print(underline + separator + underline)
            print(f"Action: {prev_action}".center(
                width_board * symbols_len + 1
            ) + separator + f"Length: {self.snake.brain.get_length_q_table()}".center(
                    width_board * symbols_len))
            print(f"Reward: {self.snake.brain.prev_reward}".center(
                width_board * symbols_len) + separator)

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
        # Out of bounds with board[row][col] = board[y][x]
        if not (
            0 < pos.x < self.board.shape[1]) or not (
            0 < pos.y < self.board.shape[0]
        ):
            return True
        return False

    def game_over(self):
        print("\n=== GAME OVER ===")
        print(f"Snake Length: {self.snake.get_length()}")
        if self.interface:
            pygame.quit()
            sys.exit()
        elif self.training_mode:
            self.epochs -= 1
            self.max_lengths.append(self.snake.max_length)
            self.green_apples_ate.append(self.green_apple_counter)
            self.red_apples_ate.append(self.red_apple_counter)
            self.movements.append(self.movement_counter)
            self.green_apple_counter = 0
            self.red_apple_counter = 0
            self.movement_counter = 0
            if self.epochs > 0:
                self.reset()
            else:
                epochs = self.total_epochs if self.epochs == 0 else self.epochs
                if LOAD_CHECKPOINT:
                    epochs += self.previous_epochs
                print(f"TOTAL EPOCH: {epochs}")
                print(f"MOVEMENTS: {self.movements}")
                save_data(epochs, self.snake.brain.q_table)
                draw_step_graph(
                    epochs=self.total_epochs,
                    nb_steps=self.movements,
                    name=get_name("step_graph")
                )
                draw_object_graph(
                    epochs=self.total_epochs,
                    nb_green_apples_ate=self.green_apples_ate,
                    nb_red_apples_ate=self.red_apples_ate,
                    snake_sizes=self.max_lengths,
                    name=get_name("object_graph")
                )
                sys.exit()

    def check_collectible(self):
        for apple in self.green_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                self.green_apple_counter += 1
                print("Snake ate yummy green apple ! Happy snake !")
        for apple in self.red_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                self.red_apple_counter += 1
                print("Snake ate an horrible red apple... Poor snake...")


if __name__ == "__main__":
    env = Board()
    env.play()
