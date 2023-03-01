from dotenv import load_dotenv
import discord
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
        #print("Waiting for message")
        await fetchMessages(message)
        #print("Message fetched")

    
async def fetchMessages(message):
    #print("About to insert in list")
    MyClient.conversation+= (message.author.name + ": " + message.content + ". ")
    MyClient.i += 1
    if MyClient.i == 2:
        bot_response = chatgpt_response(prompt = "Find the event, location, time, date and participants in the following conversation, and if only one thing can be found, return N/A: " + MyClient.conversation)
        eventHandler(bot_response)
        await message.channel.send(f"Answer: {bot_response}")
        MyClient.i = 0
        #print(MyClient.conversation)
        MyClient.conversation = ""
    #print(MyClient.conversation)    


# Returns a conversation of multiple users in the form of a string


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

# get nickname from discord id
def get_nickname(discord_id):
    for member in client.get_all_members():
        if member.id == discord_id:
            return member.nick
    return None

# get discord id from nickname
def get_discord_id(nickname):
    for member in client.get_all_members():
        if member.name == nickname:
            return member.id
    return None
            
def eventHandler(bot_response):
    first_user = MyClient.conversation.splitlines()[0].split(": ")[0]

    response = bot_response.splitlines()[2:]
    print(response)
    event = response[0].split(": ")[1].strip()
    if event == "NA":
        return False
    location = response[1].split(": ")[1].strip()
    time = response[2].split(": ")[1].strip()
    date = response[3].split(": ")[1].strip()
    participants = response[4].split(": ")[1].strip()
    if " and " in participants:
        participants = participants.split(" and ")

    user_id = MyClient.participants[0]

    if event not in commands.events:
        print(user_id, event, time, location)
        commands.addevent(user_id, event, time, location)
        commands.events.add(event)

