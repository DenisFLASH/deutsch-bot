#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

import pandas as pd
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="./bot.log",
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    level=logging.INFO)


HELLO, LESSON = 0, 1  # states
DICTIONARIES = {
    "Verben": "./data/verbs.csv",
    "Adjektiven": "./data/adjectives.csv"
}


def select_dictionary(update, context):
    """Send greeting and ask which dictionary to learn."""

    user = update.message.from_user
    update.message.reply_text(f"👋 Hallo, {user.first_name}!")

    keyboard = [DICTIONARIES.keys()]
    update.message.reply_text(
        "Welche Wörter wollen Sie lernen?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return HELLO


def hello(update, context):
    """Open the corresponding dictionary, ask the 1st question."""

    key = update.message.text
    dictionary = pd.read_csv(DICTIONARIES[key], sep=";")
    context.user_data["dictionary"] = dictionary

    update.message.reply_text("Lass uns gehen!")

    _set_question(update, context)

    return LESSON


def lesson(update, context):
    """Compare user's answer to the correct translation, stored in context"""

    # 1) check the answer to the current question
    user = update.message.from_user
    answer = update.message.text
    logging.info(f"{user.first_name}'s answer: {answer}")
    q = context.user_data["q"]
    translation = q["de"]

    if answer.lower() == translation.lower():
        update.message.reply_text("Ja! Gut gemacht!!! 👍")
    else:
        update.message.reply_text("nein...")

    update.message.reply_text(f"{q['ru']} = {q['de']}")

    # 2) set a new question
    _set_question(update, context)

    return LESSON


def stop(update, context):
    """Stop learning session."""
    user = update.message.from_user
    update.message.reply_text(f"👋 Tschüss, {user.first_name}! Bis bald!")

    context.user_data.clear()
    return ConversationHandler.END


def _set_question(update, context) -> None:
    """Pick a question, show to the user and set inside the context."""
    dictionary = context.user_data["dictionary"]
    q = dict(dictionary.sample(1).iloc[0])
    context.user_data["q"] = q  # {"de": ..., "ru": ...}
    logging.info(f"context.user_data: {context.user_data}")

    update.message.reply_text("---------------------------------------")
    update.message.reply_text(f"{q['ru']}:")


def main():
    """Start the bot."""

    # Create the Updater and pass it your bot's token.
    token = os.environ.get("DEUTSCH2020BOT_TOKEN")
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", select_dictionary)],
        states={
            HELLO: [
                MessageHandler(Filters.text & ~Filters.command, hello)
            ],
            LESSON: [
                MessageHandler(Filters.text & ~Filters.command, lesson)
            ]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
