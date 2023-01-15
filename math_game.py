import pygame
import os
import sys
import random

# Карта
map_file = 'education_level.map'
level_list = ['level_1.map', 'level_2.map', 0]


pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

load = pygame.mixer.Sound('data/background music.mp3')
game = pygame.mixer.Sound('data/fon_sound.mp3')
go = pygame.mixer.Sound('data/grass_step.mp3')
ivent = pygame.mixer.Sound('data/zvuk_but.mp3')
math_event = pygame.mixer.Sound('data/end_event_sound.mp3')
new_level_sound = pygame.mixer.Sound('data/new_level_sound.mp3')


# Функция загрузки спрайтов
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


def update_result(result):
    pressed_key = pygame.key.get_pressed()
    if pressed_key[pygame.K_1]:
        result += '1'
    elif pressed_key[pygame.K_2]:
        result += '2'
    elif pressed_key[pygame.K_3]:
        result += '3'
    elif pressed_key[pygame.K_4]:
        result += '4'
    elif pressed_key[pygame.K_5]:
        result += '5'
    elif pressed_key[pygame.K_6]:
        result += '6'
    elif pressed_key[pygame.K_7]:
        result += '7'
    elif pressed_key[pygame.K_8]:
        result += '8'
    elif pressed_key[pygame.K_9]:
        result += '9'
    elif pressed_key[pygame.K_0]:
        result += '0'
    elif pressed_key[pygame.K_MINUS]:
        result += '-'
    elif pressed_key[pygame.K_BACKSPACE]:
        result = result[:-1]
    clock.tick(10)
    return result


#
pygame.init()
screen_size = (1080, 720)
screen = pygame.display.set_mode(screen_size)
wight = screen.get_size()[0]
height = screen.get_size()[1]
FPS = 50

tile_images = {
    'wall': pygame.transform.scale(load_image('tree.png'), (95, 95)),
    'empty': pygame.transform.scale(load_image('grass.png'), (100, 100)),
    'ivent': pygame.transform.scale(load_image('ivent.png'), (50, 100)),
    'hint': pygame.transform.scale(load_image('hint.png'), (50, 100)),
    'door': pygame.transform.scale(load_image('close_door.png'), (75, 100)),
    'end_level': pygame.transform.scale(load_image('close_door_end.png'), (75, 100)),
    'end_game': pygame.transform.scale(load_image('close_door_end.png'), (75, 100))}  # Названия некоторых спрайтов

player_image = pygame.transform.scale(load_image('hero_down_1.png'), (58, 90))  # Спрайт персонажа по умолчанию

tile_width = tile_height = 100

# Списки со спрайтами персонажа, нужны для анимации передвижения
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

hero_anim_count = 0  # Индекс текущего спрайта в списке

max_ivent = 0
total_ivent = 0


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None


# установка неподвижных объектов, через которые можно ходить (трава)
class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_y, pos_x


