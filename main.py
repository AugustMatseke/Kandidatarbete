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
    
    if message.content.startswith("!event"):
        await message.channel.send("'detected event' " + message.content[6:])

@tree.command(name="addevent", description="Add an event")
async def addevent(interaction: discord.Interaction, name: str, time: str, location: str):
    pass
@tree.command(name="removeevent", description="Delete an event")
async def removeevent(interaction: discord.Interaction, name: str):
    pass
@tree.command(name="modifyevent", description="Modify an event")
async def modifyevent(interaction: discord.Interaction, name: str, time: str, location: str):
    pass
@tree.command(name="joinevent", description="Join an event")
async def joinevent(interaction: discord.Interaction, name: str):
    pass
@tree.command(name="leaveevent", description="Leave an event")
async def leaveevent(interaction: discord.Interaction, name: str):
    pass

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1064844577820921886))
    print("Initializing database...")
    db.init_database()
    print(commands.events)
    print(f"We have logged in as {client.user}")

client.run(config["bot_token"])
