import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import conn

# 1. Page Configuration
st.set_page_config(page_title="Admin Analytics", layout="wide")

# 2. Security Check (Prevents AttributeError)
if st.session_state.get('role') != 'admin':
    st.error("🔒 Admin access required! Please log in as an admin.")
    st.stop()

st.title("📊 Admin Analytics Dashboard")
st.divider()

# 3. Data Fetching & Processing
try:
    # Fetch all data once to save database resources
    df_all_orders = pd.read_sql("SELECT * FROM orders", conn)
    
    if not df_all_orders.empty:
        # --- FIX: THE DATE ERROR ---
        # We tell pandas to be flexible with 'mixed' formats
        df_all_orders['order_date'] = pd.to_datetime(df_all_orders['order_date'], format='mixed')
        
        # 4. KPI Calculations
        delivered_orders = df_all_orders[df_all_orders['status'] == 'delivered']
        total_revenue = delivered_orders['total'].sum()
        total_orders_count = len(delivered_orders)
        unique_customers = df_all_orders['user_id'].nunique()
        
        # 5. KPI Section Display
        col1, col2, col3, col4 = st.columns(4)
        with col1: 
            st.metric("💰 Total Revenue", f"₹{total_revenue:,.2f}")
        with col2: 
            st.metric("📦 Delivered Orders", total_orders_count)
        with col3: 
            st.metric("👥 Total Customers", unique_customers)
        with col4: 
            st.metric("⭐ Avg Rating", "4.8")

        st.divider()

        # 6. Charts Section
        col_left, col_right = st.columns(2)

        with col_left:
            # Group by date for Trend Line
            orders_by_date = df_all_orders.groupby(df_all_orders['order_date'].dt.date).size().reset_index(name='count')
            fig1 = px.line(
                orders_by_date, 
                x='order_date', 
                y='count', 
                title="📈 Daily Order Trends",
                labels={'order_date': 'Date', 'count': 'Number of Orders'},
                template="plotly_dark"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_right:
            # Group by status for Pie Chart
            revenue_by_status = df_all_orders.groupby('status')['total'].sum().reset_index()
            fig2 = px.pie(
                revenue_by_status, 
                values='total', 
                names='status', 
                title="🍰 Revenue Distribution by Status",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 7. Recent Transactions Table
        st.subheader("📑 Recent Activity")
        st.dataframe(
            df_all_orders.sort_values('order_date', ascending=False).head(10), 
            use_container_width=True
        )

    else:
        st.info("No order data available yet to generate analytics.")

except Exception as e:
    st.error(f"Error loading analytics: {e}")
    st.warning("Ensure your 'orders' table contains 'total', 'status', and 'order_date' columns.")
