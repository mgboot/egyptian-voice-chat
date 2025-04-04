import azure.cognitiveservices.speech as speechsdk

def setup_speech_client(config):
    """Initialize and return the Azure Speech client."""
    speech_config = speechsdk.SpeechConfig(
        subscription=config.azure_speech_key, 
        endpoint=config.azure_speech_endpoint
    )
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="ar-EG")
    
    return speech_recognizer

def recognize_speech(speech_recognizer):
    """Use Azure Speech to convert speech to text."""
    print("Listening... (speak now)")
    
    result = speech_recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("Speech recognition was canceled.")
        return None
    
    return None