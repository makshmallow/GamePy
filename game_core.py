import random
import pygame as pg
import configparser
import copy
import time
import json
from scripts import *

pg.init()
# Работа с парсером
scan: configparser.ConfigParser = configparser.ConfigParser()
scan.read('setting.ini')
ratio = copy.copy(scan.getfloat('other_settings', 'ratio'))
volume: float = copy.copy(scan.getfloat('other_settings', 'volume'))
FPS: int = copy.copy(scan.getint('other_settings', 'FPS'))
day = copy.copy(scan.getint('Save', 'day'))

# некоторые асстеты
main_font = pg.font.SysFont('comicsansms', int(20 * ratio))
if_close = main_font.render('Нажмите F, для начала действия', True, (255, 255, 255))
cloud_of_info = pg.Rect(0, 0, 100 * ratio, 70 * ratio)
announce = pg.font.SysFont('comicsansms', int(60 * ratio))

# Игровые объекты привязанный к месту
clickable = dict()
all_sprites = dict()
all_borders = dict()
all_slots_objects = dict()
spawn_range = dict()
x_y_body = dict()
all_particles = dict()
enemy = dict()
all_items = dict()

# Другие списки
active_slots = list()
active_buttons = list()
blocked_to_place = list()
event_stock = list()
distributor = list()
borders_distributor = list()
windows = list()
Queue = list()
None_particles = list()
played = list()

# Создание окна
wd_height = 480 * ratio
wd_wight = 720 * ratio
wd = pg.display.set_mode((int(wd_wight), int(wd_height)))
pg.display.set_caption('Name')
cl = pg.time.Clock()


def guess(seconds: int) -> bool:
    global FPS
    return random.randint(0, seconds * FPS) == 0


def make_image(path: str, width: int, height: int) -> pg.Surface:
    global ratio
    return pg.transform.scale(pg.image.load(path), (width * ratio, height * ratio))


def animation_generator(source: str, quantity: int, width: int, height: int) -> list:
    frames = list()
    for i in range(quantity):
        frames.append(make_image(source + str(i) + ".png", width, height))
    return frames


def location_generator(name: str, spawn_x: list, spawn_y: list):
    global all_sprites, all_borders, clickable, all_slots_objects, spawn_range, all_particles
    all_sprites[name] = list()
    clickable[name] = list()
    all_slots_objects[name] = list()
    spawn_range[name] = [[int(spawn_x[0]*ratio), int(spawn_x[1]*ratio)], [int(spawn_y[0]*ratio), int(spawn_y[1]*ratio)]]
    all_borders[name] = list()
    all_particles[name] = list()
    enemy[name] = list()


def reset_all(array: list, main_hero, visible: bool = True):
    for sprite in array:
        sprite.motion(main_hero)
        if visible:
            sprite.reset()


def corpuscle(gloss: dict, chel, color: list, count: int, size: int, borders_x: list = (-30, 30),
              borders_y: list = (-30, 0), scattering: int = 20, add: tuple = (0, 0),
              differ: int = 5, where=None, array: list = None, func=lambda person, arr: None):
    if where is not None:
        def playing() -> int:
            nonlocal count, size, chel, gloss, color, add, func
            global FPS
            count -= 1
            gloss[where].append(
                [(color[0] + random.randint(-10, 10), color[1] + random.randint(-10, 10), color[2]),
                 chel.rect.x + (add[0] + random.randint(-scattering, scattering)) * ratio, chel.rect.y +
                 (add[1] + random.randint(-scattering, scattering)) * ratio,
                 random.randint(*borders_x) / FPS * 30
                 / 10 * ratio, random.randint(*borders_y) / 10 / FPS * 30 * ratio,
                 (size + random.randint(-differ, differ)) * ratio, func])
            return count
    else:
        def playing() -> int:
            nonlocal count, size, chel, color, add, func
            global FPS
            count -= 1
            array.append([(color[0] + random.randint(-10, 10),
                          color[1] + random.randint(-10, 10), color[2]),
                          chel.rect.x + (add[0] + random.randint(-scattering, scattering)) * ratio,
                          chel.rect.y + (add[1] + random.randint(-scattering, scattering)) * ratio,
                          random.randint(*borders_x) / FPS * 30
                          / 10 * ratio, random.randint(*borders_y) / 10 / FPS * 30 * ratio,
                          (size + random.randint(-differ, differ)) * ratio, func])
            return count
    return playing


