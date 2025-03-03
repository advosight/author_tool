from openai import OpenAI

class OpenAiLLM:
    def __init__(self, config: dict):
        self.name = "OpenAI"
        api_key = config.get('api_key', '')
        self.client = OpenAI(api_key=api_key)
        self.default_temp = config.get('default_temp', 0.7)
        self.model = config.get('model', 'gpt-4o')

        if api_key == '':
            self.max_tokens = 0
        else:
            self.max_tokens = 30000

    def conversation(self, conversation: [dict], temperature: float = None):
        if temperature is None:
            temperature = self.default_temp

        # Convert conversation into messages for OpenAI
        messages = []
        for message in conversation:
            role = "user"
            if message["role"] == "ai":
                role = "assistant"
            messages.append({
                "role": role, 
                "content": [ 
                    { "type": "text", "text": message['content'] } 
                ] 
            })
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            n=1,
            stop=None,
        )

        # Return the response
        return response.choices[0].message.content.strip()

    def prompt(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            n=1,
            stop=None,
            temperature=self.default_temp,
        )
        return response.choices[0].message.content.strip()