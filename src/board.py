import os
from tabnanny import check
import tkinter as tk
from typing import Any
import pygame
import pygame_menu
import time
import sys
from tkinter import filedialog
from pygame_menu.widgets.core.widget import Widget
from tqdm import tqdm
from pygame.math import Vector2
import numpy as np
from src.brain import Brain
from src.utils import (
    UP, DOWN, LEFT, RIGHT, SYMBOLS, DIRECTIONS_ICON,
    draw_step_graph, draw_object_graph,
    get_name, save_data, load_data, GREEN_APPLE, RED_APPLE, WALL
)
from src.object import GreenApple, RedApple
from src.snake import Snake


#TODO: can activate interface on training mode ?
class Board:
    training_mode: bool = False
    save: bool = False
    ai_player: bool = False
    load_checkpoint: bool = False
    force_exploration: bool = False
    interface: bool = False
    terminal: bool = False
    step_by_step: bool = False

    save_as: str = "experiments_00"
    save_in: str = "./weights/casual/"
    load_data_from: str = ""
    load_weights_from: str = ""

    epochs: int = 1000
    total_epochs: int = 0
    previous_epoch: int = 0
    learning_rate: float = 0.9
    epsilon_greedy: float = 0.1

    map_shape: list[int] = [10, 10]
    cell_size: int = 40
    framerate: int = 60
    interface_speed: int = 200
    terminal_speed: int = 75

    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen_menu = pygame.display.set_mode(
            Vector2(800, 800))
        self.create_menu()
        self.menu.mainloop(self.screen_menu)

    def __setattr(self, name: str, caster: type) -> None:
        def setter(val: str) -> None:
            if val == "":
                return
            setattr(self, name, caster(val))
        return setter

    def create_menu(self):
        def select_load_data_file() -> None:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select data file",
                filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                self.load_data_from = file_path
                load_data_from.set_value(file_path)

        def select_load_weights_file() -> None:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select weights file",
                filetypes=[("Pickle files", "*.pck")]
            )
            if file_path:
                self.load_weights_from = file_path
                load_weights_from.set_value(file_path)

        def toggle_widgets(show: bool, widgets: list[Widget]):
            if show:
                for w in widgets:
                    w.show()
            else:
                for w in widgets:
                    w.hide()

        def set_height(val: str):
            if val == "" or not val.isdigit():
                return
            nb = int(val)
            if nb < 10 or nb > 30:
                # TODO: print message
                return
            self.map_shape[0] = int(val)

        def set_width(val: str):
            if val == "" or not val.isdigit():
                return
            nb = int(val)
            if nb < 10 or nb > 30:
                # TODO: print message
                return
            self.map_shape[1] = int(val)

        def set_training_mode(_, val: bool):
            self.training_mode = val
            training.set_value(val)
            if self.training_mode:
                set_ai_mode('No', 0)
                set_interface('No', 0)
            else:
                set_save_training('No', 0)
            toggle_widgets(self.training_mode, training_widgets)

        def set_save_training(_, val: bool):
            self.save = val
            save.set_value(val)
            toggle_widgets(self.save, save_widgets)

        def set_ai_mode(_, val: bool):
            self.ai_player = val
            print(f"val: {val}\n\n")
            ai_mode.set_value(val)
            if self.ai_player:
                set_training_mode('No', 0)
                set_interface('Yes', 1)
                interface.is_selectable = False
                checkpoint.is_selectable = False
                set_load_checkpoint('Yes', 1)
                checkpoint.show()
            else:
                checkpoint.hide()
                checkpoint.is_selectable = True
                set_load_checkpoint('No', 0)
                interface.is_selectable = True

        def set_load_checkpoint(_, val: bool):
            self.load_checkpoint = val
            checkpoint.set_value(val)
            toggle_widgets(
                self.load_checkpoint, checkpoint_widgets)

        def set_force_exploration(_, val: bool):
            self.force_exploration = val
            force_exploration.set_value(val)

        def set_step_by_step(_, val: bool):
            self.step_by_step = val
            step_by_step.set_value(val)

        def set_interface(_, val: bool):
            self.interface = val
            interface.set_value(val)
            toggle_widgets(self.interface, interface_widgets)

        def set_terminal(_, val: bool):
            self.terminal = val
            terminal.set_value(val)
            toggle_widgets(self.terminal, [terminal_speed])

        self.menu = pygame_menu.Menu(
            "SNAKE", 800, 800, theme=pygame_menu.themes.THEME_GREEN,
            columns=2, rows=12
        )
        self.menu.add.text_input(
            'Height :  ', default='10', onchange=set_height)
        self.menu.add.text_input(
            'Width :  ', default='10', onchange=set_width)
        training: Widget = self.menu.add.selector(
            'Training :  ', [('No', 0), ('Yes', 1)], onchange=set_training_mode)
        save: Widget = self.menu.add.selector(
            'Save :  ', [('No', 0), ('Yes', 1)], onchange=set_save_training)
        save_as: Widget = self.menu.add.text_input(
            'Save as :  ', default='experimentation_00',
            onchange=self.__setattr('save_as', str))
        save_in: Widget = self.menu.add.text_input(
            'Save in :  ', default='./weights/casual/',
            onchange=self.__setattr('save_in', str))
        epochs: Widget = self.menu.add.text_input(
            'Epochs :  ', default='1000', onchange=self.__setattr('epochs', int))
        learning_rate: Widget = self.menu.add.text_input(
            'Learning Rate :  ', default='0.9',
            onchange=self.__setattr('learning_rate', float))
        epsilon_greedy: Widget = self.menu.add.text_input(
            'Epsilon Greedy :  ', default='0.1',
            onchange=self.__setattr('epsilon_greedy', float))
        force_exploration: Widget = self.menu.add.selector(
            'Force Exploration :  ', [('No', 0), ('Yes', 1)],
            onchange=set_force_exploration)
        checkpoint: Widget = self.menu.add.selector(
            'Load checkpoint :  ', [('No', 0), ('Yes', 1)],
            onchange=set_load_checkpoint)
        load_data_from: Widget = self.menu.add.text_input(
            'Load data from :  ', default='',
            onchange=self.__setattr('load_data_from', str))
        load_data_from.readonly = True
        data_button = self.menu.add.button('Browse', select_load_data_file)
        load_weights_from: Widget = self.menu.add.text_input(
            'Load weights from :  ', default='',
            onchange=self.__setattr('load_weights_from', str))
        load_weights_from.readonly = True
        weights_button = self.menu.add.button('Browse', select_load_weights_file)
        ai_mode: Widget = self.menu.add.selector(
            'AI Mode :  ', [('No', 0), ('Yes', 1)], onchange=set_ai_mode)
        interface: Widget = self.menu.add.selector(
            'Interface :  ', [('No', 0), ('Yes', 1)], onchange=set_interface)
        cell_size: Widget = self.menu.add.text_input(
            'Cell size :  ', default='40',
            onchange=self.__setattr('cell_size', int))
        framerate: Widget = self.menu.add.text_input(
            'Framerate :  ', default='60',
            onchange=self.__setattr('framerate', int))
        interface_speed: Widget = self.menu.add.text_input(
            'Interface Speed :  ', default='200',
            onchange=self.__setattr('interface_speed', int))
        terminal: Widget = self.menu.add.selector(
            'Terminal :  ', [('No', 0), ('Yes', 1)], onchange=set_terminal)
        terminal_speed: Widget = self.menu.add.text_input(
            'Terminal Speed :  ', default='75',
            onchange=self.__setattr('terminal_speed', int))
        step_by_step: Widget = self.menu.add.selector(
            'Step by step :  ', [('No', 0), ('Yes', 1)],
            onchange=set_step_by_step)
        #TODO : enlever le widget de texte et modifier la variable directement depuis le bouton
        checkpoint_widgets: list[Widget] = [
            load_data_from, load_weights_from, data_button, weights_button]
        save_widgets: list[Widget] = [
            save_as, save_in]
        training_widgets: list[Widget] = [
            checkpoint, save, epochs, learning_rate,
            epsilon_greedy, force_exploration, step_by_step]
        interface_widgets: list[Widget] = [
            cell_size, framerate, interface_speed]
        toggle_widgets(
            False,
            training_widgets + interface_widgets + checkpoint_widgets + [
                terminal_speed] + save_widgets
        )
        self.menu.add.button('Play', self.start_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def start_game(self):
        self.total_epochs = self.epochs
        if self.load_checkpoint:
            data = load_data(self.load_data_from)
            self.previous_epochs = data["epochs"]
        if self.interface:
            self.screen = pygame.display.set_mode(
                Vector2(
                    self.cell_size * self.map_shape[1],
                    self.cell_size * self.map_shape[0]
                ))
            self.clock = pygame.time.Clock()
            pygame.time.set_timer(pygame.USEREVENT, self.interface_speed)
            self.background_color = (175, 215, 70)
            self.game_font = pygame.font.Font(
                'font/PoetsenOne-Regular.ttf', 25)
        if not self.terminal and self.training_mode:
            self.progression = tqdm(
                total=self.total_epochs, desc="Steps", unit="step")
        self.game_over_msg: str = ""
        self.max_lengths: list[int] = []
        self.movements: list[int] = []
        self.green_apples_ate: list[int] = []
        self.red_apples_ate: list[int] = []
        self.board = np.zeros((self.map_shape[0], self.map_shape[1]))
        self.walls: list = self.create_wall()
        self.snake: Snake = self.create_snake()
        self.green_apple: list = self.create_green_apple()
        self.red_apple: list = self.create_red_apple()
        self.green_apple_counter: int = 0
        self.red_apple_counter: int = 0
        self.hit_wall_counter: int = 0
        self.ate_himself_counter: int = 0
        self.movement_counter: int = 0
        self.play()

    def play(self):
        try:
            while True:
                if self.terminal:
                    self.display()
                if self.training_mode and not self.interface:
                    if self.is_finished():
                        self.game_over(losing_action=None)
                        continue
                    self.check_collectible()
                    terminal, action = self.snake.call_brain(
                        self.training_mode)
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
                            self.game_over(losing_action=None)
                            continue
                        if event.type == pygame.QUIT:
                            self.quit()
                        if (event.type == pygame.KEYDOWN) and (
                            event.key == pygame.K_ESCAPE
                        ):
                            self.game_over(losing_action=None, finish=True)
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
                                    self.game_over(losing_action=None)
                                    continue
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
                                self.training_mode)
                            if terminal:
                                self.game_over(losing_action=action)
                                if self.step_by_step:
                                    input()
                                continue
                            self.snake.move(action)
                            if self.step_by_step:
                                input()
                            elif self.terminal_speed != 0:
                                time.sleep(self.terminal_speed / 1000)
                        else:
                            _, action = self.snake.call_brain(
                                self.training_mode)
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
            apple = GreenApple(self.board, self.cell_size, self.interface)
            self.board[int(apple.pos.y)][int(apple.pos.x)] = GREEN_APPLE
            apples.append(apple)
        return apples

    def create_red_apple(self, nb: int = 1):
        apples: list = []
        for _ in range(nb):
            apple = RedApple(self.board, self.cell_size, self.interface)
            self.board[int(apple.pos.y)][int(apple.pos.x)] = RED_APPLE
            apples.append(apple)
        return apples

    def create_snake(self, brain: Brain = None):
        return Snake(
            self.board,
            self.cell_size,
            self.interface,
            brain,
            load_weights_from=self.load_weights_from,
            learning_rate=self.learning_rate,
            epsilon_greedy=self.epsilon_greedy,
            force_exploration=self.force_exploration
        )

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
            print("\n\n")
            print(underline + "=" * 9 + underline)
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
        #os.system('clear')
        separator = '    |    '
        symbols_len = 2
        width_board = len(self.board[0])
        snake_vision = self.snake.vision()
        underline = "=" * width_board * symbols_len
        if self.training_mode:

            print(underline + "=" * len(separator) + underline)
            print(f"REMAINING EPOCHS: {self.epochs}".center(
                width_board * symbols_len * 2 + len(separator)))
            print
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
                self.game_over_msg = "Snake ate himself !!! Feed your snake !"
            return True
        return False

    def is_snake_too_short(self) -> bool:
        if self.snake.get_length() < 2:
            if self.terminal:
                self.game_over_msg = "Snake too short..."
            return True
        return False

    def is_hitting_wall(self) -> bool:
        head = self.snake.get_head_position()
        for wall in self.walls:
            if head.x == wall.x and head.y == wall.y:
                if self.terminal:
                    self.game_over_msg = "Snake is gone, good bye snaky snakie"
                self.hit_wall_counter += 1
                return True
        return False

    def is_finished(self):
        if self.is_snake_too_short() or self.is_eating_body(
        ) or self.is_hitting_wall():
            return True
        return False

    def last_action(self, losing_action: Vector2):
        self.snake.call_brain(self.training_mode)
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
            print(self.game_over_msg)
            self.game_over_msg = ""
            print("\n=== GAME OVER ===")
            print(f"Length: {self.snake.get_length()}")
            self.quit()
        elif self.training_mode:
            if losing_action:
                self.last_action(losing_action)
            self.epochs -= 1
            if self.interface:
                print("\n=== GAME OVER ===")
                print(self.gamestep_graph_over_msg)
                self.game_over_msg = ""
                print(f"Length: {self.snake.get_length()}")
            if not self.terminal and self.progression is not None:
                self.progression.update(1)
            if self.epochs > 0 and not finish:
                self.reset()
            else:
                self.reset_training_counter()
                epochs = self.total_epochs - self.epochs
                if self.load_checkpoint:
                    epochs += self.previous_epochs
                if self.save:
                    save_data(
                        epochs,
                        self.snake.brain.q_table,
                        self.map_shape,
                        self.learning_rate,
                        self.epsilon_greedy,
                        self.force_exploration,
                        get_name(
                            epochs, "", self.map_shape,
                            self.save_as, self.save_in)
                    )
                    draw_step_graph(
                        epochs=self.total_epochs,
                        nb_steps=self.movements,
                        name=get_name(
                            epochs, "step_graph", self.map_shape,
                            self.save_as, self.save_in)
                    )
                    draw_object_graph(
                        epochs=self.total_epochs,
                        nb_green_apples_ate=self.green_apples_ate,
                        nb_red_apples_ate=self.red_apples_ate,
                        snake_sizes=self.max_lengths,
                        name=get_name(
                            epochs, "object_graph", self.map_shape,
                            self.save_as, self.save_in)
                    )
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
