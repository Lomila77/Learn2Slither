import pygame
import numpy as np
from random import randint
from pygame.math import Vector2
from src.brain import Brain
from src.object import Object
from src.utils import (
    UP,
    DOWN,
    LEFT,
    RIGHT,
    GREEN_APPLE,
    RED_APPLE,
    SNAKE_HEAD,
    SNAKE_BODY,
    WALL,
    EMPTY_CASE,
    get_random_position,
    draw_position_on_board
)


class Snake(Object):

    def __init__(
        self,
        board: list[list[int]],
        brain: Brain | None = None,
        interface: bool = True,
        load_checkpoint: bool = False
    ) -> None:
        self.game_board = board
        self.interface = interface
        if self.interface:
            self.image_body_bl = pygame.transform.scale(
                pygame.image.load('graphics/body_bl.png').convert_alpha(),
                (self.cell_size, self.cell_size)
            )
            self.image_body_br = pygame.transform.scale(
                pygame.image.load('graphics/body_br.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_body_tl = pygame.transform.scale(
                pygame.image.load('graphics/body_tl.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_body_tr = pygame.transform.scale(
                pygame.image.load('graphics/body_tr.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_body_hor = pygame.transform.scale(pygame.image.load(
                    'graphics/body_horizontal.png'
                ).convert_alpha(), (self.cell_size, self.cell_size)
            )
            self.image_body_ver = pygame.transform.scale(pygame.image.load(
                'graphics/body_vertical.png').convert_alpha(),
                (self.cell_size, self.cell_size)
            )
            self.image_head_left = pygame.transform.scale(
                pygame.image.load('graphics/head_left.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_head_right = pygame.transform.scale(
                pygame.image.load('graphics/head_right.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_head_up = pygame.transform.scale(
                pygame.image.load('graphics/head_up.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_head_down = pygame.transform.scale(
                pygame.image.load('graphics/head_down.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_tail_left = pygame.transform.scale(
                pygame.image.load('graphics/tail_left.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_tail_right = pygame.transform.scale(
                pygame.image.load('graphics/tail_right.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_tail_up = pygame.transform.scale(
                pygame.image.load('graphics/tail_up.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.image_tail_down = pygame.transform.scale(
                pygame.image.load('graphics/tail_down.png').convert_alpha(),
                (self.cell_size, self.cell_size))
            self.crunch_sound = pygame.mixer.Sound('sound/crunch.wav')

        row, col = get_random_position(
            self.game_board,
            [WALL, RED_APPLE, GREEN_APPLE, SNAKE_BODY, SNAKE_HEAD]
        )
        # Store positions as (x, y) = (col, row)
        self.body: list[Vector2] = [Vector2(col, row)]

        x_axis, y_axis = self.watch()
        if brain is None:
            self.brain = Brain(
                self.game_board.shape,
                self.get_head_position(),
                x_axis,
                y_axis,
                self,
                load_checkpoint
            )
        else:
            self.brain = brain
        self.direction = self.brain.actions[randint(0, 3)]

        for _ in range(2):
            last_pos = self.body[-1]
            for action in self.brain.actions:
                body = last_pos + action
                # Board is indexed as board[row][col] = board[y][x]
                if (
                    0 < body.x < self.game_board.shape[1] and
                    0 < body.y < self.game_board.shape[0] and
                    self.game_board[int(body.y)][int(body.x)] == EMPTY_CASE and
                    body not in self.body
                ):
                    self.body.append(body)
                    break

        if self.get_length() != 3:
            raise ValueError("The snake is too short... No place available")

        for i, body in enumerate(self.body):
            id = SNAKE_HEAD if i == 0 else SNAKE_BODY
            draw_position_on_board(self.game_board, body, id)
        self.growth_effect = -1
        self.max_length = self.get_length()

    def update_head_graphics(self):
        body_direction = self.body[1] - self.body[0]
        head = None
        if body_direction == UP:
            head = self.image_head_down
        elif body_direction == DOWN:
            head = self.image_head_up
        elif body_direction == LEFT:
            head = self.image_head_right
        elif body_direction == RIGHT:
            head = self.image_head_left
        return head

    def update_tail_graphics(self):
        body_direction = self.body[-2] - self.body[-1]
        tail = None
        if body_direction == UP:
            tail = self.image_tail_down
        elif body_direction == DOWN:
            tail = self.image_tail_up
        elif body_direction == LEFT:
            tail = self.image_tail_right
        elif body_direction == RIGHT:
            tail = self.image_tail_left
        return tail

    def draw(self, screen):
        head = self.update_head_graphics()
        tail = self.update_tail_graphics()
        for index, block in enumerate(self.body):
            rect = pygame.Rect(
                int(block.x * self.cell_size),
                int(block.y * self.cell_size),
                self.cell_size,
                self.cell_size
            )

            if index == 0:
                screen.blit(head, rect)
            elif index == len(self.body) - 1:
                screen.blit(tail, rect)
            else:
                prev_block_dir = self.body[index + 1] - block
                next_block_dir = self.body[index - 1] - block
                if prev_block_dir.x == next_block_dir.x:
                    screen.blit(self.image_body_ver, rect)
                elif prev_block_dir.y == next_block_dir.y:
                    screen.blit(self.image_body_hor, rect)
                else:
                    if prev_block_dir.x == -1 and next_block_dir.y == -1 or \
                            prev_block_dir.y == -1 and next_block_dir.x == -1:
                        screen.blit(self.image_body_tl, rect)
                    elif prev_block_dir.x == 1 and next_block_dir.y == -1 or \
                            prev_block_dir.y == -1 and next_block_dir.x == 1:
                        screen.blit(self.image_body_tr, rect)
                    elif prev_block_dir.x == -1 and next_block_dir.y == 1 or \
                            prev_block_dir.y == 1 and next_block_dir.x == -1:
                        screen.blit(self.image_body_bl, rect)
                    elif prev_block_dir.x == 1 and next_block_dir.y == 1 or \
                            prev_block_dir.y == 1 and next_block_dir.x == 1:
                        screen.blit(self.image_body_br, rect)

    def play_crunch_sound(self):
        self.crunch_sound.play()

    def get_position(self):
        return self.body

    def get_head_position(self):
        return self.body[0]

    def get_body_position(self):
        return self.body[1:]

    def get_length(self):
        return len(self.body)

    def update_max_length(self):
        length = self.get_length()
        if length > self.max_length:
            self.max_length = length

    def move(self, action: Vector2):
        self.direction = action
        # Clear current snake positions
        for pos in self.body:
            draw_position_on_board(self.game_board, pos, EMPTY_CASE)
        body_copy = (
            self.body[:] if self.growth_effect == 0 else self.body[
                :self.growth_effect]
        )
        self.growth_effect = -1
        if len(body_copy) != 0:
            body_copy.insert(0, body_copy[0] + self.direction)
        else:
            body_copy.append(self.get_head_position() + self.direction)
        self.body = body_copy[:]
        for i, pos in enumerate(self.body):
            id = SNAKE_HEAD if i == 0 else SNAKE_BODY
            draw_position_on_board(self.game_board, pos, id)
        self.update_max_length()

    def eat(self, nutrient: int = 0):
        self.growth_effect += nutrient
        if self.interface:
            self.play_crunch_sound()

    def vision(self):
        x_axis, y_axis = self.watch()
        board: np.ndarray = np.full(self.game_board.shape, 6)
        head = self.get_head_position()
        # Horizontal line at y = head.y
        board[int(head.y)] = x_axis
        # Vertical line at x = head.x
        for row in range(board.shape[0]):
            board[row][int(head.x)] = y_axis[row]
        return board

    def watch(self):
        head: Vector2 = self.get_head_position()
        # board[row][col] => board[y][x]
        # x_axis: horizontal line (vary x) at fixed y
        x_axis: list[int] = list(self.game_board[int(head.y)])
        # y_axis: vertical line (vary y) at fixed x
        y_axis: list[int] = [
            self.game_board[row][int(head.x)]
            for row in range(self.game_board.shape[0])
        ]
        return x_axis, y_axis

    def call_brain(self, training: bool = False):
        x_axis, y_axis = self.watch()
        shape = self.game_board.shape
        if shape[0] > 10 or shape[1] > 10:
            head = self.get_head_position()
            height, width = shape

            start_row = max(0, min(height - 10, int(head.y) - 5))
            start_col = max(0, min(width - 10, int(head.x) - 5))
            end_row = start_row + 10
            end_col = start_col + 10
            local_board = self.game_board[start_row:end_row, start_col:end_col]

            local_body = [
                Vector2(pos.x - start_col, pos.y - start_row)
                for pos in self.body
            ]
            local_head = local_body[0]

            local_x_axis = list(local_board[int(local_head.y)])
            local_y_axis = [
                local_board[row][int(local_head.x)] for row in range(10)
            ]

            action = self.brain.call_brain(
                local_x_axis,
                local_y_axis,
                local_body,
                training=training
            )
        else:
            action = self.brain.call_brain(
                x_axis, y_axis, self.get_position(), training=training)
        return action
