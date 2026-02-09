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
    TRAINING_SPEED,
    EPOCHS,
    TRAINING_MODE,
    AI_MODE,
    LOAD_CHECKPOINT,
    MAP_SHAPE
)
from src.utils import (
    UP, DOWN, LEFT, RIGHT, SYMBOLS, DIRECTIONS_ICON,
    draw_step_graph, draw_object_graph,
    get_name, save_data, load_data, GREEN_APPLE, RED_APPLE, WALL
)
from src.object import GreenApple, RedApple
from src.snake import Snake


class Board:
    def __init__(self) -> None:
        shape = MAP_SHAPE
        self.interface = True
        self.training_mode = False
        self.load_checkpoint = False
        self.ai_player = False
        if TRAINING_MODE:
            self.interface = False
            self.training_mode = True
            if LOAD_CHECKPOINT:
                data = load_data()
                self.previous_epochs = data["epochs"]
                self.load_checkpoint = True
            self.total_epochs = EPOCHS
            self.epochs = EPOCHS
        elif AI_MODE:
            self.ai_player = True
            self.load_checkpoint = True

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
        self.board = np.zeros((shape[0], shape[1]))
        self.walls: list = self.create_wall()
        self.snake: Snake = self.create_snake(
            load_checkpoint=self.load_checkpoint)
        self.green_apple: list = self.create_green_apple()
        self.red_apple: list = self.create_red_apple()
        self.green_apple_counter: int = 0
        self.red_apple_counter: int = 0
        self.hit_wall_counter: int = 0
        self.ate_himself_counter: int = 0
        self.movement_counter: int = 0

    def play(self):
        try:
            while True:
                self.display()
                if self.training_mode:
                    self.display()
                    if self.is_finished():
                        self.game_over()
                    self.check_collectible()
                    terminal, action = self.snake.call_brain()
                    if terminal:
                        self.game_over()
                        continue
                    self.snake.move(action)
                    self.movement_counter += 1
                    if TRAINING_SPEED != 0:
                        time.sleep(TRAINING_SPEED / 1000)
                else:
                    for event in pygame.event.get():
                        self.display()
                        if self.is_finished():
                            self.game_over()
                        self.check_collectible()
                        if event.type == pygame.QUIT:
                            self.quit()
                        if (event.type == pygame.KEYDOWN) and (
                            event.key == pygame.K_ESCAPE
                        ):
                            self.game_over()
                        if not self.ai_player:
                            if event.type == SCREEN_UPDATE:
                                self.snake.move(self.snake.direction)
                            if event.type == pygame.KEYDOWN:
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
                        else:
                            _, action = self.snake.call_brain()
                            self.snake.move(action)
                        self.movement_counter += 1
                    self.screen.fill(self.background_color)
                    self.draw_grass()
                    self.draw_wall()
                    self.draw_object()
                    self.draw_score()
                    pygame.display.update()
                    self.clock.tick(self.framerate)
        except KeyboardInterrupt:
            self.game_over(True)

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
        score_x = int(CELL_SIZE * self.board.shape[1] - 60)
        score_y = int(CELL_SIZE * self.board.shape[0] - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        self.screen.blit(score_surface, score_rect)

    def create_wall(self):
        print("Build walls (water)")
        walls: list[Vector2] = []
        for row_idx, row in enumerate(self.board):
            for col_idx, _ in enumerate(row):
                if (
                    col_idx == 0 or col_idx == len(row) - 1) or (
                    row_idx == 0 or row_idx == len(self.board) - 1
                ):
                    self.board[row_idx][col_idx] = WALL
                    walls.append(Vector2(col_idx, row_idx))
        return walls

    def create_green_apple(self, nb: int = 2):
        apples: list = []
        for _ in range(nb):
            apple = GreenApple(self.board, self.interface)
            self.board[int(apple.pos.y)][int(apple.pos.x)] = GREEN_APPLE
            apples.append(apple)
        print("Create green apple")
        return apples

    def create_red_apple(self, nb: int = 1):
        apples: list = []
        for _ in range(nb):
            apple = RedApple(self.board, self.interface)
            self.board[int(apple.pos.y)][int(apple.pos.x)] = RED_APPLE
            apples.append(apple)
        print("Create green apple")
        return apples

    def create_snake(self, brain: Brain = None, load_checkpoint: bool = False):
        print("Create lovely snake")
        return Snake(self.board, brain, self.interface, load_checkpoint)

    def reset(self):
        self.reset_training_counter()
        self.board = np.zeros_like(self.board)
        print("Game reset")
        self.walls = self.create_wall()
        brain = self.snake.brain
        self.snake = self.create_snake(brain=brain)
        self.green_apple = self.create_green_apple()
        self.red_apple = self.create_red_apple()
        self.snake.brain.reset()

    def reset_training_counter(self):
        self.max_lengths.append(self.snake.max_length)
        self.green_apples_ate.append(self.green_apple_counter)
        self.red_apples_ate.append(self.red_apple_counter)
        self.movements.append(self.movement_counter)
        self.green_apple_counter = 0
        self.red_apple_counter = 0
        self.movement_counter = 0

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
        for i in range(len(self.board)):
            line1 = ''.join(
                SYMBOLS.get(cell, '?') for cell in self.board[i])
            line2 = ''.join(
                SYMBOLS.get(cell, '?') for cell in snake_vision[i])
            print(line1 + separator + line2)
        if self.training_mode:
            print(underline + "=" * len(separator) + underline)
            prev_action = DIRECTIONS_ICON[self.snake.brain.prev_action]
            print(f"EPOCHS: {self.epochs}".center(
                width_board * symbols_len * 2 + len(separator)))
            if len(self.max_lengths) != 0:
                print(f"MAX LENGTH REACH: {max(self.max_lengths)}".center(
                    width_board * symbols_len * 2 + len(separator)))
            print(f"GREEN APPLE ATE: {sum(self.green_apples_ate)}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(f"RED APPLE ATE: {sum(self.red_apples_ate)}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(f"WALL HITTED: {self.hit_wall_counter}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(f"ATE HIMSELF: {self.ate_himself_counter}".center(
                width_board * symbols_len * 2 + len(separator)))
            if LOAD_CHECKPOINT:
                epochs = self.total_epochs + self.previous_epochs
            else:
                epochs = self.total_epochs
            print(f"TOTAL EPOCHS: {epochs}".center(
                width_board * symbols_len * 2 + len(separator)))
            print(underline + "=" * len(separator) + underline)
            print("BRAIN".center(
                width_board * symbols_len) + separator + "Q_TABLE".center(
                    width_board * symbols_len))
            print(underline + separator + underline)
            print(f"Action: {prev_action}".center(
                width_board * symbols_len + 1) + separator
                + f"Length: {self.snake.brain.get_length_q_table()}".center(
                    width_board * symbols_len
                )
            )
            print(f"Reward: {self.snake.brain.prev_reward}".center(
                width_board * symbols_len) + separator)

    def is_eating_body(self, pos: Vector2) -> bool:
        if pos in self.snake.get_body_position():
            self.snake.body.pop(0)
            self.ate_himself_counter += 1
            print("Snake ate himself !!! Feed your snake !")
            return True
        return False

    def is_snake_too_short(self) -> bool:
        if self.snake.get_length() < 3:
            print("Snake too short...")
            return True
        return False

    def is_hitting_wall(self, pos: Vector2) -> bool:
        for wall in self.walls:
            if pos.x == wall.x and pos.y == wall.y:
                print("Snake is gone, good bye snaky snakie")
                self.hit_wall_counter += 1
                return True
        return False

    def is_finished(self, pos: Vector2 = None):
        if pos is None:
            pos = self.snake.get_head_position()
        if self.is_snake_too_short() or self.is_eating_body(
                pos=pos) or self.is_hitting_wall(pos=pos):
            return True
        return False

    def last_action(self):
        _, action = self.snake.call_brain()
        losing_pos = self.snake.get_head_position() + action
        self.is_eating_body(pos=losing_pos)
        self.is_hitting_wall(pos=losing_pos)

    def quit(self):
        pygame.quit()
        sys.exit()

    def game_over(self, finish: bool = False):
        print("\n=== GAME OVER ===")
        print(f"Length: {self.snake.get_length()}")
        if self.interface:
            self.quit()
        elif self.training_mode:
            self.last_action()
            self.epochs -= 1
            if self.epochs > 0 and not finish:
                self.reset()
            else:
                self.reset_training_counter()
                epochs = self.total_epochs if self.epochs == 0 else self.epochs
                if LOAD_CHECKPOINT:
                    epochs += self.previous_epochs
                save_data(epochs, self.snake.brain.q_table)
                draw_step_graph(
                    epochs=self.total_epochs,
                    nb_steps=self.movements,
                    name=get_name(epochs, "step_graph")
                )
                draw_object_graph(
                    epochs=self.total_epochs,
                    nb_green_apples_ate=self.green_apples_ate,
                    nb_red_apples_ate=self.red_apples_ate,
                    snake_sizes=self.max_lengths,
                    name=get_name(epochs, "object_graph")
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
