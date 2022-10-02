import os
import motor.motor_asyncio
from cogs.mongo import Document
from discord_slash import SlashCommand
from discord.ext.commands import AutoShardedBot
from discord.ext import commands
import discord
import requests
import discordhealthcheck


async def create_thread(self, name, minutes, message):
    token = 'Bot ' + self._state.http.token
    url = f"https://discord.com/api/v9/channels/{self.id}/messages/{message.id}/threads"
    headers = {
        "authorization": token,
        "content-type": "application/json"
    }
    data = {
        "name": name,
        "type": 11,
        "auto_archive_duration": minutes
    }

    return requests.post(url, headers=headers, json=data).json()

discord.TextChannel.create_thread = create_thread

"""discord api connection"""


# replace args.token with "discord-token" if you dont want to run this in pterodactyl
TOKEN = os.getenv('token', None)
MONGO = os.getenv('mongo', None)

if TOKEN == None or TOKEN == "default_token_value":
    raise "token not set!"
if MONGO == None or MONGO == "default_mongo_value":
    raise "database not set!"


# intents = discord.Intents.default()
# Intents.members = True
# bot = commands.Bot(command_prefix='!')
bot = AutoShardedBot(
    fetch_offline_members=False,
    command_prefix="!"
)
# Declares slash commands through the client.
slash = SlashCommand(bot, sync_commands=True,
                     sync_on_cog_reload=True)
discordhealthcheck.start(bot)

bot.load_extension("cogs.matching")
bot.load_extension("cogs.ranking")


@bot.event
async def on_ready():
    print("bot started \n")
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO)
    bot.db = bot.mongo["bfprime"]
    bot.matches = Document(bot.db, 'matches')
    bot.queue = Document(bot.db, 'queue')
    bot.ranking = Document(bot.db, 'ranking')

    print("Initialized Database")
    print(f"Connected on {len(bot.guilds)} server(s)")


# dont give a error if a command doesn't exist


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            color=0xe74c3c, description="Your not allowed to use this command")
        await ctx.send(embed=embed)
    raise error
# run the bot
bot.run(TOKEN)
