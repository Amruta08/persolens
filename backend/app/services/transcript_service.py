from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def transcribe(audio_path: str) -> dict:
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    
    return {
        "text": response.text,
        "words": [{"word": w.word, "start": w.start, "end": w.end} for w in response.words],
    }