def particles(screen, array: list):
    if array[5] < 0:
        array[5] = 0
    pg.draw.circle(screen, array[0], (array[1], array[2]), array[5])


def create_particles(queue: list) -> None:
    for func in queue:
        if random.randint(2, int(FPS / 10)) == 2:
            a = func()
            if a == 0:
                queue.remove(func)


def blit_particles(parts: list, person) -> None:
    global ratio, FPS
    for part in parts:
        particles(wd, part)
        part[1] += part[3] - person.real_x_speed
        part[2] += part[4] - person.real_y_speed
        part[5] -= 0.5 * ratio / FPS * 30
        # parts[6](person, parts)
        if part[5] <= 0:
            parts.remove(part)


def check_sounds():
    global played
    for sound in played:
        if time.time() - sound.point > sound.length:
            played.remove(sound)


class GameSprite(pg.sprite.Sprite):
    def __init__(self, picture: str, x: int, y: int, width, height, where=None):
        global ratio
        super().__init__()
        self.image = make_image(picture, width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x * ratio
        self.rect.y = y * ratio
        self.count = 0
        self.where = where
        if where is not None:
            all_sprites[where].append(self)
        else:
            distributor.append(self)

    def reset(self):
        wd.blit(self.image, (self.rect.x, self.rect.y))

    def motion(self, person):
        self.rect.x -= person.real_x_speed
        self.rect.y -= person.real_y_speed

    def counter(self, frames, length):
        global FPS
        real_length = length * 60 / FPS
        if self.image not in frames:
            self.count = 0
        self.count += 1
        self.image = frames[int(self.count / real_length)]
        if self.count + 1 >= real_length * len(frames):
            self.count = 0


class GameEvent:
    def __init__(self, min_time, radius):
        self.radius = radius
        self.min_time = min_time
        self.last_call = time.time() - min_time
        self.active = False
        event_stock.append(self)

    def check(self):
        if time.time() - self.last_call > self.min_time:
            if guess(self.radius):
                self.active = True
                self.last_call = time.time()


class SerialSound:
    def __init__(self, source, length):
        self.sound = pg.mixer.Sound(source)
        self.sound.set_volume(volume / 100)
        self.length = length
        self.point = None

    def play(self):
        global played
        if self not in played:
            self.sound.play()
            played.append(self)
            self.point = time.time()


class ForBorders(GameSprite):
    def __init__(self, x, y, width, height, where):
        global ratio
        super().__init__('images/nothing.png', x, y, width, height, where)
        all_borders[self.where].append(self)

    def reset(self):
        pg.draw.rect(wd, (255, 255, 255), self.rect)


class Item(GameSprite):
    def __init__(self, picture, length, name, description, special_stat=None):
        super().__init__(picture, 0, 0, length, length)
        self.name = name
        self.description = description
        self.stats = special_stat
        all_items[name] = self

    def use(self, person):
        pass


class Toxic(Item):
    def __init__(self, picture, length, name, description, stats):
        super().__init__(picture, length, name, description, stats)
        self.damage = None

    def use(self, person):
        global Queue, enemy, ratio
        Queue.append(corpuscle(all_particles, person, *self.stats, where=person.where))
        person.inventory.slots[-1].number -= 1
        if person.inventory.slots[-1].number == 0:
            person.held = None
            person.inventory.slots[-1].item = None
        for obj in enemy[person.where]:
            if (person.rect.x - obj.rect.x) ** 2 + (person.rect.y - obj.rect.y) ** 2 < 40000 * ratio ** 2:
                obj.death = True


class Food(Item):
    def use(self, person):
        self.stats.play()
        person.health += 1 * FPS
        person.inventory.slots[-1].number -= 1
        if person.inventory.slots[-1].number == 0:
            person.inventory.slots[-1].item = None
            person.held = None


class Weapon(Item):
    def use(self, person):
        if not person.current_animation == person.animations['attack']:
            person.current_animation = person.animations['attack']
            person.current_animation_str = 'attack'
            person.active = True


class Skin(Item):
    def __init__(self, picture, length, name, description, animations, sound):
        super().__init__(picture, length, name, description)
        self.animations = animations
        self.sound = sound


class Clickable(GameSprite):
    def __init__(self, picture, x, y, width, height, where):
        super().__init__(picture, x, y, width, height, where)
        self.be_ready = False
        self.open = False
        clickable[where].append(self)

    def analysis(self, person):
        if (person.rect.x - self.rect.x) ** 2 + (person.rect.y - self.rect.y) ** 2 < 10000 * ratio ** 2:
            self.be_ready = True
            wd.blit(if_close, (200 * ratio, 400 * ratio))
        else:
            self.be_ready = False


class CoPortal(Clickable):
    def __init__(self, x, y, where, host):
        super().__init__(r'images/nothing.png', x, y, 1, 1, where)
        self.host = host

    def do(self, person):
        self.host.do(person)


class Portal:
    def __init__(self, x1, y1, where1, x2, y2, where2):
        self.point_1 = CoPortal(x1, y1, where1, self)
        self.point_2 = CoPortal(x2, y2, where2, self)

    def do(self, person):
        if self.point_1.where == person.where:
            person.where = self.point_2.where
        else:
            person.where = self.point_1.where


class Slot(GameSprite):
    def __init__(self, picture: str, length: int, x: int, y: int, inventory, cords: tuple):
        super().__init__(picture, x, y, length, length)
        self.host = inventory
        self.cords = cords
        self.item = None
        self.number = 0

    def reset(self):
        wd.blit(self.image, (self.rect.x, self.rect.y))
        if self.item is not None:
            wd.blit(self.item.image, (self.rect.x, self.rect.y))
            wd.blit(main_font.render(str(self.number), True, (0, 0, 0)),
                    (self.rect.x + 2 / 3 * self.rect.width, self.rect.y + 2 / 3 * self.rect.width))


class Button(pg.sprite.Sprite):
    def __init__(self, picture, x, y, width, height, host, command):
        super().__init__()
        self.host = host
        self.image = make_image(picture, width, height)
        self.rect = self.image.get_rect()
        self.rect.x = host.x2 + x * ratio
        self.rect.y = host.y2 + y * ratio
        self.command = command

    def reset(self):
        wd.blit(self.image, (self.rect.x, self.rect.y))


class WithSlot(Clickable):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2,
                 lines, columns, x_start, y_start, image_of_slots, length, inventory):
        super().__init__(picture, x, y, width, height, where)
        self.interface = GameSprite(interface, x2, y2, width2, height2)
        self.x2 = x2
        self.y2 = y2
        self.open = False
        self.lines = lines
        self.columns = columns
        self.inventory = inventory
        self.slots = list()
        for line in range(lines):
            for column in range(columns):
                self.slots.append(Slot(
                    image_of_slots, length, self.x2 + column * length + x_start,
                                            self.y2 + line * length + y_start, self, (line, column)))
        self.x2 = x2 * ratio
        self.y2 = y2 * ratio
        all_slots_objects[where].append(self)

    def check_for(self):
        pass

    def another_check_for(self, slot):
        pass

    def do(self, person):
        global active_slots
        if self.inventory.open and self.inventory.active is None:  # если открыт инвентарь то он закрывается
            if self.inventory.grab is None:
                for slot in person.inventory.slots:
                    active_slots.remove(slot)
                self.inventory.open = False
        else:
            if self.inventory.active is None:  # откат или активация
                self.inventory.active = self
                self.inventory.host.x_speed = 0
                self.inventory.host.y_speed = 0
            else:
                self.inventory.active = None
            self.inventory.open = not self.inventory.open
            self.open = not self.open
            if self.open:
                active_slots += self.slots
                active_slots += person.inventory.slots
            else:
                for slot in self.slots:
                    active_slots.remove(slot)
                for slot in person.inventory.slots:
                    active_slots.remove(slot)


