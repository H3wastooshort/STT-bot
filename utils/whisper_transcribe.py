import whisper
from pathlib import Path
import yaml

# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    AUDIO_FILE_OGG = config["audio_file"]

def transcribe() :
    #load model
    model = whisper.load_model("small")

    #load audio file
    audio = whisper.load_audio(Path(__file__).parent.parent / AUDIO_PATH / AUDIO_FILE_OGG)

    #transcribe audio
    result = model.transcribe(audio)
    return result['text']