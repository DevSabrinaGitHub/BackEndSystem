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


# Función para calcular el promedio móvil
def calculate_moving_average(prices, window_size):
    return sum(prices[-window_size:]) / window_size if len(prices) >= window_size else None


# Vista para realizar el backtesting con mejoras
def backtest(request, symbol, initial_investment):
    stock_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not stock_data.exists():
        return HttpResponse(f"No se encontraron datos para el símbolo {symbol}.", content_type="text/plain")

    balance = initial_investment
    holdings = 0  # Número de acciones en posesión
    trade_count = 0
    initial_price = stock_data.first().close_price  # Precio inicial para calcular ROI

    close_prices = [data.close_price for data in stock_data]

    # Variable para evitar comprar y vender inmediatamente después
    can_trade = True
    last_trade_action = None

    for i, data in enumerate(stock_data):
        ma50 = calculate_moving_average(close_prices[:i + 1], 50)
        ma200 = calculate_moving_average(close_prices[:i + 1], 200)

        # Estrategia de compra: Solo se compra si no se ha comprado recientemente
        if can_trade and ma50 and ma200 and holdings == 0 and data.close_price < ma50:
            holdings = balance / data.close_price  # Comprar
            balance = 0
            trade_count += 1
            can_trade = False  # Bloquear más operaciones hasta que vendamos
            last_trade_action = 'buy'

        # Estrategia de venta: Solo se vende si no se ha vendido recientemente
        elif can_trade and ma50 and ma200 and holdings > 0 and data.close_price > ma200:
            balance = holdings * data.close_price  # Vender
            holdings = 0
            trade_count += 1
            can_trade = False  # Bloquear más operaciones hasta que compremos
            last_trade_action = 'sell'

        # Desbloquear después de una operación opuesta
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
    """Función para predecir el precio de las acciones del símbolo dado para los próximos 30 días."""
    try:
        predictions = predict_next_30_days(symbol)

        # Convertir las fechas a formato ISO para JSON
        for prediction in predictions:
            prediction['date'] = prediction['date'].isoformat()

        return JsonResponse(predictions, safe=False)

    except ValueError as e:
        return HttpResponse(str(e), content_type="text/plain")



# Función para entrenar el modelo
def train_ml_model(request, symbol):
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        return HttpResponse(f"No se encontraron datos históricos para {symbol}.", content_type="text/plain")

    train_model(historical_data)
    return HttpResponse(f"Modelo entrenado para {symbol} con éxito.", content_type="text/plain")


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


# Función para generar un informe en JSON
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


# Vista para generar el gráfico de precios históricos
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


# Página principal
def home(request):
    return render(request, 'myapp/home.html')
