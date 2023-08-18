from game_core import *
import math

# # # # # # # # # # # # # # # # # # # # Анимации # # # # # # # # # # # # # # # # # # # # #

# Перс #
person_walking = animation_generator(r'images/person_stuff/person_walking', 4, 70, 100)

person_walking_right = animation_generator(r'images/person_stuff/person_walking_right', 4, 70, 100)

person_dash_right = animation_generator(r'images/person_stuff/dash_right', 5, 300, 150)

person_dash_up = animation_generator(r'images/person_stuff/dash_up', 5, 150, 300)

person_dash_down = animation_generator(r'images/person_stuff/dash_down', 5, 150, 300)

person_dash_left = animation_generator(r'images/person_stuff/dash_left', 5, 300, 150)

person_animations = {'person_walking': person_walking, 'person_walking_right': person_walking_right,
                     'person_dash_up': person_dash_up, 'person_dash_down': person_dash_down,
                     'person_dash_left': person_dash_left, 'person_dash_right': person_dash_right}

# Одежда #
water_proof_walking = animation_generator(r'images/animations/water_proof_walking', 4, 70, 100)

water_proof_walking_right = animation_generator(r'images/animations/water_proof_walking_right', 4, 70, 100)

water_proof_main = make_image(r'images/animations/water_proof_main.png', 70, 100)

water_proof_animations = {'main': water_proof_main, 'person_walking': water_proof_walking,
                          'person_walking_right': water_proof_walking_right}

# Враги #
worm_animations = {'spawn': animation_generator(r'images/animations/spawn_worm', 3, 60, 50),
                   'crawl': animation_generator(r'images/animations/worm', 3, 60, 50)}

rat_animations = {'walking': animation_generator(r'images/animations/rat_walking', 3, 80, 48),
                  'walking_right': animation_generator(r'images/animations/rat_walking_right', 3, 80, 48)}

mole_animations = {'get': animation_generator(r'images/animations/mole_spawn', 5, 150, 150),
                   'attack': animation_generator(r'images/animations/mole_attack', 5, 150, 150),
                   'death': animation_generator(r'images/animations/mole_spawn', 5, 150, 150)[::-1]}

# # # # # # # # # # # # # # # # # # # # Звуки  # # # # # # # # # # # # # # # # # # # # # #

take_off_on_sound = SerialSound(r'sounds/zip_sound.mp3', 1)

potato_sound = SerialSound(r'sounds/hrum.mp3', 1)

# # # # # # # # # # # # # # # # # Конкретные классы # # # # # # # # # # # # # # # # # # #


class Day(GameEvent):
    def __init__(self, min_time, core, init, reader, person, windows):
        super().__init__(min_time, 0)
        self.sign = announce.render("День" + str(day), True, (255, 255, 255))
        self.day = day
        self.core = core
        self.init = init
        self.reader = reader
        self.drops = list()
        self.intense = 5
        self.person = person
        self.windows = windows

    def action(self):
        global windows
        if time.time() - self.last_call < 2:
            wd.blit(self.sign, (250 * ratio, 180 * ratio))
        if time.time() - self.last_call > 0.5 * self.min_time:  # TODO: выбор записей, под ситуацию
            for obj in self.init:
                obj.init = True  # откат объектов
            self.active = False  # прибавление дня
            self.day += 1
            self.sign = announce.render("День " + str(self.day), True, (255, 255, 255))
            if self.person.psycho > 2*FPS:
                curr = random.choice(self.reader.texts[:-1])  # вывод в читалку
            else:
                curr = random.choice(self.reader.texts)
            if curr:
                text = curr.pop(random.randint(0, len(curr) - 1))
                text.insert(0, "День " + str(self.day))
                self.reader.interface.make_performance(text)
            for window in windows:  # окна
                window.image = window.night_pic

        if guess(1):
            enemy['main'].append(Worm(r'images/enemy/worm.png', 60, 50, 'main', worm_animations, self.core))
        if random.randint(1, int(FPS/20)) == 1:
            for i in range(self.intense):
                self.drops.append(
                    [pg.Rect((random.randint(int(-100 * ratio), int(820 * ratio)), 0, 5 * ratio, 15 * ratio)),
                     random.randint(2, 10)])
        if guess(7):
            enemy['main'].append(Mole(r'images/nothing.png', 150, 150, 'main', mole_animations, 10, 2, 200))
        for i in range(len(self.drops)):
            self.drops[i][0].y += self.drops[i][1] - self.person.real_y_speed
            self.drops[i][0].x -= self.person.real_x_speed
            self.drops[i][1] += 0.2
            pg.draw.rect(wd, (100, 100, 200), self.drops[i][0])

        for i in self.drops:
            if i[1] > 14:
                self.drops.remove(i)
                del i


