import streamlit as st
from book_maker import Chapter, Book
import pandas as pd

def listCharacters(chapter: Chapter):
    characters = chapter.characters
    if len(characters) > 0:
        columns = st.columns(len(characters))
        for i in range(len(characters)):
            with columns[i]:
                st.image(f"data:image/png;base64, {characters[i].thumbnail}")
                st.write(characters[i].name)

def viewChapterCharacters(chapter: Chapter):
    characters = chapter.characters

    colSelect, colAdd = st.columns([7, 3])
    selectedCharacter = ''
    with colSelect:
        selectedCharacter = st.selectbox("Select a character", [''] + chapter.book.characters, index=0)
    with colAdd:
        if st.button("Add Character"):
            if selectedCharacter != '':
                print(f"Adding character {selectedCharacter}")
                chapter.addCharacter(selectedCharacter)


    if len(characters) > 0:
        thumbnails = []
        names = []
        descriptions = []
        actions = []

        for character in chapter.characters:
            thumbnails.append(f"data:image/png;base64,{character.thumbnail}")
            names.append(character.name)
            descriptions.append(character.description)
            actions.append(False)

        df = pd.DataFrame({
            'action': actions,
            'thumbnail': thumbnails,
            'name': names,
            'description': descriptions
        })
        def onCharacterChange():
            characterGrid = st.session_state['characterGrid']
            print(characterGrid)
            # Update the characters in the chapter
            for i in range(len(characters)):
                print(f"Updating character {i}, {characters[i].name}")
                # find the character for the line in the dataframe
                for j in characterGrid['edited_rows']:
                    print(f"On key {j}")
                    
                    item = characterGrid['edited_rows'][j]
                    if j == i:
                        print(f"Updating character {i}, with {item}")
                        if item.get('name') is not None:
                            characters[i].name = item['name']
                        if item.get('description') is not None:
                            characters[i].description = item['description']
                        break

        st.data_editor(df, column_config={
            "name": st.column_config.TextColumn(
                "Name",
                help="Streamlit **widget** commands",
                default="",
                width="medium",
                required=True
            ),
            "description": st.column_config.TextColumn(
                "Description",
                help="Streamlit **widget** commands",
                default="",
                width="large",
                required=True,
            ),
            "thumbnail": st.column_config.ImageColumn("Thumbnail", help="Streamlit **widget** commands", width="medium"),
            "action": st.column_config.CheckboxColumn("Action", help="Streamlit **widget** commands", width="small", required=False)
        }, key="characterGrid", on_change=onCharacterChange)

        if st.button("Delete"):
            # Delete the selected characters
            print(st.session_state['characterGrid'])
            for i in st.session_state['characterGrid']['edited_rows']:
                item = st.session_state['characterGrid']['edited_rows'][i]
                if item.get('action') is True:
                    name = names[i]
                    print(f"Deleting character {i}, {name}")
                    index = -1
                    for char in characters:
                        if char.name == name:
                            char.delete()
                            break
                    
                    df.drop(i)
                    break
    else:
        st.write("No characters found")
