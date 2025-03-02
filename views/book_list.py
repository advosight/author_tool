import streamlit as st
from book_maker import BookLibrary

def book_list():
    # List books in a dropdown
    def book_change():
        if 'selected_book' in st.session_state and st.session_state.book_name == st.session_state.selected_book:
            return
        st.session_state.selected_chapter = 0
        st.session_state.selected_book = st.session_state.book_name

    library = BookLibrary()
    books = library.listBooks()
    book_index = 0
    book = None
    if len(books) > 0 and 'selected_book' in st.session_state:
        # Get index of the book in the list
        book_index = books.index(st.session_state.selected_book)
    st.selectbox("Books", books, index=book_index, key="book_name", on_change=book_change)
    if st.session_state.book_name is not None and st.session_state.book_name != "":
        st.session_state.book = library.getBook(st.session_state.book_name)
        st.rerun()
    else:
        st.session_state.book = None
    
    if st.session_state.book is None:
        storyFile = st.file_uploader("Upload story")
        if storyFile is not None:
            st.write(storyFile.name)

            st.session_state.book = library.loadFromContent(storyFile.name, storyFile)