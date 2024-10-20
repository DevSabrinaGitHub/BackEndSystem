import os
import requests
from myapp.models import StockData
from datetime import datetime

ALPHA_VANTAGE_API_KEY = "DYIVABL5P6CM8OCQ"  #API KEY
BASE_URL = "https://www.alphavantage.co/query"

def fetch_stock_data(symbol):
    """Obtener datos de precios de acciones para un símbolo dado desde Alpha Vantage"""
    print(f"Fetching data for {symbol} from Alpha Vantage...")
    
    # Free endpoint parameters TIME_SERIES_DAILY
    params = {
        "function": "TIME_SERIES_DAILY",  #free enpoints
        "symbol": symbol,
        "outputsize": "full",
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    # Make the API request
    response = requests.get(BASE_URL, params=params)
    print(f"Request made. Status code: {response.status_code}")
    
    data = response.json()
    print(f"API Response: {data}")

    # Check if the answer contains valid data
    if 'Time Series (Daily)' not in data:
        print(f"Error: Data format incorrect or not available for {symbol}")
        print(f"API Response: {data}")
        return

    # Get the daily data
    daily_data = data['Time Series (Daily)']

    # Save the data in the database
    for date_str, values in daily_data.items():
        timestamp = datetime.strptime(date_str, "%Y-%m-%d")
        StockData.objects.update_or_create(
            symbol=symbol,
            timestamp=timestamp,
            defaults={
                'open_price': values['1. open'],
                'close_price': values['4. close'],
                'high_price': values['2. high'],
                'low_price': values['3. low'],
                'volume': values['5. volume'],
            }
        )
    print(f"Data for {symbol} saved successfully.")
