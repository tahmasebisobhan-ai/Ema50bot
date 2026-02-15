import requests

# -----------------------------
# تنظیمات تلگرام (توکن و chat_id واقعی خودت)
# -----------------------------
BOT_TOKEN = "8546173398:AAEDnGYPuKKhWATYnZ8cbzFe3Q7kJ2AnkUQ"
CHAT_ID = 161280400

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Telegram ERROR:", e)

# -----------------------------
# لیست ارزهای مورد نظر
# -----------------------------
pairs = [
    "btcusdt", "ethusdt", "solusdt", "ltcusdt", "avaxusdt",
    "adausdt", "ensusdt", "xrpusdt", "algousdt",
    "etcusdt", "suiusdt", "linkusdt"
]

# -----------------------------
# EMA50 ساده
# -----------------------------
def ema50(prices):
    k = 2 / 51
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

# -----------------------------
# تایم فریم ها
# -----------------------------
timeframes = ["5min", "15min"]

# -----------------------------
# حافظه داخلی برای جلوگیری از پیام تکراری
# -----------------------------
last_touch = {}  # کلید: symbol+tf, value: True/False

# -----------------------------
# پردازش هر ارز و تایم فریم
# -----------------------------
for symbol in pairs:
    for tf in timeframes:
        try:
            url = f"https://api.lbank.info/v2/kline.do?symbol={symbol}&type={tf}&size=80"
            res = requests.get(url, timeout=10).json()
            data = res["data"]

            closes = [float(c[2]) for c in data]
            highs  = [float(c[3]) for c in data]
            lows   = [float(c[4]) for c in data]

            ema = ema50(closes)
            last_close = closes[-1]
            last_high = highs[-1]
            last_low = lows[-1]
            prev_close = closes[-2]

            # -------------------------
            # بررسی برخورد با EMA (shadow یا close crossing)
            # -------------------------
            touched = False
            # shadow یا close touch
            if last_low <= ema <= last_high:
                touched = True
            elif (prev_close - ema) * (last_close - ema) <= 0:
                touched = True

            # کلید حافظه: ارز+تایم فریم
            key = f"{symbol}_{tf}"

            if touched and not last_touch.get(key, False):
                send_telegram(f"⚡ برخورد با EMA50\n{symbol.upper()} | تایم فریم: {tf}\nClose: {last_close}")
                last_touch[key] = True
            elif not touched:
                last_touch[key] = False

        except Exception as e:
            print("ERROR:", symbol, tf, e)
