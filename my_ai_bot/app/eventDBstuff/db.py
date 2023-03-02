import sqlite3

con = None
cur = None


def init_database():
    global cur, con
    con = sqlite3.connect("events.db")
    cur = con.cursor()
    return True


def addevent(name, time, location, owner):
    owner = str(owner)
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    result = cur.fetchone()
    if result:
        return False
    cur.execute("INSERT INTO events (name, time, location, owner, participants) VALUES (?, ?, ?, ?, ?)",
                (name, time, location, owner, owner))
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


def modifyevent(name, time, location, user):
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    owner = cur.fetchone()[3]
    if str(user) != owner:
        return False
    cur.execute("UPDATE events SET time = ?, location = ? WHERE name = ?",
                (time, location, name))
    con.commit()
    return True


def joinevent(name, user):
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    participants = cur.fetchone()[4]
    if user in participants.split(", "):
        return False
    participants = participants + ", " + user
    cur.execute("UPDATE events SET participants = ? WHERE name = ?",
                (participants, name))
    con.commit()
    return True


def leaveevent(name, user):
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    participants = cur.fetchone()[4]
    if user not in participants.split(", "):
        return False
    participants = participants.replace(", " + user, "")
    cur.execute("UPDATE events SET participants = ? WHERE name = ?",
                (participants, name))
    con.commit()
    return True


def getevents():
    cur.execute("SELECT name FROM events")
    return cur.fetchall()


def getevent(name):
    cur.execute("SELECT * FROM events WHERE name = ?", (name,))
    return cur.fetchone()
