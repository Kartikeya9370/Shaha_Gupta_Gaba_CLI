

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.json")

class Contact:
   

    def __init__(self, name, phone, email):
     
        self.name = name.strip()
        self.phone = phone.strip()
        self.email = email.strip()

        # Validate fields
        if not self.is_valid_name(self.name):
            raise ValueError("Invalid name: Name cannot be empty and must only contain letters and spaces.")

        if not self.is_valid_phone(self.phone):
            raise ValueError("Invalid phone number: Phone number must contain at least 10 digits.")

        if not self.is_valid_email(self.email):
            raise ValueError("Invalid email address format.")

    @staticmethod
    def is_valid_name(name):
        return bool(name) and all(char.isalpha() or char.isspace() for char in name)

    @staticmethod
    def is_valid_phone(phone):
        digits = ''.join([char for char in phone if char.isdigit()])
        return len(digits) >= 10

    @staticmethod
    def is_valid_email(email):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(email_regex, email) is not None

    def to_dict(self):
        return {"name": self.name, "phone": self.phone, "email": self.email}


class ContactBook:

    def __init__(self, contacts_file=CONTACTS_FILE):
        self.contacts_file = contacts_file
        self.contacts = self.load_contacts()

    def load_contacts(self):
        if not os.path.exists(self.contacts_file):
            return []
        with open(self.contacts_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "contacts" in data and isinstance(data["contacts"], list):
                    return data["contacts"]
                else:
                    return []
            except json.JSONDecodeError:
                return []

    def save_contacts(self):
        with open(self.contacts_file, "w", encoding="utf-8") as file:
            json.dump(self.contacts, file, indent=4, ensure_ascii=False)

    def add_contact(self, name, phone, email):
        try:
            new_contact = Contact(name, phone, email).to_dict()
        except ValueError as e:
            print(f"Error adding contact: {e}")
            return False

        if any(contact["name"].lower() == new_contact["name"].lower() for contact in self.contacts):
            print("Error: A contact with that name already exists.")
            return False

        self.contacts.append(new_contact)
        self.save_contacts()
        print(f"Contact '{name}' added successfully!")
        return True

    def display_contacts(self):
        if not self.contacts:
            print("\nNo contacts found.")
            return

        sorted_contacts = sorted(self.contacts, key=lambda c: c["name"].lower())

        print("\n" + "-" * 80)
        print(f"{'Name':<25} | {'Phone':<15} | {'Email':<20}")
        print("-" * 80)
        for contact in sorted_contacts:
            print(f"{contact['name']:<25} | {contact['phone']:<15} | {contact['email']:<20}")
        print("=" * 80)
        print(f"Total: {len(self.contacts)} contacts")

    def search_contact(self, query):
        q = query.lower()
        results = [
            c for c in self.contacts
            if q in c["name"].lower() or q in c["phone"].lower() or q in c["email"].lower()
        ]

        if not results:
            print(f"\nNo contacts found with name containing '{query}'.")
            return []

        print(f"\nFound {len(results)} results")
        print("-" * 80)
        print(f"{'Name':<25} | {'Phone':<15} | {'Email':<20}")
        print("-" * 80)
        for c in results:
            print(f"{c['name']:<25} | {c['phone']:<15} | {c['email']:<20}")
        print("-" * 80)
        return results

    def update_contact(self, name):
        contact = next((c for c in self.contacts if c["name"].lower() == name.lower()), None)

        if not contact:
            print(f"Error: Contact '{name}' not found.")
            return False

        print(f"Name: {contact['name']}")
        print(f"Phone: {contact['phone']}")
        print(f"Email: {contact['email']}")
        print("\nLeave a field empty to keep the current value.")
        new_name = input(f"New name [{contact['name']}]: ").strip() or contact["name"]
        new_phone = input(f"New phone [{contact['phone']}]: ").strip() or contact["phone"]
        new_email = input(f"New email [{contact['email']}]: ").strip() or contact["email"]

        try:
            Contact(new_name, new_phone, new_email)
        except ValueError as e:
            print(f"Error updating contact: {e}")
            return False

        if new_name.lower() != contact["name"].lower() and any(
            c["name"].lower() == new_name.lower() for c in self.contacts
        ):
            print("Error: Another contact with that name already exists.")
            return False

        contact["name"] = new_name
        contact["phone"] = new_phone
        contact["email"] = new_email
        self.save_contacts()
        print(f"Contact '{name}' updated successfully!")
        return True

    def delete_contact(self, name):
        for i, contact in enumerate(self.contacts):
            confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                del self.contacts[i]
                self.save_contacts()
                print(f"Contact '{name}' deleted successfully!")
                return True
            else:
                print("Deletion cancelled.")
                return False

        print(f"Error: Contact '{name}' not found.")
        return False

    def menu(self):
        print("\n" + "=" * 80)
        print("Contact Book - Terminal CLI")
        print("=" * 80)
        print("1. View All Contacts")
        print("2. Add Contact")
        print("3. Search Contact by Name")
        print("4. Edit Contact")
        print("5. Delete Contact")
        print("0. Save and Exit")
        return input("\nSelect an option: ").strip()

    def run(self):
        while True:
            choice = self.menu()

            if choice == "1":
                self.display_contacts()
            elif choice == "2":
                print("\nAdd New Contact")
                name = input("Name: ").strip()
                phone = input("Phone: ").strip()
                email = input("Email: ").strip()
                self.add_contact(name, phone, email)
            elif choice == "3":
                query = input("\nSearch for: ").strip()
                self.search_contact(query)
            elif choice == "4":
                name = input("\nEnter name of contact to update: ").strip()
                self.update_contact(name)
            elif choice == "5":
                name = input("\nEnter name of contact to delete: ").strip()
                self.delete_contact(name)
            elif choice == "0":
                print("\nSaving contacts to file...")
                self.save_contacts()
                print("\nData saved. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 0 and 5.")


if __name__ == "__main__":
    app = ContactBook()
    app.run()
