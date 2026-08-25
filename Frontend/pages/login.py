import streamlit as st
import requests

from config import API_URL


# ==========================
# PAGE CONFIGURATION
# ==========================

st.set_page_config(
    page_title="Login",
    page_icon="🔐"
)

st.title("🔐 Login")


# ==========================
# LOGIN FORM
# ==========================

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)


# ==========================
# LOGIN BUTTON
# ==========================

if st.button("Login", width="stretch"):

    if not email:
        st.error("Please enter your email.")
        st.stop()

    if not password:
        st.error("Please enter your password.")
        st.stop()

    try:

        # ==========================
        # CALL FASTAPI LOGIN
        # ==========================

        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": email.strip(),
                "password": password
            },
            timeout=30
        )

        # ==========================
        # SUCCESS RESPONSE
        # ==========================

        if response.status_code == 200:

            data = response.json()

            if data.get("message") == "Login Successful":

                # ==========================
                # COMMON SESSION DATA
                # ==========================

                st.session_state["token"] = data.get(
                    "access_token"
                )

                st.session_state["logged_in"] = True

                st.session_state["name"] = data.get(
                    "name"
                )

                st.session_state["email"] = data.get(
                    "email"
                )

                st.session_state["role"] = data.get(
                    "role"
                )

                st.session_state["user_type"] = data.get(
                    "user_type"
                )

                # ==========================
                # EMPLOYEE SESSION DATA
                # ==========================

                if data.get("user_type") == "employee":

                    st.session_state["employee_id"] = data.get(
                        "employee_id"
                    )

                    st.session_state["team_id"] = data.get(
                        "team_id"
                    )

                    # Customer data is not required
                    st.session_state.pop(
                        "customer_id",
                        None
                    )

                # ==========================
                # CUSTOMER SESSION DATA
                # ==========================

                elif data.get("user_type") == "customer":

                    st.session_state["customer_id"] = data.get(
                        "customer_id"
                    )

                    # Employee data is not required
                    st.session_state.pop(
                        "employee_id",
                        None
                    )

                    st.session_state.pop(
                        "team_id",
                        None
                    )

                # ==========================
                # VERIFY LOGIN DATA
                # ==========================

                if not st.session_state.get("token"):

                    st.error(
                        "Login succeeded but access token "
                        "was not returned by the backend."
                    )
                    st.stop()

                # ==========================
                # GO TO DASHBOARD
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

        # ==========================
        # BACKEND ERROR
        # ==========================

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

    # ==========================
    # CONNECTION ERROR
    # ==========================

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Cannot connect to the FastAPI server."
        )

        st.info(
            f"Backend URL: {API_URL}"
        )

    # ==========================
    # TIMEOUT ERROR
    # ==========================

    except requests.exceptions.Timeout:

        st.error(
            "❌ Backend request timed out."
        )

    # ==========================
    # OTHER ERROR
    # ==========================

    except Exception as e:

        st.error(
            f"Unexpected error: {e}"
        )