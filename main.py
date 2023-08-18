from assets import *


location_generator('main', [50, 650], [50, 650])

location_generator('workshop', [0, 700], [0, 700])

location_generator('core_location', [0, 700], [0, 700])

inventory = Inventory(r'images/person_stuff/pre_inventory.png', 50, 50,
                      225, 250, 2, 3, 20, 20, r'images/person_stuff/slot.png', 60)

kwark = PlayerGetReady(r'images/person_stuff/person_new.png',
                       315, 200, 70, 100, 5, inventory, person_animations, 10, 10)

core = CampCore(r'images/objects/core.png', 200, -100, 200, 200, 'core_location',
                r'images/person_stuff/pre_inventory.png', 300, 50, 300, 300, inventory)


grey_box_1 = GameSprite('images/location/grey_box.png', -100, -400, 700, 700, 'workshop')
grey_box = GameSprite('images/location/grey_box.png', 0, 0, 700, 700, 'main')

# барьеры
border1 = ForBorders(0, 0, 700, 20, 'main')
border2 = ForBorders(0, 0, 20, 700, 'main')
border3 = ForBorders(700, 0, 10, 700, 'main')
border4 = ForBorders(0, 700, 700, 20, 'main')

border1w = ForBorders(-100, -400, 700, 20, 'workshop')
border2w = ForBorders(-100, -400, 20, 700, 'workshop')
border3w = ForBorders(600, -400, 20, 700, 'workshop')
border4w = ForBorders(-100, 300, 700, 20, 'workshop')
# порталы
main_workshop = Portal(50, 200, 'main', 450, 100, 'workshop')

workshop_core = Portal(200, -400, 'workshop', 350, 450, 'core_location')

inventory.slots[0].item = hydrochloric_acid
inventory.slots[0].number = 5


chest = WithSlot(r'images/objects/chest.png', 0, 0, 90, 60, 'main', r'images/person_stuff/pre_inventory.png',
                 300, 50, 225, 150, 2, 3, 20, 20, r'images/person_stuff/slot.png', 60, inventory)
chest.slots[0].item = Skin(r'images/items/skin_water_proof.png', 60, 'Дождевик', ['Спасает от дождя'],
                           water_proof_animations, take_off_on_sound)
chest.slots[0].number = 1

chest1 = WithSlot(r'images/objects/chest.png', 500, 0, 90, 60, 'main', r'images/person_stuff/pre_inventory.png',
                  300, 50, 225, 150, 2, 3, 20, 20, r'images/person_stuff/slot.png', 60, inventory)

table = CraftTable(r'images/objects/crafting_table.png', 200, 50, 70, 70, 'main',
                   r'images/person_stuff/pre_inventory.png', 300, 50, 300, 250, 3, 3, 20, 20,
                   r'images/person_stuff/slot.png', 60, inventory, craft_list1, result_list, 220, 80)

reader = Reader(r'images/objects/reader.png', 600, 50, 100, 100, 'main', r'images/person_stuff/pre_inventory.png',
                300, 50, 400, 300, inventory, 20, 20)

reader.interface.make_performance(reader_scripts[0].pop(0))
reader.interface.make_performance(reader_scripts[1].pop(0))
green_house = GreenHouse(r'images/objects/green_house.png', 200, 600, 100, 50, 'main',
                         r'images/objects/green_house_.png', 300, 50, 375, 300, inventory, potato)
insects = Insect(green_house)

camp_chp = CHP(r'images/objects/CHP.png', 0, 400, 100, 100, 'main',
               r'images/objects/CHP_.png', 300, 50, 300, 300, inventory, coal, core)

sender = Sender(r'images/objects/sender.png', 300, 50, 100, 80, 'main',
                r'images/person_stuff/pre_inventory.png', 300, 50, 300, 300, inventory)
mine_items = {'active_metal': active_metal, 'nonactive_metal': nonactive_metal, 'stone': stone, 'coal': coal}
camp_mine = Mine(r'images/objects/mine.png', 600, 300, 80, 160, 'main',
                 r'images/person_stuff/pre_inventory.png', 300, 50, 300, 300, inventory, mine_items)
check = CampCheck(core, kwark, sender,  camp_chp)
day_event = Day(20, core, [sender, camp_mine], reader, kwark, windows)
night_event = Night(20)
rave = RatRave(10, 2, core)
# rain = Rain(3, day_event)
x_y_body['main'] = chest
x_y_body['workshop'] = grey_box_1
while check.active:
    wd.fill((50, 50, 50))
    # чек ивентов
    for event in pg.event.get():
        if event.type == pg.QUIT:
            check.active = False
        kwark.control(event)
        inventory.shift(event)
    kwark.collusion()
    # отображение
    reset_all(all_sprites[kwark.where], kwark)
    kwark.reset()
    # инвентарь и кликабельные объекты
    for obj in clickable[kwark.where]:
        obj.analysis(kwark)
    blit_particles(all_particles[kwark.where], kwark)
    if inventory.open:
        inventory.show()
    # частицы
    create_particles(Queue)
    blit_particles(None_particles, kwark)
    for game_event in event_stock:
        if game_event.active:
            game_event.action()
        else:
            game_event.check()
    check_sounds()
    if guess(2):
        print(kwark.health)
    if guess(2):
        print('atmosphere', core.atmosphere)
        print('cond', core.condition)
        print(camp_chp.duration)
    pg.display.update()
    cl.tick(FPS)
