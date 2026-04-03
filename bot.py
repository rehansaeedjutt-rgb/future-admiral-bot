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

def get_ai_analysis(prices):
    btc = prices['bitcoin']
    eth = prices['ethereum']
    sol = prices['solana']

    prompt = f"""You are the admin of a crypto Discord channel called "Future Admiral".
Write a daily market update in the EXACT style and structure shown below.
Use the live data provided. Do NOT add anything outside this format.

Live Data:
- BTC: ${btc['usd']:,} ({btc['usd_24h_change']:+.2f}%)
- ETH: ${eth['usd']:,} ({eth['usd_24h_change']:+.2f}%)
- SOL: ${sol['usd']:,} ({sol['usd_24h_change']:+.2f}%)

EXACT FORMAT TO FOLLOW:

Assalam-o-Alaikum and Good Morning, my Future Admiral family! Hope you all are disciplined and sticking to the plan. Market is showing some interesting moves, let's break it down.

FUTURE ADMIRAL | MARKET INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━

---SPLIT---

ADMIN ADVICE (Roman Urdu)
• [2-3 bullet points in Roman Urdu about current BTC situation, OI/Funding rates warning, and trap levels — exactly like a senior trader talking to his community]

---SPLIT---

CORE MARKET SNAPSHOT
• Bitcoin (BTC): ${btc['usd']:,} ({btc['usd_24h_change']:+.2f}%)
• Ethereum (ETH): ${eth['usd']:,} ({eth['usd_24h_change']:+.2f}%)
• Solana (SOL): ${sol['usd']:,} ({sol['usd_24h_change']:+.2f}%)
• Market Cap: [estimate]
• BTC Dominance: [estimate]%

---SPLIT---

TECHNICAL ANALYSIS (English)
• [3 bullet points — resistance/support zones, BTC dominance impact on alts, RSI and liquidity observations — confident senior trader tone]

---SPLIT---

STRATEGY
• Leverage: [specific advice based on current market]
• Stop-Loss: [specific SL levels based on current price]
• [1 closing motivational line]

Discipline is the key to Wealth.
Future Admiral

STRICT RULES:
- Roman Urdu ONLY in Admin Advice section
- English everywhere else
- Bullet points with • symbol only
- No emojis anywhere
- Confident, senior trader tone throughout
- Keep it concise exactly like the example"""

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
    eth = prices['ethereum']
    sol = prices['solana']
    change = btc['usd_24h_change']
    direction = "upar" if change > 0 else "neeche"

    return f"""Assalam-o-Alaikum and Good Morning, my Future Admiral family! Hope you all are disciplined and sticking to the plan. Market is showing some interesting moves, let's break it down.

FUTURE ADMIRAL | MARKET INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━

---SPLIT---

ADMIN ADVICE (Roman Urdu)
• Dosto, BTC is waqt ${btc['usd']:,} ki range mein trade kar raha hai, 24 ghanton mein {abs(change):.1f}% {direction} gaya hai. Market ko carefully observe karo aur jaldi mein koi decision mat lo.
• Bina proper analysis ke trade mat karo — capital protect karna pehli priority hai. Risk management ko kabhi ignore mat karo.
• TRAP SE BACHEIN: Sirf confirmed breakout par hi entry lo. Apne jazbaat ko side par rakh kar sirf chart ko follow karein.

---SPLIT---

CORE MARKET SNAPSHOT
• Bitcoin (BTC): ${btc['usd']:,} ({btc['usd_24h_change']:+.2f}%)
• Ethereum (ETH): ${eth['usd']:,} ({eth['usd_24h_change']:+.2f}%)
• Solana (SOL): ${sol['usd']:,} ({sol['usd_24h_change']:+.2f}%)
• Market Cap: ~$2.4T
• BTC Dominance: ~55-57%

---SPLIT---

TECHNICAL ANALYSIS (English)
• BTC is trading at key levels. Watch for resistance and support zones carefully before making any entry. Volume confirmation is essential.
• BTC Dominance remains elevated — this is a warning sign for Altcoins. If BTC sees any selling pressure, Alts will bleed significantly. Be cautious with altcoin positions.
• RSI is in neutral territory, giving room for a move in either direction. Look for liquidity sweeps before any major directional move.

---SPLIT---

STRATEGY
• Leverage: Strictly 3x to 5x. Avoid gambling in this choppy range.
• Stop-Loss: Place your SLs below recent lows for long positions. Stay nimble and take profits early.
• Discipline is the key to Wealth.

Discipline is the key to Wealth.
Future Admiral"""


def build_message(prices, fg_value, fg_label, ai_text):
    parts = ai_text.split("---SPLIT---")

    header   = parts[0].strip() if len(parts) > 0 else ""
    advice   = parts[1].strip() if len(parts) > 1 else ""
    snapshot = parts[2].strip() if len(parts) > 2 else ""
    analysis = parts[3].strip() if len(parts) > 3 else ""
    strategy = parts[4].strip() if len(parts) > 4 else ""

    now = datetime.now().strftime("%A, %d %B %Y")

    message = f"""{header}

{advice}

━━━━━━━━━━━━━━━━━━━━━

{snapshot}

Fear & Greed Index: {fg_value} — {fg_label}

━━━━━━━━━━━━━━━━━━━━━

{analysis}

━━━━━━━━━━━━━━━━━━━━━

{strategy}

━━━━━━━━━━━━━━━━━━━━━
Date: {now}"""

    return message


def send_to_discord(message):
    webhook = os.environ['DISCORD_WEBHOOK']
    print(f"Webhook URL being used: {webhook[:50]}...")
    data = {
        "content": message,
        "username": "Future Admiral"
    }
    r = requests.post(webhook, json=data)
    print(f"Discord status code: {r.status_code}")
    print(f"Discord response: {r.text}")


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
print("Done!")
