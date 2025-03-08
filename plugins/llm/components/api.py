import openai as openai
from utils.logging import getLogger
import streamlit as st

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

    def display_config(self, feature: str, setting: dict, saveSettings: any):
        # Get API Information
        def on_change():
            setting['url'] = st.session_state[f"{feature}_url"]
            saveSettings()
        st.text_input(f"{feature} Url", value=setting.get('url', 'http://localhost:1234/v1'), key=f"{feature}_url", on_change=on_change)

        # Get API Key
        def on_change_key():
            setting['api_key'] = st.session_state[f"{feature}_api_key"]
            saveSettings()
        st.text_input(f"{feature} API Key", value=setting.get('api_key', ''), key=f"{feature}_api_key", on_change=on_change_key)

        # Get Model Name
        def on_change_model():
            setting['model'] = st.session_state[f"{feature}_model"]
            saveSettings()
        st.text_input(f"{feature} Model", value=setting.get('model', ''), key=f"{feature}_model", on_change=on_change_model)

        def on_change_max_tokens():
            setting['max_tokens'] = st.session_state[f"{feature}_max_tokens"]
            saveSettings()
        st.text_input(f"{feature} Max Tokens", value=setting.get('max_tokens', '10370'), key=f"{feature}_max_tokens", on_change=on_change_max_tokens)

    def getAIFunctions():
        return ['Entertainment', "Technical", "Entertainment", "Speech"]

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