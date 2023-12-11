import whisper
from pathlib import Path
import yaml
import os

# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    AUDIO_FILE_OGG = config["audio_file"]

def transcribe(message_id : int) :
    #load model
    model = whisper.load_model("small")

    #load audio file
    audio = whisper.load_audio(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")

    #transcribe audio
    result = model.transcribe(audio)

    #clean up
    os.remove(Path(__file__).parent.parent / AUDIO_PATH / f"voice_message_{str(message_id)}.ogg")
    return result['text']