import pygame
import json


with open("config.json", "r") as f:
    _cfg = json.load(f)

FILENAME = _cfg["save_as"]
DIRECTORY = _cfg["save_in"]
LOAD_DATA = _cfg["load_data_from"]
LOAD_WEIGHTS = _cfg["load_weights_from"]
TRAINING_MODE = _cfg["training_mode"]
LOAD_CHECKPOINT = _cfg["load_checkpoint"]
AI_MODE = _cfg["ai_mode"]
MAP_SHAPE = _cfg["map_shape"]
LEARNING_RATE = _cfg["learning_rate"]
EPSILON_GREEDY = _cfg["epsilon_greedy"]
FORCE_EXPLORATION = _cfg["force_exploration"]
EPOCHS = _cfg["epochs"]
CELL_SIZE = _cfg["training_mode"]
FRAMERATE = _cfg["training_mode"]
SPEED = _cfg["training_mode"]
TRAINING_SPEED = _cfg["training_mode"]

SCREEN_UPDATE = pygame.USEREVENT
