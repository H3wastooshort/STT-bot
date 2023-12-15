# Overview

**Speech-To-Text** is a Discord bot that, as the name suggests, automatically transcribes voice recordings sent in a channel.
**This is a self-hosted bot** and you will need to host it on your own machine. <br>
This bot uses [OpenAI's Whisper speech recognition model](https://github.com/openai/whisper), as it can perform fast speech recognition across a large array of languages.

# Features

## Listen & Transcribe

Once a voice message is sent in a channel, the bot replies with a message containing a `Show transcription` button.
In the background, it will automatically download the audio and process it using **Whisper**.
The message will be processed twice ; the first time with a smaller model for faster transcription time, and a second time for better accuracy. The output is then saved to a cache.
Once this is done, any user will be able to click the button. The bot will send an **ephemeral message**, only visible to the user, containing the transcription.

![image](https://github.com/zatomos/Speech-to-text_bot/assets/68819715/0d5c04b7-1d4d-4a5d-a6ad-ed37aaca594b)


The cache, by default, is emptied every month. If a voice message has been deleted from the cache, it can still be transcribed using a command. <br>

## Commands

By using the command `/transcribe <voice_message_id>`, the bot will not attempt to find the transcription in the cache but will instead process the audio and directly send it to the user, without saving it.

# Installation

This bot has been tested to work on Windows and Linux

## Discord application

You will first need to set up a new Discord application on the [Discord developer portal](https://discord.com/developers/applications).
- Create a new application and fill in the general information.
- In the `Bot` category, click `Reset Token` to generate it. **DO NOT FORGET TO SAVE IT !** Then toggle on everything under `Priviledged Gateway Intents`. <br>
- In the `OAuth2` category, select the `bot` scope and give the bot these permissions :
  - Send Messages
  - Read Message History
  - Use Slash Commands  
- Copy the generated URL and invite the bot to your server.

## Install Python 3.11+
[Download link](https://www.python.org/downloads/)

## Install FFmpeg

This is mandatory for **Whisper**. [Download link](https://ffmpeg.org/download.html)

## Setup the repository

- Download the repository as a zip or clone it with `git clone https://github.com/zatomos/Speech-to-text_bot.git`. <br>
- Then install the libraries using `pip install -r requirements.txt`. <br>
- Edit the `config.yaml` file to store your bot token. You can also tweak some settings to your liking.<br>
- Finally, run the bot using `python speechtotext.py`.
