import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import qrcode
from io import BytesIO
import base64

# Database setup
@st.cache_resource
def init_db():
    conn = sqlite3.connect('food_ordering.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'customer')''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, description TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total REAL, status TEXT DEFAULT 'pending', 
                  order_date TEXT, items TEXT, tracking_status TEXT DEFAULT 'preparing',
                  tracking_updated TEXT, payment_status TEXT DEFAULT 'pending')''')
    
    sample_menu = [
        ('Burger', 150.0, 'Juicy beef patty', 'Main'),
        ('Pizza', 300.0, 'Cheese overload Margherita', 'Main'),
        ('Salad', 100.0, 'Fresh veggies', 'Healthy'),
        ('Soda', 50.0, 'Refreshing drink', 'Drink'),
        ('Ice Cream', 80.0, 'Vanilla delight', 'Dessert')
    ]
    c.executemany('INSERT OR IGNORE INTO menu (name, price, description, category) VALUES (?, ?, ?, ?)', sample_menu)
    conn.commit()
    return conn

conn = init_db()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'show_payment' not in st.session_state:
    st.session_state.show_payment = False
if 'selected_order' not in st.session_state:
    st.session_state.selected_order = None

st.set_page_config(page_title="Food Ordering System", page_icon="🍔", layout="wide")

# Migration
def migrate_db():
    c = conn.cursor()
    c.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'tracking_status' not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN tracking_status TEXT DEFAULT 'preparing'")
    if 'tracking_updated' not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN tracking_updated TEXT")
    if 'payment_status' not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'pending'")
    
    c.execute("UPDATE orders SET tracking_status='preparing', payment_status='pending' WHERE tracking_status IS NULL")
    conn.commit()
    return "Migration complete! 🎉"

# QR Payment
def generate_qr_payment(order_id, amount):
    upi_url = f"upi://pay?pa=foodordering@paytm&pn=FoodApp&am={amount}&cu=INR&tn=Order-{order_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return base64.b64encode(bio.getvalue()).decode()

def show_payment_modal():
    st.markdown("## 💳 Complete Payment")
    order_df = pd.read_sql(f"SELECT * FROM orders WHERE id={st.session_state.selected_order}", conn)
    if not order_df.empty:
        order = order_df.iloc[0]
        st.info(f"Order #{order['id']} - Total: ₹{order['total']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📱 Scan to Pay")
            qr_code = generate_qr_payment(order['id'], order['total'])
            st.image(f"data:image/png;base64,{qr_code}", use_column_width=True)
        
        with col2:
            st.info("1. Open UPI app\n2. Scan QR\n3. Pay ₹{:.0f}\n4. Click 'Payment Done'".format(order['total']))
            
            if st.button("✅ Payment Completed", type="primary"):
                c = conn.cursor()
                c.execute("UPDATE orders SET payment_status='paid', tracking_status='preparing', tracking_updated=? WHERE id=?", 
                         (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), st.session_state.selected_order))
                conn.commit()
                st.success("✅ Payment confirmed!")
                st.session_state.show_payment = False
                st.rerun()
    st.button("❌ Cancel", on_click=lambda: setattr(st.session_state, 'show_payment', False) or st.rerun())

def login_page():
    st.title("🍔 Food Ordering System - Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            c = conn.cursor()
            c.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.role = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["customer", "admin"])
        if st.button("Register"):
            try:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, role))
                conn.commit()
                st.success("Registered! Login now.")
            except:
                st.error("Username exists")

def customer_dashboard():
    st.title(f"Welcome, Customer! 🍕")
    menu_df = pd.read_sql("SELECT * FROM menu", conn)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Menu")
        category = st.selectbox("Category", menu_df['category'].unique())
        filtered = menu_df[menu_df['category'] == category]
        for _, row in filtered.iterrows():
            if st.button(f"{row['name']} - ₹{row['price']}"):
                st.session_state.cart.append({'name': row['name'], 'price': row['price'], 'qty': 1})
                st.rerun()
    
    with col2:
        st.subheader("Cart")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            cart_df['subtotal'] = cart_df['qty'] * cart_df['price']
            total = cart_df['subtotal'].sum()
            st.dataframe(cart_df)
            st.metric("Total", f"₹{total}")
            if st.button("Place Order"):
                items_json = cart_df.to_json(orient='records')
                c = conn.cursor()
                c.execute("INSERT INTO orders (user_id, total, order_date, items) VALUES (?, ?, ?, ?)", 
                         (st.session_state.user_id, total, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), items_json))
                conn.commit()
                st.session_state.cart = []
                st.success("Order placed!")
                st.rerun()
        else:
            st.info("Cart empty")
    
    # Order Tracking
    st.subheader("📦 Order Tracking")
    orders_df = pd.read_sql(f"SELECT * FROM orders WHERE user_id={st.session_state.user_id} ORDER BY order_date DESC", conn)
    if not orders_df.empty:
        for _, order in orders_df.iterrows():
            with st.expander(f"Order #{order['id']} - ₹{order['total']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    color = "🟢" if order['payment_status'] == 'paid' else "🟡"
                    st.metric("Payment", f"{color} {order['payment_status'].title()}")
                with col2:
                    status_map = {'preparing':'🍳 Preparing', 'cooking':'🔥 Cooking', 'ready':'✅ Ready', 'delivered':'🚚 Delivered'}
                    st.metric("Status", status_map.get(order['tracking_status'], order['tracking_status']))
                with col3:
                    if order['payment_status'] == 'pending':
                        if st.button(f"💳 Pay ₹{order['total']}", key=f"pay_{order['id']}"):
                            st.session_state.selected_order = order['id']
                            st.session_state.show_payment = True
                if order['items']:
                    items = pd.read_json(order['items'])
                    st.dataframe(items)
        
        if st.session_state.show_payment:
            show_payment_modal()
    else:
        st.info("No orders yet")

def admin_dashboard():
    st.title("Admin Dashboard 👨‍💼")
    tab1, tab2, tab3 = st.tabs(["Menu", "Orders", "Analytics"])
    
    with tab1:
        st.subheader("Manage Menu")
        with st.form("add_menu"):
            name = st.text_input("Name")
            price = st.number_input("Price")
            desc = st.text_area("Description")
            cat = st.text_input("Category")
            if st.form_submit_button("Add Item"):
                c = conn.cursor()
                c.execute("INSERT INTO menu (name, price, description, category) VALUES (?, ?, ?, ?)", (name, price, desc, cat))
                conn.commit()
                st.success("Added!")
        st.dataframe(pd.read_sql("SELECT * FROM menu", conn))
    
    with tab2:
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
        st.dataframe(orders_df[['id', 'user_id', 'total', 'status', 'tracking_status', 'payment_status']])
    
    with tab3:
        revenue_df = pd.read_sql("SELECT SUM(total) as revenue, COUNT(*) as orders FROM orders WHERE status='pending'", conn)
        col1, col2 = st.columns(2)
        col1.metric("Pending Revenue", f"₹{revenue_df['revenue'].iloc[0] or 0}")
        col2.metric("Pending Orders", revenue_df['orders'].iloc[0] or 0)

# Sidebar
st.sidebar.title("⚙️ Controls")
if st.sidebar.checkbox("🔧 Migrate DB (one-time)"):
    st.sidebar.success(migrate_db())

st.sidebar.button("Logout", on_click=lambda: (setattr(st.session_state, 'logged_in', False), setattr(st.session_state, 'user_id', None), setattr(st.session_state, 'role', None), st.rerun()))

# Main app
if not st.session_state.logged_in:
    login_page()
elif st.session_state.role == 'customer':
    customer_dashboard()
else:
    admin_dashboard()
