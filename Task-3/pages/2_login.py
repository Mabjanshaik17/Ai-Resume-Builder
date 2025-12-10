import sys
import os
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../Task-4/backend"))
sys.path.append(backend_path)

from auth import login_user

# -----------------------------------
# Login UI
# -----------------------------------
st.title("User Login")

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

                st.session_state["user_email"] = email
                st.success(message)
                st.switch_page("pages/dashboard.py")
            else:
                st.error(message)
