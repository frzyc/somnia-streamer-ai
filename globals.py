from dotenv import load_dotenv
from openai_manager import OpenAiManager
from azure_speech import AzureSpeechAIManager
from obs_websocket import OBSWebsocketsManager


load_dotenv(dotenv_path=".env.local")

obswebsockets_manager = OBSWebsocketsManager()
openai_manager = OpenAiManager()
speechtotext_manager = AzureSpeechAIManager()
