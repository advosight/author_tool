from .api import ApiLLM
from .bedrock import BedrockLLM
from .openai import OpenAiLLM
from .murf import Murf
from logging import getLogger
from utils import Storage

storage = Storage(None)
logger = getLogger('LLM')

class EmptyLLM:
    def __init__(self):
        self.name = "Empty LLM"
        self.max_tokens = 0

    def prompt(self, prompt) -> str:
        return None
    def conversation(self, conversation: [dict], temperature: float = 0.7) -> str:
        return None
    def image(self, prompt) -> bytes:
        return None
    def getSpeech(self, text: str) -> bytes:
        return None

class LLM:
    def __init__(self):
        self.api = EmptyLLM()
        self.image_api = EmptyLLM()
        self.tech_eval = EmptyLLM()
        self.ent_eval = EmptyLLM()
        self.voice = EmptyLLM()

        storage = Storage(None)
        settings = storage.getSettings()
        if settings is not None:
            self.loadConfigurations(settings)

    @property
    def max_tokens(self) -> int:
        """ Returns the maximum tokens for the LLMs """
        return self.api.max_tokens
    
    @property
    def is_configured(self) -> bool:
        """ Returns True if the LLMs are configured """
        if self.api.max_tokens == 0:
            logger.error("No editing LLM configured")
            return False
        if self.image_api.max_tokens == 0:
            logger.error("No image LLM configured")
            return False
        if self.tech_eval.max_tokens == 0:
            logger.error("No tech eval LLM configured")
            return False
        if self.ent_eval.max_tokens == 0:
            logger.error("No entertainment eval LLM configured")
            return False
        return True

    def loadConfigurations(self, configs: dict = None):
        """ Loads the configurations for the LLMs """
        
        if configs is None:
            configs = storage.getSettings()
            
        for config in configs['gen_ai']:
            type = config.get('type', None)
            
            if not config.get('enabled', True):
                logger.warning(f"Configuration {type} is disabled")
                continue

            if type is None:
                logger.error(f"Configuration {type} does not have a type")
                continue

            role = config.get('role', None)
            if role is None:
                logger.error(f"Configuration {type} does not have a role")
                continue

            api = EmptyLLM()
            if type == 'API':
                api = ApiLLM(config)
            if type == 'AWS Bedrock':
                api = BedrockLLM(config)
            if type == 'OpenAI':
                api = OpenAiLLM(config)
            if type == 'Murf':
                api = Murf(config)
            
            logger.info(f"Loaded configuration {type} for roles {role}")
            if 'image' == role:
                self.image_api = api
            if 'content' == role:
                self.api = api
            if 'tech_eval' == role:
                self.tech_eval = api
            if 'ent_eval' == role:
                self.ent_eval = api
            if 'voice' == role:
                self.voice = api

    def prompt(self, prompt: str) -> str:
        """ Invokes LLM with the prompt
        
        Args:
            prompt (str): The prompt for the LLM
        """
        print(f"Executing prompt on {self.api.name}")
        return self.api.prompt(prompt)

    def image(self, prompt: str) -> bytes:
        """ Invokes the LLM to produce an image
        Args:
            prompt (str): The prompt for the LLM
        
        Returns: The bytes of the image
        """
        print(f"Executing image on {self.image_api.name}")
        return self.image_api.image(prompt)

    def conversation(self, conversation: [dict], temperature: float = 0.7) -> str:
        """ Invokes the LLM with a conversation
        Args:
            conversation ([dict]): The conversation to be passed to the LLM
            temperature (float): The temperature to be used for the LLM
        
        Returns (str): The response from the LLM

        Conversation Example:
            [
                { "role": "user", "content": "User prompt"},
                { "role": "ai", "content": "System response"},
            ]
        """
        print(f"Executing conversation on {self.api.name}")
        return self.api.conversation(conversation, temperature)
    
    def techEval(self, conversation: [dict], temperature: float = 0.9) -> str:
        """ Invokes the LLM with a conversation
        Args:
            conversation ([dict]): The conversation to be passed to the LLM
            temperature (float): The temperature to be used for the LLM
        
        Returns (str): The response from the LLM

        Conversation Example:
            [
                { "role": "user", "content": "User prompt"},
                { "role": "ai", "content": "System response"},
            ]
        """
        print(f"Executing techEval on {self.tech_eval.name}")
        return self.tech_eval.conversation(conversation, temperature)

    def entEval(self, conversation: [dict], temperature: float = 0.9) -> str:
        """ Invokes the LLM with a conversation
        Args:
            conversation ([dict]): The conversation to be passed to the LLM
            temperature (float): The temperature to be used for the LLM

        Returns (str): The response from the LLM

        Conversation Example:
            [
                { "role": "user", "content": "User prompt"},
                { "role": "ai", "content": "System response"},
            ]
        """
        print(f"Executing entEval on {self.ent_eval.name}")
        return self.ent_eval.conversation(conversation, temperature)
    
    def getSpeech(self, text: str) -> bytes:
        """ Invokes the LLM to produce speech
        Args:
            text (str): The text to be converted to speech

        Returns: The bytes of the speech
        """
        print(f"Executing getSpeech on {self.voice.name}")
        return self.voice.getSpeech(text)

_llm_instance = LLM()

def getLLM():
    return _llm_instance

