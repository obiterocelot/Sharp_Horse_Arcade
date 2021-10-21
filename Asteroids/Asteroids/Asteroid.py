import pygame
from pygame.math import Vector2
from pygame.locals import RLEACCEL

from random import randint, uniform, choice
import copy
import os

from Animations.Animations import Asteroid_Death

screen_width = 1600
screen_height = 1200

pygame.mixer.init()
asteroid_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'bangLarge.wav'))

SPAWNALIEN = pygame.USEREVENT + 4

def image_definer(filestarter):
    """randomly selects an image for asteroid"""
    randomrole = randint(1, 3)
    if randomrole == 1:
        image = os.path.join(os.path.dirname(__file__), filestarter + "1.png")
    if randomrole == 2:
        image = os.path.join(os.path.dirname(__file__), filestarter + "2.png")
    if randomrole == 3:
        image = os.path.join(os.path.dirname(__file__), filestarter + "3.png")
    return pygame.image.load(image).convert_alpha()

def initial_asteroid_spawn(game):
    """creates conditions for the asteroid spawn every cycle"""
    maximum_asteroid_spawn = 11 #figure based on og game - stops the increase of asteroids on spawn
    alien_spawntime = randint(5500, 9000) #randomises exactly when the alien spaceship is spawned
    if len(game.all_asteroids_list) == 0:
        #spawning new asteroids
        pygame.time.set_timer(SPAWNALIEN, 0)
        asteroid_spawn = int(game.score / 2000) + 5
        if asteroid_spawn > maximum_asteroid_spawn:
            asteroid_spawn = maximum_asteroid_spawn #sets the number of asteroids in the new spawn based on the score.
            
        while len(game.asteroid_BIG_list) < asteroid_spawn: #create the set number of asteroids from above
            new_asteroid = Asteroid_BIG()
            game.asteroid_BIG_list.add(new_asteroid)
            game.all_asteroids_list.add(new_asteroid)
            game.all_sprites_list.add(new_asteroid) #add them to the list
            pygame.time.set_timer(SPAWNALIEN, alien_spawntime)
            game.score_trigger = game.score + 1000


class Asteroid(pygame.sprite.Sprite):
    """Asteroid parent class"""
    def __init__(self, acceleration, speed):
        #all asteroids have the same features, but different sizes of those features. The children classes define those sizes and any extra features
        super(Asteroid, self).__init__()
        self.rect = self.surf.get_rect()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.radius = self.surf.get_width()
        self.accel = acceleration
        self.speed = Vector2(0, -1) #speed is an increasing upwards momentum. When scaled down by the max_speed, it allows you to set different speeds for the asteroids
        self.max_speed = speed

    def death_pos(self): #The asteroid.death_pos and death_accel are necessary figures to spawn the new kinds of asteroids on death
        """position at moment of collision with Bullet class"""
        return copy.deepcopy(self.pos)

    def death_accel(self):
        """acceleration/direction at moment of collision with Bullet class"""
        return copy.deepcopy(self.accel)

    def update(self):
        """asteroid movement/update"""
        self.speed += self.accel #continue to update accel to a factor of the speed...

        if self.speed.length() > self.max_speed: #then scale it to the max_speed.
            self.speed.scale_to_length(self.max_speed)

        self.pos += self.speed
        self.rect.center = self.pos

        #screen wrap rules below allow. +/- 40 allow for smoother transition
        if self.pos.x > screen_width + 40:
            self.pos.x = -40
        if self.pos.x < -40:
            self.pos.x = screen_width + 40
        if self.pos.y <= -40:
            self.pos.y = screen_height + 40
        if self.pos.y > screen_height + 40:
            self.pos.y = -40
            
    def asteroid_hit(self, game, death, accel, new_astsize, new_list, counter=0):
        """instruction on how to split asteroid. Small Asteroid is different"""
        if counter < 2:
            new_asteroid = new_astsize(accel, Vector2(death)) #essentially, creates a new list from the death accel pulled before def is called
            asteroid_sound.set_volume(0.1)
            asteroid_sound.play()
            game.all_asteroids_list.add(new_asteroid) #... and adds it to the necessary lists
            new_list.add(new_asteroid)
            game.all_sprites_list.add(new_asteroid)
            accel2 = copy.deepcopy(accel) #makes a copy of the accel (else both asteroids would use the same Vector)
            counter += 1 #only needs to happen twice
            self.asteroid_hit(game, death, accel2, new_astsize, new_list, counter) #and does it again

    def asteroid_death(self, game):
        """definition of what happens on an asteroid death"""
        death = self.death_pos()
        self.kill()
        accel = copy.deepcopy(self.death_accel()) #passes copies of accel for new asteroids
        death_animation = Asteroid_Death(death)
        game.animations_list.add(death_animation)
        game.all_sprites_list.add(death_animation) #plays death animation
        if self.score == 20: #if a large or medium asteroid, split it
            self.asteroid_hit(game, death, accel, Asteroid_MED, game.asteroid_MED_list)
        if self.score == 50:
            self.asteroid_hit(game, death, accel, Asteroid_SML, game.asteroid_SML_list)

