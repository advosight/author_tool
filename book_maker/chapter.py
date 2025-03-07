import streamlit as st
import json
import pygame
from io import BytesIO
from utils import Storage, getLogger
from .character import Character
from llm import getLLM

logger = getLogger('Chapter')

class ChapterEval:
    def __init__(self, data: dict):
        self.score = int(data.get('score', 0))
        self.comments = data.get('comments', [])

class Chapter:
    def __init__(self, book: any, number: int, storage: Storage):
        # Get first line as chapter name
        self.name = None
        self.llm = getLLM()
        self.storage = storage
        self.book = book
        self._number = number
        self._characters = None
        self._content = None
        self._edit_mode = 'full'
        self._edit_text = ''
        self._technical_eval = None
        self._entertainment_eval = None

        if storage.chapterExists(number):
            self.name = storage.loadChapterName(number)
            self.summary = storage.loadChapterSummary(number)
            
            characters = storage.loadChapterCharacters(number)
            
            if characters is not None:
                self._characters = []
                for character in characters:
                    self._characters.append(Character(book, self, character, storage))

            self._content = storage.loadChapterContent(number)

    def loadFromContent(self, content):
        self.name = content.split("\n")[0].strip()
        # Check for : and remove chapter information to the left
        if ":" in self.name:
            self.name = self.name.split(":")[1].strip()

        number = self.number
        if self.name == f"Chapter {number}":
            self.name = f""

        if self.name == "Chapter":
            self.name = ""

        self.title = f"Chapter {number}"
        if self.name != "":
            self.title += f": {self.name}"

        self.number = number
        
        # Remove first line from content
        self.content = content[(len(self.name) + 1):]

        self.summary = None

        self.storage.saveChapterContent(self.number, self.content)

    def __str__(self):
        if self.name is None:
            return f"Chapter {self.number}"
        if self.name == "":
            return f"Chapter {self.number}"
        return f"Chapter {self.number}: {self.name}"

    def __repr__(self):
        return f"# {self}\n{self.content}\n"

    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, number: int):
        if number == self._number:
            logger.info(f"Chapter number is already {number}")
            return
        
        logger.info(f"Changing chapter from {self._number} to {number}")
        self.storage.moveChapterNumber(self._number, number)
        self._number = number

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content: str):
        self._content = content
        self.storage.saveChapterContent(self.number, content)

    @property
    def characters(self):
        if self._characters is not None:
            return self._characters

        if self.content is None or self.content.strip() == '':
            return []

        prev_characters = self.book.characters
        prev_characters_str = ", ".join(prev_characters)
        characterResult = self.llm.prompt(f"List the main characters in the following chapter. Only include the characters in the response in a json string array without annotation. The current known characters are: {prev_characters_str}. If an existing character's first or last name is found, use the existing name from the list. Look in the chapter: " + self.content)

        if characterResult is None:
            return "No characters found"

        characters = json.loads(characterResult)
        self._characters = []
        names = []
        for character in characters:
            name = str(character)
            names.append(name)
            self._characters.append(Character(self.book, self, name, self.storage))

        self.storage.saveChapterCharacters(self.number, names)
        return self._characters

    @property
    def summary(self):
        if self._summary is not None:
            return self._summary

        if self.content is None or self.content.strip() == '':
            return "No summary available"

        tokens = self.content.split(" ");

        if len(tokens) > self.llm.max_tokens:
            summaries = []
            max_tokens = self.llm.max_tokens - 200
            top_range = int(len(tokens) / max_tokens)
            for i in range(0, top_range + 1):
                start = (i * max_tokens) - 50
                if start < 0:
                    start = 0
                storyPart = " ".join(tokens[start:i* max_tokens])
                summary = self.llm.prompt("The following is a segment of a chapter. Summarize, in 200 words, the following to be used later to create a full summary and only return the summary: " + storyPart)

                if summary is not None:
                    # Remove "<think></think>" from the summary
                    indexOfEndThink = summary.find("</think>")
                    if indexOfEndThink != -1:
                        summary = summary[indexOfEndThink + 8:]

                    # Add summary to summaries
                    summaries.append(summary)
            
            summariesStr = " ".join(summaries)
            self._summary = self.llm.prompt("Summarize the following: " + " ".join(summariesStr))
        else:
            summary = self.llm.prompt("Summarize the following chapter. Only include the summary in the response: " + self.content)
            indexOfEndThink = summary.find("</think>")
            if indexOfEndThink != -1:
                summary = summary[indexOfEndThink + 8:]

            self._summary = summary

        if self._summary is None:
            return "No summary available"

        self.storage.saveChapterSummary(self.number, self._summary)
        return self._summary
    
    @summary.setter
    def summary(self, value):
        self._summary = value

    @property
    def edit_mode(self):
        return self._edit_mode
    
    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value

    @property
    def edit_text(self):
        return self._edit_text

    @edit_text.setter
    def edit_text(self, value):
        if value == '':
            self.edit_text = self.content
        else:
            self._edit_text = value

    def clearAudio(self, paragraph: int):
        self.storage.saveParagraphAudio(self.number, paragraph, None)

    def playParagraphs(self, paragraphs: [int]):
        st.session_state['play'] = True
        for i in paragraphs:
            self.playParagraph(i)
            
            # Check to see if the user wants to stop
            if not st.session_state['play']:
                break

    def getParagraphAudio(self, paragraphs: [str], paragraph: int):
        if self.content is None or self.content.strip() == '':
            return None

        # Get audio from storage
        existing_audio = self.storage.getParagraphAudio(self.number, paragraph)
        if existing_audio is not None:
            return existing_audio
            
        # Construct audio from paragraphs
        paragraph_content = paragraphs[paragraph]
        new_audio = self.llm.getSpeech(paragraph_content)

        self.storage.saveParagraphAudio(self.number, paragraph, new_audio)
        return new_audio

    def getAudio(self, paragraphs: [int]) -> bytes:
        if self.content is None or self.content.strip() == '':
            return None

        paragraph_content = self.content.split("\n\n")
        audio = b''
        for paragraph in paragraphs:
            par_audio = self.getParagraphAudio(paragraph_content, paragraph)
            if par_audio is not None:
                audio += par_audio

        return audio

    def playParagraph(self, paragraph: int):
        audio = self.getAudio(paragraph)
        if audio is None:
            return

        try:
            pygame.mixer.init()
            mp3_file = BytesIO(audio)
            pygame.mixer.music.load(mp3_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            pygame.mixer.quit()

    def getCharacter(self, name: str) -> Character:
        """Gets a character based on the character's name

        Args:
            name (str): The name of the character

        Returns:
            Character: The character object
        """

        if self._characters is None:
            return None
        for character in self.characters:
            if character.name == name:
                return character

        return None

    def addCharacter(self, name: str):
        """Adds a character to the chapter

        Args:
            name (str): The name of the character
        """
        if self._characters is None:
            self._characters = []

        character = Character(self.book, self, name, self.storage)
        self._characters.append(character)
        names = []
        for character in self._characters:
            names.append(character.name)

        self.storage.saveChapterCharacters(self.number, names)
        return character

    def evalTechnical(self):
        """Evaluates the technical details of the chapter
        """
        if self.content is None or self.content.strip() == '':
            return "No technical evaluation available"

        conversation = []
        for character in self.characters:
            conversation.append({ "role": "user", "content": f"The character {character.name} has expertise in the following:\n{character.expertise}"})
            conversation.append({ "role": "ai", "content": "I will take this into account"})

        conversation.append({"role": "user", "content": f"The following is the current chapter: {self.content}"})
        conversation.append({"role": "ai", "content": "I will take this into account"})

        conversation.append({ "role": "user", "content": f"""
        You are an expert in the fields that the characters are experts in. 
        Evaluate the technical details of the following chapter and identify all incongruence and misstatements when it comes to the technical expertise of the characters in the chapter. Take into account
        Who is communicating and who they are communicating to, to ensure things like simplification of concepts are taken into account.
        If a character states something that mitigates the concern, do not include the feedback.
        In the response, if something is generally aligned, then don't include it in the feedback. Only include the specific bullet pointed issues with the chapter while considering of the situation the characters find themselves in
        the current chapter. Return only negative feedback, and exclude positive feedback. The format of the result is JSON with the following structure: {{ "score": int, "comments": [str] }}
        """})

        try:
            evalStr = self.llm.techEval(conversation)
            if evalStr is None:
                self._technical_eval = None
                return None
            
            evalStr = evalStr[8:-3]
            logger.info(evalStr)
            self.storage.saveChapterTechnicalEval(self.number, evalStr)
            self._technical_eval = ChapterEval(json.loads(evalStr))
        except:
            return None
        
        return self._technical_eval

    @property
    def technical_eval(self):
        """The technical evaluation of the chapter"""

        if self._technical_eval is not None:
            return self._technical_eval

        # Load technical eval from storage
        evalStr = self.storage.loadChapterTechnicalEval(self.number)
        if evalStr is not None:
            self._technical_eval = ChapterEval(json.loads(evalStr))
            if self._technical_eval is not None:
                return self._technical_eval

        return self._technical_eval

    @technical_eval.setter
    def technical_eval(self, value):
        self._technical_eval = value
        self.storage.saveChapterTechnicalEval(self.number, json.dumps(value.__dict__))

    def evalEntertainment(self) -> ChapterEval:
        """Uses the LLM to evaluate the entertainment value of the current chapter"""
        if self.content is None or self.content.strip() == '':
            return None

        conversation = []
        
        # Append all previous chapters to the conversation
        for i in range(0, self.number):
            chapter = self.book.chapters[i]
            conversation.append({ "role": "user", "content": f"The following is a summary of the chapter {i}:\n{chapter.summary}"})
            conversation.append({ "role": "ai", "content": "I will take this into account" })

        conversation.append({ "role": "user", "content": f"The current chapter: {self.content}"})
        conversation.append({ "role": "ai", "content": "I will take this into account" })

        conversation.append({ "role": "user", "content": f"""
        Evaluate the current chapter for entertainment value and estimate a score from 0 - 100. Return only negative feedback, and exclude positive feedback. 
        The format of the result is JSON with the following structure: {{ "score": int, "comments": [str] }}
        """})

        try:
            evalStr = self.llm.entEval(conversation)
            if evalStr is None:
                self._entertainment_eval = None
                return None
            
            evalStr = evalStr[8:-3]
            logger.info(json.dumps(evalStr))
            self.storage.saveChapterEntertainmentEval(self.number, evalStr)

            logger.info("Loading eval")
            logger.info(evalStr)
            self._entertainment_eval = ChapterEval(json.loads(evalStr))
        except Exception as e:
            logger.error(f"Entertainment Eval Failed {e}")
            return None
        return self._entertainment_eval
    
    @property
    def entertainment_eval(self) -> ChapterEval:
        """The entertainment evaluation of the chapter"""

        if self._entertainment_eval is not None:
            return self._entertainment_eval

        # Load technical eval from storage
        evalStr = self.storage.loadChapterEntertainmentEval(self.number)
        if evalStr is not None:
            self._entertainment_eval = ChapterEval(json.loads(evalStr))
            if self._entertainment_eval is not None:
                return self._entertainment_eval

        return self._entertainment_eval
    
    @entertainment_eval.setter
    def entertainment_eval(self, value: ChapterEval):
        self._entertainment_eval = value
        evalStr = json.dumps(value.__dict__)
        self.storage.saveChapterEntertainmentEval(self.number, evalStr)
