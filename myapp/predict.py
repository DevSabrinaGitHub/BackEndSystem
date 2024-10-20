import numpy as np
from sklearn.linear_model import LinearRegression
from myapp.models import StockData, Prediction
from datetime import datetime, timedelta

def predict_next_30_days(symbol):
    stock_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')
    close_prices = np.array([data.close_price for data in stock_data]).reshape(-1, 1)
    last_date = stock_data.last().timestamp  # Last Recorded Date

    days = np.array(range(1, len(close_prices) + 1)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(days, close_prices)

    future_days = np.array(range(len(close_prices) + 1, len(close_prices) + 31)).reshape(-1, 1)
    predictions = model.predict(future_days).flatten()

    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]

    # Package predictions as a list of dictionaries
    predicted_data = [{"date": future_dates[i], "predicted_price": predictions[i]} for i in range(30)]

    return predicted_data
