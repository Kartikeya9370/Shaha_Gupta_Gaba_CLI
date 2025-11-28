Contact Book – Terminal & Web Application
=========================================

1. Project Scope & Overview
---------------------------

Original scope:
- Build a **contact book application for the terminal** that can:
  - Store contacts (name, phone, email) in a file
  - List, search, update, and delete contacts interactively

New features include a Flask REST API (contactbook_server.py) and a web interface built with JavaScript and CSS. The web UI supports live search, contact editing, and deletion without page reloads, status messages, and custom styles.

The terminal and web apps both use the same contacts.json file. Any changes made in one interface will appear in the other.

Data & Files
------------

- `contacts.json` – JSON array of contacts: each item has `name`, `phone`, `email.`
- Shared by:
  - Terminal app (`contactbook.py`)
  - Flask server (`contactbook_server.py`)

2. Terminal Application (`contactbook.py`)
-----------------------------------------

The terminal app is the core deliverable. It provides a text menu for managing contacts.

### 2.1 Contact Class

Handles individual contact objects with built-in validation.

- `__init__(self, name, phone, email)`
  - Removes unnecessary whitespace before storing inputs 
  - Validates each field through helper methods during object creation
  - Raises ValueError if something's wrong, so bad data never gets stored

- `is_valid_name(self, name)`
  - Ensures the name field is not empty
  - Uses regex to verify the name contains only letters and spaces
  - Rejects entries with numbers, symbols, or special characters

- `is_valid_phone(self, phone)`
  - Removes formatting characters and counts remaining digits
  - Requires at least 10 digits for a valid phone number
  - Accepts various formats without enforcing country-specific rules

- `is_valid_email(self, email)`
  - Checks for basic email structure (user@domain) using a regex pattern
  - Filters out clearly malformed email addresses

- `to_dict(self)`
  - Returns contact data as a dictionary with name, phone, and email keys
  - Ensures consistent formatting for JSON serialization and API responses

### 2.2 ContactBook Class

This class handles saving contact data and runs the command-line interface.

- `__init__(self, contacts_file=CONTACTS_FILE)`
  - Stores the file path for contacts.json
  - Loads existing contacts into memory during initialization

- `load_contacts(self)`
  - Returns an empty list if the file doesn't exist (first-time execution)
  - Reads and parses contacts.json, returning a list of contact dictionaries
  - Centralizes file-reading logic for reuse across methods

- `save_contacts(self)`
  - Writes the current contact list to contacts.json with formatting
  - Persists all changes in a human-readable JSON format

- `add_contact(self, name, phone, email)`
  - Validates input by instantiating a Contact object
  - Performs case-insensitive duplicate checking by name
  - If validation passes and no duplicate exists:
    - Adds the contact to the in-memory list
    - Saves changes to the file
    - Displays confirmation message

- `display_contacts(self)`
  - If the list is empty, it will display "No contact found."
  - Otherwise,  contacts are alphabetically (case-insensitive)sorted  and displayed 
  - Provides a formatted overview of all stored contacts

- `search_contact(self, query)`
  - Performs case-insensitive search across name, phone, and email fields
  - Displays all matching contacts or a "not found" message
  - Enables flexible keyword-based searching

- `update_contact(self, name)`
  - Locates contact using case-insensitive name matching
  - Prompts for new values, keeping existing data if the user presses Enter
  - Validates new input using Contact class validation rules
  - Saves updated contact to file

- `delete_contact(self, name)`
  - Finds and removes contact using case-insensitive name matching
  - Saves changes to the file after deletion

- `menu(self)`
  - Displays available operations (list, add, search, update, delete, exit)
  - Captures and returns user selection
  - Serves as the main navigation interface

- `run(self)`
  - Main application loop that:
    - Displays menu and captures user choice
    - Routes to the appropriate method based on selection
    - Handles exit by saving data and terminating gracefully
  - Coordinates the overall CLI workflow

- `if __name__ == "__main__":`
  - Entry point for direct script execution
  - Instantiates ContactBook and launches the application

