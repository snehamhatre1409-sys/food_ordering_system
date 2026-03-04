import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn  # ← THIS FIXES THE ERROR!


st.title("🔐 Login / Register")
st.markdown("---")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Login"):
            c = conn.cursor()
            c.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
                     (username, password))
            user = c.fetchone()
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.role = user[2]
                st.success(f"✅ Welcome back, {user[1]}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

with tab2:
    with st.form("register_form"):
        new_username = st.text_input("👤 New Username")
        new_password = st.text_input("🔒 New Password", type="password")
        email = st.text_input("📧 Email")
        phone = st.text_input("📱 Phone")
        role = st.selectbox("Role", ["customer", "admin"])
        
        if st.form_submit_button("Register"):
            try:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, email, phone, role, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                         (new_username, new_password, email, phone, role, datetime.now().isoformat()))
                conn.commit()
                st.success("✅ Registered successfully! Please login.")
            except Exception as e:
                st.error("❌ Username already exists")

