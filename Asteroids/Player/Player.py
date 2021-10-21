import pygame
from pygame.math import Vector2
from pygame.locals import (RLEACCEL, K_UP, K_LEFT, K_RIGHT)

import copy
import os
from random import randrange, randint

from Bullet.Bullet import Bullet
from Animations.Animations import Player_Death

#easier to just set these here rather than pulling from gameplay. Otherwise could cause cyclical import
screen_width = 1600
screen_height = 1200
max_speed = 10 #this is the max speed for all sprites - including bullets

#have to init mixer if any sounds are loaded in module
pygame.mixer.init()
thruster_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'thrust.wav'))
bullet_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), '..', 'Bullet', 'fire.wav'))
ship_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'bangSmall.wav'))

#alien user events that are used here (connected to player death)
SHARPMOVE = pygame.USEREVENT + 1
STOP = pygame.USEREVENT + 2
SHOOT = pygame.USEREVENT + 3
SPAWNALIEN = pygame.USEREVENT + 4
alien_spawntime = randint(5000, 9000)

#player user events used in module.
RESPAWN = pygame.USEREVENT + 5
HYPERDRIVE = pygame.USEREVENT + 6

class Player(pygame.sprite.Sprite):
    """this class defines the attributes of your controlable sprite"""
    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'ship.png')).convert_alpha()
        self.thrustimage = pygame.image.load(os.path.join(os.path.dirname(__file__), 'thrustersmall.png')).convert_alpha()
        self.surf = self.image #need to be seperately defined to switch between standard image and thruster
        self.surf.set_colorkey((0, 0, 0), RLEACCEL) #important if surfaces are transparent
        self.surf_copy = self.surf #copy necessary for rotation
        self.rect = self.surf.get_rect() #all sprites need a rect in order to be blitted when cycling through all_sprites list
        self.accel = Vector2(0, -0.05)  # The acceleration Vector points upwards.
        self.pos = Vector2(screen_width / 2, screen_height / 2) #starting in the middle of the screen
        self.angle = 0
        self.turn_speed = 0
        self.radius = self.surf.get_width() / 2 #useful for collision detection
        self.speed = Vector2(0, 0)
        self.gun_accel = Vector2(0, -10) #creation of the ship's gun
        self.immunity = False #required for respawn
        self.gameover = False #required to help set player instructions when it is gameover
        self.hdcooldown = False #required to stop spanning of hyperdrive

    def update(self, pressed_keys):
        """updates the location of the sprite every frame if moved by keypress"""
        #pressing LEFT or RIGHT will start the player turning in the given direction
        if pressed_keys[K_LEFT]:
            self.turn_speed = -3 #can continue to change these ints to increase/decrease turn speed
            self.rotate()
        if pressed_keys[K_RIGHT]:
            self.turn_speed = 3
            self.rotate()
        #pressing up will increase the player speed by a factor of the acceleration
        if self.gameover == False: #only if it's not gameover
            if pressed_keys[K_UP]:
                thruster_sound.set_volume(0.05) #for some reason imported sounds are super loud
                thruster_sound.play()
                self.surf_copy = self.thrustimage
                self.surf = pygame.transform.rotozoom(self.surf_copy, -self.angle, 1) #for some reason, rotozoom with the scale produces a far better image quality than just rotate
                self.speed += self.accel

        #setting a max speed and adjusting the Vector to that max speed
        if self.speed.length() > max_speed:
            self.speed.scale_to_length(max_speed) #scales the direction down to the speed so it's not expontentially if you're going at an angle

        self.pos += self.speed #updates the new player position to a factor of the given speed
        self.rect.center = self.pos #updates the surface drawing to the new player position

    def rotate(self):
        """providing the rotation of the acceleration Vector"""
        self.accel.rotate_ip(self.turn_speed) #acceleration Vector is the one moving (speed is just by what factor)
        self.gun_accel.rotate_ip(self.turn_speed)
        self.angle += self.turn_speed #turn to a new angle as key is held down
        #this bit allows you to just go round and round in circles
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
        #transforms the ship sprite
        self.surf = pygame.transform.rotozoom(self.surf_copy, -self.angle, 1) 
        self.rect = self.surf.get_rect(center=self.rect.center)

    def get_gun_vec(self):
        """pull a copy of the gun vector on command"""
        return copy.deepcopy(self.gun_accel) #this way the bullets wont turn as the ship turns

    def shoot(self, accel, game):
        """spawning your bullets"""
        bullet = Bullet(self.pos.x, self.pos.y, accel, None) #spawning from the ship's location
        bullet_sound.set_volume(0.1)
        bullet_sound.play()
        game.all_sprites_list.add(bullet) #adding them to the list
        game.bullets_list.add(bullet)

    def screen_wrap(self):
        """rules for player wrapping around screen (each sprite is a little different)"""
        if self.gameover == False: #only set if gameover false so the player can be set offscreen, away from incoming asteroids
            if self.pos.x > screen_width:
                self.pos.x = 0
            if self.pos.x < 0:
                self.pos.x = screen_width
            if self.pos.y <= 0:
                self.pos.y = screen_height
            if self.pos.y > screen_height:
                self.pos.y = 0

    def hyperdrive(self):
        """allows character to blit to a new location instantly"""
        if self.hdcooldown == False: #there is a small cooldown to prevent hyperdrive spamming
            self.pos.x = randrange(10, screen_width-10)
            self.pos.y = randrange(10, screen_height-10) #chose a random location on the screen
            self.hdcooldown = True #turn on the cooldown
            pygame.time.set_timer(HYPERDRIVE, 3000) #and set a timer to turn off the cooldown

    def collides_with(self, obj):
        """collision detector"""
        #Note: collisions are designed this way because it was found that the game couldn't keep up with the speed of the 
        #mask when using mask detection. Resulted in wildly inaccurate game collision as well as some weird bugs.
        #While not perfect pixel collision, this works better
        distance = self.pos.distance_to(obj.pos)
        return distance < self.radius + obj.radius

    def player_death(self, game):
        """list of instructions if the player is hit"""
        self.immunity = True #stops secondary collision bug
        self.kill() #removes player from all lists
        game.lost_life() #decrease life
        ship_sound.set_volume(0.1)
        ship_sound.play() #play collision sound
        death = self.pos
        death_animation = Player_Death(death) #play death animation at player position
        game.animations_list.add(death_animation)
        game.all_sprites_list.add(death_animation)
        for bullets in game.enemy_bullets_list:
            bullets.kill() #remove any bullets still in air
        for aliens in game.alienships_list:
            aliens.kill()
            aliens.onscreen_sound.stop() #remove any spaceships around and reset their spawn
            pygame.time.set_timer(SHARPMOVE, 0)
            pygame.time.set_timer(SHOOT, 0)
            pygame.time.set_timer(SPAWNALIEN, alien_spawntime)
        pygame.time.set_timer(RESPAWN, 500) #respawn the character in a few moments

class GameoverPlayer(Player):
    """creates a character instance that can't move or be seen while gameover screen is blitted over asteroids"""
    def __init__(self):
        super(GameoverPlayer, self).__init__()
        self.pos = Vector2(-500, -500) #puts character far off screen
        self.gameover = True #sets the rules that player cannot be moved etc
        self.immunity = True #just in case, confirms player cannot be killed