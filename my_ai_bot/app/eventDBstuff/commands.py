import discord
import app.eventDBstuff.db as db

# This is a set of the names of all events in the database.
events = set()

def addevent(user_id, name: str, time: str, location: str):
    global events
    if name in events:
        return False
    db.addevent(name, time, location, str(user_id))
    events.add(name)
    return True

def removeevent(user_id, name: str):
    global events
    if name not in events:
        return False
    if db.removeevent(name, str(user_id)):
        events.remove(name)
        return True
    return False

def modifyevent(user_id, name: str, time: str, location: str):
    if name not in events:
        return False
    db.modifyevent(name, time, location, str(user_id))
    return True

def joinevent(user_id, name: str):
    if name not in events:
        return False
    return db.joinevent(name, str(user_id))

def leaveevent(user_id, name: str):
    if name not in events:
        return False
    return db.leaveevent(name, str(user_id))

def getevents():
    return events
