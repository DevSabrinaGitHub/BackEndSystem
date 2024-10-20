from django.contrib import admin
from .models import StockData, Prediction  

admin.site.register(StockData)
admin.site.register(Prediction)