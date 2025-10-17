from pathlib import Path
# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config.get("audio_path",None) or os.getenv("STTB_AUDIO_PATH","/cache/audio"))
    CACHE = Path(config.get("cache",None) or os.getenv("STTB_CACHE_PATH","/cache/text"))
    TOKEN = config.get("token",None) or os.getenv("STTB_TOKEN",None)
    CACHE_HISTORY_LIFESPAN = config["cache_history_lifespan"]
    TIMEOUT = cache_handling.cache_lifespan_to_timedelta().total_seconds()
    FIRST_MODEL = config["whisper_model_first_pass"]
    SECOND_MODEL = config["whisper_model_second_pass"]
    LANGUAGE = config["language"]
