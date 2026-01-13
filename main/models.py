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
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,  # ← вместо CASCADE
        null=True,                  # ← обязательно, так как поле может стать NULL
        verbose_name="Блюдо"
    )
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время заказа")

    def __str__(self):
        if self.card:
            return f"Заказ: {self.card.title} в {self.ordered_at.strftime('%H:%M')}"
        else:
            return f"Заказ: [УДАЛЁННОЕ БЛЮДО] в {self.ordered_at.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class CardBuys(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"