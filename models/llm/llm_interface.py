
class LLMPlugin:
    def __init__(self, config):
        pass

    def getAIFunctions() -> [str]:
        """
        Returns a list of functions that the LLM can use
        """
        return []

    def prompt(self, prompt: str) -> str:
        """
        Prompt the LLM with the given prompt

        Args:
            prompt (str): The prompt to use with the LLM

        Returns:
            The LLM response
        """
        # Prompt the LLM with the given prompt
        logger = getLogger()
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                { "role": "system", "content": "You are a focused copywriter. When you respond you only respond with the requested information and no context or conversation." },
                { "role": "user", "content": prompt }
            ]
        )

        if response.choices is None:
            return None

        retval = response.choices[0].message.content
        
        return retval

    def conversation(self, conversation: [dict]) -> str:
        """
        Based on a conversation, generate a response from the LLM

        Args:
            conversation ([dict]): The conversation to use with the LLM

        Returns:
            The LLM response
        """
        pass

    def getSpeech(self, text: str) -> bytes:
        """
        Generates an MP3 from the text provided.

        Args:
            text (str): The text to convert to audio
        """
        pass
