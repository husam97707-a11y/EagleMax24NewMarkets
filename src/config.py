import os


# =========================
# Telegram
# =========================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


# =========================
# Deduplication
# =========================

DEDUP_FILE = "sent_news.json"


# =========================
# Keywords
# =========================

KEYWORDS = [
    "gold",
    "xau",
    "xauusd",
    "forex",
    "currency",
    "dollar",
    "usd",
    "fed",
    "federal reserve",
    "interest rate",
    "interest rates",
    "inflation",
    "cpi",
    "ppi",
    "nfp",
    "jobs",
    "employment",
    "unemployment",
    "oil",
    "crude oil",
    "crypto",
    "bitcoin",
    "ethereum",
    "economy",
    "economic",
    "economic data",
    "market",
    "markets",
    "stocks",
    "treasury",
    "bond",
    "geopolitics"
]


# =========================
# RSS Sources
# =========================

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]


# =========================
# Configuration check
# =========================

if not BOT_TOKEN:
    raise ValueError(
        "❌ TELEGRAM_BOT_TOKEN غير موجود في GitHub Secrets"
    )


if not CHANNEL_ID:
    raise ValueError(
        "❌ TELEGRAM_CHANNEL_ID غير موجود في GitHub Secrets"
    )
```
