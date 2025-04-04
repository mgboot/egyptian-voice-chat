import os
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

def setup_tts_client(config):
    """Initialize and return the ElevenLabs TTS client."""
    return ElevenLabs(api_key=config.elevenlabs_api_key)

def text_to_speech(tts_client, text):
    """Convert text to speech using ElevenLabs and play it."""
    audio_stream = tts_client.text_to_speech.convert_as_stream(
        text=text,
        voice_id="meAbY2VpJkt1q46qk56T", # Hoda
        model_id="eleven_multilingual_v2"
    )
    
    # Play the audio
    stream(audio_stream)