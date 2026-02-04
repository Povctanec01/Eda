from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('student', 'Student'), ('chef', 'Chef'), ('admin', 'Admin')])
    auto_redirect_to_home = models.BooleanField(default=False)
    # Баланс
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Баланс",
        default=0.00
    )

    # Аллергены студента
    critical_allergens = models.ManyToManyField(
        'Allergen',
        related_name='critical_profiles',
        blank=True,
        verbose_name="Критические аллергены",
        help_text="Блюда с этими аллергенами будут скрыты"
    )

    non_critical_allergens = models.ManyToManyField(
        'Allergen',
        related_name='non_critical_profiles',
        blank=True,
        verbose_name="Некритические аллергены",
        help_text="Блюда с этими аллергенами будут отображаться с предупреждением"
    )

    # ДОБАВЬТЕ ЭТО ПОЛЕ ДЛЯ ЛАЙКОВ
    liked_cards = models.ManyToManyField(
        'Card',
        related_name='liked_by_profiles',
        blank=True,
        verbose_name="Понравившиеся блюда",
        help_text="Блюда, отмеченные пользователем как понравившиеся"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def get_all_allergens(self):
        return self.critical_allergens.all() | self.non_critical_allergens.all()

    def has_critical_allergen(self, allergen):
        return self.critical_allergens.filter(id=allergen.id).exists()

    def has_non_critical_allergen(self, allergen):
        return self.non_critical_allergens.filter(id=allergen.id).exists()

    def get_role_display(self):
        role_display = {
            'student': 'Студент',
            'chef': 'Повар',
            'admin': 'Администратор'
        }
        if not self.role:
            return 'Студент'
        return role_display.get(self.role, self.role)

class Allergen(models.Model):
    name = models.CharField('Название аллергена', max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Аллерген"
        verbose_name_plural = "Аллергены"

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
    price = models.DecimalField(  # ДОБАВИТЬ ЭТО ПОЛЕ
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        default=0.00
    )
    ingredients = models.TextField('Ингредиенты', blank=True, null=True)
    allergens = models.ManyToManyField(Allergen, blank=True, verbose_name="Аллергены")
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False, verbose_name="Скрыто")

    def __str__(self):
        hidden_status = " (скрыто)" if self.is_hidden else ""
        return f"{self.title} ({self.get_meal_type_display()}) - {self.price} руб.{hidden_status}"

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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)


class ProductRemaining(models.Model):
    """Модель для отслеживания остатков продуктов на складе"""
    name = models.CharField(max_length=255, verbose_name="Название продукта")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Количество"
    )
    unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения",
        default="кг"
    )
    min_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Минимальное количество",
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Остаток продукта"
        verbose_name_plural = "Остатки продуктов"

    def __str__(self):
        return f"{self.name} - {self.quantity} {self.unit}"

    def is_low_stock(self):
        """Проверяет, есть ли низкий запас продукта"""
        return self.quantity <= self.min_quantity


# Добавьте в конец models.py или после модели ProductRemaining
class BuffetProduct(models.Model):
    CATEGORY_CHOICES = [
        ('baked', 'Выпечка'),
        ('sweets', 'Сладости'),
        ('drinks', 'Напитки'),
        ('snacks', 'Закуски'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание", blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        default=0.00
    )
    ingredients = models.TextField(verbose_name="Состав", blank=True)
    allergens = models.ManyToManyField(Allergen, blank=True, verbose_name="Аллергены")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    stock_quantity = models.IntegerField(
        default=0,
        verbose_name="Количество в наличии"
    )

    class Meta:
        verbose_name = "Буфетный товар"
        verbose_name_plural = "Буфетные товары"
        ordering = ['category', 'name']

    def __str__(self):
        available = "✓" if self.is_available else "✗"
        return f"{self.name} ({self.get_category_display()}) - {self.price} руб. [{available}]"