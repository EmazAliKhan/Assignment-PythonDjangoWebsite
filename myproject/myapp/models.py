from django.db import models
import datetime
from django import forms

# Create your models here.
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

class PasswordResetForm(forms.Form):
    code = forms.CharField(label="Enter the 4-digit code", max_length=4)
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE , null=True)

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.FloatField()
    qty = models.IntegerField()
    active=models.BooleanField(default=True)
    description = models.CharField(max_length=100)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    imgurl = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)