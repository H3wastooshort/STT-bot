import json
from pathlib import Path
import yaml
import os
import logging
import discord
import datetime

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    CACHE = Path(config["cache"])

def add_to_cache(id : str, author : discord.Member, date : datetime.datetime, content : str) :
    try :
        #check if cache exists and create it if not
        if not os.path.exists(Path(__file__).parent / AUDIO_PATH / CACHE):
            with open(Path(__file__).parent / AUDIO_PATH / CACHE, "w") as file :
                data = {}
                data[id] = {"author" : str(author), "date" : str(date), "content" : content}
                json.dump(data, file)
                file.close()
        else : #if cache exists, add new entry
            with open(Path(__file__).parent / AUDIO_PATH / CACHE, "r") as file:
                cache = json.load(file)
                cache[id] = {"author" : str(author), "date" : str(date), "content" : content}
                file.close()
            with open(Path(__file__).parent / AUDIO_PATH / CACHE, "w") as file:
                json.dump(cache, file)
                file.close()
    except Exception as e:
        logging.error("Error writing to cache: %s", e)
        return False
    return True