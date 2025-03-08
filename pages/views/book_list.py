import streamlit as st
import utils.logging as lg
from models.book_maker import BookLibrary

logger = lg.getLogger(__name__, 'DEBUG')

def book_list():
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = ''
    if 'book' not in st.session_state:
        st.session_state.book = None

    # List books in a dropdown
    def book_change():
        if 'selected_book' in st.session_state and st.session_state.book_name == st.session_state.selected_book:
            return
        st.session_state.selected_chapter = 0
        st.session_state.selected_book = st.session_state.book_name
        st.session_state.book = library.getBook(st.session_state.book_name)

    library = BookLibrary()
    books = library.listBooks()
    book_index = 0
    book = None
    if len(books) > 0 and 'selected_book' in st.session_state:
        # Get index of the book in the list
        book_index = books.index(st.session_state.selected_book)
    st.selectbox("Books", books, index=book_index, key="book_name", on_change=book_change)
    
    if st.session_state.book is None:
        storyFile = st.file_uploader("Upload story")
        if storyFile is not None:
            st.write(storyFile.name)

            st.session_state.book = library.loadFromContent(storyFile.name, storyFile)
            st.rerun()