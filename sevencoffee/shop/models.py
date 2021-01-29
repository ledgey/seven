from django.db import models

# Create your models here.

class Contents(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=150)

class Items(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=150)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    image = models.ImageField(upload_to='food')
    contains = models.ForeignKey(Contents, on_delete=models.CASCADE)

class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.CharField(max_length=300)








