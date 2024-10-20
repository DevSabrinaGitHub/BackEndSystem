from django.core.management.base import BaseCommand
from myapp.ml_model import predict_next_30_days
from myapp.models import StockData

class Command(BaseCommand):
    help = 'Genera predicciones para los próximos 30 días para un símbolo bursátil'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Símbolo de la acción para predecir')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol']
        historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

        if not historical_data.exists():
            self.stdout.write(self.style.ERROR(f"No se encontraron datos para el símbolo {symbol}"))
            return

        predictions = predict_next_30_days(symbol)

        self.stdout.write(self.style.SUCCESS(f"Predicciones generadas para {symbol}:"))
        for prediction in predictions:
            self.stdout.write(f"Fecha: {prediction['date']}, Precio predicho: {prediction['predicted_price']}")
