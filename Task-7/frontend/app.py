import streamlit as st
import requests
import sys
import os

import pandas as pd
from utils import save_history, load_history, search_history

BACKEND_URL = "http://localhost:8000/upload_resume"

st.set_page_config(page_title="AI Resume Manager", layout="wide")

st.title("AI-Powered Resume Manager")

menu = st.sidebar.radio(
    "Select Page",
    ["Registration", "Login", "Upload Resume", "Dashboard"]
)

# ---------------------------
# PAGE 1 — Upload Resume
# ---------------------------
if menu == "Upload Resume":

    st.header("Upload a Resume for Parsing")

    uploaded = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

    if uploaded:

        # Send to backend
        with st.spinner("Processing your resume..."):
            files = {"file": uploaded}
            response = requests.post(BACKEND_URL, files=files)

        if response.status_code == 200:
            data = response.json()

            parsed = data["parsed_info"]
            extracted = data["extracted_text"]

            # Display results
            st.success("Resume Updated Successfully!")


        else:
            st.error("Error parsing file. Check backend.")

# ---------------------------
# PAGE 2 — Resume History
# ---------------------------
# ---------------------------
# PAGE — Registration
# ---------------------------
elif menu == "Registration":

    import re
    import sys
    import os

    # Backend path setup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(current_dir, "..", "..", "Task-4", "backend")
    backend_path = os.path.abspath(backend_path)

    if backend_path not in sys.path:
        sys.path.append(backend_path)

    from auth import register_user

    st.header("Create New Account")

    # Validation functions
    def valid_name(name):
        return bool(re.match(r"^[A-Za-z ]+$", name))

    def valid_email(email):
        return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

    def valid_password(password):
        return len(password) >= 6

    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")

        if submitted:

            # Validations
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



# ---------------------------
# PAGE — Login
# ---------------------------
elif menu == "Login":

    import sys
    import os

    # Add backend path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.abspath(os.path.join(current_dir, "../../Task-4/backend"))
    if backend_path not in sys.path:
        sys.path.append(backend_path)

    from auth import login_user

    st.header("User Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:

            if not email or not password:
                st.error("Please fill all fields.")

            else:
                success, message = login_user(email, password)

                if success:
                    st.success(message)
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = email
                else:
                    st.error(message)

import streamlit as st
import sys
import os

# -----------------------------------
# Import backend modules
# -----------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../Task-6/backend"))
sys.path.append(backend_path)

from parse_utils import parse_basic_info



# -----------------------------------
# DASHBOARD FUNCTION
# -----------------------------------
def dashboard():
    st.title("User Dashboard")

    # Check login session
    if "user_email" not in st.session_state:
        st.error("You are not logged in! Please login first.")
        return

    email = st.session_state["user_email"]
    user = get_user_details(email)

    st.subheader(f"Welcome, {user.get('name', 'User')} 👋")
    st.write(f"**Email:** {email}")

    st.markdown("---")
    st.header("Upload and Parse Resume")

    uploaded_file = st.file_uploader("Select your Resume (PDF / DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        # Temporary save
        temp_path = "temp_resume"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Uploading successful! Parsing your resume...")

        # Parse using backend
        parsed_output = parse_basic_info(text=uploaded_file.read())

        # Show parsed text
        st.subheader("📄 Parsed Resume Text")
        st.text_area("Extracted Text", parsed_output, height=350)

        # Save to session
        st.session_state["parsed_resume"] = parsed_output

        # Remove temporary file
        os.remove(temp_path)
