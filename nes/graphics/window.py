import pygame
from pygame.locals import *
from nes.console import Console
import sys
import time
import os

def _abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)


def main():
    t = time.time()
    pygame.init()

    size = (320, 240)

    width = size[0]
    height = size[1]

    black = (0, 0, 0)

    screen = pygame.display.set_mode(size)
    pixels = pygame.Surface(size).convert()
    pixels.fill((0, 0, 0)) # Black
    screen.blit(pixels, (0, 0))
    console = Console(_abs_path('../../tests/color_test.nes'), pixels)

    is_frame_even = 0
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)

        old_frame_val = console.ppu.frame
        while console.ppu.frame == old_frame_val:
            console.step()

        screen.blit(pixels, (0, 0))
        pygame.display.flip()
        is_frame_even = not is_frame_even

