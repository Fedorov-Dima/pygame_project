import pygame
import os
import sys
import random

#Карта
map_file = 'education_level.map'

#Функция загрузки спрайтов
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image

#
pygame.init()
screen_size = (1080, 720)
screen = pygame.display.set_mode(screen_size)
wight = screen.get_size()[0]
height = screen.get_size()[1]
FPS = 50

tile_images = {
    'wall': pygame.transform.scale(load_image('box.png'), (100, 100)),
    'empty': pygame.transform.scale(load_image('grass.png'), (100, 100)),
    'ivent': pygame.transform.scale(load_image('ivent.png'), (50, 100)),
    'hint': pygame.transform.scale(load_image('hint.png'), (50, 100))}  #Названия некоторых спрайтов

player_image = pygame.transform.scale(load_image('hero_down_1.png'), (58, 90))  #Спрайт персонажа по умолчанию

tile_width = tile_height = 100

#Списки со спрайтами персонажа, нужны для анимации передвижения
walk_down = [pygame.transform.scale(load_image('hero_down_1.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_down_2.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_down_1.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_down_3.png'), (58, 90))]

walk_up = [pygame.transform.scale(load_image('hero_up_1.png'), (58, 90)),
           pygame.transform.scale(load_image('hero_up_2.png'), (58, 90)),
           pygame.transform.scale(load_image('hero_up_1.png'), (58, 90)),
           pygame.transform.scale(load_image('hero_up_3.png'), (58, 90))]

walk_left = [pygame.transform.scale(load_image('hero_left_1.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_left_2.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_left_1.png'), (58, 90)),
             pygame.transform.scale(load_image('hero_left_3.png'), (58, 90))]

walk_right = [pygame.transform.scale(load_image('hero_right_1.png'), (58, 90)),
              pygame.transform.scale(load_image('hero_right_2.png'), (58, 90)),
              pygame.transform.scale(load_image('hero_right_1.png'), (58, 90)),
              pygame.transform.scale(load_image('hero_right_3.png'), (58, 90))]

hero_anim_count = 0  #Индекс текущего спрайта в списке


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


# установка неподвижных объектов, через которые можно ходить (трава)
class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Gras(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# установка неподвижных объектов, через которые нельзя ходить (стены)
class Wall(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

class Ivent(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(ivent_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 20, tile_height * pos_y)

# класс персонажа
class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, wall_group):
            self.rect = self.rect.move(-x, -y)

# Клас камеры
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - wight // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


player = None
running = True
clock = pygame.time.Clock()

sprite_group = SpriteGroup()  # группа спрайтов травы
wall_group = SpriteGroup()  # группа спрайтов стен
hero_group = SpriteGroup()  # группа спрайта игрока
ivent_group = SpriteGroup()
all_sprites = SpriteGroup()  # группа всех спрайтов


# "аварийное завершение" программы в виде отдельной функции
def terminate():
    pygame.quit()
    sys.exit()


# стартовый экран
def start_screen():
    intro_text = ["Перемещение героя", "",
                  "Герой двигается"]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)

def questionsGeneration():
    global question
    arithmetics = {
        " + ": lambda x, y: x + y,
        " - ": lambda x, y: x - y,
        " * ": lambda x, y: x * y,
        " / ": lambda x, y: x / y,
    }
    number_1 = random.choice(range(1, 11))
    number_2 = random.choice(range(1, 11))
    action = random.choice(list(arithmetics.keys()))
    answer = arithmetics[action](number_1, number_2)
    if int(answer) == answer:
        question = str(number_1) + str(action) + str(number_2)
    else:
        questionsGeneration()
    return question, int(answer)

# загрузка уровня
def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))
    except FileNotFoundError:
        print("Не удалось загрузить файл:", filename)
        pygame.quit()
        return None

# генерация уровня
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            Gras('empty', x, y)
            if level[y][x] == '.':
                Gras('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '!':
                Ivent('ivent', x, y)
            elif level[y][x] == '?':
                Ivent('hint', x, y)
    return new_player, x, y

# когда персонаж останавливается, его спрайт переходит в стоячее положение
def check_image_hero(hero):
    if hero.image in walk_down:
        hero.image = walk_down[0]
    elif hero.image in walk_up:
        hero.image = walk_up[0]
    elif hero.image in walk_left:
        hero.image = walk_left[0]
    elif hero.image in walk_right:
        hero.image = walk_right[0]

# обработка перемещения героя
def move(hero, movement):
    clock.tick(15)

    global hero_anim_count  #Индекс текущего спрайта в списке, его изменение
    if hero_anim_count == 3:
        hero_anim_count = 0
    else:
        hero_anim_count += 1

    if movement == "up":
        hero.image = walk_up[hero_anim_count]  # смена спрайта
        hero.move(0, -5)
    elif movement == "down":
        hero.image = walk_down[hero_anim_count]  # смена спрайта
        hero.move(0, 5)
    elif movement == "left":
        hero.image = walk_left[hero_anim_count]  # смена спрайта
        hero.move(-5, 0)
    elif movement == "right":
        hero.image = walk_right[hero_anim_count]  # смена спрайта
        hero.move(5, 0)

# стандартный запуск
start_screen()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera = Camera()

all_sprites.add(hero_group)
all_sprites.add(sprite_group)
all_sprites.add(wall_group)
all_sprites.add(ivent_group)

up, down, left, right = False, False, False, False  # флаги перемещения
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # проверка зажатия кнопки, изменение флагов перемещения
            if event.key == pygame.K_UP:
                up = True
            elif event.key == pygame.K_DOWN:
                down = True
            elif event.key == pygame.K_LEFT:
                left = True
            elif event.key == pygame.K_RIGHT:
                right = True
        elif event.type == pygame.KEYUP:  # проверка зажатия кнопки, изменение флагов перемещения
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                up, down, left, right = False, False, False, False
                check_image_hero(hero)  # спрайт персонажа должен остановиться

    # вызов функции передвижения персонажа
    if up:
        move(hero, "up")
    elif down:
        move(hero, "down")
    elif left:
        move(hero, "left")
    elif right:
        move(hero, "right")

    # камера
    camera.update(hero)
    for sprite in all_sprites:
        camera.apply(sprite)

    # стандартные команды
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    wall_group.draw(screen)
    hero_group.draw(screen)
    ivent_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()