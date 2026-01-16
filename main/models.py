from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    ingredients = models.TextField('Ингредиенты', blank=True, null=True)
    allergens = models.CharField('Аллергены', max_length=255, blank=True, null=True)
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

class CardBuys(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    title = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=[('breakfast', 'Завтрак'), ('lunch', 'Обед')], blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Готовится'),
        ('ready', 'Готов'),
        ('received', 'Получен'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Блюдо"
    )
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время заказа")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        username = self.user.username if self.user else "Неизвестный"
        title = self.card.title if self.card else "[УДАЛЁННОЕ БЛЮДО]"
        return f"{username} → {title} ({self.get_status_display()})"