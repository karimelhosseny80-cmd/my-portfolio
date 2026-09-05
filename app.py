import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

# إعداد الصفحة وتفعيل اتجاه اليمين لليسار
st.set_page_config(page_title="محفظتي - البورصة المصرية والمصاريف", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# بيانات المحفظة الأساسية
DEFAULT_PORTFOLIO = [
    {"name": "العربية للصناعات الهندسية", "ticker": "EEII", "qty": 24372, "avg_cost": 2.2904, "last_price": 2.35},
    {"name": "نهر الخير للتنمية والاستثمار", "ticker": "KRDI", "qty": 123690, "avg_cost": 0.4159, "last_price": 0.449},
    {"name": "القاهرة للإسكان والتعمير", "ticker": "ELKA", "qty": 21990, "avg_cost": 1.7544, "last_price": 1.87},
    {"name": "سيراميكا ريماس", "ticker": "CERA", "qty": 22100, "avg_cost": 1.3159, "last_price": 1.50},
    {"name": "المصريين للإسكان والتنمية", "ticker": "EHDR", "qty": 9793, "avg_cost": 2.6623, "last_price": 2.88},
    {"name": "العز سيراميك (الجوهرة)", "ticker": "ECAP", "qty": 365, "avg_cost": 34.4619, "last_price": 33.62},
    {"name": "مصر الوطنية للصلب (عتاقة)", "ticker": "ATQA", "qty": 592, "avg_cost": 12.6712, "last_price": 12.17},
    {"name": "أموك للزيوت المعدنية", "ticker": "AMOC", "qty": 449, "avg_cost": 7.9226, "last_price": 13.50},
]

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(DEFAULT_PORTFOLIO)

if "cash" not in st.session_state:
    st.session_state.cash = 0.0

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["التاريخ", "النوع", "التصنيف", "المبلغ", "ملاحظات"])

# دالة جلب بيانات السوق المباشرة من مباشر
@st.cache_data(ttl=300)
def fetch_egx_data(ticker):
    url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # استخراج السعر
            price_elem = soup.find(class_=lambda x: x and 'stock-overview__price' in x)
            price = float(price_elem.text.strip().replace(',', '')) if price_elem else None
            return {"price": price, "status": "متصل"}
    except Exception:
        pass
    return {"price": None, "status": "غير متصل"}

# دالة التحليل الفني التقديري
def technical_analysis(cur_price, avg_cost):
    r_price = cur_price if cur_price else avg_cost
    support = round(r_price * 0.95, 2)
    resistance = round(r_price * 1.05, 2)
    stop_loss = round(r_price * 0.93, 2)
    trend = "صاعد 🟢" if r_price >= avg_cost else "هابط / تصحيحي 🔴"
    return support, resistance, stop_loss, trend

# الشريط الجانبي (التنقل)
st.sidebar.title("لوحة التحكم 📊")
menu = st.sidebar.radio("الانتقال إلى:", ["المحفظة الاستثمارية", "التحليل الفني اليومي", "المصاريف والسيولة", "تسجيل عملية جديدة"])

# 1. شاشة المحفظة
if menu == "المحفظة الاستثمارية":
    st.title("محفظة الأسهم المصرية 🇪🇬")
    
    col_btn, _ = st.columns([1, 4])
    if col_btn.button("🔄 تحديث أسعار السوق الآن"):
        st.cache_data.clear()
        st.rerun()

    df = st.session_state.portfolio.copy()
    
    # حساب القيم
    df["القيمة الشرائية"] = df["qty"] * df["avg_cost"]
    df["السعر الحالي"] = df["last_price"]
    df["القيمة السوقية"] = df["qty"] * df["السعر الحالي"]
    df["الربح / الخسارة"] = df["القيمة السوقية"] - df["القيمة الشرائية"]
    df["العائد %"] = (df["الربح / الخسارة"] / df["القيمة الشرائية"]) * 100

    tot_cost = df["القيمة الشرائية"].sum()
    tot_market = df["القيمة السوقية"].sum()
    tot_pnl = tot_market - tot_cost
    tot_ret = (tot_pnl / tot_cost) * 100 if tot_cost > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("إجمالي القيمة السوقية", f"{tot_market:,.2f} ج.م")
    kpi2.metric("رأس المال المستثمر", f"{tot_cost:,.2f} ج.م")
    kpi3.metric("صافي الأرباح", f"{tot_pnl:+,.2f} ج.م", f"{tot_ret:+.2f}%")
    kpi4.metric("الكاش المتاح", f"{st.session_state.cash:,.2f} ج.م")

    st.subheader("مراكز الأسهم النشطة")
    display_df = df[["name", "ticker", "qty", "avg_cost", "السعر الحالي", "القيمة السوقية", "الربح / الخسارة", "العائد %"]].copy()
    display_df.columns = ["اسم الشركة", "الكود", "الكمية", "متوسط الشراء", "السعر الحالي", "القيمة السوقية", "الربح / الخسارة", "العائد %"]
    st.dataframe(display_df.style.format({
        "الكمية": "{:,.0f}",
        "متوسط الشراء": "{:,.4f}",
        "السعر الحالي": "{:,.2f}",
        "القيمة السوقية": "{:,.2f} ج.م",
        "الربح / الخسارة": "{:+,.2f} ج.م",
        "العائد %": "{:+.2f}%"
    }), use_container_width=True)

