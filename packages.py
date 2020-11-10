# -*- coding: utf-8 -*-
from dbworker import DB, db
from random import randint, random
from pickle import dump, load

prizes = {2: (15, 1, 1, 1, 0, 0),
          3: (30, 1, 1, 1, 0, 0),
          4: (60, 3, 3, 3, 1, 0),
          5: (100, 5, 5, 5, 1, 1),
          6: (150, 10, 10, 8, 2, 2),
          }


class Chances(object):

    def __init__(self):
        pass

    def paper(self):
        return randint(0, 10)

    def foods(self):
        return randint(0, 10)

    def water(self):
        return randint(0, 10)

    def medicines(self):
        chance = randint(-10, 5)
        if chance < 0:
            return 0
        else:
            return chance

    def masks(self):
        chance = randint(-15, 5)
        if chance < 0:
            return 0
        else:
            return chance

    def drugs(self):
        chance = randint(-15, 3)
        if chance < 0:
            return 0
        else:
            return chance

    async def ill(self, chat_id):
        your_chance = db.get_info(chat_id)['chance_sick']
        fortuna = round(random(), 2)
        if fortuna <= your_chance:
            return randint(60 * 5, 60 * 24)
        else:
            return 0

    async def random_event(self):
        fortuna = random()
        if fortuna <= 0.10:
            if fortuna <= 0.05:
                sub_hp = 10
                return sub_hp, f'\n_\- Прийдя в свой двор, в тебя швырнулась открывшаяся дверь\.\n\-{sub_hp} к здоровью\._'
            else:
                sub_hp = 5
                return sub_hp, f'\n_\- Во время прогулки ты наступил на рулон бумаги, и упал\.\n' \
                               f'Бумага укатилась, а тебе \-{sub_hp} к здоровью\._'
        else:
            return 0, ''


class Player:

    def __init__(self, chat_id):
        self.id = chat_id
        self.info = DB.show_user_info(self.id)
        self.nickname = self.info[2]
        self.paper = self.info[4]
        self.foods = self.info[5]
        self.water = self.info[6]
        self.medicines = self.info[7]
        self.masks = self.info[8]
        self.drugs = self.info[9]
        self.hunger = self.info[10]
        self.thirst = self.info[11]
        self.health = self.info[12]
        self.level = self.info[13]
        self.experience = self.info[14]
        self.drug = self.info[15]
        self.ill = self.info[16]
        self.exploring = self.info[17]
        self.stayhome = self.info[18]
        self.sum_storage = sum((self.paper, self.foods, self.water, self.medicines, self.masks, self.drugs))


class LevelSys(Player):

    def __init__(self, chat_id):
        super().__init__(chat_id)

    async def need_exp(self):
        exp = 150
        need_exp = exp + exp * (self.level - 1)
        return need_exp

    async def level_type(self):
        if self.level < 10:
            return 'Новичок'
        elif 10 <= self.level < 25:
            return 'Дворовой'
        elif 25 <= self.level < 50:
            return 'Уличный'
        else:
            return 'Путешественник'

    async def storage_type(self):

        if self.sum_storage < 250:
            return 'Комната🚪'
        elif 250 <= self.sum_storage < 500:
            return 'Чердак🏡'
        elif 500 <= self.sum_storage < 1000:
            return 'Сарай🏚'
        elif 1000 <= self.sum_storage < 5000:
            return 'Ангар🏠'
        elif 5000 <= self.sum_storage < 10000:
            return 'Склад🏢'
        elif 10000 <= self.sum_storage < 50000:
            return 'Стратегический склад🏭'
        elif 50000 <= self.sum_storage < 250000:
            return 'Частный гос.обьект🏛'
        elif 250000 <= self.sum_storage < 1000000:
            return 'Континент. резерв🏙'
        else:
            return 'Планетный резерв🌍'

    async def new_level(self):
        need_exp = await self.need_exp()
        experience = DB.check_experience(self.id)
        if experience >= need_exp:

            DB.upd_lvl(self.id, self.experience - need_exp)
            return '\n*Новый уровень\!* 🆙 '
        else:
            return ''


