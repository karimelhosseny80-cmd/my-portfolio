import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from google import genai

st.set_page_config(page_title="محفظتي - EGX", layout="centered", initial_sidebar_state="collapsed")

# تصميم داكن متكامل للموبايل
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700;800&display=swap');
    * { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .block-container { padding: 1rem !important; background-color: #0e1117; }
    
    .card {
        background-color: #1a1f2c !important;
        border: 1px solid #2d3748 !important;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .card-title { color: #f8fafc !important; font-size: 16px; font-weight: 700; }
    .card-ticker {
        background-color: #2b354f;
        color: #60a5fa !important;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
    }
    .card-text { color: #cbd5e1 !important; font-size: 13px; line-height: 1.8; }
    .badge-win { color: #4ade80 !important; font-weight: 700; font-size: 14px; }
    .badge-loss { color: #f87171 !important; font-weight: 700; font-size: 14px; }
    
    .tech-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 10px;
        background: #131722;
        padding: 12px;
        border-radius: 10px;
    }
    .tech-item { font-size: 13px; color: #94a3b8; }
    .tech-val { color: #f8fafc; font-weight: 700; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# قائمة الأسهم
DEFAULT_STOCKS = [
    {"icon": "⚙️", "name": "العربية للصناعات الهندسية", "ticker": "EEII", "qty": 24372, "avg": 2.2904, "fallback_price": 2.35},
    {"icon": "🌾", "name": "نهر الخير للتنمية والاستثمار", "ticker": "KRDI", "qty": 123690, "avg": 0.4159, "fallback_price": 0.449},
    {"icon": "🏢", "name": "القاهرة للإسكان والتعمير", "ticker": "ELKA", "qty": 21990, "avg": 1.7544, "fallback_price": 1.87},
    {"icon": "🏺", "name": "سيراميكا ريماس", "ticker": "CERA", "qty": 22100, "avg": 1.3159, "fallback_price": 1.50},
    {"icon": "🏗️", "name": "المصريين للإسكان والتنمية", "ticker": "EHDR", "qty": 9793, "avg": 2.6623, "fallback_price": 2.88},
    {"icon": "💎", "name": "العز سيراميك (الجوهرة)", "ticker": "ECAP", "qty": 365, "avg": 34.4619, "fallback_price": 33.62},
    {"icon": "🔩", "name": "مصر الوطنية للصلب (عتاقة)", "ticker": "ATQA", "qty": 592, "avg": 12.6712, "fallback_price": 12.17},
    {"icon": "🛢️", "name": "أموك للزيوت المعدنية", "ticker": "AMOC", "qty": 449, "avg": 7.9226, "fallback_price": 13.50},
]

# دالة جلب السعر المباشر
@st.cache_data(ttl=180)
def get_live_price(ticker, fallback):
    url = f"https://www.mubasher.info/markets/EGX/stocks/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            elem = soup.find(class_=lambda x: x and 'stock-overview__price' in x)
            if elem:
                return float(elem.text.strip().replace(',', ''))
    except Exception:
        pass
    return fallback

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

# تجميع بيانات المحفظة
portfolio_data = []
for s in DEFAULT_STOCKS:
    live_p = get_live_price(s["ticker"], s["fallback_price"])
    item = dict(s)
    item["price"] = live_p
    portfolio_data.append(item)

df = pd.DataFrame(portfolio_data)
total_cost = (df["qty"] * df["avg"]).sum()
total_market = (df["qty"] * df["price"]).sum()
net_pnl = total_market - total_cost
net_return = (net_pnl / total_cost) * 100 if total_cost > 0 else 0

# بنر الإجماليات
pnl_color = "#4ade80" if net_pnl >= 0 else "#f87171"
st.markdown(f"""
<div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 14px; padding: 18px; margin-bottom: 12px; text-align: center;">
    <div style="color: #94a3b8; font-size: 13px;">إجمالي القيمة السوقية للمحفظة</div>
    <div style="color: #f8fafc; font-size: 26px; font-weight: 800; margin: 4px 0;">{total_market:,.2f} ج.م</div>
    <div style="color: {pnl_color}; font-size: 15px; font-weight: 700;">
        الأرباح: {net_pnl:+,.2f} ج.م ({net_return:+.2f}%)
    </div>
    <div style="color: #64748b; font-size: 12px; margin-top: 6px;">الكاش المتاح: {st.session_state.cash:,.2f} ج.م</div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 تحديث أسعار السوق الآن", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 المحفظة", "📈 التحليل", "📰 الأخبار", "🤖 البوت", "💵 الكاش"])

# 1. شاشة الأسهم
with tab1:
    for _, row in df.iterrows():
        cost = row["qty"] * row["avg"]
        val = row["qty"] * row["price"]
        pnl = val - cost
        ret = (pnl / cost) * 100
        cls = "badge-win" if pnl >= 0 else "badge-loss"
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div class="card-title">{row['icon']} {row['name']}</div>
                <div class="card-ticker">{row['ticker']}</div>
            </div>
            <div class="card-text">
                <div>الكمية: <b style="color: #f8fafc;">{row['qty']:,}</b> سهم</div>
                <div>متوسط الشراء: <b style="color: #f8fafc;">{row['avg']:.4f}</b> | السعر الحالي: <b style="color: #38bdf8;">{row['price']:.2f}</b></div>
                <div>القيمة الإجمالية: <b style="color: #f8fafc;">{val:,.2f} ج.م</b></div>
                <div class="{cls}" style="margin-top: 4px;">الربح / الخسارة: {pnl:+,.2f} ج.م ({ret:+.2f}%)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. التحليل الفني
with tab2:
    st.markdown("<div style='color: #94a3b8; font-size: 13px; margin-bottom: 10px;'>مستويات الدعم والمقاومة والاتجاه الفني (محدثة لحظياً):</div>", unsafe_allow_html=True)
    for _, row in df.iterrows():
        p = row["price"]
        sup1 = round(p * 0.96, 2)
        res1 = round(p * 1.05, 2)
        sl = round(p * 0.93, 2)
        trend = "صاعد 🟢" if p >= row["avg"] else "هابط / تصحيحي 🔴"
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="card-title">{row['icon']} {row['name']}</span>
                <span class="card-ticker">{row['ticker']}</span>
            </div>
            <div class="tech-grid">
                <div class="tech-item">السعر الحالي:<br><span class="tech-val" style="color: #38bdf8;">{p:.2f} ج.م</span></div>
                <div class="tech-item">الاتجاه المتوقع:<br><span class="tech-val">{trend}</span></div>
                <div class="tech-item">الدعم الأول:<br><span class="tech-val" style="color: #4ade80;">{sup1:.2f} ج.م</span></div>
                <div class="tech-item">المقاومة الأولى:<br><span class="tech-val" style="color: #fb923c;">{res1:.2f} ج.م</span></div>
                <div class="tech-item" style="grid-column: span 2;">وقف الخسارة المقترح:<br><span class="tech-val" style="color: #f87171;">{sl:.2f} ج.م</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. الأخبار
with tab3:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 10px;'>أحدث إفصاحات وأخبار أسهم المحفظة:</div>", unsafe_allow_html=True)
    for _, row in df.iterrows():
        news = get_stock_news(row["ticker"])
        with st.expander(f"{row['icon']} {row['name']} ({row['ticker']})"):
            if news:
                for n in news:
                    st.markdown(f"• [{n['title']}]({n['url']})")
            else:
                st.caption("لا توجد أخبار جديدة معلنة اليوم.")

# 4. البوت الذكي
with tab4:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 6px;'>🤖 مساعد التداول الذكي</div>", unsafe_allow_html=True)
    st.caption("مربوط بمحفظتك مباشرة؛ اسأله عن تحركات الأسهم أو نصائح التداول.")
    
    api_key = st.text_input("أدخل مفتاح Gemini API المجاني:", type="password")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("اسأل البوت عن أي سهم في محفظتك...")
    if user_q:
        if not api_key:
            st.error("يرجى إدخال مفتاح Gemini API أولاً للاستفادة من البوت.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
            
            portfolio_summary = df[["ticker", "name", "qty", "avg", "price"]].to_string()
            prompt = f"""
            أنت خبير ومحلل مالي في البورصة المصرية ومساعد شخصي للمستخدم.
            بيانات محفظة المستخدم الحالية هي:
            {portfolio_summary}
            سؤال المستخدم: {user_q}
            جاوب بدقة واختصار وباللهجة المصرية الودودة وقدم نصائح فنية واقعية.
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
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# 5. الكاش والمصاريف
with tab5:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 8px;'>تسجيل حركة كاش أو مصروف</div>", unsafe_allow_html=True)
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
        st.write("---")
        for exp in reversed(st.session_state.expenses[-5:]):
            st.markdown(f"<div style='color: #94a3b8; font-size: 12px;'>• {exp['التاريخ']} | {exp['النوع']}: <b style='color: #f8fafc;'>{exp['المبلغ']} ج.م</b> ({exp['البيان']})</div>", unsafe_allow_html=True)
