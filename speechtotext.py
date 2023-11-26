import discord
from discord.ext import commands
import yaml
import urllib.request
import traceback
from pydub import AudioSegment
import logging
import tracemalloc
import whisper_transcribe as wt


class SpeechToText(commands.Cog):
    "Commands for speech to text"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start tracing memory allocations
tracemalloc.start()

# Constants
AUDIO_FILE_OGG = "voice-message.ogg"
AUDIO_FILE_WAV = "voice-message.wav"

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

token = config["token"]
LANG = config["lang"]

# Discord Bot Setup
bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())

class ButtonsView(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
    @discord.ui.button(label='Show transcription', style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):
        with open("output.txt", "r") as file:
            text = file.read()
            await interaction.response.send_message(text, ephemeral=True)

# CUSTOM FUNCTIONS
def convert_ogg_to_wav(ogg_file: str, wav_file_path: str = None) -> str:
    try:
        audio = AudioSegment.from_ogg(ogg_file)
        audio.export(wav_file_path, format="wav")
        return f"File converted successfully: {wav_file_path}"
    except Exception as e:
        logger.error("Error converting file: %s", e)
        return f"Error converting file: {e}"

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
            opener.retrieve(url, AUDIO_FILE_OGG)
        except Exception as e:
            logger.error("Error retrieving file: %s", e)
            traceback.print_exc()

        convert_ogg_to_wav(AUDIO_FILE_OGG, AUDIO_FILE_WAV)
        output = await wt.transcribe()
        with open("output.txt", "w") as file:
            file.write(output)

@bot.event
async def on_ready():
    logger.info("Bot started!")
    await bot.change_presence(activity=discord.Game(name="user audio"))

async def setup():
    bot.add_cog(SpeechToText())

bot.run(token)