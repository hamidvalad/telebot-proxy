# telebot-proxy

**Route any `requests`-based HTTP traffic through a forwarder service — zero code changes to your application logic.**

Originally built for [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (telebot), but works with **any** Python code that uses the `requests` library.

[![PyPI version](https://img.shields.io/pypi/v/telebot-proxy.svg)](https://pypi.org/project/telebot-proxy/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()
[![Downloads](https://img.shields.io/pypi/dm/telebot-proxy.svg)](https://pypi.org/project/telebot-proxy/)

---

<div dir="rtl">

**[🇮🇷 مستندات فارسی](#مستندات-فارسی)**

</div>

---

## Table of Contents

- [What does it do?](#what-does-it-do)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Telegram Bot](#1-telegram-bot-default)
  - [Custom hosts](#2-proxy-specific-hosts)
  - [Intercept everything](#3-intercept-all-requests)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Forwarder Service](#forwarder-service)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)
- [مستندات فارسی](#مستندات-فارسی)

---

## What does it do?

In some networks, direct access to certain APIs (like `api.telegram.org`) is blocked or unreliable. **telebot-proxy** solves this by transparently routing HTTP requests through an intermediate **forwarder service** that you control.

### Three modes of operation

| Mode | Description | Use case |
|---|---|---|
| **Default** | Intercept only `api.telegram.org` | Telegram bots |
| **Selective hosts** | Intercept a custom list of hostnames | Specific blocked APIs |
| **Intercept all** | Route *every* outgoing request through the forwarder | Fully restricted networks |

### Feature support

| Feature | Status |
|---|---|
| Any API that uses `requests` | ✅ |
| pyTelegramBotAPI (telebot) 3.x & 4.x | ✅ |
| Text messages, photos, videos, files | ✅ |
| File downloads | ✅ |
| Inline queries & callbacks | ✅ |
| Long polling (`infinity_polling`) | ✅ |
| Webhook mode | ✅ |
| JSON body, form data, multipart upload | ✅ |
| Thread-safe | ✅ |
| Multiple bots/clients in one process | ✅ |
| Loop guard (forwarder host never intercepted) | ✅ |
| Python 3.7 – 3.13 | ✅ |

---

## How it works

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│  Your Code   │─req──▶│ telebot-proxy │─req──▶│ Forwarder Service│
│  (requests,  │◀─res──│  (this lib)   │◀─res──│  (your server)   │
│  telebot, …) │       └──────────────┘       └───────┬──────────┘
└──────────────┘                                      │ req/res
                                                      ▼
                                              ┌───────────────┐
                                              │  Real Target  │
                                              │  (Telegram,   │
                                              │  OpenAI, …)   │
                                              └───────────────┘
```

1. You call `setup_proxy()` **once**, at startup.
2. The library monkey-patches `requests.Session.request`.
3. Matching HTTP requests are **rewritten** to go to your forwarder service.
4. The forwarder relays the request to the real destination and returns the response unchanged.
5. Your application code doesn't know the difference.

---

## Installation

### From PyPI (recommended)

```bash
pip install telebot-proxy
```

With Telegram bot library:

```bash
pip install telebot-proxy pyTelegramBotAPI
```

### From source

```bash
git clone https://github.com/hamidvalad/telebot-proxy.git
cd telebot-proxy
pip install .
```

### Copy directly

Just copy the `telebot_proxy/` folder into your project. The only dependency is `requests` (which most projects already have).

---

## Quick Start

### 1. Telegram Bot (default)

Add **two lines** to the top of your bot file — before `import telebot`:

```python
from telebot_proxy import setup_proxy
setup_proxy(proxy_token="YOUR_FORWARDER_TOKEN")

import telebot

bot = telebot.TeleBot("YOUR_BOT_TOKEN")

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello from behind a proxy!")

bot.infinity_polling()
```

### 2. Proxy specific hosts

Route requests to selected APIs through the forwarder:

```python
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token="YOUR_FORWARDER_TOKEN",
    hosts=["api.telegram.org", "api.openai.com", "httpbin.org"],
)

import requests

# This goes through the forwarder:
resp = requests.get("https://httpbin.org/ip")
print(resp.json())

# This goes DIRECTLY (not in the hosts list):
resp = requests.get("https://api.github.com/zen")
print(resp.text)
```

### 3. Intercept ALL requests

Route **every** outgoing request through the forwarder:

```python
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token="YOUR_FORWARDER_TOKEN",
    intercept_all=True,
)

import requests

# ALL of these go through the forwarder:
requests.get("https://httpbin.org/ip")
requests.get("https://api.github.com/zen")
requests.post("https://any-api.example.com/data", json={"key": "value"})
```

> **Loop guard:** Requests to the forwarder itself are never intercepted, preventing infinite loops.

---

## Configuration

### `setup_proxy()` parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `proxy_token` | `str` | **Yes** | — | Auth token for the forwarder (`FORWARDER_TOKEN`). |
| `proxy_base_url` | `str` | No | `https://forwarder.only.ir` | Base URL of the forwarder service. |
| `hosts` | `list[str]` | No | `["api.telegram.org"]` | Hostnames to intercept. Ignored when `intercept_all=True`. |
| `intercept_all` | `bool` | No | `False` | If `True`, intercept ALL outgoing requests. |
| `extra_hosts` | `list[str]` | No | `None` | **Deprecated** — use `hosts`. Merges with the default Telegram host. |

### Using environment variables (recommended for production)

```python
import os
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token=os.environ["FORWARDER_TOKEN"],
    proxy_base_url=os.environ.get("FORWARDER_URL", "https://forwarder.only.ir"),
    # hosts=["api.telegram.org"],       # specific hosts
    # intercept_all=True,               # or intercept everything
)
```

```bash
export FORWARDER_TOKEN="your_secret_token"
export FORWARDER_URL="https://your-forwarder.example.com"  # optional
python your_bot.py
```

---

## Examples

See the [`examples/`](examples/) directory for complete, runnable scripts:

| File | Description |
|---|---|
| [`echo_bot.py`](examples/echo_bot.py) | Minimal Telegram echo bot |
| [`photo_bot.py`](examples/photo_bot.py) | Telegram bot — tests file uploads |
| [`env_bot.py`](examples/env_bot.py) | Production config via environment variables |
| [`webhook_bot.py`](examples/webhook_bot.py) | Telegram webhook mode (Flask) |
| [`toggle_proxy.py`](examples/toggle_proxy.py) | Enable / disable / switch modes at runtime |
| [`general_api_proxy.py`](examples/general_api_proxy.py) | Proxy non-Telegram APIs (httpbin, JSONPlaceholder) |
| [`intercept_all.py`](examples/intercept_all.py) | Intercept every outgoing request |
| [`mixed_bot.py`](examples/mixed_bot.py) | Telegram bot + external API, both proxied |

---

## API Reference

### `setup_proxy(proxy_token, proxy_base_url=..., hosts=None, intercept_all=False)`

Activate the proxy. Call **once**, at startup, before making any requests.

```python
# Default (Telegram only)
setup_proxy(proxy_token="tok")

# Custom hosts
setup_proxy(proxy_token="tok", hosts=["api.telegram.org", "httpbin.org"])

# Everything
setup_proxy(proxy_token="tok", intercept_all=True)
```

### `disable_proxy()`

Deactivate the proxy. All requests go directly to their targets.

### `is_active() -> bool`

Check if the proxy is currently active.

### `get_proxy_url() -> str`

Get the current forwarder base URL.

### `get_intercepted_hosts() -> set[str]`

Get the set of hostnames being intercepted. Returns an empty set when `intercept_all=True` (meaning everything is intercepted).

---

## Forwarder Service

telebot-proxy requires a **forwarder service** running on a server with unrestricted internet access. The forwarder receives requests, relays them to the real target, and returns the response.

### Expected endpoint

```
GET/POST/PUT/DELETE  <base_url>/forward?url=<target_url>&<other_params>
```

### Authentication

The library sends the token via **two** headers:

```
Authorization: Bearer <proxy_token>
X-Api-Token: <proxy_token>
```

### Minimal forwarder (Flask)

```python
import requests as http_client
from flask import Flask, Response, jsonify, request

app = Flask(__name__)
AUTH_TOKEN = "your_secret_token"

def verify_token():
    token = request.headers.get("X-Api-Token") or ""
    bearer = request.headers.get("Authorization", "").replace("Bearer ", "")
    return token == AUTH_TOKEN or bearer == AUTH_TOKEN

@app.route("/forward", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def forward():
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    target_url = request.args.get("url")
    if not target_url:
        return jsonify({"error": "Missing url parameter"}), 400

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {
            "host", "authorization", "x-api-token",
            "connection", "transfer-encoding",
        }
    }

    params = {k: v for k, v in request.args.items() if k != "url"}

    resp = http_client.request(
        method=request.method,
        url=target_url,
        headers=headers,
        params=params or None,
        data=request.data if not request.is_json else None,
        json=request.get_json(silent=True) if request.is_json else None,
        timeout=60,
    )

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type"),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### Important: timeout

For Telegram bots using long polling, `getUpdates` can take up to **20 seconds**. Set the forwarder's timeout to **at least 30–60 seconds**.

---

## FAQ

### Does this work with non-Telegram APIs?

**Yes!** Use the `hosts` parameter to specify any hostname, or `intercept_all=True` to proxy everything. It works with any library built on `requests`.

### Does this work with async telebot?

Currently it patches `requests.Session`, used by the **synchronous** `TeleBot`. For `AsyncTeleBot` (which uses `aiohttp`), a different approach would be needed — contributions welcome!

### Can I use this with other Python HTTP libraries?

Any library that internally uses `requests` will be intercepted automatically (e.g., many REST API wrappers). Libraries using `httpx` or `aiohttp` directly will **not** be intercepted.

### Is there any performance impact?

Each intercepted request adds one extra network hop. The added latency depends on the distance between your server and the forwarder.

### What about infinite loops?

The library has a built-in **loop guard**: requests to the forwarder's own hostname are never intercepted, even in `intercept_all` mode.

### How do I verify it's working?

```python
from telebot_proxy import setup_proxy, is_active
import requests

setup_proxy(proxy_token="your_token", hosts=["httpbin.org"])
print(f"Proxy active: {is_active()}")

resp = requests.get("https://httpbin.org/ip")
print(resp.json())  # If this prints, it's working!
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

```
24 passed in 0.20s
```

---

## Project Structure

```
telebot-proxy/
├── telebot_proxy/                  # Main package
│   ├── __init__.py                 # Public API
│   └── core.py                     # Monkey-patch engine
├── examples/                       # Runnable examples
│   ├── echo_bot.py                 # Telegram echo bot
│   ├── photo_bot.py                # Telegram photo bot
│   ├── env_bot.py                  # Environment variables
│   ├── webhook_bot.py              # Webhook mode
│   ├── toggle_proxy.py             # Runtime toggle
│   ├── general_api_proxy.py        # Non-Telegram APIs
│   ├── intercept_all.py            # Intercept everything
│   └── mixed_bot.py                # Telegram + external API
├── tests/
│   └── test_core.py                # 24 tests
├── pyproject.toml                  # Package config
├── requirements.txt
├── README.md
├── LICENSE                         # MIT
├── CHANGELOG.md
└── CONTRIBUTING.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[MIT](LICENSE) — use it however you want.

---

---

<div dir="rtl">

## مستندات فارسی

### این کتابخانه چیست؟

این کتابخانه تمام درخواست‌های HTTP ارسال‌شده از طریق کتابخانه `requests` پایتون را به صورت شفاف از طریق یک **سرویس واسط** (forwarder) ارسال می‌کند.

در ابتدا برای هدایت درخواست‌های ربات تلگرام (`pyTelegramBotAPI`) طراحی شده، اما **برای هر API و سرویسی** قابل استفاده است.

### چرا نیاز است؟

در برخی شبکه‌ها و سرورها، دسترسی مستقیم به برخی APIها (مثل `api.telegram.org`) مسدود یا ناپایدار است. با این کتابخانه، درخواست‌ها از طریق سرویس واسطی که روی سروری با دسترسی آزاد قرار دارد ارسال می‌شوند.

### سه حالت کاری

| حالت | توضیح | کاربرد |
|---|---|---|
| **پیش‌فرض** | فقط `api.telegram.org` را رهگیری می‌کند | ربات‌های تلگرام |
| **هاست‌های انتخابی** | لیست دلخواه از هاست‌ها | APIهای خاص |
| **همه درخواست‌ها** | تمام درخواست‌های خروجی | شبکه‌های کاملاً محدود |

### نصب

</div>

```bash
pip install telebot-proxy
```

<div dir="rtl">

یا از سورس:

</div>

```bash
git clone https://github.com/hamidvalad/telebot-proxy.git
cd telebot-proxy
pip install .
```

<div dir="rtl">

یا فقط پوشه <code>telebot_proxy/</code> را در پروژه خود کپی کنید.

### شروع سریع

#### حالت ۱: ربات تلگرام (پیش‌فرض)

فقط **دو خط** به بالای فایل ربات اضافه کنید — **قبل از** <code>import telebot</code>:

</div>

```python
from telebot_proxy import setup_proxy
setup_proxy(proxy_token="توکن_سرویس_واسط")

import telebot
bot = telebot.TeleBot("توکن_ربات")

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "سلام! ربات از طریق پراکسی کار می‌کنه.")

bot.infinity_polling()
```

<div dir="rtl">

#### حالت ۲: هاست‌های دلخواه

</div>

```python
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token="توکن_سرویس_واسط",
    hosts=["api.telegram.org", "api.openai.com", "httpbin.org"],
)

import requests

# این از پراکسی رد میشه:
resp = requests.get("https://httpbin.org/ip")
print(resp.json())

# این مستقیم ارسال میشه (توی لیست نیست):
resp = requests.get("https://api.github.com/zen")
print(resp.text)
```

<div dir="rtl">

#### حالت ۳: تمام درخواست‌ها

</div>

```python
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token="توکن_سرویس_واسط",
    intercept_all=True,
)

import requests

# همه درخواست‌ها از پراکسی رد میشن:
requests.get("https://httpbin.org/ip")
requests.get("https://api.github.com/zen")
requests.post("https://any-api.example.com/data", json={"key": "value"})
```

<div dir="rtl">

> **محافظت از حلقه:** درخواست‌هایی که مقصدشان خود سرویس واسط باشد هرگز رهگیری نمی‌شوند.

### پارامترهای `setup_proxy()`

| پارامتر | نوع | الزامی | پیش‌فرض | توضیحات |
|---|---|---|---|---|
| `proxy_token` | `str` | **بله** | — | توکن احراز هویت سرویس واسط. |
| `proxy_base_url` | `str` | خیر | `https://forwarder.only.ir` | آدرس پایه سرویس واسط. |
| `hosts` | `list[str]` | خیر | `["api.telegram.org"]` | هاست‌هایی که باید رهگیری شوند. وقتی `intercept_all=True` باشد نادیده گرفته می‌شود. |
| `intercept_all` | `bool` | خیر | `False` | اگر `True` باشد، تمام درخواست‌ها رهگیری می‌شوند. |
| `extra_hosts` | `list[str]` | خیر | `None` | **منسوخ** — از `hosts` استفاده کنید. |

### استفاده با متغیرهای محیطی (توصیه‌شده)

</div>

```python
import os
from telebot_proxy import setup_proxy

setup_proxy(
    proxy_token=os.environ["FORWARDER_TOKEN"],
    proxy_base_url=os.environ.get("FORWARDER_URL", "https://forwarder.only.ir"),
    # hosts=["api.telegram.org"],       # هاست‌های خاص
    # intercept_all=True,               # یا همه درخواست‌ها
)
```

```bash
set FORWARDER_TOKEN=your_secret_token
set FORWARDER_URL=https://your-forwarder.example.com
python your_bot.py
```

<div dir="rtl">

### توابع

| تابع | توضیح |
|---|---|
| `setup_proxy(...)` | فعال‌سازی پراکسی. **یک بار** در ابتدای برنامه صدا بزنید. |
| `disable_proxy()` | غیرفعال‌سازی پراکسی. |
| `is_active()` | آیا پراکسی فعال است؟ |
| `get_proxy_url()` | آدرس فعلی سرویس واسط. |
| `get_intercepted_hosts()` | مجموعه هاست‌های رهگیری‌شده. اگر `intercept_all=True` مجموعه خالی برمی‌گرداند (یعنی همه). |

### نمونه‌کدها

| فایل | توضیح |
|---|---|
| `echo_bot.py` | ربات ساده echo تلگرام |
| `photo_bot.py` | تست آپلود عکس |
| `env_bot.py` | استفاده از متغیرهای محیطی |
| `webhook_bot.py` | حالت webhook با Flask |
| `toggle_proxy.py` | فعال/غیرفعال کردن و تغییر حالت |
| `general_api_proxy.py` | پراکسی APIهای غیر تلگرام |
| `intercept_all.py` | رهگیری تمام درخواست‌ها |
| `mixed_bot.py` | ربات تلگرام + API خارجی |

### نکات مهم

1. **`setup_proxy()` باید قبل از ساخت اشیاء `TeleBot` یا ارسال درخواست فراخوانی شود.**

2. **timeout سرویس واسط باید حداقل ۳۰ ثانیه باشد** — چون long-polling تلگرام پیش‌فرض ۲۰ ثانیه صبر می‌کند.

3. **توکن‌ها را hard-code نکنید** — از متغیرهای محیطی استفاده کنید.

4. **این کتابخانه فقط برای تلگرام نیست** — هر کدی که از `requests` استفاده می‌کند با آن سازگار است.

### تست

</div>

```bash
pip install -e ".[dev]"
pytest -v
# 24 passed
```

<div dir="rtl">

### مجوز

[MIT](LICENSE) — آزادانه استفاده کنید.

</div>
