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
    FIRST_MODEL = config["whisper_model_first_pass"]
    SECOND_MODEL = config["whisper_model_second_pass"]
    LANGUAGE = config["language"]
    
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe(message_id : int, model : str = FIRST_MODEL) :
    #load model
    available_models = whisper.available_models()

    #check if model exists
    if model not in available_models:
        logger.warning(f"Model {model} not found; using small model instead")
        model = "small"

    #load model
    model = whisper.load_model(model)

    #load audio file
    audio = whisper.load_audio(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")

    #transcribe audio
    if LANGUAGE == "auto" :
        result = model.transcribe(audio)
    else :
        result = model.transcribe(audio, language=LANGUAGE)

    return result['text']

def transcribe_and_cache(message : discord.Message, view_message : discord.Message) :
    '''Transcribes the audio file and adds the result to the cache, then removes old entries from the cache'''

    #FIRST PASS
    logger.info("Starting first pass transcription")

    try :
        output = transcribe(message.id, FIRST_MODEL)
    except Exception as e:
        logger.error("Error during the transcription: %s", e)

        #clean up if error
        os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message.id)}.ogg")
        return
    
    #cache
    if c_handle.add_to_cache(message.id, view_message.id, message.channel.id, message.author, message.created_at, output) :
        logger.info("Transcription completed")
    else :
        logger.error("Error adding to cache")
    c_handle.remove_old_cache()

    if FIRST_MODEL != SECOND_MODEL :
    #SECOND PASS
        logger.info("Starting second pass transcription")

        try :
            output = transcribe(message.id, SECOND_MODEL)
        except Exception as e:
            logger.error("Error during the transcription: %s", e)
            
            #clean up if error
            os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message.id)}.ogg")
            return
        
        #cache
        if c_handle.add_to_cache(message.id, view_message.id, message.channel.id, message.author, message.created_at, output) :
            logger.info("Transcription completed")
        else :
            logger.error("Error adding to cache")
        c_handle.remove_old_cache()

    #clean up
    os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message.id)}.ogg")


async def transcribe_no_cache(message_id : int, interaction : discord.Interaction) :
    '''Directly transcribes the audio file and sends the result to the user'''

    #transcribe
    try :
        transcription = await asyncio.to_thread(transcribe, message_id, FIRST_MODEL)
        await interaction.edit_original_response(content=transcription)
    except Exception as e:
        logger.error("Error during the transcription: %s", e)
        
        #clean up if error
        await interaction.edit_original_response(content="Error during the transcription")
        os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")
    
    #clean up
    os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")
