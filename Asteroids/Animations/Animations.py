import pygame

import os

def animate(index=0):
    """misc animations that require cyclical animation"""
    multiple = 6
    index += 1

    if index < multiple:
        animation_speed = 0
    if index >= multiple+1 and index < multiple*2:
        animation_speed = 1

    if index >= multiple*4+1:
        index = 0

    return animation_speed

class Death_Animations(pygame.sprite.Sprite):
    """all death animations"""
    def __init__(self, death):
        super(Death_Animations, self).__init__()
        self.index = 0
        self.animation_speed = 0
        self.rect = death

    def update(self):
        """update of animation"""
        self.index += 1
        #as the animations are only placed once, this slows the animation down at a set rate then kills it once complete

        if self.index < self.multiple:
            self.animation_speed = 0 #basically an index of what image to use
        if self.index >= self.multiple+1 and self.index < self.multiple*2:
            self.animation_speed = 1
        if self.index >= self.multiple*2+1 and self.index < self.multiple*3:
            self.animation_speed = 2
        if self.index >= self.multiple*3+1 and self.index < self.multiple*4:
            self.animation_speed = 3

        if self.index >= self.multiple*4+1:
            self.index = 0
            self.kill()

        self.surf = self.images[self.animation_speed]

class Asteroid_Death(Death_Animations):
    """all asteroid death animation"""
    def __init__(self, death):
        super(Asteroid_Death, self).__init__(death)
        self.images = [pygame.image.load(os.path.join(os.path.dirname(__file__), 'astdeath1.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'astdeath2.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'astdeath3.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'astdeath4.png')).convert_alpha()]
        self.surf = self.images[self.animation_speed]
        self.multiple = 3

class Player_Death(Death_Animations):
    def __init__(self, death):
        """player death animation"""
        super(Player_Death, self).__init__(death)
        self.images = [pygame.image.load(os.path.join(os.path.dirname(__file__), 'shipdeath1.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'shipdeath2.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'shipdeath3.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'shipdeath4.png')).convert_alpha()]
        self.surf = self.images[self.animation_speed]
        self.multiple = 6

class AlienShip_Death(Death_Animations):
    """alien spaceship death animation"""
    def __init__(self, death):
        super(AlienShip_Death, self).__init__(death)
        self.images = [pygame.image.load(os.path.join(os.path.dirname(__file__), 'alienshipdeath1.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'alienshipdeath2.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'alienshipdeath3.png')).convert_alpha(), 
                       pygame.image.load(os.path.join(os.path.dirname(__file__), 'alienshipdeath4.png')).convert_alpha()]
        self.surf = self.images[self.animation_speed]
        self.multiple = 6