from main.models import Card, Order, Allergen, BuffetProduct, Review
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from datetime import time, datetime, timedelta
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from main.forms import CardForm
from decimal import Decimal


# Домашняя страница
@login_required
def student_home_page(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    # Показвыаем все НЕ скрытые блюда на сегодня
    today_cards = Card.objects.filter(
        is_hidden=False  # Только не скрытые блюда
    ).exclude(meal_type='select').order_by('meal_type', 'title')

    # Аллергены пользователя
    profile = request.user.profile
    critical_allergens = profile.critical_allergens.all()
    non_critical_allergens = profile.non_critical_allergens.all()

    # Убираем блюда с критическими аллергенами
    if critical_allergens.exists():
        today_cards = today_cards.exclude(
            allergens__in=critical_allergens
        ).distinct()

    # Добавляем информацию об аллергенах и рейтингах для каждого блюда
    filtered_cards = []
    for card in today_cards:
        # Проверяем некритичные аллергены
        card_non_critical_allergens = card.allergens.filter(
            id__in=non_critical_allergens.values_list('id', flat=True)
        )

        if card_non_critical_allergens.exists():
            card.has_non_critical_allergens = True
            card.non_critical_allergens_list = list(card_non_critical_allergens)
        else:
            card.has_non_critical_allergens = False
            card.non_critical_allergens_list = []

        if card.meal_type == 'breakfast':
            card.badge_class = 'bg-success'
        elif card.meal_type == 'lunch':
            card.badge_class = 'bg-primary'
        else:
            card.badge_class = 'bg-secondary'

        # Информацию о рейтинге
        reviews = Review.objects.filter(card=card)
        if reviews.exists():
            from django.db.models import Avg
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            card.average_rating = round(avg_rating, 1)
            card.review_count = reviews.count()
        else:
            card.average_rating = None
            card.review_count = 0

        filtered_cards.append(card)

    all_orders_count = Order.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:3]

    return render(request, 'main/student_dashboard/student_home_page.html', {
        'today_cards': filtered_cards,
        'orders': recent_orders,
        'all_orders_count': all_orders_count,
        'balance': profile.balance,
    })


# Пополнение счёта
@login_required
def top_up_balance(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return JsonResponse({'success': False, 'error': 'Доступ запрещен'}, status=403)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))

            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'Сумма должна быть положительной'})

            if amount > 10000:  # Ограничение на максимальное пополнение
                return JsonResponse({'success': False, 'error': 'Максимальная сумма пополнения - 10000 руб'})

            # Пополняем баланс
            profile = request.user.profile
            profile.balance += amount
            profile.save()

            return JsonResponse({
                'success': True,
                'new_balance': float(profile.balance),
                'message': f'Баланс успешно пополнен на {amount} руб.'
            })

        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': 'Неверная сумма'})

    return JsonResponse({'success': False, 'error': 'Упс, Произошла Ошибка'})


