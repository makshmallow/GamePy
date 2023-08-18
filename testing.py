from datetime import datetime
from random import randint


# 1
print('\n Задание 1 \n')

ice_cream_stats = {
    'summer': [{
        'name': 'Пломбир',
        'votes': 320
    }, {
        'name': 'Сливочное',
        'votes': 265
    }, {
        'name': 'Молочное',
        'votes': 163
    }, {
        'name': 'Крем-брюле',
        'votes': 90
    }, {
        'name': 'Сорбет',
        'votes': 290
    }],
    'winter': [{
        'name': 'Пломбир',
        'votes': 210
    }, {
        'name': 'Сливочное',
        'votes': 157
    }, {
        'name': 'Молочное',
        'votes': 243
    }, {
        'name': 'Крем-брюле',
        'votes': 254
    }, {
        'name': 'Сорбет',
        'votes': 264
    }]
}
print('3 Самых популярных видов мороженного:')
res = dict()
for ice_cream in ice_cream_stats['summer']:
    res[ice_cream['name']] = ice_cream['votes']

for val in sorted(res.values())[-3:][::-1]:
    for ice_cream in res:
        if res[ice_cream] == val:
            print(f'{ice_cream} - {res[ice_cream]}')
            res.pop(ice_cream)
            break
res = dict()

print('Самое популярное мороженное:')
for season in ['summer', 'winter']:
    for ice_cream in ice_cream_stats[season]:
        if season == 'summer':
            res[ice_cream['name']] = ice_cream['votes']
        else:
            res[ice_cream['name']] += ice_cream['votes']

maximum = sorted(res.values())[-1]
for ice_cream in res:
    if res[ice_cream] == maximum:
        print(f'{ice_cream} - {res[ice_cream]}')
        # нет брейка, вдруг есть такой же

# 2
print('\n Задание 2 \n')

data = {
    'question': ['почему', 'как', 'зачем', 'столько'],
    'animals': {
        'birds': [
            {
                'name': 'грачи',
            },
            {
                'name': 'воробьи',
            },
        ],
        'others': [
            {
                'name': 'кошки'
            },
            {
                'name': 'рыбы'
            },
            {
                'name': 'собаки'
            },
        ],
    },
    'parts': {
        'hands': 'рук',
        'feathers': 'перьев',
        'eyes': 'глаз',
    },
}

print(data['question'][0], data['animals']['birds'][0]['name'], 'не', data['animals']['others'][0]['name'],
      data['animals']['others'][0]['name'][-1], data['question'][2],
      data['animals']['others'][0]['name'][-1] + data['question'][2][-1], data['question'][3],
      data['parts']['feathers'])

# 3
print('\n Задание 3 \n')

for i in range(1, 49, 4):
    for j in range(1, 49):
        for l in range(4):
            print(f'{i + l} × {j} = {(i + l) * j}', end='     ')
        print()

# 4
print('\n Задание 4 \n')

playbill = [
    {
        "name": "Щелкунчик",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": True,
        "ageLimit": 6
    },
    {
        "name": "Сказка о царе Салтане",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": True,
        "ageLimit": 12
    },
    {
        "name": "Ростовское действо",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": False,
        "ageLimit": 12
    },
    {
        "name": "Путеводитель по оркестру. Карнавал животных",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": True,
        "ageLimit": 6
    },
    {
        "name": "Борис Годунов",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": True,
        "ageLimit": 12
    },
    {
        "name": "Чайка",
        "date": datetime.fromtimestamp(randint(1677618000, 1680210000)),
        "isAvailable": False,
        "ageLimit": 16
    },
]
print('Афиша на март:')
for play in playbill:
    if play['isAvailable'] and play['ageLimit'] >= 12:
        print(f'{play["name"]} - {play["date"].strftime("%d")} марта - {play["ageLimit"]}+')

# 5
print('\n Задание 5 \n')

garages = {
    1: {
        'id': 1,
        'name': 'Гараж на улице 1',
        'size': 1
    },
    7: {
        'id': 7,
        'name': 'Подземная парковка',
        'size': 100
    },
    23: {
        'id': 23,
        'name': 'У домика в деревне',
        'size': 2
    },
}

# Машины
cars = [
    {
        'name': 'Желтый Mazda',
        'garageId': 7
    },
    {
        'name': 'Черный Уаз',
        'garageId': 1
    },
    {
        'name': 'Оранжевый Nissan',
        'garageId': 7
    },
]

for car in cars:
    print(f'Машина "{car["name"]}" стоит в "{garages[car["garageId"]]["name"]}"')
# 6
print('\n Задание 6 \n')
pairs = {'а': 'a', 'б': 'b', 'в': 'v',
         'г': 'g', 'д': 'd', 'е': 'e',
         'ё': 'jo', 'ж': 'zh', 'з': 'z',
         'и': 'i', 'й': 'j', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n',
         'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u',
         'ф': 'ph', 'х': 'kh', 'ц': 'c',
         'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
         'ъ': '', 'ы': 'y', 'ь': "'",
         'э': 'e', 'ю': 'yu', 'я': 'ya'}

string = input('Введите строку на кириллице: ')
for letter in pairs:
    string = string.replace(letter, pairs[letter])
    string = string.replace(letter.upper(), pairs[letter].upper())
print(string)

# 7
print('\n Задание 7 \n')
path = input('Введите путь до заметки: ')
with open(path, 'w') as note:
    string_note = input("Введите содержимое заметки: ")
    note.write(string_note + '\n')
print('Успешно сохранено.')

# 8
print('\n Задание 8 \n')
number_1 = float(input('Введите первое число: '))
number_2 = float(input('Введите второе число: '))
operation = input('Выберите операцию(+, -, *, /): ')
print('Результат:', end=' ')
match operation:
    case '+':
        print(number_1 + number_2)
    case '-':
        print(number_1 - number_2)
    case '*':
        print(number_1 * number_2)
    case '/':
        print(number_1 / number_2)

# 9
print('\n Задание 9 \n')
data = [randint(1, 100) for i in range(10)]

print('Максимальное число:', max(data))
print('Минимальное число:', min(data))

# 10
print('\n Задание 10 \n')
past = 0
current = 1
border = int(input('Введите число: '))
print(f'Числа Фибоначчи до {border}:', end=' ')
while past < border:
    print(past, end=' ')
    past, current = current, current+past
print(border)
