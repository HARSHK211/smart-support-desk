import streamlit as st


def handle_error(error):

    st.error(
        "⚠️ Something went wrong."
    )

    st.write(
        "Please try again or return to the home page."
    )

    if st.button(
        "🏠 Go to Error Page",
        width="stretch"
    ):

        st.switch_page(
            "pages/error_page.py"
        )