# main/views/admin_views.py
from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, datetime, timedelta
from ..models import Card, Order, CardBuys, Profile
from ..forms import CardForm, CardFormBuys
from datetime import timedelta

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
        widget=forms.Select(attrs={'class': 'form-control'})
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
        user = User.objects.create_user(username=username, password=password)
        user.profile.role = role
        user.profile.save()
        return user


@login_required
def admin_home_page(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    student_count = Profile.objects.filter(role='student').count()
    return render(request, 'main/admin_dashboard/admin_home_page.html', {
        'student_count': student_count,
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

        if 'delete_account' in request.POST:
            user = request.user
            username = user.username
            user.delete()
            logout(request)
            messages.success(request, f"Ваш аккаунт '{username}' был успешно удалён.")
            return redirect('login')

        # Сохранение настроек автоперехода (добавьте этот блок)
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
    if request.method == 'POST' and 'add' in request.POST:
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Блюдо добавлено!")
            return redirect('admin_card_edit')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form = CardForm()
    if request.method == 'POST' and 'delete' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.delete()
        messages.success(request, "Блюдо удалено.")
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
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'main/admin_dashboard/admin_finance.html')


from django.contrib.auth.models import User

@login_required
def admin_users_delete_selected(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        usernames = request.POST.getlist('usernames')
        if usernames:
            deleted_count = User.objects.filter(username__in=usernames).exclude(id=request.user.id).delete()[0]
            messages.success(request, f"Успешно удалено {deleted_count} пользователей.")
        else:
            messages.warning(request, "Не выбрано ни одного пользователя.")

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
                messages.success(request, f"Пользователь '{user.username}' успешно создан как {user.profile.get_role_display()}.")
                return redirect('admin_users_statistics')
            except Exception as e:
                messages.error(request, f"Ошибка при создании пользователя: {str(e)}")

    # Сбор статистики
    users_with_roles = []
    for user in User.objects.all():
        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            role = 'student'
        users_with_roles.append({
            'username': user.username,
            'role': role
        })
    role_counts = {'student': 0, 'chef': 0, 'admin': 0}
    for ur in users_with_roles:
        role_counts[ur['role']] += 1

    return render(request, 'main/admin_dashboard/admin_users_statistics.html', {
        'users_with_roles': users_with_roles,
        'role_counts': role_counts,
        'staff_form': staff_form,
    })


@login_required
def admin_statistics(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')

    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()
    today_start = timezone.make_aware(timezone.datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(timezone.datetime.combine(now.date(), time.max))

    # === ЗАКАЗАННЫЕ БЛЮДА (все заказы) ===
    orders_today_all = Order.objects.filter(ordered_at__range=(today_start, today_end))
    orders_week_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=7))
    orders_month_all = Order.objects.filter(ordered_at__gte=now - timedelta(days=30))

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
    # === ЗАБРАННЫЕ БЛЮДА (status = 'received') ===
    orders_today_received = Order.objects.filter(
        ordered_at__range=(today_start, today_end),
        status='received'
    )
    orders_week_received = Order.objects.filter(
        ordered_at__gte=now - timedelta(days=7),
        status='received'
    )
    orders_month_received = Order.objects.filter(
        ordered_at__gte=now - timedelta(days=30),
        status='received'
    )
    total_received_today = orders_today_received.count()
    total_received_week = orders_week_received.count()
    total_received_month = orders_month_received.count()

    total_ready_today = orders_today_ready.count()
    total_ready_week = orders_week_ready.count()
    total_ready_month = orders_month_ready.count()

    # Для совместимости с текущим шаблоном (завтрак/обед)
    breakfast_count = orders_today_all.filter(card__meal_type='breakfast').count()
    lunch_count = orders_today_all.filter(card__meal_type='lunch').count()

    return render(request, 'main/admin_dashboard/admin_statistics.html', {
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'total_today': total_ordered_today,

        # Новые данные
        'total_ordered_today': total_ordered_today,
        'total_ordered_week': total_ordered_week,
        'total_ordered_month': total_ordered_month,

        'total_ready_today': total_ready_today,
        'total_ready_week': total_ready_week,
        'total_ready_month': total_ready_month,

        'total_received_today': total_received_today,
        'total_received_week': total_received_week,
        'total_received_month': total_received_month,
    })