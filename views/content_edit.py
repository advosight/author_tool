import streamlit as st
from code_editor import code_editor
from book_maker import Book, Chapter
from llm import getLLM
from streamlit_quill import st_quill

def segmentEditor(original_text: str, chapter: Chapter):
    if original_text is None:
        return
    
    original_text = original_text.strip()
    print(f"\"{original_text}\"")
    start_pos = 0
    if original_text != '':
        try:
            start_pos = chapter.content.index(original_text)
        except:
            start_pos = -1

    if start_pos == -1:
        return

    end_pos = start_pos + len(original_text)

    chatCol, displayCol = st.columns([0.3, 0.7])
    if "original_text" not in st.session_state:
        st.session_state.original_text = original_text
        st.session_state.edit_text = original_text

    # Navigation Controls
    with chatCol:
        messages = st.container(height=300)
        conversation = []

        messages.chat_message("ai").write("Describe the story or changes you want.")

        prompt = st.chat_input("Enter a prompt")
        if prompt:
            messages.chat_message("user").write(prompt)
            conversation.append({ "role": "user", "content": prompt })

            llm = getLLM()
            origin = [ { "role": "user", "content": f"I will describe the fictional story and changes wanted, and you will only return the updates to the text without commentary. The writing style for this book is as follows: {chapter.book.writing_style}" } ]
            for character in chapter.characters:
                origin.append({ "role": "ai", "content": "I will use that in future content"})
                origin.append({ "role": "user", "content": f"The character {character.name} visually is {character.visual_description}. The character's story arch so far: {character.summary}" })
            
            origin.append({ "role": "ai", "content": "I will use that in future content"})

            original_text_index = chapter.content.index(original_text)
            if original_text_index > 0:
                origin.append({ "role": "user", "content": f"The current chapter up to this point is: {chapter.content[:original_text_index]}"})
                origin.append({ "role": "ai", "content": "I will use that in future content"})

            if st.session_state.edit_text is not None:
                origin.append({ "role": "user", "content": f"Use the following text as a basis for the request, and ensure that all parts of the story the text covers are returned in the response. Only return the story without any commentary: {st.session_state.edit_text}"})

            response = llm.conversation(origin + conversation, 0.7)
            conversation.append({ "role": "ai", "content": response })
            messages.chat_message("ai").write("The text has been updated")
            st.session_state.prev_text = st.session_state.edit_text
            st.session_state.edit_text = response

    with displayCol:
        section_edit_buttons = [{
                "name": "Update",
                "feather": "Save",
                "hasText": True,
                "alwaysOn": True,
                "commands": ["submit"],
                "responseType": "Update",
                "style": {"top": "0rem", "right": "0.4rem"}
            }
        ]

        col1, col2 = st.columns([1, 1])
        if col1.button("Replace in document"):
            content_text = chapter.content[start_pos:end_pos]
            if content_text == original_text:
                print("Replacing text")
                chapter.content = chapter.content[:start_pos] + st.session_state.edit_text_area + chapter.content[end_pos:]
            else:
                print("Text not found in document")

        if col2.button("Revert to previous"):
            st.session_state.edit_text = st.session_state.prev_text

        def text_change():
            st.session_state.edit_text = st.session_state.edit_text_area

        st.session_state.edit_text = st.text_area("Edit the text", value=st.session_state.edit_text, key="edit_text_area", height=300, on_change=text_change)

        st.write(original_text)

def contentEditor(book: Book, chapter: Chapter):
    if chapter.content is None:
        return

    colEdit, colEval = st.columns([0.8, 0.2])

    with colEdit:

        def text_change():
            chapter.content = st.session_state.chapter_text

        st.text_area(
            "Chapter Text",
            value=chapter.content, 
            key="chapter_text",
            on_change=text_change,
            height=400)

    with colEval:
        st.write("Evaluation")
        st.write(chapter.technical_eval)