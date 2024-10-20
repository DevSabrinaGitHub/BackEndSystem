import os
import requests
from django.core.management.base import BaseCommand
from myapp.models import StockData
from datetime import datetime

ALPHA_VANTAGE_API_KEY = os.getenv('DYIVABL5P6CM8OCQ')

class Command(BaseCommand):
    help = 'Cargar datos históricos desde Alpha Vantage'

    def handle(self, *args, **kwargs):
        symbol = 'AAPL'
        self.stdout.write(self.style.SUCCESS(f'Cargando datos para {symbol}'))
        
        # URL de Alpha Vantage (Time Series Daily)
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}'
        
        response = requests.get(url)
        data = response.json()

        if "Time Series (Daily)" not in data:
            self.stdout.write(self.style.ERROR("Error al obtener datos de Alpha Vantage"))
            return

        time_series = data['Time Series (Daily)']

        for date_str, daily_data in time_series.items():
            timestamp = datetime.strptime(date_str, '%Y-%m-%d')
            open_price = float(daily_data['1. open'])
            high_price = float(daily_data['2. high'])
            low_price = float(daily_data['3. low'])
            close_price = float(daily_data['4. close'])
            volume = int(daily_data['5. volume'])

            # Guarda los datos en la base de datos
            stock_data, created = StockData.objects.get_or_create(
                symbol=symbol,
                timestamp=timestamp,
                defaults={
                    'open_price': open_price,
                    'close_price': close_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'volume': volume,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Dato para {timestamp} guardado con éxito'))
            else:
                self.stdout.write(self.style.WARNING(f'Dato para {timestamp} ya existe'))

        self.stdout.write(self.style.SUCCESS(f'Datos cargados con éxito para {symbol}'))
