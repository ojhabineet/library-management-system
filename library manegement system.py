
import json
import os
from collections import deque
from datetime import datetime, timedelta

class Book:
    """Represents a physical book in our inventory"""
    def __init__(self, title, author, isbn):
        self.title = title.strip().title()
        self.author = author.strip().title()
        self.isbn = isbn.strip()
        self.is_available = True
        self.waitlist = deque()
        self.due_date = None
        self.checkout_history = []
        
    def __str__(self):
        status = "Available" if self.is_available else f"Checked Out (Due: {self.due_date})"
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}) - {status}"

    def to_dict(self):
        """Prepare book data for JSON storage"""
        return {
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'is_available': self.is_available,
            'waitlist': list(self.waitlist),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'checkout_history': self.checkout_history
        }

class Library:
    """Core system class handling all library operations"""
    
    def __init__(self):
        self.books = {}  # ISBN -> Book mapping (our hash map)
        self.log_file = "library_activity.log"
        self.data_file = "library_inventory.json"
        self.load_data()
        self.current_date = datetime.now().date()
        
    # ========== Data Persistence Methods ==========
    def load_data(self):
        """Load existing library data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for isbn, book_data in data.items():
                        book = Book(book_data['title'], 
                                  book_data['author'], 
                                  isbn)
                        book.is_available = book_data['is_available']
                        book.waitlist = deque(book_data.get('waitlist', []))
                        book.due_date = datetime.strptime(book_data['due_date'], '%Y-%m-%d').date() if book_data['due_date'] else None
                        book.checkout_history = book_data.get('checkout_history', [])
                        self.books[isbn] = book
            self.log("System initialized - data loaded")
        except Exception as e:
            self.log(f"Error loading data: {str(e)}", error=True)

    def save_data(self):
        """Save current state to file"""
        try:
            data = {isbn: book.to_dict() for isbn, book in self.books.items()}
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.log(f"Error saving data: {str(e)}", error=True)
            return False

    def log(self, message, error=False):
        """Record system activity and errors"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_type = "ERROR" if error else "INFO"
        entry = f"[{timestamp}] {log_type}: {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(entry)
        
        if error:
            print(f"! System Error: {message}")

    # ========== Core Library Operations ==========
    def add_book(self, title, author, isbn):
        """Add a new book to the collection"""
        if not isbn or not title:
            print("Error: ISBN and title are required")
            return False
            
        if isbn in self.books:
            print(f"Error: Book with ISBN {isbn} already exists")
            return False
            
        new_book = Book(title, author, isbn)
        self.books[isbn] = new_book
        self.log(f"Added new book: {title} by {author} (ISBN: {isbn})")
        self.save_data()
        print(f"Successfully added '{title}' to the collection")
        return True

    def checkout_book(self, isbn, member_id, days=14):
        """Check out a book to a patron"""
        if isbn not in self.books:
            print("Error: Book not found in our system")
            return False
            
        book = self.books[isbn]
        
        if not book.is_available:
            if member_id not in book.waitlist:
                book.waitlist.append(member_id)
                self.save_data()
                print(f"Book is currently checked out. You're #{len(book.waitlist)} in line.")
                self.log(f"Added {member_id} to waitlist for {book.title}")
            else:
                print("You're already on the waitlist for this book")
            return False
            
        book.is_available = False
        book.due_date = self.current_date + timedelta(days=days)
        book.checkout_history.append({
            'member': member_id,
            'checkout_date': self.current_date.isoformat(),
            'due_date': book.due_date.isoformat()
        })
        self.save_data()
        self.log(f"{member_id} checked out {book.title} (Due: {book.due_date})")
        print(f"Successfully checked out '{book.title}'. Due: {book.due_date}")
        return True

    def return_book(self, isbn):
        """Process a book return"""
        if isbn not in self.books:
            print("Error: Invalid ISBN - not in our records")
            return False
            
        book = self.books[isbn]
        
        if book.is_available:
            print("Error: This book wasn't checked out")
            return False
            
        # Check for late returns
        is_late = self.current_date > book.due_date if book.due_date else False
        late_days = (self.current_date - book.due_date).days if is_late else 0
        
        book.is_available = True
        book.due_date = None
        
        # Notify next in line if waitlisted
        if book.waitlist:
            next_member = book.waitlist.popleft()
            self.log(f"Notifying {next_member} that {book.title} is available")
            print(f"Notified member {next_member} that book is now available")
        
        self.save_data()
        self.log(f"Book returned: {book.title}" + 
                (f" (Late by {late_days} days)" if is_late else ""))
        
        if is_late:
            print(f"Book returned {late_days} days late. Fine may apply.")
        else:
            print("Thank you for returning the book on time!")
        
        return True

    def search_books(self, search_term):
        """Search books by title, author, or ISBN"""
        results = []
        search_term = search_term.lower().strip()
        
        for book in self.books.values():
            if (search_term in book.title.lower() or 
                search_term in book.author.lower() or 
                search_term in book.isbn.lower()):
                results.append(book)
        
        if not results:
            print("\nNo matching books found")
            return False
        
        print(f"\nFound {len(results)} matching book(s):")
        for book in results:
            print(f"- {book}")
        
        return True

def print_menu():
    """Display the main menu"""
    print("\nLIBRARY MANAGEMENT SYSTEM")
    print("1. Add new book")
    print("2. Check out book")
    print("3. Return book")
    print("4. Search books")
    print("5. View all books")
    print("6. Exit")

def get_input(prompt, required=True):
    """Helper for getting user input"""
    while True:
        user_input = input(prompt).strip()
        if not user_input and required:
            print("This field is required")
            continue
        return user_input

def main():
    """Main program loop"""
    print("\nWelcome to the Library Management System!")
    library = Library()
    
    while True:
        print_menu()
        choice = get_input("Enter your choice (1-6): ")
        
        try:
            if choice == '1':
                print("\nADD NEW BOOK")
                title = get_input("Title: ")
                author = get_input("Author: ")
                isbn = get_input("ISBN: ")
                library.add_book(title, author, isbn)
            
            elif choice == '2':
                print("\nCHECK OUT BOOK")
                isbn = get_input("Enter book ISBN: ")
                member_id = get_input("Enter your member ID: ")
                library.checkout_book(isbn, member_id)
            
            elif choice == '3':
                print("\nRETURN BOOK")
                isbn = get_input("Enter book ISBN: ")
                library.return_book(isbn)
            
            elif choice == '4':
                print("\nSEARCH BOOKS")
                search_term = get_input("Enter title, author or ISBN: ")
                library.search_books(search_term)
            
            elif choice == '5':
                print("\nALL BOOKS IN COLLECTION:")
                for book in library.books.values():
                    print(f"- {book}")
            
            elif choice == '6':
                print("\nThank you for using the Library System!")
                break
            
            else:
                print("Invalid choice. Please enter 1-6")
        
        except Exception as e:
            library.log(f"Unexpected error: {str(e)}", error=True)
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()
