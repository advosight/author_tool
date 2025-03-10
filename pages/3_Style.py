import streamlit as st
from pages.views.book_list import book_list

book = None
with st.sidebar:
    if 'book' not in st.session_state or st.session_state.book is None:
        book_list()
        st.stop()

    book = st.session_state.book
    st.write(f"# {book.title}")

if 'book' not in st.session_state:
    st.write("No book loaded")
    st.stop()

mode = st.selectbox("Mode", ["View", "Edit"])

if book is None:
    st.write("No book selected")
    st.stop()

if mode == "View":
    st.write(book.writing_style)
else:
    btn_settings_editor_btns = [{
        "name": "save",
        "feather": "Save",
        "hasText": True,
        "alwaysOn": True,
        "commands": ["submit"],
        "style": {"top": "0rem", "right": "0.4rem"}
    }]
    writing_style = st.text_area("Writing Style", book.writing_style, height=500)

    if writing_style is not None:
        book.writing_style = writing_style