#Заказ
@login_required
def student_order_create(request, card_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    card = get_object_or_404(Card, id=card_id)

    # Проверяем, не скрыто ли блюдо
    if card.is_hidden:
        messages.error(request, "Это блюдо временно недоступно для заказа.")
        return redirect('student_home_page')

    # Проверяем баланс пользователя
    profile = request.user.profile
    if profile.balance < card.price:
        messages.error(request,f"Недостаточно средств на счете. Требуется: {card.price} руб., доступно: {profile.balance} руб.")
        return redirect('student_home_page')

    # Списываем средства
    profile.balance -= card.price
    profile.save()

    # Создаем заказ
    Order.objects.create(user=request.user, card=card)

    messages.success(request, f"Вы заказали: {card.title} за {card.price} руб.!")
    return redirect('student_home_page')

#Меню
@login_required
def student_menu(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    form = CardForm(request.POST)
    # Показываем только не скрытые блюда
    cards = Card.objects.filter(is_hidden=False).order_by('meal_type', 'title')
    for card in cards:
        reviews = Review.objects.filter(card=card)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            card.average_rating = round(avg_rating, 1)
            card.review_count = reviews.count()
        else:
            card.average_rating = None
            card.review_count = 0

    return render(request, 'main/student_dashboard/student_menu.html', {
        'form': form,
        'cards': cards
    })


# Отзывы
@login_required
def student_feedback(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    thirty_days_ago = timezone.now() - timedelta(days=30)

    evaluable_orders = Order.objects.filter(
        user=request.user,
        ordered_at__gte=thirty_days_ago,
        status__in=['ready', 'received']
    ).select_related('card').order_by('-ordered_at')

    reviewed_card_ids = Review.objects.filter(
        user=request.user
    ).values_list('card_id', flat=True)

    evaluable_orders = evaluable_orders.exclude(card_id__in=reviewed_card_ids)

    user_reviews = Review.objects.filter(
        user=request.user
    ).select_related('card').order_by('-created_at')

    return render(request, 'main/student_dashboard/student_feedback.html', {
        'evaluable_orders': evaluable_orders,
        'user_reviews': user_reviews
    })

#Обработчик отправки отзыва
@login_required
def submit_review(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        try:
            card_id = request.POST.get('card_id')
            rating = int(request.POST.get('rating', 0))

            if not card_id:
                return JsonResponse({'success': False, 'error': 'Блюдо не выбрано'})

            if rating < 1 or rating > 5:
                return JsonResponse({'success': False, 'error': 'Оценка должна быть от 1 до 5'})

            # Проверяем, что заказ существует и принадлежит пользователю
            card = get_object_or_404(Card, id=card_id)

            # Проверяем, что у пользователя был заказ этого блюда
            has_order = Order.objects.filter(
                user=request.user,
                card=card,
                status__in=['ready', 'received']
            ).exists()

            if not has_order:
                return JsonResponse({'success': False, 'error': 'Вы не заказывали это блюдо'})

            # Проверяем, нет ли уже отзыва
            existing_review = Review.objects.filter(
                user=request.user,
                card=card
            ).first()

            if existing_review:
                # Обновляем существующий отзыв - теперь только рейтинг
                existing_review.rating = rating
                existing_review.save()
                messages.success(request, f"Оценка для {card.title} обновлена!")
            else:
                Review.objects.create(
                    user=request.user,
                    card=card,
                    rating=rating
                )
                messages.success(request, f"Спасибо за оценку {card.title}!")

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Упс, Произошла Ошибка'})


#Удаление отзыва
@login_required
def delete_review(request, review_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    messages.success(request, "Отзыв удален")
    return redirect('student_feedback')


#Отметка нравиться (страница)
@login_required
def student_likes(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    all_cards = Card.objects.filter(is_hidden=False).exclude(meal_type='select').order_by('meal_type', 'title')

    # Лайкнутые блюда пользователя
    profile = request.user.profile
    liked_cards = profile.liked_cards.all()

    # Сортируем
    sorted_cards = []
    # Сначала лайкнутые
    for card in all_cards:
        if card in liked_cards:
            card.is_liked = True
            sorted_cards.append(card)
    for card in all_cards:
        if card not in liked_cards:
            card.is_liked = False
            sorted_cards.append(card)

    return render(request, 'main/student_dashboard/student_likes.html', {
        'cards': sorted_cards,
        'liked_cards': liked_cards
    })

# Отметка лайка
@login_required
def toggle_like(request, card_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    card = get_object_or_404(Card, id=card_id)
    profile = request.user.profile

    if card in profile.liked_cards.all():
        # Убираем лайк
        profile.liked_cards.remove(card)
        messages.success(request, f"Убрано из избранного: {card.title}")
    else:
        # Добавляем лайк
        profile.liked_cards.add(card)
        messages.success(request, f"Добавлено в избранное: {card.title}")

    profile.save()
    return redirect('student_likes')


#История
@login_required
def student_my_orders(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    #Отметка Забрал
    status_filter = request.GET.get('status')
    if status_filter in ['pending', 'ready']:
        orders = Order.objects.filter(user=request.user, status=status_filter).order_by('-ordered_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-ordered_at')

    return render(request, 'main/student_dashboard/student_my_orders.html', {
        'orders': orders,
        'current_status': status_filter
    })


#Аллергены
@login_required
def student_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    all_allergens = Allergen.objects.all().order_by('name')

    # Аллергены студента из профиля
    profile = request.user.profile
    critical_allergens = profile.critical_allergens.all()
    non_critical_allergens = profile.non_critical_allergens.all()

    return render(request, 'main/student_dashboard/student_allergens.html', {
        'all_allergens': all_allergens,
        'critical_allergens': critical_allergens,
        'non_critical_allergens': non_critical_allergens,
    })


#Обновление крит аллергенов
@login_required
def update_critical_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        profile = request.user.profile
        selected_allergen_ids = request.POST.getlist('critical_allergens')

        # Обновляем
        profile.critical_allergens.clear()
        for allergen_id in selected_allergen_ids:
            try:
                allergen = Allergen.objects.get(id=allergen_id)
                profile.critical_allergens.add(allergen)
            except Allergen.DoesNotExist:
                continue

        profile.save()
        messages.success(request, "Критические аллергены обновлены!")

    return redirect('student_allergens')


#Обновление Не крит аллергенов
@login_required
def update_non_critical_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        profile = request.user.profile
        selected_allergen_ids = request.POST.getlist('non_critical_allergens')

        # Обновляем не крит аллергены
        profile.non_critical_allergens.clear()
        for allergen_id in selected_allergen_ids:
            try:
                allergen = Allergen.objects.get(id=allergen_id)
                profile.non_critical_allergens.add(allergen)
            except Allergen.DoesNotExist:
                continue

        profile.save()
        messages.success(request, "Некритичные аллергены обновлены!")

    return redirect('student_allergens')


#Буфет
@login_required
def student_buffet(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    # Получаем доступные товары
    products = BuffetProduct.objects.filter(
        is_available=True
    ).order_by('category', 'name')

    # Фильтрация
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category=category_filter)

    # Аллергены пользователя
    profile = request.user.profile
    critical_allergens = profile.critical_allergens.all()

    # Убираем товары с критическими аллергенами
    if critical_allergens.exists():
        products = products.exclude(
            allergens__in=critical_allergens
        ).distinct()

    non_critical_allergens = profile.non_critical_allergens.all()
    filtered_products = []

    for product in products:
        # Проверяем некритические аллергены
        product_non_critical_allergens = product.allergens.filter(
            id__in=non_critical_allergens.values_list('id', flat=True)
        )

        if product_non_critical_allergens.exists():
            product.has_non_critical_allergens = True
            product.non_critical_allergens_list = list(product_non_critical_allergens)
        else:
            product.has_non_critical_allergens = False
            product.non_critical_allergens_list = []

        # Добавляем badge для категории
        category_badge_classes = {
            'baked': 'bg-warning',
            'sweets': 'bg-pink',
            'drinks': 'bg-info',
            'snacks': 'bg-secondary',
            'other': 'bg-dark'
        }
        product.category_badge_class = category_badge_classes.get(product.category, 'bg-dark')

        # Проверяем наличие на складе
        if product.stock_quantity == 0:
            product.is_out_of_stock = True
            product.availability_text = "Нет в наличии"
            product.availability_class = "text-danger"
        elif product.stock_quantity < 10:
            product.is_low_stock = True
            product.availability_text = f"Мало ({product.stock_quantity} шт.)"
            product.availability_class = "text-warning"
        else:
            product.is_out_of_stock = False
            product.is_low_stock = False
            product.availability_text = f"В наличии ({product.stock_quantity} шт.)"
            product.availability_class = "text-success"

        filtered_products.append(product)

    return render(request, 'main/student_dashboard/student_buffet.html', {
        'products': filtered_products,
        'category_filter': category_filter,
        'category_choices': BuffetProduct.CATEGORY_CHOICES,
    })

# Настройки
@login_required
def student_settings(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        # Изменение пароля
        if 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            # Проверка текущего пароля
            if not request.user.check_password(current_password):
                messages.error(request, "Текущий пароль указан неверно.")
                return redirect('student_settings')

            # Проверка совпадения новых паролей
            if new_password1 != new_password2:
                messages.error(request, "Новые пароли не совпадают.")
                return redirect('student_settings')

            # Проверка длины пароля
            if len(new_password1) < 8:
                messages.error(request, "Пароль должен содержать минимум 8 символов.")
                return redirect('student_settings')

            # Изменение пароля
            request.user.set_password(new_password1)
            request.user.save()


            update_session_auth_hash(request, request.user)

            messages.success(request, "Пароль успешно изменён!")
            return redirect('student_settings')

        # Удаление аккаунта
        if 'delete_account' in request.POST:
            user = request.user
            username = user.username
            user.delete()
            logout(request)
            messages.success(request, f"Ваш аккаунт '{username}' был успешно удалён.")
            return redirect('login')

        # Сохранение настроек автоперехода
        profile = request.user.profile
        profile.auto_redirect_to_home = 'auto_redirect' in request.POST
        profile.save()
        messages.success(request, "Настройки сохранены.")
        return redirect('student_settings')

    return render(request, 'main/student_dashboard/student_settings.html')

@login_required
def student_mark_received(request, order_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')
    order = get_object_or_404(Order, id=order_id, user=request.user, status='ready')
    order.status = 'received'
    order.save()
    return redirect(request.META.get('HTTP_REFERER', 'student_home_page'))
