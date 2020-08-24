# -*- coding: utf-8 -*-
import packages
from time import strftime
from dbworker import DB


async def str_num(num, space, unit='m'):
    string = str(num)
    if len(string) < space:
        return ' ' * (space - len(string)) + string
    elif len(string) == space:
        return string
    else:
        number = string[:(len(string)-space)] + unit
        spaces = " " * (space - len(number))
        return spaces + number


async def str_num_2(num, space, unit="..."):
    string = str(num)
    if len(string) < space + 3:
        return string + ' ' * ((space + 3) - len(string))
    elif len(string) == space + 3:
        return string
    else:
        return string[:space] + unit


async def main(player):
    if player.ill <= 0:
        ill = '\- Ты полностью здоров\n'
    else:
        ill = f'\- Ты болеешь, до конца\nболезни: {player.ill//60} ч\.\n'
    if player.drug <= 0:
        med = ''
    else:
        med = f'\- Действует лекарство\n'
    if player.health <= 0:
        hp = '\- Ты присмерти\!\n'
    else:
        hp = ''
    if player.exploring is None:
        exp = ''
    else:
        exp = f'\- Ты на прогулке\n'
    if player.hunger > 0:
        hungry = ''
    else:
        hungry = '\- Ты голодаешь\n'
    if player.thirst > 0:
        thirst = ''
    else:
        thirst = '\- Тебя мучает жажда\n'
    return f'*{player.nickname}*\n`' \
           f'Уровень:    {await str_num(player.level, 6)}ℹ️\n' \
           f'Опыт:    {await str_num(player.experience, 5, "k")}/{await str_num(await player.need_exp(), 3, "k")}⭐️\n' \
           f'Тип:       {await str_num(await player.level_type(), 9)}\n' \
           f'Время:      {strftime("%H:%M:%S")}\n' \
           f'Голод:      {await str_num(player.hunger, 6)}🍽\n' \
           f'Жажда:      {await str_num(player.thirst, 6)}💦\n' \
           f'Здоровье:   {await str_num(player.health, 6)}♥️`\n\n' \
           f'_{ill}{med}{hp}{hungry}{thirst}{exp}_'


async def outside(exp):
    stocks = await packages.WORLD.show()
    equipment = ''
    masked = ""
    hands = ""
    if exp.exploring is None:
        exploring = ''
        if packages.db.get_info(exp.id)['masked'] is True:
            equipment = "Снаряжение: "
            masked = '- Маска\n'
        if packages.db.get_info(exp.id)['washed_hands'] is True:
            equipment = "Снаряжение:\n"
            hands = '- Помытые руки\n'
    else:
        exploring = f'Идёт прогулка.\nОсталось времени: {exp.exploring} мин.'

    return f'*А на улице:*\n`' \
           f'Шанс на заражение:{await str_num(round(await packages.WORLD.infection() * 100, 2), 6)}` _%_\n`' \
           f'Мировые запасы:   {await str_num(stocks["stocks"], 6)}📦\n\n' \
           f'В наличии масок:  {await str_num(exp.masks, 6)}😷\n' \
           f'Твои шансы:       {await str_num(round(await exp.your_chance() * 100, 2), 6)}` _%_\n`' \
           f'{exploring}{equipment}{masked}{hands}`'

world_info = '*На улице не все так светло, да радужно\.*\n' \
             '\- Каждое исследование проходит _от 10 до 20 минут_ и сопровождается ' \
             'шансом заразится с получением определенного количества мировых запасов, которые ты можешь найти\.\n' \
             '\- Исследовать ты можешь только будучи здоровым, или приняв лекарство\. Опыт начисляется за каждую ' \
             'вылазку с успешным нахождением чего\-нибудь и равняется времени за её прохождения\.\n' \
             '\- Шанс заразиться зависит от процента игроков на прогулке от всех зарегистрированных игроков в боте\.' \
             'Те, которые болеют, повышают шанс на заражение\. Шанс не может _превышать 90 и быть меньше 1\-го %_\.\n' \
             '\- Количество запасов зависит от численности всех пользователей бота\. В среднем, _75 на каждого_\. ' \
             'Если мировых запасов меньше суммы минимальных на каждого, к ним прибавляется новая партия на ' \
             'следующий реальный день\.'


async def storage(your):
    stayhomezero = ''
    if your.stayhome == 0:
        stayhomezero = 'Отсчёт пойдёт со второго\nуровня'
    return f'*Твоё хранилище:*\n`' \
           f'Тип:{await str_num(await your.storage_type(), 21)}\n' \
           f'Совокупность:     {await str_num(your.sum_storage, 6)}📦\n\n' \
           f'Туалетная бумага: {await str_num(your.paper, 6)}🧻\n' \
           f'Продовольствия:   {await str_num(your.foods, 6)}🍖\n' \
           f'Количество воды:  {await str_num(your.water, 6)}💧\n' \
           f'Медикаментов:     {await str_num(your.medicines, 6)}💉\n' \
           f'Количество масок: {await str_num(your.masks, 6)}😷\n' \
           f'Кол-во лекарств:  {await str_num(your.drugs, 6)}💊\n\n' \
           f'Времени дома:     {await str_num(your.stayhome, 6)}🕑\n' \
           f'{stayhomezero}\n`'


store_1 = "*Добро пожаловать в Пандемический Магаз\!*"
store_2 = "_Здесь ты можешь затариться нужным добром:_"

MONO = "`"
smile = "🔅"


async def statistics_bot():
    return f'*Это раздел статистики\.*\n\nВсего пользователей:  {DB.show_users_count()}\n'


async def statistics_storage():
    show = DB.top_storage()

    text = '*📦Наибольшие запасы:*\n' + MONO  + "\n"
    for i in show:

        text += f"{smile}{await str_num_2(i[0], 6)}{await str_num_2(i[1], 12)}\n"
    return text + MONO


async def statistics_stayhome():
    show = DB.top_stayhome()
    text = '*🕑Наидольше дома:*\n' + MONO + "\n"
    for i in show:
        text += f"{smile}{await str_num_2(i[0], 6)}{await str_num_2(i[1], 12)}\n"
    return text + MONO


async def lucker():
    return "*Лаки Дайс\!*\nЗдесь ты можешь выиграть определённое количество запасов, бросив свой кубик\!\n" \
           "Стоимость возможности получения приза: 100🧻\n\n" \
           "_Такие награды:_\n\n" \
           "`Номер 1:\n" \
           "Нет награды\n" \
           "Номер 2:\n🧻15   🍖1  💧1  💉1  😷0 💊0\n" \
           "Номер 3:\n🧻30  🍖1  💧1  💉1  😷0 💊0\n" \
           "Номер 4:\n🧻60  🍖3  💧3  💉3  😷1 💊0\n" \
           "Номер 5:\n🧻100  🍖5  💧5  💉5  😷1 💊1\n" \
           "Номер 6:\n🧻150 🍖10 💧10 💉8  😷2 💊2\n`\n" \
           "_Бросай кубик и проверь свою удачу\!\n" \
           "\(Чтобы бросить кубик отправь 🎲\)_"
