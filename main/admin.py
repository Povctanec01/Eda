# cards_app/admin.py
from django.contrib import admin
from .models import Card, Order

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'meal_type', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('card', 'ordered_at')