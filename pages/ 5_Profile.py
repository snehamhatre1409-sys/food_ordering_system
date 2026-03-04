import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn  # ← THIS FIXES THE ERROR!

st.title("👤 My Profile")
st.markdown("---")

user_data = pd.read_sql(f"SELECT * FROM users WHERE id={st.session_state.user_id}", conn).iloc[0]

col1, col2 = st.columns(2)
with col1:
    st.metric("👤 Username", user_data['username'])
    st.metric("📧 Email", user_data['email'])
    st.metric("📱 Phone", user_data['phone'])
with col2:
    st.metric("🎂 Member Since", user_data['join_date'][:10])
    total_orders = pd.read_sql(f"SELECT COUNT(*) as count FROM orders WHERE user_id={st.session_state.user_id}", conn).iloc[0]['count']
    total_spent = pd.read_sql(f"SELECT SUM(total) as spent FROM orders WHERE user_id={st.session_state.user_id}", conn).iloc[0]['spent']
    st.metric("🛒 Total Orders", total_orders)
    st.metric("💰 Total Spent", f"₹{total_spent or 0}")

with st.form("update_profile"):
    new_email = st.text_input("Email", user_data['email'])
    new_phone = st.text_input("Phone", user_data['phone'])
    if st.form_submit_button("Update Profile"):
        c = conn.cursor()
        c.execute("UPDATE users SET email=?, phone=? WHERE id=?", (new_email, new_phone, st.session_state.user_id))
        conn.commit()
        st.success("Profile updated!")

