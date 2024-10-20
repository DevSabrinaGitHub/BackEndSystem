import requests
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from myapp.models import StockData
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetches daily stock data from Alpha Vantage API and stores it in the database.'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Stock symbol to fetch data for')

    def handle(self, *args, **options):
        symbol = options['symbol'].upper()
        api_key = 'TU_CLAVE_API'  # Reemplaza esto con tu clave de API de Alpha Vantage
        function = 'TIME_SERIES_DAILY'
        url = (
            f'https://www.alphavantage.co/query?function={function}'
            f'&symbol={symbol}&outputsize=full&apikey={api_key}'
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Manejar límite de tasas de la API
            if 'Note' in data:
                self.stdout.write(self.style.WARNING('Límite de la API alcanzado. Esperando 60 segundos.'))
                time.sleep(60)
                response = requests.get(url)
                data = response.json()

            # Manejar errores de la API
            if 'Error Message' in data:
                raise CommandError(f"Error de API: {data['Error Message']}")

            time_series = data.get('Time Series (Daily)', {})

            # Filtrar los datos de los últimos 2 años
            two_years_ago = datetime.now() - timedelta(days=730)
            records_created = 0

            for date_str, values in time_series.items():
                timestamp = datetime.strptime(date_str, '%Y-%m-%d')
                if timestamp < two_years_ago:
                    continue

                stock_data, created = StockData.objects.update_or_create(
                    symbol=symbol,
                    timestamp=timestamp,
                    defaults={
                        'open_price': values['1. open'],
                        'high_price': values['2. high'],
                        'low_price': values['3. low'],
                        'close_price': values['4. close'],
                        'volume': values['5. volume'],
                    }
                )
                if created:
                    records_created += 1

            self.stdout.write(self.style.SUCCESS(
                f"Datos obtenidos y almacenados correctamente para {symbol}. Registros creados: {records_created}"
            ))
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Error de red: {e}")
        except Exception as e:
            raise CommandError(f"Ocurrió un error: {e}")
