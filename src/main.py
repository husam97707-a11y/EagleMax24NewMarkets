
import asyncio
import feedparser
import hashlib
import json
import re

from datetime import datetime
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.error import TelegramError

import config


# ==========================================
# Translator
# ==========================================

translator = GoogleTranslator(
    source="en",
    target="ar"
)


# ==========================================
# Load sent news
# ==========================================

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

    except FileNotFoundError:

        return []

    except json.JSONDecodeError:

        return []

    except Exception as error:

        print(f"❌ خطأ تحميل قاعدة الأخبار: {error}")

        return []


# ==========================================
# Save sent news
# ==========================================

def save_sent_news(news_list):

    try:

        # Keep last 500 hashes
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

        print(
            f"💾 تم حفظ {len(news_list)} خبر في قاعدة التكرار"
        )

    except Exception as error:

        print(
            f"❌ خطأ حفظ قاعدة الأخبار: {error}"
        )


# ==========================================
# Generate news hash
# ==========================================

def get_news_hash(title, link):

    text = (
        title.strip()
        + "|"
        + link.strip()
    ).lower()

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ==========================================
# Clean HTML
# ==========================================

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


# ==========================================
# Keyword filter
# ==========================================

def find_matching_keywords(
    title,
    summary
):

    text = (
        title
        + " "
        + summary
    ).lower()

    matches = []

    for keyword in config.KEYWORDS:

        if keyword.lower() in text:

            matches.append(keyword)

    return matches


# ==========================================
# Translation
# ==========================================

def translate_text(text):

    if not text:
        return ""

    try:

        return translator.translate(
            text
        )

    except Exception as error:

        print(
            f"⚠️ فشل الترجمة: {error}"
        )

        return text


# ==========================================
# Impact analysis
# ==========================================

def detect_impact(
    title,
    summary
):

    text = (
        title
        + " "
        + summary
    ).lower()

    strong_words = [
        "crash",
        "collapse",
        "plunge",
        "surge",
        "soar",
        "record",
        "crisis",
        "shock",
        "war",
        "sanctions",
    ]

    positive_words = [
        "rise",
        "gain",
        "growth",
        "increase",
        "higher",
        "strong",
        "boost",
    ]

    negative_words = [
        "fall",
        "drop",
        "decline",
        "loss",
        "lower",
        "weak",
        "cut",
    ]

    if any(
        word in text
        for word in strong_words
    ):

        return "🔴 قوي"

    if any(
        word in text
        for word in positive_words
    ):

        return "🟢 إيجابي"

    if any(
        word in text
        for word in negative_words
    ):

        return "🔴 سلبي"

    return "🟡 متوسط"


# ==========================================
# Format Telegram message
# ==========================================

def format_news(
    title,
    summary,
    link,
    published,
    matched_keywords,
    source
):

    ar_title = translate_text(
        title
    )

    ar_summary = translate_text(
        summary[:700]
    )

    impact = detect_impact(
        title,
        summary
    )

    try:

        if published:

            dt = datetime(
                *published[:6]
            )

            time_str = dt.strftime(
                "%d-%m-%Y %H:%M"
            )

        else:

            time_str = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )

    except Exception:

        time_str = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

    keyword_text = ", ".join(
        matched_keywords[:5]
    )

    message = (
        f"🚨 <b>Eagle Max 24</b>\n\n"

        f"📰 <b>المصدر:</b> "
        f"{source}\n\n"

        f"⏰ <b>الوقت:</b> "
        f"{time_str}\n\n"

        f"📌 <b>العنوان:</b>\n"
        f"{ar_title}\n\n"

        f"📝 <b>التفاصيل:</b>\n"
        f"{ar_summary}\n\n"

        f"📊 <b>التأثير المتوقع:</b> "
        f"{impact}\n\n"

        f"🔎 <b>الكلمات المطابقة:</b> "
        f"{keyword_text}\n\n"

        f'🔗 <a href="{link}">قراءة الخبر</a>\n\n'

        f"#XAUUSD #GOLD #FOREX #NEWS"
    )

    return message


# ==========================================
# Fetch all news
# ==========================================

