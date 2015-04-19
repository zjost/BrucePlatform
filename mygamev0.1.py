import pygame
import sys
from pygame.locals import *
from random import randint

class Player(pygame.sprite.Sprite):
    '''The class that holds the main player, and controls how they jump. nb. The player doens't move left or right, the world moves around them'''
    def __init__(self, start_x, start_y, width, height):

        pygame.sprite.Sprite.__init__(self)
        
        # Define list of images
        self.images = []
        self.images.append(pygame.transform.scale(
            pygame.image.load(player_image), (width, height)))
        self.images.append(pygame.transform.scale(
            pygame.image.load(player_image2), (width, height)))
        # Create an index for the images
        self.index = 0
        # Initialize to first image
        self.image = self.images[self.index]
        
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.speed_y = 0
        self.base = pygame.Rect(start_x, start_y + height, width, 2)

        self.sound = pygame.mixer.Sound(jump_sound)
        self.sound.set_volume(0.2)

        self.dogsound = pygame.mixer.Sound(dog_sound)
        self.dogsound.set_volume(1.0)
    
        

    def move_y(self):
        '''this calculates the y-axis movement for the player in the 
        current speed'''
        collided_y = world.collided_get_y(self.base)
        # If upward velocity or not colliding, treat as free
        if self.speed_y <= 0 or collided_y < 0:
            # Move according to speed
            self.rect.y = self.rect.y + self.speed_y
            # Accelerate speed downward
            self.speed_y = self.speed_y + gravity
        # If colliding and not moving upward
        if collided_y >0 and self.speed_y > 0:
            # y position is at the top of the block
            self.rect.bottom = collided_y
            
        self.base.y = self.rect.y+self.rect.height
        

    def jump(self, speed):
        '''This sets the player to jump, but it only can if its feet are on the floor'''
        if world.collided_get_y(self.base)>0:
            self.speed_y = speed
            self.index = 1
            self.image = self.images[self.index]
            self.sound.play()

    def update(self):
        ''' This changes the image back to standard if touching ground '''
        if world.collided_get_y(self.base)>0 and self.index >0 :
            self.index = 0
            self.image = self.images[self.index]

    def animate(self, ind):
        self.image = self.images[ind]
            

class World():
    '''This will hold the platforms and the goal. 
    nb. In this game, the world moves left and right rather than the player'''
    def __init__(self, level, block_size, color_platform, color_goals):
        self.platforms = []
        self.goals = []
        self.posn_y = 0
        self.color = color_platform
        self.color_goals = color_goals
        self.block_size = block_size
        self.sound = pygame.mixer.Sound(level_sound)
        self.sound.play()

        for line in level:
            self.posn_x = 0
            for block in line:
                if block == '-':
                    self.platforms.append(pygame.Rect(
                        self.posn_x, self.posn_y,
                        block_size, block_size))
                if block == 'G':
                    self.goals.append(Goals(self.posn_x, self.posn_y))
                    
                self.posn_x = self.posn_x + block_size
            self.posn_y = self.posn_y + block_size

        

    def move(self, dist):
        '''move the world dist pixels right (a negative dist means left)'''
        for block in self.platforms:
            block.move_ip(dist, 0)

        for block in self.goals:
            block.move_x(dist)

    def collided_get_y(self, player_rect):
        '''get the y value of the platform the player is currently on'''
        return_y = -1
        for block in self.platforms:
            if block.colliderect(player_rect):
                return_y = block.y + 1
        return return_y

    def at_goal(self, player_rect):
        '''return True if the player is currently in contact with the goal. False otherwise'''
        for block in self.goals:
            if block.rect.colliderect(player_rect):
                return True
        return False

    def update(self, screen):
        '''draw all the rectangles onto the screen'''
        for block in self.platforms:
            pygame.draw.rect(screen, self.color, block, 0)
        for block in self.goals:
            self.ball_plain = pygame.sprite.RenderPlain(self.goals)
            self.ball_plain.draw(screen)
            #pygame.draw.rect(screen, self.color_goals, block, 0)


class Doom():
    '''this class holds all the things that can kill the player'''
    def __init__(self, fireball_num, pit_depth, color):
        self.base = pygame.Rect(0, screen_y - pit_depth,
                    screen_x, pit_depth)
        self.color = color
        self.fireballs = []
        for i in range(0, fireball_num):
            self.fireballs.append(Fireball())
        self.fireball_plain = pygame.sprite.RenderPlain(self.fireballs)

        self.sound = pygame.mixer.Sound(explo_sound)
        self.sound.set_volume(0.5)

    def move(self, dist):
        '''move everything right dist pixels (negative dist means left)'''
        for fireball in self.fireballs:
            fireball.move_x(dist)

    def update(self, screen):
        '''move fireballs down, and draw everything on the screen'''
        for fireball in self.fireballs:
            fireball.move_y()
        self.fireball_plain.draw(screen)
        pygame.draw.rect(screen, self.color, self.base, 0)
        

    def collided(self, player_rect):
        '''check if the player is currently in contact with any of the doom.
        nb. shrink the rectangle for the fireballs to make it fairer'''
        for fireball in self.fireballs:
            if fireball.rect.colliderect(player_rect):
                hit_box = fireball.rect.inflate(
                    -int(fireball_size/2),
                    -int(fireball_size/2))
                if hit_box.colliderect(player_rect):
                    return True
        return self.base.colliderect(player_rect)

