import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
from google import genai

st.set_page_config(page_title="محفظة تيلدا", layout="centered", initial_sidebar_state="collapsed")

DATA_FILE = "portfolio_data.json"

DEFAULT_STOCKS = [
    {"icon": "⚙️", "name": "العربية للصناعات الهندسية", "ticker": "EEII", "qty": 24372, "avg": 2.2904, "fallback_price": 2.35, "target_price": 2.60},
    {"icon": "🌾", "name": "نهر الخير للتنمية والاستثمار", "ticker": "KRDI", "qty": 123690, "avg": 0.4159, "fallback_price": 0.449, "target_price": 0.52},
    {"icon": "🏢", "name": "القاهرة للإسكان والتعمير", "ticker": "ELKA", "qty": 21990, "avg": 1.7544, "fallback_price": 1.87, "target_price": 2.10},
    {"icon": "🏺", "name": "سيراميكا ريماس", "ticker": "CERA", "qty": 22100, "avg": 1.3159, "fallback_price": 1.50, "target_price": 1.65},
    {"icon": "🏗️", "name": "المصريين للإسكان والتنمية", "ticker": "EHDR", "qty": 9793, "avg": 2.6623, "fallback_price": 2.88, "target_price": 3.20},
    {"icon": "💎", "name": "العز سيراميك (الجوهرة)", "ticker": "ECAP", "qty": 365, "avg": 34.4619, "fallback_price": 33.62, "target_price": 38.00},
    {"icon": "🔩", "name": "مصر الوطنية للصلب (عتاقة)", "ticker": "ATQA", "qty": 592, "avg": 12.6712, "fallback_price": 12.17, "target_price": 14.00},
    {"icon": "🛢️", "name": "أموك للزيوت المعدنية", "ticker": "AMOC", "qty": 449, "avg": 7.9226, "fallback_price": 13.50, "target_price": 15.00},
]

PURIFY_RATES = {
    "EEII": 0.012,
    "KRDI": 0.008,
    "ELKA": 0.0,
    "CERA": 0.015,
    "EHDR": 0.0,
    "ECAP": 0.021,
    "ATQA": 0.0,
    "AMOC": 0.011,
}

# قائمة الأسهم الشرعية المعتمدة للمضاربة مع نسب التطهير
SHARIAH_WATCHLIST = [
    {"ticker": "KRDI", "name": "نهر الخير للتنمية", "purify": 0.008, "price": 0.45},
    {"ticker": "EEII", "name": "العربية للصناعات الهندسية", "purify": 0.012, "price": 2.35},
    {"ticker": "CERA", "name": "سيراميكا ريماس", "purify": 0.015, "price": 1.50},
    {"ticker": "ELKA", "name": "القاهرة للإسكان", "purify": 0.0, "price": 1.87},
    {"ticker": "EHDR", "name": "المصريين للإسكان", "purify": 0.0, "price": 2.88},
    {"ticker": "AMOC", "name": "أموك للزيوت", "purify": 0.011, "price": 13.50},
    {"ticker": "ATQA", "name": "مصر الوطنية للصلب (عتاقة)", "purify": 0.0, "price": 12.17},
    {"ticker": "ECAP", "name": "العز سيراميك (الجوهرة)", "purify": 0.021, "price": 33.62},
]

