import json

import discord
from discord import app_commands

import commands
import db

config = json.load(open("config.json"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

@tree.command(name="addevent", description="Add an event", guild=discord.Object(id=1064844577820921886), )
async def addevent(interaction: discord.Interaction, name: str, time: str, location: str):
    if commands.addevent(interaction, name, time, location):
        await interaction.response.send_message("Event added.")
    else:
        await interaction.response.send_message("Event already exists.")

@tree.command(name="removeevent", description="Delete an event", guild=discord.Object(id=1064844577820921886), )
async def removeevent(interaction: discord.Interaction, name: str):
    if commands.removeevent(interaction, name):
        await interaction.response.send_message("Event removed.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you do not own it.)")

@tree.command(name="modifyevent", description="Modify an event", guild=discord.Object(id=1064844577820921886), )
async def modifyevent(interaction: discord.Interaction, name: str, time: str, location: str):
    if commands.modifyevent(interaction, name, time, location):
        await interaction.response.send_message("Event modified.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you do not own it.)")

@tree.command(name="joinevent", description="Join an event", guild=discord.Object(id=1064844577820921886), )
async def joinevent(interaction: discord.Interaction, name: str):
    if commands.joinevent(interaction, name):
        await interaction.response.send_message("Joined event.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you are already in it.)")

@tree.command(name="leaveevent", description="Leave an event", guild=discord.Object(id=1064844577820921886), )
async def leaveevent(interaction: discord.Interaction, name: str):
    if commands.leaveevent(interaction, name):
        await interaction.response.send_message("Left event.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you are not in it.)")

@tree.command(name="getevents", description="Get all events", guild=discord.Object(id=1064844577820921886), )
async def getevents(interaction: discord.Interaction):
    await interaction.response.send_message(str(commands.getevents()))

@client.event
async def on_ready():
    # print("Registering commands...")
    # await tree.sync(guild=discord.Object(id=1064844577820921886))
    print("Initializing database...")
    db.init_database()
    print("Loading events...")
    commands.events = set(event[0] for event in db.getevents())
    print(commands.events)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for events."))
    print(f"We have logged in as {client.user}")
    print("Ready.")

client.run(config["bot_token"])
