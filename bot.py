import requests

# -----------------------------
# تنظیمات تلگرام
# -----------------------------
BOT_TOKEN = "8546173398:AAEDnGYPuKKhWATYnZ8cbzFe3Q7kJ2AnkUQ"
CHAT_ID = "161280400"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=5)
    except:
        pass

# -----------------------------
# لیست ارزهای مورد نظر
# -----------------------------
pairs = [
    "btcusdt", "ethusdt", "solusdt", "ltcusdt", "avaxusdt",
    "adausdt", "ensusdt", "xrpusdt", "algousdt",
    "etcusdt", "suiusdt", "linkusdt"
]

# -----------------------------
# محاسبه EMA50 بدون pandas
# -----------------------------
def ema50(prices):
    k = 2 / 51
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

# -----------------------------
# پردازش هر ارز
# -----------------------------
for symbol in pairs:
    try:
        url = f"https://api.lbank.info/v2/kline.do?symbol={symbol}&type=5min&size=80"
        res = requests.get(url, timeout=5).json()

        data = res["data"]

        closes = [float(c[2]) for c in data]   # close
        highs  = [float(c[3]) for c in data]   # high
        lows   = [float(c[4]) for c in data]   # low

        ema = ema50(closes)

        last_close = closes[-1]
        prev_close = closes[-2]

        last_high = highs[-1]
        last_low = lows[-1]

        # -------------------------
        # کراس رو به بالا
        # -------------------------
        if prev_close < ema and last_close > ema:
            send_telegram(
                f"🔼 کراس رو به بالا EMA50\n{symbol.upper()}\nClose: {last_close}"
            )

        # -------------------------
        # کراس رو به پایین
        # -------------------------
        if prev_close > ema and last_close < ema:
            send_telegram(
                f"🔽 کراس رو به پایین EMA50\n{symbol.upper()}\nClose: {last_close}"
            )

        # -------------------------
        # برخورد ساده (Shadow Touch)
        # -------------------------
        if last_low <= ema <= last_high:
            send_telegram(
                f"⚡ برخورد با EMA50\n{symbol.upper()}\nClose: {last_close}"
            )

    except Exception as e:
        print("ERROR:", symbol, str(e))