class Night(GameEvent):
    def __init__(self, min_time):
        super().__init__(min_time, 0)
        self.last_call = self.last_call + min_time * 0.5

    def action(self):
        global windows
        if time.time() - self.last_call > self.min_time * 0.5:
            for window in windows:
                window.image = window.day_pic
            self.active = False
            # for x in enemy:
            #     for xx in enemy[x]:
            #         xx.death = True

        if guess(5):
            if len([None for x in enemy['main'] if isinstance(x, Snake)]) < 5:
                enemy['main'].append(Snake(12, 12, 'main', random.randint(10, 30), 5))


class RatRave(GameEvent):
    def __init__(self, min_time, radius, core):
        super().__init__(min_time, radius)
        self.core = core

    def action(self):
        if guess(15):
            self.active = False
        if guess(3):
            enemy['workshop'].append(Rat(80, 48, 'workshop', rat_animations, 3, self.core))


class CraftTable(WithSlot):
    def __init__(self, picture, x, y, width, height, where, interface, x2, y2, width2, height2,
                 lines, columns, x_start, y_start, image_of_slots, length, inventory, craft_list, result, x_res, y_res):
        super().__init__(picture, x, y, width, height, where, interface, x2, y2, width2, height2,
                         lines, columns, x_start, y_start, image_of_slots, length, inventory)
        self.craft_list = craft_list
        self.result_list = result
        self.slots.append(
            Slot(image_of_slots, length, x_res + self.x2 / ratio, y_res + self.y2 / ratio, self, (None, None)))
        blocked_to_place.append(self.slots[-1])
        self.current_craft = None

    def check_for(self):  # при отжатии мышки (помещение какого-то предмета на верстак)
        a = []
        for slot in self.slots[:-1]:
            if slot.item is not None:  # считывание вещей верстака
                a.append(slot.item.name)
            else:
                a.append(None)
        if a in self.craft_list:
            self.slots[-1].item = self.result_list[self.craft_list.index(a)]  # помещение скрафченного предмета
            self.slots[-1].number = 1
            self.current_craft = self.craft_list.index(a)

    def another_check_for(self, slot):  # при нажатии
        a = []
        for slot1 in self.slots[:-1]:
            if slot1.item is not None:
                a.append(slot1.item.name)
            else:
                a.append(None)
        if self.current_craft is not None:
            if not a == self.craft_list[self.current_craft]:
                self.slots[-1].item = None
        if slot is self.slots[-1]:
            for slot in self.slots[:-1]:
                if slot.number != 0:
                    slot.number -= 1
                if slot.number == 0:
                    slot.item = None


class Worm(Enemy):
    def __init__(self, picture, width, height, where, animations, core):
        super().__init__(picture, width, height, where, animations, 1, 2)
        self.core = core
        self.forward = 0
        self.spawn()

    def motion(self, person):
        if time.time() - self.time_spawn < 2:
            self.counter(self.animations['spawn'], int(FPS * 0.7))
            self.rect.x -= person.real_x_speed
            self.rect.y -= person.real_y_speed
        elif self.death:
            enemy[self.where].remove(self)
            all_sprites[self.where].remove(self)
            self.core.atmosphere -= 0.005
        else:
            if self.forward == 0:
                self.forward = random.randint(0, 5) * FPS
                self.speed = -self.speed
            else:
                for border in all_borders[self.where]:
                    if pg.sprite.collide_rect(self, border):
                        self.forward = random.randint(0, 5) * FPS
                        self.speed = -self.speed
                self.counter(self.animations['crawl'], int(FPS * 0.25))
                self.rect.x -= person.real_x_speed - self.speed
                self.rect.y -= person.real_y_speed
                if pg.sprite.collide_rect(self, person):
                    self.death = True
                self.forward -= 1


