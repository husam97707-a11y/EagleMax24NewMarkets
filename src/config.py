import feedparser
import hashlib
import json
import time
import re
from datetime import datetime
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.error import TelegramError

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

translator = GoogleTranslator(source='en', target='ar')
bot = Bot(token=config.BOT_TOKEN)
