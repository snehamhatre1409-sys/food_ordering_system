import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn 

# 1. Access Control (Check this before doing anything else)
if st.session_state.get('role') != 'admin':
    st.error("🔒 Admin access required!")
    st.stop()

st.title("📋 Admin: Order Management")
st.markdown("---")

# 2. Load Data
orders_df = pd.read_sql("""
    SELECT o.*, u.username 
    FROM orders o JOIN users u ON o.user_id = u.id 
    ORDER BY order_date DESC
""", conn)

# 3. FIX: Convert the date column immediately after loading the DataFrame
# This handles the "format mismatch" error you were seeing
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], format='mixed')

# 4. Display the Data
st.dataframe(orders_df, use_container_width=True)

st.markdown("---")
st.subheader("Update Order Status")

# 5. Order Update Logic
if not orders_df.empty:
    selected_order = st.selectbox("Select Order ID", orders_df['id'])

    if selected_order:
        # Get details for the specific selected order
        order_details = orders_df[orders_df['id'] == selected_order].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            status_options = ["pending", "preparing", "out-for-delivery", "delivered", "cancelled"]
            # Set the default index to the current status of the order
            current_status_index = status_options.index(order_details['status']) if order_details['status'] in status_options else 0
            
            new_status = st.selectbox("Status", status_options, index=current_status_index)
            
        with col2:
            delivery_date = st.date_input("Delivery Date", value=datetime.now().date())
        
        if st.button("Update Status", use_container_width=True):
            c = conn.cursor()
            c.execute("UPDATE orders SET status=?, delivery_date=? WHERE id=?", 
                     (new_status, delivery_date.isoformat(), selected_order))
            conn.commit()
            st.success("✅ Status updated successfully!")
            st.rerun()
else:
    st.info("No orders found in the database.")