class Rat(Enemy):
    def __init__(self, width, height, where, animations, speed, core):
        super().__init__(r'images/nothing.png', width, height, where, animations, 2, speed)
        self.core = core
        self.spawn()

    def motion(self, person):
        global all_borders
        if self.death:
            enemy[self.where].remove(self)  # при смерти
            all_sprites[self.where].remove(self)
        else:
            if person.rect.x - self.rect.x == 0:
                iks = 1
            else:
                iks = person.rect.x - self.rect.x
            fi = math.atan((person.rect.y - self.rect.y) / iks)
            if (iks > 0 > math.cos(fi)) or (iks < 0 < math.cos(fi)):
                fi += math.pi
            xcor = int(-self.speed * math.cos(fi))
            ycor = int(-self.speed * math.sin(fi))
            if xcor > 0:
                self.counter(self.animations['walking_right'], int(FPS * 0.2))
            else:
                self.counter(self.animations['walking'], int(FPS * 0.2))
            for border in all_borders[self.where]:
                if pg.sprite.collide_rect(self, border):
                    self.touched.append(border)
            real_speed = [True, True]
            for el in self.touched:
                if el.rect.y - self.rect.height + 10 * ratio < self.rect.y < el.rect.y + el.rect.height - 10 * ratio:
                    if el.rect.x > self.rect.x:  # чекает с какой стороны
                        if xcor > 0:
                            real_speed[0] = False
                    else:
                        if xcor < 0:
                            real_speed[0] = False
                else:
                    if self.rect.y < el.rect.y:
                        if ycor > 0:
                            real_speed[1] = False
                    else:
                        if ycor < 0:
                            real_speed[1] = False
            self.rect.x -= person.real_x_speed - xcor * real_speed[0]
            self.rect.y -= person.real_y_speed - ycor * real_speed[1]
            self.touched = list()
            self.core.condition -= 0.001 / FPS


class Snake(Enemy):
    def __init__(self, width, height, where, chains, speed):
        super().__init__('images/nothing.png', speed / FPS * 60 * chains, height, where, None, 1, speed)
        self.spawn()
        self.forward = 0
        self.chains = list()
        self.colors = list()
        self.num_chains = chains
        self.generated = 0
        for chain in range(chains):
            self.chains.append(
                pg.Rect(self.rect.x + speed * chain * ratio, self.rect.y * ratio, width * ratio, height * ratio))
            self.colors.append((100, random.randint(200, 230), 100))
        self.head = self.chains[-1]
        self.direction = 0

    def reset(self):
        pass

    def motion(self, person):
        global all_borders
        if self.death:
            if self.generated != 0:
                for i in range(self.generated):
                    pg.draw.rect(wd, self.colors[i], self.chains[i])
                    self.chains[i].x -= person.real_x_speed
                    self.chains[i].y -= person.real_y_speed  # исчезновение блоков по одному
                self.generated -= 1
            else:
                enemy[self.where].remove(self)
                all_sprites[self.where].remove(self)
        elif self.generated != self.num_chains - 1:
            self.generated += 1
            if self.where == person.where:
                for i in range(self.generated):
                    pg.draw.rect(wd, self.colors[i], self.chains[i])
                    self.chains[i].x -= person.real_x_speed
                    self.chains[i].y -= person.real_y_speed
        else:
            if self.where == person.where:
                for i in range(self.num_chains):
                    pg.draw.rect(wd, self.colors[i], self.chains[i])  # отрисовка блоков
            if self.forward == 0:
                self.direction += random.randint(-1, 1)
                self.direction %= 4
                self.forward = random.randint(int(FPS / 10), int(FPS / 2))
            match self.direction:
                case 0:
                    self.head.x += self.speed
                case 1:
                    self.head.y -= self.speed  # движения башки в соответствии с направлением
                case 2:
                    self.head.x -= self.speed
                case 3:
                    self.head.y += self.speed
            for border in all_borders[self.where]:
                if self.head.colliderect(border):  # чек соприкосновения
                    self.death = True
            for i in range(len(self.chains) - 1):
                self.chains[i].x = self.chains[i + 1].x  # сдвиг всех блоков за башкой
                self.chains[i].y = self.chains[i + 1].y
                self.chains[i].x -= person.real_x_speed
                self.chains[i].y -= person.real_y_speed
                if self.chains[i].colliderect(person.rect):
                    person.health -= 1
            self.head.x -= person.real_x_speed
            self.head.y -= person.real_y_speed  # движение башки
            self.forward -= 1


