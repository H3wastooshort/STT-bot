import discord
from discord import client
from discord.ext import commands
import asyncio
import yaml

bot = commands.Bot(command_prefix = ".", description= "Speech to text",case_insensitive=1,intents=discord.Intents.all())
config = yaml.safe_load(open("config.yaml"))
token = config["token"]
print(config)
print(token)

class myCog(commands.Cog) :
    "Bot commands"

@bot.event
async def on_ready() :
    print("Started !")
    await bot.change_presence(activity=discord.Game(name="user audio"))

bot.add_cog(myCog())
bot.run(token)