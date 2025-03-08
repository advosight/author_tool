import streamlit as st
from utils import Storage, getLogger
from models.llm import getLLM
from models.plugin_framework import load_plugin_class

logger = getLogger('Settings')

def saveSettings(settings: dict):
    storage = Storage(None)
    storage.saveSettings(settings)
    llm = getLLM()
    llm.loadConfigurations(settings)

def AIConfig(key: str, default_temp: float, settings: dict):
    llm = getLLM()
    ai_providers = []
    for plugin in llm.plugins:
        if key in plugin['features']:
            ai_providers.append(plugin['name'])

    setting = None
    setting_index = -1
    for i, ai in enumerate(settings['gen_ai']):
        if ai.get('role', None) == key:
            setting = ai
            try:
                setting_index = ai_providers.index(ai.get('type', 'OpenAI'))
            except:
                setting_index = -1
            break
    
    if setting == None:
        # Save default settings if not present
        setting = {'type': ai_providers[0], 'role': key}
        settings['gen_ai'].append(setting)
        saveSettings(settings)
        setting_index = 0
    elif setting_index == -1:
        # The AI specified is not in the list
        setting_index = 0
        setting['type'] = ai_providers[setting_index]
        saveSettings(settings)

    def on_change_ai_provider(val: str):
        logger.warning(f"Changing AI provider for {key} to {val}")
        setting['type'] = val
        saveSettings(settings)

    provider = st.selectbox(f"{key} Provider Type", ai_providers, key=f"{key}_ai_provider", index=setting_index, on_change=lambda: on_change_ai_provider(st.session_state[f"{key}_ai_provider"]))

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

    plugin_def = None
    for plugin in llm.plugins:
        if plugin['name'] == provider:
            plugin_def = plugin
            break
    
    if plugin_def is None:
        st.write(f"Plugin definition not found for {provider}")
        return
    
    pluginClass = load_plugin_class(plugin_def)
    plugin = pluginClass(setting)
    plugin.display_config(key, setting, lambda: saveSettings(settings))