class Exploring(LevelSys):

    def __init__(self, chat_id):
        super().__init__(chat_id)

    async def try_go(self):
        if self.ill > 0 and self.drug == 0:
            return f'*Ты не здоров\!*\n_Тебе нужно принять лекарство, чтобы ты мог выходить на улицу\._'
        minutes = randint(10, 20)
        if self.exploring is None:
            DB.set_exploring(self.id, minutes)
            db.equipment(self.id, {"exp": minutes})
            if db.get_info(self.id)['masked'] is True:
                DB.use_mask(self.id)
            return f'*Путешествие началось\!*\n_Это займёт {minutes} минут времени\._'
        else:
            return f'*Ты уже гуляешь по окрестностям\!*' \
                   f'\n_Осталось времени: около \{self.exploring} мин\._'

    async def end(self):
        chances = [
            CHANCES.paper(), CHANCES.foods(), CHANCES.water(), CHANCES.medicines(), CHANCES.masks(), CHANCES.drugs()
        ]
        if self.ill > 0:
            chances = tuple(map(lambda i: i//2, chances))
        illness = await CHANCES.ill(self.id)
        if illness != 0:
            if self.ill > illness:
                illness = self.ill
            sick = f'\n_\- Ты подхватил болезнь\!\nТебе необходимы медикаменты, чтобы поддерживать здоровье\.\n' \
                   f'Болезнь будет длиться где\-то {illness // 60} часов\._'
        else:
            sick = ''
            illness = self.ill
        world = await WORLD.show()
        if world['stocks'] <= 0:
            db.end_exploring(self.id)
            DB.set_exploring(self.id, 'NULL')
            return '*Путешествие окончилось\!*\n_Ты ничего не получил, так как все мировые запасы пустуют\!_'

        if world['stocks'] >= sum(chances):
            await WORLD.upd_stocks((-sum(chances)))
        else:
            x = world['stocks'] / sum(chances)
            chances = tuple(map(lambda i: round(i * x), chances))
            await WORLD.upd_stocks(-world['stocks'])
        event = await CHANCES.random_event()
        DB.end_exploring(self.id, chances[0], chances[1], chances[2], chances[3], chances[4], chances[5], illness,
                         event[0])
        db.end_exploring(self.id)

        return f'*Путешествие окончилось\!*\n_Ты получил:_\n`' \
               f'Бумаги:        {chances[0]}🧻\n' \
               f'Еды:           {chances[1]}🍖\n' \
               f'Воды:          {chances[2]}💧\n' \
               f'Медикаментов:  {chances[3]}💉\n' \
               f'Масок:         {chances[4]}😷\n' \
               f'Лекарств:      {chances[5]}💊\n`' + sick + event[1] + await self.new_level()

    async def your_chance(self):
        you = db.get_info(self.id)
        world = await WORLD.infection()
        if world < you['chance_sick'] or you['chance_sick'] <= 0.00:
            if you['masked'] is True:
                world -= 0.05
            if you['washed_hands'] is True:
                world -= 0.02
            if world <= 0:
                world = 0.01
            db.equipment(self.id, {'chance_sick': world})
            return world
        return you['chance_sick']

    async def masked(self):
        if self.masks > 0:
            upd = db.get_info(self.id)['chance_sick'] - 0.05
            if upd <= 0.01:
                upd = 0.01
            db.equipment(self.id, {'masked': True, 'chance_sick': upd})
            return 'Надета маска.'
        else:
            return 'У тебя нет маски!'

    async def washed_hands(self):
        if self.water >= 5 and self.medicines >= 1:
            DB.wash_hands(self.id)
            upd = db.get_info(self.id)['chance_sick'] - 0.02
            if upd <= 0.01:
                upd = 0.01
            db.equipment(self.id, {'washed_hands': True, 'chance_sick': upd})
            return 'Помыты руки.'
        elif self.water < 5:
            return 'Не хватает воды!'
        else:
            return 'Не хватает медикамента для дезинфекции!'


class Stats(LevelSys):

    def __init__(self, chat_id):
        super().__init__(chat_id)

    async def eat(self):
        count = 10
        if self.hunger < 100 and self.foods > 0:
            if self.hunger > 90:
                count = 100-self.hunger
                DB.eating(self.id, count)
            else:
                DB.eating(self.id)
            return f'*Ты поел вкусной еды\.*\n_\+ {count} к сытости\._'
        elif self.foods <= 0:
            return '_У тебя не хватает еды\!_'
        else:
            return '_Ты не голоден\!_'

    async def drink(self):
        count = 10
        if self.thirst < 100 and self.water > 0:
            if self.thirst > 90:
                count = 100 - self.thirst
                DB.drink(self.id, count)
            else:
                DB.drink(self.id)
            return f'*Ты выпил освежающей воды\.*\n_\+ {count} к твоему водному балансу\._'
        elif self.water <= 0:
            return '_У тебя не хватает воды\!_'
        else:
            return '_Тебе не хочется пить\!_'

    async def heal(self):
        count = 5
        if self.health < 100 and self.medicines > 0:
            if self.health > 95:
                count = 100 - self.health
                DB.heal(self.id, count)
            else:
                DB.heal(self.id)
            return f'*Ты принял медикаменты\.*\n_\+ {count} к здоровью\._'
        elif self.medicines <= 0:
            return '_Нет медикаментов\!_'
        else:
            return '_У тебя здоровье на максимуме\!_'

    async def take_medicine(self):
        if self.drug == 0 and self.drugs > 0 and self.ill > 0:
            DB.take_med(self.id)
            return '*Ты принял лекарство\.*\n_Действие лекарства продлится 2 часа\._'
        elif self.drugs <= 0:
            return '_У тебя нет лекарств\!_'
        elif self.ill == 0:
            return '_Ты здоров\! Нет необходимости в лекарстве\._'
        else:
            return '_Лекарство уже действует\!_'


class Store(LevelSys):

    def __init__(self, chat_id):
        super().__init__(chat_id)

    async def buy_drug(self, price=50):
        if self.paper >= price:
            DB.buy_drug(self.id, price)
            return '_Куплено лекарств\._'
        else:
            return '_Не хватает бумаги\!_'

    async def try_luck(self, value, price=100):
        async def you_gave(chances):
            return f'_Ты получил:_\n`' \
                   f'🧻{chances[0]} 🍖{chances[1]} 💧{chances[2]} 💉{chances[3]} 😷{chances[4]} 💊{chances[5]}\n`'
        if self.paper >= price:
            DB.buy_luck_chance(self.id, price)
            if value == 1:
                return f"*Номер 1*\n_Ты ничего не получил_"
            elif value > 1:
                DB.you_win(self.id, prizes[value])
                return f"*Номер {value}*\n" + await you_gave(prizes[value])
        else:
            return '_Не хватает бумаги для розыгрыша\!_'


class World:

    startpoint = {'normal': 50, 'stocks': 50}

    async def stocks(self): return DB.show_users_count() * randint(50, 100)

    def __init__(self, file='situation.world'):
        self.file = file
        self.max_chance = 0.90
        self.min_chance = 0.05

    async def upd_stocks(self, change_stock):
        stocks = await self.show()
        stocks['stocks'] += change_stock
        if stocks['stocks'] < 0:
            stocks['stocks'] = 0
        with open(self.file, 'wb') as f:
            dump(stocks, f)

    async def show(self):
        try:
            with open(self.file, 'rb') as f:
                return load(f)
        except FileNotFoundError:
            with open(self.file, 'wb') as f:
                dump(self.startpoint, f)
                return self.startpoint

    async def infection(self):
        percent = (DB.who_healthy_and_walk() + DB.who_ill_and_walk()*1.5) / (DB.show_users_count())
        if percent <= 0:
            return self.min_chance
        elif percent > self.max_chance:
            return self.max_chance
        return round(percent, 2)

    async def stocks_everyday(self):
        check = await self.show()
        if (len(db) * 50) > check['stocks']:
            new_stocks = await self.stocks()
            await self.upd_stocks(new_stocks)


WORLD = World()
CHANCES = Chances()

if __name__ == '__main__':
    pass