3. Web Backend (`contactbook_server.py`)
---------------------------------------

The web backend was not part of the original requirements. It uses the same data model to offer a REST API for the web interface, but it was added later.

### 3.1 Configuration & Setup

- `BASE_DIR`, `CONTACTS_FILE`
- used to determine the script's main directory and locate `contacts.json` from the same folder 
 - **Why:** This works no matter where the script runs from because it always points to correct working directory  

- `app = Flask(__name__, template_folder=BASE_DIR, static_folder=BASE_DIR)`
  - Creates the Flask application.
  - **Why **Uses the project directory as a template and a static folder so files like `index.html`, `script.js`, and `style.css` can be served.

- `CORS(app)`
  - Enables Cross-Origin Resource Sharing.
  - **Why:** It allows the front end to call the API even if its hosted on a different origin - something very useful during development,especially when the backend and frontend run on separate servers.

### 3.2 Helper functions

- `_log(msg: str)`
  - Prints server-side log messages prefixed with `[server]`.
  - **Why:** Simple debugging/logging helper.

- `_load_contacts() -> List[Dict]`
  - Similar logic to the terminal’s `load_contacts`:
    - Generates an empty file if one is missing.
    - Loads contact data from contacts.json as a list of dictionaries.
  - Returns an empty list if the JSON file cannot be parsed correctly.
  - **Why:** Single point where the server reads the contact data.

- `_save_contacts(contacts: List[Dict]) -> bool`
  - Updates the contacts.json file with the modified contact information.
  - Returns `True` on success, `False`, and logs an error on failure.
  - **Why:** Centralizes file writing and error handling for all routes.

- `_index_by_name(contacts: List[Dict])`
  - Builds a mapping from lower‑cased name → index in list.
  - **Why:** Makes updates and deletions by name efficient and consistent.

- `_valid_email(email: str)`, `_valid_phone(phone: str)`
  - Very similar validation logic to the terminal `Contact` class:
    - Email uses a regex.
    - Phone checks digit count.
  - **Why:** Ensures the web API enforces the same rules as the CLI.

### 3.3 Routes (HTTP endpoints)

- - `home()` → `GET /`
  - Serves the main HTML page (index.html) using Flask's render_template
  - Acts as the entry point for the web interface

- `js()` → `GET /script.js`
  - Delivers the JavaScript file to the browser

- `css()` → `GET /style.css`
  - Delivers the stylesheet to the browser

**API Endpoints:**

- `api_list()` → `GET /api/contacts.`
  - Retrieves all contacts by calling  _load_contacts()
  - Then returns JSON response: `{ "success": true, "data": [...], "count": N }.`
  - the complete contact list sent back to the frontend

- `api_add()` → `POST /api/contacts.`
  - Accepts new contact information in JSON format from the request body
  - It extracts and cleans the  name, phone, and email fields
  - Validates input using _valid_email() and _valid_phone() functions
  - Checks for duplicate contact names
  - Adds valid contacts to the list and persists changes
  - Returns appropriate HTTP status codes: 200 for success, 400 for invalid input, 
    409 for duplicate entries

- `api_update(name)` → `PUT /api/contacts/<name>`
  - Locates existing contact by name (case-insensitive matching)
  - Reads updated fields from the JSON request body
  - The new data is validated before applying changes
  - Saves modifications and returns a success confirmation
  - In case the specific contact is missing, it returns 404 

- `api_delete(name)` → `DELETE /api/contacts/<name>`
  - Removes contact matching the provided name (case-insensitive)
  - Returns 404 if no matching contact is found
  - Saves updated list and confirms successful deletion

**Server Initialization:**

- `if __name__ == "__main__":`
  - Displays startup information, including file paths and data file status
  - Launches Flask development server on 127.0.0.1:5000 with debug mode enabled

## 4. Web Frontend – JavaScript (script.js)

The JavaScript file connects to the Flask API and manages the UI.

### 4.1 Initialization

- `API_BASE` constant defines the base path ('/api') for all API requests