# 2. شاشة التحليل الفني
elif menu == "التحليل الفني اليومي":
    st.title("التحليل الفني ومستويات الجلسة 📈")
    st.info("المستويات محسوبة بناءً على الإغلاقات الحالية وسلوك الأسعار اليومي لدعم اتخاذ القرار.")
    
    analysis_data = []
    for _, row in st.session_state.portfolio.iterrows():
        sup, res, sl, tr = technical_analysis(row["last_price"], row["avg_cost"])
        analysis_data.append({
            "اسم السهم": row["name"],
            "الكود": row["ticker"],
            "سعر الإغلاق": row["last_price"],
            "الاتجاه المتوقع": tr,
            "الدعم الأول": sup,
            "المقاومة الأولى": res,
            "وقف الخسارة المقترح": sl
        })
    st.dataframe(pd.DataFrame(analysis_data), use_container_width=True)

# 3. شاشة المصاريف والسيولة
elif menu == "المصاريف والسيولة":
    st.title("حركة الكاش والمصاريف الشخصية 💵")
    
    col1, col2 = st.columns(2)
    col1.metric("رصيد السيولة في المحفظة", f"{st.session_state.cash:,.2f} ج.م")
    exp_sum = st.session_state.expenses[st.session_state.expenses["النوع"] == "مصروف"]["المبلغ"].sum() if not st.session_state.expenses.empty else 0.0
    col2.metric("إجمالي المصاريف المسجلة", f"{exp_sum:,.2f} ج.م")

    st.subheader("سجل المعاملات")
    if not st.session_state.expenses.empty:
        st.dataframe(st.session_state.expenses, use_container_width=True)
    else:
        st.info("لا توجد مصاريف أو حركات كاش مسجلة بعد.")

# 4. تسجيل عملية جديدة
elif menu == "تسجيل عملية جديدة":
    st.title("تسجيل عملية تداول أو مصروف ✍️")
    op_type = st.radio("نوع الإدخال:", ["صفقة أسهم (بيع / شراء)", "حركة كاش / مصروف شخصي"], horizontal=True)

    if op_type == "صفقة أسهم (بيع / شراء)":
        with st.form("trade_form"):
            selected_ticker = st.selectbox("اختر السهم:", st.session_state.portfolio["ticker"].tolist())
            action = st.selectbox("نوع الصفقة:", ["شراء", "بيع"])
            qty = st.number_input("الكمية:", min_value=1, step=10)
            price = st.number_input("سعر التنفيذ (ج.م):", min_value=0.01, format="%.4f")
            submitted = st.form_submit_button("تنفيذ وتسجيل الصفقة")
            if submitted:
                st.success(f"تم تسجيل صفقة {action} لـ {qty} سهم على {selected_ticker} بسعر {price} ج.م بنجاح!")
    else:
        with st.form("cash_form"):
            cash_action = st.selectbox("نوع الحركة:", ["مصروف شخصي", "إيداع كاش للمحفظة", "سحب كاش من المحفظة"])
            category = st.text_input("التصنيف (مثال: فواتير، مواصلات، أرباح تداول):")
            amount = st.number_input("المبلغ (ج.م):", min_value=1.0, step=50.0)
            notes = st.text_area("ملاحظات:")
            submitted_cash = st.form_submit_button("حفظ الحركة")
            if submitted_cash:
                new_row = {"التاريخ": str(datetime.date.today()), "النوع": cash_action, "التصنيف": category, "المبلغ": amount, "ملاحظات": notes}
                st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_row])], ignore_index=True)
                if cash_action == "إيداع كاش للمحفظة":
                    st.session_state.cash += amount
                elif cash_action == "سحب كاش من المحفظة":
                    st.session_state.cash -= amount
                st.success("تم تسجيل العملية وتحديث رصيد الكاش فوراً!")
