```python
import os


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


DEDUP_FILE = "sent_news.json"


KEYWORDS = [
    "gold",
    "xau",
    "forex",
    "currency",
    "dollar",
    "usd",
    "fed",
    "federal reserve",
    "interest rate",
    "inflation",
    "cpi",
    "ppi",
    "nfp",
    "jobs",
    "employment",
    "oil",
    "crypto",
    "bitcoin",
    "ethereum",
    "economy",
    "economic",
    "market",
    "markets"
]


RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]
```
