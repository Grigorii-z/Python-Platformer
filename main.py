
import pygame
from os import listdir
from os.path import isfile, join
#dinam download

pygame.init()

pygame.display.set_caption("V1 Platformer")



WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5  # speed player
time1= 0
real_time = 0
hight_score = 12
window = pygame.display.set_mode((WIDTH, HEIGHT)) #sozd okna


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))] #zagruz file iz konkret dir

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect) #ric tol primoug
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 128, size, size)
    surface.blit(image, (0,0),rect) #stiraem i ostav tolko
    return pygame.transform.scale2x(surface)



class Player(pygame.sprite.Sprite): #sprite dly udob v stalk

    GRAVITY = 1
    SPRITES  = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None #na samom dele
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.game_over =0
        self.score = 0



    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self,fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self): #smena anim ot sostoyn
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction #naprav
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) #speed of anim caj 3 cadra
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):

        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite) #otobraz vsex pix

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self,x ,y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)



class Apple(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x,y,width, height):
        super().__init__(x,y, width, height, "apple")
        self.apple = load_sprite_sheets("Items", "Fruits",width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Apple"
        self.off = 0

    def loop(self):
        sprites = self.apple[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Kiwi(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x,y,width, height):
        super().__init__(x,y, width, height, "kiwi")
        self.kiwi = load_sprite_sheets("Items", "Fruits", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Kiwi"
        self.off = 0

    def loop(self):
        sprites = self.kiwi[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Melon(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x,y,width, height):
        super().__init__(x,y, width, height, "melon")
        self.melon = load_sprite_sheets("Items", "Fruits", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Melon"
        self.off = 0

    def loop(self):
        sprites = self.melon[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):

        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fire_2(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"fire_2")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):

        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
class Fire_3(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"fire_3")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):

        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"


    def loop(self):

        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw_2(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"saw_2")
        self.saw_2 = load_sprite_sheets("Traps", "Saw", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"


    def loop(self):

        sprites = self.saw_2[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw_3(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"saw_3")
        self.saw_3 = load_sprite_sheets("Traps", "Saw", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"


    def loop(self):

        sprites = self.saw_3[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class FlagStart(Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width,height,"flagstart")
        self.flagstart = load_sprite_sheets("Items", "Checkpoints", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Flag1"
        self.off = 0


    def loop(self):

        sprites = self.flagstart[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect() # x and y
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height) # vverx lev
            tiles.append(pos)

    return tiles, image


def draw(window, background,bg_image, player, objects, offset_x,apple,flagstart,kiwi):


    for tile in background:
        window.blit(bg_image, tile)

    if apple.off == 0:
        for obj in objects:
            obj.draw(window, offset_x)
    else:
        player.score+=1
        objects.remove(apple)
        apple.off = 0
        for obj in objects:
            obj.draw(window, offset_x)


    if flagstart.off == -1:
        player.score+=1
        objects.remove(flagstart)
        flagstart.off = 0


    if kiwi.off == -1:
        player.score+=1
        objects.remove(kiwi)
        kiwi.off = 0

    game_over_font = pygame.font.Font('Sonic 1 Title Screen Filled.ttf', 40)
    game_over_font_2 = pygame.font.Font('Sonic 1 Title Screen Outline.ttf', 40)
    game_over_font_3 = pygame.font.Font('Sonic 1 Title Screen Outline.ttf', 20)



    if player.game_over == 0:

        player.draw(window, offset_x)
        global real_time
        global time1
        time1+=1

        if time1>100:
            real_time=time1//100
        tt = game_over_font.render(f'Time {real_time} ',True,0)
        window.blit(tt, (20, 20))
    else:

        tt = game_over_font.render(f'Time {real_time} ', True, 0)
        window.blit(tt, (20, 20))
        time1 = 0
        ds = game_over_font_2.render("Game Over",True,0)
        dss = game_over_font.render("Press X to continue", True, 255)
        window.blit(ds,(300,250))
        window.blit(dss, (180, 300))

    if player.score == 3:
        ds = game_over_font_2.render("Victory", True, 0)
        dss = game_over_font.render("Press Z to restart", True, 255)
        window.blit(ds, (300, 250))
        window.blit(dss, (180, 300))
        tt = game_over_font.render(f'Time {real_time} ', True, 0)
        window.blit(tt, (20, 20))
        time1 = 0

    ss = game_over_font_3.render(f'Best Time {hight_score} ', True, 0)
    window.blit(ss, (20, 80))

    pygame.display.update() #totech obnov

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top #niz k vverx
                player.landed()
            elif dy <0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player,objects,dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects,apple,melon,kiwi):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
       if (obj and obj.name == "fire") or (obj and obj.name == "fire_2") or (obj and obj.name == "fire_3") or (obj and obj.name == "saw") or (obj and obj.name == "saw_2") or (obj and obj.name == "saw_3"):
           player.make_hit()
           player.game_over = -1
       elif obj and obj.name =="apple":
           apple.off = -1
       elif obj and obj.name == "flagstart":
           melon.off = -1
       elif obj and obj.name == "kiwi":
           kiwi.off = -1

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Purple.png")
    global hight_score
    global real_time
    global time1
    block_size = 96

    player = Player(100,100,50,50)
    floor = [Block(i *  block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    fire = Fire(1250, HEIGHT - block_size * 5 - 64, 16, 32)
    fire.on()
    fire_2 = Fire_2(1890, HEIGHT - block_size*3 - 64, 16, 32)
    fire_2.on()
    fire_3 = Fire_2(1650, HEIGHT - block_size * 5 - 64, 16, 32)
    fire_3.on()
    apple = Apple(600, HEIGHT - block_size * 5 - 64, 32, 32)
    kiwi = Kiwi(1250, HEIGHT - block_size * 6 - 64, 32, 32)
    melon = Melon(-850, HEIGHT - block_size * 2 - 64, 32, 32)
    saw = Saw(700,HEIGHT - block_size - 64, 128, 64)
    saw_2 = Saw_2(458,HEIGHT - block_size - 64, 128, 64)
    saw_3 = Saw_3(200, HEIGHT - block_size - 64, 128, 64)

    flagstart = FlagStart (2100, HEIGHT - block_size * 5 - 32, 64, 96)


    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(0, HEIGHT - block_size * 3, block_size),
               Block(0, HEIGHT - block_size * 4, block_size), Block(0, HEIGHT - block_size * 5, block_size),
               Block(0, HEIGHT - block_size * 6, block_size), Block(0, HEIGHT - block_size * 7, block_size), Block(block_size * 1, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 3, block_size), Block(block_size * 6, HEIGHT - block_size * 5, block_size),
               Block(block_size * 10, HEIGHT - block_size * 5, block_size), Block(block_size * 10, HEIGHT - block_size * 4, block_size),
               Block(block_size * 10, HEIGHT - block_size * 3, block_size), Block(block_size * 10, HEIGHT - block_size * 2, block_size),
               Block(block_size * 11, HEIGHT - block_size * 5, block_size), Block(block_size * 12, HEIGHT - block_size * 5, block_size),
               Block(block_size * 13, HEIGHT - block_size * 5, block_size), Block(block_size * 14, HEIGHT - block_size * 5, block_size),
               Block(block_size * 15, HEIGHT - block_size * 5, block_size), Block(block_size * 16, HEIGHT - block_size * 5, block_size),
               Block(block_size * 17, HEIGHT - block_size * 5, block_size), Block(block_size * 10, HEIGHT - block_size * 8, block_size), Block(block_size * 10, HEIGHT - block_size * 8, block_size),
               Block(block_size * 11, HEIGHT - block_size * 8, block_size), Block(block_size * 12, HEIGHT - block_size * 8, block_size),
               Block(block_size * 13, HEIGHT - block_size * 8, block_size), Block(block_size * 14, HEIGHT - block_size * 8, block_size),
               Block(block_size * 15, HEIGHT - block_size * 8, block_size), Block(block_size * 16, HEIGHT - block_size * 8, block_size),
               Block(block_size * 17, HEIGHT - block_size * 8, block_size), Block(block_size * 17, HEIGHT - block_size * 4, block_size),
               Block(block_size * 17, HEIGHT - block_size * 3, block_size), Block(block_size * 17, HEIGHT - block_size * 2, block_size),
               Block(block_size * 16, HEIGHT - block_size * 4, block_size), Block(block_size * 16, HEIGHT - block_size * 3, block_size),
               Block(block_size * 16, HEIGHT - block_size * 2, block_size), Block(block_size * 15, HEIGHT - block_size * 4, block_size),
               Block(block_size * 15, HEIGHT - block_size * 3, block_size), Block(block_size * 15, HEIGHT - block_size * 2, block_size),
               Block(block_size * 14, HEIGHT - block_size * 4, block_size), Block(block_size * 14, HEIGHT - block_size * 3, block_size),
               Block(block_size * 14, HEIGHT - block_size * 2, block_size), Block(block_size * 13, HEIGHT - block_size * 4, block_size),
               Block(block_size * 13, HEIGHT - block_size * 3, block_size), Block(block_size * 13, HEIGHT - block_size * 2, block_size),
               Block(block_size * 12, HEIGHT - block_size * 4, block_size), Block(block_size * 12, HEIGHT - block_size * 3, block_size),
               Block(block_size * 12, HEIGHT - block_size * 2, block_size), Block(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block(block_size * 11, HEIGHT - block_size * 3, block_size), Block(block_size * 11, HEIGHT - block_size * 2, block_size),
               Block(block_size * 18, HEIGHT - block_size * 4, block_size), Block(block_size * 18, HEIGHT - block_size * 3, block_size),
               Block(block_size * 18, HEIGHT - block_size * 2, block_size), Block(block_size * 19, HEIGHT - block_size * 3, block_size),
               Block(block_size * 19, HEIGHT - block_size * 2, block_size), Block(block_size * 20, HEIGHT - block_size * 3, block_size),
               Block(block_size * 21, HEIGHT - block_size * 4, block_size), Block(block_size * 22, HEIGHT - block_size * 4, block_size),
               Block(block_size * 23, HEIGHT - block_size * 4, block_size),
               saw,saw_2,saw_3,fire,fire_2,fire_3,apple,flagstart,kiwi]

    offset_x = 0
    scroll_area_width = 200
    run = True
    while run:
        clock.tick(FPS) #cicle vipoln 60 za 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_x and player.game_over == -1:
                    player.game_over = 0
                    player = Player(100, 100, 50, 50)
                    offset_x = 0
                    apple.off = 0
                    if apple in objects:
                        pass
                    else:
                        objects.append(apple)
                    flagstart.off = 0
                    if flagstart in objects:
                        pass
                    else:
                        objects.append(flagstart)
                    kiwi.off = 0
                    if kiwi in objects:
                        pass
                    else:
                        objects.append(kiwi)
                if event.key == pygame.K_z and player.score == 3:
                    player.score = 0
                    player = Player(100, 100, 50, 50)
                    offset_x = 0
                    apple.off = 0
                    objects.append(apple)
                    flagstart.off = 0
                    objects.append(flagstart)
                    kiwi.off = 0
                    objects.append(kiwi)
                    if real_time < hight_score:
                        hight_score = real_time
                        time1 = 0






        player.loop(FPS)
        flagstart.loop()
        saw_3.loop()
        saw_2.loop()
        saw.loop()
        fire.loop()
        fire_2.loop()
        fire_3.loop()
        apple.loop()
        kiwi.loop()
        melon.loop()

        handle_move(player, objects,apple,flagstart,kiwi)

        draw(window, background , bg_image,player, objects, offset_x,apple,flagstart,kiwi)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel >0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    pygame.quit()
    quit()


if __name__ == "__main__":  # zapuskaet corectno
    main(window)
