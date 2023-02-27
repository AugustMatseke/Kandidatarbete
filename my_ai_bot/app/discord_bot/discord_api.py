from dotenv import load_dotenv
import discord
import os
import asyncio
from app.chatgpt_ai.openai import chatgpt_response

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
messages = []


class MyClient(discord.Client):
    async def on_ready(self):
        print("Successfully logged in as: ", self.user)

    async def on_message(self, message):
        print(message.content)
        if message.author == self.user:
            return
        command, user_message = None, None
        
        print("Waiting for message")
        await fetchMessages(message)
        print("Message fetched")

        for  text in ['/join', '/Join']:
            if message.content.startswith(text):
                command=message.content.split(' ')[0]
                user_message=message.content.replace(text, '')
                print(command,user_message)

            if command == '/join' or command == '/Join':
                ##TODO joina ett event
                print("Work in progress")

    
async def fetchMessages(message):
    print("About to insert in list")
    messages.insert(len(messages), message.content)  # Dont save the entire message ( a lot of info )
    print("Message inserted in list")                # Maybe map name and message?

    if len(messages) > 5:
        print(messages)
        messages.clear()
            
            
 
            


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)