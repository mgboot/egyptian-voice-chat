import asyncio
from config.environment import load_config
from kernel.setup import setup_kernel, create_chat_function, setup_chat_interface
from speech.recognition import setup_speech_client
from speech.synthesis import setup_tts_client
from chat.interface import run_console_interface

async def main():
    # Load configuration
    config, error_message = load_config()
    if not config:
        print(error_message)
        return

    # Setup kernel and model
    kernel, service_id, model_id = setup_kernel(config)
    
    # Create chat function
    chat_function = create_chat_function(kernel, service_id, model_id)
    
    # Setup chat interface
    chat_history, arguments = setup_chat_interface(kernel, chat_function, service_id, model_id)
    
    # Initialize speech and TTS clients
    speech_recognizer = setup_speech_client(config)
    tts_client = setup_tts_client(config)
    
    # Run the console interface with speech capabilities
    await run_console_interface(kernel, chat_function, chat_history, arguments, speech_recognizer, tts_client)

if __name__ == "__main__":
    asyncio.run(main())