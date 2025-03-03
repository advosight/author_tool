import openai as openai
from logging import getLogger

class ApiLLM:
    def __init__(self, config):
        self.name = "API"
        self.endpoint = config.get('url', None)
        self.model = config.get('model', None)

        if self.endpoint is None or self.model is None:
            self.max_tokens = 0
            return

        self.client = openai.OpenAI(
            base_url=self.endpoint,
            api_key=config.get('api_key', "not-needed")
        )
        self.client.with_options()
        self.max_tokens = int(config.get('max_tokens', '10370'))

    def prompt(self, prompt):
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

    def conversation(self, conversation):
        # Prompt the LLM with the given conversation
        logger = getLogger()
        messages = []
        for message in conversation:
            role = message['role']
            if role == 'ai':
                role = 'system'
            messages.append({"role": message['role'], "content": message['content']})

        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages
        )

        if response.choices is None:
            return None

        retval = response.choices[0].message.content

        return retval