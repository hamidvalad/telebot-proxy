"""
telebot-proxy
=============

Route **any** ``requests``-based HTTP traffic through an HTTP forwarder service.

This package monkey-patches ``requests.Session.request`` so that HTTP calls
targeting specific hosts — or **all** hosts — are transparently redirected to a
forwarder endpoint.  The forwarder relays the request to the real destination
and returns the response unchanged.

Originally built for routing Telegram Bot API calls (``pyTelegramBotAPI``)
through a relay, but works with **any** library or code that uses ``requests``.

Quick start — Telegram bot::

    from telebot_proxy import setup_proxy

    setup_proxy(
        proxy_token="YOUR_FORWARDER_TOKEN",
        hosts=["api.telegram.org"],
    )

    import telebot
    bot = telebot.TeleBot("BOT_TOKEN")
    ...

Quick start — proxy everything::

    from telebot_proxy import setup_proxy

    setup_proxy(
        proxy_token="YOUR_FORWARDER_TOKEN",
        intercept_all=True,
    )

    import requests
    # This request will go through the forwarder
    requests.get("https://any-api.example.com/data")

Full documentation: https://github.com/hamidvalad/telebot-proxy
"""

from telebot_proxy.core import (
    disable_proxy,
    get_intercepted_hosts,
    get_proxy_url,
    is_active,
    setup_proxy,
)

__all__ = [
    "setup_proxy",
    "disable_proxy",
    "is_active",
    "get_proxy_url",
    "get_intercepted_hosts",
]

__version__ = "1.1.1"
__author__ = "Hamidvalad.ir"
