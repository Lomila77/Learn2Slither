import pygame
from pygame.math import Vector2
from src.config import CELL_SIZE
from src.brain import Brain
from src.object import Object
from src.utils import get_random_position
from src.utils import (
    UP,
    DOWN,
    LEFT,
    RIGHT,
    SNAKE_HEAD,
    SNAKE_BODY,
    EMPTY_CASE
)


class Snake(Object):

    def __init__(self, board: list[list[int]]) -> None:
        self.head_id = SNAKE_HEAD
        self.body_id = SNAKE_BODY
        self.brain = Brain(board.shape)
        # TODO: modifier la direction de base
        self.direction = Vector2(1, 0)
        self.game_board = board
        self.image_body_bl = pygame.transform.scale(
            pygame.image.load('graphics/body_bl.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE)
        )
        self.image_body_br = pygame.transform.scale(
            pygame.image.load('graphics/body_br.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_body_tl = pygame.transform.scale(
            pygame.image.load('graphics/body_tl.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_body_tr = pygame.transform.scale(
            pygame.image.load('graphics/body_tr.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_body_hor = pygame.transform.scale(
            pygame.image.load('graphics/body_horizontal.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_body_ver = pygame.transform.scale(
            pygame.image.load('graphics/body_vertical.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_head_left = pygame.transform.scale(
            pygame.image.load('graphics/head_left.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_head_right = pygame.transform.scale(
            pygame.image.load('graphics/head_right.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_head_up = pygame.transform.scale(
            pygame.image.load('graphics/head_up.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_head_down = pygame.transform.scale(
            pygame.image.load('graphics/head_down.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_tail_left = pygame.transform.scale(
            pygame.image.load('graphics/tail_left.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_tail_right = pygame.transform.scale(
            pygame.image.load('graphics/tail_right.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_tail_up = pygame.transform.scale(
            pygame.image.load('graphics/tail_up.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.image_tail_down = pygame.transform.scale(
            pygame.image.load('graphics/tail_down.png').convert_alpha(),
            (CELL_SIZE, CELL_SIZE))
        self.crunch_sound = pygame.mixer.Sound('sound/crunch.wav')



        x, y = get_random_position(self.game_board)
        self.body: list[Vector2] = [Vector2(x, y)]
        for _ in range(2):
            last_pos = self.body[-1]
            for action in self.brain.actions:
                new_place = last_pos + action
                if (
                    0 <= new_place.x < self.game_board.shape[0] and
                    0 <= new_place.y < self.game_board.shape[1] and
                    self.game_board[int(new_place.x)][int(new_place.y)] == EMPTY_CASE and
                    new_place not in self.body
                ):
                    self.body.append(new_place)
                    break

        if self.get_length() != 3:
            print(self.body)
            raise ValueError("The snake is too short... No place available")
        
        for i, snake_piece in enumerate(self.body):
            id = SNAKE_HEAD if i == 0 else SNAKE_BODY
            self.game_board[int(snake_piece.x)][int(snake_piece.y)] = id

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
                int(block.x * CELL_SIZE),
                int(block.y * CELL_SIZE),
                CELL_SIZE,
                CELL_SIZE
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

    def move(
        self, action: Vector2, growth_effect: int = -1
    ):
        self.direction = action
        for pos in self.body:
            self.game_board[int(pos.x)][int(pos.y)] = EMPTY_CASE
        body_copy = (
            self.body[:] if growth_effect == 0 else self.body[:growth_effect])
        body_copy.insert(0, body_copy[0] + self.direction)
        self.body = body_copy[:]
        if 0 <= self.get_head_position().x < len(self.game_board[0]) and \
                0 <= self.get_head_position().y < len(self.game_board[1]):
            for i, pos in enumerate(self.body):
                id = SNAKE_HEAD if i == 0 else SNAKE_BODY
                self.game_board[int(pos.x)][int(pos.y)] = id

    def eat(self, nutrient: int = 0):
        print(f"Snack {nutrient}")
        self.move(self.direction, -1 + nutrient)
        self.play_crunch_sound()

    def watch(self):
        head_x, head_y = self.get_position()
        x_axis: list[tuple[int, int]] = []
        y_axis: list[tuple[int, int]] = []
        for row in self.game_board:
            for col in row:
                if row == head_x:
                    x_axis.append((row, col))
                elif col == head_y:
                    y_axis.append((row, col))
        return x_axis, y_axis

    def call_brain(self):
        x_axis, y_axis = self.watch()

