import pygame as pg
import math

vec = pg.math.Vector2


# Game properties
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0,0,0)  # Black
COL1 = (69,139,116)  # Aquamarine4
# Class attributes
MAX_SPEED = 6
MIN_SPEED = 3
MAX_FORCE = 0.5
SEPARATION_FACTOR = 0.05
ALIGNMENT_FACTOR = 0.05
COHESION_FACTOR = 0.0005
CHASE_RANGE = 150

TITLE = "Boids"
