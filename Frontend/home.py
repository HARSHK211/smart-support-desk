import streamlit as st


st.set_page_config(
    page_title="Smart Support Desk",
    page_icon="🎫"
)

st.title("🎫 Smart Support Desk")

st.write("Welcome to Smart Support Desk")

# ==========================
# Check Login Status
# ==========================

if st.session_state.get("logged_in"):

    st.success(f"Welcome, {st.session_state['name']} 👋")

    if st.button(
        "🚪 Logout",
        width='stretch'
    ):
        st.session_state.clear()
        st.rerun()

else:

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔐 Login",
            width='stretch'
        ):
            st.switch_page("pages/login.py")

    with col2:

        if st.button(
            "📝 Register",
            width='stretch'
        ):
            st.switch_page("pages/register.py")