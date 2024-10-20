from django.core.management.base import BaseCommand
from myapp.ml_model import train_model

class Command(BaseCommand):
    help = 'Train the machine learning model for a given stock symbol'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Stock symbol to train the model on')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol']
        self.stdout.write(f"Training machine learning model for {symbol}...")

        # function for the model
        train_model(symbol)

        self.stdout.write(self.style.SUCCESS(f"Model trained successfully for {symbol}."))
