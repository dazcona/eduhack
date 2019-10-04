#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import cv2
from yolo import get_yolo

TOKEN = os.environ['TOKEN']

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MENU, DONE, SUCCESS, INTERACTION = range(4)

def start(update, context):

    user = update.message.from_user
    logger.info("User: %s", user.first_name)
    update.message.reply_text(
        'Hi David! What would you like to report? 🐦')

    return INTERACTION


def interaction(update, context):

    d = {
        'obstruction': 'Where?',
        'quarry': 'What is the obstruction?',
    }
    
    text = update.message.text
    print('Text: {}'.format(text))

    for key, response_text in d.items():
        if key in text.lower():
            print(key)
            print(response_text)
            update.message.reply_text(response_text)
            return INTERACTION
    else:
        reply_keyboard = [['Photo', 'Audio', 'Text'], [], ['Done']]
        update.message.reply_text(
            'Please report it on the menu',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MENU


def menu(update, context):

    print('Menu...')
    user = update.message.from_user
    category = update.message.text
    print('Category: {}'.format(category))
    return category


def photo(update, context):

    print('Getting picture...')
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    name = '{}_{}.jpg'.format(user.first_name, time.strftime("%Y%m%d-%H%M%S"))
    filename = 'static/pictures/{}'.format(name)
    print('Saving picture as "{}"...'.format(filename))
    # Save picture
    photo_file.download(filename)
    # Calling the detection...
    update.message.reply_text('Analyzing picture...')
    result = get_yolo(filename)
    # Save result
    result_filename = "static/results/{}".format(name)
    print('Saving new picture as "{}"...'.format(result_filename))
    cv2.imwrite(result_filename, result)
    update.message.reply_text('Picture has been processed!')
    # Send message with picture
    update.message.reply_photo(photo=open(result_filename, 'rb'),
                                caption="Backpack left on site")
    logger.info("Photo of %s: %s", user.first_name, filename)
    update.message.reply_text('Backpack needs to be removed, could cause staff to trip')

    return DONE


def success(update, context):
    
    print('Success...')
    user_data = context.user_data

    update.message.reply_text("Thanks very much for reporting! Your point balance is: 5"
                              "Happy working!")

    return ConversationHandler.END


def skip_photo(update, context):

    return PHOTO


def done(update, context):
    
    print('Done...')
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("Take action: Remove backpack & exit area. "
                              "Thanks very much for reporting! 👍 Your point balance is: 5 🌟")

    user_data.clear()
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={

            INTERACTION: [ 
                MessageHandler(Filters.text, interaction) 
            ],

            MENU: [ 
                MessageHandler(Filters.text, menu) 
            ],

            'Photo': [ 
                MessageHandler(Filters.photo, photo), 
                CommandHandler('skip', skip_photo) 
            ],

            SUCCESS: [ 
                MessageHandler(Filters.text, success) 
            ],

            'Done': [ 
                MessageHandler(Filters.text, done) 
            ],

        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print('Starting Canary AI Bot...')
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()