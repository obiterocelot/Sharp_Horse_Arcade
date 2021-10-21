import pygame
from pygame.math import Vector2
from pygame.locals import RLEACCEL

from random import randint, choice, randrange
import math
import os

from Bullet.Bullet import Bullet
from Animations.Animations import AlienShip_Death

screen_width = 1600
screen_height = 1200 #placeholder screensize

pygame.mixer.init()
bullet_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), '..', 'Bullet', 'fire.wav'))
alienship_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'bangMedium.wav'))
SHARPMOVE = pygame.USEREVENT + 1
STOP = pygame.USEREVENT + 2
SHOOT = pygame.USEREVENT + 3
SPAWNALIEN = pygame.USEREVENT + 4
alien_spawntime = randint(5000, 9000)

def alienship_spawn(game):
    """instructions on how to spawn the alienship"""
    while len(game.alienships_list) < 1: #if there isn't an alienship already
        randomrole = randint(1, 2)
        if game.score < 30000: #and the score is less than 30000
            if randomrole == 1:
                game.spaceship = AlienShip_small() 
            if randomrole == 2:
                game.spaceship = AlienShip_large() #spawn randomly a big or small ship
        else: 
            game.spaceship = AlienShip_small() #all ships are small
        game.alienships_list.add(game.spaceship)
        game.all_sprites_list.add(game.spaceship)

        movement = randint(1500, 4000)
        pygame.time.set_timer(SHARPMOVE, movement)
        pygame.time.set_timer(SHOOT, 750)
        pygame.time.set_timer(SPAWNALIEN, 0)

class AlienShip(pygame.sprite.Sprite):
    """Alien Spaceship class"""
    def __init__(self, image):
        super(AlienShip, self).__init__()
        self.surf = pygame.image.load(image).convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.radius = self.surf.get_width() / 4
        self.pos = self.starting_pos()
        self.accel = self.starting_accel()
        self.max_speed = 5
        self.speed = Vector2(1, 0) #speed is an increasing upwards momentum.
        self.counter = 0 #counter helps despawn alien cleanly (without bugs)

    def starting_pos(self):
        """define starting position of alienship"""
        left = -40, randint(10, (screen_height - 10)) #quadrants are all the same size off-screen
        right = screen_width + 40, randint(10, (screen_height - 10))
        list = [left, right] #picks one from the left or right
        return Vector2(choice(list)) #random.choice picks one of the 2 options at random.

    def starting_accel(self):
        """define starting movement (going left or right"""
        if self.pos.x == -40: #if the alien is starting from the left of the screen
            return Vector2(1, 0) #move right
        if self.pos.x == (screen_width + 40): #vice versa
            return Vector2(-1, 0)

    def stop(self):
        """stop alien ship turn"""
        self.speed.y = 0
        self.accel.y = 0

    def shoot(self, game):
        """spawning your bullets"""
        bullet_accel = self.fire(game.player.pos, game.score) #bullet_accel is defined below, depending on what kind of ship
        bullet = Bullet(self.pos.x, self.pos.y, bullet_accel, self.pos)
        bullet_sound.set_volume(0.1)
        bullet_sound.play()
        game.all_sprites_list.add(bullet)
        game.enemy_bullets_list.add(bullet)

    def update(self):
        """defining space ship movement/update"""
        self.speed += self.accel #continue to update accel to a factor of the speed...

        if self.speed.length() > self.max_speed: #then scale it to the max_speed.
            self.speed.scale_to_length(self.max_speed)

        self.pos += self.speed
        self.rect.center = self.pos

        #screen wrap rules below allow. +/- 40 allow for smoother transition. Similar to Asteroids.
        if self.pos.x > screen_width + 40:
            self.pos.x = -40
            self.counter += 1
        if self.pos.x < -40:
            self.pos.x = screen_width + 40
            self.counter += 1
        if self.pos.y <= -40:
            self.pos.y = screen_height + 40
        if self.pos.y > screen_height + 40:
            self.pos.y = -40
    

    def collides_with(self, obj):
        """collision detection"""
        distance = self.pos.distance_to(obj.pos)
        return distance < self.radius + obj.radius

    def alien_death(self, game):
        """instructions on what happens on alienship death"""
        self.kill()
        self.onscreen_sound.stop() #stops the sound playing
        death = self.pos
        alienship_sound.set_volume(0.1)
        alienship_sound.play()
        death_animation = AlienShip_Death(death) #plays death animation at location of death
        game.animations_list.add(death_animation)
        game.all_sprites_list.add(death_animation)
        pygame.time.set_timer(SHARPMOVE, 0) #rests all alienship spawn timers
        pygame.time.set_timer(SHOOT, 0)
        pygame.time.set_timer(SPAWNALIEN, alien_spawntime)

