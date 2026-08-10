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


if not config.BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN غير موجود")

if not config.CHANNEL_ID:
    raise ValueError("TELEGRAM_CHANNEL_ID غير موجود")


translator = GoogleTranslator(
    source="en",
    target="ar"
)

bot = Bot(
    token=config.BOT_TOKEN
)


def load_sent_news():
    try:
        with open(
            config.DEDUP_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (FileNotFoundError, json.JSONDecodeError):
        return []

    except Exception as error:
        print(f"خطأ في تحميل الأخبار: {error}")
        return []


def save_sent_news(news_list):
    try:
        if len(news_list) > 500:
            news_list = news_list[-500:]

        with open(
            config.DEDUP_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                news_list,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as error:
        print(f"خطأ في حفظ الأخبار: {error}")


def get_news_hash(title, summary):
    text = (
        title.strip()
        + " "
        + summary.strip()
    ).lower()

    return hashlib.md5(
        text[:500].encode("utf-8")
    ).hexdigest()


def filter_news(title, summary):
    text = (
        title
        + " "
        + summary
    ).lower()

    return any(
        keyword.lower() in text
        for keyword in config.KEYWORDS
    )


def clean_html(text):
    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def translate_text(text):
    if not text:
        return ""

    try:
        return translator.translate(text)

    except Exception as error:
        print(f"خطأ في الترجمة: {error}")
        return text


def detect_impact(title, summary):
    text = (
        title
        + " "
        + summary
    ).lower()

    strong_words = [
        "surge",
        "soar",
        "plunge",
        "crash",
        "record",
        "shock",
        "crisis"
    ]

    positive_words = [
        "rise",
        "gain",
        "growth",
        "increase",
        "higher",
        "strong"
    ]

    negative_words = [
        "fall",
        "drop",
        "decline",
        "loss",
        "lower",
        "weak"
    ]

    if any(word in text for word in strong_words):
        return "🔴 قوية"

    if any(word in text for word in positive_words):
        return "🟢 إيجابية"

    if any(word in text for word in negative_words):
        return "🔴 سلبية"

    return "🟡 متوسطة"


def format_news(title, summary, link, published):

    ar_title = translate_text(title)
    ar_summary = translate_text(summary[:500])

    try:
        dt = datetime(*published[:6])
        time_str = dt.strftime(
            "%d-%m-%Y %H:%M"
        )

    except Exception:
        time_str = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

    impact = detect_impact(
        title,
        summary
    )

    try:
        source = link.split("/")[2]
    except Exception:
        source = "وكالات"

    message = (
        f"📰 <b>المصدر:</b> {source}\n\n"
        f"⏰ <b>الوقت:</b> {time_str}\n\n"
        f"🇸🇦 <b>العنوان:</b>\n"
        f"{ar_title}\n\n"
        f"{ar_summary}\n\n"
        f"📊 <b>التأثير المتوقع:</b> {impact}\n\n"
        f'🔗 <a href="{link}">قراءة الخبر</a>\n\n'
        f"#XAUUSD #GOLD #FOREX #اقتصاد"
    )

    return message


def fetch_news():

    all_news = []
    sent_hashes = load_sent_news()

    for feed_url in config.RSS_FEEDS:

        print(f"🔎 فحص المصدر: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                print("⚠️ لا توجد أخبار في هذا المصدر")
                continue

            for entry in feed.entries[:10]:

                title = entry.get(
                    "title",
                    ""
                )

                summary = entry.get(
                    "summary",
                    ""
                )

                if not summary:
                    summary = entry.get(
                        "description",
                        ""
                    )

                link = entry.get(
                    "link",
                    ""
                )

                published = entry.get(
                    "published_parsed",
                    time.localtime()
                )

                title = clean_html(title)
                summary = clean_html(summary)

                if not title:
                    continue

                if not filter_news(
                    title,
                    summary
                ):
                    continue

                news_hash = get_news_hash(
                    title,
                    summary
                )

                if news_hash in sent_hashes:
                    continue

                message = format_news(
                    title,
                    summary,
                    link,
                    published
                )

                all_news.append(
                    (
                        news_hash,
                        message
                    )
                )

        except Exception as error:
            print(
                f"❌ خطأ في المصدر "
                f"{feed_url}: {error}"
            )

    return all_news


def send_to_telegram(message):

    try:
        bot.send_message(
            chat_id=config.CHANNEL_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False
        )

        return True

    except TelegramError as error:
        print(
            f"❌ خطأ Telegram: {error}"
        )
        return False

    except Exception as error:
        print(
            f"❌ خطأ أثناء الإرسال: {error}"
        )
        return False


def main():

    print("=" * 50)
    print("🚀 Eagle Max 24 News Bot")
    print(
        f"⏰ وقت التشغيل: {datetime.now()}"
    )
    print("=" * 50)

    news_list = fetch_news()

    if not news_list:
        print("📭 لا توجد أخبار جديدة")
        return

    print(
        f"📰 تم العثور على "
        f"{len(news_list)} أخبار جديدة"
    )

    sent_hashes = load_sent_news()
    sent_count = 0

    for news_hash, message in news_list:

        if send_to_telegram(message):

            sent_hashes.append(news_hash)
            sent_count += 1

            print("✅ تم إرسال خبر بنجاح")

            time.sleep(2)

        else:
            print("❌ فشل إرسال الخبر")

    save_sent_news(sent_hashes)

    print("=" * 50)
    print(
        f"✅ تم إرسال {sent_count} أخبار"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()
