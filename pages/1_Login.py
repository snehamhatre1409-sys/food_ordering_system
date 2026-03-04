import streamlit as st
import sqlite3
from datetime import datetime

# --- 1. DATABASE SETUP (Integrated into utils logic) ---
# Ensuring the table exists prevents "Table not found" errors
def init_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
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
    return conn

# Initialize connection
conn = init_db()

# --- 2. SESSION STATE MANAGEMENT ---
# This checks if a user is already logged in for this browser session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- 3. UI LOGIC: LOGGED IN VIEW ---
if st.session_state.logged_in:
    st.title(f"👋 Welcome, {st.session_state.username}!")
    st.subheader(f"Role: {st.session_state.role.capitalize()}")
    st.info("You are currently logged into the system.")
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    st.stop() # This prevents the login/register tabs from showing up

# --- 4. UI LOGIC: LOGIN / REGISTER TABS ---
st.title("🔐 User Portal")
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
                c.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
                         (username, password))
                user = c.fetchone()
                
                if user:
                    # Save user info to session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.role = user[2]
                    st.success(f"✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("Please fill in both fields.")

with tab2:
    with st.form("register_form"):
        new_username = st.text_input("👤 Choose Username")
        new_password = st.text_input("🔒 Choose Password", type="password")
        email = st.text_input("📧 Email Address")
        phone = st.text_input("📱 Phone Number")
        role = st.selectbox("Assign Role", ["customer", "admin"])
        submit_reg = st.form_submit_button("Create Account")
        
        if submit_reg:
            if new_username and new_password:
                try:
                    c = conn.cursor()
                    c.execute("""INSERT INTO users (username, password, email, phone, role, join_date) 
                                 VALUES (?, ?, ?, ?, ?, ?)""",
                             (new_username, new_password, email, phone, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("✨ Registration successful! You can now switch to the Login tab.")
                except sqlite3.IntegrityError:
                    st.error("❌ That username is already taken. Try another.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")
            else:
                st.warning("Username and Password are required for registration.")
