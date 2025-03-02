from utils import Storage
from .book import Book

class BookLibrary:
    def __init__(self):
        self.storage = Storage(None)
        self.books = None
        self.bookNames = None

    def addBook(self, book):
        self.books.append(book)

    def listBooks(self):
        if self.books is not None:
            return self.books

        self.books = []
        self.bookNames = ['']
        titles = self.storage.listBooks()
        for title in titles:
            self.addBook(Book(title))
            self.bookNames.append(title)
        
        return self.bookNames

    def getBook(self, title):
        # Find the book in the list of books
        for book in self.books:
            if book.title == title:
                return book

    def loadFromContent(self, storyFileName: str,  storyFile: any):
        book = Book(storyFileName)
        book.loadFromContent(storyFile)
        self.addBook(book)
        return book

