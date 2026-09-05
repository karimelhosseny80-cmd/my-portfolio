import streamlit as st
import pandas as pd
import datetime

# إعداد الصفحة وتناسب شاشات الهواتف
st.set_page_config(page_title="محفظتي", layout="centered", initial_sidebar_state="collapsed")

# تصميم مخصص للموبايل بواجهة عربية نظيفة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    * { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .block-container { padding: 1rem !important; }
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .kpi-box {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        text-align: center;
    }
    .badge-win { color: #16a34a; font-weight: bold; }
    .badge-loss { color: #dc2626; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# بيانات المحفظة
DEFAULT_STOCKS = [
    {"name": "العربية للصناعات الهندسية", "ticker": "EEII", "qty": 24372, "avg": 2.2904, "price": 2.35},
    {"name": "نهر الخير للتنمية", "ticker": "KRDI", "qty": 123690, "avg": 0.4159, "price": 0.449},
    {"name": "القاهرة للإسكان والتعمير", "ticker": "ELKA", "qty": 21990, "avg": 1.7544, "price": 1.87},
    {"name": "سيراميكا ريماس", "ticker": "CERA", "qty": 22100, "avg": 1.3159, "price": 1.50},
    {"name": "المصريين للإسكان", "ticker": "EHDR", "qty": 9793, "avg": 2.6623, "price": 2.88},
    {"name": "العز سيراميك (الجوهرة)", "ticker": "ECAP", "qty": 365, "avg": 34.4619, "price": 33.62},
    {"name": "مصر الوطنية للصلب (عتاقة)", "ticker": "ATQA", "qty": 592, "avg": 12.6712, "price": 12.17},
    {"name": "أموك للزيوت المعدنية", "ticker": "AMOC", "qty": 449, "avg": 7.9226, "price": 13.50},
]

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(DEFAULT_STOCKS)
if "cash" not in st.session_state:
    st.session_state.cash = 0.0
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# حساب الإجماليات
df = st.session_state.portfolio.copy()
total_cost = (df["qty"] * df["avg"]).sum()
total_market = (df["qty"] * df["price"]).sum()
net_pnl = total_market - total_cost
net_return = (net_pnl / total_cost) * 100 if total_cost > 0 else 0

# بطاقة الملخص المالي العلوية
pnl_color = "#4ade80" if net_pnl >= 0 else "#f87171"
st.markdown(f"""
<div class="kpi-box">
    <div style="font-size: 13px; opacity: 0.9;">إجمالي القيمة السوقية</div>
    <div style="font-size: 24px; font-weight: bold; margin: 4px 0;">{total_market:,.2f} ج.م</div>
    <div style="font-size: 14px; color: {pnl_color}; font-weight: bold;">
        صافي الأرباح: {net_pnl:+,.2f} ج.م ({net_return:+.2f}%)
    </div>
    <div style="font-size: 12px; margin-top: 6px; opacity: 0.85;">الكاش المتاح: {st.session_state.cash:,.2f} ج.م</div>
</div>
""", unsafe_allow_html=True)

# أزرار تنقل عريضة في الأعلى للموبايل
tab1, tab2, tab3 = st.tabs(["📊 الأسهم والمحفظة", "📈 التحليل الفني", "💵 المصاريف والكاش"])

# 1. شاشة الأسهم بنظام كروت الموبايل
with tab1:
    for _, row in df.iterrows():
        cost = row["qty"] * row["avg"]
        val = row["qty"] * row["price"]
        pnl = val - cost
        ret = (pnl / cost) * 100
        cls = "badge-win" if pnl >= 0 else "badge-loss"
        
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; font-size: 15px;">{row['name']}</span>
                <span style="background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">{row['ticker']}</span>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;">
            <div style="font-size: 13px; line-height: 1.8;">
                <div>الكمية: <b>{row['qty']:,}</b> سهم</div>
                <div>متوسط الشراء: <b>{row['avg']:.4f}</b> ج.م | السعر الحالي: <b>{row['price']:.2f}</b> ج.م</div>
                <div>القيمة: <b>{val:,.2f}</b> ج.م</div>
                <div class="{cls}">الربح / الخسارة: {pnl:+,.2f} ج.م ({ret:+.2f}%)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. شاشة التحليل الفني
with tab2:
    st.caption("مستويات الدعم والمقاومة المقترحة:")
    for _, row in df.iterrows():
        p = row["price"]
        sup = round(p * 0.95, 2)
        res = round(p * 1.05, 2)
        sl = round(p * 0.93, 2)
        trend = "صاعد 🟢" if p >= row["avg"] else "تصحيحي 🔴"
        
        st.markdown(f"""
        <div class="card">
            <div style="font-weight: bold; color: #1e3a8a;">{row['name']} ({row['ticker']})</div>
            <div style="font-size: 13px; margin-top: 6px;">
                <div>الاتجاه: <b>{trend}</b></div>
                <div>الدعم الأول: <b style="color: #16a34a;">{sup} ج.م</b></div>
                <div>المقاومة الأولى: <b style="color: #ea580c;">{res} ج.م</b></div>
                <div>وقف الخسارة: <b style="color: #dc2626;">{sl} ج.م</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. شاشة المصاريف والكاش
with tab3:
    st.write("### تسجيل حركة نقدية سريعة")
    with st.form("quick_cash"):
        action = st.selectbox("نوع الحركة:", ["مصروف شخصي", "إيداع بالمحفظة", "سحب كاش من المحفظة"])
        amt = st.number_input("المبلغ (ج.م):", min_value=1.0, step=50.0)
        desc = st.text_input("البيان / التصنيف (مثال: بنزين، خروج، أرباح):")
        if st.form_submit_button("حفظ المعاملة", use_container_width=True):
            if action == "إيداع بالمحفظة":
                st.session_state.cash += amt
            elif action == "سحب كاش من المحفظة":
                st.session_state.cash -= amt
            st.session_state.expenses.append({"التاريخ": str(datetime.date.today()), "النوع": action, "المبلغ": amt, "البيان": desc})
            st.success("تم الحفظ وتحديث الرصيد!")
            st.rerun()

    if st.session_state.expenses:
        st.write("---")
        st.write("### آخر المعاملات:")
        for exp in reversed(st.session_state.expenses[-5:]):
            st.caption(f"{exp['التاريخ']} | {exp['النوع']}: {exp['المبلغ']} ج.م ({exp['البيان']})")
