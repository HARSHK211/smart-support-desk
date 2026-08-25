import streamlit as st


st.set_page_config(
    page_title="Error",
    page_icon="⚠️"
)


st.title("⚠️ Something went wrong")

st.error(
    "An unexpected error occurred."
)

st.write(
    "Please try again or return to the home page."
)


if st.button(
    "🏠 Go to Home",
    width="stretch"
):

    st.switch_page(
        "home.py"
    )