import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="INDUSTRIAL STOCK & ACCOUNTING SYSTEM",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM INDUSTRIAL STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-title {
        color: #F59E0B;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border-bottom: 2px solid #334155;
        padding-bottom: 10px;
        margin-bottom: 25px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
    }
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-card:hover {
        border-color: #F59E0B;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value-gold {
        font-size: 1.75rem;
        color: #F59E0B;
        font-weight: 700;
        font-family: 'Courier New', Courier, monospace;
    }
    .metric-value-green {
        font-size: 1.8rem;
        color: #10B981;
        font-weight: 700;
        font-family: 'Courier New', Courier, monospace;
    }
    .metric-value-red {
        font-size: 1.8rem;
        color: #EF4444;
        font-weight: 700;
        font-family: 'Courier New', Courier, monospace;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E293B;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 6px;
        color: #94A3B8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #F59E0B !important;
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    .stButton > button {
        background-color: #F59E0B;
        color: #0F172A;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        width: 100%;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background-color: #D97706;
        color: #FFFFFF;
    }
    .login-box {
        background-color: #1E293B;
        padding: 40px;
        border-radius: 12px;
        border: 2px solid #F59E0B;
        max-width: 450px;
        margin: 80px auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    try:
        conn = sqlite3.connect('stock_management.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                     (item_name TEXT PRIMARY KEY, quantity_tons REAL DEFAULT 0.0)''')
        c.execute("INSERT OR IGNORE INTO inventory VALUES ('เหล็กหล่อ', 0.0)")
        c.execute("INSERT OR IGNORE INTO inventory VALUES ('เหล็กเหนียว', 0.0)")
        c.execute("INSERT OR IGNORE INTO inventory VALUES ('แม่พิมพ์', 0.0)")
        
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        type TEXT,
                        company_name TEXT,
                        item_name TEXT,
                        quantity_tons REAL,
                        price REAL,
                        travel_cost REAL,
                        payment_status TEXT
                    )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS deleted_transactions (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        type TEXT,
                        company_name TEXT,
                        item_name TEXT,
                        quantity_tons REAL,
                        price REAL,
                        travel_cost REAL,
                        payment_status TEXT,
                        deleted_at TEXT
                    )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS companies (name TEXT PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS balance (id INTEGER PRIMARY KEY, amount REAL)''')
        c.execute("INSERT OR IGNORE INTO balance VALUES (1, 0.0)")
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database Initialization Error: {e}")

# --- HELPER FUNCTIONS ---
def get_inventory():
    conn = sqlite3.connect('stock_management.db')
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def get_balance():
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    c.execute("SELECT amount FROM balance WHERE id = 1")
    row = c.fetchone()
    bal = row[0] if row else 0.0
    conn.close()
    return bal

def update_balance(new_amount):
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    c.execute("UPDATE balance SET amount = ? WHERE id = 1", (new_amount,))
    conn.commit()
    conn.close()

def get_companies():
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    c.execute("SELECT name FROM companies ORDER BY name ASC")
    companies = [row[0] for row in c.fetchall()]
    conn.close()
    return companies

def add_company(name):
    if name and name.strip():
        conn = sqlite3.connect('stock_management.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO companies VALUES (?)", (name.strip(),))
        conn.commit()
        conn.close()

def delete_company(name):
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    c.execute("DELETE FROM companies WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect('stock_management.db')
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC, id DESC", conn)
    conn.close()
    return df

def get_deleted_transactions():
    conn = sqlite3.connect('stock_management.db')
    df = pd.read_sql_query("SELECT * FROM deleted_transactions ORDER BY deleted_at DESC", conn)
    conn.close()
    return df

def delete_transaction(trans_id):
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    
    c.execute("SELECT id, timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status FROM transactions WHERE id = ?", (trans_id,))
    row = c.fetchone()
    
    if row:
        t_id, timestamp, t_type, company_name, item_name, qty_tons, price, travel_cost, payment_status = row
        
        if t_type == "รับซื้อ":
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons - ? WHERE item_name = ?", (qty_tons, item_name))
            c.execute("UPDATE balance SET amount = amount + ? WHERE id = 1", (price,))
            
        elif t_type == "ขาย":
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons + ? WHERE item_name = ?", (qty_tons, item_name))
            
            refund_amount = -travel_cost
            if payment_status == "ชำระแล้ว":
                refund_amount += price
            
            c.execute("UPDATE balance SET amount = amount - ? WHERE id = 1", (refund_amount,))
        
        deleted_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""INSERT INTO deleted_transactions 
                     (id, timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status, deleted_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (t_id, timestamp, t_type, company_name, item_name, qty_tons, price, travel_cost, payment_status, deleted_now))
            
        c.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def restore_transaction(trans_id):
    conn = sqlite3.connect('stock_management.db')
    c = conn.cursor()
    
    c.execute("SELECT id, timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status FROM deleted_transactions WHERE id = ?", (trans_id,))
    row = c.fetchone()
    
    if row:
        t_id, timestamp, t_type, company_name, item_name, qty_tons, price, travel_cost, payment_status = row
        
        if t_type == "รับซื้อ":
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons + ? WHERE item_name = ?", (qty_tons, item_name))
            c.execute("UPDATE balance SET amount = amount - ? WHERE id = 1", (price,))
            
        elif t_type == "ขาย":
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons - ? WHERE item_name = ?", (qty_tons, item_name))
            
            net_income = -travel_cost
            if payment_status == "ชำระแล้ว":
                net_income += price
            
            c.execute("UPDATE balance SET amount = amount + ? WHERE id = 1", (net_income,))
        
        c.execute("""INSERT INTO transactions 
                     (id, timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (t_id, timestamp, t_type, company_name, item_name, qty_tons, price, travel_cost, payment_status))
            
        c.execute("DELETE FROM deleted_transactions WHERE id = ?", (trans_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

init_db()

# --- AUTHENTICATION SCREEN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("""
        <div class="login-box">
            <h2 style="text-align: center; color: #F59E0B; margin-bottom: 5px;">🏭 SECURE SYSTEM</h2>
            <p style="text-align: center; color: #94A3B8; font-size: 0.9rem; margin-bottom: 25px;">ระบบบริหารจัดการคลังสินค้าและบัญชีส่วนบุคคล</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        password = st.text_input("PASSWORD / รหัสผ่านเข้าใช้งาน", type="password")
        submit_pass = st.form_submit_button("LOGIN TO SYSTEM")
        if submit_pass:
            if password == "wipaporn152628":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Access Denied: รหัสผ่านไม่ถูกต้อง")
    st.stop()

# --- SIDEBAR: เพิ่ม/ปรับเงินก่อนใช้งานระบบ ---
with st.sidebar:
    st.markdown("### 💰 จัดการเงินทุน")
    current_b = get_balance()
    
    if current_b < 0:
        st.error(f"ยอดเงินสดติดลบ: **฿ {current_b:,.2f}**")
    else:
        st.write(f"ยอดเงินสดในบัญชีปัจจุบัน: **฿ {current_b:,.2f}**")
    
    st.markdown("---")
    st.markdown("#### ⚙️ เพิ่ม / ปรับเงินสดเริ่มต้น")
    
    new_bal_input = st.number_input(
        "ระบุยอดเงินสด (บาท)", 
        value=float(current_b), 
        step=1000.0, 
        format="%.2f"
    )
    
    if st.button("💵 บันทึกยอดเงินหลัก"):
        update_balance(new_bal_input)
        st.success("✅ อัปเดตยอดเงินสำเร็จ")
        st.rerun()

# --- MAIN DASHBOARD INTERFACE ---
st.markdown("<h1 class='main-title'>⚡ STEEL PLANT & STOCK CONTROL CENTER</h1>", unsafe_allow_html=True)

# --- DASHBOARD SUMMARY METRICS ---
current_bal = get_balance()
inv_df = get_inventory().set_index('item_name')

cast_iron = inv_df.loc['เหล็กหล่อ', 'quantity_tons'] if 'เหล็กหล่อ' in inv_df.index else 0.0
ductile_iron = inv_df.loc['เหล็กเหนียว', 'quantity_tons'] if 'เหล็กเหนียว' in inv_df.index else 0.0
molds = inv_df.loc['แม่พิมพ์', 'quantity_tons'] if 'แม่พิมพ์' in inv_df.index else 0.0

col_b, col_s1, col_s2, col_s3 = st.columns(4)

bal_class = "metric-value-green" if current_bal >= 0 else "metric-value-red"

with col_b:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {'#10B981' if current_bal >= 0 else '#EF4444'};">
            <div class="metric-label">💵 เงินคงเหลือสุทธิ (NET BALANCE)</div>
            <div class="{bal_class}">฿ {current_bal:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_s1:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #F59E0B;">
            <div class="metric-label">⚙️ สต็อกเหล็กหล่อ (CAST IRON)</div>
            <div class="metric-value-gold">{cast_iron:.3f} <span style="font-size:1rem;">ตัน</span></div>
        </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #F59E0B;">
            <div class="metric-label">🔩 สต็อกเหล็กเหนียว (DUCTILE IRON)</div>
            <div class="metric-value-gold">{ductile_iron:.3f} <span style="font-size:1rem;">ตัน</span></div>
        </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #F59E0B;">
            <div class="metric-label">🧱 สต็อกแม่พิมพ์ (MOLDS)</div>
            <div class="metric-value-gold">{molds:.3f} <span style="font-size:1rem;">ตัน</span></div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS SYSTEM (กราฟกำไรอยู่ก่อนแท็บถังขยะ) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🛒 บันทึกการรับซื้อ (PURCHASE)", 
    "🚚 บันทึกการขาย (SALES)", 
    "🏷️ เช็คค้างจ่าย (UNPAID CHEQUES)", 
    "📜 ประวัติบัญชี (TRANSACTION LOGS)",
    "🏢 จัดการคู่ค้า (COMPANIES)",
    "📊 สรุปกำไร/ขาดทุนรายเดือน (PROFIT ANALYSIS)",
    "🗑️ ถังขยะ (RECYCLE BIN)"
])

# --- TAB 1: BUY ---
with tab1:
    st.markdown("### 📥 แบบฟอร์มบันทึกการรับซื้อสินค้าเข้าคลัง")
    companies = get_companies()
    
    c_type, c_input = st.columns([1, 2])
    with c_type:
        company_option = st.radio("ตัวเลือกบริษัท", ["เลือกรายชื่อเดิม", "เพิ่มบริษัทใหม่"], key="b_opt")
    with c_input:
        if company_option == "เลือกรายชื่อเดิม" and companies:
            company_name = st.selectbox("ชื่อบริษัทผู้ขาย", companies, key="b_sel")
        else:
            company_name = st.text_input("ระบุชื่อบริษัทผู้ขายใหม่", key="b_new")

    st.markdown("---")
    col_i, col_kg, col_rate = st.columns(3)
    item_type = col_i.selectbox("ชนิดวัตถุดิบ", ["เหล็กหล่อ", "เหล็กเหนียว", "แม่พิมพ์"], key="b_item")
    
    qty_kg = col_kg.number_input("จำนวน (หน่วย: กิโลกรัม)", min_value=0.0, step=1.0, format="%.2f", key="b_kg")
    price_per_kg = col_rate.number_input("ราคาซื้อต่อกิโลกรัม (บาท/กก.)", min_value=0.0, step=0.10, format="%.2f", key="b_rate")
    
    qty_tons = qty_kg / 1000.0
    total_price = qty_kg * price_per_kg
    
    st.info(f"📊 **คำนวณอัตโนมัติ**: ปริมาณน้ำหนัก = **{qty_tons:.3f} ตัน** ({qty_kg:,.2f} กก.) | ราคารวมซื้อ = **฿ {total_price:,.2f} บาท**")
    
    if st.button("💾 บันทึกรายการรับซื้อ (RECORD PURCHASE)"):
        if not company_name:
            st.error("❌ กรุณาระบุชื่อบริษัทคู่ค้า")
        elif qty_kg <= 0 or price_per_kg <= 0:
            st.error("❌ กรุณากรอกจำนวนกิโลกรัมและราคาต่อกิโลกรัมให้ถูกต้อง")
        else:
            add_company(company_name)
            conn = sqlite3.connect('stock_management.db')
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO transactions (timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status) VALUES (?, 'รับซื้อ', ?, ?, ?, ?, 0.0, 'ชำระแล้ว')", 
                      (now, company_name, item_type, qty_tons, total_price))
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons + ? WHERE item_name = ?", (qty_tons, item_type))
            c.execute("UPDATE balance SET amount = amount - ? WHERE id = 1", (total_price,))
            conn.commit()
            conn.close()
            st.success("✅ บันทึกรายการรับซื้อเรียบร้อย")
            st.rerun()

# --- TAB 2: SELL ---
with tab2:
    st.markdown("### 📤 แบบฟอร์มบันทึกการขายสินค้าออก")
    companies = get_companies()
    
    cs_type, cs_input = st.columns([1, 2])
    with cs_type:
        company_option_sell = st.radio("ตัวเลือกบริษัท", ["เลือกรายชื่อเดิม", "เพิ่มบริษัทใหม่"], key="s_opt")
    with cs_input:
        if company_option_sell == "เลือกรายชื่อเดิม" and companies:
            company_name_sell = st.selectbox("ชื่อบริษัทผู้ซื้อ", companies, key="s_sel")
        else:
            company_name_sell = st.text_input("ระบุชื่อบริษัทผู้ซื้อใหม่", key="s_new")

    st.markdown("---")
    col_si, col_skg, col_srate = st.columns(3)
    item_type_sell = col_si.selectbox("ชนิดวัตถุดิบ", ["เหล็กหล่อ", "เหล็กเหนียว", "แม่พิมพ์"], key="s_item")
    
    qty_kg_sell = col_skg.number_input("จำนวนขาย (หน่วย: กิโลกรัม)", min_value=0.0, step=1.0, format="%.2f", key="s_kg")
    price_per_kg_sell = col_srate.number_input("ราคาขายต่อกิโลกรัม (บาท/กก.)", min_value=0.0, step=0.10, format="%.2f", key="s_rate")
    
    qty_tons_sell = qty_kg_sell / 1000.0
    total_price_sell = qty_kg_sell * price_per_kg_sell

    st.info(f"📊 **คำนวณอัตโนมัติ**: ปริมาณน้ำหนัก = **{qty_tons_sell:.3f} ตัน** ({qty_kg_sell:,.2f} กก.) | ราคารวมขาย = **฿ {total_price_sell:,.2f} บาท**")

    col_st, col_spay = st.columns(2)
    travel_cost = col_st.number_input("ค่าเดินทาง / เบี้ยเลี้ยงคนขับรถ (บาท)", min_value=0.00, step=10.00, format="%.2f", key="s_travel")
    payment_status = col_spay.selectbox("สถานะชำระเงิน", ["ชำระเรียบร้อย (เงินสด/โอน)", "ยังไม่จ่าย (จ่ายเป็นเช็ค)"], key="s_pay")
    
    if st.button("💾 บันทึกรายการขาย (RECORD SALES)"):
        current_stock = inv_df.loc[item_type_sell, 'quantity_tons'] if item_type_sell in inv_df.index else 0.0
        if not company_name_sell:
            st.error("❌ กรุณาระบุชื่อบริษัทคู่ค้า")
        elif qty_kg_sell <= 0 or price_per_kg_sell <= 0:
            st.error("❌ กรุณากรอกจำนวนกิโลกรัมและราคาขายต่อกิโลกรัมให้ถูกต้อง")
        elif qty_tons_sell > current_stock:
            st.error(f"❌ สินค้าในคลังไม่พอขาย! (คงเหลือเพียง {current_stock:.3f} ตัน / {current_stock*1000:,.0f} กก.)")
        else:
            add_company(company_name_sell)
            conn = sqlite3.connect('stock_management.db')
            c = conn.cursor()
            status_text = "ชำระแล้ว" if "ชำระเรียบร้อย" in payment_status else "จ่ายเป็นเช็ค (ยังไม่จ่าย)"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute("INSERT INTO transactions (timestamp, type, company_name, item_name, quantity_tons, price, travel_cost, payment_status) VALUES (?, 'ขาย', ?, ?, ?, ?, ?, ?)",
                      (now, company_name_sell, item_type_sell, qty_tons_sell, total_price_sell, travel_cost, status_text))
            c.execute("UPDATE inventory SET quantity_tons = quantity_tons - ? WHERE item_name = ?", (qty_tons_sell, item_type_sell))
            
            net_income = -travel_cost
            if status_text == "ชำระแล้ว":
                net_income += total_price_sell
            c.execute("UPDATE balance SET amount = amount + ? WHERE id = 1", (net_income,))
            
            conn.commit()
            conn.close()
            st.success("✅ บันทึกรายการขายเรียบร้อย")
            st.rerun()

# --- TAB 3: UNPAID CHEQUES ---
with tab3:
    st.markdown("### 🏷️ รายการค้างชำระ (ลูกหนี้ / เช็ครอเรียกเก็บ)")
    conn = sqlite3.connect('stock_management.db')
    unpaid_df = pd.read_sql_query("SELECT id AS 'ID', timestamp AS 'วันที่/เวลา', company_name AS 'บริษัทผู้ซื้อ', item_name AS 'สินค้า', quantity_tons AS 'ตัน', price AS 'ยอดเงิน (บาท)', travel_cost AS 'ค่าเดินทาง' FROM transactions WHERE payment_status = 'จ่ายเป็นเช็ค (ยังไม่จ่าย)'", conn)
    conn.close()
    
    if unpaid_df.empty:
        st.info("👍 ไม่มีรายการเช็คค้างจ่ายในระบบ")
    else:
        st.dataframe(unpaid_df, use_container_width=True)
        st.markdown("---")
        
        c_sel, c_act = st.columns([2, 1])
        with c_sel:
            selected_id = st.selectbox("เลือก ID รายการที่ขึ้นเงินเช็คสำเร็จ", unpaid_df['ID'].tolist())
        with c_act:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("✅ มาร์กเป็นชำระแล้ว"):
                row = unpaid_df[unpaid_df['ID'] == selected_id].iloc[0]
                amount_to_add = row['ยอดเงิน (บาท)']
                
                conn = sqlite3.connect('stock_management.db')
                c = conn.cursor()
                c.execute("UPDATE transactions SET payment_status = 'ชำระแล้ว' WHERE id = ?", (selected_id,))
                c.execute("UPDATE balance SET amount = amount + ? WHERE id = 1", (amount_to_add,))
                conn.commit()
                conn.close()
                st.success(f"✅ อัปเดตรายการ ID {selected_id} เรียบร้อย!")
                st.rerun()

# --- TAB 4: AUDIT LOGS & DELETE ---
with tab4:
    st.markdown("### 📜 ประวัติการทำรายการทั้งหมด (TRANSACTION LOGS)")
    history_df = get_transactions()
    
    if not history_df.empty:
        disp_df = history_df.copy()
        disp_df.columns = ['ID', 'วันที่/เวลา', 'ประเภท', 'บริษัทคู่ค้า', 'รายการ', 'ปริมาณ (ตัน)', 'มูลค่า (บาท)', 'ค่าเดินทาง (บาท)', 'สถานะชำระเงิน']
        st.dataframe(disp_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🗑️ ลบประวัติรายการ / ย้ายไปถังขยะ (ระบบจะคืนค่าเงินและสต็อกให้อัตโนมัติ)")
        
        del_col1, del_col2 = st.columns([2, 1])
        with del_col1:
            del_id = st.selectbox("เลือก ID รายการที่ต้องการลบ", history_df['id'].tolist(), key="del_box")
            confirm_del_trans = st.checkbox("⚠️ ยืนยันว่าต้องการลบรายการนี้ลงถังขยะจริง", key="chk_del_trans")
        with del_col2:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("❌ ยืนยันย้ายลงถังขยะ"):
                if confirm_del_trans:
                    if delete_transaction(del_id):
                        st.success(f"🗑️ ย้ายรายการ ID {del_id} ไปไว้ในถังขยะเรียบร้อย")
                        st.rerun()
                    else:
                        st.error("❌ ไม่สามารถดำเนินการได้")
                else:
                    st.warning("⚠️ กรุณากดติ๊กถูกในช่องยืนยันก่อนกดปุ่มลบ")
    else:
        st.info("ยังไม่มีประวัติการทำรายการ")

# --- TAB 5: MANAGE COMPANIES ---
with tab5:
    st.markdown("### 🏢 จัดการรายชื่อบริษัทคู่ค้า")
    company_list = get_companies()
    
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.markdown("#### ➕ เพิ่มรายชื่อบริษัท")
        new_comp_name = st.text_input("ระบุชื่อบริษัทใหม่", key="manual_add_comp")
        if st.button("➕ บันทึกบริษัทใหม่"):
            if new_comp_name.strip():
                add_company(new_comp_name)
                st.success(f"✅ เพิ่มบริษัท '{new_comp_name.strip()}' เรียบร้อย")
                st.rerun()
            else:
                st.error("❌ กรุณากรอกชื่อบริษัท")
                
    with col_del:
        st.markdown("#### 🗑️ ลบรายชื่อบริษัท")
        if company_list:
            comp_to_del = st.selectbox("เลือกบริษัทที่ต้องการลบ", company_list, key="manual_del_comp")
            confirm_del_comp = st.checkbox("⚠️ ยืนยันลบรายชื่อบริษัทนี้", key="chk_del_comp")
            if st.button("❌ ยืนยันลบรายชื่อบริษัทนี้"):
                if confirm_del_comp:
                    delete_company(comp_to_del)
                    st.success(f"🗑️ ลบบริษัท '{comp_to_del}' ออกจากระบบเรียบร้อย")
                    st.rerun()
                else:
                    st.warning("⚠️ กรุณากดติ๊กถูกในช่องยืนยันก่อนกดปุ่มลบ")
        else:
            st.info("ยังไม่มีรายชื่อบริษัทในระบบ")

    st.markdown("---")
    st.markdown("#### 📋 รายชื่อบริษัททั้งหมดในระบบ")
    if company_list:
        df_comp = pd.DataFrame(company_list, columns=["รายชื่อบริษัท"])
        df_comp.index = df_comp.index + 1
        st.dataframe(df_comp, use_container_width=True)
    else:
        st.write("ไม่มีข้อมูลบริษัท")

# --- TAB 6: PROFIT ANALYSIS & GRAPH (ตั้งอยู่ก่อนถังขยะ) ---
with tab6:
    st.markdown("### 📊 สรุปกำไร/ขาดทุนรายเดือน (PROFIT & LOSS ANALYSIS)")
    
    df_raw = get_transactions()
    
    if not df_raw.empty:
        df_raw['datetime'] = pd.to_datetime(df_raw['timestamp'])
        df_raw['Year'] = df_raw['datetime'].dt.year
        df_raw['Month'] = df_raw['datetime'].dt.month
        df_raw['YearMonth'] = df_raw['datetime'].dt.strftime('%Y-%m')
        
        # --- ตัวเลือก Filter เลือกปี / เลือกเดือน ---
        filter_col1, filter_col2 = st.columns(2)
        
        available_years = sorted(df_raw['Year'].unique().tolist(), reverse=True)
        selected_year = filter_col1.selectbox("📅 เลือกปีที่ต้องการดูข้อมูล", available_years)
        
        months_in_year = sorted(df_raw[df_raw['Year'] == selected_year]['Month'].unique().tolist())
        month_options = ["ทุกเดือนในปีนี้"] + [f"เดือน {m:02d}" for m in months_in_year]
        selected_month_str = filter_col2.selectbox("📆 เลือกเดือน", month_options)
        
        # --- กรองข้อมูลตามที่เลือก ---
        df_filtered = df_raw[df_raw['Year'] == selected_year].copy()
        
        if selected_month_str != "ทุกเดือนในปีนี้":
            selected_m = int(selected_month_str.split(" ")[1])
            df_filtered = df_filtered[df_filtered['Month'] == selected_m]
        
        # --- คำนวณรายรับ/รายจ่าย/กำไร ---
        # รายรับ = ยอดขายสินค้า
        # รายจ่าย = ยอดซื้อสินค้า + ค่าเดินทาง
        df_filtered['Revenue'] = df_filtered.apply(lambda r: r['price'] if r['type'] == 'ขาย' else 0.0, axis=1)
        df_filtered['Expense'] = df_filtered.apply(lambda r: r['price'] + r['travel_cost'] if r['type'] == 'รับซื้อ' else r['travel_cost'], axis=1)
        
        # จัดกลุ่มตาม YearMonth
        summary_df = df_filtered.groupby('YearMonth').agg(
            รายรับรวม=('Revenue', 'sum'),
            รายจ่ายรวม=('Expense', 'sum')
        ).reset_index()
        
        summary_df['กำไรสุทธิ'] = summary_df['รายรับรวม'] - summary_df['รายจ่ายรวม']
        
        st.markdown("---")
        
        # แสดงสรุปตัวเลข
        total_rev = summary_df['รายรับรวม'].sum()
        total_exp = summary_df['รายจ่ายรวม'].sum()
        total_profit = summary_df['กำไรสุทธิ'].sum()
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("📈 รายรับรวมทั้งหมด", f"฿ {total_rev:,.2f}")
        m_col2.metric("📉 รายจ่ายรวมทั้งหมด", f"฿ {total_exp:,.2f}")
        profit_color = "normal" if total_profit >= 0 else "inverse"
        m_col3.metric("💰 กำไรสุทธิรวม", f"฿ {total_profit:,.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 กราฟแท่งเปรียบเทียบ รายรับ, รายจ่าย และ กำไรสุทธิ (รายเดือน)")
        
        # แสดงกราฟแท่ง
        chart_data = summary_df.set_index('YearMonth')[['รายรับรวม', 'รายจ่ายรวม', 'กำไรสุทธิ']]
        st.bar_chart(chart_data)
        
        st.markdown("---")
        st.markdown("#### 📋 ตารางสรุปยอดกำไรสุทธิ")
        st.dataframe(summary_df.style.format({
            'รายรับรวม': '฿ {:,.2f}',
            'รายจ่ายรวม': '฿ {:,.2f}',
            'กำไรสุทธิ': '฿ {:,.2f}'
        }), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🗑️ ลบประวัติกำไร / ลบรายการที่ไม่ถูกต้อง")
        st.caption("หมายเหตุ: การลบรายการที่นี่ คือการย้ายรายการธุรกรรมไปยังถังขยะ ซึ่งจะส่งผลให้ตัวเลขกำไรในเดือนนั้นคำนวณใหม่โดยอัตโนมัติ")
        
        del_p_col1, del_p_col2 = st.columns([2, 1])
        with del_p_col1:
            profit_del_id = st.selectbox("เลือก ID รายการธุรกรรมที่ต้องการลบออก", df_filtered['id'].tolist(), key="profit_del_id")
            confirm_del_profit = st.checkbox("⚠️ ยืนยันต้องการลบรายการนี้เพื่อปรับปรุงประวัติกำไร", key="chk_del_profit")
        with del_p_col2:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ ยืนยันลบรายการนี้ลงถังขยะ"):
                if confirm_del_profit:
                    if delete_transaction(profit_del_id):
                        st.success(f"🗑️ ลบรายการ ID {profit_del_id} และคำนวณกำไรใหม่เรียบร้อยแล้ว!")
                        st.rerun()
                    else:
                        st.error("❌ ไม่สามารถลบรายการได้")
                else:
                    st.warning("⚠️ กรุณากดติ๊กถูกในช่องยืนยันก่อนกดปุ่มลบ")
    else:
        st.info("ยังไม่มีข้อมูลรายการซื้อขายเพียงพอสำหรับการวิเคราะห์กำไร")

# --- TAB 7: RECYCLE BIN ---
with tab7:
    st.markdown("### 🗑️ ถังขยะและกู้คืนรายการ (RECYCLE BIN)")
    deleted_df = get_deleted_transactions()
    
    if not deleted_df.empty:
        disp_del_df = deleted_df.copy()
        disp_del_df.columns = ['ID', 'วันที่/เวลาเดิม', 'ประเภท', 'บริษัทคู่ค้า', 'รายการ', 'ปริมาณ (ตัน)', 'มูลค่า (บาท)', 'ค่าเดินทาง (บาท)', 'สถานะชำระเงิน', 'วันที่ลบรายการ']
        st.dataframe(disp_del_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### ♻️ กู้คืนรายการ (แทรกกลับไปตามลำดับเวลาซื้อ/ขายเดิมอัตโนมัติ)")
        
        res_col1, res_col2 = st.columns([2, 1])
        with res_col1:
            restore_id = st.selectbox("เลือก ID รายการที่ต้องการกู้คืน", deleted_df['id'].tolist(), key="res_box")
            confirm_restore = st.checkbox("⚠️ ยืนยันการกู้คืนรายการนี้กลับสู่ระบบ", key="chk_restore")
        with res_col2:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("♻️ ยืนยันกู้คืนรายการนี้"):
                if confirm_restore:
                    if restore_transaction(restore_id):
                        st.success(f"✅ กู้คืนรายการ ID {restore_id} เข้าสู่ประวัติบัญชีตามลำดับเวลาเดิมเรียบร้อยแล้ว!")
                        st.rerun()
                    else:
                        st.error("❌ ไม่สามารถกู้คืนรายการได้")
                else:
                    st.warning("⚠️ กรุณากดติ๊กถูกในช่องยืนยันก่อนกดปุ่มกู้คืน")
    else:
        st.info("👍 ถังขยะว่างเปล่า (ไม่มีรายการที่ถูกลบ)")
