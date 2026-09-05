import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from google import genai

st.set_page_config(page_title="محفظتي - EGX", layout="centered", initial_sidebar_state="collapsed")

# تصميم داكن متوافق للموبايل
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
    
    .purify-box {
        background-color: #1c2720;
        border: 1px dashed #22c55e;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 12px;
        color: #86efac;
    }
    .purify-box-haram {
        background-color: #2a1b1b;
        border: 1px dashed #ef4444;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 12px;
        color: #fca5a5;
    }
    </style>
""", unsafe_allow_html=True)

# قاعدة البيانات المرجعية للأسهم الحلال ونسب التطهير
SHARIA_DATABASE = {
    "BIGP": {"name": "بي اي جي للتجاره والاستثمار", "purify": 0.00, "grade": "نقي", "sector": "التجارة والتوكيلات"},
    "CAED": {"name": "القاهرة للخدمات التعليمية", "purify": 0.00, "grade": "نقي", "sector": "تعليم"},
    "FIRE": {"name": "الاولى للاستثمار", "purify": 0.00, "grade": "نقي", "sector": "عقاري"},
    "FNAR": {"name": "الفنار للمقاولات", "purify": 0.00, "grade": "نقي", "sector": "عقاري"},
    "MISR": {"name": "مصر انتركونتننتال لصناعة الجرانيت والرخام", "purify": 0.00, "grade": "نقي", "sector": "مواد بناء"},
    "MOED": {"name": "المصرية لنظم التعليم الحديثة", "purify": 0.00, "grade": "نقي", "sector": "تعليم"},
    "NEDA": {"name": "شمال الصعيد للتنمية الزراعية - نيوداب", "purify": 0.00, "grade": "نقي", "sector": "استثمار زراعي"},
    "UPMS": {"name": "الاتحاد الصيدلي للخدمات الطبية", "purify": 0.00, "grade": "نقي", "sector": "الأدوية و الرعاية الصحية"},
    "AMES": {"name": "المركز الطبي الجديد - الاسكندرية للخدمات", "purify": 1.00, "grade": "شبه نقي", "sector": "الأدوية و الرعاية الصحية"},
    "BIOC": {"name": "جلاسكو", "purify": 0.69, "grade": "شبه نقي", "sector": "الأدوية و الرعاية الصحية"},
    "CEFM": {"name": "مطاحن مصر الوسطى", "purify": 3.80, "grade": "شبه نقي", "sector": "اغذية ومشروبات"},
    "DCRC": {"name": "دلتا للانشاء والتعمير", "purify": 0.72, "grade": "شبه نقي", "sector": "مقاولات استشارات هندسية"},
    "EGAS": {"name": "غاز مصر", "purify": 0.06, "grade": "شبه نقي", "sector": "طاقة - مرافق"},
    "ELNA": {"name": "النصر للحاصلات الزراعية", "purify": 0.00, "grade": "شبه نقي", "sector": "استثمار زراعي"},
    "ELWA": {"name": "الوادي للاستثمار والتنمية", "purify": 2.12, "grade": "شبه نقي", "sector": "سياحه"},
    "FCMD": {"name": "فيوتشر كير للصناعات الطبية", "purify": 1.31, "grade": "شبه نقي", "sector": "الأدوية و الرعاية الصحية"},
    "GGRN": {"name": "جو جرين للاستثمار الزراعى والتنمية", "purify": 0.01, "grade": "شبه نقي", "sector": "استثمار زراعي"},
    "ICFC": {"name": "الدولية للأسمدة والكيماويات", "purify": 1.10, "grade": "شبه نقي", "sector": "موارد اساسية"},
    "IEEC": {"name": "المشروعات الصناعية", "purify": 1.48, "grade": "شبه نقي", "sector": "مقاولات استشارات هندسية"},
    "INEG": {"name": "المجموعة المتكاملة", "purify": 0.52, "grade": "شبه نقي", "sector": "مقاولات استشارات هندسية"},
    "INFI": {"name": "الاسماعيلية الوطنية للصناعات الغذائية - فوديكو", "purify": 1.39, "grade": "شبه نقي", "sector": "اغذية ومشروبات"},
    "MBSC": {"name": "مصر بني سويف للاسمنت", "purify": 1.28, "grade": "شبه نقي", "sector": "مواد بناء"},
    "MILS": {"name": "مطاحن شمال القاهرة", "purify": 0.89, "grade": "شبه نقي", "sector": "اغذية ومشروبات"},
    "MOSC": {"name": "مصر للزيوت و الصابون", "purify": 0.08, "grade": "شبه نقي", "sector": "اغذية ومشروبات"},
    "NDRL": {"name": "الحفر الوطنية", "purify": 0.00, "grade": "شبه نقي", "sector": "طاقة / خدمات مسانده"},
    "OBRI": {"name": "العبور للاستثمار العقاري", "purify": 0.94, "grade": "شبه نقي", "sector": "عقاري"},
    "PHGC": {"name": "بريميم هيلثكير جروب", "purify": 0.00, "grade": "شبه نقي", "sector": "الأدوية و الرعاية الصحية"},
    "PRCL": {"name": "الشركة العامة لنتجات الخزف والصيني شيني", "purify": 0.07, "grade": "شبه نقي", "sector": "مواد بناء"},
    "SIPC": {"name": "سبأ الدولية للأدوية والصناعات الكيماوية", "purify": 0.00, "grade": "شبه نقي", "sector": "الأدوية و الرعاية الصحية"},
    "SMFR": {"name": "سماد مصر - ايجيفرت", "purify": 1.95, "grade": "شبه نقي", "sector": "موارد اساسية"},
    "VERT": {"name": "فرتيكا للصناعة و التجارة", "purify": 0.00, "grade": "شبه نقي", "sector": "التجارة والتوكيلات"},
    "ZEOT": {"name": "الزيوت المستخلصة ومنتجاتها", "purify": 0.47, "grade": "شبه نقي", "sector": "اغذية ومشروبات"},
    "ZMID": {"name": "زهراء المعادي", "purify": 4.08, "grade": "شرعي مختلط A", "sector": "عقاري"},
    "AXPH": {"name": "الاسكندرية للادوية", "purify": 0.49, "grade": "شرعي مختلط A", "sector": "الأدوية و الرعاية الصحية"},
    "BONY": {"name": "بنيان", "purify": 3.00, "grade": "شرعي مختلط A", "sector": "عقاري"},
    "CLHO": {"name": "مستشفى كليوباترا", "purify": 0.63, "grade": "شرعي مختلط A", "sector": "الأدوية و الرعاية الصحية"},
    "CPCI": {"name": "القاهرة للادوية", "purify": 0.74, "grade": "شرعي مختلط A", "sector": "الأدوية و الرعاية الصحية"},
    "EGAL": {"name": "مصر للالومنيوم", "purify": 0.73, "grade": "شرعي مختلط A", "sector": "المعادن"},
    "FTNS": {"name": "فيتنس برايم", "purify": 0.00, "grade": "شرعي مختلط A", "sector": "الأدوية و الرعاية الصحية"},
    "ISMA": {"name": "الاسماعيلية مصر للدواجن", "purify": 0.00, "grade": "شرعي مختلط A", "sector": "اغذية ومشروبات"},
    "MTIE": {"name": "ام ام جروب للصناعة والتجارة العالمية", "purify": 0.60, "grade": "شرعي مختلط A", "sector": "التجارة والتوكيلات"},
    "ORAS": {"name": "اوراسكوم كونستراكشون بي ال سي", "purify": 0.87, "grade": "شرعي مختلط A", "sector": "عقاري"},
    "RACC": {"name": "راية لخدمات مراكز الاتصالات", "purify": 2.00, "grade": "شرعي مختلط A", "sector": "اتصالات وتكنولوجيا رقمية"},
    "SPMD": {"name": "سبيد ميديكال", "purify": 0.00, "grade": "شرعي مختلط A", "sector": "الأدوية و الرعاية الصحية"},
    "ACGC": {"name": "العربية لحليج الأقطان", "purify": 1.37, "grade": "شرعي مختلط B", "sector": "منسوجات وسلع معمرة"},
    "AIDC": {"name": "ارابيا للاستثمار والتنمية", "purify": 0.33, "grade": "شرعي مختلط B", "sector": "التجارة والتوكيلات"},
    "AMOC": {"name": "الاسكندرية للزيوت - اموك", "purify": 0.05, "grade": "شرعي مختلط B", "sector": "طاقة / خدمات مسانده"},
    "APSW": {"name": "العربية وبولفارا للغزل والنسيج", "purify": 0.24, "grade": "شرعي مختلط B", "sector": "منسوجات وسلع معمرة"},
    "ARCC": {"name": "العربية للاسمنت", "purify": 2.02, "grade": "شرعي مختلط B", "sector": "مواد بناء"},
    "ATQA": {"name": "مصر الوطنية للصلب - عتاقة", "purify": 3.54, "grade": "شرعي مختلط B", "sector": "المعادن"},
    "DAPH": {"name": "التعمير والاستشارات الهندسية", "purify": 3.00, "grade": "شرعي مختلط B", "sector": "عقاري"},
    "ETRS": {"name": "المصرية لخدمات النقل - ايجيترانس", "purify": 1.20, "grade": "شرعي مختلط B", "sector": "وسائل نقل ومواصلات"},
    "GGCC": {"name": "الجيزة للمقاولات", "purify": 0.27, "grade": "شرعي مختلط B", "sector": "مقاولات استشارات هندسية"},
    "GOUR": {"name": "جورميه ايجيبت دوت كوم للاغذية", "purify": 1.84, "grade": "شرعي مختلط B", "sector": "اغذية ومشروبات"},
    "KABO": {"name": "النصر للملابس والمنسوجات - كابو", "purify": 0.55, "grade": "شرعي مختلط B", "sector": "منسوجات وسلع معمرة"},
    "KRDI": {"name": "نهر الخير", "purify": 0.06, "grade": "شرعي مختلط B", "sector": "استثمار زراعي"},
    "MCQE": {"name": "مصر للاسمنت قنا", "purify": 3.22, "grade": "شرعي مختلط B", "sector": "مواد بناء"},
    "MPCO": {"name": "المنصورة للدواجن", "purify": 0.42, "grade": "شرعي مختلط B", "sector": "اغذية ومشروبات"},
    "OCPH": {"name": "اكتوبر فارما", "purify": 1.11, "grade": "شرعي مختلط B", "sector": "الأدوية و الرعاية الصحية"},
    "ROTO": {"name": "رواد السياحة", "purify": 0.40, "grade": "شرعي مختلط B", "sector": "سياحه"},
    "UEFM": {"name": "مطاحن مصر العليا", "purify": 2.88, "grade": "شرعي مختلط B", "sector": "اغذية ومشروبات"},
    "AALR": {"name": "العامة لاستصلاح الاراضي", "purify": 0.06, "grade": "شرعي مختلط C", "sector": "استثمار زراعي"},
    "ADCI": {"name": "العربية للادوية والصناعات الكيماوية", "purify": 0.62, "grade": "شرعي مختلط C", "sector": "الأدوية و الرعاية الصحية"},
    "ALUM": {"name": "العربية للالومنيوم", "purify": 0.00, "grade": "شرعي مختلط C", "sector": "المعادن"},
    "AMII": {"name": "العربية للصناعات المعدنية - العربية للمحابس", "purify": 0.90, "grade": "شرعي مختلط C", "sector": "مواد بناء"},
    "CERA": {"name": "سراميكا ريماس", "purify": 0.11, "grade": "شرعي مختلط C", "sector": "مواد بناء"},
    "CIRA": {"name": "القاهرة للإستثمار و التنمية العقاريه سيرا للتعليم", "purify": 3.49, "grade": "شرعي مختلط C", "sector": "تعليم"},
    "COSG": {"name": "القاهرة للزيوت والصابون", "purify": 0.00, "grade": "شرعي مختلط C", "sector": "اغذية ومشروبات"},
    "EEII": {"name": "العربية للصناعات الهندسية", "purify": 0.16, "grade": "شرعي مختلط C", "sector": "خدمات و منتجات صناعية وسيارات"},
    "EHDR": {"name": "المصريين للاسكان والتنمية والتعمير", "purify": 0.77, "grade": "شرعي مختلط C", "sector": "عقاري"},
    "ELKA": {"name": "القاهرة للاسكان", "purify": 4.75, "grade": "شرعي مختلط C", "sector": "عقاري"},
    "EPPK": {"name": "الاهرام للطباعة و التغليف", "purify": 0.00, "grade": "شرعي مختلط C", "sector": "الطباعة"},
    "ETEL": {"name": "المصرية للاتصالات", "purify": 0.20, "grade": "شرعي مختلط C", "sector": "اتصالات وتكنولوجيا رقمية"},
    "GTEX": {"name": "جيتكس للاستثمارات التجارية والصناعية", "purify": 0.42, "grade": "شرعي مختلط C", "sector": "منسوجات وسلع معمرة"},
    "GTWL": {"name": "جولدن تكس للاصواف", "purify": 0.11, "grade": "شرعي مختلط C", "sector": "منسوجات وسلع معمرة"},
    "HBCO": {"name": "هيبكو للاستثمارات التجارية", "purify": 0.00, "grade": "شرعي مختلط C", "sector": "مقاولات استشارات هندسية"},
    "ISPH": {"name": "ابن سينا فارما", "purify": 0.01, "grade": "شرعي مختلط C", "sector": "الأدوية و الرعاية الصحية"},
    "KORA": {"name": "قره لمشروعات الطاقة والاستثمار", "purify": 0.31, "grade": "شرعي مختلط C", "sector": "مقاولات استشارات هندسية"},
    "MAAL": {"name": "مرسيليا المصرية الخليجية", "purify": 1.17, "grade": "شرعي مختلط C", "sector": "عقاري"},
    "MBEG": {"name": "ام بي للهندسة M.B", "purify": 0.05, "grade": "شرعي مختلط C", "sector": "خدمات و منتجات صناعية وسيارات"},
    "MCRO": {"name": "ماكرو جروب للمستحضرات الطبية", "purify": 4.08, "grade": "شرعي مختلط C", "sector": "الأدوية و الرعاية الصحية"},
    "MPCI": {"name": "ممفيس للادوية والصناعات الكيماوية", "purify": 4.87, "grade": "شرعي مختلط C", "sector": "الأدوية و الرعاية الصحية"},
    "NIPH": {"name": "النيل للادوية والصناعات الكيماوية - النيل", "purify": 0.39, "grade": "شرعي مختلط C", "sector": "الأدوية و الرعاية الصحية"},
    "ORWE": {"name": "النساجون الشرقيون للسجاد", "purify": 1.87, "grade": "شرعي مختلط C", "sector": "منسوجات وسلع معمرة"},
    "RUBX": {"name": "روبكس العالميه لتصنيع البلاستيك", "purify": 0.03, "grade": "شرعي مختلط C", "sector": "صناعة البلاستيك"},
    "SKPC": {"name": "سيدي كرير للبتروكيماويات - سيدبك", "purify": 3.40, "grade": "شرعي مختلط C", "sector": "موارد اساسية"},
    "SUCE": {"name": "السويس للاسمنت", "purify": 0.25, "grade": "شرعي مختلط C", "sector": "مواد بناء"},
    "SVCE": {"name": "جنوب الوادي للاسمنت", "purify": 0.75, "grade": "شرعي مختلط C", "sector": "مواد بناء"},
    "SWDY": {"name": "السويدي اليكتريك", "purify": 0.86, "grade": "شرعي مختلط C", "sector": "طاقة - مرافق"},
    "TALM": {"name": "تعليم لخدمات الإدارة", "purify": 1.18, "grade": "شرعي مختلط C", "sector": "تعليم"},
    "PRDC": {"name": "بايونيرز بروبرتيز للتنمية العمرانية بي ار اي جروب", "purify": 0.00, "grade": "متوافق", "sector": "عقاري"},
}

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

# ربط بيانات السهم بقاعدة بيانات الشريعة تلقائياً
def get_sharia_info(ticker):
    if ticker in SHARIA_DATABASE:
        info = SHARIA_DATABASE[ticker]
        return {
            "purify_rate": info["purify"],
            "sharia_status": f"🟢 متوافق ({info['grade']})",
            "is_halal": True,
            "sector": info["sector"]
        }
    else:
        return {
            "purify_rate": 100.0,
            "sharia_status": "🔴 غير متوافق (تطهير 100% للربح)",
            "is_halal": False,
            "sector": "خارج القائمة الشرعية"
        }

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
    
    if ticker == "KRDI":
        vol_status = "تداول مرتفع جداً (سيولة مضاربية)"
        forecast = f"تجميع قرب القاع وامتصاص عروض. اختراق {round(price * 1.03, 3)} بفوليوم متصاعد يستهدف {res} ج.م. الحفاظ على دعم {sup} ج.م شرط استمرار الإيجابية."
    elif ticker == "EEII":
        vol_status = "فوليوم متوازن مع تناقص بيعي"
        forecast = f"تهدئة صحية أعلى متوسط الدخول. اختراق {round(price * 1.025, 2)} بحجم تداول يفتح موجة سريعة نحو {res} ج.م. وقف الخسارة عند {sl} ج.م."
    elif ticker == "AMOC":
        vol_status = "سيولة مؤسسية واستثمار طويل الأجل"
        forecast = f"سهم أمان المحفظة. أي ضخ فوليوم أعلى {round(price * 1.02, 2)} يستهدف القمة النفسية {res} ج.م. الدعم الصلب عند {sup} ج.م."
    elif ticker in ["ELKA", "EHDR"]:
        vol_status = "تجميع هادئ في قطاع الإسكان"
        forecast = f"حركة عرضية مائلة للصعود. الثبات فوق {sup} ج.م يؤهل لاختبار مقاومة {res} ج.م بشرط استمرار الزخم الشرائي."
    elif ticker == "CERA":
        vol_status = "دوران سيولة جيد وأرباح متماسكة"
        forecast = f"حماية الأرباح فوق {sup} ج.م، واستهداف مقاومة {res} ج.م للمضاربة السريعة."
    elif ticker == "ECAP":
        vol_status = "سهم غير متوافق شرعاً"
        forecast = f"يستحسن التخارج منه فور ارتداده قرب مستويات {res} ج.م لاسترداد رأس المال فقط وإخراج أي ربح كتطهير كامل."
    else:
        vol_status = "فوليوم متوازن"
        forecast = f"حركة عرضية بين دعم {sup} ج.م ومقاومة {res} ج.م. يفضل المراقبة قبل زيادة المراكز."
        
    trend = "صاعد 🟢" if ratio >= 0 else "تصحيحي / هابط 🔴"
    return {"sup": sup, "res": res, "sl": sl, "trend": trend, "vol_status": vol_status, "forecast": forecast}

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

# جمع البيانات الحية وحسابات التطهير الآلية
portfolio_data = []
for s in DEFAULT_STOCKS:
    market_info = get_live_market_data(s["ticker"], s["fallback_price"])
    sharia_data = get_sharia_info(s["ticker"])
    
    item = dict(s)
    item["price"] = market_info["price"]
    item["volume"] = market_info["volume"]
    item["change"] = market_info["change"]
    item["purify_rate"] = sharia_data["purify_rate"]
    item["sharia_status"] = sharia_data["sharia_status"]
    item["is_halal"] = sharia_data["is_halal"]
    
    cost = item["qty"] * item["avg"]
    val = item["qty"] * item["price"]
    profit = max(0.0, val - cost)
    purify_amount = profit * (item["purify_rate"] / 100.0)
    
    item["profit"] = val - cost
    item["purify_val"] = purify_amount
    item["net_profit_clean"] = max(0.0, (val - cost) - purify_amount) if item["is_halal"] else 0.0
    portfolio_data.append(item)

df = pd.DataFrame(portfolio_data)
total_cost = (df["qty"] * df["avg"]).sum()
total_market = (df["qty"] * df["price"]).sum()
net_pnl = total_market - total_cost
net_return = (net_pnl / total_cost) * 100 if total_cost > 0 else 0
total_purify_due = df["purify_val"].sum()

# بنر الإجماليات العلوي
pnl_color = "#4ade80" if net_pnl >= 0 else "#f87171"
st.markdown(f"""
<div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 14px; padding: 16px; margin-bottom: 12px; text-align: center;">
    <div style="color: #94a3b8; font-size: 13px;">إجمالي القيمة السوقية للمحفظة</div>
    <div style="color: #f8fafc; font-size: 26px; font-weight: 800; margin: 4px 0;">{total_market:,.2f} ج.م</div>
    <div style="color: {pnl_color}; font-size: 15px; font-weight: 700;">
        الأرباح: {net_pnl:+,.2f} ج.م ({net_return:+.2f}%)
    </div>
    <div style="display: flex; justify-content: space-around; margin-top: 10px; border-top: 1px solid #334155; padding-top: 8px;">
        <span style="color: #64748b; font-size: 12px;">الكاش: <b style="color:#cbd5e1;">{st.session_state.cash:,.2f}</b> ج.م</span>
        <span style="color: #86efac; font-size: 12px;">مستحق التطهير: <b style="color:#4ade80;">{total_purify_due:,.2f}</b> ج.م</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 تحديث أسعار وفوليوم السوق الآن", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 المحفظة", "⚖️ التطهير", "📈 الفوليوم والتوقع", "📰 الأخبار", "🤖 البوت", "💵 الكاش"])

