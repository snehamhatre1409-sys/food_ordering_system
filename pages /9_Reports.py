import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF  # FIX: Ensure 'fpdf' or 'fpdf2' is installed
from utils import conn
import io

st.set_page_config(page_title="Reports & Downloads", page_icon="📄")

st.title("📄 Reports & Downloads")
st.divider()

# Security Check (Optional but recommended)
if st.session_state.get('role') != 'admin':
    st.error("🔒 Admin access required to view reports.")
    st.stop()

tab1, tab2 = st.tabs(["📊 View Analytics", "📥 Export PDF"])

# --- TAB 1: VIEW REPORTS ---
with tab1:
    report_type = st.selectbox("Select Report Type", 
                               ["Daily Sales", "Top Customers", "Menu Performance"])
    
    try:
        if report_type == "Daily Sales":
            query = """
                SELECT DATE(order_date) as Date, SUM(total) as Total_Sales, COUNT(id) as Order_Count 
                FROM orders 
                WHERE status='delivered' 
                GROUP BY Date ORDER BY Date DESC LIMIT 30
            """
            sales = pd.read_sql(query, conn)
            st.subheader("📅 Last 30 Days Sales")
            st.dataframe(sales, use_container_width=True)
            st.line_chart(sales.set_index('Date')['Total_Sales'])
            
        elif report_type == "Top Customers":
            query = """
                SELECT u.username as Customer, COUNT(o.id) as Total_Orders, SUM(o.total) as Total_Spent 
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                GROUP BY u.id ORDER BY Total_Spent DESC LIMIT 10
            """
            top_cust = pd.read_sql(query, conn)
            st.subheader("🏆 Top 10 Customers")
            st.table(top_cust) # Using table for a clean static look

        elif report_type == "Menu Performance":
            st.info("💡 Tip: This report shows which items are generating the most interest.")
            # Note: This assumes you are storing item names in your 'orders' items JSON
            st.write("Feature coming soon: Item-wise breakdown.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# --- TAB 2: DOWNLOAD PDF ---
with tab2:
    st.subheader("Generate Official Report")
    st.write("Click the button below to generate a PDF of the last 50 delivered orders.")

    if st.button("🚀 Prepare Sales Report"):
        try:
            # 1. Fetch Data
            sales_data = pd.read_sql("SELECT id, total, order_date FROM orders WHERE status='delivered' ORDER BY order_date DESC LIMIT 50", conn)
            
            # 2. Create PDF in Memory
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="FOODPRO ENTERPRISE", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Sales Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            pdf.ln(10) # Line break
            
            # Table Header
            pdf.set_fill_color(200, 220, 255)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(40, 10, "Order ID", 1, 0, 'C', True)
            pdf.cell(80, 10, "Date", 1, 0, 'C', True)
            pdf.cell(60, 10, "Amount (INR)", 1, 1, 'C', True)
            
            # Table Body
            pdf.set_font("Arial", size=10)
            for idx, row in sales_data.iterrows():
                pdf.cell(40, 8, str(row['id']), 1)
                pdf.cell(80, 8, str(row['order_date'])[:16], 1)
                pdf.cell(60, 8, f"Rs. {row['total']}", 1, 1)

            # 3. Output to BytesIO (This is the "clean" way for Streamlit)
            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            st.success("✅ PDF Ready!")
            st.download_button(
                label="⬇️ Download Sales Report",
                data=pdf_output,
                file_name=f"Sales_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF Generation failed: {e}")
