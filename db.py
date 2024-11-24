import sqlite3
from random import shuffle

def con_open():
    global con, cur
    con = sqlite3.connect('db.db')
    cur = con.cursor()

def con_close():
    global con
    con.commit()
    con.close()

def get_all_alive():
    con_open()
    sql = "SELECT username FROM players WHERE dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    data2 = [user[0] for user in data]
    # for user in data:
    #     u = user[0]
    #     data2.append(u)
    con_close()
    return data2



def set_roles(players):
    game_roles = ['citezen']*players
    
    for i in range(int(players*0.3)):       
        game_roles[i] = 'mafia'
    game_roles[i+1] = 'sherif'
    shuffle(game_roles)
    print(game_roles)
    con_open()
    cur.execute("SELECT player_id FROM players")
    ids = [id[0] for id in cur.fetchall()]
    for id, role in zip(ids, game_roles):
        cur.execute(f"UPDATE players SET role='{role}'" + \
                      f"WHERE player_id = {id}")
    con_close()

def add_player(id, name):
    con_open()
    sql = f"""INSERT INTO players (player_id, username) 
             VALUES ({id}, '{name}')"""
    cur.execute(sql)    
    con_close()

def players_count():
    con_open()
    sql = "SELECT player_id FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con_close()
    return len(data)

def get_mafia():
    con_open()
    sql = """SELECT username 
             FROM players 
             WHERE role = 'mafia'"""
    cur.execute(sql)
    data = cur.fetchall()
    data2 = [user[0] for user in data]   
    con_close() 
    return data2

def reset(dead = False):
    con_open()
    sql = """UPDATE players 
             SET role='', mafia_vote='', 
                 citizen_vote='', voted=''
             """
    if dead:
        sql += ", dead=0"
    cur.execute(sql)
    con_close()  
    
def get_roles():
    con_open()
    sql = """SELECT player_id, role 
             FROM players"""
    cur.execute(sql)
    data = cur.fetchall()      
    con_close() 
    return data



def vote(type, username, player_id):
    # type = 'mafia_vote, citizen_vote'
    con_open()
    cur.execute(
        f"""SELECT username 
          FROM players 
          WHERE player_id = {player_id} and dead = 0 and voted = 0""")
    can_vote = cur.fetchone()
    if can_vote:  # если список не пустой, значит пользователь существует
        cur.execute(
            f"UPDATE players SET {type} = {type} + 1" + \
            f"WHERE username = '{username}' ")
        cur.execute(
            f"""UPDATE players SET voted = 1 
                WHERE player_id = '{player_id}' """)
        con_close()
        return True
    con_close()
    return False


def mafia_kill():
    con_open()
    # Выбираем за кого больше всего голосов отдала мафия
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    # Выбираем кол-во игроков за мафию, которых не убили
    cur.execute(
        f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    # Максимальное кол-во голосов мафии должно быть равно кол-ву мафии
    if max_votes == mafia_alive:
        # Получаем имя пользователя, за которого проголосовали
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        # Делаем update БД, ставим, что игрок мертв
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        
    con.close()
    return username_killed


def citizens_kill():
    con_open()
    # Выбираем большинство голосов горожан
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    # Выбираем кол-во живых горожан
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'
    # Проверяем, что только 1 человек с макс. кол-вом голосов
    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")     
    con_close()
    return username_killed

def check_winner():
    con_open()
    cur.execute("SELECT COUNT(*) FROM players WHERE role = 'mafia' and dead = 0")
    mafia_alive = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM players WHERE role != 'mafia' and dead = 0")
    citizens_alive = cur.fetchone()[0]
    if mafia_alive >= citizens_alive:
        return 'Мафия'
    if mafia_alive == 0:
        return 'Горожане'


def del_all():
    con_open()
    cur.execute("DELETE FROM players")
    con_close()

del_all()
# add_player(12310, 'user17')
# print(players_count())
# reset()
# set_role(players_count())

# print(get_mafia())

print(get_roles())


#привет