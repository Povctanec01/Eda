# models.py - дополненный код Profile
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('student', 'Student'), ('chef', 'Chef'), ('admin', 'Admin')])
    auto_redirect_to_home = models.BooleanField(default=False)

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

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def get_all_allergens(self):
        """Получить все аллергены пользователя"""
        return self.critical_allergens.all() | self.non_critical_allergens.all()

    def has_critical_allergen(self, allergen):
        """Проверить, является ли аллерген критическим для пользователя"""
        return self.critical_allergens.filter(id=allergen.id).exists()

    def has_non_critical_allergen(self, allergen):
        """Проверить, является ли аллерген некритическим для пользователя"""
        return self.non_critical_allergens.filter(id=allergen.id).exists()

    # models.py - в класс Profile
    def get_role_display(self):
        """Получить отображаемое имя роли"""
        role_display = {
            'student': 'Студент',
            'chef': 'Повар',
            'admin': 'Администратор'
        }
        # Если роль пустая или None, возвращаем значение по умолчанию
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


# Остальные модели остаются без изменений
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
    ingredients = models.TextField('Ингредиенты', blank=True, null=True)
    # Заменяем CharField на ManyToManyField
    allergens = models.ManyToManyField(Allergen, blank=True, verbose_name="Аллергены")
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


# Сигнал для автоматического создания профиля при создании пользователя
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