import os
# ==========================================
# Telegram Configuration
# ==========================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


if not BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN غير موجود في GitHub Secrets"
    )

if not CHANNEL_ID:
    raise ValueError(
        "TELEGRAM_CHANNEL_ID غير موجود في GitHub Secrets"
    )


# ==========================================
# Deduplication
# ==========================================

DEDUP_FILE = "sent_news.json"


# ==========================================
# News Keywords
# ==========================================

KEYWORDS = [
    "gold",
    "xau",
    "xauusd",
    "precious metals",

    "forex",
    "currency",
    "currencies",
    "dollar",
    "usd",
    "euro",
    "eur",
    "pound",
    "gbp",
    "yen",
    "jpy",

    "fed",
    "federal reserve",
    "interest rate",
    "interest rates",
    "central bank",
    "monetary policy",
    "rate cut",
    "rate hike",

    "inflation",
    "cpi",
    "ppi",
    "nfp",
    "nonfarm payrolls",
    "jobs",
    "employment",
    "unemployment",
    "gdp",
    "retail sales",
    "consumer confidence",
    "economic data",

    "oil",
    "crude oil",
    "brent",
    "wti",
    "opec",

    "crypto",
    "cryptocurrency",
    "bitcoin",
    "btc",
    "ethereum",
    "eth",

    "stock market",
    "stocks",
    "shares",
    "market",
    "markets",
    "wall street",
    "nasdaq",
    "dow jones",
    "s&p 500",
    "sp500",

    "treasury",
    "bond",
    "bonds",
    "yield",
    "yields",

    "economy",
    "economic",
    "recession",
    "geopolitics",
    "geopolitical",
    "sanctions",
    "trade war",
]


# ==========================================
# RSS NEWS SOURCES
# ==========================================

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",

    "https://news.google.com/rss/search?q=gold+XAUUSD&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=forex+USD+currency&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=Federal+Reserve+interest+rates&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=inflation+CPI+economy&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=oil+Brent+WTI+OPEC&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=Bitcoin+Ethereum+crypto&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=stock+market+Wall+Street&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=economic+data+GDP+jobs&hl=en-US&gl=US&ceid=US:en",

    "https://news.google.com/rss/search?q=geopolitics+markets&hl=en-US&gl=US&ceid=US:en",
]


print("=" * 50)
print("Eagle Max 24 Configuration")
print("=" * 50)
print(f"RSS Sources: {len(RSS_FEEDS)}")
print(f"Keywords: {len(KEYWORDS)}")
print("Telegram configuration loaded")
print("=" * 50)
