import discord
import logging
import json
import yaml
from pathlib import Path

from . import cache_handling

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open(Path(__file__).parent.parent / "config.yaml", "r") as file:
    config = yaml.safe_load(file)
    AUDIO_PATH = Path(config["audio_path"])
    
    CACHE = Path(config["cache"])
    TIMEOUT = cache_handling.cache_lifespan_to_timedelta().total_seconds()
    print(TIMEOUT)
    TIMEOUT = 60


class ButtonsView(discord.ui.View):
    def __init__(self, message : discord.Message = None):
        super().__init__(timeout=TIMEOUT)
        self.message = message

    def __str__(self):
        return f"ButtonsView(message={self.message.id})"
    
    def __del__(self):
        #delete associated view
        cache_handling.remove_from_cache(self.message.id)
        logger.info(f"View {self} deleted")

    async def on_timeout(self) -> None:
        logger.info(f"View {self} timed out")
        return await super().on_timeout()

    @discord.ui.button(label='Show transcription', custom_id="buttons", style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):
        if self.message is None:
            date = interaction.message.created_at
            history = interaction.channel.history(before=date, limit=1)
            async for message in history:
                self.message = message

        #open cache
        try :
            with open(Path(__file__).parent.parent / AUDIO_PATH / CACHE, "r") as file:
                cache = json.load(file)
                message = cache[str(self.message.id)]
                text = f"**{message['author']}** said:\n ```{message['content']}```"
                try :
                    await interaction.response.send_message(text, ephemeral=True)
                except discord.errors.HTTPException as e:
                    logger.error("Error sending message: %s", e)
                    await interaction.response.send_message("Error during the transcription", ephemeral=True)
        except :
            await interaction.response.send_message("This message has not been transcribed yet. Wait or use `/transcribe` instead", ephemeral=True)
