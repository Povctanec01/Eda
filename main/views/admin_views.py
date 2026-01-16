# main/views/admin_views.py
from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, datetime
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
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return redirect('auth_view')
    staff_form = None
    registration_success = False
    if request.method == 'POST' and 'register_staff' in request.POST:
        staff_form = StaffRegistrationForm(request.POST)
        if staff_form.is_valid():
            try:
                user = staff_form.save()
                registration_success = True
                request.session['staff_registration_success'] = True
                request.session['registered_username'] = user.username
                request.session['registered_role'] = user.profile.role
                return redirect('admin_home_page')
            except Exception as e:
                messages.error(request, f"Ошибка при создании пользователя: {str(e)}")
        else:
            request.session['staff_registration_errors'] = True
    else:
        staff_form = StaffRegistrationForm()
    if 'staff_registration_success' in request.session:
        registration_success = True
        registered_username = request.session.get('registered_username', '')
        registered_role = request.session.get('registered_role', '')
        del request.session['staff_registration_success']
        if 'registered_username' in request.session:
            del request.session['registered_username']
        if 'registered_role' in request.session:
            del request.session['registered_role']
    else:
        registered_username = ''
        registered_role = ''
    student_count = Profile.objects.filter(role='student').count()
    return render(request, 'main/admin_dashboard/admin_home_page.html', {
        'student_count': student_count,
        'staff_form': staff_form,
        'registration_success': registration_success,
        'registered_username': registered_username,
        'registered_role': registered_role,
    })

@login_required
def admin_settings(request):
    if not (hasattr(request.user, 'profile') or request.user.profile.role != 'admin'):
        messages.error(request, "У вас нет доступа к этой странице.")
        return redirect('student_dashboard/student_home_page')

    if request.method == 'POST':
        # Удаление аккаунта
        user = request.user
        username = user.username
        user.delete()
        logout(request)
        messages.success(request, f"Ваш аккаунт '{username}' был успешно удалён.")
        return redirect('login')

    # GET: просто показываем страницу настроек
    return render(request, 'main/admin_dashboard/admin_settings.html')

@login_required
def admin_card_edit(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return redirect('auth_view')
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
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return redirect('auth_view')
    one_week_ago = timezone.now() - timedelta(days=7)
    buys_queryset = CardBuys.objects.filter(created_at__gte=one_week_ago)

    pending_count = buys_queryset.filter(status='pending').count()
    rejected_count = buys_queryset.filter(status='rejected').count()
    approved_count = buys_queryset.filter(status='approved').count()
    if request.method == 'POST':
        # Обработка Принять / Отклонить
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

        # Обработка удаления
        if 'delete' in request.POST:
            card_id_buys = request.POST.get('card_id_buys')
            buy = get_object_or_404(CardBuys, id=card_id_buys)
            buy.delete()
            messages.success(request, "Блюдо удалено.")
            return redirect('admin_buys')

        # Обработка добавления (остаётся без изменений)
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
        'approved_count': approved_count,})

@login_required
def admin_finance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'main/admin_dashboard/admin_finance.html')

@login_required
def admin_users_statistics(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Доступ запрещён.")
        return redirect('auth_view')
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
    })

@login_required
def admin_statistics(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')
    today = timezone.now().date()
    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))
    breakfast_count = Order.objects.filter(
        ordered_at__range=(start_of_day, end_of_day),
        card__meal_type='breakfast'
    ).count()
    lunch_count = Order.objects.filter(
        ordered_at__range=(start_of_day, end_of_day),
        card__meal_type='lunch'
    ).count()
    total_today = breakfast_count + lunch_count
    return render(request, 'main/admin_dashboard/admin_statistics.html', {
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'total_today': total_today,
    })