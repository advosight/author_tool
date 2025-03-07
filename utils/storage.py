import os
from PIL import Image
from io import BytesIO
import shutil
import json
import logging as lg

logger = lg.getLogger(__name__)

def createDirIfNeeded(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

class Storage:
    def __init__(self, title: str):
        self.title = title

        # Create directory to store temporary files
        self.root = None
        self.libraryRoot = ".data"
        createDirIfNeeded(self.libraryRoot)

        if title is not None:
            self.root = ".data/" + title
            createDirIfNeeded(self.root)
            createDirIfNeeded(self.root + "/chapters")
            createDirIfNeeded(self.root + "/summaries")
            createDirIfNeeded(self.root + "/characters")

    def exists(self):
        """ Checks to see if the book exists"""
        return os.path.exists(f"{self.root}")

    def chapterExists(self, chapter: int) -> bool:
        """ Checks to see if the chapter exists

        Args:
            chapter (int): The chapter number in the book

        Returns:
            bool: True if the chapter exists
        """
        return os.path.exists(f"{self.root}/chapters/{chapter}")

    def saveChapterName(self, chapter: int, name: str):
        """ Saves the name of the chapter

        Args:
            chapter (str): The chapter number
            name (str): The name of the chapter
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}"):
            os.makedirs(f"{self.root}/chapters/{chapter}")

        with open(f"{self.root}/chapters/{chapter}/name.md", "w") as f:
            f.write(name)
            f.close()

    def loadChapterName(self, chapter: int) -> str:
        """ Load a chapter's name

        Args:
            chapter (int): The number of the chapter

        Returns:
            str: The name of the chapter
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}/name.md"):
            return f"Chapter {chapter}"

        with open(f"{self.root}/chapters/{chapter}/name.md", "r") as f:
            name = f.read()
            f.close()
            return name

    def saveChapterContent(self, chapter: int, content: str):
        """ Saves the contents of a chapter for the book

        Args:
            chapter (int): The chapter number in the book
            content (str): The content of the chapter
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}"):
            os.makedirs(f"{self.root}/chapters/{chapter}")
        with open(f"{self.root}/chapters/{chapter}/content.md", "w") as f:
            f.write(content)
            f.close()

    def loadChapterContent(self, chapter: int) -> str:
        """Loads the chapter contents

        Args:
            chapter (int): The chapter number in the book

        Returns:
            str: The content of the chapter
        """
        with open(f"{self.root}/chapters/{chapter}/content.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveChapterSummary(self, chapter: int, content: str):
        """ Saves a chapter summary

        Args:
            chapter (int): The chapter number in the book
            content (str): The chapter summary
        """
        print(f"Saving chapter {chapter} summary")
        if not os.path.exists(f"{self.root}/chapters/{chapter}"):
            os.makedirs(f"{self.root}/chapters/{chapter}")
            
        with open(f"{self.root}/chapters/{chapter}/summary.md", "w") as f:
            f.write(content)
            f.close()

    def loadChapterSummary(self, chapter: int) -> str:
        """ Loads the chapter summary

        Args:
            chapter (int): The chapter number in the book

        Returns:
            str: The chapter summary
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}/summary.md"):
            return None

        with open(f"{self.root}/chapters/{chapter}/summary.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def loadChapterCharacters(self, chapter: int) -> [str]:
        """Loads the list of characters for the chapter

        Args:
            chapter (int): The chapter number in the book

        Returns:
            [str]: An array of character names
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}/characters.md"):
            return None

        with open(f"{self.root}/chapters/{chapter}/characters.md", "r") as f:
            content = f.read()
            f.close()
            return content.split("\n")

    def saveChapterCharacters(self, chapter: int, characters: [str]):
        """Saves the list of characters that are in the chapter

        Args:
            chapter (int): The chapter number in the book
            characters ([str]): An array of character names
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}"):
            os.makedirs(f"{self.root}/chapters/{chapter}")

        with open(f"{self.root}/chapters/{chapter}/characters.md", "w") as f:
            f.write("\n".join(characters))
            f.close()

    def saveCharacter(self, chapter: int, character: str, content: str):
        """Saves a character's description summary for the chapter

        Args:
            chapter (int): The chapter number in the book
            character (str): The character's name
            content (str): The summary for the character for the chapter

        """
        if not os.path.exists(f"{self.root}/characters/{chapter}/"):
            os.makedirs(f"{self.root}/characters/{chapter}")

        character_root = f"{self.root}/characters/{chapter}/characters"
        if not os.path.exists(character_root):
            os.makedirs(character_root)
        with open(f"{character_root}/{character}.md", "w") as f:
            f.write(content)
            f.close()

    def loadCharacterDescription(self, chapter: int, character: str):
        """Loads a character description

        Args:
            chapter (int): The chapter number in the book
            character (str): The character's name
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}/characters/{character}.md"):
            return None

        with open(f"{self.root}/chapters/{chapter}/characters/{character}.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveCharacterDescription(self, chapter: int, character: str, content: str):
        """Saves a character description

        Args:
            chapter (int): The chapter number in the book
            character (str): The name of the character
            content (str): The character description
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        if not os.path.exists(chapter_root):
            os.makedirs(chapter_root)

        character_root = f"{chapter_root}/characters"
        if not os.path.exists(character_root):
            os.makedirs(character_root)
        with open(f"{character_root}/{character}.md", "w") as f:
            f.write(content)
            f.close()

    def characterExists(self, chapter: int, name: str) -> bool:
        """Checks to see if the character exists in the book

        Args:
            chapter (int): The chapter number in the book
            name (str): The name of the character
        """
        return os.path.exists(f"{self.root}/chapters/{chapter}/characters/{name}.md")

    def listChapters(self):
        return os.listdir(f"{self.root}/chapters")

    def listBooks(self):
        # Get a list of all directories
        directories = [d for d in os.listdir(self.libraryRoot) if os.path.isdir(os.path.join(self.libraryRoot, d))]

        return directories

    def loadCharacterVisualDescription(self, character: str) -> str:
        """ Loads the visual description of a character

        Args:
            character (str): The name of the character

        Returns:
            str: The visual description of the character
        """
        if not os.path.exists(f"{self.root}/characters/{character}/description.md"):
            return None

        with open(f"{self.root}/characters/{character}/description.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveCharacterVisualDescription(self, character: str, content: str):
        """ Saves the visual description of the character

        Args:
            character (str): The name of the character
            content (str): The visual description of the character
        """
        character_root = f"{self.root}/characters/{character}"
        if not os.path.exists(character_root):
            os.makedirs(character_root)

        with open(f"{character_root}/description.md", "w") as f:
            f.write(content)
            f.close()

    def loadCharacterThumbnail(self, character: str) -> any:
        """ Loads a character's thumbnail from the image stored for the character

        Args:
            character (str): The name of the character

        Returns:
            any: The image byte buffer
        """
        if not os.path.exists(f"{self.root}/characters/{character}/thumbnail.png"):
            return None

        
        with open(f"{self.root}/characters/{character}/thumbnail.png", "rb") as f:
            content = f.read()
            f.close()
            
            image = Image.open(BytesIO(content))
            resized_image = image.resize((500, 500))
            output_buffer = BytesIO()
            resized_image.save(output_buffer, format="PNG")
            return output_buffer.getvalue()

    def saveCharacterThumbnail(self, character: str, content: any):
        """ Saves a thumbnail for the character

        Args:
            character (str): The name of the character
            content (any): The png data for the image
        """
        character_root = f"{self.root}/characters/{character}"
        if not os.path.exists(character_root):
            os.makedirs(character_root)

        with open(f"{character_root}/thumbnail.png", "wb") as f:
            f.write(content)
            f.close()

    def getCharacterNames(self):
        """Gets all the character names for the book"""
        return os.listdir(f"{self.root}/characters")

    def loadWritingStyle(self):
        """ Loads the writing style for the book"""

        if not os.path.exists(f"{self.root}/writing_style.md"):
            return None

        with open(f"{self.root}/writing_style.md", "r") as f:
            content = f.read()
            f.close()
            return content
    
    def saveWritingStyle(self, content: str):
        """ Saves the notes on the writing style

        Args:
            content (str): The notes on the writing style
        """
        with open(f"{self.root}/writing_style.md", "w") as f:
            f.write(content)
            f.close()

    def renameCharacter(self, chapter: int, old_name: str, new_name: str):
        """Rename character in chapter characters

        Args:
            chapter (int): The chapter number
            old_name (str): The name the character used to have
            new_name (str): The new name of the character
        """
        chapterCharacters = self.loadChapterCharacters(chapter)

        # Check to see if character is in list of chapter characters
        if old_name in chapterCharacters:
            print(f"The name {old_name} was found in the characters")
            # replace old name with new name in chapter characters
            chapterCharacters.remove(old_name)
            print(f"Removed character {chapterCharacters}, {new_name}")
            chapterCharacters.append(new_name)

            print(f"Saving characters {chapterCharacters}")

            self.saveChapterCharacters(chapter, chapterCharacters)

            # remove chapter character summary
            if os.path.exists(f"{self.root}/chapters/{chapter}/characters/{old_name}.md"):
                os.remove(f"{self.root}/chapters/{chapter}/characters/{old_name}.md")
    
    def removeCharacter(self, name: str):
        """Removes a character from the book
        Args:
            name (str): The name of the character
        """
        # remove character from all chapters
        for chapter in self.listChapters():
            if os.path.exists(f"{self.root}/chapters/{chapter}/characters/{name}.md"):
                os.remove(f"{self.root}/chapters/{chapter}/characters/{name}.md")

        # remove character from characters folder
        if os.path.exists(f"{self.root}/characters/{name}"):
            # Remove directory and all contents
            shutil.rmtree(f"{self.root}/characters/{name}")


    def deleteCharacter(self, chapter: int, name: str):
        """Deletes a character from the chapter
        Args:
            chapter (int): The chapter number
            name (str): The name of the character
        """
        chapterCharacters = self.loadChapterCharacters(chapter)

        # Check to see if character is in list of chapter characters
        if name in chapterCharacters:
            print(f"The name {name} was found in the characters")
            # replace old name with new name in chapter characters
            chapterCharacters.remove(name)

            print(f"Saving characters {chapterCharacters}")

            self.saveChapterCharacters(chapter, chapterCharacters)

            # remove chapter character summary
            if os.path.exists(f"{self.root}/chapters/{chapter}/characters/{name}.md"):
                os.remove(f"{self.root}/chapters/{chapter}/characters/{name}.md")
    
    def getParagraphAudio(self, chapter: int, paragraph: int) -> any:
        """Gets the audio for the paragraph
        Args:
            chapter (int): The chapter number
            paragraph (int): The paragraph number
        """
        if not os.path.exists(f"{self.root}/chapters/{chapter}/audio/paragraph_{paragraph}.mp3"):
            return None

        with open(f"{self.root}/chapters/{chapter}/audio/paragraph_{paragraph}.mp3", "rb") as f:
            content = f.read()
            f.close()
            return content

    def saveParagraphAudio(self, chapter: int, paragraph: int, audio: any):
        """Saves the audio for the paragraph
        Args:
            chapter (int): The chapter number
            paragraph (int): The paragraph number
            audio (any): The audio data
        """
        # Validate folder exists
        chapter_root = f"{self.root}/chapters/{chapter}/audio"
        if not os.path.exists(chapter_root):
            os.makedirs(chapter_root)

        # See if we're saving or deleting a file
        file_name = f"{chapter_root}/paragraph_{paragraph}.mp3"
        if audio is not None:
            with open(file_name, "wb") as f:
                f.write(audio)
                f.close()
        else:
            # Delete audio file if it exists
            if os.path.exists(file_name):
                os.remove(file_name)

    def hasCharacterSummary(self, chapter: int, character: str) -> bool:
        """Checks to see if the character summary exists for the chapter

        Args:
            chapter (int): The chapter number
            character (str): The name of the character

        Returns: True if the summary exists
        """
        return os.path.exists(f"{self.root}/chapters/{chapter}/characters/{character}_summary.md")

    def loadCharacterSummary(self, chapter: int, character: str):
        """Loads the summary of the character for everything up to the chapter

        Args:
            chapter (int): The chapter number
            character (str): The name of the character
        """
        characters_dir = f"{self.root}/chapters/{chapter}/characters"
        if not os.path.exists(f"{characters_dir}/{character}_summary.md"):
            return None

        with open(f"{characters_dir}/{character}.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveCharacterSummary(self, chapter: int, character: str, content: str):
        """Saves the summary of the character for everything up to the chapter
        Args:
            chapter (int): The chapter number
            character (str): The name of the character
            content (str): The summary of the character
        """
        characters_dir = f"{self.root}/chapters/{chapter}/characters"
        if not os.path.exists(characters_dir):
            os.makedirs(characters_dir)

        with open(f"{characters_dir}/{character}_summary.md", "w") as f:
            f.write(content)
            f.close()

    def loadCharacterExpertise(self, character: str) -> str:
        """Loads the expertise of the character

        Args:
            character (str): The name of the character

        Returns:
            str: The expertise of the character
        """
        if not os.path.exists(f"{self.root}/characters/{character}/expertise.md"):
            return None

        with open(f"{self.root}/characters/{character}/expertise.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveCharacterExpertise(self, character: str, content: str):
        """Saves the expertise of the character

        Args:
            character (str): The name of the character
            content (str): The expertise of the character
        """
        character_root = f"{self.root}/characters/{character}"
        if not os.path.exists(character_root):
            os.makedirs(character_root)

        with open(f"{character_root}/expertise.md", "w") as f:
            f.write(content)
            f.close()

    def loadChapterTechnicalEval(self, chapter: int):
        """Loads the technical evaluation of the chapter
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        if not os.path.exists(f"{chapter_root}/technical_eval.md"):
            return None

        # Load the technical evaluation
        with open(f"{chapter_root}/technical_eval.md", "r") as f:
            content = f.read()
            f.close()
            return content

    def saveChapterTechnicalEval(self, chapter: int, content: str):
        """Saves the technical evaluation of the chapter

        Args:
            chapter (int): The chapter number
            content (str): The technical evaluation of the chapter
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        if not os.path.exists(chapter_root):
            os.makedirs(chapter_root)

        with open(f"{chapter_root}/technical_eval.md", "w") as f:
            f.write(content)
            f.close()

    def loadChapterEntertainmentEval(self, chapter: int) -> str:
        """Loads the entertainment evaluation of the chapter
        Args:
            chapter (int): The chapter number
        
        Returns:
            The entertainment eval
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        if not os.path.exists(f"{chapter_root}/entertainment_eval.md"):
            return None

        # Load the entertainment evaluation
        with open(f"{chapter_root}/entertainment_eval.md", "r") as f:
            content = f.read()
            f.close()
            return content
        
    def saveChapterEntertainmentEval(self, chapter: int, content: str):
        """Saves the entertainment evaluation of the chapter
        Args:
            chapter (int): The chapter number
            content (str): The entertainment evaluation of the chapter
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        if not os.path.exists(chapter_root):
            os.makedirs(chapter_root)

        with open(f"{chapter_root}/entertainment_eval.md", "w") as f:
            f.write(content)
            f.close()

    def getSettings(self):
        """Gets the settings for tool

        Returns:
            The settings for the book
        """
        if not os.path.exists(f"{self.libraryRoot}/settings.json"):
            return {}

        with open(f"{self.libraryRoot}/settings.json", "r") as f:
            content = f.read()
            f.close()
            return json.loads(content)
        
    def saveSettings(self, settings: dict):
        """Saves the settings for the book

        Args:
            settings (dict): The settings for the book
        """
        with open(f"{self.libraryRoot}/settings.json", "w") as f:
            f.write(json.dumps(settings, indent=4))
            f.close()

    def moveChapterNumber(self, chapter: int, new_number: int):
        """Moves the chapter to a new number
        Args:
            chapter (int): The chapter number
            new_number (int): The new chapter number
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        new_root = f"{self.root}/chapters/{new_number}"

        logger.info(f"Moving chapter {chapter} to {new_number}")
        # Move directory from chapter_root to new_root
        shutil.move(chapter_root, new_root)

    def deleteChapter(self, chapter: int):
        """Deletes the chapter
        Args:
            chapter (int): The chapter number
        """
        chapter_root = f"{self.root}/chapters/{chapter}"
        logger.info(f"Deleting chapter {chapter}")
        # Delete directory and all contents
        shutil.rmtree(chapter_root)
