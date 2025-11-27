"""
Contact Book Flask Server
Run:  python contactbook_server.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import os, json, re
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.json")

app = Flask(__name__, template_folder=BASE_DIR, static_folder=BASE_DIR)
CORS(app)  

def _log(msg: str):
    print(f"[server] {msg}")

def _load_contacts() -> List[Dict]:
    if not os.path.exists(CONTACTS_FILE):
        _log("contacts.json not found; creating empty []")
        _save_contacts([])
        return []
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("contacts"), list):
                # accept legacy shape
                return data["contacts"]
            _log("contacts.json had unexpected shape; using empty list")
            return []
    except Exception as e:
        _log(f"load error: {e}")
        return []

def _save_contacts(contacts: List[Dict]) -> bool:
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        _log(f"save error: {e}")
        return False

def _index_by_name(contacts: List[Dict], name: str) -> int:
    key = (name or "").strip().lower()
    for i, c in enumerate(contacts):
        if (c.get("name") or "").strip().lower() == key:
            return i
    return -1

def _valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (email or "")) is not None

def _valid_phone(phone: str) -> bool:
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return len(digits) >= 10

# ---------- pages ----------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/script.js")
def js():
    return send_from_directory(BASE_DIR, "script.js")

@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")

# ---------- API ----------

@app.route("/api/contacts", methods=["GET"])
def api_list():
    contacts = _load_contacts()
    _log(f"GET /api/contacts -> {len(contacts)} items")
    return jsonify({"success": True, "data": contacts, "count": len(contacts)})

@app.route("/api/contacts", methods=["POST"])
def api_add():
    try:
        body = request.get_json(force=True) or {}
    except Exception as e:
        _log(f"POST parse error: {e}")
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    name  = (body.get("name")  or "").strip()
    phone = (body.get("phone") or "").strip()
    email = (body.get("email") or "").strip()
    _log(f"POST add name='{name}' phone='{phone}' email='{email}'")

    if not name or not phone or not email:
        return jsonify({"success": False, "error": "All fields are required"}), 400
    if not _valid_phone(phone):
        return jsonify({"success": False, "error": "Phone must contain at least 10 digits"}), 400
    if not _valid_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    contacts = _load_contacts()
    if _index_by_name(contacts, name) != -1:
        return jsonify({"success": False, "error": "Contact with that name already exists"}), 400

    contacts.append({"name": name, "phone": phone, "email": email})
    if not _save_contacts(contacts):
        return jsonify({"success": False, "error": "Failed to save contact"}), 500

    _log(f"POST saved. Total now {len(contacts)}")
    return jsonify({"success": True, "message": "Contact added"})

@app.route("/api/contacts/<name>", methods=["PUT"])
def api_update(name):
    try:
        body = request.get_json(force=True) or {}
    except Exception as e:
        _log(f"PUT parse error: {e}")
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    new_name = (body.get("name")  or "").strip()
    phone    = (body.get("phone") or "").strip()
    email    = (body.get("email") or "").strip()
    _log(f"PUT update '{name}' -> '{new_name}'")

    if not new_name or not phone or not email:
        return jsonify({"success": False, "error": "All fields are required"}), 400
    if not _valid_phone(phone):
        return jsonify({"success": False, "error": "Phone must contain at least 10 digits"}), 400
    if not _valid_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    contacts = _load_contacts()
    idx = _index_by_name(contacts, name)
    if idx == -1:
        return jsonify({"success": False, "error": "Contact not found"}), 404

    # prevent rename collision
    other = _index_by_name(contacts, new_name)
    if other != -1 and other != idx:
        return jsonify({"success": False, "error": "Another contact already has that name"}), 400

    contacts[idx] = {"name": new_name, "phone": phone, "email": email}
    if not _save_contacts(contacts):
        return jsonify({"success": False, "error": "Failed to save contact"}), 500

    _log("PUT saved successfully")
    return jsonify({"success": True, "message": "Contact updated"})

@app.route("/api/contacts/<name>", methods=["DELETE"])
def api_delete(name):
    contacts = _load_contacts()
    before = len(contacts)
    contacts = [c for c in contacts if (c.get("name") or "").lower() != (name or "").lower()]
    if len(contacts) == before:
        return jsonify({"success": False, "error": "Contact not found"}), 404
    if not _save_contacts(contacts):
        return jsonify({"success": False, "error": "Failed to delete contact"}), 500
    _log(f"DELETE '{name}' ok. Total now {len(contacts)}")
    return jsonify({"success": True, "message": f"Deleted '{name}'"})

# ---------- main ----------

if __name__ == "__main__":
    print("="*64)
    print("Contact Book Server")
    print(f"Serving from: {BASE_DIR}")
    print(f"Contacts file: {CONTACTS_FILE}")
    print(f"Exists: {os.path.exists(CONTACTS_FILE)}")
    print("="*64)
    app.run(host="127.0.0.1", port=5000, debug=True)
