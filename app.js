// ===================================================
// تطبيق محفظة تيلدا - محرك الداش بورد العصري والواجهة التفاعلية
// ===================================================

const STORAGE_KEY = 'telda_portfolio_storage_v5';
const THEME_KEY = 'telda_theme_preference';
const GEMINI_KEY_STORAGE = 'telda_gemini_api_key';
const DEFAULT_GEMINI_KEY = 'AQ.Ab8RN6JjuV_LyMA6n54c5Y9mtwKpjvZLSrLawPKiRUEbliUs9Q';

let state = {
    stocks: JSON.parse(JSON.stringify(DEFAULT_STOCKS)),
    cash: 0.0,
    realized_pnl: 0.0,
    trades: [],
    expenses: [],
    payouts: []
};

let currentSelectedImage = null; // { dataUrl, base64, mimeType, name }

let messages = [
    { 
        role: "assistant", 
        content: "أهلاً بك يا غالي في محفظة تيلدا! 🚀\nأنا مساعد التداول الذكي الخاص بك (Gemini 3.6 Flash)، ومربوط مباشرة مع محفظتك.\n\n✨ **كيف أساعدك الآن:**\n1. **تسجيل صفقات الشراء والبيع تلقائياً:** اكتب لي مباشرة (مثال: `اشتريت 500 سهم فوري بسعر 7.20`) وسأقوم بتعديل المحفظة والكاش وتحديث الجداول فوراً.\n2. **قراءة لقطات الشاشة (Screenshots):** أرفق صورة لأمر الشراء أو البيع من تطبيق ثندر أو شركة السمسرة وسأستخرج بيانات الصفقة وأسجلها في ثانية واحدة!\n3. **تحليل المحفظة والسيولة والفوليوم:** اسألني عن أي سهم ومستهدفاته والموقف الشرعي من كاشف." 
    }
];

// لوحة ألوان متناسقة وهادئة لتوزيع أوزان المحفظة
const PALETTE = [
    "#10b981", "#059669", "#0d9488", "#14b8a6", 
    "#2dd4bf", "#0284c7", "#38bdf8", "#64748b", 
    "#475569", "#334155"
];

// معلومات كل تبويب لتحديث الشريط العلوي
const TAB_INFOS = {
    "tab-dashboard": { title: "لوحة التحكم الشاملة", desc: "نظرة عامة على أداء المحفظة، الأسعار اللحظية، والسيولة" },
    "tab-stocks": { title: "أسهم المحفظة بالتفصيل", desc: "بطاقات الأسعار اللحظية، الفوليوم، والشارتات الفنية" },
    "tab-recommendations": { title: "فرص وتوصيات البورصة", desc: "مسح فني لحظي للبورصة المصرية وأفضل الفرص المتوافقة مع كاشف" },
    "tab-partners": { title: "حسابات الشركاء وكشوفات الحساب", desc: "توزيع الأرباح الحلال، كشوفات الحساب للطباعة، وسجل السدادات" },
    "tab-targets": { title: "المستهدفات السعرية والتقدم", desc: "متابعة نسب الوصول للأهداف وجني الأرباح" },
    "tab-volume": { title: "الفوليوم والتحليل الفني", desc: "الدعوم والمقاومات، وقف الخسارة، وقراءة السيولة الحقيقية" },
    "tab-trades": { title: "تسجيل الصفقات والتسوية", desc: "إدخال عمليات الشراء والبيع واحتساب دورات T+1 و T+2" },
    "tab-shariah": { title: "التطهير الشرعي للمحفظة", desc: "المبالغ الواجب إخراجها طبقاً لنسب كاشف الرسمية" },
    "tab-kashef": { title: "دليل أسهم كاشف (80+)", desc: "القائمة الكاملة للأسهم الحلال المصرح بها في البورصة" },
    "tab-news": { title: "أخبار وإفصاحات الشركات", desc: "متابعة القرارات ونتائج الأعمال لشركات المحفظة" },
    "tab-ai": { title: "مساعد التداول الذكي AI", desc: "Gemini 3.6 Flash لتحليل الصفقات وقراءة الصور وتنفيذ الأوامر" },
    "tab-assistant": { title: "مساعد التداول الذكي AI", desc: "Gemini 3.6 Flash لتحليل الصفقات وقراءة الصور وتنفيذ الأوامر" },
    "tab-cash": { title: "إدارة الكاش والمصاريف", desc: "تسجيل الإيداعات والسحوبات والنسخ الاحتياطي للمحفظة" },
    "tab-tools": { title: "أدوات التداول الذكية والزكاة", desc: "حاسبة التبريد وتعديل متوسطات الشراء وحاسبة زكاة الأسهم الشرعية" }
};

// ==========================================
// إدارة الثيم (Theme Switcher: Dark / Light)
// ==========================================
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.innerHTML = theme === 'dark' 
            ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`
            : `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`;
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    showToast(next === 'dark' ? 'تم التبديل إلى الوضع الداكن' : 'تم التبديل إلى الوضع الفاتح');
}

// تهيئة وتحميل البيانات من localStorage
function initState() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            state = {
                stocks: Array.isArray(parsed.stocks) ? parsed.stocks : JSON.parse(JSON.stringify(DEFAULT_STOCKS)),
                cash: typeof parsed.cash === 'number' ? parsed.cash : 0.0,
                realized_pnl: typeof parsed.realized_pnl === 'number' ? parsed.realized_pnl : 0.0,
                trades: Array.isArray(parsed.trades) ? parsed.trades : [],
                expenses: Array.isArray(parsed.expenses) ? parsed.expenses : [],
                payouts: Array.isArray(parsed.payouts) ? parsed.payouts : [],
                customNews: Array.isArray(parsed.customNews) ? parsed.customNews : (JSON.parse(localStorage.getItem('telda_custom_news') || '[]'))
            };
        } catch (e) {
            console.error("خطأ في قراءة البيانات المحفوظة:", e);
            state.stocks = JSON.parse(JSON.stringify(DEFAULT_STOCKS));
        }
    } else {
        state = {
            stocks: JSON.parse(JSON.stringify(DEFAULT_STOCKS)),
            cash: 0.0,
            realized_pnl: 0.0,
            trades: [],
            expenses: [],
            payouts: [],
            customNews: JSON.parse(localStorage.getItem('telda_custom_news') || '[]')
        };
        saveState();
    }
    
    // التأكد من وجود كافة الأسهم مع الحفاظ على التحديثات اللحظية وعدم مسحها
    DEFAULT_STOCKS.forEach(def => {
        const s = state.stocks.find(item => item.ticker === def.ticker);
        if (s) {
            s.name = def.name;
            if (s.price === undefined) s.price = def.price;
            if (s.avg === undefined) s.avg = def.avg;
            if (s.qty === undefined) s.qty = def.qty;
            if (s.change === undefined) s.change = def.change;
            if (s.volume === undefined) s.volume = def.volume;
            if (s.target_price === undefined) s.target_price = def.target_price;
        } else {
            state.stocks.push(JSON.parse(JSON.stringify(def)));
        }
    });

    const savedKey = localStorage.getItem(GEMINI_KEY_STORAGE) || DEFAULT_GEMINI_KEY;
    localStorage.setItem(GEMINI_KEY_STORAGE, savedKey);
    const keyInput = document.getElementById('geminiApiKey');
    if (keyInput) keyInput.value = savedKey;

    setupChatListeners();
}

function resetToOfficialPortfolio() {
    state.stocks = JSON.parse(JSON.stringify(DEFAULT_STOCKS));
    saveState();
    showToast("تم تحديث أسهم المحفظة بالأرقام الدقيقة بنجاح! ✨");
}

function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    if (state.customNews) {
        localStorage.setItem('telda_custom_news', JSON.stringify(state.customNews));
    }
    renderAll();
}

// ==========================================
// محرك البورصة المصرية اللحظي والشارتات (Live Market Engine)
// ==========================================
let isRefreshingPrices = false;
let autoRefreshTimer = null;
let autoRefreshEnabled = true;
let lastMarketUpdateTime = null;

async function refreshMarketPrices(isAuto = false) {
    if (isRefreshingPrices) return;
    isRefreshingPrices = true;

    const refreshBtn = document.getElementById('refreshPricesBtn');
    if (refreshBtn) refreshBtn.classList.add('loading-spin');

    const statusText = document.getElementById('marketStatusText');
    if (statusText) statusText.textContent = "جاري الاتصال بالبورصة...";

    try {
        const tickers = state.stocks.map(s => `EGX:${s.ticker.toUpperCase()}`);
        const payload = {
            symbols: { tickers: tickers },
            columns: [
                "name", "close", "change", "Value.Traded", "volume", 
                "Recommend.All", "RSI", "high", "low", "open"
            ]
        };

        const res = await fetch('https://scanner.tradingview.com/egypt/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        let updatedCount = 0;
        if (data && Array.isArray(data.data)) {
            data.data.forEach(row => {
                const tvSymbol = row.s || "";
                const cleanTicker = tvSymbol.replace('EGX:', '').toUpperCase();
                const stock = state.stocks.find(s => s.ticker.toUpperCase() === cleanTicker);
                if (stock && row.d) {
                    const [name, close, change, valueTraded, volume, recAll, rsi, high, low, open] = row.d;

                    if (typeof close === 'number' && close > 0) stock.price = close;
                    if (typeof change === 'number') {
                        stock.change = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
                        stock.change_num = change;
                    }
                    if (typeof volume === 'number') {
                        stock.volume = Number(volume).toLocaleString();
                        stock.volume_raw = volume;
                    }
                    if (typeof valueTraded === 'number') stock.value_traded = valueTraded;
                    if (typeof high === 'number') stock.day_high = high;
                    if (typeof low === 'number') stock.day_low = low;
                    if (typeof open === 'number') stock.day_open = open;
                    if (typeof rsi === 'number') stock.rsi = Number(rsi.toFixed(1));

                    if (typeof recAll === 'number') {
                        stock.rec_score = recAll;
                        if (recAll >= 0.5) stock.recommendation = { text: "شراء قوي", type: "strong-buy", icon: "🚀", color: "emerald" };
                        else if (recAll >= 0.1) stock.recommendation = { text: "شراء", type: "buy", icon: "🟢", color: "emerald" };
                        else if (recAll > -0.1) stock.recommendation = { text: "حياد", type: "neutral", icon: "⚖️", color: "amber" };
                        else if (recAll > -0.5) stock.recommendation = { text: "بيع", type: "sell", icon: "🔴", color: "rose" };
                        else stock.recommendation = { text: "بيع قوي", type: "strong-sell", icon: "⚠️", color: "rose" };
                    }
                    stock.last_updated = new Date().toLocaleTimeString('ar-EG');
                    updatedCount++;
                }
            });
        }

        lastMarketUpdateTime = new Date();
        saveState();
        updateMarketStatusUI();
        if (!isAuto) {
            showToast(`تم تحديث أسعار ${updatedCount} أسهم وفوليوم التداول لحظياً! 🟢`);
        }
    } catch (err) {
        console.error("خطأ في جلب بيانات البورصة المصرية:", err);
        if (!isAuto) {
            showToast("تعذر جلب التحديث اللحظي للبورصة، تم الإبقاء على آخر أسعار مسجلة.");
        }
    } finally {
        isRefreshingPrices = false;
        if (refreshBtn) refreshBtn.classList.remove('loading-spin');
    }
}

function updateMarketStatusUI() {
    const statusText = document.getElementById('marketStatusText');
    const statusTime = document.getElementById('marketStatusTime');
    const dot = document.getElementById('livePulseDot');

    if (dot) dot.classList.remove('offline');
    if (statusText) statusText.textContent = "البورصة: لحظي ومباشر";
    if (statusTime && lastMarketUpdateTime) {
        statusTime.textContent = `(آخر تحديث: ${lastMarketUpdateTime.toLocaleTimeString('ar-EG')})`;
    }
}

function startAutoRefresh() {
    if (autoRefreshTimer) clearInterval(autoRefreshTimer);
    if (autoRefreshEnabled) {
        autoRefreshTimer = setInterval(() => {
            refreshMarketPrices(true);
        }, 30000);
    }
}

function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const label = document.getElementById('autoRefreshLabel');
    const icon = document.getElementById('autoRefreshIcon');

    if (autoRefreshEnabled) {
        if (label) label.textContent = "تحديث آلي: مفعل (30ث)";
        if (icon) icon.textContent = "⏱️";
        startAutoRefresh();
        showToast("تم تفعيل التحديث اللحظي التلقائي كل 30 ثانية ⏱️");
    } else {
        if (label) label.textContent = "تحديث آلي: متوقف";
        if (icon) icon.textContent = "⏸️";
        if (autoRefreshTimer) clearInterval(autoRefreshTimer);
        showToast("تم إيقاف التحديث التلقائي ⏸️");
    }
}

// مسح البورصة المصرية اللحظي لاستخراج أنشط الأسهم الشرعية
async function fetchLiveMarketScreener() {
    const container = document.getElementById('liveMarketScreenerContainer');
    if (!container) return;

    container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted);">جاري فحص 290+ سهم في البورصة المصرية...</div>`;

    try {
        const payload = {
            filter: [{ left: 'volume', operation: 'nempty' }],
            markets: ['egypt'],
            symbols: { query: { types: [] } },
            columns: ['name', 'description', 'close', 'change', 'volume', 'Value.Traded', 'Recommend.All', 'RSI'],
            sort: { sortBy: 'volume', sortOrder: 'desc' },
            range: [0, 40]
        };

        const res = await fetch('https://scanner.tradingview.com/egypt/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (data && Array.isArray(data.data)) {
            // تصفية الأسهم المتوافقة مع كاشف
            const matched = [];
            data.data.forEach(item => {
                const rawTicker = (item.s || "").replace('EGX:', '').toUpperCase();
                const d = item.d;
                if (!d) return;
                const isShariah = rawTicker in SHARIAH_ALL_STOCKS;
                matched.push({
                    ticker: rawTicker,
                    name: d[1] || rawTicker,
                    price: d[2] || 0,
                    change: d[3] || 0,
                    volume: d[4] || 0,
                    valTraded: d[5] || 0,
                    rec: d[6] || 0,
                    rsi: d[7] ? Number(d[7].toFixed(1)) : null,
                    shariah: isShariah ? SHARIAH_ALL_STOCKS[rawTicker] : null
                });
            });

            // فرز الأسهم: أسهم كاشف الشرعية أولاً ثم الأعلى فوليوم
            matched.sort((a, b) => {
                if (a.shariah && !b.shariah) return -1;
                if (!a.shariah && b.shariah) return 1;
                return b.volume - a.volume;
            });

            const topList = matched.slice(0, 10);

            container.innerHTML = `
                <div class="stocks-table-wrapper">
                    <table class="stocks-table">
                        <thead>
                            <tr>
                                <th>السهم</th>
                                <th>الرمز</th>
                                <th>الموقف الشرعي (كاشف)</th>
                                <th>السعر اللحظي</th>
                                <th>التغير</th>
                                <th>حجم التداول (الفوليوم)</th>
                                <th>مؤشر RSI</th>
                                <th>التوصية الفنية</th>
                                <th>إجراء</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${topList.map(s => {
                                const chgColor = s.change >= 0 ? 'text-emerald' : 'text-rose';
                                let recBadge = '';
                                if (s.rec >= 0.5) recBadge = `<span class="badge-rec strong-buy">🚀 شراء قوي</span>`;
                                else if (s.rec >= 0.1) recBadge = `<span class="badge-rec buy">🟢 شراء</span>`;
                                else if (s.rec > -0.1) recBadge = `<span class="badge-rec neutral">⚖️ حياد</span>`;
                                else recBadge = `<span class="badge-rec sell">🔴 بيع</span>`;

                                const shariahBadge = s.shariah 
                                    ? `<span class="badge-emerald" style="font-size: 10.5px;">✓ ${s.shariah.category}</span>`
                                    : `<span class="badge-rose" style="font-size: 10.5px;">غير مصنف بكاشف</span>`;

                                return `
                                    <tr>
                                        <td><b>${s.name}</b></td>
                                        <td><span class="ticker-badge">${s.ticker}</span></td>
                                        <td>${shariahBadge}</td>
                                        <td><b style="color: var(--primary);">${fmtPrice(s.price)} ج.م</b></td>
                                        <td class="${chgColor}"><b>${(s.change >= 0 ? '+' : '') + s.change.toFixed(2)}%</b></td>
                                        <td><b>${Number(s.volume).toLocaleString()}</b></td>
                                        <td><b>${s.rsi ? s.rsi : '—'}</b></td>
                                        <td>${recBadge}</td>
                                        <td>
                                            <button class="btn btn-glass" style="font-size: 11px; padding: 2px 7px;" onclick="openTradingViewChart('${s.ticker}', '${s.name}')">
                                                📈 شارت
                                            </button>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
    } catch (e) {
        console.error("خطأ في مسح السوق اللحظي:", e);
        container.innerHTML = `<div style="text-align: center; padding: 14px; color: var(--text-muted);">تعذر تحميل مسح السوق اللحظي حالياً.</div>`;
    }
}

