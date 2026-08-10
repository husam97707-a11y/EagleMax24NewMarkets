```python
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


# ==============================
# إعداد المترجم والبوت
# ==============================

translator = GoogleTranslator(
    source="en",
    target="ar"
)

bot = Bot(
    token=config.BOT_TOKEN
)


# ==============================
# تحميل الأخبار المرسلة سابقًا
# ==============================

def load_sent_news():
    try:
        with open(config.DEDUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

    except Exception as e:
        print(f"خطأ في تحميل الأخبار السابقة: {e}")
        return []


# ==============================
# حفظ الأخبار المرسلة
# ==============================

def save_sent_news(news_list):
    try:
        if len(news_list) > 500:
            news_list = news_list[-500:]

        with open(config.DEDUP_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"خطأ في حفظ الأخبار: {e}")


# ==============================
# إنشاء بصمة للخبر لمنع التكرار
# ==============================

def get_news_hash(title, summary):
    text = (title + " " + summary)[:500]

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()


# ==============================
# فلترة الأخبار حسب الكلمات
# ==============================

def filter_news(title, summary):
    text = (title + " " + summary).lower()

    for keyword in config.KEYWORDS:
        if keyword.lower() in text:
            return True

    return False


# ==============================
# ترجمة النص
# ==============================

def translate_text(text):
    if not text:
        return ""

    try:
        result = translator.translate(text)
        return result

    except Exception as e:
        print(f"خطأ في الترجمة: {e}")
        return text


# ==============================
# تنسيق الخبر
# ==============================

def format_news(title, summary, link, published):

    ar_title = translate_text(title)
    ar_summary = translate_text(summary[:300])

    # الوقت
    try:
        dt = datetime(*published[:6])

        time_str = dt.strftime(
            "%d %B %Y - %H:%M"
        ) + " بتوقيت مكة"

    except Exception:
        time_str = datetime.now().strftime(
            "%d %B %Y - %H:%M"
        ) + " بتوقيت مكة"

    # ==========================
    # تحديد قوة التأثير
    # ==========================

    text_lower = (title + " " + summary).lower()

    impact = "🟡 متوسطة"

    strong_words = [
        "surge",
        "soar",
        "plunge",
        "crash",
        "record"
    ]

    positive_words = [
        "rise",
        "gain",
        "growth",
        "increase"
    ]

    negative_words = [
        "fall",
        "drop",
        "decline",
        "loss"
    ]

    if any(word in text_lower for word in strong_words):
        impact = "🔴 قوية"

    elif any(word in text_lower for word in positive_words):
        impact = "🟢 إيجابية"

    elif any(word in text_lower for word in negative_words):
        impact = "🔴 سلبية"

    # ==========================
    # استخراج اسم المصدر
    # ==========================

    try:
        source = link.split("/")[2]

    except Exception:
        source = "وكالات"

    # ==========================
    # إنشاء الرسالة
    # ==========================

    message = f"""
📰 <b>المصدر:</b> {source}

⏰ <b>الوقت:</b> {time_str}

🇸🇦 <b>العنوان:</b>
{ar_title}

{ar_summary}

📊 <b>التأثير المتوقع:</b> {impact}

🔗 <a href="{link}">قراءة الخبر</a>

#XAUUSD #GOLD #FOREX #اقتصاد
"""

    return message.strip()


# ==============================
# جلب الأخبار من RSS
# ==============================

def fetch_news():

    all_news = []

    sent_hashes = load_sent_news()

    for feed_url in config.RSS_FEEDS:

        try:

            print(f"🔎 فحص المصدر: {feed_url}")

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:5]:

                title = entry.get(
                    "title",
                    ""
                )

                summary = (
                    entry.get("summary", "")
                    or entry.get("description", "")
                )

                link = entry.get(
                    "link",
                    ""
                )

                published = entry.get(
                    "published_parsed",
                    time.localtime()
                )

                # إزالة HTML من الملخص
                summary = re.sub(
                    r"<[^<]+?>",
                    "",
                    summary
                )

                # التأكد من وجود عنوان
                if not title:
                    continue

                # فلترة الأخبار
                if not filter_news(title, summary):
                    continue

                # إنشاء Hash
                news_hash = get_news_hash(
                    title,
                    summary
                )

                # منع الأخبار المكررة
                if news_hash in sent_hashes:
                    continue

                # تنسيق الخبر
                message = format_news(
                    title,
                    summary,
                    link,
                    published
                )

                all_news.append(
                    (news_hash, message)
                )

        except Exception as e:

            print(
                f"❌ خطأ في المصدر {feed_url}: {e}"
            )

    return all_news


# ==============================
# إرسال الخبر إلى Telegram
# ==============================

def send_to_telegram(message):

    try:

        bot.send_message(
            chat_id=config.CHANNEL_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False
        )

        return True

    except TelegramError as e:

        print(
            f"❌ خطأ في إرسال Telegram: {e}"
        )

        return False

    except Exception as e:

        print(
            f"❌ خطأ غير متوقع أثناء الإرسال: {e}"
        )

        return False


# ==============================
# تشغيل البوت
# ==============================

def main():

    print(
        f"🚀 بدء جلب الأخبار - {datetime.now()}"
    )

    news_list = fetch_news()

    if not news_list:

        print(
            "📭 لا توجد أخبار جديدة"
        )

        return

    sent_hashes = load_sent_news()

    sent_count = 0

    for news_hash, message in news_list:

        if send_to_telegram(message):

            sent_hashes.append(
                news_hash
            )

            sent_count += 1

            print(
                "✅ تم إرسال خبر"
            )

            # تأخير بين الأخبار
            time.sleep(2)

    save_sent_news(
        sent_hashes
    )

    print(
        f"✅ تم إرسال {sent_count} أخبار جديدة"
    )


# ==============================
# نقطة تشغيل البرنامج
# ==============================

if __name__ == "__main__":
    main()
```
