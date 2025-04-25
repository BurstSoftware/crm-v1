import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="CRM Dashboard", layout="wide")

# Title
st.title("📊 Customer Relationship Management (CRM) Dashboard")

# Sample customer data (replace with your database or CSV file)
@st.cache_data
def load_data():
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
    return df

# Load data
df = load_data()

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Customer Management", "Reports"])

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
    
    # Sales by Customer
    fig_sales = px.bar(df, x="Name", y="Sales", title="Sales by Customer", color="Status")
    st.plotly_chart(fig_sales, use_container_width=True)
    
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
    filtered_df = df[df["Status"].isin(status_filter)]
    st.dataframe(filtered_df, use_container_width=True)
    
    # Add new customer
    st.subheader("Add New Customer")
    with st.form("add_customer_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        status = st.selectbox("Status", ["Active", "Lead", "Inactive"])
        sales = st.number_input("Sales", min_value=0, step=100)
        last_contacted = st.date_input("Last Contacted", datetime.today())
        submit = st.form_submit_button("Add Customer")
        
        if submit:
            new_customer = {
                "Customer ID": max(df["Customer ID"]) + 1,
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Status": status,
                "Sales": sales,
                "Last Contacted": last_contacted
            }
            df = pd.concat([df, pd.DataFrame([new_customer])], ignore_index=True)
            st.success("Customer added successfully!")
            st.experimental_rerun()
    
    # Edit customer
    st.subheader("Edit Customer")
    customer_id = st.selectbox("Select Customer ID", df["Customer ID"])
    selected_customer = df[df["Customer ID"] == customer_id].iloc[0]
    
    with st.form("edit_customer_form"):
        edit_name = st.text_input("Name", value=selected_customer["Name"])
        edit_email = st.text_input("Email", value=selected_customer["Email"])
        edit_phone = st.text_input("Phone", value=selected_customer["Phone"])
        edit_status = st.selectbox("Status", ["Active", "Lead", "Inactive"], index=["Active", "Lead", "Inactive"].index(selected_customer["Status"]))
        edit_sales = st.number_input("Sales", min_value=0, step=100, value=int(selected_customer["Sales"]))
        edit_last_contacted = st.date_input("Last Contacted", value=selected_customer["Last Contacted"])
        edit_submit = st.form_submit_button("Update Customer")
        
        if edit_submit:
            df.loc[df["Customer ID"] == customer_id, ["Name", "Email", "Phone", "Status", "Sales", "Last Contacted"]] = [
                edit_name, edit_email, edit_phone, edit_status, edit_sales, edit_last_contacted
            ]
            st.success("Customer updated successfully!")
            st.experimental_rerun()

# Reports Page
elif page == "Reports":
    st.header("Reports")
    
    # Sales Trend
    st.subheader("Sales Trend")
    df["Month"] = df["Last Contacted"].dt.to_period("M").astype(str)
    sales_trend = df.groupby("Month")["Sales"].sum().reset_index()
    fig_trend = px.line(sales_trend, x="Month", y="Sales", title="Monthly Sales Trend")
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Top Customers
    st.subheader("Top 5 Customers by Sales")
    top_customers = df.nlargest(5, "Sales")[["Name", "Sales"]]
    st.dataframe(top_customers, use_container_width=True)

# Save data (in a real app, save to a database or file)
def save_data():
    # For demonstration, we're not saving to a file or database
    pass

# Run the app
if __name__ == "__main__":
    st.write("Built with Streamlit")
