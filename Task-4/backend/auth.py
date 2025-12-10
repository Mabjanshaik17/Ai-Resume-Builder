import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


# -----------------------------
# Initialize DB
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
                """)
    conn.commit()
    conn.close()


init_db()


# -----------------------------
# Register user (hash here only)
# -----------------------------
def register_user(full_name, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Hash password ONCE here
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cur.execute(
            "INSERT INTO users (user_id, full_name, email, password) VALUES (?, ?, ?, ?)",
            (os.urandom(16).hex(), full_name, email, hashed_pw)
        )
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    finally:
        conn.close()


# -----------------------------
# Login user
# -----------------------------
def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        stored_pw = row[0]  # from DB

        # Convert to bytes ONLY if it's string
        if isinstance(stored_pw, str):
            stored_pw = stored_pw.encode()

        # Compare
        if bcrypt.checkpw(password.encode(), stored_pw):
            return True, "Login successful!"
        else:
            return False, "Incorrect password."

    return False, "Email not found."
