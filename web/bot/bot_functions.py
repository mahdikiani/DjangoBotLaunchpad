import telebot
from django.contrib.auth.models import User
from django.utils import timezone
from telebot.handler_backends import BaseMiddleware
from singleton import Singleton
from .Bot import BaseBot, TelegramBot, BaleBot


class UserMiddleware(BaseMiddleware):
    def __init__(self, bot: BaseBot, *args, **kwargs):
        self.update_sensitive = True
        self.update_types = [
            "message",
            #  "edited_message",
            "callback_query",
            # "inline_query"
        ]
        self.bot = bot
        self.bot_type = bot.bot_type
        super().__init__(*args, **kwargs)

    def pre_process_message(self, message: telebot.types.Message, data):
        messenger = self.bot_type
        from_user = message.from_user if message.from_user else message.chat
        save_username = f"{messenger}-{from_user.id}"
        save_name = name = " ".join(
            [
                f'{from_user.first_name if from_user.first_name else ""}',
                f'{from_user.last_name if from_user.last_name else ""}',
                f'{from_user.username if from_user.username else ""}',
            ]
        )
        qs = User.objects.filter(username=save_username, first_name=save_name)
        if not qs.exists():
            user = User.objects.create(username=save_username, first_name=save_name)

        user.last_login = timezone.now()

        if save_name != user.first_name:
            user.first_name = save_name
        user.save()
        message.user = user

    def pre_process_callback_query(self, call: telebot.types.CallbackQuery, data):
        self.pre_process_message(call.message, data)

    def post_process_message(self, message: telebot.types.Message, data, exception):
        pass

    def post_process_callback_query(
        self, call: telebot.types.CallbackQuery, data, exception
    ):
        pass


command_key = {
    "/start": "start",
    "/help": "help",
}


def command(message: telebot.types.Message, bot: BaseBot):
    format_dict = {
        "username": message.from_user.username,
        "id": message.chat.id,
        "first": message.from_user.first_name,
        "last": message.from_user.last_name,
        "language": message.from_user.language_code,
    }

    query = message.text if message.text in command_key else "/start"
    if command_key[query] == "start":
        bot.reply_to(message, "Welcome to the bot!")
    elif command_key[query] == "help":
        bot.reply_to(message, "Just send a message")


def prompt(message: telebot.types.Message, bot: BaseBot):
    bot.reply_to(message, message.text)


def message(message: telebot.types.Message, bot: BaseBot):
    if message.text.startswith("/"):
        command(message, bot)
    else:
        prompt(message, bot)


def callback(call: telebot.types.CallbackQuery, bot: BaseBot):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Callback received")


def setup_bot(bot: BaseBot):
    bot.setup_middleware(UserMiddleware(bot))
    bot.register_callback_query_handler(
        callback,
        func=lambda _: True,
        pass_bot=True,
    )
    bot.register_message_handler(
        message,
        func=lambda _: True,
        content_types=["text"],
        pass_bot=True,
    )


class BotFunctions(metaclass=Singleton):
    is_setup = False

    def __init__(self):
        if not self.is_setup:
            self.setup()
            self.is_setup = True

    def setup(self):
        for bot in [TelegramBot(), BaleBot()]:
            setup_bot(bot)
