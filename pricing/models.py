from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
class WeatherData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()  # in Kelvin
    weather_condition = models.CharField(max_length=100)
    
class BusyTimesData(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 0-6 for Monday-Sunday
    hour = models.IntegerField()  # 0-23
    busyness_level = models.FloatField()  # 0-1 scale
