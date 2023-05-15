import sqlite3, json

con = None
cur = None


def init_database():
    global cur, con
    con = sqlite3.connect("data.db")
    cur = con.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS events (name, time, location, owner, participants)"
    )
    cur.execute("CREATE TABLE IF NOT EXISTS calendar (discord_id, token)")
    con.commit()

    return True


def addevent(name, time, location, owner, participants):
    owner = str(owner)
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    result = cur.fetchone()
    if result:
        return False
    cur.execute(
        "INSERT INTO events (name, time, location, owner, participants) VALUES (?, ?, ?, ?, ?)",
        (name, time, location, owner, participants),
    )
    con.commit()
    return True


def removeevent(name, user):
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    owner = cur.fetchone()[3]
    if user != owner:
        return False
    cur.execute("DELETE FROM events WHERE name = ?", (name,))
    con.commit()
    return True


def modifyevent(name, time, location, participants, owner):
    cur.execute(
        "UPDATE events SET time = ?, location = ?, participants = ? WHERE name = ? AND owner = ?",
        (time, location, participants, name, owner),
    )
    con.commit()
    return True


def getevents():
    cur.execute("SELECT * FROM events")
    return cur.fetchall()


def getevent(name, owner):
    cur.execute("SELECT * FROM events WHERE name = ? AND owner = ?", (name, owner))
    return cur.fetchone()


def get_token(discord_id):
    discord_id = int(discord_id)
    cur.execute("SELECT token FROM calendar WHERE discord_id = ?", (discord_id,))
    result = cur.fetchall()
    if result:
        return json.loads(result[0][0])
    return None


def set_token(discord_id, token):
    discord_id = int(discord_id)
    cur.execute(
        "INSERT INTO calendar (discord_id, token) VALUES (?, ?)", (discord_id, token)
    )
    con.commit()
    return True
