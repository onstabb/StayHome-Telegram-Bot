from aiogram import types
import packages

delete = types.ReplyKeyboardRemove()


async def main():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('На улицу', 'Хранилище')
    key.row('Рейтинги')
    # key.row('Обратная связь')
    return key


async def ratings():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row("Топ хранилищ")
    key.row("Топ времени дома")
    key.row("Главное меню")
    return key


async def outside(exp):
    equip = packages.db.get_info(exp.id)
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='Надесь маску -5%', callback_data='Надеть маску')
    but_2 = types.InlineKeyboardButton(text='Помыть руки -2% ', callback_data='Помыть руки')
    but_3 = types.InlineKeyboardButton(text='Исследовать', callback_data='Исследовать')
    but_4 = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
    but_5 = types.InlineKeyboardButton(text='Информация', callback_data='info')
    if exp.exploring is None:
        if equip['masked'] is False and exp.masks > 0:
            key.add(but_1)
        if (equip['washed_hands'] is False) and (exp.water >= 5) and (exp.medicines > 0):
            key.add(but_2)
    key.add(but_3)
    key.add(but_4, but_5)
    return key


async def storage():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Поесть еды', 'Выпить воды')
    key.row('Лечиться', 'Принять лекарство')
    key.row('Вернуться', 'Магазин')
    return key


async def inl_back(cb='back'):
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(text='Вернуться', callback_data=cb))
    return key


async def store():
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(text='Выбить приз🌟', callback_data='lucker'))
    key.add(types.InlineKeyboardButton(text='Купить лекарство💊 за 50🧻', callback_data='buy drug'))
    key.add(types.InlineKeyboardButton(text='Вернуться', callback_data='back'))
    return key