class Asteroid_BIG(Asteroid):
    """Big Asteroid subclass of Asteroid"""
    def __init__(self):
        acceleration = Vector2(0, -1) #needs a starting accel to turn
        speed = uniform(1, 3.5) #uniform randomisation because of the float number
        self.surf = image_definer("asteroid_L") #pick a random image
        self.pos = self.starting_pos() #randomly generated off screen starter.
        super(Asteroid_BIG, self).__init__(acceleration, speed) #individually broken down so I can more easily adjust at a later date if need be.
        self.accel.rotate_ip(randint(0, 360)) #random turn is in children classes so as to give some illusion of momentum.
        self.surf = pygame.transform.rotozoom(self.surf, randint(0, 360), 1)
        self.radius = self.radius / 3
        self.score = 20

    def starting_pos(self):
        """provides a random off-screen starting position"""
        #starting positions are split into quadrants. starting_pos randomly generates a point position from each quadrant, then one of the quadrants is randomly selected.
        left = (randint(-80, -40), randint(-80, (screen_height + 80))) #quadrants are all the same size off-screen
        right = (randint((screen_width + 40), (screen_width + 80)), randint(-80, (screen_height + 80)))
        top = (randint(-80, (screen_width + 80)), randint(-80, -40))
        bottom = (randint(-80, (screen_width +80)), randint(screen_height + 40, screen_height + 80))
        list = [left, right, top, bottom] #list of the four quadrants
        return choice(list) #random.choice picks one of the 4 options at random.

class Asteroid_MED(Asteroid):
    """Medium Asteroid subclass of Asteroid"""
    def __init__(self, accel, death):
        acceleration = accel
        self.pos = death
        speed = uniform(2, 5)
        self.surf = image_definer("asteroid_M")
        super(Asteroid_MED, self).__init__(acceleration, speed)
        self.rect.center = self.pos
        self.accel.rotate_ip(randint(0, 90)) #can only turn a maximum of 90 degrees from the direction it was going.
        self.surf = pygame.transform.rotozoom(self.surf, randint(0, 360), 1)
        self.radius = self.radius / 4
        self.score = 50

class Asteroid_SML(Asteroid):
    """Small Asteroid subclass of Asteroid"""
    def __init__(self, accel, death):
        acceleration = accel
        self.pos = death
        speed = uniform(3, 6)
        self.surf = image_definer("asteroid_S")
        super(Asteroid_SML, self).__init__(acceleration, speed)
        self.rect.center = self.pos
        self.accel.rotate_ip(randint(0, 90))
        self.surf = pygame.transform.rotozoom(self.surf, randint(0, 360), 1)
        self.radius = self.radius / 12
        self.score = 100

def main():
    pass

if __name__ == '__main__':
    main()
