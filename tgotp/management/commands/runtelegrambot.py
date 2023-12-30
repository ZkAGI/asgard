from django.core.management.base import BaseCommand
from tgotp.bot import bot


class Command(BaseCommand):
    help = 'Starts the Telegram bot.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Telegram bot...")
        bot.infinity_polling()  # Start your bot