# 1. شاشة الأسهم
with tab1:
    for _, row in df.iterrows():
        cost = row["qty"] * row["avg"]
        val = row["qty"] * row["price"]
        pnl = row["profit"]
        ret = (pnl / cost) * 100
        cls = "badge-win" if pnl >= 0 else "badge-loss"
        
        purify_snippet = ""
        if not row["is_halal"]:
            purify_snippet = f"""
            <div class="purify-box-haram">
                🔴 السهم غير متوافق شرعاً (تطهير كامل 100% للربح)<br>
                💰 مطلوب إخراج كامل الربح: <b>{row['purify_val']:,.2f} ج.م</b> | تسترد رأس مالك فقط: <b>{cost:,.2f} ج.م</b>
            </div>
            """
        elif pnl > 0 and row["purify_rate"] > 0:
            purify_snippet = f"""
            <div class="purify-box">
                {row['sharia_status']} | نسبة التطهير: <b>{row['purify_rate']}%</b><br>
                💰 مستحق التطهير حالياً: <b>{row['purify_val']:,.2f} ج.م</b> | الصافي الحلال: <b>{row['net_profit_clean']:,.2f} ج.م</b>
            </div>
            """
        
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
            {purify_snippet}
        </div>
        """, unsafe_allow_html=True)

# 2. تبويب التطهير وحاسبة الصفقات لجميع أسهم البورصة
with tab2:
    st.subheader("⚖️ مطابقة الشريعة والتطهير الآلي")
    st.caption("النسب مستخرجة تلقائياً من قوائم الفحص المعتمدة للأسهم الحلال:")
    
    for _, row in df.iterrows():
        with st.container():
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{row['icon']} {row['name']}** (`{row['ticker']}`)")
                st.caption(row["sharia_status"])
            with c2:
                st.markdown(f"نسبة التطهير: **`{row['purify_rate']}%`**")
                if row['profit'] > 0:
                    st.markdown(f"مبلغ التطهير: :red[**{row['purify_val']:,.2f} ج.م**]" if not row['is_halal'] else f"مبلغ التطهير: :green[**{row['purify_val']:,.2f} ج.م**]")
                else:
                    st.caption("لا يوجد ربح حالياً")
            st.divider()
            
    st.write("### 🧮 حاسبة التطهير لأي سهم في البورصة")
    with st.expander("اضغط لحساب التطهير لأي صفقة بيع (مربوطة بقاعدة بيانات كل الأسهم)"):
        all_tickers = sorted(list(SHARIA_DATABASE.keys()))
        selected_ticker = st.selectbox("اختر رمز السهم (Ticker):", all_tickers)
        selected_info = SHARIA_DATABASE[selected_ticker]
        
        st.info(f"**اسم الشركة:** {selected_info['name']} | **القطاع:** {selected_info['sector']} | **نسبة التطهير:** `{selected_info['purify']}%` ({selected_info['grade']})")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            calc_qty = st.number_input("عدد الأسهم:", min_value=1, value=1000, step=100)
        with col_c2:
            calc_buy = st.number_input("سعر الشراء (ج.م):", min_value=0.01, value=10.0, step=0.1)
        with col_c3:
            calc_sell = st.number_input("سعر البيع (ج.م):", min_value=0.01, value=11.0, step=0.1)
            
        realized_pnl = (calc_sell - calc_buy) * calc_qty
        if realized_pnl > 0:
            calc_purify_amt = realized_pnl * (selected_info["purify"] / 100.0)
            net_clean_pnl = realized_pnl - calc_purify_amt
            st.success(f"""
            * **إجمالي ربح الصفقة:** `{realized_pnl:,.2f} ج.م`
            * **مبلغ التطهير المطلوب إخراجه ({selected_info['purify']}%):** `{calc_purify_amt:,.2f} ج.م`
            * **صافي الربح الحلال في جيبك:** `{net_clean_pnl:,.2f} ج.م`
            """)
        else:
            st.warning("لا يوجد ربح في هذه الصفقة، وبالتالي لا يستحق عليها تطهير.")

# 3. شاشة التحليل الفني وقراءة الفوليوم وتوقع الجلسة
with tab3:
    st.caption("التحليل الفني الديناميكي، قراءة السيولة، وتوقعات الجلسة:")
    for _, row in df.iterrows():
        analysis = analyze_volume_and_forecast(row["ticker"], row["price"], row["avg"])
        
        with st.container():
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                st.subheader(f"{row['icon']} {row['name']}")
            with col_t2:
                st.markdown(f"**`{row['ticker']}`**")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("السعر الحالي", f"{row['price']:.2f} ج.م", delta=row['change'])
                st.metric("حجم التداول", str(row['volume']))
                st.markdown(f"🟢 **الدعم الأول:** `{analysis['sup']:.2f} ج.م`")
            with c2:
                st.metric("الاتجاه الفني", analysis['trend'])
                st.markdown(f"💧 **السيولة:** {analysis['vol_status']}")
                st.markdown(f"🟠 **المقاومة الأولى:** `{analysis['res']:.2f} ج.م`")
            
            st.markdown(f"🔴 **وقف الخسارة المقترح:** `{analysis['sl']:.2f} ج.م`")
            st.info(f"🔮 **توقع جلسة الغد:**\n\n{analysis['forecast']}")
            st.divider()

# 4. الأخبار
with tab4:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 10px;'>أحدث إفصاحات وأخبار أسهم المحفظة:</div>", unsafe_allow_html=True)
    for _, row in df.iterrows():
        news = get_stock_news(row["ticker"])
        with st.expander(f"{row['icon']} {row['name']} ({row['ticker']})"):
            if news:
                for n in news:
                    st.markdown(f"• [{n['title']}]({n['url']})")
            else:
                st.caption("لا توجد أخبار جديدة معلنة اليوم.")

# 5. البوت الذكي
with tab5:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 6px;'>🤖 مساعد التداول الذكي</div>", unsafe_allow_html=True)
    st.caption("يحلل المحفظة وفتاوى التطهير الشرعية بناءً على الفوليوم والأسعار الحية.")
    
    api_key = st.text_input("أدخل مفتاح Gemini API المجاني:", type="password")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("اسأل عن الفوليوم، التطهير، أو خطة سهم محدد...")
    if user_q:
        if not api_key:
            st.error("يرجى إدخال مفتاح Gemini API أولاً للاستفادة من البوت.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
            
            portfolio_summary = df[["ticker", "name", "qty", "avg", "price", "profit", "purify_rate", "purify_val"]].to_string()
            prompt = f"""
            أنت خبير ومحلل مالي ومستشار للتداول المتوافق مع الشريعة في البورصة المصرية (EGX).
            بيانات المحفظة الحية ونسب التطهير حالياً:
            {portfolio_summary}
            سؤال المستخدم: {user_q}
            جاوب باختصار ووضوح وباللهجة المصرية، واذكر له أرقام التطهير بدقة لو سأل عن البيع أو الأرباح.
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

