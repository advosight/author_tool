import streamlit as st
from llm import getLLM
from pages.views.book_list import book_list
from utils import getLogger
from book_maker import Book, Chapter

logger = getLogger('Author Tool')

st.set_page_config(page_title="Author Tool")

st.write("# Author Tool")

llm = getLLM()
llm.loadConfigurations()

if not llm.is_configured:
    logger.info("LLM is not configured")
    st.switch_page("pages/4_Settings.py")
    st.stop()


# List books in a dropdown
book_list()

if 'book' not in st.session_state or st.session_state.book is None:
    st.write("No book selected")
    st.stop()

book: Book = st.session_state.book

def on_change_name():
    book.title = st.session_state.book_title

st.text_input("Book Title", value=book.title, key="book_title", on_change=on_change_name)

def chapterLayout(chapter: Chapter):
    colNum, colName, colDel = st.columns([1, 9, 1])
    with colNum:
        chapter_key = f"chapter_number_{i}"
        def on_change_chapter_number(key: str):
            cur_number = st.session_state[key]

            print(f"Changing chapter {key} number to {cur_number}")

            # Walk through chapters in reverse, incrementing chapter number until
            # we reach the current chapter
            for chIndex in range(len(book.chapters) - 1, cur_number - 1, -1):
                ch: Chapter = book.chapters[chIndex]
                if ch.number >= cur_number:
                    ch.number += 1
            book.chapters[cur_number - 1].number = cur_number
            
            for chIndex in range(cur_number, len(book.chapters)):
                ch: Chapter = book.chapters[chIndex]
                if ch.number != chIndex + 1:
                    ch.number = chIndex + 1
        st.number_input("Chapter", 0, 999, chapter.number, key=chapter_key, on_change=lambda: on_change_chapter_number(chapter_key))
    with colName:
        def on_change_chapter(index: int):
            print(f"Updating chapter name at index {i}")
            chapter.name = st.session_state[f"chapter_name_{i}"]

        st.text_input("Name", value=chapter.name, key=f"chapter_name_{i}", on_change=lambda: on_change_name(i))
    
    with colDel:
        st.write("")
        st.write("")
        if st.button("🗑", key=f"chapter_delete_{i}", type="tertiary"):
            book.removeChapter(chapter)
    
for i in range(0, len(book.chapters)):
    chapter = book.chapters[i]
    chapterLayout(chapter)