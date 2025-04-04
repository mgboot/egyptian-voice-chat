import os
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Configuration object containing all app settings"""
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_speech_key: str
    azure_speech_endpoint: str
    elevenlabs_api_key: str

def load_config():
    """Load environment variables and return a configuration object"""
    # Load .env file
    load_dotenv()
    
    # Define required variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_ENDPOINT",
        "ELEVENLABS_API_KEY"
    ]
    
    # Check for missing variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_message = "Error: The following environment variables are missing:\n"
        for var in missing_vars:
            error_message += f"  - {var}\n"
        error_message += "Please add them to your .env file."
        return None, error_message
    
    # Create configuration object
    config = AppConfig(
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_speech_key=os.getenv("AZURE_SPEECH_KEY"),
        azure_speech_endpoint=os.getenv("AZURE_SPEECH_ENDPOINT"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    
    return config, None