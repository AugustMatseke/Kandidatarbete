from app.discord_bot.discord_api import client

# get nickname from discord id
def get_nickname(discord_id):
    for member in client.get_all_members():
        if member.id == discord_id:
            return member.nick
    return None