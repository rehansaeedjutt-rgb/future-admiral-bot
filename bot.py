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
👀 [Coin name] — [2 line observation, key level to watch]

RULES:
- Roman Urdu only in Captain's Briefing
- English everywhere else
- Confident senior trader tone
- No extra text outside the format"""

    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_KEY']}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=body
    )
    return r.json()['choices'][0]['message']['content']

def build_message(prices, fg_value, fg_label, ai_text):
    btc = prices['bitcoin']
    eth = prices['ethereum']
    sol = prices['solana']

    parts = ai_text.split("---SPLIT---")
    briefing = parts[0].strip() if len(parts) > 0 else ""
    technical = parts[1].strip() if len(parts) > 1 else ""
    orders    = parts[2].strip() if len(parts) > 2 else ""
    coin      = parts[3].strip() if len(parts) > 3 else ""

    bar = make_progress_bar(fg_value)
    now = datetime.now().strftime("%A, %d %B %Y")

    message = f"""🌅 Assalam-o-Alaikum & Good Morning!
🚢 Future Admiral Family — Discipline is the Strategy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ⚓ FUTURE ADMIRAL
     MARKET INTELLIGENCE DESK
     📅 {now}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{briefing}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MARKET SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠 BTC   ${btc['usd']:,}   {btc['usd_24h_change']:+.2f}%
🔵 ETH   ${eth['usd']:,}    {eth['usd_24h_change']:+.2f}%
🟣 SOL   ${sol['usd']:,}     {sol['usd_24h_change']:+.2f}%
📈 Market Cap  ~$2.4T

😨 Fear & Greed:  {fg_value} — {fg_label}
   {bar}  Keep emotions in check!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{orders}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{coin}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚢 Stay disciplined. Stay in the fleet.
⚓ Future Admiral — Har Roz. Har Trade.
🔔 Next update: Kal 9:00 AM PKT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    return message

def send_to_discord(message):
    webhook = os.environ['DISCORD_WEBHOOK']
    data = {
        "content": message,
        "username": "Future Admiral ⚓",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"
    }
    r = requests.post(webhook, json=data)
    print(f"Discord response: {r.status_code}")

# --- Run ---
print("Fetching prices...")
prices = get_prices()

print("Fetching Fear & Greed...")
fg_value, fg_label = get_fear_greed()

print("Getting AI analysis...")
ai_text = get_ai_analysis(prices)

print("Building message...")
message = build_message(prices, fg_value, fg_label, ai_text)

print("Sending to Discord...")
send_to_discord(message)
print("✅ Done!")
