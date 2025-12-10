import numpy as np
from pygame.math import Vector2


class Brain:
    def __init__(self, shape) -> None:
        self.actions = [
            Vector2(-1, 0),    # Up
            Vector2(1, 0),     # Down
            Vector2(0, -1),    # Left
            Vector2(0, 1)      # Right
        ]

        self.q_table = np.zeros((shape[0] * shape[1], len(self.actions)))

    def call_brain(self, x_axis, y_axis):
        action = 1
        return self.take_action(action)

    def take_action(self, action) -> tuple:
        return self.actions[action]
