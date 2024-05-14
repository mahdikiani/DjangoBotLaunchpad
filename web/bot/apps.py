import os
import logging

from django.apps import AppConfig
from django.urls import reverse
from telebot import TeleBot

logger = logging.getLogger("bot")


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self) -> None:
        super().ready()
        
        # from . import Bot

        # bot = Bot.TelegramBot()
        # self.set_webhook(bot, "telegram_webhook")
        # bot = Bot.BaleBot()
        # self.set_webhook(bot, "bale_webhook")

    def set_webhook(self, bot: TeleBot, webhook_name):
        reverse_url = reverse(webhook_name)
        webhook_url = f'https://{os.getenv("DOMAIN")}{reverse_url}'
        # bot.get_webhook_info()
        bot.delete_webhook()
        res = bot.set_webhook(url=webhook_url)
        logger.info(f"set webhook for {bot} with result: {res}")
