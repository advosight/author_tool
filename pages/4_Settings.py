import streamlit as st
from pages.views.settings import AIConfig
from utils.storage import Storage

st.write("# Settings")

storage = Storage(None)
settings = storage.getSettings()

if 'gen_ai' not in settings:
    settings['gen_ai'] = []

tab_editing, tab_images, tab_tech, tab_ent, tab_voice = st.tabs(["Editing", "Images", "Technical", "Entertainment", "Voice"])

with tab_editing:
    AIConfig('content', 0.7, settings)

with tab_images:
    AIConfig('image', 0.7, settings)

with tab_tech:
    AIConfig('tech_eval', 0.95, settings)

with tab_ent:
    AIConfig('ent_eval', 0.95, settings)

with tab_voice:
    AIConfig('voice', 0.7, settings)
