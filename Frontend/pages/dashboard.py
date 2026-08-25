from asyncio import timeout

import streamlit as st
import requests
import pandas as pd
import traceback
from pathlib import Path
from config import API_URL

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊"
)


# ==========================
# ERROR HANDLER
# ==========================

def handle_error(error):



    st.title("⚠️ Something went wrong")

    st.error(f"Error: {str(error)}")

    st.code(
        traceback.format_exc(),
        language="text"
    )

    if st.button("🏠 Go to Home", width="stretch"):
        st.switch_page("home.py")

try:




    def load_css():

        css_path = Path(__file__).parent.parent / "styles" / "style.css"

        with open(css_path, encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


    load_css()

    # ==========================
    # AUTH CHECK
    # ==========================

    if not st.session_state.get("logged_in"):
        st.switch_page("home.py")

    headers = {
        "Authorization": f"Bearer {st.session_state['token']}"
    }

    # ======================================
    # HEADER
    # ======================================

    left, right = st.columns([5, 2])

    with left:
        st.title("🎫 Smart Support Desk")
        st.caption("Customer Support Management System")

    with right:

        if st.session_state["user_type"] == "employee":

            st.info(
                f"""
    👤 **{st.session_state['name']}**

    🆔 Employee ID : {st.session_state['employee_id']}

    💼 Role : {st.session_state['role'].replace('_', ' ').title()}
    """
            )

        else:

            st.info(
                f"""
    👤 **{st.session_state['name']}**

    🙋 Customer
    """
            )

    st.divider()

    st.subheader("📊 Dashboard Overview")

    card1, card2, card3, card4 = st.columns(4)

    # ===========================
    # Sidebar Navigation
    # ===========================

    # ==========================
    # ADMIN DASHBOARD
    # ==========================

    if (
            st.session_state["user_type"] == "employee"
            and st.session_state["role"] == "admin"
    ):
        page = st.sidebar.radio(
            "📋 Navigation",
            [
                "🏠 Dashboard",
                "👥 Employees",
                "🎫 Tickets",
                "🛠 Agent Support",
                "🏢 Teams",
                "👤 Add Employee",
                "➕ Add Team"
            ]
        )

        # Get all  Employees data

        with st.spinner("Employees response..."):
            employee_response = requests.get(
                f"{API_URL}/admin/employees",
                headers=headers,
                timeout=30
            )

        # Get all Teams
        with st.spinner("Loading Team response..."):
            team_response = requests.get(
                f"{API_URL}/admin/teams",
                headers=headers,
                timeout=30
            )

        # open tickets
        with st.spinner("Loading Ticket response..."):
            ticket_response = requests.get(
                f"{API_URL}/tickets/open/count",
                headers=headers,
                timeout=30
            )

        # ticket priority
        priority_response = requests.get(
            f"{API_URL}/tickets/priority/stats",
            headers=headers,
            timeout=30
        )
        # customer tickets
        with st.spinner("Loading Top customer  response..."):
            top_customer_response = requests.get(
                f"{API_URL}/tickets/customers/top",
                headers=headers,
                timeout=30
            )

        if ticket_response.status_code == 200:
            open_tickets = ticket_response.json()["open_tickets"]
        else:
            open_tickets = "--"

        # total customer(users)
        with st.spinner("Loading customer  response..."):
            customer_response = requests.get(
                f"{API_URL}/customer/count",
                headers=headers,
                timeout=30
            )
        # All Tickets
        with st.spinner("Loading all tickets response..."):
            ticket_all_response = requests.get(
                f"{API_URL}/tickets/all",
                headers=headers,
                timeout=30
            )

        if customer_response.status_code == 200:
            customers = customer_response.json()["customers"]
        else:
            customers = "--"

        if employee_response.status_code == 200 and team_response.status_code == 200:

            employees = employee_response.json()
            teams = team_response.json()

            # Dashboard Cards
            card1, card2, card3, card4 = st.columns(4)

            with card1:
                st.metric(
                    label="👨 Employees",
                    value=len(employees)
                )

            with card2:
                st.metric(
                    label="🏢 Teams",
                    value=len(teams)
                )

            with card3:
                st.metric(
                    label="🎫 Open Tickets",
                    value=open_tickets
                )

            with card4:
                st.metric(
                    label="👥 Customers",
                    value=customers
                )
            st.divider()

            card1, card2 = st.tabs(
                ["Top Customers", "Tickets by Priority"]
            )
            with card1:
                if top_customer_response.status_code == 200:
                    customer_df = pd.DataFrame(
                        top_customer_response.json()
                    )

                    st.subheader("🏆 Top Customers")

                    st.dataframe(
                        customer_df,
                        width='stretch'
                    )

            with card2:
                st.subheader("🎫 Tickets by Priority")

                if priority_response.status_code == 200:

                    priority_data = priority_response.json()

                    if priority_data:

                        priority_df = pd.DataFrame(priority_data)

                        # Debug temporarily if needed
                        # st.write(priority_data)
                        # st.write(priority_df.columns.tolist())

                        if "priority" in priority_df.columns and "count" in priority_df.columns:

                            st.bar_chart(
                                priority_df,
                                x="priority",
                                y="count"
                            )

                        else:

                            st.warning(
                                "Priority API did not return 'priority' and 'count' columns."
                            )

                            st.write(
                                "Received columns:",
                                priority_df.columns.tolist()
                            )

                    else:

                        st.info("No ticket priority data available.")

                else:

                    st.error(
                        f"Unable to load priority statistics. "
                        f"Status: {priority_response.status_code}"
                    )

            st.divider()
            if page == "👥 Employees":

                st.subheader("👨‍💼 Employee Management")

                # Same width configuration for header and rows
                employee_cols = [
                    1,  # ID
                    1.5,  # Name
                    2.8,  # Email
                    1.3,  # Role
                    1.0,  # Active
                    2.4,  # Team
                    1.2,  # Assign
                    1.8,  # Status
                    1.2  # Delete
                ]

                # ==========================
                # HEADER
                # ==========================

                header = st.columns(employee_cols)

                header[0].markdown("**ID**")
                header[1].markdown("**Name**")
                header[2].markdown("**Email**")
                header[3].markdown("**Role**")
                header[4].markdown("**Active**")
                header[5].markdown("**Team**")
                header[6].markdown("**Assign**")
                header[7].markdown("**Status**")
                header[8].markdown("**Delete**")

                team_names = [t["team_name"] for t in teams]

                # ==========================
                # EMPLOYEE ROWS
                # ==========================

                for emp in employees:

                    with st.container(
                            border=True,
                            width="stretch"
                    ):

                        cols = st.columns(employee_cols)

                        with cols[0]:
                            st.write(emp["employee_id"])

                        with cols[1]:
                            st.write(emp["name"])

                        with cols[2]:
                            st.write(emp["email"])

                        with cols[3]:
                            st.write(emp["role"])

                        with cols[4]:

                            if emp["is_active"]:
                                st.markdown(
                                    '<span style="color:#22c55e; font-size:22px;">●</span>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    '<span style="color:#ef4444; font-size:22px;">●</span>',
                                    unsafe_allow_html=True
                                )

                        with cols[5]:

                            current_team = emp.get("team_name")

                            selected_team = st.selectbox(
                                "Team",
                                team_names,
                                index=(
                                    team_names.index(current_team)
                                    if current_team in team_names
                                    else 0
                                ),
                                key=f"team_{emp['id']}",
                                label_visibility="collapsed"
                            )

                        with cols[6]:

                            if st.button(
                                    "Assign",
                                    key=f"assign_{emp['id']}"
                            ):

                                # Find selected team's ID
                                selected_team_id = next(
                                    t["id"]
                                    for t in teams
                                    if t["team_name"] == selected_team
                                )

                                assign_response = requests.put(
                                    f"{API_URL}/admin/employees/{emp['id']}/team",
                                    json={
                                        "team_id": selected_team_id
                                    },
                                    headers=headers
                                )

                                if assign_response.status_code == 200:

                                    st.success(
                                        f"Team assigned successfully."
                                    )

                                    st.rerun()

                                else:

                                    try:
                                        error_data = assign_response.json()

                                        st.error(
                                            error_data.get(
                                                "detail",
                                                error_data.get(
                                                    "message",
                                                    "Failed to assign team."
                                                )
                                            )
                                        )

                                    except Exception:
                                        st.error(assign_response.text)

                        with cols[7]:

                            # Current status
                            status_text = (
                                "Deactivate"
                                if emp["is_active"]
                                else "Activate"
                            )

                            if st.button(
                                    status_text,
                                    key=f"status_{emp['id']}"
                            ):

                                try:

                                    # Call FastAPI status toggle endpoint
                                    status_response = requests.put(
                                        f"{API_URL}/admin/employees/{emp['id']}/status",
                                        headers=headers
                                    )

                                    # ==========================
                                    # SUCCESS
                                    # ==========================

                                    if status_response.status_code == 200:

                                        data = status_response.json()

                                        if data["is_active"]:

                                            st.success(
                                                "Employee activated successfully."
                                            )

                                        else:

                                            st.success(
                                                "Employee deactivated successfully."
                                            )

                                        # Reload employees from database
                                        st.rerun()

                                    # ==========================
                                    # ERROR
                                    # ==========================

                                    else:

                                        try:

                                            error_data = status_response.json()

                                            st.error(
                                                error_data.get(
                                                    "detail",
                                                    error_data.get(
                                                        "message",
                                                        "Unable to update employee status."
                                                    )
                                                )
                                            )
                                        except Exception as e:

                                            st.error(
                                                status_response.text
                                            )


                                except requests.exceptions.RequestException as e:

                                    st.error(
                                        f"Backend connection error: {e}"
                                    )

                        with cols[8]:

                            if st.button(
                                    "Delete",
                                    key=f"delete_{emp['id']}"
                            ):
                                # Your delete API here
                                pass
            if page == "🏢 Teams":
                st.subheader("🏢 Teams Management")
                team_df = pd.DataFrame(team_response.json())

                if not team_df.empty:

                    st.dataframe(
                        team_df[["id", "team_name"]],
                        width='stretch'
                    )

                else:
                    st.info("No teams found.")

                st.divider()
            if page == "👤 Add Employee":
                with st.expander("👤 Add Support Agent"):
                    st.subheader("New Support Agent")

                    with st.form("add_employee"):

                        name = st.text_input("Name")

                        email = st.text_input("Email")

                        password = st.text_input(
                            "Password",
                            type="password"
                        )

                        submitted = st.form_submit_button(
                            "Create Support Agent"
                        )

                        if submitted:

                            response = requests.post(
                                f"{API_URL}/admin/employees",
                                json={
                                    "name": name,
                                    "email": email,
                                    "password": password
                                },
                                headers=headers
                            )

                            data = response.json()

                            if response.status_code == 200:
                                st.success(data["message"])
                                st.write("Support Agent added")
                                st.rerun()
                            else:
                                st.error(data["message"])
            if page == "➕ Add Team":
                with st.expander("➕ Add New Team"):

                    team_name = st.text_input("Team Name")

                    if st.button("Add Team", width='stretch'):

                        if not team_name:
                            st.error("Please enter a team name.")

                        else:

                            response = requests.post(
                                f"{API_URL}/admin/teams",
                                json={
                                    "team_name": team_name,
                                },
                                headers=headers
                            )

                            if response.status_code == 201:
                                st.success("Team added successfully.")
                                st.rerun()

                            else:
                                st.error(response.json()["detail"])
            if page == "🎫 Tickets":

                st.subheader("🎫 All Support Tickets")

                if ticket_all_response.status_code == 200:

                    tickets = ticket_all_response.json()

                    if not tickets:

                        st.info(
                            "No tickets available."
                        )


                    else:

                        ticket_df = pd.DataFrame(tickets)

                        st.dataframe(
                            ticket_df[
                                [
                                    "ticket_number",
                                    "title",
                                    "priority",
                                    "status",
                                    "team_id",
                                    "customer_id"
                                ]
                            ],
                            width='stretch'
                        )


                else:

                    st.error(
                        "Unable to fetch tickets."
                    )
            if page == "🛠 Agent Support":

                st.subheader("🛠 Support Agent Requests")

                all_ticket_response = requests.get(
                    f"{API_URL}/agent-support/all",
                    headers=headers
                )

                if all_ticket_response.status_code == 200:

                    tickets = all_ticket_response.json()

                    open_tab, resolved_tab = st.tabs(
                        [
                            "🆕 Open Requests",
                            "✅ Resolved Requests"
                        ]
                    )

                    # =====================================
                    # OPEN REQUESTS
                    # =====================================
                    with open_tab:

                        open_tickets = [
                            t for t in tickets
                            if t["status"] == "Open"
                        ]

                        if not open_tickets:
                            st.info("No open support requests.")

                        else:

                            for ticket in open_tickets:

                                with st.container(border=True):

                                    col1, col2 = st.columns([5, 1])

                                    with col1:

                                        st.write(f"### {ticket['ticket_number']}")
                                        st.write(f"**Employee ID:** {ticket['employee_id']}")
                                        st.write(f"**Title:** {ticket['title']}")
                                        st.write(f"**Priority:** {ticket['priority']}")
                                        st.write(f"**Status:** {ticket['status']}")

                                    with col2:

                                        if st.button(
                                                "Accept",
                                                key=f"accept_{ticket['id']}"
                                        ):

                                            request_accept = requests.put(
                                                f"{API_URL}/agent-support/{ticket['id']}/accept",
                                                headers=headers
                                            )

                                            if request_accept.status_code == 200:
                                                st.success("Support request accepted.")
                                                st.rerun()
                                            else:
                                                st.error(request_accept.text)

                    # =====================================
                    # RESOLVED REQUESTS
                    # =====================================
                    with resolved_tab:

                        resolved_tickets = [
                            t for t in tickets
                            if t["status"] == "Resolved..Done"
                        ]

                        if not resolved_tickets:
                            st.info("No resolved support requests.")

                        else:

                            for ticket in resolved_tickets:

                                with st.container(border=True):

                                    st.write(f"### {ticket['ticket_number']}")
                                    st.write(f"**Employee ID:** {ticket['employee_id']}")
                                    st.write(f"**Title:** {ticket['title']}")
                                    st.write(f"**Priority:** {ticket['priority']}")

                                    st.success("✅ Resolved")

                                    if ticket.get("assigned_admin"):
                                        st.write(
                                            f"**Resolved By Admin ID:** {ticket['assigned_admin']}"
                                        )

                                    if ticket.get("resolved_at"):
                                        st.write(
                                            f"**Resolved At:** {ticket['resolved_at']}"
                                        )

                else:
                    st.error(all_ticket_response.text)

    # ==========================
    # Support agent DASHBOARD
    # ==========================

    elif (
            st.session_state["user_type"] == "employee"
            and st.session_state["role"] == "support_agent"
    ):

        st.subheader("👨‍💻 Support Agent Dashboard")

        st.success(f"Team ID : {st.session_state['team_id']}")

        st.divider()

        # Create three separate sections
        open_tab, assigned_tab, support_tabs = st.tabs(
            [
                "🆕 Open Tickets",
                "📌 My Assigned Tickets",
                "🆘 Contact Admin"
            ]
        )

        # ==========================
        # OPEN TICKETS TAB
        # ==========================
        with open_tab:

            st.subheader("🆕 Open Tickets")

            response = requests.get(
                f"{API_URL}/tickets/team/{st.session_state['team_id']}",
                headers=headers
            )

            if response.status_code == 200:

                tickets = response.json()

                if not tickets:

                    st.info("No open tickets.")


                else:

                    for ticket in tickets:

                        with st.container(border=True):

                            st.write(
                                f"### {ticket['ticket_number']}"
                            )

                            st.write(
                                f"**Title:** {ticket['title']}"
                            )

                            st.write(
                                f"**Priority:** {ticket['priority']}"
                            )

                            st.write(
                                f"**Status:** {ticket['status']}"
                            )

                            if st.button(
                                    "Accept Ticket",
                                    key=f"accept_{ticket['id']}"
                            ):

                                res = requests.put(
                                    f"{API_URL}/tickets/{ticket['id']}/accept",
                                    params={
                                        "employee_id": st.session_state["employee_id"]
                                    }
                                )

                                if res.status_code == 200:
                                    st.success(
                                        "Ticket Accepted"
                                    )

                                    st.rerun()

        # ==========================
        # ASSIGNED TICKETS TAB
        # ==========================
        with assigned_tab:

            st.subheader("📌 My Assigned Tickets")

            response = requests.get(
                f"{API_URL}/tickets/assigned/{st.session_state['employee_id']}",
                headers=headers
            )

            if response.status_code == 200:

                tickets = response.json()

                if not tickets:
                    st.info("No assigned tickets.")

                else:

                    for ticket in tickets:

                        with st.container(border=True):

                            card1, card2, card3 = st.columns([2, 2, 0.9])

                            # ==========================
                            # LEFT
                            # ==========================

                            with card1:

                                st.markdown(
                                    f"### 🎫 {ticket['ticket_number']}"
                                )

                                st.markdown(
                                    f"**Title:** {ticket['title']}"
                                )

                            # ==========================
                            # MIDDLE
                            # ==========================

                            with card2:

                                st.markdown(
                                    f"**Status:** {ticket['status']}"
                                )

                                st.markdown(
                                    f"**Customer ID:** {ticket['customer_id']}"
                                )

                                st.markdown(
                                    f"**Priority:** {ticket['priority']}"
                                )

                            # ==========================
                            # RIGHT
                            # ==========================

                            with card3:

                                if ticket["status"].lower() != "closed":

                                    if st.button(
                                            "✅ Close Ticket",
                                            key=f"close_{ticket['id']}"
                                    ):

                                        res = requests.put(
                                            f"{API_URL}/tickets/{ticket['id']}/close",
                                            headers=headers
                                        )

                                        if res.status_code == 200:
                                            st.success("Ticket Closed Successfully")
                                            st.rerun()

                                        else:
                                            st.error("Unable to close ticket.")

                                else:

                                    st.success("✅ Closed")

        # ==========================
        # Support agent TICKETS TAB
        # ==========================
        with support_tabs:

            team_response = requests.get(
                f"{API_URL}/agent-support/teams",
                headers=headers
            )

            teams = team_response.json()

            team_names = [t["team_name"] for t in teams]

            st.subheader("🆘 Raise Support Request")

            with st.form("agent_support_form"):

                title = st.text_input("Title")

                description = st.text_area("Describe your issue")

                selected_team = st.selectbox(
                    "Assign To Team",
                    team_names
                )

                priority = st.selectbox(
                    "Priority",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Critical"
                    ]
                )
                team_id = next(
                    t["id"]
                    for t in teams
                    if t["team_name"] == selected_team
                )

                submit = st.form_submit_button("Submit")

                if submit:

                    support_response = requests.post(
                        f"{API_URL}/agent-support/tickets/{st.session_state['employee_id']}",
                        json={
                            "title": title,
                            "description": description,
                            "priority": priority,
                            "team_id": team_id
                        },
                        headers=headers
                    )

                    if support_response.status_code == 200:
                        st.success("Support request created.")
                        st.rerun()
                    else:
                        st.error(support_response.json()["message"])

            # -----------------------------------------
            # My Support Requests
            # -----------------------------------------

            support_response = requests.get(
                f"{API_URL}/agent-support/my-tickets/{st.session_state['employee_id']}",
                headers=headers
            )

            if support_response.status_code == 200:

                tickets = support_response.json()

                st.divider()
                st.subheader("📋 My Support Requests")

                if not tickets:
                    st.info("No support requests.")

                else:

                    for ticket in tickets:

                        with st.container(border=True):

                            st.write(f"### {ticket['ticket_number']}")
                            st.write(f"**Title:** {ticket['title']}")
                            st.write(f"**Priority:** {ticket['priority']}")
                            st.write(f"**Status:** {ticket['status']}")

                            if ticket.get("assigned_admin"):
                                st.write(
                                    f"***Assigned Admin***"
                                )

                            if ticket.get("resolved_at"):
                                st.success(
                                    f"Resolved At: {ticket['resolved_at']}"
                                )

    # ==========================
    # customer DASHBOARD
    # ==========================
    else:

        st.subheader("🙋 Customer Dashboard")

        profile_tab, ticket_tab = st.tabs(
            [
                "👤 My Profile",
                "🎫 My Tickets"
            ]
        )

        # ==================================
        # MY PROFILE
        # ==================================
        with profile_tab:

            st.subheader("👤 My Profile")

            with st.form("customer_profile"):

                name = st.text_input(
                    "Name",
                    value=st.session_state["name"]
                )

                email = st.text_input(
                    "Email",
                    value=st.session_state["email"]
                )

                submitted = st.form_submit_button(
                    "💾 Update Profile"
                )

                if submitted:

                    response = requests.put(
                        f"{API_URL}/customer/profile/{st.session_state['customer_id']}",
                        json={
                            "name": name,
                            "email": email
                        },
                        headers=headers
                    )

                    if response.status_code == 200:

                        st.session_state["name"] = name
                        st.session_state["email"] = email
                        st.write("Profile updated successfully.")
                        st.rerun()
                    else:
                        st.error(response.json()["detail"])

        # ==================================
        # MY TICKETS
        # ==================================
        with ticket_tab:

            team_response = requests.get(
                f"{API_URL}/customer/teams",
                headers=headers
            )

            teams = team_response.json()

            team_names = [t["team_name"] for t in teams]

            st.subheader("➕ Raise New Ticket")

            with st.form("ticket_form"):

                title = st.text_input("Title")

                description = st.text_area("Description")

                selected_team = st.selectbox(
                    "Select Team",
                    team_names
                )

                priority = st.selectbox(
                    "Priority",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Critical"
                    ]
                )

                submit = st.form_submit_button("Raise Ticket")

                if submit:

                    team_id = next(
                        t["id"]
                        for t in teams
                        if t["team_name"] == selected_team
                    )

                    response = requests.post(
                        f"{API_URL}/tickets/",
                        json={
                            "title": title,
                            "description": description,
                            "team_id": team_id,
                            "priority": priority,
                            "customer_id": st.session_state["customer_id"]
                        },
                        headers=headers
                    )

                    if response.status_code == 200:
                        st.success("Ticket Raised Successfully")
                        st.rerun()

                    else:
                        st.error(f"Status Code: {response.status_code}")
                        st.write(response.text)

            st.divider()

            st.subheader("🎫 My Tickets")

            response = requests.get(
                f"{API_URL}/tickets/customer/{st.session_state['customer_id']}",
                headers=headers
            )

            if response.status_code == 200:

                tickets = response.json()

                if not tickets:

                    st.info("No tickets found.")

                else:

                    df = pd.DataFrame(tickets)

                    st.dataframe(
                        df[
                            [
                                "ticket_number",
                                "title",
                                "priority",
                                "status"
                            ]
                        ],
                        width='stretch'
                    )
except Exception as e:

    handle_error(e)
# ==========================
# LOGOUT
# ==========================
if st.sidebar.button("Logout"):
    st.session_state.clear()

    st.switch_page(
        "home.py"
    )