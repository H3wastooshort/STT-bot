import whisper
from pathlib import Path
import yaml
import os
import logging

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
        result = model.transcribe(audio, language="fr")

    #clean up
    os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")
    return result['text']