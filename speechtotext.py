import discord
from discord.ext import commands
import yaml
import urllib.request
import traceback
import logging
import tracemalloc
from pathlib import Path
import json
import threading
import gc

from utils import whisper_transcribe as wt, cache_handling as c_handle
from utils.buttons_view import ButtonsView

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start tracing memory allocations
tracemalloc.start()

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    CACHE = Path(config["cache"])
    TOKEN = config["token"]

class SpeechToText(commands.Bot):

    # DISCORD BOT EVENTS
    async def on_message(self, message: discord.Message):        
        if message.author == self.user:
            return

        #check if message is a voice message
        url = str(message.attachments[0]) if message.attachments else ""
        if url and ".ogg" in url:
            logger.info(f"Voice message URL found: {url}")

            gc.collect() #collect garbage to avoid memory leaks

            view = ButtonsView(message)
            view_message = await message.channel.send("", view=view, reference=message, mention_author=False)

            try:
                #download audio file
                opener = urllib.request.URLopener()
                opener.addheader("User-Agent", "Mozilla/5.0")
                opener.retrieve(url, Path(__file__).parent / AUDIO_PATH / f"voice_message_{str(message.id)}.ogg")
            except Exception as e:
                logger.error("Error retrieving file: %s", e)
                traceback.print_exc()
            
            #add to cache with empty content
            c_handle.add_to_cache(message.id, view_message.id, message.channel.id, message.author, message.created_at, "TRANSCRIPTION IN PROGRESS")

            #transcription and cache
            t = threading.Thread(target=wt.transcribe_and_cache, args=(message, view_message))
            t.start()

    async def on_message_delete(self, message: discord.Message):
        #check if message is a voice message
        url = str(message.attachments[0]) if message.attachments else ""
        if url and ".ogg" in url:
            logger.info(f"Voice message URL found: {url}")
            #remove associated view

            cache_r = json.load(open(Path(__file__).parent / AUDIO_PATH / CACHE, "r"))
            try :
                view_msg_id = int(cache_r[str(message.id)]["view_id"])
                view_message = await message.channel.fetch_message(view_msg_id)
                await view_message.delete()
                c_handle.remove_from_cache(message.id)

            except :
                logger.warning("Cache entry not found for message %s. Either it has already been deleted or the transcription is not finished yet", message.id)

    async def on_ready(self):
        #sync slash commands
        synced = await self.tree.sync() #syncs the slash commands
        logger.info(f"Synced {synced} commands")
        
        await self.change_presence(activity=discord.Game(name="user audio"))
        logger.info("Bot started!")

# BOT
bot = SpeechToText(command_prefix=".", intents=discord.Intents.all())

# SLASH COMMAND
@bot.tree.command(name="transcribe", description="Transcribes a specified audio message in the channel")
async def transcribe(interaction : discord.Interaction, message_id : str) :
    '''Transcribes a specified audio message in the channel'''

    channel = interaction.channel
    message = await channel.fetch_message(int(message_id))
    url = str(message.attachments[0]) if message.attachments else ""

    if url and ".ogg" in url:
        try:
            #download audio file
            opener = urllib.request.URLopener()
            opener.addheader("User-Agent", "Mozilla/5.0")
            opener.retrieve(url, Path(__file__).parent / AUDIO_PATH / f"voice_message_{str(message.id)}.ogg")
        except Exception as e:
            logger.error("Error retrieving file: %s", e)
            traceback.print_exc()
            await interaction.response.send_message("Internal error", ephemeral=True)
            return
        
        await interaction.response.send_message("Transcribing... (do not close this message)", ephemeral=True) #wait msg to avoid timeout

        #transcription
        await wt.transcribe_no_cache(message.id, interaction)

    else :
        await interaction.response.send_message("No audio file found", ephemeral=True)

bot.run(TOKEN)