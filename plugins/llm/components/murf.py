import requests
import json
import streamlit as st

murf_url = "https://api.murf.ai/v1/speech/generate"
class Murf:
    def __init__(self, config: dict):
        self.name = "Murf"
        self.api_key = config.get('api_key', None)
        self.local = config.get('local', 'en-US')
        self.model_version = config.get('model_version', 'GEN2')

        if self.api_key is None:
            self.max_tokens = 0
        else:
            self.max_tokens = int(config.get('max_tokens', '10370'))

    def display_config(self, feature: str, setting: dict, saveSettings: any):
        st.write("## Murf Configurations")

        # Settings for api key
        def on_change_key():
            setting['api_key'] = st.session_state[f"{feature}_api_key"]
            saveSettings()
        st.text_input(f"{feature} API Key", value=setting.get('api_key', ''), key=f"{feature}_api_key", on_change=on_change_key)

        # Settings for voice
        def on_change():
            setting['voice'] = st.session_state[f"{feature}_voice"]
            saveSettings()
        st.text_input(f"{feature} Voice", value=setting.get('voice', ''), key=f"{feature}_voice", on_change=on_change)

        # Settings for local
        def on_change_local():
            setting['local'] = st.session_state[f"{feature}_local"]
            saveSettings()
        st.text_input(f"{feature} Local", value=setting.get('local', 'en-US'), key=f"{feature}_local", on_change=on_change_local)

        # Settings for model version
        def on_change_model_version():
            setting['model_version'] = st.session_state[f"{feature}_model_version"]
            saveSettings()
        st.text_input(f"{feature} Model Version", value=setting.get('model_version', 'GEN2'), key=f"{feature}_model_version", on_change=on_change_local)

    def getAIFunctions():
        return ['Speech']

    def getSpeech(self, paragraph: str) -> bytes:
        if paragraph.strip() == "":
            return None
        
        print(f"Speech: {paragraph}")

        payload = json.dumps({
            "voiceId": "en-UK-juliet",
            "style": "Conversational",
            "text": paragraph,
            "rate": 0,
            "pitch": 0,
            "sampleRate": 48000,
            "format": "MP3",
            "channelType": "MONO",
            "pronunciationDictionary": {},
            "encodeAsBase64": False,
            "variation": 1,
            "audioDuration": 0,
            "modelVersion": self.model_version,
            "multiNativeLocale": self.local
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': self.api_key
        }

        response = requests.request("POST", murf_url, headers=headers, data=payload)

        result = response.json()

        print(f"Speech Result: {result}")
        audioResponse = requests.request("GET", result["audioFile"])

        retval = audioResponse.content

        # print(f"Speech Result: {retval}")
        return retval