- `DOMContentLoaded` event listener ensures the script executes after the page loads
  - Initializes an in-memory contacts array
  - Tracks which contact is being edited via `editingContactName.`
  - Caches references to DOM elements (forms, lists, buttons, counters, modal fields)

### 4.2 Utility Functions

showMessage(text, type) displays temporary notifications. fmtTime formats dates. updateLastUpdated refreshes the timestamp.

escapeHtml(str) sanitizes user input to prevent HTML injection.

### 4.3 Contact Filtering and Display

- `filterContacts(query)`
  - When the search query is empty, all contacts are returned.
  - Carries out case-insensitive matching against the email, phone, and name fields
  - Enables the live search functionality

- `render(list)`
  - Clears and rebuilds the contact list display
  - When the list is empty, a "No contacts found" notice appears
  - Creates DOM elements for each contact, including:
    - Contact information (name, phone, email)
    - Action buttons (Edit and Delete)
  - Updates the contact counter to reflect search results

### 4.4 API Communication

All API functions use the fetch API and refresh the UI by calling loadContacts() after successful operations.

- `loadContacts()`
  - Sends GET request to /api/contacts
  - Handles multiple response formats for compatibility
  - Updates the local contacts array and triggers re-rendering
  - Updates the timestamp and displays status messages

- `addContact(payload)`
  - Sends a POST request with contact data
  - Validates server response
  - Refreshes the contact list and shows confirmation on success

- `updateContact(name, payload)`
  - Sends a PUT request to update a specific contact
  - Reloads contacts and displays a success message

- `delContact(name)`
  - Prompts for user confirmation before deletion
  - Sends a DELETE request for the specified contact
  - Refreshes the list and confirms deletion

### 4.5 Modal and Event Handling

- `openEdit(contact)`
  - Stores the contact name being edited
  - Populates the edit form with current contact data
  - Displays the modal by adding the 'show' CSS class

- `closeEditModal()`
  - Clears the editing state
  - Hides the modal by removing the 'show' class

- `setupEventListeners()`
  - Attaches event handlers for:
    - Add contact form submission (validates and calls addContact)
    - Search input changes (filters and re-renders contacts)
    - Refresh button (reloads contact data)
    - Edit form submission (validates and calls updateContact)
    - Modal close actions (button click and background click)

**Application Initialization:**
- Registers all event listeners
- Loads initial contact data
- Sets current timestamp
- Establishes a 60-second interval to keep the timestamp current

## 5. Styling (style.css)

The CSS file handles the visual presentation of the web application.

**Key Features:**
- Defines a color scheme using CSS custom properties (CSS variables in:root)
- Implements a dark theme with a card-based layout and centered container
- Styles core UI elements, including headers, cards, buttons, and input fields
- Formats contact list rows with their associated action buttons
- Provides visual feedback through styled status messages (success, error, warning)
- Designs the edit modal with overlay and content container
- Includes responsive adjustments to maintain usability on smaller screens

## 6. System Architecture

The application uses contacts.json as the central data store for all contact information.

- The terminal application (contactbook.py) reads from and writes to this file directly 
  through the ContactBook class
- The Flask server (contactbook_server.py) accesses the same file through its API endpoints
- The web frontend (script.js and style.css) runs in the browser, communicates with the 
  Flask API, and updates the interface accordingly

This design allows for flexible usage:
- Contacts can be managed entirely through the terminal interface
- The Flask server can be started at any time to enable browser-based management
- Both interfaces work with the same data without requiring migration or synchronization

7. How to Run
-------------

### 7.1 Terminal Version

Run the terminal application using:
```bash
python contactbook.py
```

Follow the menu options to manage your contacts (list, add, search, update, delete).

### 7.2 Web Version

1. Install Flask and its dependencies:
```bash
pip install flask flask-cors
```

2. Start the web server:
```bash
python contactbook_server.py
```

3. Access the interface by opening your browser to:
```text
http://localhost:5000
```

The web interface lets you manage contacts visually, with all changes synced to the 
same contacts.json file used by the terminal version.
