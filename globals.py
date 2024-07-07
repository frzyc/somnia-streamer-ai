from dotenv import load_dotenv
from openai_manager import OpenAiManager
from azure_speech import AzureSpeechAIManager
from obs_websocket import OBSWebsocketsManager


load_dotenv(dotenv_path=".env.local")

obswebsockets_manager: OBSWebsocketsManager | None = None


def getOBSWebsocketsManager() -> OBSWebsocketsManager:
    global obswebsockets_manager
    if not obswebsockets_manager:
        obswebsockets_manager = OBSWebsocketsManager()
    return obswebsockets_manager


openai_manager: OpenAiManager | None = None


def getOpenAiManager() -> OpenAiManager:
    global openai_manager
    if openai_manager is None:
        openai_manager = OpenAiManager()
    return openai_manager


speechtotext_manager: AzureSpeechAIManager | None = None


def getAzureSpeechAIManager() -> AzureSpeechAIManager:
    global speechtotext_manager
    if not speechtotext_manager:
        speechtotext_manager = AzureSpeechAIManager()
    return speechtotext_manager
