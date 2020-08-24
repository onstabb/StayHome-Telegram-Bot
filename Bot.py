from aiogram import Bot, Dispatcher, executor, types
import config
from dbworker import DB, db
from asyncio import sleep
import packages
import TEXTS
import KEY
from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()

bot = Bot(token=config.TOKEN, parse_mode='markdownv2')
dp = Dispatcher(bot)


async def time_eat_and_drink():
    hungry = DB.hunger_and_thirsted()
    max_mes = 30-1
    if hungry:
        for i in enumerate(hungry):
            if i[1].count(0) == 2:
                await bot.send_message(i[1][0], 'Ты голоден и хочешь пить\! Используй еду и воду из хранилища\.')

            elif i[1][1] == 0:
                await bot.send_message(i[1][0], 'Ты проголодался\! Используй еду из своего хранилища, пока не замучал голод\.')

            elif i[1][2] == 0:
                await bot.send_message(i[1][0], 'Ты хочешь пить\! Выпей воды из своего хранилища, пока не замучала жажда\.')

            if i[0] == max_mes:
                max_mes += 30
                await sleep(1)
    dead = tuple(DB.dead())
    if dead:
        for i in dead:
            await bot.send_message(i, '*Здоровье обнулилось до нуля\!*\nПонижен уровень, отнято по 100 с каждого запаса '
                                      'хранилища\.')


async def time_flow():
    messages = 0
    max_mes = 30
    time_is_now = DB.time_flow()
    if time_is_now:
        for user in time_is_now:
            exp_end = packages.Exploring(user[0])
            messages += 1
            await bot.send_message(user[0], await exp_end.end(), reply_markup=await KEY.inl_back(cb='home'))
            if messages == max_mes:
                max_mes += 30
                await sleep(1)
#
#
scheduler.add_job(time_flow, 'cron', minute='*')
scheduler.add_job(time_eat_and_drink, 'cron', minute='15, 30, 45, 0')
scheduler.add_job(packages.WORLD.stocks_everyday, trigger='cron', day='*')
scheduler.start()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if DB.return_id(message.chat.id) != message.chat.id:
        db.add_user(message.chat.id)
        DB.add(message.chat.id, message.date)
        await message.answer('*Добро пожаловать в Карантин Бот\!*'
                             'Данный бот представляет собой симулятор карантина, где твоя задача получить '
                             'как можно больше ограниченое кол\-во припасов для выживания\!'
                             'Чтобы получать припасы, тебе нужно выходить на улицу, населенной вирусами\!')
        await sleep(3)
        await message.answer('Для начала введи свой никнейм\.\nДоступны символы кириллицы, латиницы и цифры\.\n'
                             'Максимальная длина ника \- 12, минимальная 4\.')

    else:
        name = DB.return_name(message.chat.id)
        if name is None:
            await message.answer('Приветствую\! По\-моему, ты должен был ввести свой никнейм\. Введи его сейчас\!\n'
                                 '_Доступны символы кириллицы, латиницы и цифры\n'
                                 'Максимальная длина ника \- 12, минимальная 4\._')
        else:
            await message.answer(f'Привет, {name}\!', reply_markup=await KEY.main())


@dp.message_handler(lambda message: DB.return_name(message.chat.id) is None)
async def registration(message: types.Message):
    if message.text.isalnum() is False or (4 >= len(message.text) > 12):
        await message.answer('Такой никнейм не пойдет\.')
    elif DB.check_name(message.text) is not None:
        await message.answer('Это имя уже занято\!')
    else:
        await message.answer('Отлично\!\nЧто ж, удачи в выживании\!')
        DB.registered(message.chat.id, message.text)
        await sleep(1)
        await main(message)


@dp.message_handler(lambda message: message.chat.id == config.ADMIN, commands='set_commands')
async def cmd_set_commands(message: types.Message):
    commands = [types.BotCommand(command="/refresh", description="Обновить бота, если что-то не так, или не то")]
    await bot.set_my_commands(commands)
    await message.answer("Команды настроены\.")


@dp.message_handler(lambda message: db.check(message.chat.id) in range(3), content_types=["dice"])
async def play_dice(message):
    if DB.check_exploring(message.chat.id) is not None:
        await message.answer('Ты гуляешь\! Играть можно только дома\.')
    else:
        dice = await bot.send_dice(message.chat.id)
        await sleep(5)
        if dice.dice.value > message.dice.value:
            await message.answer('Моя взяла\!')
        elif dice.dice.value == message.dice.value:
            await message.answer('Ну ничья\.')
        else:
            await message.answer('Ты выиграл\!')


@dp.message_handler(commands=['refresh'])
async def main(message: types.Message):

    db.user_set(message.chat.id, 0)
    player = packages.LevelSys(message.chat.id)
    await message.answer(await TEXTS.main(player), reply_markup=await KEY.main())


