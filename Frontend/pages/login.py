import streamlit as st
import requests
from config import API_URL


st.set_page_config(
    page_title="Login",
    page_icon="🔐"
)

st.title("🔐 Login")


email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)


if st.button("Login", width="stretch"):

    if not email:
        st.error("Please enter your email.")
        st.stop()

    if not password:
        st.error("Please enter your password.")
        st.stop()

    try:

        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": email.strip(),
                "password": password
            }
        )

        if response.status_code == 200:

            data = response.json()


            if data["message"] == "Login Successful":

                # ==========================
                # Common Login Information
                # ==========================

                st.session_state["token"] = data["access_token"]

                st.session_state["logged_in"] = True

                st.session_state["name"] = data["name"]

                st.session_state["email"] = data["email"]

                st.session_state["role"] = data["role"]

                st.session_state["user_type"] = data["user_type"]


                # ==========================
                # Employee
                # ==========================

                if data["user_type"] == "employee":

                    st.session_state["employee_id"] = data["employee_id"]

                    # Team can be None if admin has not
                    # assigned a team yet
                    st.session_state["team_id"] = data.get("team_id")


                # ==========================
                # Customer
                # ==========================

                elif data["user_type"] == "customer":

                    st.session_state["customer_id"] = data["customer_id"]




                # ==========================
                # Go Dashboard
                # ==========================

                st.switch_page(
                    "pages/dashboard.py"
                )

            else:

                st.error(
                    data.get(
                        "message",
                        "Login failed."
                    )
                )

        else:

            try:
                data = response.json()

                st.error(
                    data.get(
                        "message",
                        data.get(
                            "detail",
                            "Login failed."
                        )
                    )
                )

            except Exception:

                st.error(
                    f"Login failed. "
                    f"Status Code: {response.status_code}"
                )

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Cannot connect to the FastAPI server. "
            "Please start the backend on port 8000."
        )

    except Exception as e:

        st.error(
            f"Unexpected error: {e}"
        )