import discord
from discord.ext import commands
import yaml
import urllib.request
import traceback
import logging
import tracemalloc
import whisper_transcribe as wt
from pathlib import Path


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
    TOKEN = config["token"]

# Discord Bot Setup
bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())

class ButtonsView(discord.ui.View):
    def __init__(self, message=None):
        super().__init__(timeout=None)
        self.message = message
    @discord.ui.button(label='Show transcription', custom_id="buttons", style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):
        with open("output.txt", "r") as file:
            text = file.read()
            await interaction.response.send_message(text, ephemeral=True)

# DISCORD BOT EVENTS
@bot.event
async def on_message(message: discord.Message):
    logger.info("Message received")
    if message.author == bot.user:
        return

    url = str(message.attachments[0]) if message.attachments else ""
    if url and ".ogg" in url:
        logger.info(f"Voice message URL found: {url}")
        await message.channel.send("", view=ButtonsView(message))
        try:
            opener = urllib.request.URLopener()
            opener.addheader("User-Agent", "Mozilla/5.0")
            opener.retrieve(url, Path(__file__).parent / AUDIO_PATH / AUDIO_FILE_OGG)
        except Exception as e:
            logger.error("Error retrieving file: %s", e)
            traceback.print_exc()

        output = await wt.transcribe()
        with open("output.txt", "w") as file:
            file.write(output)

@bot.event
async def on_ready():
    logger.info("Bot started!")
    bot.add_view(ButtonsView())
    await bot.change_presence(activity=discord.Game(name="user audio"))

async def setup():
    bot.add_cog(SpeechToText())

bot.run(TOKEN)