@dp.callback_query_handler(lambda c: c.data == 'home')
async def home(c: types.CallbackQuery):
    player = packages.LevelSys(c.message.chat.id)
    await c.message.edit_text('Домой\!')
    await sleep(1)
    await c.message.answer(await TEXTS.main(player), reply_markup=await KEY.main())
    db.user_set(c.message.chat.id, 0)


@dp.message_handler(lambda message: db.check(message.chat.id) == 0)
async def main_menu(message: types.Message):
    if message.text == 'На улицу':
        exp = packages.Exploring(message.chat.id)
        await message.answer('Выходим\.\.\.', reply_markup=KEY.delete)
        await sleep(1)
        await message.answer(await TEXTS.outside(exp),
                             reply_markup=await KEY.outside(exp))
        db.user_set(message.chat.id, 1)
    elif message.text == 'Хранилище':
        await storage(message)
    elif message.text == 'test' and message.chat.id == config.ADMIN:
        await packages.WORLD.upd_stocks(-80)
    elif message.text == 'Рейтинги':

        await message.answer(await TEXTS.statistics_bot(), reply_markup=await KEY.ratings())
    elif message.text == "Топ хранилищ":
        await message.answer(await TEXTS.statistics_storage())
    elif message.text == "Топ времени дома":
        await message.answer(await TEXTS.statistics_stayhome())
    elif message.text == "Главное меню":
        await main(message)


@dp.callback_query_handler(lambda c: db.check(c.message.chat.id) == 1)
async def c_outside(c: types.CallbackQuery):
    exp = packages.Exploring(c.message.chat.id)
    if c.data == 'back':
        await c.message.edit_text('Вернёмся')
        player = packages.LevelSys(c.message.chat.id)
        await c.message.answer(await TEXTS.main(player), reply_markup=await KEY.main())
        db.user_set(c.message.chat.id, 0)
    elif c.data == 'Исследовать':
        await c.message.edit_text(await exp.try_go(), reply_markup=await KEY.inl_back())
    elif c.data == 'Надеть маску':
        await bot.answer_callback_query(c.id, await exp.masked())
        await c.message.edit_text(await TEXTS.outside(exp),
                                  reply_markup=await KEY.outside(exp))
    elif c.data == 'Помыть руки':
        await bot.answer_callback_query(c.id, await exp.washed_hands())
        await c.message.edit_text(await TEXTS.outside(exp),
                                  reply_markup=await KEY.outside(exp))
    elif c.data == 'info':
        await c.message.edit_text(TEXTS.world_info, reply_markup=await KEY.inl_back('Назад'))
    elif c.data == 'Назад':
        await bot.answer_callback_query(c.id)
        await c.message.edit_text(await TEXTS.outside(exp),
                                  reply_markup=await KEY.outside(exp))


@dp.message_handler(lambda message: db.check(message.chat.id) == 2)
async def storage(message: types.Message):
    stats = packages.Stats(message.chat.id)
    if message.text == "Хранилище":
        db.user_set(message.chat.id, 2)
        return await message.answer(await TEXTS.storage(stats), reply_markup=await KEY.storage())

    if message.text == 'Вернуться':
        await message.answer(await TEXTS.main(stats), reply_markup=await KEY.main())
        db.user_set(message.chat.id, 0)
    elif message.text == 'Магазин':
        await message.answer(TEXTS.store_1, reply_markup=KEY.delete)
        await sleep(1)
        await message.answer(TEXTS.store_2, reply_markup=await KEY.store())
    elif message.text == 'Выпить воды':
        await message.answer(await stats.drink())
    elif message.text == 'Поесть еды':
        await message.answer(await stats.eat())
    elif message.text == 'Лечиться':
        await message.answer(await stats.heal())
    elif message.text == 'Принять лекарство':
        await message.answer(await stats.take_medicine())


@dp.callback_query_handler(lambda c: db.check(c.message.chat.id) in (2, 3))
async def store(c: types.CallbackQuery):
    you = packages.Store(c.message.chat.id)
    if c.data == "buy drug":
        if you.paper >= 50:
            await c.message.edit_text(await you.buy_drug())
            await c.message.edit_reply_markup(reply_markup=await KEY.store())
        else:
            await c.message.edit_text(await you.buy_drug(), reply_markup=await KEY.inl_back())
    elif c.data == "lucker":
        await c.message.edit_text(await TEXTS.lucker(), reply_markup=await KEY.inl_back())
        db.user_set(c.message.chat.id, 3)
    elif c.data == 'back':
        await c.message.edit_text('Вернёмся')
        await sleep(0.5)
        await c.message.answer(await TEXTS.storage(you), reply_markup=await KEY.storage())
        db.user_set(c.message.chat.id, 2)


@dp.message_handler(lambda message: db.check(message.chat.id) == 3, content_types=["dice"])
async def lucky_dice(message):
    you = packages.Store(message.chat.id)
    await sleep(5)
    await message.answer(await you.try_luck(message.dice.value), reply_markup=await KEY.inl_back())


async def begin(*args):
    await bot.send_message(config.ADMIN, 'Запустился\!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=begin)
