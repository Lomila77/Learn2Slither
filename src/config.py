import pygame

TRAINING_MODE = False
LOAD_CHECKPOINT = False
AI_MODE = True
MAP_SHAPE = [10, 10]
LEARNING_RATE = 0.9
EPSILON_GREEDY = 0.0  # 0.1
EPOCHS = 20000

CELL_SIZE = 40
FRAMERATE = 60

SCREEN_UPDATE = pygame.USEREVENT
SPEED = 150 #150
TRAINING_SPEED = 0

FILENAME = "try_1"
DIRECTORY = "./weights/"
LOAD_WEIGHTS = "weights/10*10_epochs_40000_try_1_weights.pck"
LOAD_DATA = "weights/10*10_epochs_40000_try_1_config.json"
