import discord
from discord.ext import commands
import yaml
import urllib.request
import speech_recognition as sr

import traceback
from pydub import AudioSegment


import tracemalloc
tracemalloc.start()


AUDIO_FILE_OGG = "voice-message.ogg"
AUDIO_FILE_WAV = "voice-message.wav"

bot = commands.Bot(command_prefix=".", description="Speech to text", case_insensitive=1, intents=discord.Intents.all())
config = yaml.safe_load(open("config.yaml"))
token = config["token"]
print(config)
print(token)

def convert_ogg_to_wav(ogg_file, wav_file_path=None):
    try:
        # Load the OGG file
        audio = AudioSegment.from_ogg(ogg_file)

        # Export as an wav file
        audio.export(wav_file_path, format="wav")

        return f"File converted successfully: {wav_file_path}"
    except Exception as e:
        return f"Error converting file: {e}"

class SpeechToText(commands.Cog):
    "pouet"

@bot.event
async def on_message(message):
    print("Message received")
    # Check if the message is from the bot itself
    if message.author == bot.user:
        return

    # Search for voice message URLs in the message content
    url = message.attachments[0]
    if url:
        print(f"Voice message URL found: {url}")
        try:
            opener = urllib.request.URLopener()
            opener.addheader("User-Agent", "Mozilla/5.0")
            opener.retrieve(str(url), AUDIO_FILE_OGG)
        except Exception as e:
            traceback.print_exc()
        #conversion to wav
        convert_ogg_to_wav(AUDIO_FILE_OGG, AUDIO_FILE_WAV)
        # Transcribe the voice message
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE_WAV) as source:
            audio = r.record(source)  # read the entire audio file
        # recognize speech using Sphinx
        output = "Could not understand audio"
        try:
            output = r.recognize_sphinx(audio)
            print("Sphinx thinks you said " + output)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
            traceback.print_exc()
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            traceback.print_exc()

        await message.channel.send(output)

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print("Started!")
    await bot.change_presence(activity=discord.Game(name="user audio"))

async def setup(bot):
    bot.add_cog(SpeechToText())
bot.run(token)
