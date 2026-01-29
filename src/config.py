import pygame

TRAINING_MODE = True
LOAD_CHECKPOINT = False
AI_MODE = False
MAP_SHAPE = [10, 10]
LEARNING_RATE = 0.9
EPOCHS = 20000

CELL_SIZE = 40
FRAMERATE = 60

SCREEN_UPDATE = pygame.USEREVENT
SPEED = 0 #150

FILENAME = "retraining"
DIRECTORY = "./weights/"
LOAD_WEIGHTS = "weights/10*10_epochs_1000_retraining_weights.pck"
LOAD_DATA = "weights/10*10_epochs_1000_retraining_config.json"