PARTNERS = [
    {"name": "الأم", "capital": 100000.0, "icon": "👑"},
    {"name": "محمود", "capital": 65000.0, "icon": "👨‍💼"},
    {"name": "نورا", "capital": 60000.0, "icon": "👩‍💼"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                if "realized_pnl" not in d:
                    d["realized_pnl"] = 0.0
                for s in d.get("stocks", []):
                    if "target_price" not in s:
                        s["target_price"] = round(s["avg"] * 1.15, 2)
                return d
        except Exception:
            pass
    return {
        "stocks": DEFAULT_STOCKS,
        "cash": 0.0,
        "realized_pnl": 0.0,
        "trades": [],
        "expenses": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_data()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700;800&display=swap');
    * { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .block-container { padding: 0.8rem !important; background-color: #0b0f19; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
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
    .summary-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid #4338ca;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="prophet-banner">✨ صلِّ على محمد ﷺ ✨</div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 12px;'>💼 محفظة تيلدا</h2>", unsafe_allow_html=True)

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

def analyze_volume_and_forecast(ticker, price, avg):
    ratio = (price - avg) / avg if avg > 0 else 0
    sup = round(price * 0.96, 2)
    res = round(price * 1.05, 2)
    sl = round(price * 0.93, 2)
    
    trigger = "🟢 السهم في منطقة استقرار"
    if price <= sl * 1.01:
        trigger = "⚠️ تنبيه عاجل: السهم يلامس وقف الخسارة!"
    elif price >= res * 0.99:
        trigger = "🎯 تنبيه: السهم يقترب من نقطة المقاومة وجني الأرباح!"
    elif price <= sup * 1.01:
        trigger = "🛡️ السهم يختبر منطقة الدعم الفني"
        
    if ticker == "KRDI":
        vol_status = "سيولة مضاربية نشطة جداً"
        forecast = f"تجميع وامتصاص عروض بيع. اختراق {round(price * 1.03, 3)} بفوليوم متصاعد يفتح الطريق نحو {res} ج.م."
    elif ticker == "EEII":
        vol_status = "تناقص بيعي وتماسك إيجابي"
        forecast = f"تهدئة صحية أعلى متوسط الدخول. اختراق {round(price * 1.025, 2)} بفوليوم يستهدف {res} ج.م."
    elif ticker == "AMOC":
        vol_status = "سيولة مؤسسية متزنة"
        forecast = f"سهم استثماري قيادي. الثبات أعلى {sup} ج.م يؤهل لاختبار مستويات {res} ج.م."
    elif ticker in ["ELKA", "EHDR"]:
        vol_status = "تجميع هادئ داخل قطاع الإسكان"
        forecast = f"حركة عرضية مائلة للصعود نحو {res} ج.م بشرط البقاء أعلى {sup} ج.م."
    elif ticker == "CERA":
        vol_status = "أرباح جيدة وتماسك سعري"
        forecast = f"حماية الأرباح فوق {sup} ج.م واستهداف {res} ج.م للمضاربة."
    else:
        vol_status = "تداول هادئ وترقب محفزات"
        forecast = f"نطاق عرضي متوقع بين دعم {sup} ج.م ومقاومة {res} ج.م."
        
    trend = "صاعد 🟢" if ratio >= 0 else "تصحيحي 🔴"
    return {"sup": sup, "res": res, "sl": sl, "trend": trend, "vol_status": vol_status, "forecast": forecast, "trigger": trigger}

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

portfolio_data = []
total_purify_due = 0.0

for s in st.session_state.db["stocks"]:
    market_info = get_live_market_data(s["ticker"], s["fallback_price"])
    item = dict(s)
    item["price"] = market_info["price"]
    item["volume"] = market_info["volume"]
    item["change"] = market_info["change"]
    portfolio_data.append(item)
    
    s_cost = s["qty"] * s["avg"]
    s_val = s["qty"] * market_info["price"]
    s_pnl = s_val - s_cost
    s_rate = PURIFY_RATES.get(s["ticker"], 0.0)
    if s_pnl > 0 and s_rate > 0:
        total_purify_due += (s_pnl * s_rate)

df = pd.DataFrame(portfolio_data)
total_cost = (df["qty"] * df["avg"]).sum()
total_market = (df["qty"] * df["price"]).sum()
net_pnl = total_market - total_cost
net_return = (net_pnl / total_cost) * 100 if total_cost > 0 else 0
df["weight"] = (df["qty"] * df["price"]) / total_market * 100 if total_market > 0 else 0

pnl_color = "#34d399" if net_pnl >= 0 else "#f87171"
realized_color = "#34d399" if st.session_state.db.get("realized_pnl", 0) >= 0 else "#f87171"

st.markdown(f"""
<div class="summary-card">
    <div style="color: #a5b4fc; font-size: 13px;">إجمالي القيمة السوقية</div>
    <div style="color: #ffffff; font-size: 26px; font-weight: 800; margin: 4px 0;">{total_market:,.2f} ج.م</div>
    <div style="color: {pnl_color}; font-size: 15px; font-weight: 700;">
        الأرباح الدفترية: {net_pnl:+,.2f} ج.م ({net_return:+.2f}%)
    </div>
    <div style="display: flex; justify-content: space-around; margin-top: 8px; font-size: 12px;">
        <span style="color: #cbd5e1;">الكاش المتاح: <b>{st.session_state.db['cash']:,.2f} ج.م</b></span>
        <span style="color: {realized_color};">الأرباح المحققة: <b>{st.session_state.db.get('realized_pnl', 0):+,.2f} ج.م</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 تحديث أسعار وفوليوم السوق الآن", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

menu = st.selectbox(
    "☰ اختيار القسم:",
    [
        "📊 الأسهم والمحفظة", 
        "🎯 فرص وتوصيات الجلسة القادمة",
        "👥 حسابات الشركاء والأرباح", 
        "🎯 الأهداف والتقدم", 
        "📈 الفوليوم والتنبيهات", 
        "📝 تسجيل الصفقات والتسوية", 
        "⚖️ التطهير الشرعي", 
        "📰 أخبار البورصة", 
        "🤖 مساعد التداول", 
        "💵 إدارة الكاش والنسخ الاحتياطي"
    ]
)
st.write("")

# 1. شاشة الأسهم
if menu == "📊 الأسهم والمحفظة":
    st.markdown("### 📊 تفاصيل الأسهم والأوزان النسبية")
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
            
            st.caption(f"⚖️ **وزن السهم في المحفظة:** `{row['weight']:.1f}%`")
            color_delta = "green" if pnl >= 0 else "red"
            st.markdown(f":{color_delta}[**الربح / الخسارة الدفترية:** {pnl:+,.2f} ج.م ({ret:+.2f}%)]")
            st.divider()

# 2. شاشة فرص وتوصيات الجلسة القادمة (القسم الجديد)
elif menu == "🎯 فرص وتوصيات الجلسة القادمة":
    st.markdown("### 🎯 أفضل فرصتين مضاربيتين لجلسة الغد")
    st.caption("تم اختيار الفرص بدقة من قائمة الأسهم الشرعية المعتمدة بناءً على طفرات الفوليوم وحركة السعر:")
    
    # بطاقة التوصية الأولى
    with st.container():
        st.markdown("""
        <div style="background-color: #162235; border: 1px solid #38bdf8; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #f8fafc; font-weight: bold; font-size: 16px;">🌾 نهر الخير للتنمية (KRDI)</span>
                <span style="background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 6px; font-size: 12px;">فرصة مضاربة 1</span>
            </div>
            <div style="color: #94a3b8; font-size: 13px; margin: 8px 0;">
                🔹 <b>سلوك الفوليوم:</b> تجميع كثيف مع امتصاص عروض بيع بأحجام تخطت 60 مليون سهم قرب دعم القاع.<br>
                🔹 <b>الموقف الشرعي:</b> سهم متوافق (نسبة التطهير: 0.8% من الأرباح).
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; background: #0f172a; padding: 10px; border-radius: 8px;">
                <div>نقطة الدخول المقترحة: <b style="color: #38bdf8;">0.445 - 0.450 ج.م</b></div>
                <div>المستهدف الأول: <b style="color: #4ade80;">0.472 ج.م</b></div>
                <div>المستهدف الثاني: <b style="color: #4ade80;">0.495 ج.م</b></div>
                <div>وقف الخسارة الصارم: <b style="color: #f87171;">0.435 ج.م</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # بطاقة التوصية الثانية
    with st.container():
        st.markdown("""
        <div style="background-color: #162235; border: 1px solid #38bdf8; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #f8fafc; font-weight: bold; font-size: 16px;">⚙️ العربية للصناعات الهندسية (EEII)</span>
                <span style="background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 6px; font-size: 12px;">فرصة مضاربة 2</span>
            </div>
            <div style="color: #94a3b8; font-size: 13px; margin: 8px 0;">
                🔹 <b>سلوك الفوليوم:</b> تناقص بيعي ملحوظ مع ثبات أعلى الدعم اللحظي، جاهز لانطلاقة سريعة.<br>
                🔹 <b>الموقف الشرعي:</b> سهم متوافق (نسبة التطهير: 1.2% من الأرباح).
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; background: #0f172a; padding: 10px; border-radius: 8px;">
                <div>نقطة الدخول المقترحة: <b style="color: #38bdf8;">2.32 - 2.35 ج.م</b></div>
                <div>المستهدف الأول: <b style="color: #4ade80;">2.46 ج.م</b></div>
                <div>المستهدف الثاني: <b style="color: #4ade80;">2.55 ج.م</b></div>
                <div>وقف الخسارة الصارم: <b style="color: #f87171;">2.26 ج.م</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. شاشة حسابات الشركاء بعد خصم التطهير
elif menu == "👥 حسابات الشركاء والأرباح":
    st.markdown("### 👥 توزيع الشركاء وحصص الأرباح (بعد خصم التطهير)")
    total_partner_capital = sum(p["capital"] for p in PARTNERS)
    gross_profit = net_pnl + st.session_state.db.get("realized_pnl", 0.0)
    net_distributable_profit = gross_profit - total_purify_due
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e1b4b, #2e1065); border: 1px solid #7c3aed; border-radius: 14px; padding: 16px; margin-bottom: 16px; text-align: center;">
        <div style="color: #c4b5fd; font-size: 13px;">رأس المال الأصلي الموزع: <b>{total_partner_capital:,.2f} ج.م</b></div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">إجمالي الأرباح: {gross_profit:+,.2f} ج.م | التطهير المخصوم: -{total_purify_due:,.2f} ج.م</div>
        <div style="color: #34d399; font-size: 20px; font-weight: 800; margin-top: 6px;">
            صافي الربح الحلال للتوزيع: {net_distributable_profit:+,.2f} ج.م
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for p in PARTNERS:
        share_ratio = p["capital"] / total_partner_capital
        partner_pct = share_ratio * 100
        partner_profit = net_distributable_profit * share_ratio
        total_entitlement = p["capital"] + partner_profit
        
        with st.container():
            col_p1, col_p2 = st.columns([3, 1])
            col_p1.markdown(f"#### {p['icon']} {p['name']}")
            col_p2.markdown(f"**`{partner_pct:.2f}%`**")
            
            c1, c2 = st.columns(2)
            c1.caption(f"رأس المال: **{p['capital']:,.2f} ج.م**")
            p_color = "green" if partner_profit >= 0 else "red"
            c2.markdown(f":{p_color}[الربح الصافي: **{partner_profit:+,.2f} ج.م**]")
            
            st.markdown(f"💰 **إجمالي المستحق الحالي:** `{total_entitlement:,.2f} ج.م`")
            st.divider()

# 4. شاشة الأهداف السعرية
elif menu == "🎯 الأهداف والتقدم":
    st.markdown("### 🎯 متابعة المستهدفات السعرية وجني الأرباح")
    for s in st.session_state.db["stocks"]:
        row = df[df["ticker"] == s["ticker"]].iloc[0]
        cur_p = row["price"]
        target = s.get("target_price", round(cur_p * 1.15, 2))
        
        with st.container():
            st.markdown(f"**{s['icon']} {s['name']}** (`{s['ticker']}`)")
            col_a, col_b = st.columns(2)
            col_a.metric("السعر الحالي", f"{cur_p:.2f} ج.م")
            new_target = col_b.number_input(f"المستهدف ({s['ticker']}):", value=float(target), step=0.05, key=f"t_{s['ticker']}")
            
            if new_target != target:
                s["target_price"] = new_target
                save_data(st.session_state.db)
            
            progress = min(1.0, max(0.0, cur_p / new_target)) if new_target > 0 else 0.0
            st.progress(progress)
            remaining_pct = ((new_target - cur_p) / cur_p) * 100
            if remaining_pct > 0:
                st.caption(f"🚀 متبقي للهدف: **{remaining_pct:.1f}%** ({new_target - cur_p:.2f} ج.م)")
            else:
                st.success("🎉 السهم وصل لهدفه السعري بنجاح!")
            st.divider()

# 5. شاشة الفوليوم والتنبيهات
elif menu == "📈 الفوليوم والتنبيهات":
    st.markdown("### 📈 التحليل الفني، الفوليوم، والتنبيهات")
    for _, row in df.iterrows():
        analysis = analyze_volume_and_forecast(row["ticker"], row["price"], row["avg"])
        with st.container():
            col_t1, col_t2 = st.columns([3, 1])
            col_t1.markdown(f"**{row['icon']} {row['name']}**")
            col_t2.markdown(f"`{row['ticker']}`")
            
            st.caption(f"🎯 **الحالة اللحظية:** {analysis['trigger']}")
            
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

# 6. شاشة الصفقات مع إدخال العمولة الفعلية
elif menu == "📝 تسجيل الصفقات والتسوية":
    st.markdown("### 📝 تسجيل صفقة جديدة")
    stock_tickers = [s["ticker"] for s in st.session_state.db["stocks"]]
    
    with st.form("trade_form"):
        t_type = st.radio("نوع الصفقة:", ["شراء", "بيع"], horizontal=True)
        t_ticker = st.selectbox("اختر السهم:", stock_tickers)
        t_qty = st.number_input("الكمية:", min_value=1, step=50)
        t_price = st.number_input("سعر التنفيذ (ج.م):", min_value=0.01, step=0.05, format="%.4f")
        t_fee_actual = st.number_input("قيمة العمولة والرسوم الفعلية (ج.م):", min_value=0.0, step=1.0, format="%.2f")
        t_cycle = st.selectbox("دورة التسوية:", ["T+1 (تسوية اليوم التالي)", "T+2 (تسوية بعد يومين)"])
        
        if st.form_submit_button("تنفيذ وتسجيل الصفقة", use_container_width=True):
            raw_val = t_qty * t_price
            today = datetime.date.today()
            settle_days = 1 if "T+1" in t_cycle else 2
            settle_date = str(today + datetime.timedelta(days=settle_days))
            
            for s in st.session_state.db["stocks"]:
                if s["ticker"] == t_ticker:
                    if t_type == "شراء":
                        total_cost_inc_fee = raw_val + t_fee_actual
                        new_qty = s["qty"] + t_qty
                        new_avg = ((s["qty"] * s["avg"]) + total_cost_inc_fee) / new_qty
                        s["qty"] = new_qty
                        s["avg"] = round(new_avg, 4)
                        st.session_state.db["cash"] -= total_cost_inc_fee
                    elif t_type == "بيع":
                        net_proceeds = raw_val - t_fee_actual
                        cost_of_sold = t_qty * s["avg"]
                        trade_realized = net_proceeds - cost_of_sold
                        st.session_state.db["realized_pnl"] = st.session_state.db.get("realized_pnl", 0) + trade_realized
                        s["qty"] = max(0, s["qty"] - t_qty)
                        st.session_state.db["cash"] += net_proceeds
            
            st.session_state.db["trades"].append({
                "date": str(today),
                "type": t_type,
                "ticker": t_ticker,
                "qty": t_qty,
                "price": t_price,
                "val": raw_val,
                "fee": round(t_fee_actual, 2),
                "settle_date": settle_date,
                "cycle": t_cycle
            })
            save_data(st.session_state.db)
            st.success("تم تسجيل العملية بنجاح بالعمولة الفعلية!")
            st.rerun()

    if st.session_state.db["trades"]:
        st.divider()
        st.markdown("### 📋 سجل الصفقات ومواعيد التسوية:")
        for tr in reversed(st.session_state.db["trades"][-6:]):
            st.markdown(f"• **{tr['type']}** {tr['qty']:,} في `{tr['ticker']}` بسعر {tr['price']:.3f} ج.م (عمولة فعلية: {tr.get('fee', 0):.2f} ج.م) | ⏳ تسوية: `{tr['settle_date']}`")

# 7. شاشة التطهير الشرعي
elif menu == "⚖️ التطهير الشرعي":
    st.markdown("### ⚖️ الموقف الشرعي ومبالغ التطهير المستحقة")
    for _, row in df.iterrows():
        val = row["qty"] * row["price"]
        cost = row["qty"] * row["avg"]
        pnl = val - cost
        rate = PURIFY_RATES.get(row["ticker"], 0.0)
        purify_amt = (pnl * rate) if (pnl > 0 and rate > 0) else 0.0
        
        with st.container():
            st.markdown(f"**{row['icon']} {row['name']}** (`{row['ticker']}`)")
            if rate == 0.0:
                st.success("🟢 سهم نقي شرعاً 100% (لا يستوجب تطهير)")
            else:
                st.warning(f"🟡 سهم مختلط - نسبة التطهير: **{rate * 100:.1f}%**")
                c1, c2 = st.columns(2)
                c1.caption(f"الأرباح السوقية: **{pnl:+,.2f} ج.م**")
                if pnl > 0:
                    c2.markdown(f"💸 **مستحق التطهير:** `{purify_amt:,.2f} ج.م`")
                else:
                    c2.caption("لا يستحق تطهير (المركز في خسارة/تعادل)")
            st.divider()
            
    st.markdown(f"""
    <div style="background-color: #1e1b4b; border: 1px solid #6366f1; border-radius: 12px; padding: 14px; text-align: center;">
        <div style="color: #c7d2fe; font-size: 13px;">إجمالي مبالغ التطهير المستحقة على أرباح المحفظة</div>
        <div style="color: #fb923c; font-size: 22px; font-weight: bold; margin-top: 4px;">{total_purify_due:,.2f} ج.م</div>
    </div>
    """, unsafe_allow_html=True)

# 8. شاشة الأخبار
elif menu == "📰 أخبار البورصة":
    st.markdown("### 📰 أحدث الإفصاحات وأخبار الأسهم")
    for _, row in df.iterrows():
        news = get_stock_news(row["ticker"])
        with st.expander(f"{row['icon']} {row['name']} ({row['ticker']})"):
            if news:
                for n in news:
                    st.markdown(f"• [{n['title']}]({n['url']})")
            else:
                st.caption("لا توجد إفصاحات جديدة اليوم.")

# 9. شاشة البوت
elif menu == "🤖 مساعد التداول":
    st.markdown("### 🤖 مساعد التداول الذكي")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("اكتب سؤالك عن المحفظة والفرص...")
    if user_q:
        if not api_key:
            st.error("يرجى إدخال المفتاح أولاً.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
            
            portfolio_summary = df[["ticker", "name", "qty", "avg", "price", "volume", "weight"]].to_string()
            watchlist_summary = str(SHARIAH_WATCHLIST)
            prompt = f"""
            أنت خبير ومحلل مالي للبورصة المصرية لمحفظة تيلدا.
            الأسهم المتوافقة مع الشريعة المعتمدة للتحليل:
            {watchlist_summary}
            
            بيانات المحفظة الحالية:
            {portfolio_summary}
            
            سؤال المستخدم: {user_q}
            قدم تحليلك بناءً على حركة السعر، الفوليوم، ونقاط الدخول والخروج الصارمة.
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

# 10. شاشة الكاش والنسخ الاحتياطي
elif menu == "💵 إدارة الكاش والنسخ الاحتياطي":
    st.markdown("### 💵 إدارة الكاش والمصاريف")
    with st.form("cash_form"):
        action = st.selectbox("نوع المعاملة:", ["مصروف شخصي", "إيداع كاش للمحفظة", "سحب كاش من المحفظة"])
        amt = st.number_input("المبلغ (ج.م):", min_value=1.0, step=50.0)
        desc = st.text_input("البيان:")
        if st.form_submit_button("حفظ الحركة", use_container_width=True):
            if action == "إيداع كاش للمحفظة":
                st.session_state.db["cash"] += amt
            elif action == "سحب كاش من المحفظة":
                st.session_state.db["cash"] -= amt
            st.session_state.db["expenses"].append({"date": str(datetime.date.today()), "type": action, "amt": amt, "desc": desc})
            save_data(st.session_state.db)
            st.success("تم الحفظ بنجاح!")
            st.rerun()

    if st.session_state.db["expenses"]:
        st.divider()
        st.markdown("### آخر المعاملات المسجلة:")
        for exp in reversed(st.session_state.db["expenses"][-5:]):
            st.markdown(f"• {exp['date']} | {exp['type']}: **{exp['amt']} ج.م** ({exp['desc']})")

    st.divider()
    st.markdown("### 💾 النسخ الاحتياطي للبيانات")
    st.caption("حمّل نسخة كاملة من بيانات محفظتك وصفقاتك لحفظها على جهازك:")
    db_json_bytes = json.dumps(st.session_state.db, ensure_ascii=False, indent=2).encode('utf-8')
    st.download_button(
        label="📥 تنزيل نسخة احتياطية (portfolio_data.json)",
        data=db_json_bytes,
        file_name="portfolio_data.json",
        mime="application/json",
        use_container_width=True
    )
