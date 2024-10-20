from django.core.management.base import BaseCommand
from myapp.ml_model import predict_next_30_days
from myapp.models import StockData

class Command(BaseCommand):
    help = 'Generate predictions for the next 30 days for a stock symbol'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Action symbol to predict')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol']
        historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

        if not historical_data.exists():
            self.stdout.write(self.style.ERROR(f"No data found for the symbol {symbol}"))
            return

        predictions = predict_next_30_days(symbol)

        self.stdout.write(self.style.SUCCESS(f"Predictions generated for{symbol}:"))
        for prediction in predictions:
            self.stdout.write(f"Date: {prediction['date']}, next prices: {prediction['predicted_price']}")
