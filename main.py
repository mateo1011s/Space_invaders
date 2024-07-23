import pygame
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#define fps
clock = pygame.time.Clock()
fps = 120

screen_width = 600
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

#load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

#define game variables
rows = 5
cols = 5
alien_cooldown = 1000  # bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0  # 0 is no game over, 1 means player has won, -1 means player has lost
score = 0  # variable to store the score
high_scores = []

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(bg, (0, 0))

#define function for creating text
def draw_text(text, font, text_col, center_x, center_y):
    img = font.render(text, True, text_col)
    img_rect = img.get_rect(center=(center_x, center_y))
    screen.blit(img, img_rect)

#create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        #set movement speed
        speed = 8
        #set a cooldown variable
        cooldown = 500  # milliseconds
        global game_over

        #get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        #record current time
        time_now = pygame.time.get_ticks()
        #shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1

#create Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            global score
            score += 5  # Increment score

#create Aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

#create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            #reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

#create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png").convert_alpha()
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            #add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)

def display_start_screen():
    enter_name = True
    player_name = ""

    while enter_name:
        draw_bg()
        # Centered title
        draw_text('SPACE INVADERS', font40, white, screen_width // 2, screen_height // 2 - 100)
        draw_text('Enter Your Name:', font30, white, screen_width // 2, screen_height // 2 - 30)
        
        # Draw the input box
        input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 20, 200, 40)
        pygame.draw.rect(screen, white, input_box)
        pygame.draw.rect(screen, black, input_box, 2)

        # Draw the name text centered in the input box
        input_text_surf = font30.render(player_name, True, black)
        input_text_rect = input_text_surf.get_rect(center=input_box.center)
        screen.blit(input_text_surf, input_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    enter_name = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

        pygame.display.update()

    return player_name

create_aliens()

run = True
start_game = False
player_name = display_start_screen()

spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

while run:
    clock.tick(fps)

    if start_game:
        #draw background
        draw_bg()

        if countdown == 0:
            #create random alien bullets
            time_now = pygame.time.get_ticks()
            if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                attacking_alien = random.choice(alien_group.sprites())
                alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                alien_bullet_group.add(alien_bullet)
                last_alien_shot = time_now

            if len(alien_group) == 0:
                game_over = 1

            if game_over == 0:
                spaceship_group.update()
                bullet_group.update()
                alien_group.update()
                alien_bullet_group.update()
            else:
                if game_over == -1:
                    draw_text('GAME OVER!', font40, white, screen_width // 2, screen_height // 2 - 50)
                    high_scores.append((player_name, score))
                    start_game = False
                if game_over == 1:
                    draw_text('YOU WIN!', font40, white, screen_width // 2, screen_height // 2 - 50)
                    high_scores.append((player_name, score))
                    start_game = False

        if countdown > 0:
            draw_text('GET READY!', font40, white, screen_width // 2, screen_height // 2 - 50)
            draw_text(str(countdown), font40, white, screen_width // 2, screen_height // 2 + 50)
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer

        explosion_group.update()

        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        explosion_group.draw(screen)

        # Adjusted the position of the score display
        draw_text('Score: ' + str(score), font30, white, screen_width // 2, 20)  # Centered horizontally at the top

    else:
        draw_bg()
        draw_text('Press ENTER to Start', font40, white, screen_width // 2, screen_height // 2 - 50)
        draw_text('High Scores:', font30, white, screen_width // 2, screen_height // 2 + 10)
        for i, (name, score) in enumerate(sorted(high_scores, key=lambda x: x[1], reverse=True)[:5]):
            draw_text(f'{i+1}. {name}: {score}', font30, white, screen_width // 2, screen_height // 2 + 50 + i * 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not start_game:
                    start_game = True
                    player_name = display_start_screen()
                    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
                    spaceship_group.empty()
                    spaceship_group.add(spaceship)
                    bullet_group.empty()
                    alien_group.empty()
                    alien_bullet_group.empty()
                    explosion_group.empty()
                    create_aliens()
                    score = 0
                    countdown = 3
                    last_count = pygame.time.get_ticks()
                    game_over = 0

    pygame.display.update()

pygame.quit()