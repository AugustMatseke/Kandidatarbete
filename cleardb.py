import sqlite3
con = sqlite3.connect("data.db")
cur = con.cursor()
cur.execute("DELETE FROM events")
cur.execute("DELETE FROM calendar")
con.commit()
