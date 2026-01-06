import pytest
import numpy as np
from src.utils import GREEN_APPLE
from src.board import Board


def test_creation_ok(shape):
    env = Board(shape)
    assert list(env.board.shape) == shape


def test_board_bad_shape_type():
    with pytest.raises(ValueError):
        Board("not_a_list")


def test_board_wrong_shape_length():
    with pytest.raises(ValueError):
        Board([10])
        Board([10, 10, 10])


def test_board_too_small(small_shape):
    with pytest.raises(ValueError):
        Board(small_shape)


def test_reset_ok(shape):
    env = Board(shape)
    env.reset()
    nb = np.count_nonzero(env.board == GREEN_APPLE)

    assert nb == 2
