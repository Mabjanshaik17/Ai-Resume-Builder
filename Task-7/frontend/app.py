import streamlit as st
import requests
import re
import sys
import os
from utils import save_history, load_history, search_history

# Resolve path to Task-4 backend folder
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../Task-4/backend"))

# Add backend path to Python import search path
if backend_path not in sys.path:
    sys.path.append(backend_path)

from auth import register_user, login_user
from main import parse_basic_info, extract_text_from_pdf


# =========================================
# 🔹 CONFIGURATION & INITIALIZATION
# =========================================
st.set_page_config(page_title="AI Resume Manager", layout="wide")

BACKEND_URL = "http://localhost:8000/upload_resume"

if "resume_records" not in st.session_state:
    st.session_state.resume_records = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================
# 🔹 APP TITLE
# =========================================
st.title("AI-Powered Resume Manager")

# Sidebar Navigation Menu
menu = st.sidebar.radio(
    "Select Page",
    ["Registration", "Login", "Upload Resume", "Dashboard"]
)

# =========================================
# 🔹 REGISTRATION PAGE
# =========================================
if menu == "Registration":

    st.header("Create New Account")


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

# =========================================
# 🔹 LOGIN PAGE
# =========================================
elif menu == "Login":

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
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.success(message)
                else:
                    st.error(message)

# =========================================
# 🔹 UPLOAD RESUME PAGE
# =========================================
elif menu == "Upload Resume":
    # Initialize storage
    if "resume_records" not in st.session_state:
        st.session_state.resume_records = []

    st.header("Upload a Resume for Parsing")

    uploaded = st.file_uploader("Choose PDF or DOCX", type=["pdf", "docx"])

    if uploaded:

        with st.spinner("Processing your resume..."):
            files = {"file": uploaded}
            response = requests.post(BACKEND_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            parsed = data.get("parsed_info", {})
            extracted = data.get("extracted_text", "")

            # Save parsed data to session storage
            st.session_state.resume_records.append({
                "filename": uploaded.name,
                "parsed": parsed,
                "extracted": extracted
            })

            st.success("Resume Parsed Successfully!")

            emails = parsed.get("emails", [])

            st.markdown("##### 📧 Email Addresses")

            if emails:
                for email in emails:
                    st.write(f"- {email}")
            else:
                st.write("No email found")

            st.write("##### 📞 Phone Numbers")
            phones = parsed.get("phones", [])

            if phones:
                for phone in phones:
                    st.write(f"- {phone}")
            else:
                st.write("No phone number found")

            st.info(f"📌 Total resumes stored locally: {len(st.session_state.resume_records)}")

        else:
            st.error("Error parsing file. Check backend.")

# =========================================
# 🔹 DASHBOARD PAGE
# =========================================
elif menu == "Dashboard":



    if not st.session_state.logged_in:
        st.warning("⚠ Please login to access dashboard.")
        st.stop()

    email = st.session_state.user_email
    user = parse_basic_info(email)
    st.subheader("Parsed Resume Data")
    if st.session_state.resume_records:
        for rec in st.session_state.resume_records:
            st.write(f"**📄 File: {rec['filename']}**")
            parsed = rec["parsed"]

            st.write(f"**👤 Name:** {parsed.get('name', 'Not found')}")

            st.write("**📧 Email(s):**")
            emails = parsed.get("emails", [])
            if emails:
                for email in emails:
                    st.write(f"- {email}")
            else:
                st.write("No email found")

            st.write("**📞 Phone Number(s):**")
            phones = parsed.get("phones", [])
            if phones:
                for phone in phones:
                    st.write(f"- {phone}")
            else:
                st.write("No phone number found")

            st.write("**💼 Skills:**")
            skills = parsed.get("skills", [])
            if skills:
                for skill in skills:
                    st.write(f"- {skill}")
            else:
                st.write("No skills found")
            with st.expander("View Extracted Text"):
                st.write(rec["extracted"])
    else:
        st.info("No stored resume data yet.")
