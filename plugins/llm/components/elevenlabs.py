import requests
import json
import streamlit as st
from elevenlabs.client import ElevenLabs
from utils import getLogger

logger = getLogger('ElevenLabs')

class ElevenLabsClient:
    def __init__(self, config: dict):
        self.name = "ElevenLabs"
        self.api_key = config.get('api_key', None)
        self.voice = config.get('voice', 'Alice')
        self.voice_id = config.get('voice_id', None)
        self.client: ElevenLabs = None

        if self.api_key is None:
            self.max_tokens = 0
        else:
            self.client = ElevenLabs(api_key=self.api_key)
            self.max_tokens = 10000

    def display_config(self, feature: str, setting: dict, saveSettings: any):
        st.write("## ElevenLabs Configurations")

        # Settings for api key
        def on_change_key():
            setting['api_key'] = st.session_state[f"{feature}_api_key"]
            saveSettings()
        st.text_input(f"{feature} API Key", value=setting.get('api_key', ''), key=f"{feature}_api_key", on_change=on_change_key)

        voicesResponse  = requests.get("https://api.elevenlabs.io/v1/voices")
        # Get the body of the response
        voices = voicesResponse.json()['voices']

        name_list = [voice['name'] for voice in voices]

        # Settings for voice
        def on_change():
            voice_name = st.session_state[f"{feature}_voice"]
            setting['voice'] = voice_name
            setting['voice_id'] = voices[name_list.index(voice_name)]['voice_id']
            saveSettings()
        
        st.selectbox(f"{feature} Voice", name_list, key=f"{feature}_voice", index=name_list.index(setting.get('voice', 'Alice')), on_change=on_change)
        # st.text_input(f"{feature} Voice", value=setting.get('voice', ''), key=f"{feature}_voice", on_change=on_change)

    def getAIFunctions():
        return ['Speech']

    def getSpeech(self, paragraph: str) -> bytes:
        if paragraph.strip() == "":
            return None
        
        logger.info(f"Speech: {paragraph}")

        audio_stream = self.client.text_to_speech.convert_as_stream(
            text=paragraph,
            voice_id=self.voice_id,
            output_format="mp3_44100_128",
            model_id="eleven_multilingual_v2"
        )

        retval: bytes = b''
        for chunk in audio_stream:
            if isinstance(chunk, bytes):
                retval += chunk

        return retval