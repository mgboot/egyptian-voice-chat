from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()

client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio_stream = client.text_to_speech.convert_as_stream(
    text="مفيش مشكلة خالص! عاصمة ولاية تكساس هي مدينة أوستن. أوستن معروفة بجوها الثقافي والفني، وفيها جامعة تكساس اللي هي واحدة من أكبر الجامعات في الولايات المتحدة. كمان أوستن بتشتهر بمهرجانات الموسيقى والفنون، زي مهرجان \"ساوث باي ساوث ويست\" (SXSW). لو عندك أي سؤال تاني عن أوستن أو تكساس بشكل عام، أنا هنا للمساعدة!",
    voice_id="meAbY2VpJkt1q46qk56T",
    model_id="eleven_multilingual_v2"
)

# option 1: play the streamed audio locally
stream(audio_stream)

# option 2: process the audio bytes manually
for chunk in audio_stream:
    if isinstance(chunk, bytes):
        print(chunk)