class Mole(Enemy):
    def __init__(self, picture, width, height, where, animation, health, speed, radius):
        super().__init__(picture, width, height, where, animation, health, speed)
        self.spawn()
        self.go = False
        self.hide = make_image(r'images/nothing.png', 10, 10)
        self.get = True
        self.destination = [0, 0]
        self.attacks = 3  # TODO: Кроты
        self.circles = list()
        self.radius = radius * ratio

    def motion(self, person):
        global x_y_body, spawn_range
        if self.death:
            self.counter(self.animations['death'], 20)
            if self.count == 0:
                enemy[self.where].remove(self)
                all_sprites[self.where].remove(self)
        elif self.get:
            self.counter(self.animations['get'], 20)
            if self.count == 20 * len(self.animations['get']) - 2:
                self.get = False
        elif self.go:
            dx = x_y_body[self.where].rect.x + self.destination[0] - self.rect.x  # идет к цели
            dy = x_y_body[self.where].rect.y + self.destination[1] - self.rect.y
            length = (dx ** 2 + dy**2) ** 0.5 + 0.1
            self.rect.x += dx / length * self.speed
            self.rect.y += dy / length * self.speed
            print(dx, dy, 'cords')
            if (-20*ratio < dx < 20*ratio) and (-20*ratio < dy < 20*ratio):
                self.go = False
                self.attacks = 3
                self.get = True
                print('hop')
        elif self.attacks:
            self.counter(self.animations['attack'], 15)
            if self.count == int(60*FPS/60):
                self.circles.append(0)
                self.attacks -= 1
        for i in self.circles:
            if i > self.radius:
                self.circles.remove(i)
                if not self.circles:
                    self.go = True
                    self.image = self.hide
                    self.destination[0] = random.randint(spawn_range['main'][0][0], spawn_range['main'][0][1])
                    self.destination[1] = random.randint(spawn_range['main'][1][0], spawn_range['main'][1][1])
                    Queue.append(corpuscle(all_particles, self, [100, 70, 35], 70, 15, where='main'))

        for i in range(len(self.circles)):
            pg.draw.circle(wd, (200, 200, 200), self.rect.center, self.circles[i], int(10 * ratio))
            self.circles[i] += 3 * ratio / FPS * 30
            if (self.rect.x - person.rect.x - person.rect.width / 2) ** 2 + \
                    (self.rect.y - person.rect.y - person.rect.height / 2) ** 2 > ((i - 30) * ratio) ** 2 < (
                    (i + 30) * ratio) ** 2:
                person.health -= 10 / FPS

        super().motion(person)


class Rain(GameSprite):
    def __init__(self, intense, day_):
        super().__init__(r'images/nothing.png', 0, 0, 10, 10, 'main')
        self.day = day_
        self.intense = intense
        self.drops = list()

    def reset(self):
        pass

    def motion(self, person):
        if random.randint(1, int(FPS/20)) == 1:
            if self.day.active:
                for i in range(self.intense):
                    self.drops.append(
                        [pg.Rect((random.randint(int(-100 * ratio), int(820 * ratio)), 0, 5 * ratio, 15 * ratio)),
                         random.randint(2, 10)])

        for i in range(len(self.drops)):
            self.drops[i][0].y += self.drops[i][1] - person.real_y_speed
            self.drops[i][0].x -= person.real_x_speed
            self.drops[i][1] += 0.2
            pg.draw.rect(wd, (100, 100, 200), self.drops[i][0])

        for i in self.drops:
            if i[1] > 14:
                self.drops.remove(i)
                del i


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# gloss: dict, color: list, chel, count: int, size: int, borders_x: list = (-30, 30),
#               borders_y: list = (-30, 0),
#               scattering: int = 20, add: tuple = (0, 0), differ: int = 5, where=None, array: list = None
# # # # # # # # # # # # # # # # # Предметы # # # # # # # # # # # # # # # # # # # #
water = Item(r'images/items/bottle.png', 60, 'Бутылка воды',
             ['Интересное явление, как', 'частичку ненастной стихии', 'можно сохранить в бутылке'])

