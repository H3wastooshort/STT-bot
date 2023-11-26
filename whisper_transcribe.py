import whisper

async def transcribe() :
    #load model
    model = whisper.load_model("small")

    #load audio file
    audio = whisper.load_audio("voice-message.ogg")

    #transcribe audio
    result = model.transcribe(audio)
    return result['text']