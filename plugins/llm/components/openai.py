from openai import OpenAI
import streamlit as st
from typing import List
from utils.logging import getLogger

logger = getLogger(__name__)

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

    def display_config(self, feature: str, setting: dict, saveSettings: any):
        st.write("## OpenAI Configurations")
        def on_change(): 
            logger.warning(f"Saving API Key for {feature}")
            setting['api_key'] = st.session_state[f"{feature}_api_key"]
            saveSettings()

        st.text_input(f"{feature} API Key", value=setting.get('api_key', ''), key=f"{feature}_api_key", on_change=on_change)

        # Configure temperature
        if 'temperature' not in setting:
            setting['temperature'] = self.default_temp
            saveSettings()

        def on_change_temp():
            setting['temperature'] = st.session_state[f"{feature}_temperature"]
            saveSettings()
        st.slider(f"{feature} Temperature", 0.0, 1.0, value=setting.get('temperature', self.default_temp), key=f"{feature}_temperature", on_change=on_change_temp,help="""
            Temperatures dictate how much creativity vs precision the AI has when generating text.
            A higher temperature means more creativity, but less precision. A lower temperature means less creativity, but more precision.
            A temperature of 0.0 means the AI will always choose the most likely option.
            A temperature of 1.0 means the AI will always choose the most creative option.
            A temperature of 0.7 is a good balance between creativity and precision.
            """)

    def getAIFunctions():
        return ['Entertainment', "Technical", "Entertainment"]
    
    def conversation(self, conversation: List[dict], temperature: float = None):
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