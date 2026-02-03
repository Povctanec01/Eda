from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, datetime, timedelta
from main.models import Card, Order, CardBuys, Profile
from main.forms import CardForm, CardFormBuys


class StaffRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[('chef', 'Повар'), ('admin', 'Администратор')],
        label="Роль",
        widget=forms.Select(attrs={'class': 'form-control try'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Пароль должен содержать минимум 8 символов")
        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        role = self.cleaned_data['role']

        # Создаем пользователя
        user = User.objects.create_user(username=username, password=password)

        # Если роль 'admin', делаем суперпользователем
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()

        # Убедимся, что роль не пустая
        if not role:
            role = 'student'

        user.profile.role = role
        user.profile.save()
        return user

@login_required
def admin_home_page(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    now = timezone.now()
    today_start = timezone.make_aware(timezone.datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(timezone.datetime.combine(now.date(), time.max))
    orders_today_all = Order.objects.filter(ordered_at__range=(today_start, today_end))
    breakfast_today = orders_today_all.filter(card__meal_type='breakfast').count()
    lunch_today = orders_today_all.filter(card__meal_type='lunch').count()

    total_ordered_today = orders_today_all.count()

    # Убираем дублирующую проверку, так как уже есть login_required
    student_count = Profile.objects.filter(role='student').count()
    return render(request, 'main/admin_dashboard/admin_home_page.html', {
        'student_count': student_count,
        'total_ordered_today': total_ordered_today,
        'breakfast_today': breakfast_today,
        'lunch_today': lunch_today,
    })


@login_required
def admin_settings(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
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
                return redirect('admin_settings')

            # Проверка совпадения новых паролей
            if new_password1 != new_password2:
                messages.error(request, "Новые пароли не совпадают.")
                return redirect('admin_settings')

            # Проверка длины пароля
            if len(new_password1) < 8:
                messages.error(request, "Пароль должен содержать минимум 8 символов.")
                return redirect('admin_settings')

            # Изменение пароля
            request.user.set_password(new_password1)
            request.user.save()

            # Обновляем сессию, чтобы пользователь не разлогинился
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, "Пароль успешно изменён!")
            return redirect('admin_settings')

        if  request.method == 'POST' and 'delete_account' in request.POST:
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
        return redirect('admin_settings')

    return render(request, 'main/admin_dashboard/admin_settings.html')


@login_required
def admin_card_edit(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    form = CardForm()

    if request.method == 'POST' and 'delete' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('admin_card_edit')

    if request.method == 'POST' and 'toggle_visibility' in request.POST :
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.is_hidden = not card.is_hidden
        card.save()

        action = "скрыто" if card.is_hidden else "отображено"
        messages.success(request, f"Блюдо «{card.title}» {action}.")
        return redirect('admin_card_edit')


    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/admin_dashboard/admin_card_edit.html', {'form': form, 'cards': cards})


@login_required
def admin_buys(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    one_week_ago = timezone.now() - timedelta(days=7)
    buys_queryset = CardBuys.objects.filter(created_at__gte=one_week_ago)
    pending_count = buys_queryset.filter(status='pending').count()
    rejected_count = buys_queryset.filter(status='rejected').count()
    approved_count = buys_queryset.filter(status='approved').count()

    if request.method == 'POST':
        if 'action' in request.POST:
            buy_id = request.POST.get('buy_id')
            action = request.POST.get('action')
            buy = get_object_or_404(CardBuys, id=buy_id)
            if action == 'approve':
                buy.status = 'approved'
                messages.success(request, f"Запрос «{buy.title}» принят.")
            elif action == 'reject':
                buy.status = 'rejected'
                messages.warning(request, f"Запрос «{buy.title}» отклонён.")
            buy.save()
            return redirect('admin_buys')

        if 'delete' in request.POST:
            card_id_buys = request.POST.get('card_id_buys')
            buy = get_object_or_404(CardBuys, id=card_id_buys)
            buy.delete()
            messages.success(request, "Блюдо удалено.")
            return redirect('admin_buys')

        if 'add' in request.POST:
            form_buys = CardFormBuys(request.POST)
            if form_buys.is_valid():
                form_buys.save()
                messages.success(request, "Запрос отправлен!")
                return redirect('admin_buys')
            else:
                for field, errors in form_buys.errors.items():
                    for error in errors:
                        messages.error(request, f"Ошибка: {error}")
    else:
        form_buys = CardFormBuys()

    buys = CardBuys.objects.all().order_by('-created_at')
    return render(request, 'main/admin_dashboard/admin_buys.html', {
        'form_buys': form_buys,
        'buys': buys,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'approved_count': approved_count,
    })


@login_required
def admin_finance(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')

    now = timezone.now()
    today_start = timezone.make_aware(timezone.datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(timezone.datetime.combine(now.date(), time.max))

    # Заказы за разные периоды
    orders_today_all = Order.objects.filter(ordered_at__range=(today_start, today_end))
    orders_week_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=7))
    orders_month_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=30))

    # Функция для расчета выручки вручную (без агрегации)
    def calculate_revenue(orders):
        total = 0.00
        for order in orders:
            if order.card and order.card.price:
                try:
                    total += float(order.card.price)
                except (ValueError, TypeError):
                    continue
        return total

    # Функция для расчета выручки по типу блюда
    def calculate_revenue_by_type(orders, meal_type):
        total = 0.00
        for order in orders:
            if order.card and order.card.price and order.card.meal_type == meal_type:
                try:
                    total += float(order.card.price)
                except (ValueError, TypeError):
                    continue
        return total

    # Функция для получения топ-блюд
    def get_top_dishes(orders, limit=5):
        dish_revenue = {}
        for order in orders:
            if order.card:
                dish_id = order.card.id
                if dish_id not in dish_revenue:
                    dish_revenue[dish_id] = {
                        'dish': order.card,
                        'revenue': 0.00,
                        'count': 0
                    }
                try:
                    dish_revenue[dish_id]['revenue'] += float(order.card.price) if order.card.price else 0.00
                except (ValueError, TypeError):
                    continue
                dish_revenue[dish_id]['count'] += 1

        # Сортируем по выручке и берем топ
        sorted_dishes = sorted(dish_revenue.values(), key=lambda x: x['revenue'], reverse=True)[:limit]
        return sorted_dishes

    # Расчет выручки
    revenue_today = calculate_revenue(orders_today_all)
    revenue_week = calculate_revenue(orders_week_all)
    revenue_month = calculate_revenue(orders_month_all)

    # Статистика по типам блюд
    breakfast_revenue_today = calculate_revenue_by_type(orders_today_all, 'breakfast')
    lunch_revenue_today = calculate_revenue_by_type(orders_today_all, 'lunch')
    breakfast_revenue_week = calculate_revenue_by_type(orders_week_all, 'breakfast')
    lunch_revenue_week = calculate_revenue_by_type(orders_week_all, 'lunch')
    breakfast_revenue_month = calculate_revenue_by_type(orders_month_all, 'breakfast')
    lunch_revenue_month = calculate_revenue_by_type(orders_month_all, 'lunch')

    # Количество заказов
    total_ordered_today = orders_today_all.count()
    total_ordered_week = orders_week_all.count()
    total_ordered_month = orders_month_all.count()

    # Средний чек
    avg_check_today = revenue_today / total_ordered_today if total_ordered_today > 0 else 0.00
    avg_check_week = revenue_week / total_ordered_week if total_ordered_week > 0 else 0.00
    avg_check_month = revenue_month / total_ordered_month if total_ordered_month > 0 else 0.00

    # Топ блюд
    top_revenue_dishes_week = get_top_dishes(orders_week_all, 5)
    top_revenue_dishes_month = get_top_dishes(orders_month_all, 5)

    # Количество завтраков и обедов
    breakfast_today = orders_today_all.filter(card__meal_type='breakfast').count()
    lunch_today = orders_today_all.filter(card__meal_type='lunch').count()
    breakfast_week = orders_week_all.filter(card__meal_type='breakfast').count()
    lunch_week = orders_week_all.filter(card__meal_type='lunch').count()
    breakfast_month = orders_month_all.filter(card__meal_type='breakfast').count()
    lunch_month = orders_month_all.filter(card__meal_type='lunch').count()

    # Преобразуем данные для шаблона - убедимся, что это числа
    context = {
        'revenue_today': float(round(revenue_today, 2)),
        'revenue_week': float(round(revenue_week, 2)),
        'revenue_month': float(round(revenue_month, 2)),

        'breakfast_revenue_today': float(round(breakfast_revenue_today, 2)),
        'lunch_revenue_today': float(round(lunch_revenue_today, 2)),
        'breakfast_revenue_week': float(round(breakfast_revenue_week, 2)),
        'lunch_revenue_week': float(round(lunch_revenue_week, 2)),
        'breakfast_revenue_month': float(round(breakfast_revenue_month, 2)),
        'lunch_revenue_month': float(round(lunch_revenue_month, 2)),

        'total_ordered_today': total_ordered_today,
        'total_ordered_week': total_ordered_week,
        'total_ordered_month': total_ordered_month,

        'avg_check_today': float(round(avg_check_today, 2)),
        'avg_check_week': float(round(avg_check_week, 2)),
        'avg_check_month': float(round(avg_check_month, 2)),

        'top_revenue_dishes_week': top_revenue_dishes_week,
        'top_revenue_dishes_month': top_revenue_dishes_month,

        'breakfast_today': breakfast_today,
        'lunch_today': lunch_today,
        'breakfast_week': breakfast_week,
        'lunch_week': lunch_week,
        'breakfast_month': breakfast_month,
        'lunch_month': lunch_month,
    }

    return render(request, 'main/admin_dashboard/admin_finance.html', context)

@login_required
def admin_users_delete_selected(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        usernames = request.POST.getlist('usernames[]')

        if not usernames:
            messages.warning(request, "Не выбрано ни одного пользователя.")
            return redirect('admin_users_statistics')

        deleted_count = 0
        for username in usernames:
            try:
                user = User.objects.get(username=username)

                # ЗАПРЕТИТЬ удаление:
                # 1. Себя самого
                if user.id == request.user.id:
                    messages.warning(request, "Нельзя удалить свой собственный аккаунт!")
                    continue

                # 2. Других администраторов (кроме суперпользователя)
                if hasattr(user, 'profile') and user.profile.role == 'admin':
                    messages.warning(request, f"Нельзя удалить администратора {username}!")
                    continue

                # 3. Суперпользователей (если удаляющий не суперпользователь)
                if user.is_superuser and not request.user.is_superuser:
                    messages.warning(request, f"Нельзя удалить суперпользователя {username}!")
                    continue

                user.delete()
                deleted_count += 1

            except User.DoesNotExist:
                continue

        if deleted_count > 0:
            messages.success(request, f"Успешно удалено {deleted_count} пользователей.")
        else:
            messages.warning(request, "Нет пользователей для удаления.")

    return redirect('admin_users_statistics')


@login_required
def admin_users_statistics(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    # Обработка формы добавления персонала
    staff_form = StaffRegistrationForm()
    if request.method == 'POST':
        staff_form = StaffRegistrationForm(request.POST)
        if staff_form.is_valid():
            try:
                user = staff_form.save()
                # Проверяем, что роль не пустая
                if user.profile.role:
                    role_display = user.profile.get_role_display()
                else:
                    role_display = "Не указана"

                # Добавляем информацию о суперпользователе
                if user.is_superuser:
                    role_display += " (Суперпользователь)"

                messages.success(request, f"Пользователь '{user.username}' успешно создан как {role_display}.")
                return redirect('admin_users_statistics')
            except Exception as e:
                messages.error(request, f"Ошибка при создании пользователя: {str(e)}")

    # Сбор статистики
    users_with_roles = []
    for user in User.objects.all():
        try:
            role = user.profile.role or 'student'  # Если роль пустая, ставим 'student'
        except Profile.DoesNotExist:
            role = 'student'

        users_with_roles.append({
            'username': user.username,
            'role': role,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'id': user.id,
        })
    role_priority = {'admin': 1, 'chef': 2, 'student': 3}
    users_with_roles.sort(key=lambda x: role_priority.get(x['role'], 1))
    role_counts = {'student': 0, 'chef': 0, 'admin': 0}
    for ur in users_with_roles:
        # Убедимся, что роль не пустая
        role = ur['role'] or 'student'
        if role in role_counts:
            role_counts[role] += 1
        else:
            # Если роль какая-то нестандартная, считаем как студента
            role_counts['student'] += 1

    return render(request, 'main/admin_dashboard/admin_users_statistics.html', {
        'users_with_roles': users_with_roles,
        'role_counts': role_counts,
        'staff_form': staff_form,
    })


@login_required
def admin_statistics(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')

    now = timezone.now()
    today_start = timezone.make_aware(timezone.datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(timezone.datetime.combine(now.date(), time.max))

    # === ВСЕ ЗАКАЗЫ ===
    orders_today_all = Order.objects.filter(ordered_at__range=(today_start, today_end))
    orders_week_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=7))
    orders_month_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=30))

    # Статистика по типам приема пищи для всех заказов
    breakfast_today = orders_today_all.filter(card__meal_type='breakfast').count()
    lunch_today = orders_today_all.filter(card__meal_type='lunch').count()

    breakfast_week = orders_week_all.filter(card__meal_type='breakfast').count()
    lunch_week = orders_week_all.filter(card__meal_type='lunch').count()

    breakfast_month = orders_month_all.filter(card__meal_type='breakfast').count()
    lunch_month = orders_month_all.filter(card__meal_type='lunch').count()

    total_ordered_today = orders_today_all.count()
    total_ordered_week = orders_week_all.count()
    total_ordered_month = orders_month_all.count()

    # === ГОТОВЫЕ БЛЮДА (status = 'ready' или 'received') ===
    ready_statuses = ['ready', 'received']

    orders_today_ready = Order.objects.filter(
        ordered_at__range=(today_start, today_end),
        status__in=ready_statuses
    )
    orders_week_ready = Order.objects.filter(
        ordered_at__gte=now - timedelta(days=7),
        status__in=ready_statuses
    )
    orders_month_ready = Order.objects.filter(
        ordered_at__gte=now - timedelta(days=30),
        status__in=ready_statuses
    )

    # Статистика по типам приема пищи для готовых заказов
    breakfast_ready_today = orders_today_ready.filter(card__meal_type='breakfast').count()
    lunch_ready_today = orders_today_ready.filter(card__meal_type='lunch').count()

    breakfast_ready_week = orders_week_ready.filter(card__meal_type='breakfast').count()
    lunch_ready_week = orders_week_ready.filter(card__meal_type='lunch').count()

    breakfast_ready_month = orders_month_ready.filter(card__meal_type='breakfast').count()
    lunch_ready_month = orders_month_ready.filter(card__meal_type='lunch').count()

    total_ready_today = orders_today_ready.count()
    total_ready_week = orders_week_ready.count()
    total_ready_month = orders_month_ready.count()

    return render(request, 'main/admin_dashboard/admin_statistics.html', {
        # Статистика по всем заказам
        'total_ordered_today': total_ordered_today,
        'total_ordered_week': total_ordered_week,
        'total_ordered_month': total_ordered_month,

        # Детализация по типам приема пищи (все заказы)
        'breakfast_today': breakfast_today,
        'lunch_today': lunch_today,
        'breakfast_week': breakfast_week,
        'lunch_week': lunch_week,
        'breakfast_month': breakfast_month,
        'lunch_month': lunch_month,

        # Статистика по готовым заказам
        'total_ready_today': total_ready_today,
        'total_ready_week': total_ready_week,
        'total_ready_month': total_ready_month,

        # Детализация по типам приема пищи (готовые заказы)
        'breakfast_ready_today': breakfast_ready_today,
        'lunch_ready_today': lunch_ready_today,
        'breakfast_ready_week': breakfast_ready_week,
        'lunch_ready_week': lunch_ready_week,
        'breakfast_ready_month': breakfast_ready_month,
        'lunch_ready_month': lunch_ready_month,
    })
