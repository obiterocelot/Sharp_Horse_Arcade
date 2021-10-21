import pygame
from pygame.math import Vector2
from pygame.locals import RLEACCEL

import copy
import math
import os

screen_width = 1600
screen_height = 1200
max_speed = 10

class Bullet(pygame.sprite.Sprite):
    """this class defines the bullets that your controlable sprite fires"""
    def __init__(self, x, y, accel, startingpos):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load(os.path.join(os.path.dirname(__file__), 'bullet.png')).convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.radius = self.surf.get_width() / 20
        self.rect = self.surf.get_rect(center=(100, 100))
        self.pos = Vector2(x, y) #let's start in the middle of the screen
        self.accel = accel #this is the pulled number from the ship's gun vector. Find this pull on the space key command
        self.startingpos = copy.deepcopy(startingpos)

    def update(self):
        """updates the location of the sprite every frame. Incl kill command"""
        self.pos += self.accel
        self.rect.center = self.pos
        #kill the bullet once off screen to keep game slick
        if self.pos.x > screen_width or self.pos.x < 0:
            self.kill()
        if self.pos.y > screen_height or self.pos.y <= 0:
            self.kill()
        if self.accel.length() > max_speed -1: #scale to keep a consistent speed. 1 less lower than max speed of ship is a figure found from studies of original asteroids(link above)
            self.accel.scale_to_length(max_speed -1)
        
        if self.startingpos != None:
            x = self.pos.x
            mx = self.startingpos[0]
            y = self.pos.y
            my = self.startingpos[1]
            d = math.sqrt((x-mx)**2+(y-my)**2)
            if d > 600:
                self.kill()
                
    def collides_with(self, obj):
        """collision detection"""
        distance = self.pos.distance_to(obj.pos)
        return distance < self.radius + obj.radius

def main():
    pass

if __name__ == '__main__':
    main()