// نافذة الشارت التفاعلي المباشر (TradingView Chart)
function openTradingViewChart(ticker, name) {
    const backdrop = document.getElementById('chartModalBackdrop');
    const titleEl = document.getElementById('chartModalTitle');
    const tickerEl = document.getElementById('chartModalTicker');
    const bodyEl = document.getElementById('chartModalBody');
    if (!backdrop || !bodyEl) return;

    const cleanTicker = (ticker || "").toUpperCase().trim();
    if (titleEl) titleEl.textContent = `الشارت اللحظي التفاعلي: ${name || cleanTicker}`;
    if (tickerEl) tickerEl.textContent = `EGX:${cleanTicker}`;

    const theme = document.documentElement.getAttribute('data-theme') || 'dark';

    bodyEl.innerHTML = `
        <iframe 
            src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=EGX%3A${cleanTicker}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=161618&studies=[%22RSI%40tv-basicstudies%22,%22MASimple%40tv-basicstudies%22]&theme=${theme}&style=1&timezone=Africa%2FCairo&locale=ar_AE" 
            width="100%" 
            height="100%" 
            frameborder="0" 
            allowtransparency="true" 
            scrolling="no" 
            allowfullscreen>
        </iframe>
    `;

    backdrop.classList.add('active');
}

function closeTradingViewModal() {
    const backdrop = document.getElementById('chartModalBackdrop');
    const bodyEl = document.getElementById('chartModalBody');
    if (backdrop) backdrop.classList.remove('active');
    if (bodyEl) bodyEl.innerHTML = '';
}

// =========================================================================
// مركز أخبار وإفصاحات الشركات المباشرة ونافذة السهم المنبثقة (Stock News Engine)
// =========================================================================

let activeNewsFilterTicker = 'all';
let activeNewsFilterCategory = 'all';
let currentNewsSearchQuery = '';
let currentModalNewsTicker = 'KRDI';

// استرجاع كافة الإفصاحات الرسمية والمخصصة مع الترتيب الزمني
function getStockDisclosures(ticker = null) {
    const custom = (state && Array.isArray(state.customNews)) ? state.customNews : [];
    const defaults = (typeof DEFAULT_STOCK_DISCLOSURES !== 'undefined') ? DEFAULT_STOCK_DISCLOSURES : [];
    let combined = [...custom, ...defaults];
    
    if (ticker && ticker !== 'all') {
        const clean = ticker.toUpperCase().trim();
        combined = combined.filter(item => (item.ticker || "").toUpperCase().trim() === clean);
    }
    
    return combined.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
}

// فتح نافذة أخبار وإفصاحات سهم محدد بنقرة واحدة
function openStockNewsModal(ticker, stockName) {
    const backdrop = document.getElementById('stockNewsModalBackdrop');
    if (!backdrop) return;
    
    currentModalNewsTicker = (ticker || 'EGX').toUpperCase().trim();
    const cleanName = stockName || currentModalNewsTicker;
    
    // البحث عن السهم في المحفظة لمعرفة سعره اللحظي وتغيره
    const s = (state.stocks || []).find(item => item.ticker.toUpperCase() === currentModalNewsTicker);
    const curPrice = s ? s.price : 0.0;
    const curChange = s ? (s.change || '0.0%') : '0.0%';
    
    const titleEl = document.getElementById('modalStockNewsTitle');
    const tickerEl = document.getElementById('modalStockNewsTicker');
    const priceBadge = document.getElementById('modalStockNewsPriceBadge');
    const chartBtn = document.getElementById('modalStockChartBtn');
    
    if (titleEl) titleEl.textContent = `أخبار وإفصاحات: ${cleanName}`;
    if (tickerEl) tickerEl.textContent = `EGX:${currentModalNewsTicker}`;
    if (priceBadge) {
        priceBadge.textContent = `${fmtPrice(curPrice)} ج.م (${curChange})`;
        priceBadge.className = curChange.startsWith('+') ? 'badge-emerald' : (curChange.startsWith('-') ? 'badge-rose' : 'screener-badge-hot');
    }
    if (chartBtn) {
        chartBtn.onclick = () => {
            closeStockNewsModal();
            openTradingViewChart(currentModalNewsTicker, cleanName);
        };
    }
    
    switchModalNewsTab('list');
    renderModalNewsList();
    loadTradingViewTimelineWidget(currentModalNewsTicker);
    fetchStockNewsLive(currentModalNewsTicker, cleanName);
    
    backdrop.classList.add('active');
}

function closeStockNewsModal() {
    const backdrop = document.getElementById('stockNewsModalBackdrop');
    if (backdrop) backdrop.classList.remove('active');
}

// نافذة تشغيل المحفظة على الموبايل عبر الواي فاي
function openMobileModal() {
    const backdrop = document.getElementById('mobileModalBackdrop');
    if (backdrop) backdrop.classList.add('active');
}

function closeMobileModal() {
    const backdrop = document.getElementById('mobileModalBackdrop');
    if (backdrop) backdrop.classList.remove('active');
}

function copyMobileUrl() {
    const input = document.getElementById('mobileUrlInput');
    if (input) {
        input.select();
        navigator.clipboard.writeText(input.value).then(() => {
            showToast('✅ تم نسخ رابط الموبايل إلى الحافظة!');
        }).catch(() => {
            showToast('الرابط: ' + input.value);
        });
    }
}

function switchModalNewsTab(tab) {
    const listBtn = document.getElementById('modalTabNewsListBtn');
    const tvBtn = document.getElementById('modalTabNewsTvBtn');
    const addBtn = document.getElementById('modalTabNewsAddBtn');
    
    const listView = document.getElementById('modalNewsListView');
    const tvView = document.getElementById('modalNewsTvView');
    const addView = document.getElementById('modalNewsAddView');
    
    if (listBtn) listBtn.classList.toggle('active', tab === 'list');
    if (tvBtn) tvBtn.classList.toggle('active', tab === 'tv');
    if (addBtn) addBtn.classList.toggle('active', tab === 'add');
    
    if (listView) listView.style.display = tab === 'list' ? 'flex' : 'none';
    if (tvView) tvView.style.display = tab === 'tv' ? 'block' : 'none';
    if (addView) addView.style.display = tab === 'add' ? 'block' : 'none';
}

