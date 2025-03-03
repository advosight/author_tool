import streamlit as st
from views.book_list import book_list
from views.view import viewChapter
from views.content_edit import contentEditor, segmentEditor
from views.characters import listCharacters, viewChapterCharacters
from streamlit_navigation_bar import st_navbar

with st.sidebar:
    # Get book, and if no book let user pick a book
    book = None
    if 'book' in st.session_state:
        book = st.session_state.book

    if book is None:
        book_list()
        st.stop()

    # A book is selected
    st.write(f"# {book.title}")
    
    # Let user pick which chapter
    def buildChapterList():
        chapters = []
        for chapter in book.chapters:
            chapters.append(str(chapter))
        
        st.session_state.chapters = chapters

    buildChapterList()
    
    if "selected_chapter" not in st.session_state:
        # No chapter selected, so get the last chapter of the book
        st.session_state.selected_chapter = len(chapters) - 1

    def onChapterChange():
        st.session_state.chapter = book.getChapter(st.session_state.selected_chapter_name)

    st.selectbox("Chapters", st.session_state.chapters, key="selected_chapter_name", index=st.session_state.selected_chapter, on_change=onChapterChange)

    # Add ability for user to add a new chapter
    if st.button("Add Chapter"):
        chapter = book.addChapter(st.session_state.chapter.number)
        buildChapterList()
        st.session_state.selected_chapter = chapter.number - 1
        st.rerun()

    onChapterChange()

if 'chapter' not in st.session_state or st.session_state.chapter is None:
        st.write("No chapter loaded")
        st.stop()

chapter = st.session_state.chapter

# Chapter details
st.write('# ' + chapter.name)

onView = st.selectbox("Views", ["View", "Edit", "Summary", "Characters", "Technical", "Entertainment"], key="writing_view")

if st.session_state.writing_view == "View":
    viewChapter(chapter)
    
if st.session_state.writing_view == "Edit":
    contentEditor(book, chapter)

if st.session_state.writing_view == "Summary":
    st.write(chapter.summary)

if st.session_state.writing_view == "Characters":
    viewChapterCharacters(chapter)

if st.session_state.writing_view == "Technical":
    if st.button("Re-evaluate Technical"):
        chapter.evalTechnical()
    st.write(chapter.technical_eval)

if st.session_state.writing_view == "Entertainment":
    if st.button("Re-evaluate Entertainment"):
        chapter.evalEntertainment()
    
    st.write(chapter.entertainment_eval)