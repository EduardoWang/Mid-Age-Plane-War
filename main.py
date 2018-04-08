import pygame
import sys

pygame.init()

size = width, height = 1280, 1080
black = 0, 0, 0

screen = pygame.display.set_mode(size)
background = pygame.image.load("map.jpg")
back_rect = background.get_rect()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.blit(background, back_rect)
    pygame.display.flip()
