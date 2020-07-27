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
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

DF = pd.read_csv("./words.csv", sep=";")
MENU, ANSWERING = 0, 1  # states


def menu(update, context):
    """User choosing to continue or not. If yes, a question is asked."""

    # question
    q = dict(DF.sample(1).iloc[0])
    context.user_data["q"] = q  # {"de": ..., "ru": ...}
    logging.info(f"context.user_data: {context.user_data}")
    update.message.reply_text(f"{q['ru']}:")

    return ANSWERING


def answering(update, context):
    """Compare user's answer to the correct translation, stored in context"""

    q = context.user_data["q"]
    translation = q["de"]

    answer = update.message.text
    logging.info(f"answer: {answer}")

    if answer.lower() == translation.lower():
        update.message.reply_text(f"Ja! Gut gemacht!!!")

    update.message.reply_text(f"{q['ru']} = {q['de']}")

    update.message.reply_text(f"Noch einmal: /ja,  stop: /stop ?")
    return MENU


def stop(update, context):
    """Stop learning session."""
    context.user_data.clear()
    update.message.reply_text("Tschüss!")
    return ConversationHandler.END


def main():
    """Start the bot."""

    # Create the Updater and pass it your bot's token.
    token = os.environ.get("DEUTSCH2020BOT_TOKEN")
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", menu)],
        states={
            MENU: [CommandHandler("ja", menu)],
            ANSWERING: [MessageHandler(Filters.text & ~Filters.command,
                                       answering)]
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
