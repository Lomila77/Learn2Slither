import pytest
import numpy as np
from src.board import EnvGrid


@pytest.fixture
def shape():
    shape: np.ndarray = np.random.randint(low=10, high=500, size=2)
    return list(shape)


@pytest.fixture
def small_shape():
    shape: np.ndarray = np.random.randint(low=0, high=10, size=2)
    return list(shape)


@pytest.fixture
def starting_position(shape: list[int]):
    starting_position: np.ndarray = np.random.randint(
        low=0, high=shape, size=2)
    return list(starting_position)


@pytest.fixture
def starting_position_out_of_range(shape: list[int]):
    starting_position: np.ndarray = np.random.randint(
        low=shape, high=1000, size=2)
    return list(starting_position)


def get_random_free_position(
    board: list[list[int]], forbidden_positions: list[int] = []
):
    positions = []
    for row in board.shape[0]:
        for col in board.shape[1]:
            if board[row][col] not in forbidden_positions:
                positions.append((row, col))
    if not positions:
        raise ValueError("Map is fullfilled")
    return positions[np.random.choice(len(positions))]


@pytest.fixture
def empty_board(shape):
    board = np.zeros(shape)
    return board


@pytest.fixture
def board_with_object(empty_board):
    forbidden_positions: list[int] = [3, 4]
    x, y = get_random_free_position(empty_board, forbidden_positions)
    empty_board[x][y] = 3  # Green Apple
    x, y = get_random_free_position(empty_board, forbidden_positions)
    empty_board[x][y] = 3  # Green Apple
    x, y = get_random_free_position(empty_board, forbidden_positions)
    empty_board[x][y] = 4  # Red Apple
    return empty_board


# TODO: Rajouter le corps
@pytest.fixture
def board_with_object_and_head_snake(shape):
    env = EnvGrid(shape)
    return env.board
