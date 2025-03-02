import streamlit as st
from llm import getLLM
from views.book_list import book_list
from views.settings import settingsView
from utils import getLogger

logger = getLogger('Author Tool')

st.set_page_config(page_title="Author Tool")

# Remove whitespace from the top of the page and sidebar
# st.markdown("""
#         <style>
#                .block-container {
#                     padding-top: 1rem;
#                     padding-bottom: 0rem;
#                     padding-left: 5rem;
#                     padding-right: 5rem;
#                 }
#                 .stMainBlockContainer {
#                     padding-left: 10px;
#                     padding-right: 10px;
#                     max-width: 100%;
#                 }
#         </style>
#         """, unsafe_allow_html=True)


st.write("# Author Tool")

llm = getLLM()
llm.loadConfigurations()

if not llm.is_configured:
    logger.info("LLM is not configured")
    settingsView()
    st.stop()


# List books in a dropdown
book_list()

