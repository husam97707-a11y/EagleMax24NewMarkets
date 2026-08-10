```python
import feedparser
import hashlib
import json
import time
import re
import sys

from datetime import datetime
from pathlib import Path
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.error import TelegramError

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

translator = GoogleTranslator(
    source="en",
    target="ar"
)

bot = Bot(
    token=config.BOT_TOKEN
)
```
