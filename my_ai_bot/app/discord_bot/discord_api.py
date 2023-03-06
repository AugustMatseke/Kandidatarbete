from dotenv import load_dotenv
import discord
from discord import app_commands
import os
import asyncio
from app.chatgpt_ai.openai import chatgpt_response

import app.eventDBstuff.db as db
import app.eventDBstuff.commands as commands

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')


class MyClient(discord.Client):
    conversation = ""
    participants = []
    i = 0
    BOT_CHANNEL_ID = 1075004933134356480

    async def on_ready(self):
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

    async def on_message(self, message: discord.Message):
        print(message.content)
        if message.author == self.user:
            return
        if message.channel.id != MyClient.BOT_CHANNEL_ID:
            return
        if message.author.bot:
            return

        self.participants.append(message.author.id)
        # print("Waiting for message")
        await fetchMessages(message)
        # print("Message fetched")


async def fetchMessages(message):
    MyClient.conversation += (message.author.name + ": " + message.content + ". ")
    MyClient.i += 1
    if MyClient.i == 2:
        bot_response = chatgpt_response(
            prompt="Find the event, location, time, date and participants in the following conversation, and if only one thing can be found, return N/A: " + MyClient.conversation)
        await eventHandler(bot_response)
        await message.channel.send(f"Answer: {bot_response}")
        MyClient.i = 0
        MyClient.conversation = ""


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)


async def get_name(discord_id):
    return (await client.fetch_user(int(discord_id))).name


async def eventHandler(bot_response):
    response = bot_response.splitlines()[2:]
    event = response[0].split(": ")[1].strip()
    if event == "NA":
        return False
    location = response[1].split(": ")[1].strip()
    time = response[2].split(": ")[1].strip()
    date = response[3].split(": ")[1].strip()
    names = response[4].split(": ")[1].strip()
    if " and " in names:
        names = names.split(" and ")

    user_id = MyClient.participants[0]
    ids = list(set(MyClient.participants))
    print(names)

    participants = []
    for id in ids:
        if await get_name(id) in names:
            participants.append(str(id))

    if event not in commands.events:
        print("detected event", [event, user_id,
              time + date, location, participants])

        commands.addevent(user_id, event, time + ";" + date, location, participants)
        commands.events.add(event)


tree = app_commands.CommandTree(client)


@tree.command(name="addevent", description="Add an event", guild=discord.Object(id=1064844577820921886), )
async def addevent(interaction: discord.Interaction, name: str, time: str, location: str):
    if commands.addevent(interaction.user.id, name, time, location):
        await interaction.response.send_message("Event added.")
    else:
        await interaction.response.send_message("Event already exists.")


@tree.command(name="removeevent", description="Delete an event", guild=discord.Object(id=1064844577820921886), )
async def removeevent(interaction: discord.Interaction, name: str):
    if commands.removeevent(interaction.user.id, name):
        await interaction.response.send_message("Event removed.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you do not own it.)")


@tree.command(name="modifyevent", description="Modify an event", guild=discord.Object(id=1064844577820921886), )
async def modifyevent(interaction: discord.Interaction, name: str, time: str, location: str):
    if commands.modifyevent(interaction.user.id, name, time, location):
        await interaction.response.send_message("Event modified.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you do not own it.)")


@tree.command(name="joinevent", description="Join an event", guild=discord.Object(id=1064844577820921886), )
async def joinevent(interaction: discord.Interaction, name: str):
    if commands.joinevent(interaction.user.id, name):
        await interaction.response.send_message("Joined event.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you are already in it.)")


@tree.command(name="leaveevent", description="Leave an event", guild=discord.Object(id=1064844577820921886), )
async def leaveevent(interaction: discord.Interaction, name: str):
    if commands.leaveevent(interaction.user.id, name):
        await interaction.response.send_message("Left event.")
    else:
        await interaction.response.send_message("Event does not exist. (Or you are not in it.)")


@tree.command(name="getevents", description="Get all events", guild=discord.Object(id=1064844577820921886), )
async def getevents(interaction: discord.Interaction):
    if len(commands.getevents()) == 0:
        await interaction.response.send_message("No events.")
    else:
        await interaction.response.send_message(", ".join(commands.getevents()))


@tree.command(name="details", description="Get an event", guild=discord.Object(id=1064844577820921886), )
async def details(interaction: discord.Interaction, name: str):
    name, time, location, owner, participants = commands.getevent(name)
    owner = await get_name(owner)
    participants = [str(await get_name(participant)) for participant in participants]
    embed = discord.Embed(title=name)
    embed.add_field(name="Time", value=time, inline=True)
    embed.add_field(name="Location", value=location, inline=False)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Participants", value= ", ".join([owner] + participants)(
        participants), inline=False)
    await interaction.response.send_message(embed=embed)
