import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from myapp.models import StockData, Prediction
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
from django.db import transaction
from datetime import timedelta
from myapp.ml_model import train_model, predict_next_30_days
from .models import Prediction


# Function to calculate the moving average
def calculate_moving_average(prices, window_size):
    return sum(prices[-window_size:]) / window_size if len(prices) >= window_size else None


# View to perform backtesting with enhancements
def backtest(request, symbol, initial_investment):
    stock_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not stock_data.exists():
        return HttpResponse(f"No data found for the symbol {symbol}.", content_type="text/plain")

    balance = initial_investment
    holdings = 0  # Number of shares held
    trade_count = 0
    initial_price = stock_data.first().close_price  # initial price to calculate ROI

    close_prices = [data.close_price for data in stock_data]

    # Variable to avoid buying and selling immediately afterwards
    can_trade = True
    last_trade_action = None

    for i, data in enumerate(stock_data):
        ma50 = calculate_moving_average(close_prices[:i + 1], 50)
        ma200 = calculate_moving_average(close_prices[:i + 1], 200)

        # Buying strategy: You only buy if you haven't bought recently
        if can_trade and ma50 and ma200 and holdings == 0 and data.close_price < ma50:
            holdings = balance / data.close_price  # buy
            balance = 0
            trade_count += 1
            can_trade = False  # Block more trades until we sell
            last_trade_action = 'buy'

        #  Selling strategy: Only selling if it hasn't sold recently
        elif can_trade and ma50 and ma200 and holdings > 0 and data.close_price > ma200:
            balance = holdings * data.close_price  #sell
            holdings = 0
            trade_count += 1
            can_trade = False  # Block more trades until we sell
            last_trade_action = 'sell'

        # Unlock after an opposite operation
        if last_trade_action == 'buy' and data.close_price > ma200:
            can_trade = True
        elif last_trade_action == 'sell' and data.close_price < ma50:
            can_trade = True

    final_balance = balance + holdings * stock_data.last().close_price
    roi = (final_balance - initial_investment) / initial_investment * 100

    return render(request, 'myapp/backtest_result.html', {
        'symbol': symbol,
        'initial_investment': initial_investment,
        'final_balance': final_balance,
        'roi': roi,
        'trade_count': trade_count,
    })


def predict_stock(request, symbol):
    """Function to predict the share price of the given symbol for the next 30 days."""
    try:
        predictions = predict_next_30_days(symbol)

        # Convert Dates to ISO Format for JSON
        for prediction in predictions:
            prediction['date'] = prediction['date'].isoformat()

        return JsonResponse(predictions, safe=False)

    except ValueError as e:
        return HttpResponse(str(e), content_type="text/plain")



# Ffunction for the model
def train_ml_model(request, symbol):
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        return HttpResponse(f"No historical data was found for {symbol}.", content_type="text/plain")

    train_model(historical_data)
    return HttpResponse(f"train model for {symbol} with successfully.", content_type="text/plain")


# Función para generar un informe en PDF
def generate_pdf_report(request, symbol):
    predictions = Prediction.objects.filter(symbol=symbol).order_by('date')

    if not predictions.exists():
        return HttpResponse("No predictions found for this symbol.", content_type='text/plain')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, f"Predictions Report for {symbol}")
    c.drawString(100, 730, f"Date       | Predicted Price | Actual Price")

    y = 710
    for prediction in predictions:
        actual_price = prediction.actual_price if prediction.actual_price is not None else "N/A"
        c.drawString(100, y, f"{prediction.date} | {prediction.predicted_price} | {actual_price}")
        y -= 20

    c.showPage()
    c.save()

    return response


# generate JSON 
def generate_json_report(request, symbol):
    predictions = Prediction.objects.filter(symbol=symbol).order_by('date')

    if not predictions.exists():
        return HttpResponse(json.dumps({"error": "No predictions found for this symbol"}), content_type='application/json')

    prediction_list = [
        {
            "date": str(prediction.date),
            "predicted_price": float(prediction.predicted_price),
            "actual_price": float(prediction.actual_price) if prediction.actual_price else None
        }
        for prediction in predictions
    ]

    return HttpResponse(json.dumps(prediction_list), content_type='application/json')


# View to generate the historical prices
def plot_stock_prices(request, symbol):
    stock_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not stock_data.exists():
        return HttpResponse(f"No se encontraron datos para el símbolo {symbol}.", content_type="text/plain")

    dates = [data.timestamp for data in stock_data]
    close_prices = [data.close_price for data in stock_data]

    if not dates or not close_prices:
        return HttpResponse("No hay datos suficientes para generar el gráfico.", content_type="text/plain")

    plt.figure(figsize=(10, 5))
    plt.plot(dates, close_prices, label='Close Price', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'Price History for {symbol}')
    plt.legend()
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return HttpResponse(buffer, content_type='image/png')


# main page
def home(request):
    return render(request, 'myapp/home.html')
