import sqlite3
import commands

cur = None

def init_database():
    global cur 
    con = sqlite3.connect("events.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM events")
    for a in cur.fetchall():
        commands.events.add(a[0])
