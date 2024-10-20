import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from myapp.models import StockData, Prediction
import os

# Ruta del archivo del modelo
MODEL_FILE = os.path.join(os.path.dirname(__file__), 'model.pkl')

def train_model(symbol):
    """Entrena un modelo de regresión lineal basado en los datos históricos del símbolo proporcionado."""
    # Obtener datos históricos de la base de datos
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        raise ValueError(f"No se encontraron datos históricos para el símbolo {symbol}")

    # Preparar los datos para el entrenamiento
    X = np.array([i for i in range(len(historical_data))]).reshape(-1, 1)  # Índices como entrada
    y = np.array([data.close_price for data in historical_data])  # Precios de cierre como salida

    model = LinearRegression()
    model.fit(X, y)

    # Guardar el modelo entrenado
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)

    print(f"Modelo entrenado y guardado para el símbolo {symbol}")

def load_model():
    """Carga el modelo entrenado desde un archivo."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        return model
    else:
        raise FileNotFoundError(f"El archivo del modelo no se encuentra en {MODEL_FILE}")

def predict_next_30_days(symbol):
    """Usa el modelo de regresión lineal para predecir los próximos 30 días de un símbolo dado."""
    # Obtener datos históricos
    historical_data = StockData.objects.filter(symbol=symbol).order_by('timestamp')

    if not historical_data.exists():
        raise ValueError(f"No se encontraron datos históricos para el símbolo {symbol}")

    # Cargar el modelo pre-entrenado
    model = load_model()

    # Preparar los datos de entrada
    X = np.array([i for i in range(len(historical_data))]).reshape(-1, 1)

    # Predecir los próximos 30 días
    predictions = []
    last_day_index = len(historical_data) - 1
    last_timestamp = historical_data.last().timestamp
    for i in range(1, 31):
        next_day = last_day_index + i
        predicted_price = model.predict(np.array([[next_day]]))[0]

        # Guardar la predicción en la base de datos
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
