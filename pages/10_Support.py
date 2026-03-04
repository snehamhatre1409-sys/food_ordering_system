import streamlit as st

st.set_page_config(page_title="Support | K-foodhub", page_icon="📞")

# Custom Styling
st.markdown("""
    <style>
    .support-header {
        color: #FF4B4B;
        font-size: 35px;
        font-weight: bold;
    }
    .info-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤝 Help & Support")
st.divider()

tab1, tab2 = st.tabs(["📖 About K-foodhub", "📩 Contact Us"])

# --- TAB 1: ABOUT US ---
with tab1:
    st.markdown("<p class='support-header'>Our Story</p>", unsafe_allow_html=True)
    st.write("""
    Welcome to **K-foodhub**, your premier destination for authentic flavors and healthy living. 
    Founded in 2026, our mission is to bridge the gap between traditional Indian taste and modern 
    nutritional needs.
    
    We believe that food should not only taste good but also make you feel good. That's why 
    every dish on our menu is prepared with locally sourced ingredients and zero artificial 
    preservatives.
    """)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Freshness", "100%")
    col2.metric("Orders Served", "5000+")
    col3.metric("Expert Chefs", "12")

# --- TAB 2: CONTACT US ---
with tab2:
    st.markdown("<p class='support-header'>Get In Touch</p>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("### 📍 Visit Us")
        st.info("**Address:** 123 Foodie Street, Gourmet Nagar, Mumbai, Maharashtra - 400001")
        
        st.write("### 📞 Call Us")
        st.success("**Phone:** +91 98765 43210")
        
        st.write("### 📧 Email")
        st.warning("**Support:** help@kfoodhub.com")

    with col_right:
        st.write("### 💬 Send a Message")
        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            msg = st.text_area("How can we help you?")
            
            if st.form_submit_button("Submit Message"):
                if name and email and msg:
                    st.balloons()
                    st.success(f"Thank you {name}! Our team will contact you within 24 hours.")
                else:
                    st.error("Please fill in all fields.")

st.divider()
st.info("💡 Follow us on Instagram and Twitter **@KFoodHub** for daily healthy tips!")
