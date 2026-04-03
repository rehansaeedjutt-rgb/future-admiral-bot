import requests
import os
from datetime import datetime

def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params)
    return r.json()

def get_fear_greed():
    r = requests.get("https://api.alternative.me/fng/")
    data = r.json()['data'][0]
    return data['value'], data['value_classification']

def make_progress_bar(value):
    filled = int(int(value) / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty

def get_ai_analysis(prices):
    btc = prices['bitcoin']
    eth = prices['ethereum']
    sol = prices['solana']

    prompt = f"""You are the admin of a crypto Discord channel called Future Admiral.
Write a daily market update. Follow this EXACT format — do not add anything outside it.

Today's data:
- BTC: ${btc['usd']:,} ({btc['usd_24h_change']:+.2f}%)
- ETH: ${eth['usd']:,} ({eth['usd_24h_change']:+.2f}%)
- SOL: ${sol['usd']:,} ({sol['usd_24h_change']:+.2f}%)

FORMAT:

👨‍✈️ CAPTAIN'S BRIEFING (Roman Urdu)
▸ [BTC situation 2 lines Roman Urdu]
▸ [OI/Funding rates warning Roman Urdu]
▸ TRAP SE BACHEIN: [specific resistance level to watch]

---SPLIT---

🔬 TECHNICAL ANALYSIS
🔴 Resistance → [level]
🟢 Support    → [level]
📉 Flush Zone → [level if support breaks]

📌 Key Observations:
- [TA point 1]
- [BTC dominance impact on alts]
- [RSI or momentum]
- [Liquidity observation]

---SPLIT---

⚔️ ADMIRAL'S ORDERS
✅ [action 1]
✅ [action 2]
✅ [action 3]
❌ [warning 1]
❌ [warning 2]

---SPLIT---

📡 COIN TO WATCH TODAY
👀 [Coin name] — [2 line observation, key level to watch]"""

    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/future-admiral-bot",
        "X-Title": "Future Admiral Bot"
    }
    body = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=30
        )
        print(f"OpenRouter status: {r.status_code}")
        print(f"OpenRouter response: {r.text[:300]}")
        
        data = r.json()
        
        if 'choices' in data:
            return data['choices'][0]['message']['content']
        elif 'error' in data:
            print(f"API Error: {data['error']}")
            return get_fallback_analysis(prices)
        else:
            print(f"Unexpected response: {data}")
            return get_fallback_analysis(prices)
            
    except Exception as e:
        print(f"Exception: {e}")
        return get_fallback_analysis(prices)


def get_fallback_analysis(prices):
    btc = prices['bitcoin']
    change = btc['usd_24h_change']
    direction = "upar" if change > 0 else "neeche"
    
    return f"""👨‍✈️ CAPTAIN'S BRIEFING (Roman Urdu)
▸ BTC ${btc['usd']:,} par trade kar raha hai, 24h mein {abs(change):.1f}% {direction} gaya hai. Market carefully observe karo.
▸ Bina proper analysis ke trade mat karo — capital protect karna pehli priority hai.
▸ TRAP SE BACHEIN: Sirf confirmed breakout par hi entry lo, emotion mein mat aao.

---SPLIT---

🔬 TECHNICAL ANALYSIS
🔴 Resistance → Key levels monitor karein
🟢 Support    → Recent lows watch karein
📉 Flush Zone → Support break hone par caution

📌 Key Observations:
- Market volatility high — position sizing dhyan se karo
- BTC Dominance high hone par Alts pe pressure rahega
- RSI neutral zone mein — koi bhi side move possible
- Volume confirmation zaroor dekho entry se pehle

---SPLIT---

⚔️ ADMIRAL'S ORDERS
✅ Apna trading plan follow karo
✅ Stop loss zaroor lagao
✅ Small position size rakho
❌ High leverage se door raho
❌ FOMO mein entry mat lo

---SPLIT---

📡 COIN TO WATCH TODAY
👀 Bitcoin (BTC) — Key levels pe nazar rakho. Confirmation ke baad hi move karo."""
