 The Library Management System is a simple command-line application written in Python that allows users to manage a library's collection of books. It supports functionalities such as adding new books, borrowing and returning books, and displaying available books. The system uses hash maps (dictionaries) for storing book information, queues for managing borrowed books, and file I/O for data persistence.

Features
Add New Books: Users can add books to the library with a title and author.
Borrow Books: Users can borrow available books. If a book is already checked out, they are added to a waitlist.
Return Books: Users can return borrowed books, and the next person on the waitlist is notified.
Display Books: Users can view all books in the library or filter to see only available books.
Data Persistence: The library's state is saved to a JSON file, allowing data to persist between sessions.
