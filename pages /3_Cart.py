import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils import conn
import streamlit.components.v1 as components
import time   # ✅ Added this line (missing import)

st.set_page_config(page_title="Shopping Cart", page_icon="🛒")

st.markdown('<h1 class="main-header">🛒 Shopping Cart</h1>', unsafe_allow_html=True)
st.divider()

# ✅ Session State
if 'cart' not in st.session_state or not st.session_state.cart:
    st.info("🛒 **Your cart is empty!** Browse delicious items from Menu!")
    if st.button("🍽️ Go to Menu", type="primary"):
        st.switch_page("pages/2_Menu.py")
    st.stop()

# 📊 Cart Data
df = pd.DataFrame(st.session_state.cart)
df['Subtotal'] = df['qty'] * df['price']
total_amount = df['Subtotal'].sum()

# 🖼️ Cart Display + Summary
col_left, col_right = st.columns([2.5, 1])
with col_left:
    st.dataframe(df[['name', 'qty', 'price', 'Subtotal']], 
                use_container_width=True, hide_index=True)

with col_right:
    st.markdown("### 💰 **Order Summary**")
    st.metric("🛍️ Items", len(df))
    st.metric("💰 Total Amount", f"₹{total_amount:.0f}")
    if st.button("🗑️ Clear Cart", type="secondary"):
        st.session_state.cart = []
        st.rerun()

st.divider()

# 🔧 Item Management
st.subheader("✏️ **Manage Items**")
for idx, item in enumerate(st.session_state.cart):
    cols = st.columns([3, 1, 1, 1])
    cols[0].markdown(f"**{item['name']}**")
    cols[0].caption(f"₹{item['price']} each")
    
    # Quantity Controls
    if cols[1].button("➖", key=f"minus_{idx}"):
        if item['qty'] > 1:
            st.session_state.cart[idx]['qty'] -= 1
        st.rerun()
    
    cols[2].metric("Qty", item['qty'])
    
    if cols[3].button("❌", key=f"remove_{idx}"):
        st.session_state.cart.pop(idx)
        st.rerun()

st.divider()

# 💳 CHECKOUT with SMALLER UPI QR ✅
st.subheader("🚀 **Checkout**")

with st.form("checkout_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        payment = st.selectbox("💳 **Payment Method**", 
                              ["Cash on Delivery", "UPI", "Card", "Wallet"])
        
        address = st.text_area("📍 **Delivery Address**", 
                              placeholder="House No, Street, Landmark, City, PIN...")
    
    with col2:
        st.markdown("### 📦 **Order Details**")
        st.info(f"🛍️ **{len(df)} items**")
        st.info(f"💰 **₹{total_amount:.0f}**")
        st.info("🚚 **30 mins delivery**")
        st.caption("*Free delivery over ₹200*")
    
    # 🔥 SMALLER UPI QR CODE (150x150 instead of 250x250) ✅
    if payment == "UPI":
        st.markdown("### 📱 **Scan to Pay**")
        st.image(
            "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa=kfoodhub@okaxis&pn=K-Food%20Hub&am=500&cu=INR&tn=Order%20Payment",
            caption="**Scan with GPay/PhonePe**",
            use_column_width=False
        )
        st.info("💡 Amount will be auto-filled based on cart total")
        st.caption("**UPI ID: kfoodhub@okaxis**")
    
    submit = st.form_submit_button("✅ **PLACE ORDER**", type="primary", use_container_width=True)
    
    if submit:
        if not address.strip():
            st.error("❌ **Please enter delivery address!**")
        elif 'user_id' not in st.session_state:
            st.error("❌ **Please login first!**")
        else:
            try:
                order_items_json = json.dumps(st.session_state.cart)
                order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (user_id, total, status, order_date, payment_method, items, address) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    st.session_state.user_id, total_amount, 'Pending', 
                    order_time, payment, order_items_json, address
                ))
                conn.commit()
                
                st.session_state.cart = []
                st.success("🎉 **Order placed successfully!**")
                st.balloons()
                st.markdown("### 📱 Check **Orders** page for tracking 🚚")
                time.sleep(2)
                st.switch_page("pages/4_Orders.py")
                
            except Exception as e:
                st.error(f"❌ Order failed: {str(e)}")

# 📱 Quick Links
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1: st.button("🍽️ Add More Items", type="secondary")
with col2: st.button("📋 View Orders", type="secondary")
with col3: st.button("🆘 Support", type="secondary")

