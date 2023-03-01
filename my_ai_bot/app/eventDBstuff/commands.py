import discord
import db

# This is a set of the names of all events in the database.
events = set()

def addevent(interaction: discord.Interaction, name: str, time: str, location: str):
    global events
    if name in events:
        return False
    db.addevent(name, time, location, str(interaction.user.id))
    events.add(name)
    return True

def removeevent(interaction: discord.Interaction, name: str):
    global events
    if name not in events:
        return False
    if db.removeevent(name, str(interaction.user.id)):
        events.remove(name)
        return True
    return False

def modifyevent(interaction: discord.Interaction, name: str, time: str, location: str):
    if name not in events:
        return False
    db.modifyevent(name, time, location, str(interaction.user.id))
    return True

def joinevent(interaction: discord.Interaction, name: str):
    if name not in events:
        return False
    return db.joinevent(name, str(interaction.user.id))

def leaveevent(interaction: discord.Interaction, name: str):
    if name not in events:
        return False
    return db.leaveevent(name, str(interaction.user.id))

def getevents():
    return events
