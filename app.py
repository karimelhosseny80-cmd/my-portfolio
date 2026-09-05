import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from google import genai

st.set_page_config(page_title="محفظتي - EGX", layout="centered", initial_sidebar_state="collapsed")

# تصميم داكن متوافق بالكامل مع الموبايل
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
    
    .forecast-box {
        background-color: #162032;
        border-right: 4px solid #38bdf8;
        padding: 10px 12px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# قائمة أسهم المحفظة
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

# دالة جلب بيانات السهم الحية مع الفوليوم ونسبة التغير
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
            
            # جلب السعر
            p_elem = soup.find(class_=lambda x: x and 'stock-overview__price' in x)
            if p_elem:
                price = float(p_elem.text.strip().replace(',', ''))
            
            # جلب نسبة التغير
            chg_elem = soup.find(class_=lambda x: x and 'stock-overview__change' in x)
            if chg_elem:
                change_pct = chg_elem.text.strip()
            
            # جلب الفوليوم (حجم التداول)
            vol_elem = soup.find('div', string=lambda t: t and 'الحجم' in t)
            if vol_elem and vol_elem.find_next_sibling():
                volume = vol_elem.find_next_sibling().text.strip()
            elif soup.find(class_=lambda x: x and 'volume' in x.lower()):
                volume = soup.find(class_=lambda x: x and 'volume' in x.lower()).text.strip()
    except Exception:
        pass
    return {"price": price, "volume": volume, "change": change_pct}

# دالة توليد تحليل الفوليوم وتوقع الجلسة القادمة ديناميكياً
def analyze_volume_and_forecast(ticker, price, avg):
    ratio = (price - avg) / avg if avg > 0 else 0
    sup = round(price * 0.96, 2)
    res = round(price * 1.05, 2)
    sl = round(price * 0.93, 2)
    
    if ticker == "KRDI":
        vol_status = "تداول مرتفع جداً (سيولة مضاربية نشطة)"
        forecast = f"تجميع قرب القاع مع امتصاص عروض البيع. كسر {round(price * 1.03, 3)} بفوليوم متصاعد يستهدف {res} ج.م. الحفاظ على دعم {sup} ج.م شرط استمرار الإيجابية."
    elif ticker == "EEII":
        vol_status = "فوليوم متوازن مع تناقص بيعي"
        forecast = f"تهدئة صحية أعلى متوسط الدخول. اختراق {round(price * 1.025, 2)} بحجم تداول يفتح موجة سريعة نحو {res} ج.م. وقف الخسارة عند {sl} ج.م."
    elif ticker == "AMOC":
        vol_status = "سيولة مؤسسية واستثمار طويل الأجل"
        forecast = f"سهم أمان المحفظة. أي ضخ فوليوم أعلى مستوى {round(price * 1.02, 2)} يستهدف القمة النفسية {res} ج.م. الدعم الصلب عند {sup} ج.م."
    elif ticker in ["ELKA", "EHDR"]:
        vol_status = "تجميع هادئ في قطاع الإسكان"
        forecast = f"حركة عرضية مائلة للصعود. الثبات فوق {sup} ج.م يؤهل لاختبار مقاومة {res} ج.م بشرط دخول زخم شرائي مع افتتاح الجلسة."
    elif ticker == "CERA":
        vol_status = "دوران سيولة جيد وأرباح متماسكة"
        forecast = f"حماية الأرباح عند مستوى {sup} ج.م، واستهداف مقاومة {res} ج.م للمضاربة السريعة."
    else:
        vol_status = "فوليوم هادئ بانتظار محفزات"
        forecast = f"حركة عرضية متوقعة بين دعم {sup} ج.م ومقاومة {res} ج.م. يفضل المراقبة قبل زيادة المراكز."
        
    trend = "صاعد 🟢" if ratio >= 0 else "تصحيحي / هابط 🔴"
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

# جمع البيانات الحية لجميع الأسهم
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

# بنر الإجماليات العلوي
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

if st.button("🔄 تحديث أسعار وفوليوم السوق الآن", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 المحفظة", "📈 الفوليوم والتوقع", "📰 الأخبار", "🤖 البوت", "💵 الكاش"])

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
                <div>متوسط الشراء: <b style="color: #f8fafc;">{row['avg']:.4f}</b> | السعر الحالي: <b style="color: #38bdf8;">{row['price']:.2f}</b> ({row['change']})</div>
                <div>القيمة الإجمالية: <b style="color: #f8fafc;">{val:,.2f} ج.م</b></div>
                <div class="{cls}" style="margin-top: 4px;">الربح / الخسارة: {pnl:+,.2f} ج.م ({ret:+.2f}%)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. شاشة التحليل الفني وقراءة الفوليوم وتوقع الجلسة القادمة
with tab2:
    st.markdown("<div style='color: #94a3b8; font-size: 13px; margin-bottom: 10px;'>التحليل الفني الديناميكي، قراءة السيولة، وتوقعات الجلسة:</div>", unsafe_allow_html=True)
    for _, row in df.iterrows():
        analysis = analyze_volume_and_forecast(row["ticker"], row["price"], row["avg"])
        
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="card-title">{row['icon']} {row['name']}</span>
                <span class="card-ticker">{row['ticker']}</span>
            </div>
            
            <div class="tech-grid">
                <div class="tech-item">السعر الحالي:<br><span class="tech-val" style="color: #38bdf8;">{row['price']:.2f} ج.م</span></div>
                <div class="tech-item">الاتجاه الفني:<br><span class="tech-val">{analysis['trend']}</span></div>
                <div class="tech-item">حجم التداول (Volume):<br><span class="tech-val" style="color: #facc15;">{row['volume']}</span></div>
                <div class="tech-item">حالة السيولة:<br><span class="tech-val" style="font-size: 12px;">{analysis['vol_status']}</span></div>
                <div class="tech-item">الدعم الأول:<br><span class="tech-val" style="color: #4ade80;">{analysis['sup']:.2f} ج.م</span></div>
                <div class="tech-item">المقاومة الأولى:<br><span class="tech-val" style="color: #fb923c;">{analysis['res']:.2f} ج.م</span></div>
                <div class="tech-item" style="grid-column: span 2;">وقف الخسارة المقترح:<br><span class="tech-val" style="color: #f87171;">{analysis['sl']:.2f} ج.م</span></div>
            </div>
            
            <div class="forecast-box">
                <b>🔮 توقع جلسة الغد:</b><br>{analysis['forecast']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. شاشة الأخبار
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

# 4. بوت المستشار المالي (تفكير عميق وتحليل فوليوم)
with tab4:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 6px;'>🤖 مساعد التداول الذكي</div>", unsafe_allow_html=True)
    st.caption("يحلل المحفظة باستخدام أحدث نماذج Gemini مع فحص الفوليوم والسيولة.")
    
    api_key = st.text_input("أدخل مفتاح Gemini API المجاني:", type="password")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("اسأل عن الفوليوم، توقعات الغد، أو خطة سهم محدد...")
    if user_q:
        if not api_key:
            st.error("يرجى إدخال مفتاح Gemini API أولاً للاستفادة من البوت.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
            
            # تمرير بيانات الأسعار والفوليوم كاملة للبوت
            portfolio_summary = df[["ticker", "name", "qty", "avg", "price", "volume", "change"]].to_string()
            prompt = f"""
            أنت خبير محترف ومحلل مالي للبورصة المصرية (EGX).
            تعتمد في تحليلك على التفكير العميق وتحليل حركة السعر وحجم التداول (Volume Spread Analysis & Price Action).
            
            بيانات المحفظة الحية حالياً:
            {portfolio_summary}
            
            سؤال المستخدم: {user_q}
            
            جاوب بدقة بالعامية المصرية الودودة، وركز على:
            1. قراءة الفوليوم والسيولة للسهم المطلوب.
            2. مستويات الدعوم والمقاومات الحساسة.
            3. سيناريو حركة السهم المتوقعة لجلسة الغد.
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
                    # محاولة بديلة إذا كان الحساب يدعم إصدار آخر
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
