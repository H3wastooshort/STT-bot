import whisper
import discord
from pathlib import Path
import yaml
import os
import logging
import asyncio

from . import cache_handling as c_handle

# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    MODEL = config["whisper_model"]
    LANGUAGE = config["language"]
    
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe(message_id : int) :
    #load model
    available_models = whisper.available_models()
    using_model = MODEL

    #check if model exists
    if using_model not in available_models:
        logger.warning(f"Model {MODEL} not found; using small model instead")
        using_model = "small"

    #load model
    model = whisper.load_model(using_model)

    #load audio file
    audio = whisper.load_audio(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")

    #transcribe audio
    if LANGUAGE == "auto" :
        result = model.transcribe(audio)
    else :
        result = model.transcribe(audio, language=LANGUAGE)

    #clean up
    os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")
    return result['text']

def transcribe_and_cache(message : discord.Message, view_message : discord.Message) :
    #transcription and cache
    output = transcribe(message.id)
    if c_handle.add_to_cache(message.id, view_message.id, message.channel.id, message.author, message.created_at, output) :
        logger.info("Transcription completed")
    else :
        logger.error("Error adding to cache")
    c_handle.remove_old_cache()

async def transcribe_no_cache(message_id : int, interaction : discord.Interaction) :
    '''Directly transcribes the audio file and sends the result to the user'''
    global last_transcription
    last_transcription = transcribe(message_id)
    if last_transcription == "" :
        await interaction.edit_original_response(content="Error during the transcription")
    else :
        await interaction.edit_original_response(content=last_transcription)