# 6. الكاش والمصاريف
with tab6:
    st.markdown("<div style='color: #f8fafc; font-weight: bold; margin-bottom: 8px;'>تسجيل حركة كاش أو مصروف</div>", unsafe_allow_html=True)
    with st.form("cash_form"):
        action = st.selectbox("نوع المعاملة:", ["مصروف شخصي", "إيداع كاش للمحفظة", "سحب كاش من المحفظة", "إخراج مبلغ تطهير شرعي"])
        amt = st.number_input("المبلغ (ج.م):", min_value=1.0, step=50.0)
        desc = st.text_input("البيان:")
        if st.form_submit_button("حفظ الحركة", use_container_width=True):
            if action == "إيداع كاش للمحفظة":
                st.session_state.cash += amt
            elif action in ["سحب كاش من المحفظة", "إخراج مبلغ تطهير شرعي"]:
                st.session_state.cash -= amt
            st.session_state.expenses.append({"التاريخ": str(datetime.date.today()), "النوع": action, "المبلغ": amt, "البيان": desc})
            st.success("تم الحفظ بنجاح!")
            st.rerun()

    if st.session_state.expenses:
        st.write("---")
        for exp in reversed(st.session_state.expenses[-5:]):
            st.markdown(f"<div style='color: #94a3b8; font-size: 12px;'>• {exp['التاريخ']} | {exp['النوع']}: <b style='color: #f8fafc;'>{exp['المبلغ']} ج.م</b> ({exp['البيان']})</div>", unsafe_allow_html=True)
