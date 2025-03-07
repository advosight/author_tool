from book_maker.chapter import Chapter
from book_maker.character import Character
from utils import Storage
import mammoth
from io import StringIO
from llm import getLLM

class Book:
    def __init__(self, title: str):
        self.title = title
        self.storage = Storage(title)
        self._chapters: list[Chapter] = None
        self._characters = None
        self._writing_style = None
        self.llm = getLLM()

    @property
    def writing_style(self):
        if self._writing_style is not None:
            return self._writing_style
        
        self._writing_style = self.storage.loadWritingStyle()
        return self._writing_style

    @writing_style.setter
    def writing_style(self, value):
        self._writing_style = value
        self.storage.saveWritingStyle(value)

    def __str__(self):
        return f"{self.title}"

    @property 
    def characters(self):
        retval = self.storage.getCharacterNames()
        retval.sort()
        return retval

    @property
    def chapters(self):
        if self._chapters is not None:
            return self._chapters
        
        if self.storage.exists():
            chapterNames = self.storage.listChapters()
            self._chapters = []
            for chapterName in chapterNames:
                self._chapters.append(Chapter(self, int(chapterName), self.storage))

        self._chapters.sort(key=lambda x: x.number)
        return self._chapters

    def getChapter(self, title: str):
        if self.chapters is not None:
            for chapter in self.chapters:
                if str(chapter) == title:
                    return chapter

    def addChapter(self, afterChapter: int = None):
        """ Adds a new chapter to the book 
        
        Args:
            afterChapter (int): The chapter to insert after
        """

        if afterChapter is None:
            chapter = Chapter(self, len(self._chapters) + 1, self.storage)
            chapter.content = ""
            self._chapters.append(chapter)
            self._chapters.sort(key=lambda x: x.number)
            return chapter

        # In reverse order increase the number of all chapters after the afterChapter
        for i in range(len(self._chapters) - 1, afterChapter - 1, -1):
            self.storage.moveChapterNumber(self._chapters[i].number, self._chapters[i].number + 1)
            self._chapters[i].number += 1

        chapter = Chapter(self, afterChapter + 1, self.storage)
        chapter.content = ""
        self._chapters.append(chapter)
        self._chapters.sort(key=lambda x: x.number)
        return chapter

    def removeChapter(self, chapter: Chapter):
        """Removes a chapter from the book

        Args:
            chapter (Chapter): The chapter to remove
        """
        self.storage.deleteChapter(chapter.number)
        self._chapters.remove(chapter)
        for i in range(chapter.number - 1, len(self._chapters)):
            self._chapters[i].number -= 1

    def loadFromContent(self, storyFile: any):
        story = mammoth.convert_to_markdown(storyFile).value
        chapterContent = story.split('#')

        # Add # back to the beginning of each chapter
        self.chapters = []
        for i in range(0, len(chapterContent)):
            chapter = Chapter(self, i + 1, self.storage)
            chapter.loadFromContent(chapterContent[i])
            self.chapters.append(chapter)

    def getLatestCharacter(self, name: str) -> Character:
        """Gets the latest character based on the character's name

        Args:
            name (str): The name of the character

        Returns:
            Character: The character object
        """
        chapter = self.chapters[-1]
        return Character(self, chapter, name, self.storage)