another_water = Item(r'images/items/bottle.png', 60, 'Другая бутылка воды', ['Ниче не поменялось'])

potato = Food(r'images/items/potato.png', 60, 'Картофка', ['То что можно есть', 'Пойдет'], potato_sound)

coal = Item(r'images/items/coal.png', 60, 'Каменный уголь', ['Можно использовать на ТЭЦ'])

active_metal = Item(r'images/items/active_metal.png', 60, 'Активный метал', ['Металл, быстрее ионизируется'])

nonactive_metal = Item(r'images/items/nonactive_metal.png', 60, 'Неактивный метал', ['Металл, медленнее ионизируется'])

hydrochloric_acid = Toxic(r'images/items/HCl.png', 60, 'Соляная кислота',
                          ['Токсична, можно', 'использовать как электролит'], ((150, 200, 100), 30, 30, (-40, 40),
                                                                               (-20, 10), 50, (70, 40), 10))

stone = Item(r'images/items/stone.png', 60, 'Камень', ['Тоже ресурс', 'Источник кремния и', 'даже бумаги'])

'''
battery = Item(r'', 1, 1, 1)

polyethylene = Item(r'', 1, 1, 1)

hydroxide = Item(r'', 1, 1, 1)

arsenic = Item(r'', 1, 1, 1)
'''

# TODO: добавить предметов
# # # # # # # # # # # # # # # # # Крафты  # # # # # # # # # # # # # # # # # # #

craft_list1 = [[None, 'Бутылка воды', None, None, None, None, None, None, None]]
result_list = [another_water]
# TODO: добавить крафтов

# # # # # # # # # # # # # # # Сохранение # # # # # # # # # # # # # # # # #


# def save(person):
#     global enemy, clickable, all_sprites, event_stock
#     # TODO: сохранение всего в JSON
#     world = dict(enemy=dict(snakes=list(), worms=list(), moles=list()),
#                  day=dict(),
#                  with_slots=list()
#                  )
#     for obj in enemy:
#         if isinstance(obj, Mole):
#             world['enemy']['moles'].append(((obj.rect.x - x_y_body[obj.where].rect.x)/ratio,
#                                             (obj.rect.y - x_y_body[obj.where].rect.y)/ratio,
#                                             obj.rect.width/ratio,
#                                             obj.rect.height/ratio,
#                                             obj.where,
#                                             obj.health/FPS,
#                                             obj.speed/ratio,
#                                             obj.radius/ratio))
#         if isinstance(obj, Snake):
#             world['enemy']['snakes'].append(((obj.rect.x - x_y_body[obj.where].rect.x)/ratio,
#                                             (obj.rect.y - x_y_body[obj.where].rect.y)/ratio,
#                                             obj.rect.width/ratio,
#                                             obj.rect.height/ratio,
#                                             obj.where,
#                                             obj.num_chains,
#                                             obj.speed))
#         if isinstance(obj, Worm):
#             world['enemy']['worms'].append(((obj.rect.x - x_y_body[obj.where].rect.x)/ratio,
#                                             (obj.rect.y - x_y_body[obj.where].rect.y)/ratio,
#                                             obj.rect.width/ratio,
#                                             obj.rect.height/ratio
#                                             ))
#     for obj in clickable:
#         if isinstance(obj, WithSlot):
#             current = list()
#             for slot in obj.slots:
#                 if slot.item is not None:
#                     current.append((slot.item.name, slot.number))
#                 else:
#                     current.append(None)
#             world['with_slots'].append((current))