class AlienShip_small(AlienShip):
    """smaller alienship"""
    def __init__(self):
        image = os.path.join(os.path.dirname(__file__), 'AlienshipS.png')
        self.score = 1000 #points are worth this amount
        self.onscreen_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'saucerSmall.wav'))
        self.onscreen_sound.set_volume(0.1)
        self.onscreen_sound.play(-1) #continue to loop sound while onscreen
        super(AlienShip_small, self).__init__(image)

    def fire(self, playerpos, score):
        """how the alienship shoots"""
        bulletx = playerpos.x #first we need to pull the player's position for the ship to aim at
        bullety = playerpos.y #both x and y axis
        if bulletx == 0:
            bulletx = 1
        if bullety == 0:
            bullety = 1 #otherwise 0 can make the bullet stop in place which we don't want
        if score > 30000:
            random_inaccuracy = randrange(-150, 150) #we don't want the spaceship to have perfect aim
        else:
            random_inaccuracy = randrange(-50, 50) #though it gets much more accurate eventually
        d = (bulletx + random_inaccuracy - self.pos.x, bullety + random_inaccuracy - self.pos.y) #then we make a tuple of the distance between the player and ship
        length = math.hypot(*d) #and calculate the angle of the vector
        direction = (d[0]/length, d[1]/length) #we can then apply the angle to the distance vector, giving us a direction to shoot.
        accel = (direction[0] * 10), (direction[1] * 10)
        #you want to multiply the axis' by 10 once you divide to give you appropriate speed. This will then be adjusted accordingly in the bullet function.
        #you want it to be at least 10 otherwise it's too slow.
        return Vector2(accel)
    
    def sharp_move(self, playerpos):
        """alienship turn angle"""
        #smaller ship moves towards the player
        #speed and accel determine turn direction - positive, negative or neutral
        if playerpos.y > self.pos.y:
            self.speed.y = 1
            self.accel.y = 1
        if playerpos.y < self.pos.y:
            self.speed.y = -1
            self.accel.y = -1
        if playerpos.y == self.pos.y:
            self.speed.y = 0
            self.accel.y = 0

class AlienShip_large(AlienShip):
    """larger alienship"""
    def __init__(self):
        image = os.path.join(os.path.dirname(__file__), 'AlienshipL.png')
        self.score = 200
        self.onscreen_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'saucerBig.wav'))
        self.onscreen_sound.set_volume(0.1)
        self.onscreen_sound.play(-1)
        super(AlienShip_large, self).__init__(image)

    def fire(self, playerpos, score): #note the unused variables are so they can be passed if its a smaller ship
        """how the alienship shoots"""
        #shoots randomly
        x = randrange(-11, 11) * 10
        y = randrange(-11, 11) * 10
        return Vector2(x, y)

    def sharp_move(self, playerpos):
        """alienship turn angle"""
        randomroll = randrange(0, 2) #turns randomly
        if randomroll == 0:
            self.speed.y = 1
            self.accel.y = 1
        if randomroll == 1:
            self.speed.y = -1
            self.accel.y = -1

