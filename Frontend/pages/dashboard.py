import streamlit as st

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊"
)

st.title("📊 Smart Support Desk")

st.success("Dashboard loaded successfully!")

st.write("Logged in:", st.session_state.get("logged_in"))
st.write("Name:", st.session_state.get("name"))
st.write("Email:", st.session_state.get("email"))
st.write("Role:", st.session_state.get("role"))
st.write("User type:", st.session_state.get("user_type"))
st.write("Employee ID:", st.session_state.get("employee_id"))
st.write("Team ID:", st.session_state.get("team_id"))