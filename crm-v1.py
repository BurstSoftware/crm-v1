import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from typing import Optional

# Set page configuration
st.set_page_config(page_title="CRM Dashboard", layout="wide")

# Title
st.title("📊 Customer Relationship Management (CRM) Dashboard")

# File path for data persistence
DATA_FILE: str = "customers.csv"

# Load data from CSV or initialize with sample data if the file doesn't exist
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Ensure consistent data types
        df["Customer ID"] = pd.to_numeric(df["Customer ID"], errors="coerce").fillna(0).astype(int)
        df["Last Contacted"] = pd.to_datetime(df["Last Contacted"], errors="coerce")
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0).astype(int)
        df["Status"] = df["Status"].astype(str)
        df["Name"] = df["Name"].astype(str)
        df["Email"] = df["Email"].astype(str)
        df["Phone"] = df["Phone"].astype(str)
    else:
        # Sample data with consistent types
        data = {
            "Customer ID": [1, 2, 3, 4, 5],
            "Name": ["John Doe", "Jane Smith", "Alice Brown", "Bob Johnson", "Emma Wilson"],
            "Email": ["john@example.com", "jane@example.com", "alice@example.com", "bob@example.com", "emma@example.com"],
            "Phone": ["555-0101", "555-0102", "555-0103", "555-0104", "555-0105"],
            "Status": ["Active", "Lead", "Inactive", "Active", "Lead"],
            "Sales": [5000, 2000, 0, 8000, 3000],
            "Last Contacted": ["2023-10-01", "2023-09-15", "2023-08-20", "2023-10-10", "2023-09-25"]
        }
        df = pd.DataFrame(data)
        df["Last Contacted"] = pd.to_datetime(df["Last Contacted"])
        df.to_csv(DATA_FILE, index=False)  # Save initial data to CSV
    return df

# Save data to CSV
def save_data(df: pd.DataFrame) -> None:
    df_to_save = df.copy()
    # Ensure "Last Contacted" is in datetime format before saving
    df_to_save["Last Contacted"] = pd.to_datetime(df_to_save["Last Contacted"], errors="coerce")
    # Convert datetime to string for CSV storage, handling NaT values
    df_to_save["Last Contacted"] = df_to_save["Last Contacted"].apply(
        lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""
    )
    df_to_save.to_csv(DATA_FILE, index=False)

# Initialize session state for the DataFrame
if "df" not in st.session_state:
    st.session_state.df = load_data()

# Reference to the DataFrame in session state
df: pd.DataFrame = st.session_state.df

# Sidebar for navigation
st.sidebar.header("Navigation")
page: str = st.sidebar.selectbox("Choose a page", ["Dashboard", "Customer Management", "Reports"])

# Dashboard Page
if page == "Dashboard":
    st.header("Overview")

    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(df))
    with col2:
        st.metric("Total Sales", f"${df['Sales'].sum():,.2f}")
    with col3:
        st.metric("Active Customers", len(df[df["Status"] == "Active"]))

    # Visualizations
    st.subheader("Customer Insights")
    col1, col2 = st.columns(2)

    with col1:
        # Sales by Customer
        fig_sales = px.bar(df, x="Name", y="Sales", title="Sales by Customer", color="Status")
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        # Customer Status Distribution
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(status_counts, values="Count", names="Status", title="Customer Status Distribution")
        st.plotly_chart(fig_status, use_container_width=True)