class WithButtons(Clickable):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory):
        super().__init__(picture, x, y, width, height, where)
        if interface is not None:
            self.interface = GameSprite(interface, x2, y2, width2, height2)
        self.inventory = inventory
        self.x2 = x2 * ratio
        self.y2 = y2 * ratio
        self.buttons = list()

    def do(self, person):
        global active_slots, active_buttons
        if self.inventory.open and self.inventory.active is None:
            if self.inventory.grab is None:  # если открыт инвентарь то он закрывается
                for slot in person.inventory.slots:
                    active_slots.remove(slot)
                self.inventory.open = False
        else:
            if self.inventory.active is None:  # откат или активация
                self.inventory.active = self
                self.inventory.host.x_speed = 0
                self.inventory.host.y_speed = 0
            else:
                self.inventory.active = None
            self.inventory.open = not self.inventory.open
            self.open = not self.open
            if self.open:
                active_buttons += self.buttons
                active_slots += person.inventory.slots
            else:
                for button in self.buttons:
                    active_buttons.remove(button)
                for slot in person.inventory.slots:
                    active_slots.remove(slot)

    def check_for(self):
        pass

    def another_check_for(self, slot):
        pass


class Inventory(GameSprite):
    def __init__(self, picture: str, x, y, width, height, lines, columns, x_start, y_start, image_of_slots, length):
        super().__init__(picture, x, y, width, height)
        self.open = False
        self.host = None
        self.lines = lines
        self.columns = columns
        self.grab = None
        self.slots = list()
        self.info = None
        self.active = None

        for line in range(lines):  # генерация слотов
            for column in range(columns):
                self.slots.append(Slot(
                    image_of_slots, length, x + column * length + x_start,
                                            y + line * length + y_start, self, (line, column)))

        self.slots.append(Slot(image_of_slots, length,  # слот скина
                               x + x_start, y + self.lines * length + 20 + y_start, self, (self.lines, 0)))

        self.slots.append(Slot(image_of_slots, length,  # слот предмета в руке
                               x + length + x_start, y + self.lines * length + 20 + y_start, self, (self.lines, 1)))

    def show(self):
        global ratio, active_slots
        self.reset()
        if self.host.skin is None:
            if isinstance(self.slots[-2].item, Skin):
                self.host.skin = self.slots[-2].item  # напяливание скина
                self.host.skin.sound.play()
        elif not isinstance(self.slots[-2].item, Skin):  # снятие скина
            self.host.skin.sound.play()
            self.host.skin = None
        self.host.held = self.slots[-1].item
        if self.active is not None:
            self.active.interface.reset()  # отображение интерфейса WithSlot
        for slot in active_slots:
            slot.reset()
        for button in active_buttons:
            button.reset()
        if self.grab is not None:
            cords = pg.mouse.get_pos()  # отображение взятого предмета
            wd.blit(self.grab.image, cords)
        if self.info is not None:  # отображение инфы
            pg.draw.rect(wd, (100, 100, 100),
                         (self.info.rect.x + self.info.rect.width, self.info.rect.y, 300 * ratio, 150 * ratio))
            pg.draw.rect(wd, (255, 255, 255),
                         (self.info.rect.x + self.info.rect.width, self.info.rect.y, 300 * ratio, 150 * ratio), 5)
            wd.blit(main_font.render(self.info.item.name, True, (0, 0, 0)),
                    (self.info.rect.x + self.info.rect.width + 10 * ratio, self.info.rect.y))
            for i in range(len(self.info.item.description)):
                wd.blit(main_font.render(self.info.item.description[i], True, (0, 0, 0)),
                        (self.info.rect.x + self.info.rect.width + 10 * ratio,
                         self.info.rect.y + 30 * ratio + 20 * i * ratio))

    def shift(self, event):
        global active_slots
        if self.grab is not None or self.open:
            if event.type == pg.MOUSEBUTTONDOWN:  # нажатие при попытки взять предмет
                xx, yy = event.pos
                if event.button == 1:
                    for slot in active_slots:
                        if slot.rect.collidepoint(xx, yy):
                            if self.active is not None:
                                self.active.another_check_for(slot)
                            if slot.item is not None and slot.number > 0:
                                self.grab = slot.item  # забор предмета
                                slot.number -= 1
                                if slot.number == 0:
                                    slot.item = None
                            break
                    for button in active_buttons:
                        if button.rect.collidepoint(xx, yy):
                            self.active.do_command(button)
                            break
                elif event.button == 3:
                    for slot in active_slots:  # назначение из какого слота инфу чекать
                        if slot.rect.collidepoint(xx, yy) and slot.item is not None:
                            self.info = slot
            if event.type == pg.MOUSEMOTION:
                self.info = None
            if event.type == pg.MOUSEBUTTONUP and self.grab is not None:  # держал предмет и отпустил
                xx, yy = event.pos
                nearest = active_slots[0]
                for slot in active_slots:  # поиск ближайшего слота
                    if slot.item is None or self.grab == slot.item:
                        if (slot.rect.x - xx) ** 2 + (slot.rect.y - yy) ** 2 < (nearest.rect.x - xx) ** 2 + (
                                nearest.rect.y - yy) ** 2:
                            if slot is self.slots[-2]:  # проверка для слота скина
                                if isinstance(self.grab, Skin):
                                    nearest = slot
                            else:
                                if slot not in blocked_to_place:
                                    nearest = slot
                if self.grab is not nearest.item:  # помещение предмета в слот
                    nearest.item = self.grab
                    nearest.number = 1
                else:
                    nearest.number += 1
                if self.active is not None:
                    self.active.check_for()
                self.grab = None


