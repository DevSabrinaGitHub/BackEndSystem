from django.urls import path
from myapp.views import home, backtest, plot_stock_prices, train_ml_model, generate_pdf_report, generate_json_report, predict_stock
from django.contrib import admin
from django.urls import path
from myapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('backtest/<str:symbol>/<int:initial_investment>/', backtest, name='backtest'),
    #path('backtest/<str:symbol>/<int:initial_investment>/', views.backtest, name='backtest'),
    path('train_model/<str:symbol>/', train_ml_model, name='train_ml_model'),
    path('plot/<str:symbol>/', plot_stock_prices, name='plot_stock_prices'),
    path('report/json/<str:symbol>/', generate_json_report, name='generate_json_report'),
    path('predict/<str:symbol>/', predict_stock, name='predict_stock'),
    path('report/<str:symbol>/', views.generate_pdf_report, name='generate_pdf_report'),
]
