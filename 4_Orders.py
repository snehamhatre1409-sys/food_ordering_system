import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn
import time

# ✅ Session State
if "user_id" not in st.session_state: st.session_state.user_id = 1
if "tracking_order_id" not in st.session_state: st.session_state.tracking_order_id = None

st.markdown('<h1 class="main-header">📋 My Orders</h1>', unsafe_allow_html=True)
st.markdown("---")

# 🔧 FIXED: Load orders + Convert total to FLOAT
orders_df = pd.read_sql(f"""
    SELECT o.*, u.username 
    FROM orders o JOIN users u ON o.user_id = u.id 
    WHERE o.user_id = {st.session_state.user_id} 
    ORDER BY order_date DESC LIMIT 10
""", conn)

# ✅ CRITICAL FIX: Convert 'total' from TEXT to FLOAT
if not orders_df.empty:
    orders_df['total'] = pd.to_numeric(orders_df['total'], errors='coerce')
    orders_df['total_display'] = orders_df['total'].apply(lambda x: f"₹{x:.0f}" if pd.notna(x) else "₹0")

if orders_df.empty:
    st.info("👋 **No orders yet.** Go to Menu to order!")
    st.button("🍽️ Browse Menu")
    st.stop()

# 📦 Orders List
st.markdown("## 📦 **Recent Orders**")
for _, order in orders_df.iterrows():
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        with st.expander(f"**Order #{order['id']}** • {order.get('total_display', '₹0')} • {order['status'].title()}"):
            st.markdown(f"**📦 Items:** {order['items'][:100]}...")
            st.markdown(f"📍 **{order['address'][:60]}...**")
            st.caption(f"🕒 {order['order_date'][:16] if order['order_date'] else 'N/A'}")
    
    with col2:
        status = order['status'].lower()
        badges = {
            "pending": "🟡 Pending", "received": "🔵 Received", 
            "shipped": "🟠 Shipped", "delivered": "🟢 Delivered",
            "completed": "✅ Completed"
        }
        st.markdown(f"**{badges.get(status, '⚪ Unknown')}**")
    
    with col3:
        if st.button(f"📦 Track", key=f"track_{order['id']}"):
            st.session_state.tracking_order_id = order['id']
            st.rerun()

st.markdown("---")

# 🚚 LIVE TRACKING
if st.session_state.tracking_order_id:
    st.markdown("## 🚚 **Live Order Tracking**")
    tracking_order = pd.read_sql(f"SELECT * FROM orders WHERE id = ?", 
                                conn, params=(st.session_state.tracking_order_id,)).iloc[0]
    
    # Simple 4-Step Progress
    steps = ["📥 Received", "👨‍🍳 Cooking", "🚚 Shipped", "✅ Delivered"]
    status_map = {"pending": 0, "received": 0, "preparing": 1, "shipped": 2, "delivered": 3}
    current_step = status_map.get(tracking_order['status'].lower(), 0)
    
    for i, step in enumerate(steps):
        col1, col2 = st.columns([4, 1])
        with col1:
            if i <= current_step:
                st.markdown(f"✅ **{step}**")
            else:
                st.markdown(f"⏳ **{step}**")
        with col2:
            st.markdown(f"{i+1}/4")
    
    # Progress Bar
    st.progress((current_step + 1) / 4)
    
    # Order Info
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📦 Order", f"#{tracking_order['id']}")
    with col2: st.metric("💰 Total", tracking_order.get('total_display', '₹0'))
    with col3: st.metric("⏱️ ETA", "25 mins")
    
    st.markdown("### 📍 **Delivery Details**")
    st.info(f"🚗 **Driver:** Rajesh | 📱 **+91-98765-43210**")
    st.caption(f"📍 **{tracking_order['address'][:60]}...**")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if tracking_order['status'] in ['delivered', 'shipped']:
            if st.button("✅ **Order Received**"):
                c = conn.cursor()
                c.execute("UPDATE orders SET status = 'completed' WHERE id = ?", 
                         (tracking_order['id'],))
                conn.commit()
                st.balloons()
                st.session_state.tracking_order_id = None
                st.rerun()
    with col2:
        if st.button("❌ **Stop Tracking**"):
            st.session_state.tracking_order_id = None
            st.rerun()

# 📊 SIMPLE STATS (FIXED!)
st.markdown("---")
st.markdown("### 📊 **Quick Stats**")
col1, col2, col3, col4 = st.columns(4)

# ✅ FIXED: Safe numeric conversion
total_spent = orders_df['total'].sum() if not orders_df['total'].isna().all() else 0
delivered_count = len(orders_df[orders_df['status'] == 'delivered'])

col1.metric("📦 Total Orders", len(orders_df))
col2.metric("✅ Delivered", delivered_count)
col3.metric("💰 Spent", f"₹{total_spent:.0f}")
col4.metric("⭐ Rating", "4.8")

# Quick Actions
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1: st.button("🍽️ New Order", type="primary")
with col2: st.button("🛒 Cart", type="secondary") 
with col3: st.button("📞 Support", type="secondary")