class Health(GameSprite):
    def __init__(self, picture, width, height, host, x2, y2, height2):
        super().__init__(picture, 0, 0, width, height)
        self.host = host
        self.health_rect = pg.Rect(x2 * ratio, y2 * ratio, host.health * ratio / FPS * 10, height2)
        self.psycho_rect = pg.Rect(x2 * ratio, (y2 + 20) * ratio, host.psycho * ratio / FPS * 10, height2)

    def reset(self):
        super().reset()
        self.health_rect.width = self.host.health * ratio / FPS * 10
        self.psycho_rect.width = self.host.psycho * ratio / FPS * 10
        pg.draw.rect(wd, (255, 100, 100), self.health_rect)
        pg.draw.rect(wd, (150, 210, 160), self.psycho_rect)


class PlayerGetReady(GameSprite):
    def __init__(self, picture, x, y, wight, height, speed, inventory, animations: dict, health: int, psycho):
        super().__init__(picture, x, y, wight, height)
        self.image1 = self.image
        self.speed = int(speed * ratio * 60 / FPS)
        self.inventory = inventory
        self.inventory.host = self
        self.animation_length = int(13 * FPS / 60)
        self.x_speed = 0
        self.y_speed = 0
        self.real_x_speed = 0
        self.real_y_speed = 0
        self.where = 'main'
        self.skin = None
        self.held = None
        self.active = None
        self.controls = dict(go_right=scan.getint('control', 'go_right'),
                             go_left=scan.getint('control', 'go_left'),
                             go_down=scan.getint('control', 'go_down'),
                             go_up=scan.getint('control', 'go_up'),
                             do=scan.getint('control', 'do'),
                             open_inventory=scan.getint('control', 'open_inventory'),
                             use_item=scan.getint('control', 'use_item'),
                             dash=scan.getint('control', 'dash'))
        self.animations: dict = animations
        self.current_animation = list()
        self.current_animation_str = ''
        self.touched = []
        self.health = health * FPS
        self.psycho = psycho * FPS
        self.health_bar = Health(r'images/person_stuff/health_bar.png', 240, 96, self, 75, 20, 15)
        self.dash = 0
        self.dash_animation = []
        self.dash_shift = (0, 0)
        self.stock = list()

    def reset(self):
        self.stock = list()
        self.health_bar.reset()

        if self.image not in self.current_animation:
            self.count = 0  # проверка смены анимации
        self.count += 1
        if self.count + 1 >= self.animation_length * len(self.current_animation):
            self.count = 0  # цикличность анимации
            self.active = False
        else:
            self.image = self.current_animation[int(self.count / self.animation_length)]  # установление изображения
        if self.skin is not None:
            if self.image is self.image1:
                wd.blit(self.skin.animations['main'],
                        (self.rect.x, self.rect.y))  # отображение скина
            else:
                wd.blit(self.skin.animations[self.current_animation_str][int(self.count / self.animation_length)],
                        (self.rect.x, self.rect.y))
        else:
            super().reset()
            
        if self.held is not None and self.image is self.image1:
            wd.blit(self.held.image, (self.rect.x + 35 * ratio, self.rect.y + 35 * ratio))

        if self.dash:
            if self.dash != int(FPS*0.5):
                wd.blit(self.dash_animation[int(self.dash/(FPS*0.1))],
                        (self.rect.x + self.dash_shift[0], self.rect.y + self.dash_shift[1]))
                self.dash += 1
                if int(self.dash/(FPS*0.1)) == 5:
                    self.dash = 0
                    self.x_speed /= 3
                    self.y_speed /= 3

    def control(self, event1):
        global active_slots
        if event1.type == pg.KEYDOWN:
            self.stock.append(event1.key)
            key = event1.key
            if self.inventory.active is None and not self.dash:
                if key == self.controls.get('go_up'):
                    self.y_speed = -self.speed
                    if self.x_speed == 0:
                        self.current_animation = self.animations['person_walking']
                        self.current_animation_str = 'person_walking'
                elif key == self.controls.get('go_down'):
                    self.y_speed = self.speed
                    if self.x_speed == 0:
                        self.current_animation = self.animations['person_walking']
                        self.current_animation_str = 'person_walking'
                elif key == self.controls.get('go_left'):
                    self.x_speed = -self.speed
                    self.current_animation = self.animations['person_walking']
                    self.current_animation_str = 'person_walking'
                elif key == self.controls.get('go_right'):
                    self.current_animation = self.animations['person_walking_right']
                    self.current_animation_str = 'person_walking_right'
                    self.x_speed = self.speed
                elif key == self.controls.get('dash') and not self.dash and (self.x_speed or self.y_speed):
                    self.dash += 1
                    self.x_speed *= 3
                    self.y_speed *= 3
                    if self.x_speed == 0:
                        if self.y_speed > 0:
                            self.dash_animation = self.animations['person_dash_down']
                            self.dash_shift = (-50*ratio, -100*ratio)
                        else:
                            self.dash_animation = self.animations['person_dash_up']
                            self.dash_shift = (-50 * ratio, -100 * ratio)
                    elif self.x_speed > 0:
                        self.dash_animation = self.animations['person_dash_right']
                        self.dash_shift = (-200 * ratio, -10*ratio)
                    else:
                        self.dash_animation = self.animations['person_dash_left']
                        self.dash_shift = (-50 * ratio, -10*ratio)

            if key == self.controls.get('do'):
                for thing in clickable[self.where]:
                    if thing.be_ready:
                        if self.inventory.grab is None:
                            thing.do(self)
                        break
            elif key == self.controls.get('open_inventory') and self.inventory.active is None:
                if not self.inventory.open and self.inventory.active is None:
                    active_slots += self.inventory.slots
                    self.inventory.open = True
                elif self.inventory.grab is None:
                    for slot in self.inventory.slots:
                        active_slots.remove(slot)
                    self.inventory.open = False
            if key == self.controls.get('use_item'):
                if self.held is not None and not self.active:
                    self.held.use(self)
        elif event1.type == pg.KEYUP and not self.dash:
            if event1.key == self.controls['go_down'] or event1.key == self.controls['go_up']:
                self.y_speed = 0
            elif event1.key == self.controls['go_right'] or self.controls['go_left']:
                self.x_speed = 0
            if self.x_speed == 0 and self.y_speed == 0:
                self.image = self.image1
            if self.x_speed == 0 and self.y_speed == 0:
                self.image = self.image1
                self.current_animation = list()

    def collusion(self):
        for border in all_borders[self.where]:
            if pg.sprite.collide_rect(self, border):  # чекает соприкосновения
                self.touched.append(border)
        real_speed = [True, True]
        for el in self.touched:
            if el.rect.y - self.rect.height + 10 * ratio < self.rect.y < el.rect.y + el.rect.height - 10 * ratio:
                if el.rect.x > self.rect.x:  # чекает с какой стороны
                    if self.x_speed > 0:
                        real_speed[0] = False
                else:
                    if self.x_speed < 0:
                        real_speed[0] = False
            else:
                if self.rect.y < el.rect.y:
                    if self.y_speed > 0:
                        real_speed[1] = False
                else:
                    if self.y_speed < 0:
                        real_speed[1] = False
        self.real_x_speed = self.x_speed * real_speed[0]  # блокирует движение
        self.real_y_speed = self.y_speed * real_speed[1]
        self.touched = []


