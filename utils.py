# utils.py - SHARED DATABASE CONNECTION
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

@st.cache_resource
def init_db():
    conn = sqlite3.connect('food_ordering_pro.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                 password TEXT, email TEXT, phone TEXT, role TEXT DEFAULT 'customer', 
                 join_date TEXT, total_orders INTEGER DEFAULT 0, total_spent REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, price REAL, 
                 description TEXT, category TEXT, image TEXT, stock INTEGER DEFAULT 100, 
                 is_available BOOLEAN DEFAULT 1, added_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, 
                 total REAL, status TEXT, order_date TEXT, delivery_date TEXT, 
                 payment_method TEXT, items TEXT, address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, order_id INTEGER, 
                 rating INTEGER, comment TEXT, review_date TEXT)''')
    
    # Sample menu
    sample_menu = [
        ('🍔 Classic Burger', 180, 'Juicy beef patty with cheese', 'Main Course', 'burger.jpg', 50, 1, datetime.now().isoformat()),
        ('🍕 Margherita Pizza', 320, 'Fresh mozzarella & basil', 'Main Course', 'pizza.jpg', 30, 1, datetime.now().isoformat()),
        ('🥗 Caesar Salad', 140, 'Crisp romaine with dressing', 'Healthy', 'salad.jpg', 40, 1, datetime.now().isoformat()),
        ('🥤 Pepsi 500ml', 60, 'Ice cold refreshment', 'Drinks', 'pepsi.jpg', 100, 1, datetime.now().isoformat()),
        ('🍦 Vanilla Ice Cream', 95, 'Creamy vanilla delight', 'Dessert', 'icecream.jpg', 60, 1, datetime.now().isoformat())
    ]
    c.executemany('INSERT OR IGNORE INTO menu VALUES (NULL, ?,?,?,?,?,?,?,?)', sample_menu)
    conn.commit()
    return conn

# Get database connection
conn = init_db()
