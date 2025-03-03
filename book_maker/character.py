from utils import Storage, getLogger
from llm import getLLM
import base64

logger = getLogger('Character', 'DEBUG')

class Character:
    def __init__(self, book: any, chapter: any, name: str, storage: Storage):
        self.book = book
        self.chapter = chapter
        self.storage = storage
        self._name = name
        self._description = None
        self.prevDescription = None
        self._thumbnail = None
        self._summary = None
        self._visual_description = None
        self._expertise = None
        self.llm = getLLM()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name: str):
        if(name == self._name or name == "" or name is None):
            return ""

        print(f"Renaming {self._name} to {name}")
        self.storage.renameCharacter(self.chapter.number, self._name, name)
        self._name = name
        self._description = None
        self._thumbnail = None

    @property
    def description(self):
        if self._description is not None:
            return self._description

        storedDescription = self.storage.loadCharacterDescription(self.chapter.number, self.name)
        if storedDescription is not None:
            self._description = storedDescription
            return self._description

        prevDescriptions = []

        # find the same character in a previous chapter going through in reverse order
        if self.chapter.number > 1:
            for i in range(1, self.chapter.number - 1):
                prevChapter = self.book.chapters[i]
                for prevCharacter in prevChapter.characters:
                    if prevCharacter.name == self.name:
                        prevDescriptions.append(prevCharacter.description)

                        if self._thumbnail is None:
                            self._thumbnail = prevCharacter.thumbnail
                        break

        if self.chapter.content is None and len(prevDescription) == 0:
            return "No chapter content found"
        if self.chapter.content is None:
            return prevDescription[len(prevDescription) - 1]

        if len(prevDescriptions) > 0:
            prevDescription = "\n\n".join(prevDescriptions)
            self._description = self.llm.conversation([
                { "role": "user", "content": f"""
You are a literature professor. For the character {self.name}, the following describes the character and their growth over the course of the book.

{prevDescription}""" },
                { "role": "assistant", "content": "I will use the previous to answer any future questions"},
                { "role": "user", "content": f"Summarize the character {self.name} and their story in 500 words. This should include their growth through this chapter and their relationships with others as a summary. It should not include any forward looking assumptions or what is expected to come. Only respond back with the analysis. Use the following chapter as information for the updated summary: {self.chapter.content}"}
            ])
        else:
            self._description = self.llm.prompt(f"Summarize the character {self.name} and their story in 500 words. Only respond with the analysis. The following is the chapter content: {self.chapter.content}")

        if self._description is None:
            return "No description found"

        self.storage.saveCharacterDescription(self.chapter.number, self.name, self.description)
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self.storage.saveCharacterDescription(self.chapter.number, self.name, self.description)

    @property
    def visual_description(self):
        if self._visual_description is not None:
            return self._visual_description
        
        self._visual_description = self.storage.loadCharacterVisualDescription(self.name)
        if self._visual_description is not None:
            return self._visual_description
        
        self.visual_description = self.llm.prompt(f"Create a visual description of the character {self.name}. Keep the description to less than 500 characters and only include the visual description in the response: {description}")
        self.storage.saveCharacterVisualDescription(self.name, visual_description)

        return self.visual_description

    @visual_description.setter
    def visual_description(self, value):
        self._visual_description = value
        self.storage.saveCharacterVisualDescription(self.name, self._visual_description)

    @property
    def thumbnail(self):
        if self._thumbnail is not None:
            return self._thumbnail

        thumbnail = self.storage.loadCharacterThumbnail(self.name)
        if thumbnail is not None:
            self._thumbnail = base64.b64encode(thumbnail).decode('utf-8')
            return self._thumbnail

        return self.generateImage()

    @property
    def summary(self):
        """Returns the summary of the character"""
        if self._summary is not None:
            return self._summary

        self._summary = self.storage.loadCharacterSummary(self.chapter.number, self.name)
        if self._summary is not None:
            return self._summary

        if self.chapter.number == 0:
            self._summary = ""
            return self._summary

        prev_character = None
        prev_chapter = None

        # find the last chapter that had this character
        for i in range(self.chapter.number - 2, 0, -1):
            prev_chapter = self.book.chapters[i]
            prev_character = prev_chapter.getCharacter(self.name)
            if prev_character is not None:
                break
        
        if prev_character is None:
            self._summary = ""
            self.storage.saveCharacterSummary(self.chapter.number, self.name, self._summary)
            return self._summary
        
        messages = []

        if self.storage.hasCharacterSummary(prev_chapter.number, prev_character.name):
            messages.append({ "role": "user", "content": f"The following is a summary of the character {self.name}:{prev_character.summary}" })
        else:
            # Walk through chapters from start to the prev_chapter and generate
            # summaries in order to avoid recursion
            for i in range(0, prev_chapter.number - 2):
                chapter = self.book.chapters[i]
                char = chapter.getCharacter(self.name)
                if char is not None:
                    print(f"Loading summary for chapter {chapter.number}, for {char.name}")
                    temp = char.summary

        if prev_character.summary != None:
            messages.append({ "role": "user", "content": f"You are a literature professor. For the character {self.name}, the following describes the character and their growth over the course of the book:{prev_character.summary}" })
        else:
            messages.append({ "role": "user", "content": f"You are a literature professor. For the character {self.name}, this is the first time they're appearing in the story" })

        messages.append({ "role": "assistant", "content": "I will use the previous to answer any future questions" })
        messages.append({ "role": "user", "content": f"The following is new content. Create a new summary of the character's story from only their own perspective (3rd person limited) by including this content and all past content: {self.chapter.content}"})
        self._summary = self.llm.conversation(messages, 0.0)

        self.storage.saveCharacterSummary(self.chapter.number, self.name, self._summary)
        return self._summary
        
    @summary.setter
    def summary(self, value):
        self._summary = value
        self.storage.saveCharacterSummary(self.chapter.number, self.name, self._summary)

    def delete(self):
        """Deletes the character from the storage"""
        for i in range(len(self.chapter.characters)):
            if self.chapter.characters[i].name == self.name:
                self.chapter.characters.pop(i)
                break

        self.storage.deleteCharacter(self.chapter.number, self.name)

        if self.references == "":
            self.storage.removeCharacter(self.name)

    @property
    def references(self):
        """Returns the chapter references of the character"""
        retval = []
        for chapter in self.chapter.book.chapters:
            for character in chapter.characters:
                if character.name == self.name:
                    retval.append(str(chapter.number))
                    break
        return ", ".join(retval)

    @property
    def expertise(self) -> str:
        """Returns the character's expertise"""
        if self._expertise is not None:
            return self._expertise

        logger.info(f"Loading expertise from storage for {self.name}")
        self._expertise = self.storage.loadCharacterExpertise(self.name)
        if self._expertise is not None:
            return self._expertise

        logger.info(f"Generating expertise for {self.name}")
        self._expertise = self.llm.prompt(f"Create a list of the professional expertise for the character {self.name}. Only include the list in the response: {self.description}")
        
        logger.info(f"Expertise for {self.name}: {self._expertise}")
        if self._expertise is not None:
            self.storage.saveCharacterExpertise(self.name, self._expertise)

        return self._expertise

    @expertise.setter
    def expertise(self, value):
        self._expertise = value
        self.storage.saveCharacterExpertise(self.name, self._expertise)

    def generateImage(self) -> any:
        print("Getting thumbnail for " + self.name)
        thumbnail = self.llm.image(f"Create a thumbnail for the character {self.name} based on the visual description: {self.visual_description}")
        print("Thumbnail generated")

        if thumbnail is None:
            return None

        self.storage.saveCharacterThumbnail(self.name, thumbnail)
        self._thumbnail = base64.b64encode(thumbnail).decode('utf-8')
        return self.thumbnail