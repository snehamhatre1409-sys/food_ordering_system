import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="K-foodhub | Premium Food Delivery",
    page_icon="🍔",
    layout="wide"
)

# Custom CSS for a "Designer" look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .hero-text {
        font-size: 60px !important;
        font-weight: 700;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-text {
        font-size: 24px;
        text-align: center;
        color: #FAFAFA;
        margin-bottom: 50px;
    }
    .feature-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #4A4A4A;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("<p class='hero-text'>🍜 K-foodhub</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Premium Flavors Delivered to Your Doorstep</p>", unsafe_allow_html=True)

# Add a professional Banner/Logo image
# If you have a local image, use st.image("logo.png")
st.image("https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80", 
         caption="Experience the best cuisine in town", 
         use_column_width=True)

st.divider()

# --- FEATURES SECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class='feature-card'>
            <h3>🚀 Fast Delivery</h3>
            <p>Hot food delivered in under 30 minutes.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='feature-card'>
            <h3>🍕 Fresh Quality</h3>
            <p>Only the finest ingredients from local farms.</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='feature-card'>
            <h3>💳 Easy Payment</h3>
            <p>Secure checkout via UPI, Card, or Cash.</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- CALL TO ACTION ---
st.write("### Ready to satisfy your hunger?")
if st.button("🍽️ Browse Menu Now", use_container_width=True, type="primary"):
    st.switch_page("pages/2_Menu.py")

# Footer

st.markdown("<br><p style='text-align: center; color: gray;'>© 2026 K-foodhub Enterprise. All rights reserved.</p>", unsafe_allow_html=True)