class Enemy(GameSprite):
    def __init__(self, picture, width, height, where, animations, health, speed):
        super().__init__(picture, 0, 0, width, height, where)
        self.animations = animations
        self.health = health * FPS
        self.time_spawn = time.time()
        self.death = False
        self.speed = int(speed * 60 / FPS * ratio)
        self.touched = []
        enemy[where].append(self)

    def spawn(self):
        spawn1 = False
        while not spawn1:
            spawn1 = True
            self.rect.x = random.randint(spawn_range[self.where][0][0], spawn_range[self.where][0][1]) + x_y_body[
                self.where].rect.x
            self.rect.y = random.randint(spawn_range[self.where][1][0], spawn_range[self.where][1][1]) + x_y_body[
                self.where].rect.y
            for border in all_borders[self.where]:
                if pg.sprite.collide_rect(self, border):
                    spawn1 = False
                    break


# # # # # # # # # # # # # # # # # # # # # Special cases # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Sender(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.good_reports = 0
        self.y_cursor = 0
        self.init = True
        self.buttons.append(Button(r'images/buttons/button_success.png', 200, 50, 70, 30, self, 'send_success'))
        self.buttons.append(Button(r'images/buttons/send_failure.png', 200, 90, 70, 30, self, 'send_failure'))

    def do_command(self, button):
        global active_buttons, Queue
        match button.command:
            case 'send_success':
                if self.init:
                    if self.y_cursor >= 5:
                        active_buttons = active_buttons[:-5]
                        self.buttons = self.buttons[:-5]
                        self.y_cursor = 0
                        print('rollback')
                    self.buttons.append(Button(r'images/buttons/report_progress.png', 10, 20 + 50 * self.y_cursor,
                                               100, 50, self, 'progress'))
                    active_buttons.append(self.buttons[-1])
                    self.y_cursor += 1
                    self.good_reports += 1
                    self.init = False
                    print('success')

            case 'progress':
                Queue.append(corpuscle(all_particles, button, [100, 200, 100],
                                       20, 10, add=(40, 20), array=None_particles))

            case 'send_failure':
                if self.init:
                    if button.command == 'send_success':
                        if self.y_cursor >= 5:
                            active_buttons = active_buttons[:-5]
                            self.buttons = self.buttons[:-5]
                            self.y_cursor = 0
                            print('rollback')
                    self.buttons.append(Button(r'images/buttons/report_failure.png', 10, 20 + 50 * self.y_cursor,
                                               100, 50, self, 'loss'))
                    active_buttons.append(self.buttons[-1])
                    self.y_cursor += 1
                    self.good_reports -= 1
                    self.init = False


