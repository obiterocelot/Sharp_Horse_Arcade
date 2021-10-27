import sys
import itertools
import os

import pygame
from pygame.locals import (KEYDOWN, KEYUP, K_ESCAPE, K_SPACE, K_LCTRL, K_UP, K_n, K_h, QUIT, MOUSEBUTTONDOWN)

#importing all the self-made modules
from Asteroids.Asteroid import Asteroid_BIG, initial_asteroid_spawn
from GamePlay.GamePlay import GamePlay
from SpaceShip.Spaceship import alienship_spawn
from Player.Player import Player
from GamePlay.Neonfont import apply_blur, set_image
from GamePlay.Highscores import add_to_highscores, get_dict

class Gamestates():
    """defining and controlling each state the game can be in."""
    def __init__(self, screen):
        super(Gamestates, self).__init__()
        self.state = 'setup' #used to pass through the states
        self.game = GamePlay() #sets up the container that stores the global variables and counters
        self.screen = screen #screen is defined in the index
   
    def setup(self):
        """the starting/opening state of the game"""
        set_asteroids = 4 #helps define how many asteroids are floating in background

        for event in pygame.event.get():
            #standard exit options
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                #most key presses will pass you onto the main game, but if you specifically press h you can view the highscores
                self.state = 'main'
            if event.type == KEYDOWN:
                if event.key == K_h:
                    self.state = 'highscores'
                else:
                    self.state = 'main'

        while len(self.game.floating_asteroids) < set_asteroids:
            #loop creates Big_Asteroids to the number of max_asteroids
            new_asteroid = Asteroid_BIG()
            self.game.floating_asteroids.add(new_asteroid)
            
        self.screen.fill((0, 0, 0)) #fill the screen with black
        surf = pygame.image.load(os.path.join(os.path.dirname(__file__), 'gamestart.jpg')) #load up the gamestart image
        new_surf = pygame.transform.scale(surf, (self.game.screen_width+2, self.game.screen_height+2)) #scale the image to fit screen.
        #need to made it just a little larger than the screen width otherwise it creates a border
        self.screen.blit(new_surf, (-2, -2)) #draws the screen image

        self.game.floating_asteroids.update() #asteroids movement found in asteroids module
        for each in self.game.floating_asteroids:
            self.screen.blit(each.surf, each.rect) #draws all asteroids

        pygame.display.update() #make sure you only have one update or flip per game state

    def main(self):
        """the game's main loop"""

        self.game = GamePlay() #resets the game each playthrough
        clock = pygame.time.Clock() #need to call own FPS stabiliser here (no idea why)

        #player is defined in the GamePlay module, so can add the player to the sprites here
        self.game.all_sprites_list.add(self.game.player) #add the player to the all_sprites list so its blitted onto the screen
        self.game.player_list.add(self.game.player)

        #defines the user events here
        #Alien Spaceship events
        SHARPMOVE = pygame.USEREVENT + 1
        STOP = pygame.USEREVENT + 2
        SHOOT = pygame.USEREVENT + 3
        SPAWNALIEN = pygame.USEREVENT + 4

        #player ship events
        RESPAWN = pygame.USEREVENT + 5
        HYPERDRIVE = pygame.USEREVENT + 6

        running = True #despite being in its own loop, need to still set a running = True otherwise lots of weird things break.

        while running == True:
            #I've found in most cases, it's best to define the keypresses here. There are some exceptions.
            #In particular, it's hard to pass in keyup/keydown to classes. Easier to do on the event listener. 

            for event in pygame.event.get():
                #standard exit options
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYUP:
                    if event.key == K_UP:
                        #when the thrust movement is lifted, reset the player image back to the standard ship
                        #only works with keyup, so must be in the event handler
                        self.game.player.surf_copy = self.game.player.image
                        #don't forget to rotate it to the player's current angle.
                        self.game.player.surf = pygame.transform.rotozoom(self.game.player.surf_copy, -self.game.player.angle, 1)

                if self.game.player.gameover == False:
                    #a 'gameover' player is set for the gameover screen where it can't be seen or moved
                    #as long as it isn't the game over player, the player can shoot and hyperspace jump
                    if event.type == KEYDOWN and event.key == K_SPACE:
                        #again, completes the action once on keydown so must be in event handler
                        """shooting the gun"""
                        gun = self.game.player.get_gun_vec() #calculates where the front of the ship is and its angle.
                        self.game.player.shoot(gun, self.game)
                    if event.type == KEYDOWN and event.key == K_LCTRL:
                        self.game.player.hyperdrive() #jumps randomly on the screen

                if self.game.player.gameover == True:
                    #if we are in the 'gameover' title screen, will move to the initial input screen with any keydown or press
                    if event.type == KEYDOWN:
                        running = False
                        self.state = 'gameover'
                    if event.type == MOUSEBUTTONDOWN:
                        running = False
                        self.state = 'gameover'

                if event.type == SPAWNALIEN and self.game.score > self.game.score_trigger:
                    #spawning new alienship on a timer and after player reaches a certain amount of points
                    alienship_spawn(self.game)

                if event.type == SHOOT:
                    #alien shoots on a timer
                    self.game.spaceship.shoot(self.game)

                if event.type == SHARPMOVE:
                    #trigger an angled movement up or down on a timer
                    self.game.spaceship.sharp_move(self.game.player.pos) 
                    pygame.time.set_timer(STOP, 500)
                    
                if event.type == STOP:
                    #stops the angled movement after a moment
                    self.game.spaceship.stop()

                if event.type == RESPAWN:
                    #adds a slight delay on player respawn
                    self.game.player = Player()
                    self.game.all_sprites_list.add(self.game.player)
                    self.game.player_list.add(self.game.player)
                    pygame.time.set_timer(RESPAWN, 0)

                if event.type == HYPERDRIVE:
                    #adds a small cooldown to using the hyperdrive
                    self.game.player.hdcooldown = False
                    pygame.time.set_timer(HYPERDRIVE, 0)

            for alien in self.game.alienships_list:
                #kills off alien after a couple of turns across the screen
                if alien.counter == 1:
                    alien.alien_death(self.game)

            initial_asteroid_spawn(self.game) #put this out of 'running' loop so it doesn't keep updating

            if running:

                #update all sprite movements
                pressed_keys = pygame.key.get_pressed()
                self.game.player.screen_wrap()
                self.game.bullets_list.update()
                self.game.player.update(pressed_keys) #some continuous movements (upward thrust, rotate) are in player update
                self.game.all_asteroids_list.update()
                self.game.alienships_list.update()
                self.game.enemy_bullets_list.update()
                self.game.animations_list.update()

                max_lives = 5
                #after a certain number of points, an extra life is given.
                if self.game.lives < max_lives:
                    self.game.additional_life()  

                #monitor for all collision types
                self.game.bullet_hit_asteroid()
                self.game.player_hit_asteroid()
                self.game.alien_hit_asteroid()
                self.game.alien_hit_player()
                self.game.player_hit_alien()

                #fill screen in black to cover previously bliped sprites
                self.screen.fill((0, 0, 0))
                
                for each in self.game.all_sprites_list: #drawing everything onto screen
                    self.screen.blit(each.surf, each.rect)

                #applying a gaussian blur to the score and blitting it in top corner
                score = str(self.game.score)
                img = set_image(score, 35)
                self.screen.blit(img, (0, 0))

                #image for player lives
                life_image = pygame.image.load(os.path.join(os.path.dirname(__file__), '..', 'Player', 'ship.png')).convert_alpha()
                x = 200 #distance from corner of screen
                for life in range(self.game.lives):
                    self.screen.blit(life_image, (x, 10))
                    x += 34 #distance between each image

                #what happens once player runs out of lives
                if self.game.lives == 0:
                    self.game.gameover()

                    #blit gameover image onto the screen with asteroids still in background (so not a new state yet)
                    go_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'GameOver.png')).convert_alpha()
                    go_surf = pygame.transform.scale(go_img, (self.game.screen_width+2, self.game.screen_height+2))

                    self.screen.blit(go_surf, (0, 0))                

            pygame.display.flip()
            clock.tick(60) #for some reason needed to set a FPS stabiliser clock here too. No idea why.

    def game_over(self):
        """the state after the main loop where you insert your score"""

        SPAWNALIEN = pygame.USEREVENT + 4
        SHARPMOVE = pygame.USEREVENT + 1
        STOP = pygame.USEREVENT + 2
        SHOOT = pygame.USEREVENT + 3

        user_text = ''
        input_rect = pygame.Rect(680, 650, 350, 250)
        running = True

        while running == True:

            for event in pygame.event.get():
            #standard exit options
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        #get text input from 0 to -1 i.e. end.
                        user_text = user_text[:-1]

                    #Unicode standard is used for string formation
                    #keep the length to only 3 initials
                    elif len(user_text) < 3:
                        user_text += event.unicode

                    if event.key == pygame.K_RETURN:
                        #once you hit enter, the score is submitted and state moves to show highscores
                        add_to_highscores(self.game.score, user_text)
                        running = False
                        self.state = 'highscores'

                #largely unnecessary, but if you accidentally move too fast out of gameover it doesn't always capture it.
                self.game.player.kill()
                self.game.player = Player()
                pygame.time.set_timer(SPAWNALIEN, 0)
                pygame.time.set_timer(SHARPMOVE, 0)
                pygame.time.set_timer(STOP, 0)
                pygame.time.set_timer(SHOOT, 0)

                #blit the insert score image (easier that gaussian blurring text)
                image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'insertscore.jpg')).convert()
                new_surf = pygame.transform.scale(image, (self.game.screen_width+2, self.game.screen_height+2))
                self.screen.blit(new_surf, (0, 0))

                #blit the typed text as its being typed
                img = set_image(user_text, 60)
                self.screen.blit(img, (input_rect.x, input_rect.y))
                
                pygame.display.flip()

    def high_scores(self):
        """where you view the highscores"""

        #get the dictionary and then slice to just display the first 10 items
        highscores = get_dict()
        displayed_scores = dict(itertools.islice(highscores.items(), 10))
        running = True

        while running == True:

            for event in pygame.event.get():
            #standard exit options
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                    if event.key == K_n:
                        running = False
                        self.state = 'setup' #returns to the start
                elif event.type == QUIT:
                    pygame.quit()

                #display the two images and blit onto the screen
                image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'highscores.jpg')).convert()
                new_surf = pygame.transform.scale(image, (self.game.screen_width+2, self.game.screen_height+2))
                self.screen.blit(new_surf, (0, 0))

                image2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'PressNtoStart.png')).convert_alpha()
                new_surf2 = pygame.transform.scale(image2, (self.game.screen_width+2, self.game.screen_height+2))
                self.screen.blit(new_surf2, (0, 0))

                counter = 0
                for item in displayed_scores:
                #run through the sliced dictionary and blit each item with a gaussian blur
                #as the design makes the blur shift if its too long, easier to blit initials and scores individually
                    counter += 1
                    item_surf = set_image(item, 60)
                    score_surf = set_image(str(highscores[item]), 60)
                    initial_pos = (570, 250)
                    self.screen.blit(item_surf, (initial_pos[0], initial_pos[1] + (50*counter)))
                    self.screen.blit(score_surf, (initial_pos[0] + 300, initial_pos[1] + (50*counter)))
                
                pygame.display.flip()

    def state_manager(self):
        """assigns the state and controls the game loop"""
        if self.state == 'setup':
            self.setup()
        if self.state == 'main':
            self.main()
        if self.state == 'gameover':
            self.game_over()
        if self.state == 'highscores':
            self.high_scores()