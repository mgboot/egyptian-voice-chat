from speech.recognition import recognize_speech
from speech.synthesis import text_to_speech
from kernel.setup import chat_with_tutor

async def run_console_interface(kernel, chat_function, chat_history, arguments, speech_recognizer, tts_client):
    """Run the console-based chat interface with speech capabilities."""
    print("\n" + "="*50)
    print("Welcome to your language tutor chat!")
    print("="*50)
    print("Say something in Arabic to begin the conversation.")
    print("The system will automatically listen for your voice input.")
    print("Say 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        print("\nListening for your voice input...")
        
        speech_input = recognize_speech(speech_recognizer)
        if not speech_input:
            print("\nNo speech detected. Please try again.")
            continue
            
        print(f"\nYou: {speech_input}")
        
        if speech_input.lower() in ["exit", "quit"]:
            print("\nThank you for chatting! Goodbye.")
            break
        
        print("\nLanguage tutor is thinking...")
        response = await chat_with_tutor(kernel, chat_function, chat_history, arguments, speech_input)
        print(f"\nLanguage tutor: {response}")
        
        # Convert the response to speech
        text_to_speech(tts_client, response)