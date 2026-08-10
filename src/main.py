import feedparser
import hashlib
import json
import time
import re
from datetime import datetime
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.error import TelegramError
import config

translator = GoogleTranslator(source='en', target='ar')
bot = Bot(token=config.BOT_TOKEN)

def load_sent_news():
    try:
        with open(config.DEDUP_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_sent_news(news_list):
    if len(news_list) > 500:
        news_list = news_list[-500:]
    with open(config.DEDUP_FILE, 'w') as f:
        json.dump(news_list, f)

def get_news_hash(title, summary):
    text = (title + ' ' + summary)[:200]
    return hashlib.md5(text.encode()).hexdigest()

def filter_news(title, summary):
    text = (title + ' ' + summary).lower()
    for keyword in config.KEYWORDS:
        if keyword.lower() in text:
            return True
    return False

def translate_text(text):
    try:
        result = translator.translate(text)
        return result
    except:
        return text

def format_news(title, summary, link, published):
    ar_title = translate_text(title)
    ar_summary = translate_text(summary[:300])
    
    try:
        dt = datetime(*published[:6])
        time_str = dt.strftime('%d %B %Y - %H:%M بتوقيت مكة')
    except:
        time_str = datetime.now().strftime('%d %B %Y - %H:%M بتوقيت مكة')
    
    impact = "🟡 متوسطة"
    if any(word in (title + summary).lower() for word in ['surge', 'soar', 'plunge', 'crash', 'record']):
        impact = "🔴 قوية"
    elif any(word in (title + summary).lower() for word in ['rise', 'fall', 'drop', 'gain']):
        impact = "🟢 إيجابية" if 'rise' in (title + summary).lower() else "🔴 سلبية"
    
    message = f"""
📰 المصدر: {link.split('/')[2] if 'http' in link else 'وكالات'}
⏰ الوقت: {time_str}
🇸🇦 العنوان: {ar_title}

{ar_summary}

📊 التأثير المتوقع: {impact}

🔗 {link}

#XAUUSD #GOLD #FOREX #اقتصاد
"""
    return message

def fetch_news():
    all_news = []
    sent_hashes = load_sent_news()
    
    for feed_url in config.RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')
                published = entry.get('published_parsed', time.localtime())
                
                summary = re.sub('<[^<]+?>', '', summary)
                
                if not filter_news(title, summary):
                    continue
                
                news_hash = get_news_hash(title, summary)
                if news_hash in sent_hashes:
                    continue
                
                message = format_news(title, summary, link, published)
                all_news.append((news_hash, message))
                
        except Exception as e:
            print(f"خطأ في المصدر {feed_url}: {e}")
    
    return all_news

def send_to_telegram(message):
    try:
        bot.send_message(chat_id=config.CHANNEL_ID, text=message, parse_mode='HTML')
        return True
    except TelegramError as e:
        print(f"خطأ في الإرسال: {e}")
        return False

def main():
    print(f"🚀 بدء جلب الأخبار - {datetime.now()}")
    news_list = fetch_news()
    
    if not news_list:
        print("📭 لا توجد أخبار جديدة")
        return
    
    sent_hashes = load_sent_news()
    for news_hash, message in news_list:
        if send_to_telegram(message):
            sent_hashes.append(news_hash)
            print(f"✅ تم إرسال خبر")
            time.sleep(2)
    
    save_sent_news(sent_hashes)
    print(f"✅ تم إرسال {len(news_list)} أخبار جديدة")

if __name__ == "__main__":
    main()
