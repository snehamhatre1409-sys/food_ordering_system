import streamlit as st
import pandas as pd
import sqlite3

# 1. PAGE CONFIG
st.set_page_config(page_title="User Profile", page_icon="👤")

# 2. LOGIN SAFETY CHECK
# This prevents the AttributeError you saw earlier
if "user_id" not in st.session_state:
    st.warning("⚠️ Access Denied. Please go to the Login page first.")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop() 

# 3. DATABASE CONNECTION
# Ensure this matches your filename on GitHub (e.g., food_ordering.db)
conn = sqlite3.connect('food_ordering.db')

try:
    # 4. FETCH USER DATA
    # We use the ID stored in session_state during login
    query = f"SELECT * FROM users WHERE id={st.session_state.user_id}"
    user_df = pd.read_sql(query, conn)

    if not user_df.empty:
        user_data = user_df.iloc[0]
        
        st.title(f"👋 Welcome, {user_data['username']}!")
        st.subheader("Your Profile Details")
        
        # Displaying data in a nice layout
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Email:** {user_data['email']}")
            st.info(f"**Phone:** {user_data.get('phone', 'Not provided')}")
        
        with col2:
            st.info(f"**Account Status:** Active")
            st.info(f"**Member Since:** 2024")

        # 5. FETCH RECENT ORDERS (Optional but recommended)
        st.divider()
        st.subheader("📦 Your Recent Orders")
        order_query = f"SELECT id, item_name, price, status FROM orders WHERE user_id={st.session_state.user_id} ORDER BY id DESC"
        orders_df = pd.read_sql(order_query, conn)
        
        if not orders_df.empty:
            st.dataframe(orders_df, use_container_width=True)
        else:
            st.write("You haven't placed any orders yet!")

    else:
        st.error("User record not found in database.")

except Exception as e:
    st.error(f"Error loading profile: {e}")

finally:
    conn.close()

# 6. LOGOUT BUTTON
if st.sidebar.button("Log Out"):
    del st.session_state.user_id
    st.rerun()
