import streamlit as st
import requests
from config import API_URL

st.set_page_config(
    page_title="Register",
    page_icon="📝"
)

st.title("📝  Registration")


name = st.text_input("Full Name")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

confirm_password = st.text_input(
    "Confirm Password",
    type="password"
)


if st.button("Register", width='stretch'):

    if password != confirm_password:

        st.error("Passwords do not match")

    else:

        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": name,
                "email": email,
                "password": password
            }
        )

        # st.write("Status Code:", response.status_code)
        # st.write("Response:", response.text)

        try:
            data = response.json()
        except Exception:
            st.error("Backend did not return JSON.")
            st.stop()

        if response.status_code == 200:
            st.success(data["message"])
        else:
            st.error(data)


if st.button("⬅ Back to Login"):

    st.switch_page("pages/login.py")