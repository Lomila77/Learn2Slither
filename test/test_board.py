import pytest
import numpy as np
from src.IDS import GREEN_APPLE
from src.board import EnvGrid


def test_creation_ok(shape):
    env = EnvGrid(shape)
    assert list(env.board.shape) == shape


def test_envgrid_bad_shape_type():
    with pytest.raises(ValueError):
        EnvGrid("not_a_list")


def test_envgrid_wrong_shape_length():
    with pytest.raises(ValueError):
        EnvGrid([10])
        EnvGrid([10, 10, 10])


def test_envgrid_too_small(small_shape):
    with pytest.raises(ValueError):
        EnvGrid(small_shape)


def test_reset_ok(shape):
    env = EnvGrid(shape)
    env.reset()
    nb = np.count_nonzero(env.board == GREEN_APPLE)

    assert nb == 2