def fetch_news():

    all_news = []

    sent_hashes = set(
        load_sent_news()
    )

    total_received = 0
    total_matched = 0

    print("")
    print("=" * 50)
    print("📡 بدء فحص مصادر الأخبار")
    print("=" * 50)

    for feed_url in config.RSS_FEEDS:

        print("")
        print(f"🔎 المصدر:")
        print(feed_url)

        try:

            feed = feedparser.parse(
                feed_url
            )

            entries = feed.entries

            print(
                f"📥 الأخبار المستلمة: "
                f"{len(entries)}"
            )

            total_received += len(entries)

            if not entries:

                print(
                    "⚠️ المصدر لم يعطِ أخبارًا"
                )

                continue

            for entry in entries[:20]:

                title = clean_html(
                    entry.get(
                        "title",
                        ""
                    )
                )

                summary = clean_html(
                    entry.get(
                        "summary",
                        ""
                    )
                )

                if not summary:

                    summary = clean_html(
                        entry.get(
                            "description",
                            ""
                        )
                    )

                link = entry.get(
                    "link",
                    ""
                )

                if not title:

                    continue

                matches = find_matching_keywords(
                    title,
                    summary
                )

                if not matches:

                    continue

                total_matched += 1

                news_hash = get_news_hash(
                    title,
                    link
                )

                if news_hash in sent_hashes:

                    print(
                        f"⏭️ مكرر: {title[:80]}"
                    )

                    continue

                source = feed.feed.get(
                    "title",
                    "News"
                )

                published = entry.get(
                    "published_parsed",
                    None
                )

                message = format_news(
                    title,
                    summary,
                    link,
                    published,
                    matches,
                    source
                )

                all_news.append(
                    (
                        news_hash,
                        message
                    )
                )

                print(
                    f"🆕 خبر جديد: "
                    f"{title[:100]}"
                )

        except Exception as error:

            print(
                f"❌ خطأ في المصدر:"
            )

            print(
                f"{error}"
            )

    print("")
    print("=" * 50)
    print(
        f"📥 إجمالي الأخبار المستلمة: "
        f"{total_received}"
    )

    print(
        f"🎯 الأخبار المطابقة: "
        f"{total_matched}"
    )

    print(
        f"🆕 الأخبار الجديدة: "
        f"{len(all_news)}"
    )

    print("=" * 50)

    return all_news


# ==========================================
# Send Telegram
# ==========================================

async def send_to_telegram(
    bot,
    message
):

    try:

        await bot.send_message(
            chat_id=config.CHANNEL_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False
        )

        return True

    except TelegramError as error:

        print(
            f"❌ Telegram Error: {error}"
        )

        return False

    except Exception as error:

        print(
            f"❌ Send Error: {error}"
        )

        return False


# ==========================================
# Main
# ==========================================

async def main():

    print("")
    print("=" * 60)
    print("🚀 EAGLE MAX 24 NEWS BOT")
    print("=" * 60)

    print(
        f"⏰ وقت التشغيل: "
        f"{datetime.now()}"
    )

    print(
        f"📡 عدد المصادر: "
        f"{len(config.RSS_FEEDS)}"
    )

    print(
        f"🔎 عدد الكلمات: "
        f"{len(config.KEYWORDS)}"
    )

    print("=" * 60)

    news_list = fetch_news()

    if not news_list:

        print("")
        print(
            "📭 لا توجد أخبار جديدة للإرسال"
        )

        return

    sent_hashes = load_sent_news()

    sent_count = 0

    print("")
    print(
        f"📤 بدء إرسال "
        f"{len(news_list)} أخبار إلى Telegram"
    )

    print("")

    async with Bot(
        token=config.BOT_TOKEN
    ) as bot:

        # Telegram connection test
        try:

            me = await bot.get_me()

            print(
                f"🤖 Telegram Bot: "
                f"@{me.username}"
            )

        except Exception as error:

            print(
                f"❌ فشل الاتصال بـ Telegram: "
                f"{error}"
            )

            return

        for news_hash, message in news_list:

            success = await send_to_telegram(
                bot,
                message
            )

            if success:

                sent_hashes.append(
                    news_hash
                )

                sent_count += 1

                print(
                    "✅ تم إرسال خبر بنجاح"
                )

                await asyncio.sleep(2)

            else:

                print(
                    "❌ فشل إرسال الخبر"
                )

    save_sent_news(
        sent_hashes
    )

    print("")
    print("=" * 60)

    print(
        f"📤 تم إرسال: "
        f"{sent_count}"
    )

    print(
        f"❌ فشل: "
        f"{len(news_list) - sent_count}"
    )

    print("=" * 60)

    print(
        "🏁 انتهى التشغيل"
    )


# ==========================================
# Start
# ==========================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
```
