import pytest
from src.snake import Snake
from src.config import SNAKE_HEAD, SNAKE_BODY


def test_init_ok(empty_board):
    snake = Snake(empty_board)
    assert snake.head_id == SNAKE_HEAD
    assert snake.body_id == SNAKE_BODY
    assert snake.get_length() == 3


