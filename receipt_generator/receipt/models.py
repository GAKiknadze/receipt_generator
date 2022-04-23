from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=60, unique=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
