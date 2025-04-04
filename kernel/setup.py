import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

def setup_kernel(config):
    """Create and configure a kernel with the primary model using the config parameter."""
    kernel = Kernel()

    # Register the primary GPT-4o model for conversation
    model_id = config.azure_openai_deployment
    service_id = "gpt4o"

    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name=model_id,
            api_key=config.azure_openai_api_key,
            endpoint=config.azure_openai_endpoint
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