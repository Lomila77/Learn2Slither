import pygame

TRAINING_MODE = True
LOAD_CHECKPOINT = True
AI_MODE = False
MAP_SHAPE = [10, 10]
LEARNING_RATE = 0.9
EPSILON_GREEDY = 0.0  # 0.9
FORCE_EXPLORATION = False
EPOCHS = 1000

CELL_SIZE = 40
FRAMERATE = 60

SCREEN_UPDATE = pygame.USEREVENT
SPEED = 150
TRAINING_SPEED = 0

# SAVE PLACE
FILENAME = "1"
DIRECTORY = "./weights/force_exploration/test/"

# LOAD FOR MONITORING OR CHECKPOINT
LOAD_DATA = (
    "weights/force_exploration/10*10_epochs_40000_force_exploration_config.json")
LOAD_WEIGHTS = (
    "weights/force_exploration/10*10_epochs_40000_force_exploration_weights.pck")
