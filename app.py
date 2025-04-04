import os
import asyncio
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings


def validate_environment():
    """Validate that all required environment variables are present."""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_ENDPOINT",
        "ELEVENLABS_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_message = "Error: The following environment variables are missing:\n"
        for var in missing_vars:
            error_message += f"  - {var}\n"
        error_message += "Please add them to your .env file."
        return False, error_message
        
    return True, None


def setup_kernel():
    """Create and configure a kernel with the primary model."""
    kernel = Kernel()

    # Register the primary GPT-4o model for conversation
    model_id = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    service_id = "gpt4o"

    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name=model_id,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    )
    
    return kernel, service_id, model_id


def create_chat_function(kernel, service_id, model_id):
    """Create and register the chat function."""
    chat_prompt = """{{$chat_history}}\nUser: {{$user_input}}\nTutor:"""

    chat_config = PromptTemplateConfig(
        template=chat_prompt,
        name="chat",
        template_format="semantic-kernel",
        input_variables=[
            InputVariable(name="chat_history", description="The conversation history", is_required=True),
            InputVariable(name="user_input", description="The user's input", is_required=True),
        ],
        execution_settings={
            service_id: {
                "model": model_id,
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
    )

    return kernel.add_function(
        function_name="Chat",
        plugin_name="TutorPlugin",
        prompt_template_config=chat_config,
    )


def get_system_message():
    """Return the system message for the tutor."""
    return """
انتي مُساعدة افتراضية.
انتي بتساعدي الناس اللى عايزين يمارسوا عربي.
انتي دايماً بتتكلمي بالبهجة المصرية.

بتكتبي تشكيل في الكتابة عشان تسهلي على الناس القراءة.
مثلاً: اللَهجة المَصريّة
    """


def setup_chat_interface(kernel, chat_function, service_id, model_id):
    """Set up the chat interface with history and settings."""
    # Initialize chat history
    chat_history = ChatHistory()
    chat_history.add_system_message(get_system_message())

    # Configure execution settings
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        ai_model_id=model_id,
        temperature=0.7,
        max_tokens=1000
    )

    # Prepare kernel arguments with settings
    arguments = KernelArguments(settings=execution_settings)
    arguments["chat_history"] = chat_history
    
    return chat_history, arguments


def setup_speech_client():
    """Initialize and return the Azure Speech client."""
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="ar-EG")
    
    return speech_recognizer


def setup_tts_client():
    """Initialize and return the ElevenLabs TTS client."""
    return ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


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


def text_to_speech(tts_client, text):
    """Convert text to speech using ElevenLabs and play it."""
    audio_stream = tts_client.text_to_speech.convert_as_stream(
        text=text,
        voice_id="meAbY2VpJkt1q46qk56T", # Hoda
        model_id="eleven_multilingual_v2"
    )
    
    # Play the audio
    stream(audio_stream)


async def chat_with_tutor(kernel, chat_function, chat_history, arguments, user_input):
    """Chat with the tutor and get a response."""
    # Update the arguments with the user input
    arguments["user_input"] = user_input
    
    # Invoke the chat function
    result = await kernel.invoke(chat_function, arguments=arguments)
    
    # Update the chat history
    chat_history.add_user_message(user_input)
    chat_history.add_assistant_message(str(result))
    
    return str(result)


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


async def main():
    # Load environment variables
    load_dotenv()

    # Validate environment
    valid, error_message = validate_environment()
    if not valid:
        print(error_message)
        return

    # Setup kernel and model
    kernel, service_id, model_id = setup_kernel()
    
    # Create chat function
    chat_function = create_chat_function(kernel, service_id, model_id)
    
    # Setup chat interface
    chat_history, arguments = setup_chat_interface(kernel, chat_function, service_id, model_id)
    
    # Initialize speech and TTS clients
    speech_recognizer = setup_speech_client()
    tts_client = setup_tts_client()
    
    # Run the console interface with speech capabilities
    await run_console_interface(kernel, chat_function, chat_history, arguments, speech_recognizer, tts_client)


if __name__ == "__main__":
    asyncio.run(main())
