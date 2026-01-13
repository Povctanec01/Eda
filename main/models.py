from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('chef', 'Chef'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

class Card(models.Model):
    MEAL_CHOICES = [
        ('select', 'Выберите'),
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    meal_type = models.CharField(
        max_length=10,
        choices=MEAL_CHOICES,
        default='select',
        verbose_name="Тип приёма пищи"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_meal_type_display()})"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

# cards_app/models.py (добавьте ниже)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Блюдо"
    )
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время заказа")

    def __str__(self):
        username = self.user.username if self.user else "Неизвестный"
        title = self.card.title if self.card else "[УДАЛЁННОЕ БЛЮДО]"
        return f"{username} → {title} ({self.ordered_at.strftime('%d.%m %H:%M')})"

class CardBuys(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"