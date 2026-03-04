import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn  # Ensure your utils.py has a valid sqlite3 connection

# --- 1. INITIALIZE DATABASE TABLE ---
def init_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  email TEXT, 
                  phone TEXT, 
                  role TEXT, 
                  join_date TEXT)''')
    conn.commit()

init_db()

# --- 2. CHECK LOGIN STATE ---
# If user is already logged in, show a welcome message and a logout button
if "username" in st.session_state:
    st.title(f"👋 Welcome, {st.session_state.username}!")
    st.info(f"Logged in as: {st.session_state.role}")
    
    if st.button("Log Out"):
        for key in ["user_id", "username", "role"]:
            del st.session_state[key]
        st.rerun()
    st.stop() # Stops the rest of the script (login form) from running

# --- 3. LOGIN / REGISTER UI ---
st.title("🔐 Login / Register")
st.markdown("---")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        submit_login = st.form_submit_button("Login")

        if submit_login:
            if username and password:
                c = conn.cursor()
                # We use a tuple for parameters
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
                    st.error("❌ Invalid username or password")
            else:
                st.warning("Please enter both username and password")

with tab2:
    with st.form("register_form"):
        new_username = st.text_input("👤 New Username")
        new_password = st.text_input("🔒 New Password", type="password")
        email = st.text_input("📧 Email")
        phone = st.text_input("📱 Phone")
        role = st.selectbox("Role", ["customer", "admin"])
        submit_reg = st.form_submit_button("Register")
        
        if submit_reg:
            if new_username and new_password:
                try:
                    c = conn.cursor()
                    c.execute("""INSERT INTO users (username, password, email, phone, role, join_date) 
                                 VALUES (?, ?, ?, ?, ?, ?)""",
                             (new_username, new_password, email, phone, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("✅ Registered successfully! You can now log in.")
                except Exception as e:
                    # This usually triggers if the username (UNIQUE) already exists
                    st.error(f"❌ Registration failed: Username might already be taken.")
            else:
                st.warning("Username and Password are required.")
                
