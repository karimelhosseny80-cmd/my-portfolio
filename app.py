import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from google import genai

st.set_page_config(page_title="محفظة تيلدا", layout="centered", initial_sidebar_state="collapsed")

# تصميم داكن نقي ومنع تداخل النصوص على شاشات الهواتف
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700;800&display=swap');
    * { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .block-container { padding: 0.8rem !important; background-color: #0b0f19; }
    
    /* إخفاء القائمة الجانبية نهائياً لمنع أي تداخل شاشات */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    /* بنر الصلاة على النبي */
    .prophet-banner {
        background: linear-gradient(90deg, #10b981, #059669);
        color: #ffffff;
        text-align: center;
        padding: 10px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    /* كارت ملخص المحفظة */
    .summary-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid #4338ca;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        text-align: center;
    }
    
    /* كارت السهم */
    .stock-box {
        background-color: #151b28;
        border: 1px solid #283347;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ترويسة التطبيق
st.markdown('<div class="prophet-banner">✨ صلِّ على محمد ﷺ ✨</div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 12px;'>💼 محفظة تيلدا</h2>", unsafe_allow_html=True)

# قائمة الأسهم
DEFAULT_STOCKS = [
    {"icon": "⚙️", "name": "العربية للصناعات الهندسية", "ticker": "EEII", "qty": 24372, "avg": 2.2904, "fallback_price": 2.35, "purify": "شرعي (تطهير 1.2%)"},
    {"icon": "🌾", "name": "نهر الخير للتنمية والاستثمار", "ticker": "KRDI", "qty": 123690, "avg": 0.4159, "fallback_price": 0.449, "purify": "شرعي (تطهير 0.8%)"},
    {"icon": "🏢", "name": "القاهرة للإسكان والتعمير", "ticker": "ELKA", "qty": 21990, "avg": 1.7544, "fallback_price": 1.87, "purify": "شرعي نقي 100%"},
    {"icon": "🏺", "name": "سيراميكا ريماس", "ticker": "CERA", "qty": 22100, "avg": 1.3159, "fallback_price": 1.50, "purify": "شرعي (تطهير 1.5%)"},
    {"icon": "🏗️", "name": "المصريين للإسكان والتنمية", "ticker": "EHDR", "qty": 9793, "avg": 2.6623, "fallback_price": 2.88, "purify": "شرعي نقي 100%"},
    {"icon": "💎", "name": "العز سيراميك (الجوهرة)", "ticker": "ECAP", "qty": 365, "avg": 34.4619, "fallback_price": 33.62, "purify": "شرعي (تطهير 2.1%)"},
    {"icon": "🔩", "name": "مصر الوطنية للصلب (عتاقة)", "ticker": "ATQA", "qty": 592, "avg": 12.6712, "fallback_price": 12.17, "purify": "شرعي نقي 100%"},
    {"icon": "🛢️", "name": "أموك للزيوت المعدنية", "ticker": "AMOC", "qty": 449, "avg": 7.9226, "fallback_price": 13.50, "purify": "شرعي (تطهير 1.1%)"},
]

# دالة جلب بيانات السهم الحية
@st.cache_data(ttl=180)
def get_live_market_data(ticker, fallback_price):
    url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    price = fallback_price
    volume = "—"
    change_pct = "0.0%"
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            p_elem = soup.find(class_=lambda x: x and 'stock-overview__price' in x)
            if p_elem:
                price = float(p_elem.text.strip().replace(',', ''))
            chg_elem = soup.find(class_=lambda x: x and 'stock-overview__change' in x)
            if chg_elem:
                change_pct = chg_elem.text.strip()
            vol_elem = soup.find('div', string=lambda t: t and 'الحجم' in t)
            if vol_elem and vol_elem.find_next_sibling():
                volume = vol_elem.find_next_sibling().text.strip()
            elif soup.find(class_=lambda x: x and 'volume' in x.lower()):
                volume = soup.find(class_=lambda x: x and 'volume' in x.lower()).text.strip()
    except Exception:
        pass
    return {"price": price, "volume": volume, "change": change_pct}

# دالة تحليل الفوليوم وتوقع الجلسة
def analyze_volume_and_forecast(ticker, price, avg):
    ratio = (price - avg) / avg if avg > 0 else 0
    sup = round(price * 0.96, 2)
    res = round(price * 1.05, 2)
    sl = round(price * 0.93, 2)
    
    if ticker == "KRDI":
        vol_status = "سيولة مضاربية عالية جداً"
        forecast = f"تجميع وامتصاص عروض بيع. اختراق {round(price * 1.03, 3)} بفوليوم متصاعد يفتح الطريق لاختبار {res} ج.م. الحفاظ على {sup} ج.م ضروري."
    elif ticker == "EEII":
        vol_status = "تناقص بيعي وتماسك إيجابي"
        forecast = f"تهدئة صحية أعلى متوسط الدخول. اختراق {round(price * 1.025, 2)} بفوليوم يستهدف {res} ج.م. وقف الخسارة عند {sl} ج.م."
    elif ticker == "AMOC":
        vol_status = "سيولة مؤسسية متزنة"
        forecast = f"سهم أمان واستقرار. الثبات أعلى {sup} ج.م يؤهل لمعاودة اختبار {res} ج.م."
    elif ticker in ["ELKA", "EHDR"]:
        vol_status = "تجميع هادئ داخل قطاع الإسكان"
        forecast = f"حركة عرضية مائلة للصعود نحو {res} ج.م بشرط البقاء أعلى دعم {sup} ج.م."
    elif ticker == "CERA":
        vol_status = "أرباح جيدة وتماسك سعري"
        forecast = f"حماية الأرباح فوق {sup} ج.م واستهداف {res} ج.م."
    else:
        vol_status = "تداول هادئ وترقب محفزات"
        forecast = f"نطاق عرضي متوقع بين دعم {sup} ج.م ومقاومة {res} ج.م."
        
    trend = "صاعد 🟢" if ratio >= 0 else "تصحيحي 🔴"
    return {"sup": sup, "res": res, "sl": sl, "trend": trend, "vol_status": vol_status, "forecast": forecast}

# دالة جلب أخبار السهم
@st.cache_data(ttl=900)
def get_stock_news(ticker):
    url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    news_items = []
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.find_all('a', href=lambda x: x and '/news/' in x)
            for a in links[:3]:
                title = a.text.strip()
                href = a.get('href')
                full_url = f"https://www.mubasher.info{href}" if href.startswith('/') else href
                if title and len(title) > 15 and {"title": title, "url": full_url} not in news_items:
                    news_items.append({"title": title, "url": full_url})
    except Exception:
        pass
    return news_items

if "cash" not in st.session_state:
    st.session_state.cash = 0.0
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# جلب البيانات الحية
portfolio_data = []
for s in DEFAULT_STOCKS:
    market_info = get_live_market_data(s["ticker"], s["fallback_price"])
    item = dict(s)
    item["price"] = market_info["price"]
    item["volume"] = market_info["volume"]
    item["change"] = market_info["change"]
    portfolio_data.append(item)

df = pd.DataFrame(portfolio_data)
total_cost = (df["qty"] * df["avg"]).sum()
total_market = (df["qty"] * df["price"]).sum()
net_pnl = total_market - total_cost
net_return = (net_pnl / total_cost) * 100 if total_cost > 0 else 0

# بطاقة ملخص المحفظة
pnl_color = "#34d399" if net_pnl >= 0 else "#f87171"
st.markdown(f"""
<div class="summary-card">
    <div style="color: #a5b4fc; font-size: 13px;">إجمالي القيمة السوقية</div>
    <div style="color: #ffffff; font-size: 26px; font-weight: 800; margin: 4px 0;">{total_market:,.2f} ج.م</div>
    <div style="color: {pnl_color}; font-size: 15px; font-weight: 700;">
        الأرباح: {net_pnl:+,.2f} ج.م ({net_return:+.2f}%)
    </div>
    <div style="color: #cbd5e1; font-size: 12px; margin-top: 6px;">الكاش المتاح: {st.session_state.cash:,.2f} ج.م</div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 تحديث أسعار وفوليوم السوق الآن", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# قائمة اختيار أنيقة وعريضة بأعلى الشاشة (بديل مثالي ونظيف للـ Sidebar)
menu = st.selectbox(
    "☰ انتقال سريع إلى:",
    ["📊 الأسهم والمحفظة", "📈 الفوليوم والتوقع", "⚖️ التطهير الشرعي", "📰 أخبار البورصة", "🤖 مساعد التداول", "💵 إدارة الكاش"]
)
st.write("")

# 1. شاشة الأسهم
if menu == "📊 الأسهم والمحفظة":
    st.markdown("### 📊 تفاصيل أسهم المحفظة")
    for _, row in df.iterrows():
        cost = row["qty"] * row["avg"]
        val = row["qty"] * row["price"]
        pnl = val - cost
        ret = (pnl / cost) * 100
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"**{row['icon']} {row['name']}**")
            col2.markdown(f"`{row['ticker']}`")
            
            c1, c2 = st.columns(2)
            c1.metric("السعر الحالي", f"{row['price']:.2f} ج.م", delta=row['change'])
            c2.metric("متوسط الشراء", f"{row['avg']:.4f} ج.م")
            
            c3, c4 = st.columns(2)
            c3.caption(f"الكمية: **{row['qty']:,}** سهم")
            c4.caption(f"القيمة: **{val:,.2f} ج.م**")
            
            color_delta = "green" if pnl >= 0 else "red"
            st.markdown(f":{color_delta}[**الربح / الخسارة:** {pnl:+,.2f} ج.م ({ret:+.2f}%)]")
            st.divider()

# 2. شاشة التحليل والفوليوم
elif menu == "📈 الفوليوم والتوقع":
    st.markdown("### 📈 التحليل الفني وحجم التداول")
    for _, row in df.iterrows():
        analysis = analyze_volume_and_forecast(row["ticker"], row["price"], row["avg"])
        with st.container():
            col_t1, col_t2 = st.columns([3, 1])
            col_t1.markdown(f"**{row['icon']} {row['name']}**")
            col_t2.markdown(f"`{row['ticker']}`")
            
            c1, c2 = st.columns(2)
            c1.metric("السعر الحالي", f"{row['price']:.2f} ج.م", delta=row['change'])
            c1.metric("حجم التداول", str(row['volume']))
            c1.markdown(f"🟢 **الدعم الأول:** `{analysis['sup']:.2f} ج.م`")
            
            c2.metric("الاتجاه", analysis['trend'])
            c2.markdown(f"💧 **السيولة:** {analysis['vol_status']}")
            c2.markdown(f"🟠 **المقاومة الأولى:** `{analysis['res']:.2f} ج.م`")
            
            st.markdown(f"🔴 **وقف الخسارة المقترح:** `{analysis['sl']:.2f} ج.م`")
            st.info(f"🔮 **توقع جلسة الغد:**\n\n{analysis['forecast']}")
            st.divider()

# 3. شاشة التطهير
elif menu == "⚖️ التطهير الشرعي":
    st.markdown("### ⚖️ الموقف الشرعي ونسب التطهير")
    for _, row in df.iterrows():
        val = row["qty"] * row["price"]
        pnl = val - (row["qty"] * row["avg"])
        with st.container():
            st.markdown(f"**{row['icon']} {row['name']}** (`{row['ticker']}`)")
            st.success(f"الحالة: {row['purify']}")
            if pnl > 0 and "تطهير" in row['purify']:
                st.caption(f"الأرباح السوقية المحققة: {pnl:,.2f} ج.م")
            st.divider()

# 4. شاشة الأخبار
elif menu == "📰 أخبار البورصة":
    st.markdown("### 📰 أحدث الإفصاحات وأخبار الأسهم")
    for _, row in df.iterrows():
        news = get_stock_news(row["ticker"])
        with st.expander(f"{row['icon']} {row['name']} ({row['ticker']})"):
            if news:
                for n in news:
                    st.markdown(f"• [{n['title']}]({n['url']})")
            else:
                st.caption("لا توجد إفصاحات جديدة معلنة اليوم.")

# 5. شاشة البوت
elif menu == "🤖 مساعد التداول":
    st.markdown("### 🤖 مساعد التداول الذكي")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("اكتب سؤالك عن المحفظة...")
    if user_q:
        if not api_key:
            st.error("يرجى إدخال المفتاح أولاً.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
            
            portfolio_summary = df[["ticker", "name", "qty", "avg", "price", "volume", "change"]].to_string()
            prompt = f"""
            أنت خبير مالي في البورصة المصرية لمحفظة تيلدا.
            بيانات المحفظة الحالية:
            {portfolio_summary}
            سؤال المستخدم: {user_q}
            جاوب باختصار بالعامية المصرية وركز على السيولة والدعوم والمقاومات.
            """
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                ans = response.text
                with st.chat_message("assistant"):
                    st.write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception:
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                    )
                    ans = response.text
                    with st.chat_message("assistant"):
                        st.write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

# 6. شاشة الكاش
elif menu == "💵 إدارة الكاش":
    st.markdown("### 💵 تسجيل حركة كاش أو مصروف")
    with st.form("cash_form"):
        action = st.selectbox("نوع المعاملة:", ["مصروف شخصي", "إيداع كاش للمحفظة", "سحب كاش من المحفظة"])
        amt = st.number_input("المبلغ (ج.م):", min_value=1.0, step=50.0)
        desc = st.text_input("البيان:")
        if st.form_submit_button("حفظ الحركة", use_container_width=True):
            if action == "إيداع كاش للمحفظة":
                st.session_state.cash += amt
            elif action == "سحب كاش من المحفظة":
                st.session_state.cash -= amt
            st.session_state.expenses.append({"التاريخ": str(datetime.date.today()), "النوع": action, "المبلغ": amt, "البيان": desc})
            st.success("تم الحفظ بنجاح!")
            st.rerun()

    if st.session_state.expenses:
        st.divider()
        st.markdown("### آخر المعاملات المسجلة:")
        for exp in reversed(st.session_state.expenses[-5:]):
            st.markdown(f"• {exp['التاريخ']} | {exp['النوع']}: **{exp['المبلغ']} ج.م** ({exp['البيان']})")
