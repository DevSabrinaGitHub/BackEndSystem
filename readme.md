# Backend Engineer Trial Task
## Objective
Develop a Django-based backend system that fetches financial data from a public API, stores it in a relational database, implements a basic backtesting module, and generates reports with performance results.

---
## Key Steps

1. **Fetch Financial Data**:
   - **API**: Alpha Vantage.
   - **Data**: Daily stock prices (e.g., AAPL) for the past 2 years (open, close, high, low prices, and volume).
   - **Storage**: PostgreSQL database with an optimized schema.

   **Deliverables**: Django view or background task to fetch data, database schema, and error handling.

2. **Backtesting Module**:
   - **Goal**: Implement a simple backtesting strategy with parameters like initial investment and buy/sell rules based on moving averages.
   - **Output**: Calculate return on investment and generate a performance summary.

   **Deliverables**: API for inputting backtesting parameters and logic to process results.

3. **Machine Learning Integration**:
   - **Use of Pre-trained Model**: Integrate a pre-trained model (e.g., linear regression) to predict future prices.
   - **API**: Endpoint that returns predictions for the next 30 days.

   **Deliverables**: Django endpoint for predictions and storage of results.

4. **Report Generation**:
   - **Output**: Performance report including key metrics and a visual comparison of predicted vs. actual prices.
   - **Formats**: PDF and JSON responses via an API.

   **Deliverables**: Endpoint to generate and return reports.

5. **Deployment**:
   - **Platform**: Deploy on AWS (or similar) with Docker, RDS (PostgreSQL), and a CI/CD pipeline.
   - **Documentation**: `README.md` explaining local setup and deployment.

   **Deliverables**: Fully deployed application and clear documentation.

---

## Evaluation Criteria

1. **API Integration**: Efficiency in fetching data and handling API limits.
2. **Backtesting Logic**: Robust implementation and accurate performance metric calculations.
3. **ML Integration**: Effective handling of a pre-trained model and clear separation of logic.
4. **Reporting**: Clear reports with visualizations and PDF generation.
5. **Deployment**: Production readiness, security, and scalability.
6. **Documentation**: Detailed `README.md` that is user-friendly.

---


# Django Stock Prediction Backend
This project implements a Django-based backend that fetches financial data, stores it in a PostgreSQL database, performs backtesting on historical data, uses a machine learning model to predict future stock prices, and generates visual and PDF reports.

## Introduction
This project is a Django-based backend system designed to:

Fetch financial data from Alpha Vantage API.
Store it in a PostgreSQL database.
Implement a simple backtesting module.
Predict future stock prices using a pre-trained linear regression model.
Generate reports in PDF and JSON formats.
Deploy the system in a Dockerized environment with AWS RDS for database management.

## Prerequisites
Before running this project, ensure you have the following installed:
- Python 3.12+
- Django 5.1+
- PostgreSQL
- Alpha Vantage API Key (to fetch stock data)
- Required Python packages (installed via `requirements.txt`)

## command to run server 
python manage.py runserver 

## command to run docker 
docker-compose up --build

#migrate to databases, apply Django migrations
docker-compose exec web python manage.py migrate

## command to run docker (login)
docker-compose down
docker-compose up --build


## command to get API info
python manage.py shell
from myapp.fetch_data import fetch_stock_data
fetch_stock_data('AAPL')

## Run queries in the Django shell to verify that the data has been saved correctly:
from myapp.models import StockData
data = StockData.objects.filter(symbol='AAPL')
for entry in data:
    print(entry.timestamp, entry.close_price)

## To apply changes
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

## upload historical dates
docker-compose exec web python manage.py load_stock_data


## command to run model APPL
docker-compose exec web python manage.py train_ml_model AAPL
http://localhost:8000/predict/AAPL/

## backtesting for the AAPL symbol with the following URL:
http://localhost:8000/backtest/AAPL/10000/

## Generate a PDF report by visiting:
http://localhost:8000/report/AAPL/

## all urls
Acceso al panel de administración: http://localhost:8000/admin
Backtesting: http://localhost:8000/backtest/AAPL/10000/
Predicciones: http://localhost:8000/predict/AAPL/
Generación de reportes: http://localhost:8000/report/AAPL/
Reporte en JSON: http://localhost:8000/report/json/AAPL/


## reiniciar server docker : 
docker-compose down
docker-compose up --build
docker-compose ps
docker-compose logs web

## get in utf-8 the Encoding
to run app server works correctly, verify that it is in UTF-8 

## FUNCTIONS
fetch_stock_data: It fetches historical data from Alpha Vantage and saves it to the database.
train_model: Train a linear regression model using historical data.
predict_next_30_days: It uses the trained model to predict the next 30 days of a stock's prices.
