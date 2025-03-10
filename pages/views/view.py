import streamlit as st
from pages.views.characters import listCharacters
from pages.views.content_edit import contentEditor, segmentEditor
from models.book_maker import Chapter
from models.llm import getLLM

def viewChapter(chapter: Chapter):

    paragraphs = chapter.content.split("\n\n")
    st.session_state.paragraphs = paragraphs

    with st.sidebar:
        st.divider()

        if st.session_state.get('edit_segment', False) == False and st.button("Edit Segment"):
            paragraphs = st.session_state.paragraphs
            edit_content = ""
            for i in range(len(paragraphs)):
                if st.session_state.get(f"PlayParagraph{i}", False):
                    edit_content += paragraphs[i] + "\n\n"
            st.session_state.edit_text = edit_content
            st.session_state['edit_content'] = edit_content
            st.session_state['edit_segment'] = True
            st.rerun()

        if st.session_state.get('edit_segment', False) and st.button("Done Editing"):
            st.session_state['edit_segment'] = False
            st.rerun()

        if 'audio' not in st.session_state:
            st.session_state.audio = None

        if st.session_state.audio is None:
            st.divider()
            if st.sidebar.button(f"Play Audio"):
                audio_list = []
                for i in range(len(paragraphs)):
                    if st.session_state.get(f"PlayParagraph{i}", False):
                        audio_list.append(i)
                
                st.session_state.audio = chapter.getAudio(audio_list)
                st.rerun()
            if st.sidebar.button("Clear Selected Audio"):
                for i in range(len(paragraphs)):
                    if st.session_state.get(f"PlayParagraph{i}", False):
                        chapter.clearAudio(i)

            st.divider()
        
        if st.session_state.audio is not None:
            st.divider()
            st.audio(st.session_state.audio, format="audio/mp3")
            if st.button("Reset audio player"):
                st.session_state.audio = None
                st.rerun()
            st.divider()

    # Check if LLM is configured and if not show a warning
    if getLLM().is_configured is False:
        st.warning("LLM is not configured. Please configure the LLM in the settings page.")

    # Display Chapter Evaluations
    col1, col2 = st.columns([1, 1])

    with col1:
        if chapter.entertainment_eval is not None:
            help_text = ""
            for feedback in chapter.entertainment_eval.comments:
                help_text += f"- {feedback}\n"
            st.select_slider("Entertainment", value=chapter.entertainment_eval.score, options=range(0, 100), help=help_text)

            if st.button("Refresh Entertainment Feedback", type="tertiary"):
                chapter.evalEntertainment()
                st.rerun()

    with col2:
        if chapter.technical_eval is not None:
            help_text = ""
            for feedback in chapter.technical_eval.comments:
                help_text += f"- {feedback}\n"
            st.select_slider("Technical", value=chapter.technical_eval.score, options=range(0, 100), help=help_text)
        if st.button("Refresh Technical Feedback", type="tertiary"):
            chapter.evalTechnical()
            st.rerun()

    listCharacters(chapter)

    def selectAllChanged():
        to_value = st.session_state.get(f"PlayAllParagraph", False)
        for p in range(len(paragraphs)):
            st.session_state[f"PlayParagraph{p}"] = to_value


    if st.session_state.get('edit_segment', False):
        segmentEditor(st.session_state.get('edit_content', ''), chapter)
    else:
        st.checkbox("Select All", value=True, key="PlayAllParagraph", on_change=selectAllChanged)
        
        for i in range(len(paragraphs)):
            paragraph = paragraphs[i]
            colRadio, colNumber, colParagraph = st.columns([0.7, 0.5, 10])

            colRadio.html(f"<a id=\"paragraph{i}\"></a>")
            colRadio.checkbox(f"Play {i}", value=st.session_state.get(f"PlayParagraph{i}", True), key=f"PlayParagraph{i}", label_visibility="hidden")
            colNumber.write(f"{i}")
            colParagraph.write(paragraph)
