import discord
from discord.ext import commands
import yaml
import urllib.request
import traceback
import logging
import tracemalloc
from pathlib import Path
import json

from utils import whisper_transcribe as wt, cache_handling as c_handle


class SpeechToText(commands.Cog):
    "Commands for speech to text"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start tracing memory allocations
tracemalloc.start()

# Constants

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    AUDIO_FILE_OGG = config["audio_file"]
    CACHE = Path(config["cache"])
    TOKEN = config["token"]

# Discord Bot Setup
bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())

class ButtonsView(discord.ui.View):
    def __init__(self, message : discord.Message = None):
        super().__init__(timeout=None)
        self.message = message

    @discord.ui.button(label='Show transcription', custom_id="buttons", style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):
        if self.message is None:
            date = interaction.message.created_at
            history = interaction.channel.history(before=date, limit=1)
            async for message in history:
                self.message = message

        #open cache
        with open(Path(__file__).parent / AUDIO_PATH / CACHE, "r") as file:
            cache = json.load(file)
            message = cache[str(self.message.id)]
            text = f"**{message['author']}** said:\n ```{message['content']}```"
            try :
                await interaction.response.send_message(text, ephemeral=True)
            except discord.errors.HTTPException as e:
                logger.error("Error sending message: %s", e)
                await interaction.response.send_message("Error during the transcription", ephemeral=True)

# DISCORD BOT EVENTS
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    #check if message is a voice message
    url = str(message.attachments[0]) if message.attachments else ""
    if url and ".ogg" in url:
        logger.info(f"Voice message URL found: {url}")
        view_message = await message.channel.send("", view=ButtonsView(message), reference = message, mention_author=False)
        try:
            opener = urllib.request.URLopener()
            opener.addheader("User-Agent", "Mozilla/5.0")
            opener.retrieve(url, Path(__file__).parent / AUDIO_PATH / AUDIO_FILE_OGG)
        except Exception as e:
            logger.error("Error retrieving file: %s", e)
            traceback.print_exc()

        #transcription and cache
        output = await wt.transcribe()
        if c_handle.add_to_cache(message.id, view_message.id, message.channel.id, message.author, message.created_at, output) :
            logger.info("Transcription completed")
        else :
            logger.error("Error adding to cache")

@bot.event
async def on_ready():    
    #restores previously created views
    cache = c_handle.get_all_cache()
    if cache is not None:
        logger.info("Restoring views")
        for key in cache :
            audio_msg_id = int(key)
            view_msg_id = int(cache[key]["view_id"])
            channel_id = int(cache[key]["channel_id"])
            audio_msg = await bot.get_channel(channel_id).fetch_message(audio_msg_id)
            bot.add_view(ButtonsView(audio_msg), message_id=view_msg_id)
    
    await bot.change_presence(activity=discord.Game(name="user audio"))
    logger.info("Bot started!")

async def setup():
    bot.add_cog(SpeechToText())

bot.run(TOKEN)