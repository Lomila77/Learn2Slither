import pytest
from src.object import GreenApple, RedApple


def test_green_apple_nourrish(empty_board):
    apple = GreenApple(empty_board)
    assert apple.nourrish() == 1


def test_red_apple_nourrish(empty_board):
    apple = RedApple(empty_board)
    assert apple.nourrish() == -1