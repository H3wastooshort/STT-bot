import json
from pathlib import Path
import yaml
import os
import logging
import discord
import datetime

# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    CACHE = Path(config["cache"])
    CACHE_HISTORY_LIFESPAN = config["cache_history_lifespan"]

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#convert cache history lifespan to timedelta
def cache_lifespan_to_timedelta() :
    duration_type = CACHE_HISTORY_LIFESPAN[-1]
    duration = int(CACHE_HISTORY_LIFESPAN[:-1])
    
    if duration_type == "d" :
        return datetime.timedelta(days=duration)
    if duration_type == "m" :
        return datetime.timedelta(days=30*duration)
    if duration_type == "y" :
        return datetime.timedelta(days=365*duration)
    
    logger.warning("Invalid cache history lifespan, using default of 30 days")
    return datetime.timedelta(days=30)
    
def add_to_cache(audio_msg_id : int, view_msg_id : int, channel_id : int, author : discord.Member, content : str) :
    '''Adds a new entry to the cache'''

    try :
        #check if cache exists and create it if not
        if not os.path.exists(Path(__file__).parent.parent / AUDIO_PATH / CACHE):
            #create file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file :
                data = {}
                data[audio_msg_id] = {"channel_id" : int(channel_id), "view_id" : view_msg_id, "author" : str(author), "content" : content}
                json.dump(data, file)
                file.close()
        else : #if cache exists, add new entry
            #open file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
                cache = json.load(file)
                cache[audio_msg_id] = {"channel_id" : int(channel_id), "view_id" : view_msg_id, "author" : str(author), "content" : content}
                file.close()
            #save file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file:
                json.dump(cache, file)
                file.close()

    except Exception as e:
        logging.error("Error writing to cache: %s", e)
        return False
    
    return True

def remove_from_cache(audio_msg_id : int) :
    '''Removes a specific entry from the cache'''

    try :
        #open file
        with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
            cache = json.load(file)
            file.close()
        
        #remove entry
        del cache[str(audio_msg_id)]
          
        #save file
        with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file:
            json.dump(cache, file)
            file.close()

    except Exception as e:
        logging.error("Error removing from cache: %s", e)
        return False
        
    return True