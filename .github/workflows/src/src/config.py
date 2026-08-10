import os

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

RSS_FEEDS = [
    'https://feeds.reuters.com/reuters/businessNews',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'https://www.alarabiya.net/feed/rss.xml',
    'https://aawsat.com/feed/rss.xml'
]

KEYWORDS = [
    'ذهب', 'gold', 'xauusd',
    'دولار', 'dollar', 'usd',
    'نفط', 'oil', 'brent', 'wti',
    'فائدة', 'interest rate', 'fed',
    'فوركس', 'forex', 'eurusd', 'gbpusd',
    'اقتصاد', 'economy', 'inflation',
    'تراجع', 'ارتفع', 'انخفاض', 'صعود'
]

DEDUP_FILE = 'sent_news.json'
