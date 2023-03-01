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
    i = 0
    BOT_CHANNEL_ID = 1075004933134356480
    async def on_ready(self):
        print("Successfully logged in as: ", self.user)

    async def on_message(self, message):
        print(message.content)
        if message.author == self.user:
            return
        if message.channel.id != MyClient.BOT_CHANNEL_ID:
            return
        command, user_message = None, None
        
        #print("Waiting for message")
        await fetchMessages(message)
        #print("Message fetched")

        for  text in ['/join', '/Join']:
            if message.content.startswith(text):
                command=message.content.split(' ')[0]
                user_message=message.content.replace(text, '')
                print(command,user_message)

            if command == '/join' or command == '/Join':
                ##TODO joina ett event
                print("Work in progress")

    
async def fetchMessages(message):
    #print("About to insert in list")
    MyClient.conversation+= (message.author.name + ": " + message.content + ". ")
    MyClient.i += 1
    if MyClient.i == 8:
        bot_response = chatgpt_response(prompt = "Find the event, location, time, date and participants in the following conversation: " + MyClient.conversation)
        await message.channel.send(f"Answer: {bot_response}")
        MyClient.i = 0
        #print(MyClient.conversation)
        MyClient.conversation = ""
    #print(MyClient.conversation)    
            


# Returns a conversation of multiple users in the form of a string


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

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