import streamlit as st
import pandas as pd
from datetime import datetime
from utils import conn

# ✅ Security check
if st.session_state.get('role') != 'admin':
    st.error("🔒 Admin access required!")
    st.stop()

st.title("👨‍💼 Admin: Menu Management")
st.markdown("---")

tab1, tab2 = st.tabs(["➕ Add New Item", "📋 View/Edit Menu"])

# --- TAB 1: ADD ITEM ---
with tab1:
    st.subheader("Add a New Dish to the Database")
    with st.form("add_menu_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            name = st.text_input("Item Name (e.g., Paneer Tikka)")
            price = st.number_input("Price (₹)", min_value=0, step=5)
            category = st.selectbox("Category", ["Veg", "Non-Veg", "Main Course", "Healthy", "Drinks", "Dessert"])
        
        with col_b:
            stock = st.number_input("Initial Stock", min_value=0, value=50)
            available = st.checkbox("Mark as Available", value=True)
            # Default image string as seen in your screenshot
            image_name = st.text_input("Image Filename (optional)", value="none.jpg")

        desc = st.text_area("Description", help="Describe the taste and ingredients")

        if st.form_submit_button("🚀 Add Item to Menu"):
            if name and desc:
                try:
                    c = conn.cursor()
                    c.execute("""INSERT INTO menu 
                                (name, price, description, category, stock, is_available, added_date, image) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                             (name, price, desc, category, stock, 1 if available else 0, 
                              datetime.now().strftime("%Y-%m-%d"), image_name))
                    conn.commit()
                    st.success(f"✅ {name} added successfully!")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Please fill in the Name and Description.")

# --- TAB 2: VIEW/EDIT MENU ---
with tab2:
    try:
        # Refresh data from DB
        menu_df = pd.read_sql("SELECT * FROM menu", conn)
        
        if menu_df.empty:
            st.info("The menu is currently empty. Add items in the first tab!")
        else:
            st.subheader("Current Database Records")
            # Displaying the table just like your screenshot
            st.dataframe(menu_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Quick Inventory Actions")
            
            # Create a clean list for editing
            for idx, row in menu_df.iterrows():
                with st.expander(f"🛠️ Manage: {row['name']} (ID: {row['id']})"):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**Category:** {row['category']} | **Price:** ₹{row['price']}")
                    
                    with col2:
                        if st.button("✏️ Edit Details", key=f"edit_{row['id']}"):
                            st.session_state.edit_item_id = row['id']
                    
                    with col3:
                        if st.button("🟢 +10 Stock", key=f"stock_{row['id']}"):
                            conn.cursor().execute("UPDATE menu SET stock = stock + 10, is_available=1 WHERE id=?", (row['id'],))
                            conn.commit()
                            st.rerun()
                            
                    with col4:
                        if st.button("🔴 OOS", key=f"oos_{row['id']}"):
                            conn.cursor().execute("UPDATE menu SET is_available=0, stock=0 WHERE id=?", (row['id'],))
                            conn.commit()
                            st.rerun()

            # --- DYNAMIC EDIT FORM ---
            if 'edit_item_id' in st.session_state:
                st.markdown("---")
                st.subheader("📝 Edit Item Details")
                edit_id = st.session_state.edit_item_id
                item_data = menu_df[menu_df['id'] == edit_id].iloc[0]
                
                with st.form("edit_form"):
                    enam = st.text_input("Name", value=item_data['name'])
                    eprc = st.number_input("Price", value=int(item_data['price']))
                    estk = st.number_input("Stock", value=int(item_data['stock']))
                    ecat = st.selectbox("Category", ["Veg", "Non-Veg", "Main Course", "Healthy", "Drinks", "Dessert"], 
                                        index=["Veg", "Non-Veg", "Main Course", "Healthy", "Drinks", "Dessert"].index(item_data['category']))
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Save Changes"):
                        conn.cursor().execute("""UPDATE menu SET name=?, price=?, stock=?, category=? WHERE id=?""", 
                                             (enam, eprc, estk, ecat, edit_id))
                        conn.commit()
                        del st.session_state.edit_item_id
                        st.success("Updated!")
                        st.rerun()
                        
                    if c2.form_submit_button("❌ Cancel"):
                        del st.session_state.edit_item_id
                        st.rerun()
    except Exception as e:
        st.error(f"Error loading table: {e}")
