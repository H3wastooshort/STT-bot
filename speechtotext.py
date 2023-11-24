import discord
from discord.ext import commands
import yaml
import urllib.request
import traceback
from pydub import AudioSegment
import requests
import time
import logging
import tracemalloc


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
API_KEY_ID = config["KeyId"]
API_KEY_SECRET = config["KeySecret"]
RESULT_TYPE = 4
headers = {"keyId": API_KEY_ID, "keySecret": API_KEY_SECRET}
LANG = "fr"

# Discord Bot Setup
bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())

class ButtonsView(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
    @discord.ui.button(label='Show transcription', style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):
        await interaction.response.send_message(self.message, ephemeral=True)

# CUSTOM FUNCTIONS

def create(wav_file_path: str) -> str:
    create_data = {"lang": LANG}
    files = {}
    create_url = "https://api.speechflow.io/asr/file/v1/create"

    try:
        if wav_file_path.startswith('http'):
            create_data['remotePath'] = wav_file_path
            logger.info('Submitting a remote file')
            response = requests.post(create_url, data=create_data, headers=headers)
        else:
            logger.info('Submitting a local file')
            create_url += "?lang=" + LANG
            files['file'] = open(wav_file_path, "rb")
            response = requests.post(create_url, headers=headers, files=files)

        response.raise_for_status()
        create_result = response.json()
        logger.info(create_result)

        if create_result["code"] == 10000:
            return create_result["taskId"]
        else:
            logger.error("Create error: %s", create_result["msg"])
            return ""

    except requests.RequestException as e:
        logger.error("Create request failed: %s", e)
        return ""

def query(task_id: str) -> dict:
    query_url = f"https://api.speechflow.io/asr/file/v1/query?taskId={task_id}&resultType={RESULT_TYPE}"
    logger.info('Querying transcription result')

    while True:
        try:
            response = requests.get(query_url, headers=headers)
            response.raise_for_status()
            query_result = response.json()

            if query_result["code"] == 11000:
                logger.info('Transcription result obtained')
                return query_result
            elif query_result["code"] == 11001:
                logger.info('Waiting for transcription result')
                time.sleep(3)
                continue
            else:
                logger.error("Transcription error: %s", query_result['msg'])
                break

        except requests.RequestException as e:
            logger.error("Query request failed: %s", e)
            break

    return query_result

def transcribe_audio(wav_file_path: str) -> str:
    task_id = create(wav_file_path)
    if not task_id:
        return "Error creating transcription task"

    query_result = query(task_id)
    if query_result.get("code") == 11000:
        return query_result.get("result", "No transcription result found")
    else:
        return "Error querying transcription result"

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

        output = transcribe_audio(url)
        if output != "Error querying transcription result":
            await message.channel.send(output)
            return

        convert_ogg_to_wav(AUDIO_FILE_OGG, AUDIO_FILE_WAV)
        output = transcribe_audio(AUDIO_FILE_WAV)
        await message.channel.send(output)

@bot.event
async def on_ready():
    logger.info("Bot started!")
    await bot.change_presence(activity=discord.Game(name="user audio"))

async def setup():
    bot.add_cog(SpeechToText())

bot.run(token)