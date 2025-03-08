import boto3
from botocore.config import Config
import json
import base64
import streamlit as st

class BedrockLLM:
    def __init__(self, settings: dict):
        self.name = "Bedrock"
        self.model_id = settings['model']
        self.max_tokens = settings['max_tokens']

        # Instantiate Bedrock LLM Client
        config = Config(read_timeout=1000)
        self.client = boto3.client("bedrock-runtime", config=config)

    def display_config(self, feature: str, setting: dict, saveSettings: any):
        st.write("## AWS Bedrock Configurations")

        has_changed = False

        # Validate defaults set in object
        if 'region' not in setting:
            setting['region'] = 'default'
            has_changed = True
        if 'auth' not in setting:
            setting['auth'] = 'profile'
            has_changed = True
        if 'profile' not in setting:
            setting['profile'] = 'default'
            has_changed = True
        
        if has_changed:
            saveSettings()
            has_changed = False

        # Get AWS region to use
        def on_change_region():
            setting['region'] = st.session_state[f"{feature}_region"]
            saveSettings()
        
        aws_regions = ['default', 'us-east-1', 'us-west-2']
        selected_region = setting.get('region', 'default')
        region_index = aws_regions.index(selected_region) if selected_region in aws_regions else 0
        st.selectbox(f"{feature} Region", aws_regions, index=region_index, on_change=on_change_region)
        
        # Get authentication type to use
        def on_change_auth():
            setting['auth'] = st.session_state[f"{feature}_auth"]
            saveSettings()

        aws_auth_types = ['profile', 'iam']
        selected_auth = setting.get('auth', 'profile')
        auth_index = aws_auth_types.index(selected_auth) if selected_auth in aws_auth_types else 0
        auth = st.selectbox(f"{feature} Auth", aws_auth_types, index=auth_index, key=f"{feature}_auth", on_change=on_change_auth)
        
        # Configure specific authentication types
        if auth == 'profile':
            # Get profile to use for authentication
            def on_change_profile():
                setting['profile'] = st.session_state[f"{feature}_profile"]
                saveSettings()

            st.text_input(f"{feature} Profile Name", value=setting.get('profile', 'default'), key=f"{feature}_profile", on_change=on_change_profile)
        if auth == 'iam':
            # Get access and secret access keys
            def on_change_key():
                setting['access_key'] = st.session_state[f"{feature}_access_key"]
                saveSettings()

            st.text_input(f"{feature} Access Key", value=setting.get('access_key', ''), key=f"{feature}_access_key", on_change=on_change_key)
            
            def on_change_secret():
                setting['secret_key'] = st.session_state[f"{feature}_secret_key"]
                saveSettings()

            st.text_input(f"{feature} Secret Key", value=setting.get('secret_key', ''), key=f"{feature}_secret", on_change=on_change_secret)

        # Model Configuration
        if 'model' not in setting:
            if feature == 'image':
                setting['model'] = 'stability.stable-diffusion-xl-v0:1'
                setting['max_tokens'] = 1024
            else:
                setting['model'] = 'us.amazon.nova-pro-v1:0'
                setting['max_tokens'] = 2048

            saveSettings()
        def on_change_model():
            setting['model'] = st.session_state[f"{feature}_model"]
            saveSettings()
        st.text_input(f"{feature} Model", value=setting.get('model', 'us.amazon.nova-pro-v1:0'), key=f"{feature}_model", on_change=on_change_model)

        # Token configuration
        if 'max_tokens' not in setting:
            setting['max_tokens'] = 1024
            saveSettings()
        
        def on_change_max_tokens():
            setting['max_tokens'] = st.session_state[f"{feature}_max_tokens"]
            saveSettings()
        st.text_input(f"{feature} Max Tokens", value=setting.get('max_tokens', 1024), key=f"{feature}_max_tokens", on_change=on_change_max_tokens)

        # Configure temperature
        if 'temperature' not in setting:
            setting['temperature'] = self.default_temp
            saveSettings()

        def on_change_temp():
            setting['temperature'] = st.session_state[f"{feature}_temperature"]
            saveSettings()
        st.slider(f"{feature} Temperature", 0.0, 1.0, value=setting.get('temperature', 0.7), key=f"{feature}_temperature", on_change=on_change_temp,help="""
            Temperatures dictate how much creativity vs precision the AI has when generating text.
            A higher temperature means more creativity, but less precision. A lower temperature means less creativity, but more precision.
            A temperature of 0.0 means the AI will always choose the most likely option.
            A temperature of 1.0 means the AI will always choose the most creative option.
            A temperature of 0.7 is a good balance between creativity and precision.
            """)

    def getAIFunctions():
        return ['Entertainment', "Technical", "Entertainment"]

    def prompt(self, prompt):
        # Construct the prompt to bedrock
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "messages": [
                    { "role": "user", "content": [ { "text": prompt } ] }
                ],
                "inferenceConfig": { "temperature": 0.5, "topP": 0.9 }
            }),
            accept="application/json",
            contentType="application/json"
        )
        print(response)

        response_body = json.loads(response['body'].read())
        
        response_text = response_body["output"]["message"]["content"][0]["text"]
        print(response_text)
        return response_text

    def conversation(self, conversation, temperature: float = 0.5):
        # Convert conversation into messages
        messages = []
        for message in conversation:
            role = "user"
            if message["role"] == "ai":
                role = "assistant"

            messages.append({"role": role, "content": [{"text": message["content"]} ]})

        # Construct the prompt to bedrock
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "messages": messages,
                "inferenceConfig": {"maxTokens": self.max_tokens, "temperature": temperature, "topP": 0.9}
            }),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response["body"].read())
        
        response_text = response_body["output"]["message"]["content"][0]["text"]

        return response_text

    def image(self, prompt):
        # Construct the prompt to bedrock

        # check if the image model id starts with stability
        if self.model_id.startswith("stability"):
            response = self.client.invoke_model(
                modelId=self.model_id,
                body= json.dumps({
                    "prompt": "The described person should be photo realistic. " + prompt,
                    "aspect_ratio": "1:1",
                    "output_format": "png"
                }),
                accept="application/json",
                contentType="application/json"
            )
            
        if self.model_id.startswith("amazon"):
            response = self.client.invoke_model(
                modelId=self.model_id,
                body= json.dumps({
                    "textToImageParams": {
                        "text": "Do not base this image on real people, but should be photo realistic. " + prompt
                    },
                    "taskType": "TEXT_IMAGE",
                    "imageGenerationConfig": {
                        "cfgScale": 8,
                        "seed": 42,
                        "quality": "standard",
                        "height": 1024,
                        "width": 1024,
                        "numberOfImages": 1
                    }
                }),
                accept="application/json",
                contentType="application/json"
            )

        response_body = json.loads(response.get("body").read())
        base64_image = response_body.get("images")[0]
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)

        return image_bytes
