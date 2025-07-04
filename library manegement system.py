#!/usr/bin/env python3
# Library System v1.2 - Last updated 2023-11-15

import json
from collections import namedtuple, deque

# Simple logging setup
def log_action(message):
    with open('library.log', 'a') as logfile:
        logfile.write(f"{message}\n")

class Book:
    def __init__(self, title, author):
        self.title = title.strip().title()
        self.author = author.strip().title()
        self.checked_out = False
        
    def __str__(self):
        return f"'{self.title}' by {self.author}"
    
    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'checked_out': self.checked_out
        }

class LibrarySys:
    def __init__(self):
        self.catalogue = {}  # title -> Book object
        self.waitlist = deque()
        self._setup()
        
    def _setup(self):
        """Initialize or load existing data"""
        try:
            with open('library.dat', 'r') as datafile:
                saved_data = json.load(datafile)
                for book_data in saved_data['books']:
                    book = Book(book_data['title'], book_data['author'])
                    book.checked_out = book_data['checked_out']
                    self.catalogue[book.title] = book
                    
                self.waitlist = deque(saved_data.get('waitlist', []))
            
            log_action("System started - loaded existing data")
        except (FileNotFoundError, json.JSONDecodeError):
            # Start fresh if no data exists
            log_action("System started - new database created")
            
    def _save(self):
        """Persist current state"""
        data = {
            'books': [book.to_dict() for book in self.catalogue.values()],
            'waitlist': list(self.waitlist)
        }
        
        with open('library.dat', 'w') as datafile:
            json.dump(data, datafile, indent=2)
        
        log_action("Data saved to disk")

    def add_new_book(self, title, author):
        """Add a book to the collection"""
        if not title or not author:
            print("Error: Must provide both title and author")
            return False
            
        existing = self.catalogue.get(title.title())
        if existing:
            print(f"Already have {existing} in collection")
            return False
            
        new_book = Book(title, author)
        self.catalogue[new_book.title] = new_book
        print(f"Added new book: {new_book}")
        
        self._save()
        log_action(f"Added book: {new_book}")
        return True

    def check_out_book(self, title):
        """Borrow a book if available"""
        book = self.catalogue.get(title.title())
        
        if not book:
            print(f"Sorry, we don't have '{title}'")
            return False
            
        if book.checked_out:
            print(f"{book} is currently checked out")
            self.waitlist.append(title.title())
            print("You've been added to the waitlist")
            return False
            
        book.checked_out = True
        print(f"You've checked out {book}")
        
        self._save()
        log_action(f"Checked out: {book}")
        return True

    def return_book(self, title):
        """Return a borrowed book"""
        book = self.catalogue.get(title.title())
        
        if not book:
            print(f"We don't have records for '{title}'")
            return False
            
        if not book.checked_out:
            print(f"{book} wasn't checked out!")
            return False
            
        book.checked_out = False
        print(f"Thanks for returning {book}")
        
        # Check waitlist
        if self.waitlist:
            next_person = self.waitlist.popleft()
            print(f"Notifying {next_person} that {book} is available")
        
        self._save()
        log_action(f"Returned: {book}")
        return True

    def list_books(self, available_only=False):
        """Show all books or filter by availability"""
        if not self.catalogue:
            print("The library is empty!")
            return
            
        print("\nLIBRARY CATALOG:")
        print("----------------")
        count = 0
        for book in sorted(self.catalogue.values(), key=lambda x: x.title):
            if not available_only or not book.checked_out:
                status = "AVAILABLE" if not book.checked_out else "CHECKED OUT"
                print(f"{book.title:30} | {book.author:20} | {status}")
                count += 1
        
        if available_only and count == 0:
            print("All books are currently checked out!")

def run_cli():
    lib = LibrarySys()
    
    HELP = """Available commands:
    add <title>,<author>  - Add new book
    borrow <title>        - Check out a book
    return <title>        - Return a book
    list                  - List all books
    available             - List available books
    help                  - Show this help
    exit                  - Quit the program
    """
    
    print("\nWelcome to the Library System!")
    print(HELP)
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'exit':
                print("Goodbye!")
                break
                
            elif cmd == 'help':
                print(HELP)
                
            elif cmd == 'list':
                lib.list_books()
                
            elif cmd == 'available':
                lib.list_books(available_only=True)
                
            elif cmd.startswith('add '):
                parts = cmd[4:].split(',', 1)
                if len(parts) == 2:
                    lib.add_new_book(parts[0], parts[1])
                else:
                    print("Usage: add <title>,<author>")
                    
            elif cmd.startswith('borrow '):
                lib.check_out_book(cmd[7:])
                
            elif cmd.startswith('return '):
                lib.return_book(cmd[7:])
                
            else:
                print("Invalid command. Type 'help' for options")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit properly")
        except Exception as e:
            print(f"Error: {e}")
            log_action(f"Error encountered: {e}")

if __name__ == '__main__':
    run_cli()
