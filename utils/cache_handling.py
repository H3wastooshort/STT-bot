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
    
def add_to_cache(audio_msg_id : str, view_msg_id : str, channel_id : discord.TextChannel, author : discord.Member, date : datetime.datetime, content : str) :
    '''Adds a new entry to the cache'''

    try :
        #check if cache exists and create it if not
        if not os.path.exists(Path(__file__).parent.parent / AUDIO_PATH / CACHE):
            #create file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file :
                data = {}
                data[audio_msg_id] = {"channel_id" : str(channel_id), "view_id" : view_msg_id, "author" : str(author), "date" : str(date), "content" : content}
                json.dump(data, file)
                file.close()
        else : #if cache exists, add new entry
            #open file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
                cache = json.load(file)
                cache[audio_msg_id] = {"channel_id" : str(channel_id), "view_id" : view_msg_id, "author" : str(author), "date" : str(date), "content" : content}
                file.close()
            #save file
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file:
                json.dump(cache, file)
                file.close()

    except Exception as e:
        logging.error("Error writing to cache: %s", e)
        return False
    
    return True

def get_all_cache() :
    '''Returns the entire cache as a dictionary'''

    try :
        #open file
        with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
            cache = json.load(file)
            file.close()

    except Exception as e:
        logging.error("Error reading cache: %s", e)
        return None
    
    return cache

def remove_old_cache() :
    '''Removes entries older than the cache history lifespan'''

    cache_timedelta = cache_lifespan_to_timedelta()

    try :
        #open file
        with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
            cache = json.load(file)
            file.close()
        
        #remove old entries
        for key in list(cache.keys()) :
            date = datetime.datetime.strptime(cache[key]["date"], "%Y-%m-%d %H:%M:%S.%f%z")
            date = date.replace(tzinfo=None) #remove timezone info
            if datetime.datetime.now() - date > cache_timedelta :
                del cache[key]
                logger.info(f"Removed old cache entry {key}")
            
        #save file
        with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "w") as file:
            json.dump(cache, file)
            file.close()

    except Exception as e:
        logging.error("Error removing old cache: %s", e)
        return False
    
    return True