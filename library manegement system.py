
import json
from datetime import datetime

class StudentNode:
    """
    Represents a single student's record in the system.
    Acts as a node in a singly linked list.
    """

    def __init__(self, student_id, name, grade, major):
        self.student_id = int(student_id)
        self.name = name.strip().title()
        self.grade = grade.upper() if isinstance(grade, str) else str(grade)
        self.major = major.strip().title()
        self.added_date = datetime.now().strftime('%Y-%m-%d')
        self.next = None

    def __str__(self):
        return (f"ID: {self.student_id} | Name: {self.name:20} | "
                f"Grade: {self.grade:2} | Major: {self.major:15} | Added: {self.added_date}")

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "grade": self.grade,
            "major": self.major,
            "added_date": self.added_date
        }

class StudentRecordSystem:
    """
    Core system class. Manages student records using a singly linked list.
    """

    def __init__(self):
        self.head = None
        self.record_count = 0
        self.load_records()

    def load_records(self):
        """Load existing student records from file."""
        try:
            with open("student_records.dat", "r") as file:
                data = json.load(file)
                for entry in reversed(data.get("records", [])):
                    self._add_node(entry["student_id"], entry["name"], entry["grade"], entry["major"], entry["added_date"])
            print(f"✅ Loaded {self.record_count} record(s) from file.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("📂 No previous records found. Starting fresh.")

    def _add_node(self, student_id, name, grade, major, added_date=None):
        """Internal helper to insert new student node at the front."""
        new_student = StudentNode(student_id, name, grade, major)
        if added_date:
            new_student.added_date = added_date
        new_student.next = self.head
        self.head = new_student
        self.record_count += 1

    def save_records(self):
        """Persist current student records to file."""
        data = []
        current = self.head
        while current:
            data.append(current.to_dict())
            current = current.next
        with open("student_records.dat", "w") as file:
            json.dump({"records": data}, file, indent=2)
        print(f"💾 Saved {len(data)} record(s) to file.")

    def add_student(self):
        """Prompt user and add a new student record."""
        print("\n🆕 Add Student Record")
        while True:
            sid = input("Enter Student ID (numeric): ").strip()
            if not sid.isdigit():
                print("❌ ID must be a number.")
                continue
            if self.find_by_id(sid):
                print(f"❌ Student ID {sid} already exists.")
                continue
            break

        name = input("Enter Full Name: ").strip()
        while not name:
            name = input("❌ Name cannot be empty. Try again: ")

        grade = input("Enter Grade (A-F or numeric): ").strip().upper()
        major = input("Enter Major: ").strip() or "Undeclared"

        self._add_node(int(sid), name, grade, major)
        print(f"✅ Student '{name}' added successfully.")
        self.save_records()

    def find_by_id(self, student_id):
        """Find a student by ID."""
        current = self.head
        while current:
            if str(current.student_id) == str(student_id):
                return current
            current = current.next
        return None

    def search_students(self, term):
        """Search by name or ID fragment."""
        matches = []
        current = self.head
        term = term.lower()
        while current:
            if term in str(current.student_id).lower() or term in current.name.lower():
                matches.append(current)
            current = current.next
        return matches

    def update_student(self):
        """Update a student's existing record."""
        sid = input("Enter Student ID to update: ").strip()
        student = self.find_by_id(sid)
        if not student:
            print("❌ Student not found.")
            return

        print(f"Current Record:\n{student}")
        name = input(f"New Name (or press Enter to keep '{student.name}'): ").strip()
        grade = input(f"New Grade (or press Enter to keep '{student.grade}'): ").strip().upper()
        major = input(f"New Major (or press Enter to keep '{student.major}'): ").strip()

        if name: student.name = name.title()
        if grade: student.grade = grade
        if major: student.major = major.title()

        print("✅ Record updated.")
        self.save_records()

    def delete_student(self):
        """Delete a student's record."""
        sid = input("Enter Student ID to delete: ").strip()
        prev, current = None, self.head

        while current:
            if str(current.student_id) == sid:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                self.record_count -= 1
                print(f"🗑️ Deleted record for {current.name} (ID: {current.student_id})")
                self.save_records()
                return
            prev = current
            current = current.next

        print("❌ Student not found.")

    def display_all(self, sort_by="id"):
        """Display all records, sorted by ID or name."""
        if not self.head:
            print("📭 No records to display.")
            return

        self.sort_by(sort_by)
        print(f"\n📋 Student Records (sorted by {sort_by.title()}):\n" + "-"*80)
        current = self.head
        while current:
            print(current)
            current = current.next
        print(f"\n📊 Total Records: {self.record_count}")

    def sort_by(self, key="id"):
        """Sort list in-place (bubble or insertion logic)."""
        if key == "name":
            # Bubble sort by name
            changed = True
            while changed:
                changed, prev, curr = False, None, self.head
                while curr and curr.next:
                    if curr.name > curr.next.name:
                        changed = True
                        temp = curr.next
                        curr.next = temp.next
                        temp.next = curr
                        if prev:
                            prev.next = temp
                        else:
                            self.head = temp
                        prev = temp
                    else:
                        prev = curr
                        curr = curr.next
        else:
            # Insertion sort by ID
            sorted_head = None
            current = self.head
            while current:
                next_node = current.next
                if not sorted_head or current.student_id < sorted_head.student_id:
                    current.next = sorted_head
                    sorted_head = current
                else:
                    pos = sorted_head
                    while pos.next and pos.next.student_id < current.student_id:
                        pos = pos.next
                    current.next = pos.next
                    pos.next = current
                current = next_node
            self.head = sorted_head

    def export_to_txt(self, filename="student_records.txt"):
        """Write all records to a human-readable text file."""
        if not self.head:
            print("📭 No records to export.")
            return
        with open(filename, "w") as f:
            f.write("Student Record Export\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now()}\n\n")
            current = self.head
            while current:
                f.write(str(current) + "\n")
                current = current.next
        print(f"📤 Exported records to '{filename}'.")

def start_cli():
    system = StudentRecordSystem()

    menu = """
==== Student Record CLI ====
Commands:
  add      - Add new student
  update   - Update student record
  delete   - Delete student record
  search   - Search by ID or name
  display  - Show all records
  export   - Export records to text file
  help     - Show this menu
  exit     - Exit the program
============================"""

    print(menu)
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            if cmd == "add":
                system.add_student()
            elif cmd == "update":
                system.update_student()
            elif cmd == "delete":
                system.delete_student()
            elif cmd == "search":
                query = input("🔍 Enter ID or name: ").strip()
                results = system.search_students(query)
                if results:
                    print("\n🔎 Search Results:")
                    for r in results:
                        print(r)
                else:
                    print("No matching student found.")
            elif cmd.startswith("display"):
                sort_key = cmd.split()[1] if len(cmd.split()) > 1 else "id"
                system.display_all(sort_key)
            elif cmd == "export":
                system.export_to_txt()
            elif cmd == "help":
                print(menu)
            elif cmd == "exit":
                system.save_records()
                print("👋 Exiting. Data saved.")
                break
            else:
                print("❓ Unknown command. Type 'help' to see options.")
        except KeyboardInterrupt:
            print("\n👋 Use 'exit' to quit cleanly.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_cli()
