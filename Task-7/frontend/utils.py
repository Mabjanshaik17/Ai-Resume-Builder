import json
import os

DB_FILE = "resume_history.json"

def load_history():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_history(record):
    history = load_history()
    history.append(record)
    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)

def search_history(query):
    query = query.lower()
    history = load_history()
    return [
        item for item in history
        if query in item["name"].lower()
        or any(query in s.lower() for s in item["skills"])
        or query in item["email"].lower()
    ]