class Insect(GameEvent):
    def __init__(self, green_house):
        super().__init__(0, 0)
        self.green_house = green_house
        self.active = True

    def check(self):
        pass

    def action(self):
        global active_buttons
        self.green_house.crop += (0.1 - len(self.green_house.buttons) * 0.01) / FPS
        if guess(10):
            self.green_house.buttons.append(
                Button(r'images\buttons\insect.png',
                       random.randint(0, int(self.green_house.interface.rect.width / ratio)),
                       random.randint(0, int(self.green_house.interface.rect.height / ratio)),
                       100, 100, self.green_house, 'insect'))
            if self.green_house.inventory.active is self.green_house:
                active_buttons.append(self.green_house.buttons[-1])


class GreenHouse(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory, crop):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.item = crop
        self.crop = 0
        self.buttons.append(Button(r'images/buttons/take.png', 20, 20, 80, 80, self, 'take'))

    def do_command(self, button):
        global active_buttons
        match button.command:
            case 'insect':
                active_buttons.remove(button)
                self.buttons.remove(button)
            case 'take':
                for slot in self.inventory.slots:
                    if slot.item is None and self.crop > 1:
                        slot.item = self.item
                        slot.number = int(self.crop)
                        self.crop -= int(self.crop)
                        break


class CampCheck(GameEvent):
    def __init__(self, core, player, sender, chp):
        super().__init__(0, 0)
        self.active = True
        self.core = core
        self.player = player
        self.sender = sender
        self.chp = chp

    def check(self):
        pass

    def action(self):
        if self.player.where == 'main' and self.player.skin is None and self.core.atmosphere < 0.5:
            self.player.health -= 0.5 - self.core.atmosphere
        if self.core.condition < 0:
            self.active = False
        if self.chp.duration <= 0:
            self.core.condition -= 0.01 / FPS
        else:
            self.chp.duration -= 0.01 / FPS
        if self.player.health < 0:
            self.active = False