# Трава
class Gras(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_y, pos_x


# установка неподвижных объектов, через которые нельзя ходить (стены)
class Wall(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_y, pos_x


# Класс ивентов (примеров)
class Ivent(Sprite):
    def __init__(self, tile_type, pos_x, pos_y, pos_door=None, question=None, answer=None):
        super().__init__(ivent_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 28, tile_height * pos_y)
        self.pos = pos_y, pos_x
        self.pos_door = pos_door
        self.question = question
        self.answer = answer
        self.flag = False
        self.result = ''
        self.message = False

    def update(self):
        if pygame.sprite.spritecollideany(self, hero_group):
            pressed_key = pygame.key.get_pressed()
            if not self.flag:
                drawing_text("Нажмите 'E'", (255, 255, 255))
            if pressed_key[pygame.K_e]:
                self.flag = True

            if self.flag:
                self.result = update_result(self.result)

                font_question = pygame.font.Font(None, 50)
                text_question = font_question.render(f"{self.question} = {self.result}", True, (0, 0, 0))
                text_x_question = screen.get_size()[0] // 2 - text_question.get_width() // 2
                text_y_question = 220
                text_question.get_width()
                text_question.get_height()
                pygame.draw.rect(screen, 'white',
                                 (screen.get_size()[0] // 2 - text_question.get_width() // 2 - 20,
                                  text_y_question - 20,
                                  text_question.get_width() + 40,
                                  text_question.get_height() + 40))
                screen.blit(text_question, (text_x_question, text_y_question))

            if pressed_key[pygame.K_RETURN]:
                if self.result != '' and self.result != '-' and int(self.result) == int(self.answer):
                    self.flag = False
                    math_event.play()
                    for el in door_group:
                        if el.pos == self.pos_door:
                            el.open = True
                            el.image = pygame.transform.scale(load_image('open_door.png'), (75, 100))
                    check_ivent()
                    self.kill()
                else:
                    self.message = True
            if self.message and self.flag:
                drawing_text("Неверно", (255, 0, 0))

        else:
            self.message = False
            self.flag = False


# Класс дверей на уровне
class Door_ivent(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(door_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y)
        self.open = False
        self.pos = pos_y, pos_x


# Класс дверей конца уровня
class Door_end(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(door_group)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y)
        self.open = False
        self.pos = pos_y, pos_x
        if tile_type == 'end_game':
            self.end_game = True
        else:
            self.end_game = False

    def update(self):
        if pygame.sprite.spritecollideany(self, hero_group):
            self.image = pygame.transform.scale(load_image('open_door_end.png'), (75, 100))
            pressed_key = pygame.key.get_pressed()
            drawing_text("Нажмите 'E'", (255, 255, 255))
            if pressed_key[pygame.K_e] and self.open and not self.end_game:
                new_level()
            elif pressed_key[pygame.K_e] and self.open and self.end_game:
                end_game()
        else:
            self.image = pygame.transform.scale(load_image('close_door_end.png'), (75, 100))


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
        if pygame.sprite.spritecollideany(self, door_group):
            for i in door_group:
                if pygame.sprite.collide_mask(self, i) and not i.open:
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
door_and_ivent = {}

# Группы спрайтов
sprite_group = SpriteGroup()
wall_group = SpriteGroup()
hero_group = SpriteGroup()
ivent_group = SpriteGroup()
door_group = SpriteGroup()
all_sprites = SpriteGroup()
list_group = [sprite_group, wall_group, hero_group, ivent_group, door_group, all_sprites]


# Отрисовка текста
def drawing_text(text, color):
    font = pygame.font.Font(None, 50)
    text = font.render(text, True, color)
    text_x = screen.get_size()[0] // 2 - text.get_width() // 2
    text_y = screen.get_size()[1] // 2 - text.get_height() // 2 + screen.get_size()[1] // 4
    text.get_width()
    text.get_height()
    screen.blit(text, (text_x, text_y))


# Загрузка нового уровня
def new_level():
    global level_map, hero, max_x, max_y, camera
    new_level_sound.play(0)
    for i in range(len(list_group)):
        for el in list_group[i]:
            el.kill()
    level_map = load_level(level_list[level_list[-1]])
    hero, max_x, max_y = generate_level(level_map)
    camera = Camera()
    for i in range(len(list_group) - 1):
        list_group[-1].add(list_group[i])
    counts_ivent_list[1] = 0
    counts_ivent_list[0] = len(ivent_group)
    level_list[-1] += 1


# Конец игры
def end_game():
    font = pygame.font.Font(None, 50)
    end_text_fon = ['Никитин Данииил', 'Фёдоров Дмитрий', 'Кутищев Максим', 'для вас старались:',  'Спаисибо за игру']

    running = True
    fon = pygame.transform.scale(load_image('fone_picture.jpg'), screen_size)
    x_pos = 400
    v = 20  # пикселей в секунду
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(fon, (0, 0))

        n_pos = 0
        for i in end_text_fon:
            string_rendered = font.render(i, True, pygame.Color('green'))
            intro_rect = string_rendered.get_rect()
            intro_rect.top = int(x_pos) - n_pos
            intro_rect.x = 300
            screen.blit(string_rendered, intro_rect)
            n_pos += 50

        x_pos -= v * clock.tick() / 1000
        pygame.display.flip()
    pygame.quit()
    sys.exit()


# "аварийное завершение" программы в виде отдельной функции
def terminate():
    pygame.quit()
    sys.exit()


# стартовый экран
def start_screen():
    w = screen.get_width()
    h = screen.get_height()
    load.play(-1)

    fon = pygame.transform.scale(load_image('fone_picture.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    pygame.draw.rect(screen, (160, 160, 160), (w // 2 - 75,
                                               h // 2 - 25, 150, 50), 0)
    pygame.draw.rect(screen, (190, 190, 190), (w // 2 - 65,
                                               h // 2 - 15, 130, 30), 0)
    font_name_game = pygame.font.Font(None, 100)
    text_name_game = font_name_game.render(f"Математическая игра", True, (0, 0, 0))
    text_x_name_game = w // 2 - text_name_game.get_width() // 2
    screen.blit(text_name_game, (text_x_name_game, 100))

    text = font.render(f"Начать игру", True, (0, 0, 0))
    text_x = w // 2 - text.get_width() // 2
    text_y = h // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                a = event.pos
                if a[0] >= w // 2 - 75 and a[0] <= w // 2 + 75 and a[1] >= h // 2 - 25 and \
                        a[1] <= h // 2 + 25:
                    ivent.play(1)
                    return
        pygame.display.flip()
        clock.tick(FPS)


# Генерация математических выражений
def questionsGeneration(n):
    arithmetics = {
        " + ": lambda x, y: x + y,
        " - ": lambda x, y: x - y,
        " * ": lambda x, y: x * y,
        " / ": lambda x, y: x / y,
    }
    number_1 = random.choice(range(1, n))
    number_2 = random.choice(range(1, n))

    action = random.choice(list(arithmetics.keys()))
    if str(action) == ' + ' or str(action) == ' - ':
        number_1 += 10
        number_2 += 10
    answer = arithmetics[action](number_1, number_2)
    if int(answer) == answer and answer >= 0:
        question = str(number_1) + str(action) + str(number_2)
    else:
        question, answer = questionsGeneration(n)
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
    load.stop()
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
                n = 11
                question, answer = questionsGeneration(n)
                if level[y - 1][x] == '|':
                    pos_door = (y - 1, x)
                    Ivent('ivent', x, y, pos_door, question, answer)
                elif level[y + 1][x] == '|':
                    pos_door = (y + 1, x)
                    Ivent('ivent', x, y, pos_door, question, answer)
                elif level[y][x - 1] == '|':
                    pos_door = (y, x - 1)
                    Ivent('ivent', x, y, pos_door, question, answer)
                elif level[y][x + 1] == '|':
                    pos_door = (y, x + 1)
                    Ivent('ivent', x, y, pos_door, question, answer)
                else:
                    pos_door = None
                    Ivent('ivent', x, y, pos_door, question, answer)
            elif level[y][x] == '?':
                Ivent('hint', x, y)
            elif level[y][x] == '|':
                Door_ivent('door', x, y)
            elif level[y][x] == '^':
                Door_end('end_level', x, y)
            elif level[y][x] == 'E':
                Door_end('end_game', x, y)
    return new_player, x, y


# Проверка на решение всех примеров
def check_ivent():
    counts_ivent_list[1] += 1
    if counts_ivent_list[1] == counts_ivent_list[0]:
        for el in door_group:
            if type(el) is Door_end:
                el.open = True


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

    global hero_anim_count  # Индекс текущего спрайта в списке, его изменение
    if hero_anim_count == 3:
        hero_anim_count = 0
    else:
        hero_anim_count += 1

    if movement == "up":
        hero.image = walk_up[hero_anim_count]  # смена спрайта
        hero.move(0, -10)
    elif movement == "down":
        hero.image = walk_down[hero_anim_count]  # смена спрайта
        hero.move(0, 10)
    elif movement == "left":
        hero.image = walk_left[hero_anim_count]  # смена спрайта
        hero.move(-10, 0)
    elif movement == "right":
        hero.image = walk_right[hero_anim_count]  # смена спрайта
        hero.move(10, 0)


# стандартный запуск
start_screen()
game.play(-1)
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera = Camera()

max_ivent = len(ivent_group)
all_sprites.add(hero_group)
all_sprites.add(sprite_group)
all_sprites.add(wall_group)
all_sprites.add(ivent_group)
all_sprites.add(door_group)

counts_ivent_list = [max_ivent, total_ivent]
up, down, left, right = False, False, False, False  # флаги перемещения
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go.stop()
            running = False
        elif event.type == pygame.KEYDOWN:  # проверка зажатия кнопки, изменение флагов перемещения
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                up = True
                go.play(-1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                down = True
                go.play(-1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left = True
                go.play(-1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right = True
                go.play(-1)
        elif event.type == pygame.KEYUP:  # проверка зажатия кнопки, изменение флагов перемещения
            go.stop()
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_a,
                             pygame.K_s, pygame.K_d]:
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
    ivent_group.draw(screen)
    door_group.draw(screen)
    door_group.update()
    all_sprites.update()
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
game.stop()
load.stop()
pygame.quit()
