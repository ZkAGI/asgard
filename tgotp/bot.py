import os
import random

import telebot

from listner.models import TGVerifiedUsers

BOT_TOKEN = "6889345733:AAE0bXPBKN03LOWBnl5QZcvLxGq_jcFbQqU"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['verify'])
def send_otp(message):
    otp = random.randint(1000, 9999)
    user_id = message.from_user.username

    # Delete existing records for this user_id, if any
    TGVerifiedUsers.objects.filter(userid=user_id).delete()

    # Create a new record with the current OTP
    TGVerifiedUsers.objects.create(userid=user_id, otp=otp)

    # Send the OTP to the user
    text = f"Your OTP is: {otp}"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