class CoCampCore(GameSprite):
    def __init__(self, picture, x, y, width, height, host):
        super().__init__(picture, x, y, width, height)
        self.host = host

    def reset(self):
        super().reset()
        self.host.buttons[0].image = main_font.render("Чистота воздуха " + str(round(self.host.atmosphere, 4)),
                                                      True, (255, 255, 255))  # характеристики
        self.host.buttons[1].image = main_font.render("Состояние ядра " + str(round(self.host.condition, 4)),
                                                      True, (255, 255, 255))


class CampCore(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.interface = CoCampCore(interface, x2, y2, width2, height2, self)
        self.atmosphere = 1
        self.condition = 1
        self.inventory = inventory
        self.buttons.append(Button(r'images/nothing.png', 20, 20, 1, 1, self, ''))
        self.buttons.append(Button(r'images/nothing.png', 20, 120, 1, 1, self, ''))


class CHP(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2,
                 inventory, fuel, core):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.fuel = fuel
        self.duration = 1
        self.core = core
        self.buttons.append(Button(r'images/buttons/power.png', 15, 15, 50, 50, self, "take"))

    def do_command(self, button):
        if button.command == 'take':
            for slot in self.inventory.slots:
                if slot.item == self.fuel:
                    slot.number -= 1
                    if slot.number == 0:
                        slot.item = None
                    self.duration += 1
                    break


class Mine(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory, items):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.items = items  # TODO: сделать что-то с шахтой
        self.init = True  # чтоб не спамить
        for i in range(6):
            for j in range(7):
                self.buttons.append(Button(
                    r'images/buttons/stone.png', (50 + 20 * j) * ratio, (20 + 20 * i) * ratio, 20 * ratio, 20 * ratio,
                    self, 'stone'))
        for button in self.buttons:  # генерация ресов
            if random.randint(1, 4) == 1:
                button.command = 'coal'
            elif random.randint(1, 7) == 1:
                button.command = 'active_metal'
            elif random.randint(1, 7) == 1:
                button.command = 'nonactive_metal'

    def do_command(self, button):
        global active_buttons
        if self.init and button.command in self.items and self.init:  # забор ресов
            for item in self.items:
                if item == button.command:
                    for slot in self.inventory.slots:
                        if slot.item is None or slot.item.name == item:
                            slot.item = self.items[item]
                            slot.number += 1
                            self.init = False
                            self.buttons.remove(button)
                            active_buttons.remove(button)
                            break
                    break


class CoReader(GameSprite):
    def __init__(self, picture, x, y, width, height, x2, y2):
        super().__init__(picture, x, y, width, height)
        self.x2 = (x + x2) * ratio  # TODO: кравсивый интерфейс читалки
        self.y2 = (y + y2) * ratio
        self.text_surfs = []
        self.cursor = 0

    def make_performance(self, text):  # добавление текста
        self.text_surfs.append([main_font.render(x, True, (255, 255, 255)) for x in text])

    def reset(self):
        super().reset()
        for i in range(len(self.text_surfs[self.cursor])):  # отображения текста 
            wd.blit(self.text_surfs[self.cursor][i], (self.x2, self.y2 + 20 * i * ratio))


class Reader(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory, x3, y3):
        super().__init__(picture, x, y, width, height, where, None, x2, y2, width2, height2, inventory)
        self.interface = CoReader(interface, x2, y2, width2, height2, x3, y3)
        # кнопки влево, вправо
        self.buttons.append(Button(r'images/buttons/book_right.png', width2 - 40, height2 - 40, 30, 30, self, "right"))
        self.buttons.append(Button(r'images/buttons/book_left.png', 10, height2 - 40, 30, 30, self, "left"))
        self.texts = reader_scripts

    def do_command(self, button):
        match button.command:
            case "left":
                if self.interface.cursor != 0:
                    self.interface.cursor -= 1
            case "right":
                if self.interface.cursor < len(self.interface.text_surfs) - 1:
                    self.interface.cursor += 1


class CoWindow(GameSprite):
    def __init__(self, picture, x, y, width, height, day1, host, picture2):
        super().__init__(picture, x, y, width, height)
        self.day = day1
        self.host = host
        self.night_pic = picture2
        self.day_pic = picture

    def reset(self):
        global active_buttons, windows
        super().reset()
        if self.day.active:
            if not random.randint(0, int(FPS)):
                self.host.buttons.append(Button(r'', random.randint(0, self.rect.width), 0, 10, 25, self.host, 'pop'))
        for button in self.host.buttons:
            button.rect.y += 1 * ratio
            if button.rect.y > self.rect.y + self.rect.height:
                self.host.buttons.remove(button)
                active_buttons.remove(button)

        # TODO: Переключение с дня и ночи, хз


class Window(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, picture2,
                 x2, y2, width2, height2, inventory, day1):
        super().__init__(picture, x, y, width, height, where, None, x2, y2, width2, height2, inventory)
        self.interface = CoWindow(interface, x2, y2, width2, height2, day1, self, picture2)
        windows.append(self)

    def do_command(self, button):
        match button.command:
            case 'pop':
                self.buttons.remove(button)
                active_buttons.remove(button)
                self.inventory.host.psycho += 0.1 * FPS


class Capsule(WithButtons):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory, resources):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2, inventory)
        self.resources = resources

    def do_command(self, button):
        if button.command == 'destroy' and self.inventory.host.psycho <= 2 * FPS:
            for slot in self.inventory.slots:
                if slot.item is None:
                    slot.item = self.resources
