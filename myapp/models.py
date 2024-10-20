from django.db import models


#creating models
#class StockData(models.Model):
    #symbol = models.CharField(max_length=10)
    #timestamp = models.DateTimeField()
   # open_price = models.DecimalField(max_digits=20, decimal_places=6)
   # close_price = models.DecimalField(max_digits=20, decimal_places=6)
    #high_price = models.DecimalField(max_digits=20, decimal_places=6)
    #low_price = models.DecimalField(max_digits=20, decimal_places=6)
    #volume = models.BigIntegerField()

    #class Meta:
      #  unique_together = ('symbol', 'timestamp')
       # indexes = [
         #   models.Index(fields=['symbol', 'timestamp']),
       # ]
        #ordering = ['-timestamp']

   # def __str__(self):
       # return f"{self.symbol} - {self.timestamp.strftime('%Y-%m-%d')}"

from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open_price = models.FloatField(null=True, blank=True)  
    close_price = models.FloatField(null=True, blank=True)  
    high_price = models.FloatField(null=True, blank=True)   
    low_price = models.FloatField(null=True, blank=True)    
    volume = models.BigIntegerField(null=True, blank=True)  

    def __str__(self):
        return f'{self.symbol} - {self.timestamp}'

    
#class Prediction(models.Model):
   # symbol = models.CharField(max_length=10)
   # date = models.DateField()
    #predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    #actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    #def __str__(self):
    #    return f"{self.symbol} - {self.date}"


class Prediction(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    predicted_price = models.FloatField()
    actual_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.date}"

