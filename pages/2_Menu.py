import streamlit as st
import pandas as pd
import time
from utils import conn

# ✅ Session State
if 'cart' not in st.session_state: 
    st.session_state.cart = []
if 'user_id' not in st.session_state: 
    st.session_state.user_id = 1

st.markdown('<h1 class="main-header">🍽️ Menu - Fresh & Delicious</h1>', unsafe_allow_html=True)

# Check login
if not st.session_state.get('user_id'):
    st.warning("👤 Please login first!")
    st.stop()

# 🔥 10 PREMIUM RECIPES - SIMPLE CARDS ✅
MENU_RECIPES = {
    "Veg": [
        {"name": "Paneer Butter Masala", "price": 220, "desc": "Creamy paneer in rich tomato gravy"},
        {"name": "Mushroom Do Pyaza", "price": 190, "desc": "Spicy mushrooms with double onions"},
        {"name": "Dal Makhani", "price": 160, "desc": "Slow-cooked black lentils with butter"},
        {"name": "Paneer Tikka Masala", "price": 240, "desc": "Grilled paneer in creamy gravy"},
        {"name": "Veg Biryani", "price": 200, "desc": "Aromatic rice with mixed vegetables"}
    ],
    "Non-Veg": [
        {"name": "Butter Chicken", "price": 250, "desc": "Classic creamy chicken curry"},
        {"name": "Chicken Tikka Masala", "price": 260, "desc": "Grilled chicken in tomato gravy"},
        {"name": "Mutton Rogan Josh", "price": 320, "desc": "Kashmiri spicy lamb curry"},
        {"name": "Fish Fry", "price": 280, "desc": "Crispy spiced fish fillets"},
        {"name": "Chicken Biryani", "price": 280, "desc": "Royal fragrant chicken rice"}
    ]
}

# 🌟 Veg/Non-Veg Tabs
tab1, tab2 = st.tabs(["🌱 Vegetarian (5)", "🍗 Non-Vegetarian (5)"])

def display_recipe(recipe):
    """Simple clean recipe card"""
    col1, col2 = st.columns([0.3, 2.7])  # Smaller left column
    
    with col1:
        st.markdown("### #")
    
    with col2:
        st.markdown(f"## **{recipe['name']}**")
        st.markdown(f"*{recipe['desc']}*")
        st.markdown(f"**Price: ₹{recipe['price']}**")
        
        col_btn, col_stock = st.columns([2, 1])
        with col_btn:
            if st.button("🛒 **ADD TO CART**", key=f"add_{recipe['name']}"):
                st.session_state.cart.append({
                    'name': recipe['name'], 
                    'price': recipe['price'], 
                    'qty': 1
                })
                st.success(f"✅ **{recipe['name']}** added!")
                st.balloons()
                st.rerun()
        with col_stock:
            st.success("**In Stock**")

# Vegetarian Tab
with tab1:
    for recipe in MENU_RECIPES["Veg"]:
        st.markdown("---")
        display_recipe(recipe)

# Non-Veg Tab
with tab2:
    for recipe in MENU_RECIPES["Non-Veg"]:
        st.markdown("---")
        display_recipe(recipe)

# 🛒 Cart Preview
st.markdown("---")
st.markdown("## 🛒 **Cart Summary**")
col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    total_items = len(st.session_state.cart)
    total_price = sum(item['price'] * item.get('qty', 1) for item in st.session_state.cart)
    st.metric("🛍️ Items", total_items)
    st.metric("💰 Total", f"₹{total_price}")

with col2:
    if st.session_state.cart:
        for item in st.session_state.cart[-3:]:
            st.caption(f"✅ {item['name']}")

with col3:
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🛒 **FULL CART**", type="primary"):
            st.switch_page("pages/3_Cart.py")
    with col_btn2:
        if st.button("✅ **CHECKOUT**", type="secondary"):
            st.switch_page("pages/3_order.py")
