import os
import pygame

pygame.init()

FPS = 10
WIDTH = 1000
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
a = 0
bs, ds = 10, 10
qwerty = False
work = -1

all_sprites = pygame.sprite.Group()
hero = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image



class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class AnimatedSprites(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(hero)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x + 100, y + 100)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

b = load_image("hero(down).png")
b.set_colorkey((0, 0, 0))
dragon = AnimatedSprite(b, 4, 1, 1, 1)
ba = load_image("hero(left).png")
ba.set_colorkey((0, 0, 0))
dragona = AnimatedSprites(ba, 4, 1, 1, 1)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                qwerty = True
                work = 0
            if event.key == pygame.K_LEFT:
                qwerty = True
                work = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                qwerty = False
            if event.key == pygame.K_LEFT:
                qwerty = False
    if qwerty:
        screen.fill(pygame.Color("black"))
        if work == 0:
            all_sprites.draw(screen)
            all_sprites.update()
            pygame.display.flip()
        if work == 1:
            bs += 10
            ds += 10
            hero.draw(screen)
            hero.update()
            pygame.display.flip()
    clock.tick(FPS)

pygame.quit()