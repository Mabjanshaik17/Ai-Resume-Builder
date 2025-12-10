import streamlit as st
import re
import sys
import os

# --------------------------
# Backend Path
# --------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, "..", "..", "Task-4", "backend")
backend_path = os.path.abspath(backend_path)

if backend_path not in sys.path:
    sys.path.append(backend_path)

from auth import register_user

# --------------------------
# Validation functions
# --------------------------
def valid_name(name):
    return bool(re.match(r"^[A-Za-z ]+$", name))

def valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def valid_password(password):
    return len(password) >= 6

# --------------------------
# Registration UI
# --------------------------
st.title("User Registration")
with st.form("register_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

    if submitted:
        if not full_name or not email or not password or not confirm_password:
            st.error("All fields are required.")
        elif not valid_name(full_name):
            st.error("Name must contain alphabets only.")
        elif not valid_email(email):
            st.error("Invalid email address.")
        elif not valid_password(password):
            st.error("Password must be at least 6 characters.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = register_user(full_name, email, password)
            if success:
                st.success(message)
            else:
                st.error(message)
