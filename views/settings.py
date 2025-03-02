import streamlit as st
from utils import Storage, getLogger
from llm import getLLM

logger = getLogger('Settings')

def saveSettings(settings: dict):
    storage = Storage(None)
    storage.saveSettings(settings)
    llm = getLLM()
    llm.loadConfigurations(settings)

def settingsView():
    storage = Storage(None)
    settings = storage.getSettings()

    if 'gen_ai' not in settings:
        settings['gen_ai'] = []

    
    def AIConfig(key: str, default_temp: float):
        ai_providers = ['OpenAI', 'AWS Bedrock', 'Local']
        if key == 'voice':
            ai_providers = ['Murf']

        setting = None
        setting_index = 0
        for i, ai in enumerate(settings['gen_ai']):
            if ai.get('role', None) == key:
                setting = ai
                try:
                    setting_index = ai_providers.index(ai.get('type', 'OpenAI'))
                except:
                    setting_index = 0
                break
        
        provider = st.selectbox(f"{key} Provider Type", ai_providers, index=setting_index)

        st.divider()

        # Find the settings for the provider
        has_changed = False
        
        if setting is None:
            # Remove provider for the current role
            for i, ai in enumerate(settings['gen_ai']):
                if ai.get('role', None) == key:
                    settings['gen_ai'].pop(i)
                    break

            logger.warning(f"No setting found for {key} with type {provider}")
            setting = {'type': provider, 'role': key}
            settings['gen_ai'].append(setting)
            has_changed = True
            has_changed = False
            saveSettings(settings)

        if provider == 'OpenAI':
            st.write("## OpenAI Configurations")
            def on_change(): 
                logger.warning(f"Saving API Key for {key}")
                setting['api_key'] = st.session_state[f"{key}_api_key"]
                saveSettings(settings)

            st.text_input(f"{key} API Key", value=setting.get('api_key', ''), key=f"{key}_api_key", on_change=on_change)

            # Configure temperature
            if 'temperature' not in setting:
                setting['temperature'] = default_temp
                saveSettings(settings)

            def on_change_temp():
                setting['temperature'] = st.session_state[f"{key}_temperature"]
                saveSettings(settings)
            st.slider(f"{key} Temperature", 0.0, 1.0, value=setting.get('temperature', 0.7), key=f"{key}_temperature", on_change=on_change_temp,help="""
                Temperatures dictate how much creativity vs precision the AI has when generating text.
                A higher temperature means more creativity, but less precision. A lower temperature means less creativity, but more precision.
                A temperature of 0.0 means the AI will always choose the most likely option.
                A temperature of 1.0 means the AI will always choose the most creative option.
                A temperature of 0.7 is a good balance between creativity and precision.
                """)

        if provider == 'AWS Bedrock':
            st.write("## AWS Bedrock Configurations")

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
                saveSettings(settings)
                has_changed = False

            # Get AWS region to use
            def on_change_region():
                setting['region'] = st.session_state[f"{key}_region"]
                saveSettings(settings)
            
            aws_regions = ['default', 'us-east-1', 'us-west-2']
            selected_region = setting.get('region', 'default')
            region_index = aws_regions.index(selected_region) if selected_region in aws_regions else 0
            st.selectbox(f"{key} Region", aws_regions, index=region_index, on_change=on_change_region)
            
            # Get authentication type to use
            def on_change_auth():
                setting['auth'] = st.session_state[f"{key}_auth"]
                saveSettings(settings)

            aws_auth_types = ['profile', 'iam']
            selected_auth = setting.get('auth', 'profile')
            auth_index = aws_auth_types.index(selected_auth) if selected_auth in aws_auth_types else 0
            auth = st.selectbox(f"{key} Auth", aws_auth_types, index=auth_index)
            
            # Configure specific authentication types
            if auth == 'profile':
                # Get profile to use for authentication
                def on_change_profile():
                    setting['profile'] = st.session_state[f"{key}_profile"]
                    saveSettings(settings)

                st.text_input(f"{key} Profile Name", value=setting.get('profile', 'default'), key=f"{key}_profile", on_change=on_change_profile)
            if auth == 'iam':
                # Get access and secret access keys
                def on_change_key():
                    setting['access_key'] = st.session_state[f"{key}_access_key"]
                    saveSettings(settings)

                st.text_input(f"{key} Access Key", value=setting.get('access_key', ''), key=f"{key}_access_key", on_change=on_change_key)
                
                def on_change_secret():
                    setting['secret_key'] = st.session_state[f"{key}_secret_key"]
                    saveSettings(settings)

                st.text_input(f"{key} Secret Key", value=setting.get('secret_key', ''), key=f"{key}_secret", on_change=on_change_secret)

            # Model Configuration
            if 'model' not in setting:
                if key == 'image':
                    setting['model'] = 'stability.stable-diffusion-xl-v0:1'
                    setting['max_tokens'] = 1024
                else:
                    setting['model'] = 'us.amazon.nova-pro-v1:0'
                    setting['max_tokens'] = 2048

                saveSettings(settings)
            def on_change_model():
                setting['model'] = st.session_state[f"{key}_model"]
                saveSettings(settings)
            st.text_input(f"{key} Model", value=setting.get('model', 'us.amazon.nova-pro-v1:0'), key=f"{key}_model", on_change=on_change_model)

            # Token configuration
            if 'max_tokens' not in setting:
                setting['max_tokens'] = 1024
                saveSettings(settings)
            
            def on_change_max_tokens():
                setting['max_tokens'] = st.session_state[f"{key}_max_tokens"]
                saveSettings(settings)
            st.text_input(f"{key} Max Tokens", value=setting.get('max_tokens', 1024), key=f"{key}_max_tokens", on_change=on_change_max_tokens)

            # Configure temperature
            if 'temperature' not in setting:
                setting['temperature'] = default_temp
                saveSettings(settings)

            def on_change_temp():
                setting['temperature'] = st.session_state[f"{key}_temperature"]
                saveSettings(settings)
            st.slider(f"{key} Temperature", 0.0, 1.0, value=setting.get('temperature', 0.7), key=f"{key}_temperature", on_change=on_change_temp,help="""
                Temperatures dictate how much creativity vs precision the AI has when generating text.
                A higher temperature means more creativity, but less precision. A lower temperature means less creativity, but more precision.
                A temperature of 0.0 means the AI will always choose the most likely option.
                A temperature of 1.0 means the AI will always choose the most creative option.
                A temperature of 0.7 is a good balance between creativity and precision.
                """)

        if provider == 'Api':
            # Get API Information
            def on_change():
                setting['url'] = st.session_state[f"{key}_url"]
                saveSettings(settings)
            st.text_input(f"{key} Url", value=setting.get('url', 'http://localhost:1234/v1'), key=f"{key}_url", on_change=on_change)

            # Get API Key
            def on_change_key():
                setting['api_key'] = st.session_state[f"{key}_api_key"]
                saveSettings(settings)
            st.text_input(f"{key} API Key", value=setting.get('api_key', ''), key=f"{key}_api_key", on_change=on_change_key)

            # Get Model Name
            def on_change_model():
                setting['model'] = st.session_state[f"{key}_model"]
                saveSettings(settings)
            st.text_input(f"{key} Model", value=setting.get('model', ''), key=f"{key}_model", on_change=on_change_model)

            def on_change_max_tokens():
                setting['max_tokens'] = st.session_state[f"{key}_max_tokens"]
                saveSettings(settings)
            st.text_input(f"{key} Max Tokens", value=setting.get('max_tokens', '10370'), key=f"{key}_max_tokens", on_change=on_change_max_tokens)

        if provider == 'Murf':
            st.write("## Murf Configurations")

            # Settings for api key
            def on_change_key():
                setting['api_key'] = st.session_state[f"{key}_api_key"]
                saveSettings(settings)
            st.text_input(f"{key} API Key", value=setting.get('api_key', ''), key=f"{key}_api_key", on_change=on_change_key)

            # Settings for voice
            def on_change():
                setting['voice'] = st.session_state[f"{key}_voice"]
                saveSettings(settings)
            st.text_input(f"{key} Voice", value=setting.get('voice', ''), key=f"{key}_voice", on_change=on_change)

            # Settings for local
            def on_change_local():
                setting['local'] = st.session_state[f"{key}_local"]
                saveSettings(settings)
            st.text_input(f"{key} Local", value=setting.get('local', 'en-US'), key=f"{key}_local", on_change=on_change_local)

            # Settings for model version
            def on_change_model_version():
                setting['model_version'] = st.session_state[f"{key}_model_version"]
                saveSettings(settings)
            st.text_input(f"{key} Model Version", value=setting.get('model_version', 'GEN2'), key=f"{key}_model_version", on_change=on_change_local)

    tab_editing, tab_images, tab_tech, tab_ent, tab_voice = st.tabs(["Editing", "Images", "Technical", "Entertainment", "Voice"])

    with tab_editing:
        AIConfig('content', 0.7)

    with tab_images:
        AIConfig('image', 0.7)

    with tab_tech:
        AIConfig('tech_eval', 0.95)

    with tab_ent:
        AIConfig('ent_eval', 0.95)

    with tab_voice:
        AIConfig('voice', 0.7)