function renderModalNewsList() {
    const container = document.getElementById('modalNewsListView');
    if (!container) return;
    
    const items = getStockDisclosures(currentModalNewsTicker);
    if (items.length === 0) {
        container.innerHTML = `
            <div style="background: var(--bg-subtle); border: 1px dashed var(--border-color); border-radius: 12px; padding: 30px; text-align: center; color: var(--text-muted);">
                <span style="font-size: 32px; display: block; margin-bottom: 8px;">📰</span>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">لا توجد إفصاحات مسجلة بعد لسهم ${currentModalNewsTicker}</div>
                <p style="font-size: 12px; margin-bottom: 12px;">يمكنك إضافة خبر أو إفصاح الآن عبر التبويب بالأعلى</p>
                <button class="btn btn-primary" onclick="switchModalNewsTab('add')" style="font-size: 12px; padding: 5px 12px;">➕ إضافة أول خبر لهذا السهم</button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = items.map(item => createNewsCardHtml(item, true)).join('');
}

// شاشة TradingView Timeline لأخبار السهم اللحظية
function loadTradingViewTimelineWidget(ticker) {
    const container = document.getElementById('modalNewsTvView');
    if (!container) return;
    const cleanTicker = (ticker || 'EGX').toUpperCase().trim();
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';

    container.innerHTML = `
        <div style="height: 100%; display: flex; flex-direction: column; gap: 8px;">
            <div style="font-size: 12px; color: var(--text-muted);">
                📡 تغطية حية لأخبار وأحداث <b>EGX:${cleanTicker}</b> وسوق المال المصري من TradingView:
            </div>
            <iframe 
                src="https://s.tradingview.com/embed-widget/timeline/?locale=ar_AE#%7B%22feedMode%22%3A%22symbol%22%2C%22symbol%22%3A%22EGX%3A${cleanTicker}%22%2C%22colorTheme%22%3A%22${theme}%22%2C%22isTransparent%22%3Afalse%2C%22displayMode%22%3A%22regular%22%2C%22width%22%3A%22100%25%22%2C%22height%22%3A%22440%22%2C%22utm_source%22%3A%22telda.wallet%22%7D" 
                width="100%" 
                height="440" 
                frameborder="0" 
                allowtransparency="true" 
                scrolling="no">
            </iframe>
        </div>
    `;
}

// جلب الأخبار اللحظية العاجلة عبر RSS في الخلفية
async function fetchStockNewsLive(ticker, stockName) {
    try {
        const query = encodeURIComponent(`سهم ${stockName || ticker} البورصة المصرية`);
        const rssUrl = `https://news.google.com/rss/search?q=${query}&hl=ar&gl=EG&ceid=EG:ar`;
        const apiUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssUrl)}`;
        const res = await fetch(apiUrl);
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === 'ok' && data.items && data.items.length > 0) {
            const liveItems = data.items.slice(0, 4).map((it, idx) => ({
                id: `live-${ticker}-${idx}`,
                ticker: ticker,
                stockName: stockName,
                title: it.title,
                category: 'live',
                date: it.pubDate ? it.pubDate.split(' ')[0] : 'اليوم',
                source: it.author || 'أخبار البورصة اللحظية',
                details: it.description ? it.description.replace(/<[^>]*>?/gm, '') : it.title,
                url: it.link,
                isLive: true
            }));
            
            if (currentModalNewsTicker === ticker) {
                const container = document.getElementById('modalNewsListView');
                if (container) {
                    const existing = getStockDisclosures(ticker);
                    const combined = [...liveItems, ...existing];
                    container.innerHTML = combined.map(item => createNewsCardHtml(item, true)).join('');
                }
            }
        }
    } catch(err) {
        // الاستمرار بالاعتماد على قاعدة البيانات الرسمية
    }
}

// توليد بطاقة الخبر بتصميم مالي موحد
function createNewsCardHtml(item, isModal = false) {
    const isCustom = item.isCustom || (item.id && String(item.id).startsWith('custom-'));
    
    let badgeClass = 'news-badge-board';
    let badgeLabel = '⚖️ قرار إدارة';
    if (item.category === 'earnings') {
        badgeClass = 'news-badge-earnings';
        badgeLabel = '📊 نتائج أعمال وقوائم';
    } else if (item.category === 'dividend') {
        badgeClass = 'news-badge-dividend';
        badgeLabel = '💰 توزيع أرباح وكوبونات';
    } else if (item.category === 'deal') {
        badgeClass = 'news-badge-deal';
        badgeLabel = '🤝 صفقة وتوسعات';
    } else if (isCustom) {
        badgeClass = 'news-badge-custom';
        badgeLabel = '📝 إفصاح مضاف منك';
    } else if (item.isLive) {
        badgeClass = 'news-badge-live';
        badgeLabel = '🔴 خبر عاجل';
    }

    const panelId = `news-panel-${item.id || Math.random().toString(36).substr(2, 9)}`;

    return `
        <div class="news-card-pro">
            <div class="news-card-header">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span class="news-badge ${badgeClass}">${badgeLabel}</span>
                    <span class="ticker-badge" style="cursor: pointer;" onclick="openStockNewsModal('${item.ticker}', '${item.stockName}')" title="عرض أخبار هذا السهم">${item.ticker}</span>
                    <b style="font-size: 12.5px; color: var(--text-primary);">${item.stockName || item.ticker}</b>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 11.5px; color: var(--text-muted);">📅 ${item.date || 'اليوم'}</span>
                    ${isCustom ? `<button class="btn btn-glass" style="font-size: 11px; padding: 2px 6px; color: var(--danger);" onclick="deleteCustomNews('${item.id}', ${isModal})" title="حذف هذا الخبر">🗑️</button>` : ''}
                </div>
            </div>
            
            <h3 class="news-card-title">${item.title}</h3>
            <p class="news-card-excerpt">${item.details ? (item.details.length > 160 ? item.details.slice(0, 160) + '...' : item.details) : ''}</p>
            
            <div class="news-card-footer">
                <span class="news-card-source">🏛️ المصدر: <b>${item.source || 'البورصة المصرية'}</b></span>
                <div style="display: flex; gap: 6px;">
                    ${item.url ? `<a href="${item.url}" target="_blank" class="btn btn-glass" style="font-size: 11px; padding: 3px 8px;">🔗 المصدر</a>` : ''}
                    <button class="btn btn-glass" style="font-size: 11px; padding: 3px 8px; color: var(--primary);" onclick="toggleNewsDetails('${panelId}')">
                        📖 التفاصيل الكاملة
                    </button>
                </div>
            </div>

            <div class="news-details-panel" id="${panelId}">
                <div style="margin-bottom: 6px; font-weight: 700; color: var(--text-primary);">نص الإفصاح الكامل:</div>
                <div style="white-space: pre-line;">${item.details || item.title}</div>
            </div>
        </div>
    `;
}

// عرض وتحديث تبويب الأخبار العام
function renderNewsTab(selectedTicker = null) {
    if (selectedTicker !== null) activeNewsFilterTicker = selectedTicker;
    
    // 1. توليد أزرار فلترة الأسهم (Stock Chips)
    const chipsBar = document.getElementById('newsStockChipsBar');
    if (chipsBar) {
        const allDisclosures = getStockDisclosures();
        const portfolioStocks = state.stocks || [];
        
        let chipsHtml = `
            <button class="stock-chip ${activeNewsFilterTicker === 'all' ? 'active' : ''}" onclick="selectNewsStockFilter('all')">
                📌 جميع الأسهم (${allDisclosures.length})
            </button>
        `;
        
        portfolioStocks.forEach(s => {
            const count = allDisclosures.filter(d => (d.ticker || '').toUpperCase() === s.ticker.toUpperCase()).length;
            chipsHtml += `
                <button class="stock-chip ${activeNewsFilterTicker === s.ticker ? 'active' : ''}" onclick="selectNewsStockFilter('${s.ticker}')">
                    ${s.name} (${s.ticker}) ${count > 0 ? `<span class="badge-rec neutral" style="font-size: 10px; padding: 1px 5px;">${count}</span>` : ''}
                </button>
            `;
        });
        
        chipsBar.innerHTML = chipsHtml;
    }
    
    // 2. تحديث قائمة اختيار السهم في نموذج الإضافة
    const stockSelect = document.getElementById('newsStockSelect');
    if (stockSelect && stockSelect.children.length === 0) {
        stockSelect.innerHTML = (state.stocks || []).map(s => `
            <option value="${s.ticker}">${s.name} (${s.ticker})</option>
        `).join('');
    }
    
    const dateInput = document.getElementById('newsDateInput');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    
    // 3. إحصائيات الأخبار
    const allItems = getStockDisclosures(activeNewsFilterTicker);
    const statTotal = document.getElementById('statTotalNews');
    const statEarnings = document.getElementById('statEarningsNews');
    const statDividends = document.getElementById('statDividendsNews');
    const statCustom = document.getElementById('statCustomNews');
    
    if (statTotal) statTotal.textContent = allItems.length;
    if (statEarnings) statEarnings.textContent = allItems.filter(d => d.category === 'earnings').length;
    if (statDividends) statDividends.textContent = allItems.filter(d => d.category === 'dividend').length;
    if (statCustom) statCustom.textContent = allItems.filter(d => d.isCustom || (d.id && String(d.id).startsWith('custom-'))).length;
    
    // 4. تصفية وعرض البطاقات
    const container = document.getElementById('newsContainer');
    if (!container) return;
    
    let filtered = allItems;
    if (activeNewsFilterCategory !== 'all') {
        filtered = filtered.filter(d => d.category === activeNewsFilterCategory || (activeNewsFilterCategory === 'custom' && (d.isCustom || (d.id && String(d.id).startsWith('custom-')))));
    }
    
    if (currentNewsSearchQuery) {
        const q = currentNewsSearchQuery.toLowerCase();
        filtered = filtered.filter(d => 
            (d.title || '').toLowerCase().includes(q) ||
            (d.details || '').toLowerCase().includes(q) ||
            (d.stockName || '').toLowerCase().includes(q) ||
            (d.ticker || '').toLowerCase().includes(q)
        );
    }
    
    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 12px; padding: 40px; text-align: center; color: var(--text-muted);">
                <span style="font-size: 36px; display: block; margin-bottom: 10px;">📰</span>
                <div style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 5px;">لا توجد إفصاحات مطابقة لخيارات الفلترة الحالية</div>
                <p style="font-size: 12.5px; margin-bottom: 16px;">يمكنك إضافة إفصاح جديد أو خبر للسهم بنفسك مباشرة بالضغط على الزر أدناه</p>
                <button class="btn btn-primary" onclick="toggleAddNewsForm()" style="font-size: 12px; padding: 6px 14px;">➕ إضافة إفصاح الآن</button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filtered.map(item => createNewsCardHtml(item)).join('');
}

// معالجة نموذج إضافة خبر مخصص من تبويب الأخبار
function handleCustomNewsSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const stockTicker = document.getElementById('newsStockSelect')?.value || 'KRDI';
    const s = (state.stocks || []).find(item => item.ticker === stockTicker);
    const stockName = s ? s.name : stockTicker;
    const category = document.getElementById('newsCategorySelect')?.value || 'custom';
    const source = document.getElementById('newsSourceInput')?.value || 'إفصاح رسمي';
    const date = document.getElementById('newsDateInput')?.value || new Date().toISOString().split('T')[0];
    const title = document.getElementById('newsTitleInput')?.value || '';
    const details = document.getElementById('newsDetailsInput')?.value || '';
    
    if (!title.trim()) {
        showToast('يرجى إدخال عنوان الإفصاح');
        return;
    }
    
    const newEntry = {
        id: `custom-${Date.now()}`,
        ticker: stockTicker,
        stockName: stockName,
        category: category,
        source: source,
        date: date,
        title: title,
        details: details,
        isCustom: true
    };
    
    if (!state.customNews) state.customNews = [];
    state.customNews.unshift(newEntry);
    localStorage.setItem('telda_custom_news', JSON.stringify(state.customNews));
    
    const form = document.getElementById('customNewsForm');
    if (form) form.reset();
    toggleAddNewsForm();
    renderNewsTab(stockTicker);
    showToast(`✅ تم إضافة الإفصاح لسهم ${stockName} بنجاح!`);
}

// معالجة إضافة خبر من داخل نافذة السهم المنبثقة
function handleModalAddNewsSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const s = (state.stocks || []).find(item => item.ticker === currentModalNewsTicker);
    const stockName = s ? s.name : currentModalNewsTicker;
    const category = document.getElementById('modalAddCategory')?.value || 'custom';
    const source = document.getElementById('modalAddSource')?.value || 'إفصاح رسمي';
    const title = document.getElementById('modalAddTitle')?.value || '';
    const details = document.getElementById('modalAddDetails')?.value || '';
    const date = new Date().toISOString().split('T')[0];

    if (!title.trim()) return;

    const newEntry = {
        id: `custom-${Date.now()}`,
        ticker: currentModalNewsTicker,
        stockName: stockName,
        category: category,
        source: source,
        date: date,
        title: title,
        details: details,
        isCustom: true
    };

    if (!state.customNews) state.customNews = [];
    state.customNews.unshift(newEntry);
    localStorage.setItem('telda_custom_news', JSON.stringify(state.customNews));

    const form = document.getElementById('modalAddNewsForm');
    if (form) form.reset();
    switchModalNewsTab('list');
    renderModalNewsList();
    renderNewsTab(currentModalNewsTicker);
    showToast(`✅ تم حفظ الإفصاح لسهم ${stockName} بنجاح!`);
}

// حذف خبر مضاف من المستخدم
function deleteCustomNews(id, isModal = false) {
    if (!confirm('هل أنت متأكد من حذف هذا الخبر/الإفصاح؟')) return;
    if (!state.customNews) return;
    state.customNews = state.customNews.filter(item => String(item.id) !== String(id));
    localStorage.setItem('telda_custom_news', JSON.stringify(state.customNews));
    if (isModal) renderModalNewsList();
    renderNewsTab();
    showToast('تم حذف الخبر بنجاح');
}

function toggleAddNewsForm() {
    const card = document.getElementById('addNewsFormCard');
    if (card) card.style.display = card.style.display === 'none' ? 'block' : 'none';
}

function toggleNewsDetails(id) {
    const panel = document.getElementById(id);
    if (panel) panel.classList.toggle('open');
}

function selectNewsStockFilter(ticker) {
    activeNewsFilterTicker = ticker;
    renderNewsTab();
}

function filterNewsCategory(cat, btn) {
    activeNewsFilterCategory = cat;
    document.querySelectorAll('#newsCategoryFilterPills .news-nav-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderNewsTab();
}

function handleNewsSearch(query) {
    currentNewsSearchQuery = query;
    renderNewsTab();
}



// ==========================================
// كشوفات حساب الشركاء وسجل التوزيعات الفعلية
// ==========================================
function renderPartnerStatement() {
    const container = document.getElementById('partnerStatementContainer');
    const select = document.getElementById('statementPartnerSelect');
    if (!container || !select) return;

    const pName = select.value || "الأم";
    const partner = PARTNERS.find(p => p.name === pName || p.name.includes(pName));
    if (!partner) return;

    const metrics = calculatePortfolioMetrics();
    const grossProfit = metrics.netPnl + state.realized_pnl;

    // حالة كشف حساب مدير المحفظة (كريم)
    if (partner.isManager || partner.capital === 0) {
        const partnerPayouts = (state.payouts || []).filter(pay => pay.partner === partner.name || pay.partner.includes(partner.name));
        const totalPaidOut = partnerPayouts.reduce((acc, pay) => acc + pay.amount, 0);

        container.innerHTML = `
            <div class="statement-card" id="printablePartnerStatement">
                <div class="statement-header">
                    <div>
                        <div class="statement-title">💼 كشف حساب وإشراف الإدارة: ${partner.name}</div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                            تاريخ الإصدار: ${new Date().toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' })} | محفظة تيلدا للأسهم
                        </div>
                    </div>
                    <div class="statement-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3);">
                        🎖️ مدير ومسؤول المحفظة
                    </div>
                </div>

                <table class="statement-table">
                    <thead>
                        <tr>
                            <th>البند الإداري والمالي</th>
                            <th>المبلغ / المؤشر</th>
                            <th>البيان والتفاصيل</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>الصفة والدور</b></td>
                            <td><b style="color: var(--primary);">مدير المحفظة (Portfolio Manager)</b></td>
                            <td>إدارة وتحليل الصفقات الفنية ومتابعة السيولة والتوزيعات</td>
                        </tr>
                        <tr>
                            <td>إجمالي القيمة السوقية للمحفظة تحت الإدارة</td>
                            <td><b style="color: var(--text-primary); font-size: 15px;">${fmtNum(metrics.totalMarket)} ج.م</b></td>
                            <td>إجمالي قيمة الأسهم بسعر البورصة اللحظي</td>
                        </tr>
                        <tr>
                            <td>إجمالي الأرباح الكلية المحققة للمحفظة</td>
                            <td class="${grossProfit >= 0 ? 'text-emerald' : 'text-rose'}"><b style="font-size: 15px;">${fmtSign(grossProfit)} ج.م</b></td>
                            <td>الأرباح الدفترية اللحظية + الأرباح المحققة السابقة</td>
                        </tr>
                        <tr>
                            <td>صافي الأرباح الحلال للتوزيع للشركاء</td>
                            <td class="${(grossProfit - metrics.totalPurifyDue) >= 0 ? 'text-emerald' : 'text-rose'}"><b style="font-size: 15px;">${fmtSign(grossProfit - metrics.totalPurifyDue)} ج.م</b></td>
                            <td>بعد تجنيب مستقطعات التطهير الشرعي (${fmtNum(metrics.totalPurifyDue)} ج.م)</td>
                        </tr>
                        <tr style="background: var(--bg-subtle);">
                            <td><b>إجمالي المسحوبات والأتعاب المسددة</b></td>
                            <td class="text-amber"><b style="font-size: 16px;">${fmtNum(totalPaidOut)} ج.م</b></td>
                            <td>مجموع ما تم تسجيله وسداده لمدير المحفظة (${partnerPayouts.length} عمليات مسجلة)</td>
                        </tr>
                    </tbody>
                </table>

                <div style="margin-top: 14px; font-size: 11.5px; color: var(--text-muted); line-height: 1.6;">
                    * تقرير رسمي صادر من محفظة تيلدا يوضح مؤشرات الأداء الإداري والمالي والمبالغ المسددة لمدير المحفظة.
                </div>
            </div>
        `;
        return;
    }

    const totalPartnerCapital = PARTNERS.filter(p => !p.isManager).reduce((sum, p) => sum + p.capital, 0);
    const ratio = totalPartnerCapital > 0 ? (partner.capital / totalPartnerCapital) : 0;
    const sharePct = (ratio * 100).toFixed(1);

    const partnerGrossProfit = grossProfit * ratio;
    const partnerPurifyDeduction = metrics.totalPurifyDue * ratio;
    const partnerNetProfit = partnerGrossProfit > 0 
        ? Math.max(0.0, partnerGrossProfit - partnerPurifyDeduction) 
        : (partnerGrossProfit - partnerPurifyDeduction);

    // حساب التوزيعات النقدية المسددة لهذا الشريك
    const partnerPayouts = (state.payouts || []).filter(pay => pay.partner === pName);
    const totalPaidOut = partnerPayouts.reduce((acc, pay) => acc + pay.amount, 0);
    const netCurrentBalance = partner.capital + partnerNetProfit - totalPaidOut;

    container.innerHTML = `
        <div class="statement-card" id="printablePartnerStatement">
            <div class="statement-header">
                <div>
                    <div class="statement-title">💼 كشف حساب استثماري رسمي: ${partner.name}</div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                        تاريخ الإصدار: ${new Date().toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' })} | محفظة تيلدا للأسهم
                    </div>
                </div>
                <div class="statement-badge">
                    نسبة الشراكة: ${sharePct}%
                </div>
            </div>

            <table class="statement-table">
                <thead>
                    <tr>
                        <th>البند المالي</th>
                        <th>المبلغ (ج.م)</th>
                        <th>ملاحظات وتفاصيل البند</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>رأس المال الأصلي المودع</b></td>
                        <td><b style="color: var(--text-primary);">${fmtNum(partner.capital)} ج.م</b></td>
                        <td>رأس المال الأساسي المسجل في المحفظة</td>
                    </tr>
                    <tr>
                        <td>حصة الشريك من إجمالي الأرباح الكلية</td>
                        <td class="${partnerGrossProfit >= 0 ? 'text-emerald' : 'text-rose'}"><b>${fmtSign(partnerGrossProfit)} ج.م</b></td>
                        <td>طبقاً لنسبة مساهمة رأس المال (${sharePct}%)</td>
                    </tr>
                    <tr>
                        <td>مستقطع التطهير الشرعي (كاشف)</td>
                        <td class="text-amber"><b>-${fmtNum(partnerPurifyDeduction)} ج.م</b></td>
                        <td>يُجنب للصدقات تطهيراً لأسهم كاشف المختلطة</td>
                    </tr>
                    <tr style="background: var(--bg-subtle);">
                        <td><b>صافي الأرباح الحلال المستحقة</b></td>
                        <td class="${partnerNetProfit >= 0 ? 'text-emerald' : 'text-rose'}"><b style="font-size: 15px;">${fmtSign(partnerNetProfit)} ج.م</b></td>
                        <td>الأرباح الحلال الصافية الجاهزة للتوزيع</td>
                    </tr>
                    <tr>
                        <td>إجمالي السدادات والتوزيعات السابقة</td>
                        <td class="text-rose"><b>-${fmtNum(totalPaidOut)} ج.م</b></td>
                        <td>مبالغ نقدية تم تحويلها للشريك فعلياً (${partnerPayouts.length} عمليات)</td>
                    </tr>
                    <tr style="background: var(--primary-subtle); border-top: 2px solid var(--primary);">
                        <td><b style="color: var(--primary); font-size: 15px;">صافي الرصيد المستحق للشريك حالياً</b></td>
                        <td><b style="color: var(--primary); font-size: 18px;">${fmtNum(netCurrentBalance)} ج.م</b></td>
                        <td><b>(رأس المال + صافي الأرباح - المسدد)</b></td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top: 14px; font-size: 11.5px; color: var(--text-muted); line-height: 1.6;">
                * تم إعداد هذا التقرير آلياً عبر نظام محفظة تيلدا بناءً على الأسعار اللحظية وقواعد التطهير الشرعي المعتمدة.
            </div>
        </div>
    `;
}

function printPartnerStatement() {
    renderPartnerStatement();
    setTimeout(() => {
        window.print();
    }, 200);
}

function handlePayoutSubmit(e) {
    e.preventDefault();
    const partner = document.getElementById('payoutPartner').value;
    const amount = parseFloat(document.getElementById('payoutAmount').value);
    const notes = document.getElementById('payoutNotes').value;

    if (isNaN(amount) || amount <= 0) {
        alert("يرجى إدخال مبلغ صحيح.");
        return;
    }

    if (!state.payouts) state.payouts = [];
    const newPayout = {
        id: Date.now().toString(),
        date: new Date().toISOString().split('T')[0],
        partner,
        amount,
        notes: notes || "سداد أرباح نقدية"
    };

    state.payouts.push(newPayout);
    saveState();
    e.target.reset();
    renderPayoutsTable();
    renderPartnerStatement();
    showToast(`تم تسجيل سداد ${fmtNum(amount)} ج.م للشريك (${partner}) بنجاح! 💰`);
}

function renderPayoutsTable() {
    const container = document.getElementById('payoutsTableContainer');
    if (!container) return;

    if (!state.payouts || state.payouts.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 10px; font-size: 12.5px;">لا توجد سدادات أرباح مسجلة بعد.</div>`;
        return;
    }

    container.innerHTML = `
        <div class="stocks-table-wrapper" style="margin-top: 10px;">
            <table class="stocks-table">
                <thead>
                    <tr>
                        <th>التاريخ</th>
                        <th>الشريك</th>
                        <th>المبلغ المسدد</th>
                        <th>البيان / ملاحظات</th>
                        <th>حذف</th>
                    </tr>
                </thead>
                <tbody>
                    ${[...state.payouts].reverse().map(p => `
                        <tr>
                            <td>${p.date}</td>
                            <td><b>${p.partner}</b></td>
                            <td class="text-rose"><b>${fmtNum(p.amount)} ج.م</b></td>
                            <td>${p.notes || '—'}</td>
                            <td>
                                <button class="btn btn-glass" style="color: var(--danger); font-size: 11px; padding: 2px 6px;" onclick="deletePayout('${p.id}')">✕</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function deletePayout(id) {
    if (!confirm("هل تريد حذف هذا السداد؟")) return;
    state.payouts = (state.payouts || []).filter(p => p.id !== id);
    saveState();
    renderPayoutsTable();
    renderPartnerStatement();
    showToast("تم حذف عملية السداد بنجاح.");
}

// ==========================================
// أدوات التداول الذكية: حاسبة التبريد (DCA) وحاسبة الزكاة
// ==========================================
function populateDcaPickers() {
    const select = document.getElementById('dcaStockSelect');
    if (!select) return;

    select.innerHTML = '<option value="">-- إدخال يدوي مخصص --</option>' + 
        state.stocks.map(s => `<option value="${s.ticker}">${s.name} (${s.ticker}) - سعر: ${s.price} ج.م</option>`).join('');
}

function populateDcaFromStock(ticker) {
    if (!ticker) return;
    const stock = state.stocks.find(s => s.ticker === ticker);
    if (!stock) return;

    const curQty = document.getElementById('dcaCurrentQty');
    const curAvg = document.getElementById('dcaCurrentAvg');
    const newPrice = document.getElementById('dcaNewPrice');

    if (curQty) curQty.value = stock.qty;
    if (curAvg) curAvg.value = stock.avg;
    if (newPrice) newPrice.value = (stock.price * 0.95).toFixed(2); // اقتراح تبريد عند نزول 5%

    calculateDca();
}

function calculateDca() {
    const q1 = parseFloat(document.getElementById('dcaCurrentQty')?.value) || 0;
    const a1 = parseFloat(document.getElementById('dcaCurrentAvg')?.value) || 0;
    const p2 = parseFloat(document.getElementById('dcaNewPrice')?.value) || 0;
    const q2 = parseFloat(document.getElementById('dcaNewQty')?.value) || 0;

    const totalSharesEl = document.getElementById('dcaTotalShares');
    const reqCashEl = document.getElementById('dcaRequiredCash');
    const redPctEl = document.getElementById('dcaReductionPct');
    const newAvgEl = document.getElementById('dcaNewAvg');

    if (q1 <= 0 || a1 <= 0 || p2 <= 0 || q2 <= 0) {
        if (totalSharesEl) totalSharesEl.textContent = "0 سهم";
        if (reqCashEl) reqCashEl.textContent = "0.00 ج.م";
        if (redPctEl) redPctEl.textContent = "0.0%";
        if (newAvgEl) newAvgEl.textContent = "0.00 ج.م";
        return;
    }

    const totalQ = q1 + q2;
    const totalCost = (q1 * a1) + (q2 * p2);
    const newAvg = totalCost / totalQ;
    const reqCash = q2 * p2;
    const redPct = a1 > 0 ? ((a1 - newAvg) / a1) * 100 : 0;

    if (totalSharesEl) totalSharesEl.textContent = `${Number(totalQ).toLocaleString()} سهم`;
    if (reqCashEl) reqCashEl.textContent = `${fmtNum(reqCash)} ج.م`;
    if (redPctEl) redPctEl.textContent = `${redPct > 0 ? '-' : ''}${Math.abs(redPct).toFixed(1)}%`;
    if (newAvgEl) newAvgEl.textContent = `${fmtNum(newAvg, 4)} ج.م`;
}

function calculateZakat() {
    const type = document.getElementById('zakatType')?.value || "trading";
    const goldPrice = parseFloat(document.getElementById('zakatGoldPrice')?.value) || 4800;

    const nisabEl = document.getElementById('zakatNisabVal');
    const baseEl = document.getElementById('zakatBaseVal');
    const statusEl = document.getElementById('zakatStatusVal');
    const dueEl = document.getElementById('zakatDueVal');

    const nisab = 85 * goldPrice; // نصاب 85 جرام ذهب
    const metrics = calculatePortfolioMetrics();

    let zakatBase = 0;
    let zakatRate = 0.025; // 2.5%

    if (type === "trading") {
        // عروض تجارة: القيمة السوقية للأسهم + الكاش المتاح
        zakatBase = metrics.totalMarket + state.cash;
        zakatRate = 0.025;
    } else if (type === "investor_div") {
        // مستثمر طويل الأجل (زكاة النماء على الأرباح 10%)
        const grossProfit = metrics.netPnl + state.realized_pnl;
        zakatBase = Math.max(0, grossProfit);
        zakatRate = 0.10; // 10%
    } else if (type === "investor_assets") {
        // مستثمر طويل الأجل (الموجودات الزكوية التقديرية 25% من القيمة السوقية)
        zakatBase = (metrics.totalMarket * 0.25) + state.cash;
        zakatRate = 0.025;
    }

    const isDue = zakatBase >= nisab;
    const zakatDue = isDue ? (zakatBase * zakatRate) : 0.0;

    if (nisabEl) nisabEl.textContent = `${fmtNum(nisab)} ج.م`;
    if (baseEl) baseEl.textContent = `${fmtNum(zakatBase)} ج.م`;
    if (statusEl) {
        if (isDue) {
            statusEl.className = "text-emerald";
            statusEl.textContent = "تجب الزكاة (تخطى النصاب الشرعي ✓)";
        } else {
            statusEl.className = "text-amber";
            statusEl.textContent = "لم تبلغ المحفظة النصاب الشرعي بعد";
        }
    }
    if (dueEl) dueEl.textContent = `${fmtNum(zakatDue)} ج.م`;
}

// تنسيق الأرقام والعملات
function fmtNum(val, decimals = 2) {
    if (val === undefined || val === null || isNaN(val)) return "0.00";
    return Number(val).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function fmtPrice(val) {
    if (val === undefined || val === null || isNaN(val)) return "0.00";
    const num = Number(val);
    const str = val.toString();
    const dec = str.includes('.') ? str.split('.')[1].length : 0;
    const decimals = Math.max(2, Math.min(dec, 4));
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function fmtSign(val, decimals = 2) {
    const s = fmtNum(val, decimals);
    return val > 0 ? `+${s}` : s;
}

// إشعار Toast سريع
function showToast(msg) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2500);
}

// فتح وإغلاق السايدبار في الموبايل
function toggleSidebar() {
    const sidebar = document.getElementById('appSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    }
}

// التبديل بين التبويبات وتحديث الرأس
function switchToTab(tabId) {
    const pane = document.getElementById(tabId);
    if (!pane) return;

    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));

    pane.classList.add('active');
    const navItem = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    if (navItem) navItem.classList.add('active');

    if (TAB_INFOS[tabId]) {
        const titleEl = document.getElementById('topNavTitle');
        const descEl = document.getElementById('topNavDesc');
        if (titleEl) titleEl.textContent = TAB_INFOS[tabId].title;
        if (descEl) descEl.textContent = TAB_INFOS[tabId].desc;
    }

    const sidebar = document.getElementById('appSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// التحليل الفني ومؤشرات الفوليوم
function analyzeVolumeAndForecast(ticker, price, avg) {
    const ratio = avg > 0 ? (price - avg) / avg : 0;
    const sup = Number((price * 0.96).toFixed(2));
    const res = Number((price * 1.05).toFixed(2));
    const sl = Number((price * 0.93).toFixed(2));

    let trigger = "السهم في منطقة استقرار";
    if (price <= sl * 1.01) {
        trigger = "تنبيه: السهم يلامس وقف الخسارة!";
    } else if (price >= res * 0.99) {
        trigger = "تنبيه: السهم يقترب من نقطة المقاومة وجني الأرباح!";
    } else if (price <= sup * 1.01) {
        trigger = "السهم يختبر منطقة الدعم الفني";
    }

    let vol_status = "تداول هادئ وترقب محفزات";
    let forecast = `نطاق عرضي متوقع بين دعم ${sup} ج.م ومقاومة ${res} ج.م.`;

    if (ticker === "KRDI") {
        vol_status = "سيولة مضاربية نشطة جداً";
        forecast = `تجميع وامتصاص عروض بيع. اختراق ${(price * 1.03).toFixed(3)} بفوليوم متصاعد يفتح الطريق نحو ${res} ج.م.`;
    } else if (ticker === "EEII") {
        vol_status = "تناقص بيعي وتماسك إيجابي";
        forecast = `تهدئة صحية أعلى متوسط الدخول. اختراق ${(price * 1.025).toFixed(2)} بفوليوم يستهدف ${res} ج.م.`;
    } else if (ticker === "AMOC") {
        vol_status = "سيولة مؤسسية متزنة";
        forecast = `سهم استثماري قيادي. الثبات أعلى ${sup} ج.م يؤهل لاختبار مستويات ${res} ج.م.`;
    } else if (["ELKA", "EHDR"].includes(ticker)) {
        vol_status = "تجميع هادئ داخل قطاع الإسكان";
        forecast = `حركة عرضية مائلة للصعود نحو ${res} ج.م بشرط البقاء أعلى ${sup} ج.م.`;
    } else if (ticker === "CERA") {
        vol_status = "أرباح جيدة وتماسك سعري";
        forecast = `حماية الأرباح فوق ${sup} ج.م واستهداف ${res} ج.م للمضاربة.`;
    }

    const trend = ratio >= 0 ? "صاعد" : "تصحيحي";
    return { sup, res, sl, trend, vol_status, forecast, trigger };
}

// حساب الموقف الشرعي والتطهير
function getShariahInfo(ticker, pnl) {
    const cleanTicker = (ticker || "").toUpperCase().trim();
    const isShariah = cleanTicker in SHARIAH_ALL_STOCKS;
    let rate = 1.0;
    let category = "غير متوافق مع الشريعة (تطهير 100%)";

    if (isShariah) {
        rate = SHARIAH_ALL_STOCKS[cleanTicker].rate;
        category = SHARIAH_ALL_STOCKS[cleanTicker].category;
    }

    const purifyAmt = (pnl > 0 && rate > 0) ? (pnl * rate) : 0.0;
    return { isShariah, rate, category, purifyAmt };
}

// الحسابات المالية الكلية للمحفظة
function calculatePortfolioMetrics() {
    let totalCost = 0.0;
    let totalMarket = 0.0;
    let totalPurifyDue = 0.0;

    const enrichedStocks = state.stocks.map((s, idx) => {
        const cost = s.qty * s.avg;
        const val = s.qty * s.price;
        const pnl = val - cost;
        const ret = cost > 0 ? (pnl / cost) * 100 : 0;
        
        totalCost += cost;
        totalMarket += val;

        const shariah = getShariahInfo(s.ticker, pnl);
        totalPurifyDue += shariah.purifyAmt;

        return {
            ...s,
            cost,
            val,
            pnl,
            ret,
            shariah,
            color: PALETTE[idx % PALETTE.length]
        };
    });

    const netPnl = totalMarket - totalCost;
    const netReturn = totalCost > 0 ? (netPnl / totalCost) * 100 : 0;

    enrichedStocks.forEach(s => {
        s.weight = totalMarket > 0 ? (s.val / totalMarket) * 100 : 0;
    });

    return {
        totalCost,
        totalMarket,
        netPnl,
        netReturn,
        totalPurifyDue,
        stocks: enrichedStocks
    };
}

// تحديث جميع مكونات الداش بورد
function renderAll() {
    const metrics = calculatePortfolioMetrics();
    
    renderKpiGrid(metrics);
    renderWeightBar(metrics);
    renderDashboardTables(metrics);
    
    renderStocksTab(metrics);
    renderPartnersTab(metrics);
    renderPartnerStatement();
    renderPayoutsTable();
    renderTargetsTab(metrics);
    renderVolumeTab(metrics);
    renderTradesTab();
    renderShariahTab(metrics);
    renderKashefDirectory();
    renderExpensesTab();
    populateSelectPickers();
    populateDcaPickers();
    calculateDca();
    calculateZakat();
    renderNewsTab();
}

// 1. كروت الـ KPI الرئيسية الستة بتوزيع منتظم (3 أعمدة × صفين) وبأيقونات SVG
function renderKpiGrid(m) {
    const grid = document.getElementById('kpiGrid');
    if (!grid) return;

    const pnlColor = m.netPnl >= 0 ? 'text-emerald' : 'text-rose';
    const realizedColor = state.realized_pnl >= 0 ? 'text-emerald' : 'text-rose';
    const totalPartnerCapital = PARTNERS.reduce((acc, p) => acc + p.capital, 0);

    grid.innerHTML = `
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">إجمالي القيمة السوقية</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                </div>
            </div>
            <div class="kpi-value">${fmtNum(m.totalMarket)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub ${pnlColor}">
                <span>${m.netPnl >= 0 ? '▲' : '▼'}</span>
                <span>الأرباح: ${fmtSign(m.netPnl)} ج.م</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">الأرباح الدفترية (غير المحققة)</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
                </div>
            </div>
            <div class="kpi-value ${pnlColor}">${fmtSign(m.netPnl)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub ${pnlColor}">
                <span>نسبة العائد:</span>
                <b>${fmtSign(m.netReturn)}%</b>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">الكاش المتاح للشراء</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>
                </div>
            </div>
            <div class="kpi-value text-primary-color">${fmtNum(state.cash)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub" style="color: var(--text-muted);">
                <span>جاهز للفرص واقتناص الصفقات</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">الأرباح المحققة الفعلية</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="m16.71 13.88.7.71-2.82 2.82"/></svg>
                </div>
            </div>
            <div class="kpi-value ${realizedColor}">${fmtSign(state.realized_pnl)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub" style="color: var(--text-muted);">
                <span>من واقع الصفقات المغلقة</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">مستحق التطهير الشرعي</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
                </div>
            </div>
            <div class="kpi-value text-amber">${fmtNum(m.totalPurifyDue)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub" style="color: var(--text-muted);">
                <span>تطهير أرباح الأسهم غير النقية</span>
            </div>
        </div>

        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">رأس مال الشركاء الأصلي</span>
                <div class="kpi-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </div>
            </div>
            <div class="kpi-value">${fmtNum(totalPartnerCapital)} <small style="font-size: 13px; font-weight: 500;">ج.م</small></div>
            <div class="kpi-sub" style="color: var(--text-muted);">
                <span>3 شركاء (الأم، محمود، نورا)</span>
            </div>
        </div>
    `;

    const sideCash = document.getElementById('sidebarCashVal');
    if (sideCash) sideCash.textContent = `${fmtNum(state.cash)} ج.م`;

    const dashPurify = document.getElementById('dashboardPurifyVal');
    if (dashPurify) dashPurify.textContent = `${fmtNum(m.totalPurifyDue)} ج.م`;
}

// 2. شريط الأوزان النسبية للأسهم
function renderWeightBar(m) {
    const segs = document.getElementById('weightSegments');
    const leg = document.getElementById('weightLegend');
    const totalValEl = document.getElementById('weightTotalVal');
    if (!segs || !leg) return;

    if (totalValEl) totalValEl.textContent = `القيمة الإجمالية: ${fmtNum(m.totalMarket)} ج.م`;

    segs.innerHTML = m.stocks.map(s => `
        <div class="weight-segment" style="width: ${s.weight}%; background-color: ${s.color};" title="${s.name} (${s.ticker}): ${s.weight.toFixed(1)}%"></div>
    `).join('');

    leg.innerHTML = m.stocks.map(s => `
        <div class="legend-item">
            <span class="legend-color" style="background-color: ${s.color};"></span>
            <span><b>${s.ticker}</b> (${s.weight.toFixed(1)}%)</span>
        </div>
    `).join('');
}

// 3. جداول وقوائم لوحة التحكم الشاملة
function renderDashboardTables(m) {
    const stocksTbody = document.getElementById('dashboardStocksTableBody');
    if (stocksTbody) {
        stocksTbody.innerHTML = m.stocks.map((s, idx) => {
            const pnlColor = s.pnl >= 0 ? 'text-emerald' : 'text-rose';
            const changeColor = s.change && s.change.startsWith('+') ? 'text-emerald' : (s.change && s.change.startsWith('-') ? 'text-rose' : '');
            
            let recBadge = '';
            if (s.recommendation) {
                recBadge = `<span class="badge-rec ${s.recommendation.type}">${s.recommendation.icon} ${s.recommendation.text}</span>`;
            } else {
                recBadge = `<span class="badge-rec neutral">⚖️ قيد الفحص</span>`;
            }

            return `
                <tr>
                    <td style="color: var(--text-muted); font-weight: 700; text-align: center;">${idx + 1}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <a href="javascript:void(0)" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" class="stock-news-link" title="اضغط لعرض كافة أخبار وإفصاحات السهم">
                                <b>${s.name}</b>
                            </a>
                        </div>
                        ${!s.shariah.isShariah ? '<div style="margin-top: 3px;"><span class="badge-rose" style="font-size: 10px; font-weight: 700; padding: 1px 6px;">غير متوافق (تطهير 100%)</span></div>' : ''}
                    </td>
                    <td><span class="ticker-badge" style="cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="عرض أخبار السهم">${s.ticker}</span></td>
                    <td><b>${Number(s.qty).toLocaleString()}</b></td>
                    <td>${fmtNum(s.avg, 4)} ج.م</td>
                    <td><b style="color: var(--primary);">${fmtPrice(s.price)} ج.م</b></td>
                    <td class="${changeColor}"><b>${s.change || '0.0%'}</b></td>
                    <td>${recBadge}</td>
                    <td><b>${s.volume || '—'}</b></td>
                    <td>${fmtNum(s.cost, 2)} ج.م</td>
                    <td><b>${fmtNum(s.val, 2)} ج.م</b></td>
                    <td class="${pnlColor}"><b>${fmtSign(s.pnl, 2)} ج.م</b></td>
                    <td class="${pnlColor}"><b>${fmtSign(s.ret, 2)}%</b></td>
                    <td><span class="text-primary-color" style="font-weight: 700;">${fmtNum(s.weight, 2)}%</span></td>
                    <td>
                        <div style="display: flex; gap: 4px; align-items: center;">
                            <button class="btn btn-glass" style="font-size: 11px; padding: 2px 7px; color: #38bdf8;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="أحدث أخبار وإفصاحات السهم">📰 أخبار</button>
                            <button class="btn btn-glass" style="font-size: 11px; padding: 2px 7px;" onclick="openTradingViewChart('${s.ticker}', '${s.name}')" title="فتح الشارت اللحظي">📊</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        const stocksTfoot = document.getElementById('dashboardStocksTableFoot');
        if (stocksTfoot) {
            const totalPnlColor = m.netPnl >= 0 ? 'text-emerald' : 'text-rose';
            stocksTfoot.innerHTML = `
                <tr>
                    <td colspan="3" style="text-align: center;"><b>الإجمالي الكلي للمحفظة</b></td>
                    <td><b>${m.stocks.reduce((acc, s) => acc + s.qty, 0).toLocaleString()}</b></td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td><b>${fmtNum(m.totalCost, 2)} ج.م</b></td>
                    <td><b style="color: var(--primary);">${fmtNum(m.totalMarket, 2)} ج.م</b></td>
                    <td class="${totalPnlColor}"><b>${fmtSign(m.netPnl, 2)} ج.م</b></td>
                    <td class="${totalPnlColor}"><b>${fmtSign(m.netReturn, 2)}%</b></td>
                    <td><b>100.00%</b></td>
                    <td>—</td>
                </tr>
            `;
        }
    }

    const tradesTbody = document.getElementById('dashboardTradesTableBody');
    if (tradesTbody) {
        if (!state.trades || state.trades.length === 0) {
            tradesTbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 14px;">لا توجد صفقات مسجلة بعد.</td></tr>`;
        } else {
            tradesTbody.innerHTML = [...state.trades].reverse().slice(0, 5).map(t => {
                const typeBadge = t.type === 'شراء' ? 'badge-emerald' : 'badge-rose';
                return `
                    <tr>
                        <td>${t.date}</td>
                        <td><span class="${typeBadge}">${t.type}</span></td>
                        <td><b>${t.ticker}</b></td>
                        <td>${Number(t.qty).toLocaleString()}</td>
                        <td>${fmtNum(t.price, 4)} ج.م</td>
                        <td>${fmtNum(t.fee || 0)} ج.م</td>
                        <td><span class="text-primary-color" style="font-weight: 700;">${t.settle_date || '—'}</span></td>
                    </tr>
                `;
            }).join('');
        }
    }

    const partnersQuick = document.getElementById('dashboardPartnersQuickList');
    if (partnersQuick) {
        const totalPartnerCapital = PARTNERS.reduce((sum, p) => sum + p.capital, 0);
        const grossProfit = m.netPnl + state.realized_pnl;
        const netDistributable = grossProfit > 0 
            ? Math.max(0.0, grossProfit - m.totalPurifyDue) 
            : (grossProfit - m.totalPurifyDue);

        partnersQuick.innerHTML = PARTNERS.map(p => {
            const ratio = p.capital / totalPartnerCapital;
            const profit = netDistributable * ratio;
            const entitlement = p.capital + profit;
            const pColor = profit >= 0 ? 'text-emerald' : 'text-rose';

            return `
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 26px; height: 26px; background: var(--bg-card); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                        </div>
                        <div>
                            <b>${p.name}</b>
                            <div style="font-size: 11px; color: var(--text-muted);">رأس المال: ${fmtNum(p.capital)} ج.م</div>
                        </div>
                    </div>
                    <div style="text-align: left;">
                        <div class="${pColor}"><b>${fmtSign(profit)} ج.م</b></div>
                        <div style="font-size: 11px; color: var(--text-muted);">المستحق: <b style="color: var(--text-primary);">${fmtNum(entitlement)}</b></div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// 4. تبويب أسهم المحفظة بالتفصيل
function renderStocksTab(m) {
    const container = document.getElementById('stocksGrid');
    if (!container) return;

    container.innerHTML = m.stocks.map(s => {
        const pnlColor = s.pnl >= 0 ? 'text-emerald' : 'text-rose';
        const changeColor = s.change && s.change.startsWith('+') ? 'text-emerald' : (s.change && s.change.startsWith('-') ? 'text-rose' : '');
        
        let recBadge = '';
        if (s.recommendation) {
            recBadge = `<span class="badge-rec ${s.recommendation.type}">${s.recommendation.icon} ${s.recommendation.text}</span>`;
        }

        return `
            <div class="stock-card">
                <div class="stock-card-top">
                    <div class="stock-title-group">
                        <div class="stock-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
                        </div>
                        <div class="stock-name-box">
                            <h3 style="cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="اضغط لعرض كافة أخبار وإفصاحات السهم">
                                ${s.name} 📰
                            </h3>
                            <div style="display: flex; align-items: center; gap: 5px; flex-wrap: wrap;">
                                <span class="ticker-badge" style="cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="عرض أخبار السهم">${s.ticker}</span>
                                ${recBadge}
                                ${!s.shariah.isShariah ? '<span class="badge-rose" style="font-size: 10px; font-weight: 700; padding: 1px 6px;">غير متوافق (تطهير 100%)</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="stock-price-box" style="text-align: left;">
                        <div class="price" style="font-size: 17px; font-weight: 800; color: var(--text-primary);">${fmtPrice(s.price)} <small style="font-size: 11px;">ج.م</small></div>
                        <div class="change ${changeColor}" style="font-size: 12px; font-weight: 700;">${s.change || '0.0%'}</div>
                    </div>
                </div>
                <div class="stock-stats-row">
                    <div class="stat-cell">
                        <span>متوسط الشراء</span>
                        <span>${fmtNum(s.avg, 4)} ج.م</span>
                    </div>
                    <div class="stat-cell">
                        <span>الكمية المملوكة</span>
                        <span>${Number(s.qty).toLocaleString()} سهم</span>
                    </div>
                    <div class="stat-cell">
                        <span>الفوليوم الحقيقي</span>
                        <span style="font-weight: 700; color: var(--text-primary);">${s.volume || '—'}</span>
                    </div>
                    <div class="stat-cell">
                        <span>مؤشر القوة (RSI)</span>
                        <span style="font-weight: 700; color: ${s.rsi > 70 ? 'var(--warning)' : (s.rsi < 35 ? 'var(--success)' : 'var(--text-primary)')};">${s.rsi ? s.rsi : '—'}</span>
                    </div>
                    <div class="stat-cell">
                        <span>القيمة الحالية</span>
                        <span>${fmtNum(s.val)} ج.م</span>
                    </div>
                    <div class="stat-cell">
                        <span>الوزن النسبي</span>
                        <span class="text-primary-color" style="font-weight: 800;">${fmtNum(s.weight, 1)}%</span>
                    </div>
                </div>
                <div class="stock-card-footer" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="color: var(--text-muted); font-size: 12px;">الربح الدفتري: </span>
                        <span class="${pnlColor}"><b>${fmtSign(s.pnl)} ج.م (${fmtSign(s.ret)}%)</b></span>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-glass" style="font-size: 11.5px; padding: 3px 9px; color: #38bdf8;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')">
                            📰 أخبار وإفصاحات
                        </button>
                        <button class="btn btn-glass" style="font-size: 11.5px; padding: 3px 9px;" onclick="openTradingViewChart('${s.ticker}', '${s.name}')">
                            📈 شارت
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// 5. تبويب حسابات الشركاء والأرباح
function renderPartnersTab(m) {
    const hero = document.getElementById('partnersHero');
    const grid = document.getElementById('partnersGrid');
    if (!hero || !grid) return;

    const totalPartnerCapital = PARTNERS.filter(p => !p.isManager).reduce((sum, p) => sum + p.capital, 0);
    const grossProfit = m.netPnl + state.realized_pnl;
    const netDistributable = grossProfit > 0 
        ? Math.max(0.0, grossProfit - m.totalPurifyDue) 
        : (grossProfit - m.totalPurifyDue);

    hero.innerHTML = `
        <div style="font-size: 13.5px; font-weight: 700; color: var(--text-muted);">
            رأس المال الأصلي الموزع (الشركاء الممولون): <b style="color: var(--text-primary);">${fmtNum(totalPartnerCapital)} ج.م</b>
        </div>
        <div style="font-size: 12.5px; color: var(--text-secondary); margin: 6px 0;">
            إجمالي الأرباح الكلية: ${fmtSign(grossProfit)} ج.م | مخصوم التطهير الشرعي: -${fmtNum(m.totalPurifyDue)} ج.م
        </div>
        <div class="text-emerald" style="font-size: 24px; font-weight: 900; margin-top: 6px;">
            صافي الربح الحلال للتوزيع: ${fmtSign(netDistributable)} ج.م
        </div>
    `;

    grid.innerHTML = PARTNERS.map(p => {
        if (p.isManager || p.capital === 0) {
            const partnerPayouts = (state.payouts || []).filter(pay => pay.partner === p.name || pay.partner.includes(p.name));
            const totalPaidOut = partnerPayouts.reduce((acc, pay) => acc + pay.amount, 0);

            return `
                <div class="partner-card" style="border: 1px solid rgba(56, 189, 248, 0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 28px; height: 28px; background: rgba(56, 189, 248, 0.15); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #38bdf8; font-size: 16px;">
                                💼
                            </div>
                            <div>
                                <h3 style="font-size: 15px; font-weight: 800; margin: 0;">${p.name}</h3>
                                <div style="font-size: 11px; color: #38bdf8; font-weight: 700;">مدير المحفظة</div>
                            </div>
                        </div>
                        <span class="badge-rec strong-buy" style="font-size: 10.5px; padding: 2px 8px;">
                            🎖️ الإشراف والإدارة
                        </span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px; background: var(--bg-subtle); padding: 12px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: var(--text-muted);">الدور في المحفظة:</span>
                            <b style="color: var(--text-primary);">مدير ومسؤول التداول</b>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: var(--text-muted);">أرباح المحفظة تحت إدارته:</span>
                            <b class="${grossProfit >= 0 ? 'text-emerald' : 'text-rose'}">${fmtSign(grossProfit)} ج.م</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--border-subtle); padding-top: 6px;">
                            <span style="color: var(--text-muted);">إجمالي المسحوبات المستلمة:</span>
                            <b style="color: #38bdf8;">${fmtNum(totalPaidOut)} ج.م</b>
                        </div>
                    </div>
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 12.5px; color: var(--text-muted);">حالة الإدارة:</span>
                        <span style="font-size: 13px; font-weight: 800; color: var(--primary);">نشط ومتابع لحظياً ✨</span>
                    </div>
                </div>
            `;
        }

        const ratio = totalPartnerCapital > 0 ? (p.capital / totalPartnerCapital) : 0;
        const pct = ratio * 100;
        const profit = netDistributable * ratio;
        const entitlement = p.capital + profit;
        const pColor = profit >= 0 ? 'text-emerald' : 'text-rose';

        return `
            <div class="partner-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 28px; height: 28px; background: var(--bg-subtle); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                        </div>
                        <h3 style="font-size: 15px; font-weight: 800;">${p.name}</h3>
                    </div>
                    <span class="badge-emerald">
                        ${fmtNum(pct, 2)}%
                    </span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px; background: var(--bg-subtle); padding: 12px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">رأس المال المساهم:</span>
                        <b>${fmtNum(p.capital)} ج.م</b>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">نصيب الربح الصافي:</span>
                        <b class="${pColor}">${fmtSign(profit)} ج.م</b>
                    </div>
                </div>
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12.5px; color: var(--text-muted);">إجمالي المستحق الحالي:</span>
                    <span style="font-size: 16px; font-weight: 800; color: var(--primary);">${fmtNum(entitlement)} ج.م</span>
                </div>
            </div>
        `;
    }).join('');
}

// 6. تبويب الأهداف والتقدم
function renderTargetsTab(m) {
    const container = document.getElementById('targetsContainer');
    if (!container) return;

    container.innerHTML = m.stocks.map(s => {
        const curP = s.price;
        const target = s.target_price || Number((curP * 1.15).toFixed(2));
        const progress = Math.min(100, Math.max(0, (curP / target) * 100));
        const remainingPct = ((target - curP) / curP) * 100;
        const isReached = curP >= target;

        return `
            <div class="form-card" style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 14.5px; font-weight: 800; cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="اضغط لعرض أخبار السهم">
                        ${s.name} (${s.ticker}) 📰
                    </span>
                    <span style="color: var(--text-muted); font-size: 12.5px;">السعر الحالي: <b style="color: var(--text-primary);">${fmtPrice(curP)} ج.م</b></span>
                </div>
                <div style="display: flex; gap: 10px; align-items: center; margin: 8px 0;">
                    <label style="font-size: 12px; color: var(--text-muted); white-space: nowrap;">المستهدف البيعي (ج.م):</label>
                    <input type="number" step="0.05" value="${target}" class="form-control" style="max-width: 130px; padding: 6px 10px;" onchange="updateStockTarget('${s.ticker}', this.value)">
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: ${progress}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; margin-top: 5px;">
                    <span style="color: var(--text-muted);">نسبة التقدم نحو الهدف: <b>${fmtNum(progress, 1)}%</b></span>
                    ${isReached 
                        ? '<span class="text-emerald" style="font-weight: 800;">وصل السهم لهدفه السعري بنجاح</span>'
                        : `<span class="text-primary-color" style="font-weight: 700;">متبقي للهدف: <b>${fmtNum(remainingPct, 1)}%</b> (${fmtNum(target - curP)} ج.م)</span>`
                    }
                </div>
            </div>
        `;
    }).join('');
}

function updateStockTarget(ticker, newTarget) {
    const val = parseFloat(newTarget);
    if (!isNaN(val) && val > 0) {
        const s = state.stocks.find(st => st.ticker === ticker);
        if (s) {
            s.target_price = val;
            saveState();
            showToast(`تم تحديث مستهدف ${ticker} إلى ${val} ج.م`);
        }
    }
}

// 7. تبويب الفوليوم والتحليل الفني
function renderVolumeTab(m) {
    const container = document.getElementById('volumeContainer');
    if (!container) return;

    container.innerHTML = m.stocks.map(s => {
        const a = analyzeVolumeAndForecast(s.ticker, s.price, s.avg);
        const changeColor = s.change && s.change.startsWith('+') ? 'text-emerald' : 'text-rose';
        let recBadge = s.recommendation 
            ? `<span class="badge-rec ${s.recommendation.type}">${s.recommendation.icon} ${s.recommendation.text}</span>`
            : '';

        return `
            <div class="stock-card" style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 14.5px; font-weight: 800; cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="اضغط لعرض أخبار وإفصاحات السهم">
                            ${s.name} 📰
                        </span>
                        <span class="ticker-badge" style="cursor: pointer;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="عرض أخبار السهم">${s.ticker}</span>
                        ${recBadge}
                    </div>
                    <div style="text-align: left; display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 15px; font-weight: 800;">${fmtPrice(s.price)} ج.م</span>
                        <span class="${changeColor}" style="font-size: 11.5px;">${s.change || ''}</span>
                        <button class="btn btn-glass" style="font-size: 11px; padding: 2px 7px; color: #38bdf8;" onclick="openStockNewsModal('${s.ticker}', '${s.name}')" title="أخبار وإفصاحات السهم">📰 أخبار</button>
                        <button class="btn btn-glass" style="font-size: 11px; padding: 2px 7px;" onclick="openTradingViewChart('${s.ticker}', '${s.name}')" title="شارت لحظي">📈 شارت</button>
                    </div>
                </div>
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 6px; padding: 7px 10px; font-size: 12.5px; font-weight: 700; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <span>الحالة اللحظية: ${a.trigger}</span>
                    <span style="font-size: 11.5px; color: var(--text-muted);">مؤشر RSI: <b style="color: var(--text-primary);">${s.rsi || '—'}</b></span>
                </div>
                <div class="stock-stats-row">
                    <div class="stat-cell">
                        <span>حجم التداول (الفوليوم الحقيقي)</span>
                        <span style="font-weight: 800; color: var(--text-primary);">${s.volume || '—'}</span>
                    </div>
                    <div class="stat-cell">
                        <span>قيمة التداول بالجلسة</span>
                        <span style="font-weight: 700;">${s.value_traded ? fmtNum(s.value_traded) + ' ج.م' : '—'}</span>
                    </div>
                    <div class="stat-cell">
                        <span>نطاق اليوم (أدنى - أعلى)</span>
                        <span>${s.day_low ? fmtPrice(s.day_low) : '—'} - ${s.day_high ? fmtPrice(s.day_high) : '—'} ج.م</span>
                    </div>
                    <div class="stat-cell">
                        <span>الدعم الفني الأول</span>
                        <span class="text-emerald">${fmtNum(a.sup)} ج.م</span>
                    </div>
                    <div class="stat-cell">
                        <span>المقاومة الفنية الأولى</span>
                        <span class="text-amber">${fmtNum(a.res)} ج.م</span>
                    </div>
                    <div class="stat-cell">
                        <span>وقف الخسارة الصارم</span>
                        <span class="text-rose">${fmtNum(a.sl)} ج.م</span>
                    </div>
                </div>
                <div style="background: var(--bg-subtle); border-right: 3px solid var(--primary); padding: 8px 12px; border-radius: 4px; font-size: 12.5px; margin-top: 6px; color: var(--text-secondary);">
                    <b>قراءة السيولة وتوقع الجلسة:</b> ${a.forecast}
                </div>
            </div>
        `;
    }).join('');
}

// 8. تبويب تسجيل الصفقات
function renderTradesTab() {
    const tbody = document.getElementById('tradesTableBody');
    if (!tbody) return;

    if (!state.trades || state.trades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 18px;">لا توجد صفقات مسجلة بعد.</td></tr>`;
        return;
    }

    tbody.innerHTML = [...state.trades].reverse().slice(0, 15).map(t => {
        const typeBadge = t.type === 'شراء' ? 'badge-emerald' : 'badge-rose';
        return `
            <tr>
                <td>${t.date}</td>
                <td><span class="${typeBadge}">${t.type}</span></td>
                <td><b>${t.ticker}</b></td>
                <td>${Number(t.qty).toLocaleString()}</td>
                <td>${fmtNum(t.price, 4)} ج.م</td>
                <td>${fmtNum(t.fee || 0)} ج.م</td>
                <td><span class="text-primary-color" style="font-weight: 700;">${t.settle_date || '—'}</span> (${t.cycle || 'T+1'})</td>
            </tr>
        `;
    }).join('');
}

// 9. تبويب التطهير الشرعي
function renderShariahTab(m) {
    const container = document.getElementById('shariahContainer');
    const hero = document.getElementById('shariahHero');
    if (!container || !hero) return;

    hero.innerHTML = `
        <div style="font-size: 13.5px; font-weight: 700; color: var(--text-muted);">إجمالي مبالغ التطهير المستحقة على أرباح المحفظة الحالية</div>
        <div class="text-amber" style="font-size: 26px; font-weight: 900; margin-top: 4px;">${fmtNum(m.totalPurifyDue)} ج.م</div>
    `;

    container.innerHTML = m.stocks.map(s => {
        const sh = s.shariah;
        let badge = '';
        let purifyNote = '';

        if (!sh.isShariah) {
            badge = `<span class="badge-rose" style="font-weight: 800;">غير متوافق مع الشريعة (تطهير 100% من الأرباح)</span>`;
            purifyNote = s.pnl > 0 
                ? `<b class="text-rose" style="font-weight: 800;">${fmtNum(sh.purifyAmt)} ج.م (تطهير كامل 100%)</b>` 
                : `<b class="text-amber">0.00 ج.م (تطهير 100% عند تحقيق أي أرباح)</b>`;
        } else if (sh.rate === 0.0) {
            badge = `<span class="badge-emerald" style="font-weight: 800;">نقي 100% (تطهير 0%)</span>`;
            purifyNote = `<b class="text-emerald">0.00 ج.م (نقي تماماً)</b>`;
        } else {
            badge = `<span style="background: var(--warning-subtle); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); padding: 2px 7px; border-radius: 4px; font-size: 11.5px; font-weight: 700;">درجة النقاء: ${sh.category} (نسبة التطهير ${(sh.rate * 100).toFixed(2)}%)</span>`;
            purifyNote = `<b class="text-amber">${fmtNum(sh.purifyAmt)} ج.م (بنسبة ${(sh.rate * 100).toFixed(2)}%)</b>`;
        }

        return `
            <div class="stock-card" style="margin-bottom: 12px; border-right: 4px solid ${!sh.isShariah ? 'var(--danger)' : (sh.rate === 0 ? 'var(--success)' : 'var(--warning)')};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 14.5px; font-weight: 800;">${s.name} (${s.ticker})</span>
                    <div>${badge}</div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12.5px; background: var(--bg-subtle); padding: 8px 12px; border-radius: 6px; margin-top: 6px;">
                    <span style="color: var(--text-muted);">الأرباح الدفترية: <b class="${s.pnl >= 0 ? 'text-emerald' : 'text-rose'}">${fmtSign(s.pnl)} ج.م</b></span>
                    <span style="color: var(--text-muted);">مستحق التطهير الشرعي: ${purifyNote}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 10. دليل أسهم كاشف
function renderKashefDirectory() {
    const tbody = document.getElementById('kashefTableBody');
    const searchInput = document.getElementById('kashefSearch');
    if (!tbody) return;

    const query = searchInput ? searchInput.value.trim().toUpperCase() : '';

    const entries = Object.entries(SHARIAH_ALL_STOCKS).filter(([ticker, info]) => {
        if (!query) return true;
        return ticker.includes(query) || info.name.includes(query) || info.category.includes(query);
    });

    if (entries.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px;">لا توجد نتائج مطابقة لبحثك.</td></tr>`;
        return;
    }

    tbody.innerHTML = entries.map(([ticker, info]) => {
        let catClass = 'text-emerald';
        if (info.category.includes('شبه نقي')) catClass = 'text-primary-color';
        if (info.category.includes('مختلط')) catClass = 'text-amber';

        return `
            <tr>
                <td><b>${ticker}</b></td>
                <td>${info.name}</td>
                <td><span style="font-weight: 700;" class="${catClass}">${info.category}</span></td>
                <td><b>${(info.rate * 100).toFixed(2)}%</b></td>
            </tr>
        `;
    }).join('');
}

// 11. تبويب إدارة الكاش والمصاريف
function renderExpensesTab() {
    const list = document.getElementById('expensesList');
    if (!list) return;

    if (!state.expenses || state.expenses.length === 0) {
        list.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 12px;">لا توجد معاملات كاش مسجلة بعد.</div>`;
        return;
    }

    list.innerHTML = [...state.expenses].reverse().slice(0, 10).map(e => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 9px 12px; background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 6px; margin-bottom: 6px; font-size: 13px;">
            <div>
                <span style="color: var(--text-muted);">${e.date}</span>
                <span style="margin: 0 6px;">|</span>
                <b>${e.type}</b> ${e.desc ? `(${e.desc})` : ''}
            </div>
            <div style="font-size: 14px; font-weight: 800; color: ${e.type.includes('إيداع') ? 'var(--success)' : 'var(--danger)'};">
                ${fmtNum(e.amt)} ج.م
            </div>
        </div>
    `).join('');
}

// ملء قوائم اختيار الأسهم في النماذج
function populateSelectPickers() {
    const picker = document.getElementById('tradeTicker');
    if (!picker) return;
    const current = picker.value;
    picker.innerHTML = state.stocks.map(s => `
        <option value="${s.ticker}">${s.name} (${s.ticker})</option>
    `).join('');
    if (current) picker.value = current;
}

// معالجة تسجيل صفقة جديدة
function handleTradeSubmit(e) {
    e.preventDefault();
    const type = document.querySelector('input[name="tradeType"]:checked').value;
    const ticker = document.getElementById('tradeTicker').value;
    const qty = parseInt(document.getElementById('tradeQty').value);
    const price = parseFloat(document.getElementById('tradePrice').value);
    const fee = parseFloat(document.getElementById('tradeFee').value) || 0.0;
    const cycle = document.getElementById('tradeCycle').value;

    if (!ticker || isNaN(qty) || qty <= 0 || isNaN(price) || price <= 0) {
        alert("يرجى ملء جميع حقول الصفقة بأرقام صحيحة.");
        return;
    }

    const rawVal = qty * price;
    const today = new Date();
    const settleDays = cycle.includes('T+1') ? 1 : 2;
    const settleDate = new Date(today);
    settleDate.setDate(today.getDate() + settleDays);
    const settleDateStr = settleDate.toISOString().split('T')[0];

    const stock = state.stocks.find(s => s.ticker === ticker);
    if (!stock) {
        alert("السهم غير موجود في المحفظة.");
        return;
    }

    if (type === "شراء") {
        const totalCostIncFee = rawVal + fee;
        const newQty = stock.qty + qty;
        const newAvg = ((stock.qty * stock.avg) + totalCostIncFee) / newQty;
        stock.qty = newQty;
        stock.avg = Number(newAvg.toFixed(4));
        state.cash -= totalCostIncFee;
    } else if (type === "بيع") {
        if (qty > stock.qty) {
            alert(`الكمية المراد بيعها (${qty}) أكبر من الرصيد المتوفر (${stock.qty})!`);
            return;
        }
        const netProceeds = rawVal - fee;
        const costOfSold = qty * stock.avg;
        const tradeRealized = netProceeds - costOfSold;
        state.realized_pnl += tradeRealized;
        stock.qty = Math.max(0, stock.qty - qty);
        state.cash += netProceeds;
    }

    state.trades.push({
        date: today.toISOString().split('T')[0],
        type,
        ticker,
        qty,
        price,
        val: rawVal,
        fee: Number(fee.toFixed(2)),
        settle_date: settleDateStr,
        cycle
    });

    saveState();
    showToast(`تم تسجيل صفقة ${type} ${qty} سهم في ${ticker} بنجاح!`);
    document.getElementById('tradeForm').reset();
    populateSelectPickers();
}

// معالجة حركة الكاش
function handleCashSubmit(e) {
    e.preventDefault();
    const action = document.getElementById('cashAction').value;
    const amt = parseFloat(document.getElementById('cashAmt').value);
    const desc = document.getElementById('cashDesc').value.trim();

    if (isNaN(amt) || amt <= 0) {
        alert("يرجى إدخال مبلغ صحيح.");
        return;
    }

    if (action === "إيداع كاش للمحفظة") {
        state.cash += amt;
    } else if (action === "سحب كاش من المحفظة") {
        state.cash -= amt;
    }

    state.expenses.push({
        date: new Date().toISOString().split('T')[0],
        type: action,
        amt,
        desc
    });

    saveState();
    showToast(`تم تسجيل حركة الكاش بقيمة ${fmtNum(amt)} ج.م!`);
    document.getElementById('cashForm').reset();
}

// تحديث أسعار السوق وتثبيت الأرقام الرسمية المعتمدة
async function refreshMarketPrices() {
    showToast("جاري تحديث وتثبيت الأسعار الرسمية المعتمدة للمحفظة...");
    
    DEFAULT_STOCKS.forEach(def => {
        const s = state.stocks.find(item => item.ticker === def.ticker);
        if (s) {
            s.name = def.name;
            s.price = def.price;
            s.avg = def.avg;
            s.qty = def.qty;
            s.change = def.change;
            s.volume = def.volume;
            s.target_price = def.target_price;
        } else {
            state.stocks.push(JSON.parse(JSON.stringify(def)));
        }
    });

    saveState();
    showToast("تم تحديث أسعار وفوليوم المحفظة بالأرقام الرسمية بنجاح! ✨");
}

// ===================================================
// المساعد الذكي Gemini 3.6 Flash - مدير التداول والصفقات الآلي
// ===================================================

function setupChatListeners() {
    const chatInput = document.getElementById('chatInput');
    const chatWrapper = document.querySelector('.chat-wrapper');

    if (chatInput) {
        // دعم اللصق المباشر للصور (Ctrl + V)
        chatInput.addEventListener('paste', (e) => {
            const items = (e.clipboardData || e.originalEvent?.clipboardData)?.items;
            if (!items) return;
            for (const item of items) {
                if (item.type.indexOf('image') === 0) {
                    const blob = item.getAsFile();
                    if (blob) {
                        processImageFile(blob);
                        e.preventDefault();
                        showToast("تم إرفاق لقطة الشاشة من الحافظة! 📷");
                        break;
                    }
                }
            }
        });
    }

    if (chatWrapper) {
        // دعم سحب وإفلات الصور (Drag & Drop)
        chatWrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            chatWrapper.style.borderColor = 'var(--primary)';
        });
        chatWrapper.addEventListener('dragleave', (e) => {
            e.preventDefault();
            chatWrapper.style.borderColor = 'var(--border-color)';
        });
        chatWrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            chatWrapper.style.borderColor = 'var(--border-color)';
            const files = e.dataTransfer?.files;
            if (files && files[0] && files[0].type.startsWith('image/')) {
                processImageFile(files[0]);
                showToast("تم إرفاق لقطة الشاشة بنجاح! 📷");
            }
        });
    }
}

function handleImageSelected(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    processImageFile(file);
}

function processImageFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast("يرجى اختيار ملف صورة صالح (PNG, JPG, WEBP)");
        return;
    }
    const reader = new FileReader();
    reader.onload = function(evt) {
        const fullBase64 = evt.target.result;
        const pureBase64 = fullBase64.split(',')[1];
        currentSelectedImage = {
            dataUrl: fullBase64,
            base64: pureBase64,
            mimeType: file.type,
            name: file.name
        };
        const bar = document.getElementById('chatImagePreviewBar');
        const img = document.getElementById('chatImagePreview');
        const nameSpan = document.getElementById('chatImageName');
        if (bar && img && nameSpan) {
            img.src = fullBase64;
            nameSpan.textContent = file.name;
            bar.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}

function clearSelectedImage() {
    currentSelectedImage = null;
    const bar = document.getElementById('chatImagePreviewBar');
    const input = document.getElementById('chatImageInput');
    if (bar) bar.style.display = 'none';
    if (input) input.value = '';
}

function setChatPrompt(text) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        input.focus();
    }
}

function saveGeminiKey(key) {
    const cleanKey = key.trim();
    if (cleanKey) {
        localStorage.setItem(GEMINI_KEY_STORAGE, cleanKey);
        showToast("تم حفظ مفتاح Gemini API بنجاح");
    }
}

// تنفيذ صفقة شراء آلياً من المساعد الذكي
function executeAiBuy(trade) {
    const ticker = (trade.ticker || "").toUpperCase().trim();
    const qty = parseInt(trade.qty) || 0;
    const price = parseFloat(trade.price) || 0;
    const fee = parseFloat(trade.fees) || 0;
    const rawVal = qty * price;
    const totalCostIncFee = rawVal + fee;

    if (qty <= 0 || price <= 0) {
        return { success: false, msg: "الكمية أو السعر غير صالح" };
    }

    // البحث عن السهم في المحفظة
    let stock = state.stocks.find(s => 
        s.ticker.toUpperCase() === ticker || 
        (trade.name && s.name.includes(trade.name)) ||
        (trade.name && trade.name.includes(s.name))
    );

    let isNewStock = false;
    if (!stock) {
        isNewStock = true;
        const shariahInfo = (typeof SHARIAH_ALL_STOCKS !== 'undefined') ? SHARIAH_ALL_STOCKS[ticker] : null;
        const officialName = shariahInfo ? shariahInfo.name : (trade.name || ticker);
        const purif = shariahInfo ? shariahInfo.purif : 0.0;
        const sector = shariahInfo ? shariahInfo.sector : "أسهم متنوعة";

        stock = {
            name: officialName,
            ticker: ticker || "EGX",
            qty: 0,
            avg: price,
            price: price,
            purif: purif,
            sector: sector,
            target_price: Number((price * 1.15).toFixed(2))
        };
        state.stocks.push(stock);
    }

    // إعادة احتساب المتوسط المتحرك للكمية
    const oldQty = stock.qty;
    const oldAvg = stock.avg;
    const newQty = oldQty + qty;
    const newAvg = ((oldQty * oldAvg) + totalCostIncFee) / newQty;

    stock.qty = newQty;
    stock.avg = Number(newAvg.toFixed(4));
    stock.price = price;

    // خصم الكاش
    state.cash -= totalCostIncFee;

    // تاريخ التسوية
    const today = new Date();
    const cycle = trade.settlement || "T+2";
    const daysToAdd = cycle === "T+0" ? 0 : (cycle === "T+1" ? 1 : 2);
    const settleDate = new Date(today);
    settleDate.setDate(settleDate.getDate() + daysToAdd);
    const settleDateStr = settleDate.toISOString().split('T')[0];

    // تسجيل في العمليات
    state.trades.unshift({
        date: today.toISOString().split('T')[0],
        type: "شراء",
        ticker: stock.ticker,
        qty: qty,
        price: price,
        val: rawVal,
        fee: Number(fee.toFixed(2)),
        settle_date: settleDateStr,
        cycle: cycle
    });

    saveState();
    showToast(`✅ تم تنفيذ صفقة شراء ${qty} سهم في ${stock.name} بنجاح!`);

    return {
        success: true,
        type: "شراء",
        stockName: stock.name,
        ticker: stock.ticker,
        qty: qty,
        price: price,
        val: rawVal,
        fee: fee,
        newAvg: stock.avg,
        newQty: stock.qty,
        isNew: isNewStock
    };
}

// تنفيذ صفقة بيع آلياً من المساعد الذكي
function executeAiSell(trade) {
    const ticker = (trade.ticker || "").toUpperCase().trim();
    const qty = parseInt(trade.qty) || 0;
    const price = parseFloat(trade.price) || 0;
    const fee = parseFloat(trade.fees) || 0;
    const rawVal = qty * price;
    const netProceeds = rawVal - fee;

    if (qty <= 0 || price <= 0) {
        return { success: false, msg: "الكمية أو السعر غير صالح" };
    }

    let stock = state.stocks.find(s => 
        s.ticker.toUpperCase() === ticker || 
        (trade.name && s.name.includes(trade.name)) ||
        (trade.name && trade.name.includes(s.name))
    );

    let tradeRealized = 0;
    let oldAvg = price;

    if (stock) {
        oldAvg = stock.avg;
        const costOfSold = qty * stock.avg;
        tradeRealized = netProceeds - costOfSold;
        state.realized_pnl += tradeRealized;
        stock.qty = Math.max(0, stock.qty - qty);
        stock.price = price;
    }

    state.cash += netProceeds;

    const today = new Date();
    const cycle = trade.settlement || "T+2";
    const daysToAdd = cycle === "T+0" ? 0 : (cycle === "T+1" ? 1 : 2);
    const settleDate = new Date(today);
    settleDate.setDate(settleDate.getDate() + daysToAdd);
    const settleDateStr = settleDate.toISOString().split('T')[0];

    state.trades.unshift({
        date: today.toISOString().split('T')[0],
        type: "بيع",
        ticker: stock ? stock.ticker : ticker,
        qty: qty,
        price: price,
        val: rawVal,
        fee: Number(fee.toFixed(2)),
        settle_date: settleDateStr,
        cycle: cycle
    });

    saveState();
    showToast(`✅ تم تنفيذ صفقة بيع ${qty} سهم في ${stock ? stock.name : ticker} بنجاح!`);

    return {
        success: true,
        type: "بيع",
        stockName: stock ? stock.name : (trade.name || ticker),
        ticker: stock ? stock.ticker : ticker,
        qty: qty,
        price: price,
        val: rawVal,
        fee: fee,
        realized: tradeRealized,
        remQty: stock ? stock.qty : 0
    };
}

// تنفيذ حركة كاش آلياً
function executeAiCash(type, amt, desc) {
    if (isNaN(amt) || amt <= 0) return;
    if (type === "deposit" || type === "إيداع") {
        state.cash += amt;
        showToast(`✅ تم إيداع ${fmtNum(amt)} ج.م كاش بالمحفظة`);
    } else {
        state.cash = Math.max(0, state.cash - amt);
        showToast(`✅ تم سحب ${fmtNum(amt)} ج.م كاش من المحفظة`);
    }
    saveState();
}

// المساعد الذكي Multimodal Gemini AI
async function sendAiMessage() {
    const input = document.getElementById('chatInput');
    const apiKeyInput = document.getElementById('geminiApiKey');
    if (!input) return;

    const userText = input.value.trim();
    const attachedImage = currentSelectedImage;
    const apiKey = (apiKeyInput ? apiKeyInput.value.trim() : "") || localStorage.getItem(GEMINI_KEY_STORAGE) || DEFAULT_GEMINI_KEY;

    if (!userText && !attachedImage) return;

    localStorage.setItem(GEMINI_KEY_STORAGE, apiKey);

    // إضافة رسالة المستخدم مع الصورة إن وجدت
    messages.push({ 
        role: "user", 
        content: userText || "أرفقت لقطة شاشة لأمر تداول / محفظة لتحليلها وتنفيذها آلياً.",
        image: attachedImage ? attachedImage.dataUrl : null
    });

    // تفريغ المدخلات فوراً لراحة المستخدم
    input.value = "";
    clearSelectedImage();
    renderChatMessages();

    // رسالة انتظار ذكية
    const tempId = "temp_loading_" + Date.now();
    messages.push({
        id: tempId,
        role: "assistant",
        content: attachedImage ? "🔍 جاري فحص لقطة الشاشة واستخراج بيانات الصفقة بواسطة Gemini 3.6 Flash..." : "⚡ جاري معالجة الأمر والاتصال بـ Gemini لتحديث المحفظة..."
    });
    renderChatMessages();

    const metrics = calculatePortfolioMetrics();
    const portfolioSummary = state.stocks.map(s => 
        `- سهم: ${s.name} (${s.ticker}), الكمية: ${s.qty}, متوسط الشراء: ${s.avg} ج.م, السعر اللحظي: ${s.price} ج.م`
    ).join("\n");

    const systemPrompt = `
أنت المساعد المالي الذكي ومدير الصفقات الآلي لمحفظة تيلدا في البورصة المصرية (EGX).
أنت مقيد بمعايير كاشف للأسهم النقية الحلال.

البيانات اللحظية للمحفظة:
- الكاش المتاح: ${fmtNum(state.cash)} ج.م
- الأرباح المحققة: ${fmtNum(state.realized_pnl)} ج.م
- الأسهم الحالية:
${portfolioSummary}

المهمة الأساسية:
إذا طلب المستخدم تسجيل عملية بيع أو شراء (بالكتابة مثل: "اشتريت 500 سهم فوري بسعر 7.20" أو "بعت 200 سهم السويدي بسعر 45")،
أو إذا أرفق لقطة شاشة (Screenshot من تطبيق ثندر Thndr أو شركة سمسرة أو إشعار بنكي أو عقد تداول)،
عليك استخراج تفاصيل العملية بدقة، ووضع كود JSON محدد في نهاية ردك بالشكل التالي:

\`\`\`json
{
  "action": "BUY" | "SELL" | "CASH_DEPOSIT" | "CASH_WITHDRAW" | "NONE",
  "trade": {
    "type": "شراء" أو "بيع",
    "ticker": "كود السهم الإنجليزي في EGX مثل FWRY, SWDY, TMGH, ESRS, MFPC, COMI, ISPH",
    "name": "الاسم العربي للسهم",
    "qty": عدد الأسهم (رقم صحيح موجب),
    "price": سعر التنفيذ للواحد (رقم),
    "fees": العمولة أو المصاريف إن وجدت (رقم، الافتراضي 0),
    "settlement": "T+0" أو "T+1" أو "T+2" (الافتراضي T+2 للأسهم العادية)
  },
  "cash_action": {
    "type": "deposit" أو "withdraw",
    "amount": المبلغ (رقم)
  }
}
\`\`\`

إذا لم تتضمن الرسالة أو الصورة أي عملية تداول، اجعل "action": "NONE"، وأجب بالعامية المصرية باختصار واحترافية وذكاء مع التركيز على الفوليوم والدعوم والمقاومات والربحية.
رسالة المستخدم: ${userText || "افحص الصورة المرفقة واستخرج أي صفقة تداول منفذة"}
    `;

    // تكوين أجزاء المحتوى (نص + صورة إن وجدت)
    const contentParts = [];
    if (attachedImage) {
        contentParts.push({
            inlineData: {
                mimeType: attachedImage.mimeType,
                data: attachedImage.base64
            }
        });
    }
    contentParts.push({ text: systemPrompt });

    // تجربة موديل gemini-3.6-flash مع fallback لموديلات سريعة
    const modelsToTry = [
        'models/gemini-3.6-flash',
        'models/gemini-3.5-flash',
        'models/gemini-flash-latest'
    ];

    let replyText = null;
    let lastError = null;

    for (const model of modelsToTry) {
        try {
            const url = `https://generativelanguage.googleapis.com/v1beta/${model}:generateContent?key=${apiKey}`;
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: contentParts }]
                })
            });

            if (res.ok) {
                const data = await res.json();
                const parts = data.candidates?.[0]?.content?.parts || [];
                replyText = parts.map(p => p.text || '').filter(Boolean).join('\n');
                if (replyText) break;
            } else {
                const errData = await res.json().catch(() => ({}));
                lastError = errData.error?.message || res.statusText;
            }
        } catch (err) {
            lastError = err.message;
        }
    }

    // إزالة رسالة الانتظار
    messages = messages.filter(m => m.id !== tempId);

    if (!replyText) {
        messages.push({ 
            role: "assistant", 
            content: `عذراً، حدث خطأ أثناء الاتصال بجيمناي: ${lastError || "يرجى التحقق من مفتاح API والاتصال بالإنترنت"}` 
        });
        renderChatMessages();
        return;
    }

    // فحص ما إذا كان الرد يحتوي على عملية تلقائية للتنفيذ
    let executedAction = null;
    const jsonMatch = replyText.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
        try {
            const parsed = JSON.parse(jsonMatch[1]);
            if (parsed.action === "BUY" && parsed.trade) {
                executedAction = executeAiBuy(parsed.trade);
            } else if (parsed.action === "SELL" && parsed.trade) {
                executedAction = executeAiSell(parsed.trade);
            } else if (parsed.action === "CASH_DEPOSIT" && parsed.cash_action) {
                executeAiCash("deposit", parsed.cash_action.amount);
                executedAction = { success: true, type: "إيداع كاش", amount: parsed.cash_action.amount };
            } else if (parsed.action === "CASH_WITHDRAW" && parsed.cash_action) {
                executeAiCash("withdraw", parsed.cash_action.amount);
                executedAction = { success: true, type: "سحب كاش", amount: parsed.cash_action.amount };
            }
        } catch (e) {
            console.warn("تعذر قراءة كود العمليات الآلية من رد الذكاء الاصطناعي:", e);
        }
    }

    // تنظيف نص الرد من كود JSON ليبدو أنيقاً ومفهوماً
    let cleanReply = replyText.replace(/```(?:json)?\s*[\s\S]*?\s*```/g, '').trim();
    if (!cleanReply && executedAction) {
        cleanReply = `تم تنفيذ العملية وتحديث بيانات المحفظة والكاش فوراً! ✨`;
    }

    messages.push({ 
        role: "assistant", 
        content: cleanReply,
        actionResult: executedAction
    });

    renderChatMessages();
}

function renderChatMessages() {
    const box = document.getElementById('chatMessages');
    if (!box) return;

    box.innerHTML = messages.map(m => {
        let actionBadgeHtml = '';
        if (m.actionResult && m.actionResult.success) {
            const isSell = m.actionResult.type === "بيع";
            const isCash = m.actionResult.type.includes("كاش");

            if (isCash) {
                actionBadgeHtml = `
                    <div class="trade-execution-card">
                        <div class="card-title">
                            <span>⚡ تم تعديل رصيد الكاش تلقائياً</span>
                        </div>
                        <div class="card-details">
                            <span>العملية: <b>${m.actionResult.type}</b></span>
                            <span>المبلغ: <b>${fmtNum(m.actionResult.amount)} ج.م</b></span>
                        </div>
                    </div>
                `;
            } else {
                actionBadgeHtml = `
                    <div class="trade-execution-card ${isSell ? 'sell' : ''}">
                        <div class="card-title">
                            <span>⚡ تم تنفيذ الصفقة وتحديث المحفظة آلياً</span>
                        </div>
                        <div class="card-details">
                            <span>النوع: <b>${m.actionResult.type}</b></span>
                            <span>السهم: <b>${m.actionResult.stockName} (${m.actionResult.ticker})</b></span>
                            <span>الكمية: <b>${m.actionResult.qty} سهم</b></span>
                            <span>السعر: <b>${fmtNum(m.actionResult.price)} ج.م</b></span>
                            <span>الإجمالي: <b>${fmtNum(m.actionResult.val)} ج.م</b></span>
                        </div>
                        <div class="card-impact">
                            ${!isSell ? `متوسط الشراء الجديد: <b>${fmtNum(m.actionResult.newAvg, 3)} ج.م</b> | الرصيد الإجمالي: <b>${m.actionResult.newQty} سهم</b>` : `الربح المحقق: <b>${fmtSign(m.actionResult.realized)} ج.م</b> | الرصيد المتبقي: <b>${m.actionResult.remQty} سهم</b>`}
                        </div>
                    </div>
                `;
            }
        }

        const imageHtml = m.image ? `<img src="${m.image}" class="chat-attached-img" alt="مرفق المستخدم" onclick="window.open(this.src)">` : '';
        const formattedContent = m.content
            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/\*(.*?)\*/g, '<i>$1</i>')
            .replace(/\n/g, '<br>');

        return `
            <div class="chat-bubble ${m.role}">
                ${m.role === 'assistant' ? '<div style="font-weight: 800; color: var(--primary); margin-bottom: 4px;">مساعد تيلدا الذكي:</div>' : '<div style="font-weight: 800; opacity: 0.85; margin-bottom: 4px;">أنت:</div>'}
                ${imageHtml}
                ${actionBadgeHtml}
                <div>${formattedContent}</div>
            </div>
        `;
    }).join('');

    box.scrollTop = box.scrollHeight;
}

// تنزيل نسخة احتياطية
function downloadBackup() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `portfolio_data_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
    showToast("تم تنزيل النسخة الاحتياطية بنجاح! 💾");
}

// استيراد نسخة سابقة
function importBackup(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const imported = JSON.parse(event.target.result);
            if (imported.stocks && Array.isArray(imported.stocks)) {
                state = imported;
                saveState();
                showToast("تم استرجاع بيانات المحفظة بنجاح! ✅");
            } else {
                alert("الملف لا يحتوي على هيكل محفظة صحيح.");
            }
        } catch (err) {
            alert("حدث خطأ أثناء قراءة ملف النسخة الاحتياطية.");
        }
    };
    reader.readAsText(file);
}

// ربط عناصر التنقل في السايدبار
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            if (tabId) switchToTab(tabId);
        });
    });
}

// تشغيل التطبيق عند التحميل
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initState();
    setupNavigation();
    renderAll();
    renderChatMessages();

    const tradeForm = document.getElementById('tradeForm');
    if (tradeForm) tradeForm.addEventListener('submit', handleTradeSubmit);

    const cashForm = document.getElementById('cashForm');
    if (cashForm) cashForm.addEventListener('submit', handleCashSubmit);

    const payoutForm = document.getElementById('payoutForm');
    if (payoutForm) payoutForm.addEventListener('submit', handlePayoutSubmit);

    const kashefSearch = document.getElementById('kashefSearch');
    if (kashefSearch) kashefSearch.addEventListener('input', renderKashefDirectory);

    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendAiMessage();
            }
        });
    }

    // تشغيل محرك البورصة اللحظي والتحديث التلقائي ومسح السوق
    refreshMarketPrices(true);
    startAutoRefresh();
    fetchLiveMarketScreener();
});