# Customer Management Page
elif page == "Customer Management":
    st.header("Manage Customers")

    # Filter customers
    st.subheader("Filter Customers")
    status_filter = st.multiselect("Filter by Status", options=df["Status"].unique(), default=df["Status"].unique())
    filtered_df = df[df["Status"].isin(status_filter)].copy()

    # Ensure filtered_df has consistent types before displaying
    filtered_df["Customer ID"] = filtered_df["Customer ID"].astype(int)
    filtered_df["Last Contacted"] = pd.to_datetime(filtered_df["Last Contacted"], errors="coerce")
    filtered_df["Sales"] = filtered_df["Sales"].astype(int)

    # Display the DataFrame with error handling
    try:
        st.dataframe(filtered_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying DataFrame: {str(e)}")
        st.write("DataFrame contents for debugging:", filtered_df)

    # Add new customer
    st.subheader("Add New Customer")
    with st.form("add_customer_form"):
        name: str = st.text_input("Name")
        email: str = st.text_input("Email")
        phone: str = st.text_input("Phone")
        status: str = st.selectbox("Status", ["Active", "Lead", "Inactive"])
        sales: int = st.number_input("Sales", min_value=0, step=100)
        last_contacted = st.date_input("Last Contacted", datetime.today())
        submit: bool = st.form_submit_button("Add Customer")

        if submit:
            # Basic validation
            if not name or not email:
                st.error("Name and Email are required fields!")
            elif email in df["Email"].values:
                st.error("A customer with this email already exists!")
            else:
                # Ensure Customer ID is numeric and find the maximum
                df["Customer ID"] = pd.to_numeric(df["Customer ID"], errors="coerce").fillna(0).astype(int)
                max_id: float = df["Customer ID"].max() if not df.empty else 0
                if pd.isna(max_id):
                    max_id = 0
                # Convert last_contacted to a pandas Timestamp
                last_contacted_ts = pd.Timestamp(last_contacted)
                new_customer = {
                    "Customer ID": int(max_id) + 1,
                    "Name": name,
                    "Email": email,
                    "Phone": phone,
                    "Status": status,
                    "Sales": sales,
                    "Last Contacted": last_contacted_ts
                }
                # Append the new customer to the DataFrame
                new_df = pd.DataFrame([new_customer])
                # Update the session state DataFrame
                st.session_state.df = pd.concat([df, new_df], ignore_index=True)
                # Persist changes to CSV
                save_data(st.session_state.df)
                st.success("Customer added successfully!")
                st.rerun()

    # Edit customer
    st.subheader("Edit Customer")
    if df.empty:
        st.warning("No customers available to edit.")
    else:
        customer_id: int = st.selectbox("Select Customer ID", df["Customer ID"])
        selected_customer = df[df["Customer ID"] == customer_id].iloc[0]

        with st.form("edit_customer_form"):
            edit_name: str = st.text_input("Name", value=selected_customer["Name"])
            edit_email: str = st.text_input("Email", value=selected_customer["Email"])
            edit_phone: str = st.text_input("Phone", value=selected_customer["Phone"])
            edit_status: str = st.selectbox("Status", ["Active", "Lead", "Inactive"], index=["Active", "Lead", "Inactive"].index(selected_customer["Status"]))
            edit_sales: int = st.number_input("Sales", min_value=0, step=100, value=int(selected_customer["Sales"]))
            # Ensure the default value for st.date_input is a datetime.date object
            default_date = selected_customer["Last Contacted"].date() if pd.notna(selected_customer["Last Contacted"]) else datetime.today().date()
            edit_last_contacted = st.date_input("Last Contacted", value=default_date)
            edit_submit: bool = st.form_submit_button("Update Customer")

            if edit_submit:
                # Validate email uniqueness (excluding the current customer)
                if edit_email in df["Email"].values and edit_email != selected_customer["Email"]:
                    st.error("A customer with this email already exists!")
                else:
                    # Convert edit_last_contacted to a pandas Timestamp
                    edit_last_contacted_ts = pd.Timestamp(edit_last_contacted)
                    st.session_state.df.loc[df["Customer ID"] == customer_id, ["Name", "Email", "Phone", "Status", "Sales", "Last Contacted"]] = [
                        edit_name, edit_email, edit_phone, edit_status, edit_sales, edit_last_contacted_ts
                    ]
                    save_data(st.session_state.df)  # Persist changes
                    st.success("Customer updated successfully!")
                    st.rerun()

# Reports Page
elif page == "Reports":
    st.header("Reports")

    # Sales Trend
    st.subheader("Sales Trend")
    if df.empty:
        st.warning("No data available for reports.")
    else:
        df["Month"] = df["Last Contacted"].dt.to_period("M").astype(str)
        sales_trend = df.groupby("Month")["Sales"].sum().reset_index()
        fig_trend = px.line(sales_trend, x="Month", y="Sales", title="Monthly Sales Trend")
        st.plotly_chart(fig_trend, use_container_width=True)

        # Top Customers
        st.subheader("Top 5 Customers by Sales")
        top_customers = df.nlargest(5, "Sales")[["Name", "Sales"]]
        try:
            st.dataframe(top_customers, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying Top Customers: {str(e)}")
            st.write("Top Customers DataFrame for debugging:", top_customers)

# Footer
st.markdown("---")
st.write("Built with Streamlit")
