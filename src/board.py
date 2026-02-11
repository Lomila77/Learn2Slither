import os
import pygame
import time
import sys
from tqdm import tqdm
from pygame.math import Vector2
import numpy as np
from src.brain import Brain
from src.utils import (
    _cfg,
    UP, DOWN, LEFT, RIGHT, SYMBOLS, DIRECTIONS_ICON,
    draw_step_graph, draw_object_graph,
    get_name, save_data, load_data, GREEN_APPLE, RED_APPLE, WALL
)
from src.object import GreenApple, RedApple
from src.snake import Snake


#TODO: can activate interface on training mode ?
class Board:
    def __init__(self) -> None:
        shape = _cfg["map_shape"]
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

        self.training_mode = _cfg["training_mode"]
        self.ai_player = _cfg["ai_mode"]
        self.load_checkpoint = _cfg["load_checkpoint"]
        self.trunc_vision = False
        self.trunc_limits = []
        if self.training_mode:
            if self.ai_player:
                raise ValueError(
                    "AI player not allowed during training."
                    + "Check json config file")
            if self.load_checkpoint:
                data = load_data()
                shape = data["shape"]
                self.previous_epochs = data["epochs"]
            self.total_epochs = _cfg["epochs"]
            self.epochs = _cfg["epochs"]
            print("MODE TRAINING")
            if not _cfg["terminal"]:
                print("Display disabled")
        elif self.ai_player:
            if not self.load_checkpoint:
                raise ValueError("Need checkpoint for ai player")
            print("MODE AI PLAYER")
            if _cfg["map_shape"] != data["shape"]:
                self.trunc_vision: bool = True
                self.trunc_limits: list[int] = data["shape"]
                print(
                    "Checkpoint loaded are not trained on map size."
                    + "Truncate vision on checkpoint.")
        else:
            print("MODE MANUAL")
        self.interface = _cfg["interface"]
        if self.interface:
            self.cell_size = _cfg["cell_size"]
            self.framerate = _cfg["framerate"]
            self.interface_speed = _cfg["interface_speed"]
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            self.screen = pygame.display.set_mode(
                Vector2(self.cell_size * shape[1], self.cell_size * shape[0]))
            self.clock = pygame.time.Clock()
            pygame.time.set_timer(pygame.USEREVENT, self.interface_speed)
            self.background_color = (175, 215, 70)
            self.game_font = pygame.font.Font(
                'font/PoetsenOne-Regular.ttf', 25)
        self.terminal = _cfg["terminal"]
        if self.terminal:
            self.terminal_speed = _cfg["terminal_speed"]
        else:
            self.progression = tqdm(
                total=self.total_epochs, desc="Steps", unit="step")
        self.step_by_step = _cfg["step_by_step"]

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
                if self.terminal:
                    self.display()
                if self.training_mode and not self.interface:
                    if self.is_finished():
                        self.game_over(losing_action=None)
                    self.check_collectible()
                    terminal, action = self.snake.call_brain(
                        self.training_mode,
                        self.trunc_vision,
                        self.trunc_limits
                    )
                    if terminal:
                        self.game_over(losing_action=action)
                        continue
                    self.snake.move(action)
                    self.movement_counter += 1
                    if self.step_by_step:
                        input()
                    elif self.terminal and self.terminal_speed != 0:
                        time.sleep(self.terminal_speed / 1000)
                elif self.interface:
                    for event in pygame.event.get():
                        if self.is_finished():
                            self.game_over()
                        #self.check_collectible()
                        if event.type == pygame.QUIT:
                            self.quit()
                        if (event.type == pygame.KEYDOWN) and (
                            event.key == pygame.K_ESCAPE
                        ):
                            self.game_over(finish=True)
                        if (event.type == pygame.KEYDOWN) and (
                            event.key == pygame.K_p
                        ):
                            self.step_by_step = (
                                True if self.step_by_step else False)
                        if not self.ai_player and not self.training_mode:
                            if event.type == pygame.USEREVENT:
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
                        elif self.training_mode:
                            terminal, action = self.snake.call_brain(
                                self.training_mode,
                                self.trunc_vision,
                                self.trunc_limits
                            )
                            if terminal:
                                self.game_over(losing_action=action)
                                continue
                            self.snake.move(action)
                            if self.step_by_step:
                                input()
                            elif self.terminal_speed != 0:
                                time.sleep(self.terminal_speed / 1000)
                        else:
                            _, action = self.snake.call_brain(
                                self.training_mode,
                                self.trunc_vision,
                                self.trunc_limits
                            )
                            self.snake.move(action)
                        self.movement_counter += 1
                    self.check_collectible()
                    self.screen.fill(self.background_color)
                    self.draw_grass()
                    self.draw_wall()
                    self.draw_object()
                    self.draw_score()
                    pygame.display.update()
                    # TODO: ???
                    if not self.training_mode:
                        self.clock.tick(self.framerate)
                    else:
                        self.clock.tick(self.terminal_speed)
        except KeyboardInterrupt:
            self.game_over(losing_action=None, finish=True)

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
                        col * self.cell_size, row * self.cell_size,
                        self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, grass_color, grass_rect)
                elif col % 2 != 0 and color is False:
                    grass_rect = pygame.Rect(
                        col * self.cell_size, row * self.cell_size,
                        self.cell_size, self.cell_size)
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
                        image, (self.cell_size, self.cell_size))
            wall_rect = pygame.Rect(
                wall.x * self.cell_size,
                wall.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            self.screen.blit(image, wall_rect)

    def draw_score(self):
        score_text = f"{len(self.snake.body) - 3}"
        score_surface = self.game_font.render(
            score_text, True, (56, 74, 12))
        score_x = int(self.cell_size * self.board.shape[1] - 60)
        score_y = int(self.cell_size * self.board.shape[0] - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        self.screen.blit(score_surface, score_rect)

    def create_wall(self):
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
        return apples

    def create_red_apple(self, nb: int = 1):
        apples: list = []
        for _ in range(nb):
            apple = RedApple(self.board, self.interface)
            self.board[int(apple.pos.y)][int(apple.pos.x)] = RED_APPLE
            apples.append(apple)
        return apples

    def create_snake(self, brain: Brain = None, load_checkpoint: bool = False):
        return Snake(self.board, brain, self.interface, load_checkpoint)

    def reset(self):
        width_board = len(self.board[0])
        self.reset_training_counter()
        self.board = np.zeros_like(self.board)
        self.walls = self.create_wall()
        brain = self.snake.brain
        self.snake = self.create_snake(brain=brain)
        self.green_apple = self.create_green_apple()
        self.red_apple = self.create_red_apple()
        self.snake.brain.reset()
        if self.terminal:
            underline = "=" * width_board * 2
            print(underline + "=" * 9 + underline)
            print(underline + "=" * 9 + underline)
            print("Game reseting...")
            print("NEW GAME".center(
                width_board * 2 * 2 + 9))

    def reset_training_counter(self):
        self.max_lengths.append(self.snake.max_length)
        self.green_apples_ate.append(self.green_apple_counter)
        self.red_apples_ate.append(self.red_apple_counter)
        self.movements.append(self.movement_counter)
        self.green_apple_counter = 0
        self.red_apple_counter = 0
        self.movement_counter = 0

    def display(self):
        if not self.terminal:
            return
        os.system('clear')
        separator = '    |    '
        symbols_len = 2
        width_board = len(self.board[0])
        snake_vision = self.snake.vision()
        underline = "=" * width_board * symbols_len
        if self.training_mode:
            print(underline + "=" * len(separator) + underline)
            print(f"REMAINING EPOCHS: {self.epochs}".center(
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
            if self.load_checkpoint:
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
            reward = self.snake.brain.prev_reward
            prev_action = DIRECTIONS_ICON[self.snake.brain.prev_action]
            if reward == 0:
                prev_action = '   '
            print(f"Action: {prev_action}".center(
                width_board * symbols_len + 1) + separator
                + f"Length: {self.snake.brain.get_length_q_table()}".center(
                    width_board * symbols_len
                )
            )
            print(f"Reward: {self.snake.brain.prev_reward}".center(
                width_board * symbols_len) + separator)
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

    def is_eating_body(self) -> bool:
        if self.snake.get_head_position() in self.snake.get_body_position():
            self.snake.body.pop(0)
            self.ate_himself_counter += 1
            if self.terminal:
                print("Snake ate himself !!! Feed your snake !")
            return True
        return False

    def is_snake_too_short(self) -> bool:
        if self.snake.get_length() < 2:
            if self.terminal:
                print("Snake too short...")
            return True
        return False

    def is_hitting_wall(self) -> bool:
        head = self.snake.get_head_position()
        for wall in self.walls:
            if head.x == wall.x and head.y == wall.y:
                if self.terminal:
                    print("Snake is gone, good bye snaky snakie")
                self.hit_wall_counter += 1
                return True
        return False

    def is_finished(self):
        if self.is_snake_too_short() or self.is_eating_body(
        ) or self.is_hitting_wall():
            return True
        return False

    def last_action(self, losing_action: Vector2):
        self.snake.call_brain(
            self.training_mode,
            self.trunc_vision,
            self.trunc_limits
        )
        self.snake.move(losing_action)
        self.is_eating_body()
        self.is_hitting_wall()
        self.is_snake_too_short()
        self.display()

    def quit(self):
        pygame.quit()
        sys.exit()

    def game_over(self, losing_action: Vector2, finish: bool = False):
        if self.interface and not self.training_mode:
            print("\n=== GAME OVER ===")
            print(f"Length: {self.snake.get_length()}")
            self.quit()
        elif self.training_mode:
            if losing_action:
                self.last_action(losing_action)
            self.epochs -= 1
            if not self.terminal and self.progression is not None:
                self.progression.update(1)
            if self.epochs > 0 and not finish:
                self.reset()
            else:
                self.reset_training_counter()
                epochs = self.total_epochs - self.epochs
                if self.load_checkpoint:
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
                if self.terminal:
                    print("\n=== GAME OVER ===")
                    print(f"Length: {self.snake.get_length()}")
                if self.interface:
                    pygame.quit()
                sys.exit()

    def check_collectible(self):
        for apple in self.green_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                self.green_apple_counter += 1
                if self.terminal:
                    print("Snake ate yummy green apple ! Happy snake !")
        for apple in self.red_apple:
            if apple.get_position() == self.snake.get_head_position():
                self.snake.eat(apple.nourrish(self.board))
                self.red_apple_counter += 1
                if self.terminal:
                    print("Snake ate an horrible red apple... Poor snake...")


if __name__ == "__main__":
    #TODO: Take arguments form input or from json
    env = Board()
    env.play()