class Fireball(pygame.sprite.Sprite):
    '''this class holds the fireballs that fall from the sky'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            pygame.image.load(fireball_image),
            (fireball_size, fireball_size))
        self.rect = self.image.get_rect()
        self.reset()
        


    def reset(self):
        '''re-generate the fireball a random distance along the screen and give them a random speed'''
        self.y = 0
        self.speed_y = randint(fireball_low_speed, fireball_high_speed)
        self.x = randint(0, screen_x)
        self.rect.topleft = self.x, self.y
        

    def move_x(self, dist):
        '''move the fireballs dist pixels to the right 
        (negative dist means left)'''
        self.rect.move_ip(dist, 0)
        if self.rect.x < -50 or self.rect.x > screen_x:
            self.reset()

    def move_y(self):
        '''move the fireball the appropriate distance down the screen
        nb. fireballs don't accellerate with gravity, but have a random speed. if the fireball has reached the bottom of the screen, 
        regenerate it'''
        self.rect.move_ip(0, self.speed_y)
        if self.rect.y > screen_y:
            self.reset()

    def update(self, screen, colour):
        '''draw the fireball onto the screen'''
        pass

class Goals(pygame.sprite.Sprite):
    '''this class holds the fireballs that fall from the sky'''
    def __init__(self, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            pygame.image.load(ball_image),
            (ball_size, ball_size))
        self.rect = self.image.get_rect()
        self.rect.topleft = xpos, ypos
     

    def move_x(self, dist):
        '''move the fireballs dist pixels to the right 
        (negative dist means left)'''
        self.rect.move_ip(dist, 0)


    def update(self, screen, colour):
        '''draw the fireball onto the screen'''
        pass

    
# options
mult = 2
screen_x = 600*mult
screen_y = 400*mult
game_name = "Awesome Raspberrylock size 30, posn_x 7050 posn_y 0"
player_spawn_x = 50
player_spawn_y = 200
player_image = "bruceside.png"
player_image2 = "bruce_turn_small.png"

player_width, player_height = int(30*mult), int(28*mult)
#player_width, player_height = 30*2, 28*2



ball_size = 15*mult
ball_image = "dryer_ball.png"


gravity = 0.8*mult
jump_speed = -10*mult

level=[
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "                    ",
    "          -       G ",
    "     - --   ---  -  ",
    " -- -          --   "]
   #"--------------------"

platform_color = (100, 100, 100)
block_size = int(30*mult)
goal_color = (0, 0, 255)
doom_color = (255, 0, 0)
fireball_size = int(20*mult)
fireball_number = 10
fireball_low_speed = 3
fireball_high_speed = 7
fireball_image = "flame.png"


# Sounds
jump_sound = "qubodup-cfork-ccby3-jump.ogg"
level_sound = "ambientmain_0_0.ogg"
explo_sound = "explosion1.ogg"
dog_sound = "dog_sound_1.ogg"

# initialise pygame.mixer
pygame.mixer.pre_init(44100, -16, 8, 2048)
pygame.mixer.init()

# initialise pygame
pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption(game_name)
screen = pygame.display.get_surface()

# load level
if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        level = f.readlines()
        
# initialise variables
clock = pygame.time.Clock()
finished = False
player = Player(player_spawn_x, player_spawn_y, player_width, player_height)
player_plain = pygame.sprite.RenderPlain(player)
world = World(level, block_size, platform_color, goal_color)
doom = Doom(fireball_number, 10, doom_color)



# setup the background
background_image = "Catacomb_Entrance_Hall_by_KingCloud_crop.png"
#background_image = "Catacomb_Entrance_Hall_by_KingCloud.jpg"
#background_image = "ex_background.png"
background = pygame.transform.scale(pygame.image.load(background_image),
                                    (screen_x, screen_y)).convert()


bg_1_x = 0
bg_2_x = screen_x

while not finished:
    # blank screen
    screen.fill((0,0,0))
    # check events
    for event in pygame.event.get():
        if event.type == QUIT:
            finished = True
            
    

    # check which keys are held
    key_state = pygame.key.get_pressed()
    if key_state[K_LEFT]:
        world.move(2*mult)
        doom.move(2*mult)
        # move background at slower pace
        bg_1_x = bg_1_x + 1
        bg_2_x = bg_2_x + 1
        # if going into negative space, bring screen 2 to -screen_x + amount negative
        if bg_1_x > 0:
            bg_2_x = -screen_x+bg_1_x

    elif key_state[K_RIGHT]:
        world.move(-2*mult)
        doom.move(-2*mult)
        # move background at slower pace
        bg_1_x = bg_1_x - 1
        bg_2_x = bg_2_x - 1

        # if have moved to edge, put screen 1 in front
        if bg_2_x < 0:
            bg_1_x = screen_x+bg_2_x
        # if going from negative to positive space, bring screen 2 back in front minus movement amount
        if bg_1_x < 0:
            bg_2_x = screen_x+bg_1_x

    if key_state[K_SPACE]:
        player.jump(jump_speed)
            
    # move the player with gravity
    player.move_y()
    # Update the image based on whether jumping or not
    player.update()
    # render the frame
    screen.blit(background, (bg_1_x,0))
    screen.blit(background, (bg_2_x,0))
    player_plain.draw(screen)
    world.update(screen)
    doom.update(screen)

    # update the display
    pygame.display.update()
    # check if the player is dead
    if doom.collided(player.rect):
        doom.sound.play()
        pygame.time.wait(1500)
        print("You Lose!")
        finished = True     
    # check if the player has completed the level
    if world.at_goal(player.rect):
        player.animate(1)
        player_plain.draw(screen)
        pygame.display.update()
        player.dogsound.play()
        pygame.time.wait(1000)
        print("Winner!")
        finished = True
    # set the speed in fps
    clock.tick(20)

pygame.quit()
