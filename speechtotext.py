import discord
from discord.ext import commands
import yaml
import re

import tracemalloc
tracemalloc.start()


bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())
config = yaml.safe_load(open("config.yaml"))
token = config["token"]
print(config)
print(token)

class myCog(commands.Cog):
    "Bot commands"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        print("Message received")
        # Check if the message is from the bot itself
        if message.author == self.bot.user:
            return

        # Regular expression to match Discord voice message URLs
        voice_msg_pattern = r"https://cdn\.discordapp\.com/attachments/\d+/\d+/voice-message\.ogg"
        
        # Search for voice message URLs in the message content
        voice_msg_urls = re.findall(voice_msg_pattern, message.content)
        if voice_msg_urls:
            for url in voice_msg_urls:
                print(f"Voice message URL found: {url}")

@bot.event
async def on_ready():
    print("Started!")
    await bot.change_presence(activity=discord.Game(name="user audio"))

bot.add_cog(myCog(bot))
bot.run(token)