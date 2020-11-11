from sqlite3 import connect
import config
from tinydb import TinyDB, Query
from threading import RLock

lock = RLock()


def document(chat_id): return {
    "chat_id": chat_id,
    "state": 0,
    "meme": 0,
    "exp": 0,
    "masked": False,
    "washed_hands": False,
    "chance_sick": 0.00,
    "blocked": False,
}


states = {'main': 0, 'outside': 1, 'storage': 2}


class States(TinyDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Query = Query()

    def add_user(self, chat_id):
        self.insert(document(chat_id))

    def get_info(self, chat_id):
        try:
            return self.search(self.Query.chat_id == chat_id)[0]
        except IndexError:
            return None

    def check(self, chat_id):
        return self.get_info(chat_id).get('state')

    def user_set(self, chat_id, state):
        self.update({'state': state}, self.Query.chat_id == chat_id)

    def exploring(self, chat_id, equipment):
        self.update(equipment, self.Query.chat_id == chat_id)

    def end_exploring(self, chat_id):
        self.update({"exp": 0, "masked": False, "washed_hands": False, "chance_sick": 0.00},
                    self.Query.chat_id == chat_id)

    def equipment(self, chat_id, equip):
        self.update(equip, self.Query.chat_id == chat_id)


class Connector:

    def __init__(self, storage):
        self.conn = connect(storage, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self):
        with self.conn and lock:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS \"users\" (
	\"id\"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	\"chat_id\"	INTEGER(12) NOT NULL UNIQUE,
	\"name\"	VARCHAR(10) NOT NULL UNIQUE,
	\"date\"	TIMESTAMP NOT NULL,
	\"paper\"	INTEGER NOT NULL DEFAULT 0,
	\"foods\"	INTEGER NOT NULL DEFAULT 0,
	\"water\"	INTEGER NOT NULL DEFAULT 0,
	\"medicines\"	INTEGER NOT NULL DEFAULT 0,
	\"masks\"	INTEGER NOT NULL DEFAULT 0,
	\"drugs\"	INTEGER NOT NULL DEFAULT 0,
	\"hunger\"	INTEGER NOT NULL DEFAULT 100,
	\"thirst\"	INTEGER NOT NULL DEFAULT 100,
	\"health\"	INTEGER NOT NULL DEFAULT 100,
	\"level\"	INTEGER NOT NULL DEFAULT 1,
	\"exp\"	INTEGER NOT NULL DEFAULT 0,
	\"drug\"	INTEGER NOT NULL DEFAULT 0,
	\"ill\"	INTEGER NOT NULL DEFAULT 0,
	\"exploring\"	INTEGER,
	\"stayhome\"	INTEGER NOT NULL DEFAULT 0
)""")
            self.conn.commit()


class Global(Connector):

    unreg_name = ""

    def select(self, what, where='1=1'):
        return f'SELECT {what} FROM users WHERE {where}'

    def update(self, what, where='1=1'):
        return f'UPDATE users SET {what} WHERE {where}'

    def __init__(self, storage):
        super().__init__(storage)

    def add(self, chat_id, date):
        with self.conn and lock:
            self.cursor.execute('INSERT INTO users(chat_id, name, date, paper, foods, water, medicines, masks, drugs) '
                                'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (chat_id, self.unreg_name, date, 5, 5, 5, 5, 2, 1))
            self.conn.commit()

    def registered(self, chat_id, name):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET name = "{name}" WHERE chat_id = {chat_id}')
            self.conn.commit()

    def return_id(self, chat_id):
        with self.conn and lock:
            show = self.cursor.execute(f'SELECT chat_id FROM users WHERE chat_id = {chat_id}').fetchone()
            if show is None:
                return show
            else:
                return show[0]

    def check_name(self, name):
        with self.conn and lock:
            show = self.cursor.execute(f'SELECT name FROM users WHERE name = "{name}"').fetchone()
            if show is None:
                return show
            else:
                return show[0]

    def return_name(self, chat_id):
        with self.conn and lock:
            show = self.cursor.execute(f'SELECT name FROM users WHERE chat_id = {chat_id}').fetchone()
            if show is None:
                return show
            else:
                return show[0]

    def show_users_count(self):
        with self.conn and lock:
            return self.cursor.execute('SELECT MAX(id) FROM users').fetchone()[0]

    def show_users(self):
        with self.conn and lock:
            return self.cursor.execute('SELECT chat_id FROM users').fetchone()

    def show_user_info(self, chat_id):
        with self.conn and lock:
            return self.cursor.execute(f'SELECT * FROM users WHERE chat_id = {chat_id}').fetchone()


class GameAbilities(Global):

    def __init__(self, storage):
        super().__init__(storage)

    def storage(self, chat_id):
        with self.conn and lock:
            return self.cursor.execute(
                f'SELECT paper, foods, water, medicines, masks, drugs, stayhome FROM users WHERE chat_id = {chat_id}'
            ).fetchone()

    def stats(self, chat_id):
        with self.conn and lock:
            return self.cursor.execute(
                f'SELECT name, level, exp, hunger, thirst, health, ill, exploring, drug '
                f'FROM users WHERE chat_id = {chat_id}'
            ).fetchone()

    def end_exploring(self, chat_id, paper, foods, water, medicines, masks, drugs, ill, health=0):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET paper = paper+{paper}, foods = foods+{foods}, water = water+{water}'
                                f', medicines = medicines+{medicines}, masks = masks+{masks}, drugs = drugs+{drugs}, '
                                f'exp = exp + {db.get_info(chat_id)["exp"]}, exploring = NULL, ill = {ill},'
                                f'health = health-{health} '
                                f'WHERE chat_id = {chat_id}')
            self.conn.commit()

    def check_count_explorers(self):
        with self.conn and lock:
            return self.cursor.execute(self.select('COUNT(exploring)', 'exploring IS NOT NULL')).fetchone()[0]

    def wash_hands(self, chat_id):
        with self.conn and lock:
            self.cursor.execute(
                f'UPDATE users SET water = water-5, medicines = medicines - 1 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def use_mask(self, chat_id):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET masks = masks-1 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def set_ill(self, chat_id, go_set):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET ill = {go_set} WHERE chat_id = {chat_id}')
            self.conn.commit()

    def check_ill(self, chat_id):
        with self.conn and lock:
            return self.cursor.execute(f'SELECT ill FROM users WHERE chat_id = {chat_id}').fetchone()[0]

    def who_ill_and_walk(self):
        with self.conn and lock:
            return self.cursor.execute(
                f'SELECT COUNT(exploring) FROM users WHERE ill > 0 AND exploring IS NOT NULL').fetchone()[0]

    def who_healthy_and_walk(self):
        with self.conn and lock:
            return self.cursor.execute(
                f'SELECT COUNT(exploring) FROM users WHERE ill <= 0 AND exploring IS NOT NULL').fetchone()[0]

    def set_exploring(self, chat_id, time):
        with self.conn:
            self.cursor.execute(f'UPDATE users SET exploring = {time} WHERE chat_id = {chat_id}')
            self.conn.commit()

    def check_exploring(self, chat_id):
        with self.conn:
            show = self.cursor.execute(f'SELECT exploring FROM users WHERE chat_id = {chat_id}').fetchone()
            if show is None:
                return show
            else:
                return show[0]

    def time_flow(self):
        with self.conn:
            self.cursor.execute('UPDATE users SET exploring = exploring - 1 WHERE exploring > 0')
            self.cursor.execute(f'UPDATE users SET stayhome = stayhome+1 WHERE level > 1 AND exploring IS NOT NULL')
            self.cursor.execute('UPDATE users SET drug = drug - 1 WHERE drug > 0')
            self.cursor.execute('UPDATE users SET ill = ill - 1 WHERE ill > 0')
            self.conn.commit()
            return self.cursor.execute(
                f'SELECT chat_id, exploring FROM users WHERE exploring <= 0'
            ).fetchall()

    def hunger_and_thirsted(self):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET hunger = hunger-1, thirst = thirst-1 WHERE level > 1')
            self.cursor.execute(
                f'UPDATE users SET hunger = hunger-1, thirst = thirst-1, health = health-1 WHERE ill > 0 AND drug <= 0')
            self.cursor.execute(f'UPDATE users SET health = health-1 WHERE hunger <= 0 OR thirst <= 0')
            self.conn.commit()
            return self.cursor.execute(
                f'SELECT chat_id, hunger, thirst FROM users WHERE hunger <= 0 OR thirst <= 0'
            ).fetchall()

    def dead(self):
        with self.conn and lock:
            show = self.cursor.execute(f'SELECT * FROM users WHERE health <= 0').fetchall()
            if show:
                for i in show:
                    paper = i[5] - 100 if i[5] - 100 >= 0 else 5
                    foods = i[6] - 100 if i[6] - 100 >= 0 else 5
                    water = i[7] - 100 if i[7] - 100 >= 0 else 5
                    medicines = i[8] - 100 if i[8] - 100 >= 0 else 5
                    masks = i[9] - 100 if i[9] - 100 >= 0 else 0
                    level = i[13] - 1 if i[13] - 1 > 1 else 1
                    stayhome = i[18] - 5000 if i[18] - 5000 >= 0 else 0
                    self.cursor.execute(
                        f'UPDATE users '
                        f'SET paper = {paper}, foods = {foods}, water = {water}, medicines = {medicines}, '
                        f'masks = {masks}, hunger = 100, thirst = 100, health = 100, level = {level}, ill = 0, '
                        f'stayhome = stayhome - {stayhome} '
                        f'WHERE chat_id = {i[1]}'
                    )
                    db.end_exploring(i[1])
                    self.conn.commit()
                    yield i[1]

    def eating(self, chat_id, count=10):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET hunger = hunger+{count}, foods = foods-1 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def drink(self, chat_id, count=10):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET thirst = thirst+{count}, water = water-1 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def heal(self, chat_id, count=5):
        with self.conn and lock:
            self.cursor.execute(
                f'UPDATE users SET health = health+{count}, medicines=medicines-1 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def take_med(self, chat_id):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET drugs = drugs - 1, drug = 120 WHERE chat_id = {chat_id}')
            self.conn.commit()

    def upd_lvl(self, chat_id, exp=0):
        with self.conn and lock:
            self.cursor.execute(f'UPDATE users SET level = level + 1, exp = {exp} WHERE chat_id = {chat_id}')
            self.conn.commit()

    def check_experience(self, chat_id):
        with self.conn:
            return self.cursor.execute(f'SELECT exp FROM users WHERE chat_id = {chat_id}').fetchone()[0]


class Store(GameAbilities):
    def __init__(self, storage):
        super().__init__(storage)

    def buy_drug(self, chat_id, price=50):
        with self.conn and lock:
            self.cursor.execute(
                f'UPDATE users SET drugs = drugs + 1, paper = paper - {price} WHERE chat_id = {chat_id}')
            self.conn.commit()

    def buy_luck_chance(self, chat_id, price=100):
        with self.conn and lock:
            self.cursor.execute(
                f'UPDATE users SET paper = paper - {price} WHERE chat_id = {chat_id}')
            self.conn.commit()

    def you_win(self, chat_id, prizes):
        with self.conn and lock:
            self.cursor.execute(
                f'UPDATE users SET paper = paper+{prizes[0]}, foods = foods+{prizes[1]}, water = water+{prizes[2]}'
                f', medicines = medicines+{prizes[3]}, masks = masks+{prizes[4]}, drugs = drugs+{prizes[5]} '
                f'WHERE chat_id = {chat_id}'
            )
            self.conn.commit()


class Statistics(Store):

    def __init__(self, storage):
        super().__init__(storage)

    def show_stayhome(self, chat_id):
        with self.conn and lock:
            return self.cursor.execute(f'SELECT stayhome FROM users WHERE chat_id = {chat_id}').fetchone()[0]

    def top_stayhome(self):
        with self.conn and lock:
            return self.cursor.execute('SELECT stayhome, name FROM users ORDER BY stayhome DESC LIMIT 10').fetchall()

    def top_storage(self):
        with self.conn and lock:
            return sorted(self.cursor.execute('SELECT paper+foods+water+medicines+masks+drugs, name '
                                              'FROM users').fetchall(), reverse=True)[:10]


DB = Statistics(config.STORAGE)
db = States(config.STATES)

if __name__ == '__main__':
    DB.create_table()
    print(DB.top_storage())
