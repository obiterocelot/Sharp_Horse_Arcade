#-------------------------------------------------------------------------------
# Name:        Asteroids
# Author:      sarah
# Created:     15/09/2020
# Copyright:   (c) sarah 2020
# Licence:     Coding help on Vectors: https://stackoverflow.com/questions/48856922/pygame-how-to-make-sprite-move-in-the-direction-its-facing-with-vectors
#              Help with structure of game loop: https://pythonprogramming.net/pygame-start-menu-tutorial/
#              Figures on appropriate sizes of sprites etc: http://www.retrogamedeconstructionzone.com/2019/10/asteroids-by-numbers.html
#              Help with info on scoring and game mechanics: http://tips.retrogames.com/gamepage/asteroid.html
#
#              Assistance with setting up the gameover screen: https://www.geeksforgeeks.org/how-to-create-a-text-input-box-with-pygame/
#-------------------------------------------------------------------------------


#minimal game initialiser only needs the following things:
#1. initialising pygame with pygame.init()
#2. setting up a timer to stabilise the framerate
#3. setting up the screen
#4. the game instructions in a while True statement.    

import pygame

from GamePlay.GameStates import Gamestates

pygame.init() #starts pygame
clock = pygame.time.Clock()
screen_width = 1600
screen_height = 1200
screen = pygame.display.set_mode((screen_width, screen_height)) #environment needs to be set up asap in order to load sprites onto it.
game = Gamestates(screen) #gamestates controls what part of the game is running on screen and what each part does.
 
while True:
    game.state_manager() #instructions on how to cycle through game states.
    clock.tick(60) #stabilises the framerate to a maximum of 60 frames per second.