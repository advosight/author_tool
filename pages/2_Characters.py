
import streamlit as st
import pandas as pd
from book_maker import Chapter, Book
from views.book_list import book_list

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

if book is None:
    st.write("No book loaded")
    st.stop()

st.write("# Characters")

character_names = book.characters
if len(character_names) == 0:
    st.write("No characters found")
    st.stop()

st.selectbox("Characters", character_names, key="character_name")

if st.session_state.character_name is not None and st.session_state.character_name != "":
    character = book.getLatestCharacter(st.session_state.character_name)
    
    imgCol, descCol = st.columns([1, 8])
    with imgCol:
        st.image(f"data:image/png;base64, {character.thumbnail}")
        st.write(character.name)
    with descCol:
        tabRefs, tabStory, tabAppear, tabExpert = st.tabs(["References", "Story", "Appearance", "Expertise"])
        
        with tabRefs:
            references = character.references
            st.write(references)

            if references == '':
                st.write("No references found")
                
                if st.button(f"Remove {character.name}"):
                    character.delete()
        with tabStory:
            st.text_area("Story", character.description)

        with tabAppear:
            character.visual_description = st.text_area("Appearance", character.visual_description)

            if st.button(f"Regenerate image for {character.name}"):
                character.generateImage()

        with tabExpert:
            def expertiseChange():
                character.expertise = st.session_state.expertise

            st.text_area("Expertise", character.expertise,  key="expertise", on_change=expertiseChange)
