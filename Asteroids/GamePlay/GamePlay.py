import pygame

from Player.Player import GameoverPlayer, Player

#timers userd
SPAWNALIEN = pygame.USEREVENT + 4
RESPAWN = pygame.USEREVENT + 5

class GamePlay():
    def __init__(self):
        super(GamePlay, self).__init__()
        self.lives = 3
        self.score = 0
        self.score_trigger = 1000
        self.player = Player()
        self.life_trigger = 10000
        self.state = 'setup'
        self.screen_width = 1600
        self.screen_height = 1200
        #all sprite lists
        self.bullets_list = pygame.sprite.Group()
        self.player_list = pygame.sprite.Group()
        self.asteroid_BIG_list = pygame.sprite.Group()
        self.asteroid_MED_list = pygame.sprite.Group()
        self.asteroid_SML_list = pygame.sprite.Group()
        self.all_asteroids_list = pygame.sprite.Group()
        self.animations_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.enemy_bullets_list = pygame.sprite.Group()
        self.alienships_list = pygame.sprite.Group()
        self.floating_asteroids = pygame.sprite.Group()
        self.spaceship = None #only one alien spaceship at a time so can be set to game

    def increase_score(self, score):
        """increase score, but stops at 99999"""
        if score < 99999:
            self.score += score

    def lost_life(self):
        """decrease life"""
        self.lives -= 1

    def additional_life(self):
        """add life every 10000 points"""
        if self.score > self.life_trigger:
            self.lives += 1
            self.life_trigger = self.score + 10000

    def gameover(self):
        """sets player conditions at gameover"""
        pygame.time.set_timer(RESPAWN, 0)
        self.player.kill()
        pygame.time.set_timer(SPAWNALIEN, 0)
        self.player = GameoverPlayer()

    #all collision conditions
    def bullet_hit_asteroid(self):
        """bullet vs asteroid"""
        for asteroid in self.all_asteroids_list:
            for bullet in self.bullets_list:
                if bullet.collides_with(asteroid):
                    asteroid.asteroid_death(self)
                    bullet.kill()
                    if bullet.startingpos == None:
                        self.increase_score(asteroid.score)

    def player_hit_asteroid(self):
        """asteroid vs player"""
        for asteroid in self.all_asteroids_list:
            if self.player.immunity == False:
                if self.player.collides_with(asteroid):
                    self.player.player_death(self)
                    asteroid.asteroid_death(self)
                    self.increase_score(asteroid.score)

    def alien_hit_asteroid(self):
        """alien spaceship vs asteroid"""
        for asteroid in self.all_asteroids_list:
            for alien in self.alienships_list:
                if alien.collides_with(asteroid):
                    asteroid.asteroid_death(self)
                    alien.alien_death(self)

    def alien_hit_player(self):
        """alien spaceship vs player (alien hits player)"""
        for alien in self.alienships_list:
            if self.player.immunity == False:
                if self.player.collides_with(alien):
                    self.player.player_death(self)
                    alien.alien_death(self)
        for bullet in self.enemy_bullets_list:
            if bullet.collides_with(self.player):
                self.player.player_death(self)
                bullet.kill()

    def player_hit_alien(self):
        """player vs alien spaceship (player hits alien)"""
        for bullet in self.bullets_list:
            for alien in self.alienships_list:
                if bullet.collides_with(alien):
                    bullet.kill()
                    alien.alien_death(self)
                    self.increase_score(alien.score)