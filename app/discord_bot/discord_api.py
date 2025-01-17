import datetime
import os
from queue import Queue
from sys import stderr

import discord
from discord import app_commands
from dotenv import load_dotenv

import app.discord_bot.commands as commands
import app.db_interface.db as db
from app.chatgpt_ai.openai import *
from app.gcal.gcal_api import do_auth

from time import sleep
import traceback

today = datetime.datetime.now().strftime('%H:%M %d/%m/%Y')

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEND")

CONVERSATION_LENGTH_LIMIT = 15


class MyClient(discord.Client):
    conversation = Queue()
    participants = []
    BOT_CHANNEL_ID = 1075004933134356480

    async def on_ready(self):
        # print("Registering commands...")
        # await tree.sync(guild=discord.Object(id=1064844577820921886))
        print("Initializing database...")
        db.init_database()
        print("Loading events...")
        commands.init_events()
        print(*commands.events, sep="\n")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for events."))
        print(f"We have logged in as {client.user}")
        print("Ready.")

    async def on_message(self, message: discord.Message):
        if message.author == self.user or message.author.bot:
            return

        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.channel.id == message.author.dm_channel.id:
            if message.content == "auth calendar":
                await do_auth(message)

        if message.channel.id != MyClient.BOT_CHANNEL_ID:
            return

        self.participants.append(message.author.id)
        await fetchMessages(message)


async def fetchMessages(message: discord.Message):
    if not message.content.startswith("#"):
        # MyClient.conversation.put(message.author.name + ": " + message.content + ". ")
        MyClient.conversation.put(str(message.author.id) + ": " + message.content)
    while MyClient.conversation.qsize() > CONVERSATION_LENGTH_LIMIT:
        MyClient.conversation.get()
    text = "\n".join(MyClient.conversation.queue)
    # prompt = f"Find all the events, meetings or other gatherings in the following conversation. Find their names, locations, times, dates and participants. For each detected event, meeting or gathering, return a list with the name, location, time and date, and participants in that specific order. Do not label the values, just list them with semicolons in between. Return N/A for values that cannot be identified. If the event name is N/A or no participants are found, skip the entire event. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {datetime.datetime.now().strftime('%H:%M, %d %b %Y')}:\n"
    prompt = f"Check if the following conversation is about an event, meeting or gathering. Specifically, check if it contains an event that can be written in a calendar. If it does, answer yes, otherwise answer no. The conversation is as follows:\n"
    bot_response = None
    event = False
    while True:
        try:
            bot_response = chatgpt_response(prompt + text)
            # print(bot_response)
            if "yes" in bot_response.lower():
                event = True
            break
        except:
            print(traceback.format_exc(), file=stderr)
            print(text, file=stderr)
            print("retrying...", file=stderr)
            sleep(1)

    if event:
        prompt = f"The following conversation is about an event. Find the event, location, time, date, and participants. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {today}. Return N/A for any values that aren't found. Do not write anything other than the results found. The conversation is as follows:\n"
        bot_response = None
        while True:
            try:
                bot_response = chatgpt_response(prompt + text)
                break
            except:
                print(traceback.format_exc(), file=stderr)
                print(text, file=stderr)
                print("retrying...", file=stderr)
                sleep(1)

        try:
            result = eventHandler(bot_response)
            # print(result)
            if set([*result[2]]) != set([*"N/A "]):
                await commands.addevent(*result)
        except:
            print(traceback.format_exc())


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)


async def get_name(discord_id):
    return (await client.fetch_user(int(discord_id))).name


def eventHandler(bot_response):
    response = bot_response.strip().splitlines()
    event = response[0].strip()
    if event.startswith("Event"):
        event = event.split(":")[1].strip()
    if event == "N/A":
        return []

    location = response[1].strip()
    if location.startswith("Location"):
        location = location.split(":")[1].strip()

    time = response[2].strip()
    if time.startswith("Time"):
        time = time.split(":", maxsplit=1)[1].strip()
    # if time == "N/A":
    #     return []

    date = response[3].strip()
    if date.startswith("Date"):
        date = date.split(":")[1].strip()
    # if date == "N/A":
    #     return []

    time += " " + date

    participants = response[4].strip()
    if participants.startswith("Participants"):
        participants = participants.split(":")[1].strip()
    if " and " in participants:
        participants = participants.replace(" and ", ", ")
    if ", " in participants:
        participants = participants.split(", ")

    return [event, location, time, participants[0], participants]



tree = app_commands.CommandTree(client)


@tree.command(
    name="addevent",
    description="Add an event",
    guild=discord.Object(id=1064844577820921886),
)
async def addevent(
    interaction: discord.Interaction, name: str, time: str, location: str
):
    if commands.addevent(interaction.user.id, name, time, location):
        await interaction.response.send_message("Event added.")
    else:
        await interaction.response.send_message("Event already exists.")


@tree.command(
    name="removeevent",
    description="Delete an event",
    guild=discord.Object(id=1064844577820921886),
)
async def removeevent(interaction: discord.Interaction, name: str):
    if commands.removeevent(str(interaction.user.id), name):
        await interaction.response.send_message("Event removed.")
    else:
        await interaction.response.send_message(
            "Event does not exist. (Or you do not own it.)"
        )


@tree.command(
    name="modifyevent",
    description="Modify an event",
    guild=discord.Object(id=1064844577820921886),
)
async def modifyevent(
    interaction: discord.Interaction, name: str, time: str, location: str
):
    if commands.modifyevent(str(interaction.user.id), name, time, location):
        await interaction.response.send_message("Event modified.")
    else:
        await interaction.response.send_message(
            "Event does not exist. (Or you do not own it.)"
        )


@tree.command(
    name="joinevent",
    description="Join an event",
    guild=discord.Object(id=1064844577820921886),
)
async def joinevent(interaction: discord.Interaction, name: str, owner: str):
    if commands.joinevent(str(interaction.user.id), name, owner):
        await interaction.response.send_message("Joined event.")
    else:
        await interaction.response.send_message(
            "Event does not exist. (Or you are already in it.)"
        )


@tree.command(
    name="leaveevent",
    description="Leave an event",
    guild=discord.Object(id=1064844577820921886),
)
async def leaveevent(interaction: discord.Interaction, name: str, owner: str):
    if commands.leaveevent(str(interaction.user.id), name, owner):
        await interaction.response.send_message("Left event.")
    else:
        await interaction.response.send_message(
            "Event does not exist. (Or you are not in it.)"
        )


@tree.command(
    name="getevents",
    description="Get all events",
    guild=discord.Object(id=1064844577820921886),
)
async def getevents(interaction: discord.Interaction):
    if len(commands.getevents()) == 0:
        await interaction.response.send_message("No events.")
    else:
        await interaction.response.send_message(", ".join(commands.getevents()))


@tree.command(
    name="details",
    description="Get an event",
    guild=discord.Object(id=1064844577820921886),
)
async def details(interaction: discord.Interaction, name: str):
    name, time, location, owner, participants = commands.getevent(name)
    owner = await get_name(owner)
    participants = [str(await get_name(participant)) for participant in participants]
    embed = discord.Embed(title=name)
    embed.add_field(name="Time", value=time, inline=True)
    embed.add_field(name="Location", value=location, inline=False)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(
        name="Participants",
        value=", ".join([owner] + participants)(participants),
        inline=False,
    )
    await interaction.response.send_message(embed=embed)
