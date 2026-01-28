# main/views/student_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from ..models import Card, Order, Allergen
from django.utils import timezone
from datetime import time, datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


# Обновить student_home_page в student_views.py

@login_required
def student_home_page(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    # Определяем начало и конец текущего дня
    today = timezone.now().date()
    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))

    # Подсчёт заказов за сегодня
    pending_orders_count = Order.objects.filter(
        user=request.user,
        status='pending',
        ordered_at__range=(start_of_day, end_of_day)
    ).count()

    ready_orders_count = Order.objects.filter(
        user=request.user,
        status='ready',
        ordered_at__range=(start_of_day, end_of_day)
    ).count()

    # Получаем все блюда на сегодня
    today_cards = Card.objects.exclude(meal_type='select').order_by('meal_type', 'title')

    # Получаем аллергены пользователя
    profile = request.user.profile
    critical_allergens = profile.critical_allergens.all()
    non_critical_allergens = profile.non_critical_allergens.all()

    # Фильтруем блюда с критическими аллергенами
    if critical_allergens.exists():
        today_cards = today_cards.exclude(
            allergens__in=critical_allergens
        ).distinct()

    # Добавляем информацию об аллергенах для каждого блюда
    filtered_cards = []
    for card in today_cards:
        # Проверяем некритические аллергены
        card_non_critical_allergens = card.allergens.filter(
            id__in=non_critical_allergens.values_list('id', flat=True)
        )

        # Добавляем признак наличия некритических аллергенов
        if card_non_critical_allergens.exists():
            card.has_non_critical_allergens = True
            card.non_critical_allergens_list = list(card_non_critical_allergens)
        else:
            card.has_non_critical_allergens = False
            card.non_critical_allergens_list = []

        # Добавляем badge class для типа блюда
        if card.meal_type == 'breakfast':
            card.badge_class = 'bg-success'
        elif card.meal_type == 'lunch':
            card.badge_class = 'bg-primary'
        else:
            card.badge_class = 'bg-secondary'

        filtered_cards.append(card)

    all_orders_count = Order.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:3]

    return render(request, 'main/student_dashboard/student_home_page.html', {
        'today_cards': filtered_cards,
        'orders': recent_orders,
        'all_orders_count': all_orders_count,
        'pending_orders_count': pending_orders_count,
        'ready_orders_count': ready_orders_count,
    })


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

            # Обновляем сессию, чтобы пользователь не разлогинился
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, "Пароль успешно изменён!")
            return redirect('student_settings')

        # Удаление аккаунта (если отправлена именно эта форма)
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

    # GET: просто показываем страницу настроек
    return render(request, 'main/student_dashboard/student_settings.html')

@login_required
def student_order_create(request, card_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')
    card = get_object_or_404(Card, id=card_id)
    Order.objects.create(user=request.user, card=card)
    messages.success(request, f"Вы заказали: {card.title}!")
    return redirect('student_home_page')

def student_menu(request):
    from ..forms import CardForm
    form = CardForm(request.POST)
    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/student_dashboard/student_menu.html', {'form': form, 'cards': cards})

def student_feedback(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'main/student_dashboard/student_feedback.html')


@login_required
def student_order_history(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    # Все заказы пользователя, от новых к старым
    orders = Order.objects.filter(user=request.user).select_related('card').order_by('-ordered_at')

    return render(request, 'main/student_dashboard/student_order_history.html', {
        'orders': orders
    })

@login_required
def student_my_orders(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    status_filter = request.GET.get('status')
    if status_filter in ['pending', 'ready']:
        orders = Order.objects.filter(user=request.user, status=status_filter).order_by('-ordered_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-ordered_at')

    return render(request, 'main/student_dashboard/student_my_orders.html', {
        'orders': orders,
        'current_status': status_filter
    })

@login_required
def student_mark_received(request, order_id):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')
    order = get_object_or_404(Order, id=order_id, user=request.user, status='ready')
    order.status = 'received'
    order.save()
    return redirect(request.META.get('HTTP_REFERER', 'student_home_page'))


# Добавить в student_views.py

@login_required
def student_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    # Получаем все аллергены
    all_allergens = Allergen.objects.all().order_by('name')

    # Получаем аллергены студента из профиля
    profile = request.user.profile
    critical_allergens = profile.critical_allergens.all()
    non_critical_allergens = profile.non_critical_allergens.all()

    return render(request, 'main/student_dashboard/student_allergens.html', {
        'all_allergens': all_allergens,
        'critical_allergens': critical_allergens,
        'non_critical_allergens': non_critical_allergens,
    })


@login_required
def update_critical_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        profile = request.user.profile
        selected_allergen_ids = request.POST.getlist('critical_allergens')

        # Обновляем критические аллергены
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


@login_required
def update_non_critical_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')

    if request.method == 'POST':
        profile = request.user.profile
        selected_allergen_ids = request.POST.getlist('non_critical_allergens')

        # Обновляем некритичные аллергены
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