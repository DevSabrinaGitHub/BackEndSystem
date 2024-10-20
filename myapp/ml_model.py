import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from myapp.models import StockData, Prediction
import os

# file path
MODEL_FILE = os.path.join(os.path.dirname(__file__), 'model.pkl')

def train_model(symbol):
    """Train a linear regression model based on historical data for the provided symbol."""
    # get historical date from DB
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        raise ValueError(f"No historical data found for the symbol {symbol}")

    # preparing data
    X = np.array([i for i in range(len(historical_data))]).reshape(-1, 1)  
    y = np.array([data.close_price for data in historical_data])  

    model = LinearRegression()
    model.fit(X, y)

    # save model
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)

    print(f"Trained and saved model for symbol {symbol}")

def load_model():
    """Load the trained model from a file."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        return model
    else:
        raise FileNotFoundError(f"The model file is not located in {MODEL_FILE}")

def predict_next_30_days(symbol):
    """Use the linear regression model to predict the next 30 days of a given symbol."""
    # get hisorical data
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        raise ValueError(f"No historical data found for the symbol {symbol}")

    # Loading the pre-trained model
    model = load_model()

    #preparing model
    X = np.array([i for i in range(len(historical_data))]).reshape(-1, 1)

    # # Predict the next 30 days
    predictions = []
    last_day_index = len(historical_data) - 1
    last_timestamp = historical_data.last().timestamp
    for i in range(1, 31):
        next_day = last_day_index + i
        predicted_price = model.predict(np.array([[next_day]]))[0]

        # Saving the prediction to the database
        prediction = Prediction.objects.create(
            symbol=symbol,
            date=last_timestamp + timedelta(days=i),
            predicted_price=predicted_price
        )
        predictions.append({
            'date': prediction.date,
            'predicted_price': predicted_price
        })

    return predictions
