import discord
import logging
import json
import yaml
from pathlib import Path

from . import cache_handling

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .load_conf import *
TIMEOUT = cache_handling.cache_lifespan_to_timedelta().total_seconds()

class ButtonsView(discord.ui.View):
    def __init__(self, message : discord.Message = None):
        super().__init__(timeout=TIMEOUT)
        self.message = message

    def __str__(self):
        return f"ButtonsView(message={self.message.id})"
    
    def __del__(self):
        logger.info(f"View {self} deleted")

    async def on_timeout(self) -> None:
        logger.info(f"View {self} timed out")
        return await super().on_timeout()

    # Button callback
    @discord.ui.button(label='Show transcription', custom_id="buttons", style=discord.ButtonStyle.primary, emoji="✍️")
    async def button_callback(self, interaction : discord.Interaction, button):

        #get message if not set
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
                author = message["author"]
                content = message["content"]
                first_pass = message["first_pass"]
                file.close()

                if content == "" :
                    text = f"Couldn't understand the audio from user **{author}**"
                elif content == "TRANSCRIPTION IN PROGRESS" :
                    text = "This message has not been transcribed yet. Wait or use `/transcribe` instead"
                else :
                    text = f"**{author}** said:```{content}```"
                    if first_pass :
                        text += "\n> This transcription may not be accurate and is still being processed."
                    else:
                        await interaction.response.send_message(text, ephemeral=False)
                        return
                await interaction.response.send_message(text, ephemeral=True)

        except :
            logger.error("Error during button callback")
            await interaction.response.send_message("Error during the transcription", ephemeral=True)
