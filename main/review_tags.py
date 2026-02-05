from django import template
from main.models import Review
from django.db.models import Avg

register = template.Library()

@register.filter
def average_rating(card):
    """Возвращает средний рейтинг блюда"""
    reviews = Review.objects.filter(card=card)
    if reviews.exists():
        return reviews.aggregate(Avg('rating'))['rating__avg']
    return None

@register.filter
def review_count(card):
    """Возвращает количество отзывов"""
    return Review.objects.filter(card=card).count()