from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Profile
from django.utils import timezone
from datetime import time, datetime
from .models import Card, Order,CardBuys
from .forms import CardForm, CardFormBuys
from django import forms
from django.contrib.auth.models import User


def auth_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    login_form = AuthenticationForm()
    register_form = UserCreationForm()

    if request.method == 'POST':
        # Вход
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect_by_role(user)

        # Регистрация
        elif 'register_submit' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                # Profile уже создан сигналом, но задаём роль по умолчанию
                user.profile.role = 'student'
                user.profile.save()
                login(request, user)
                return redirect_by_role(user)

    return render(request, 'main/login.html', {
        'login_form': login_form,
        'register_form': register_form,
    })


# Форма для регистрации staff (chef/admin) — можно вынести в отдельный файл позже
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

        # Дополнительная проверка сложности пароля
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


def admin_home_page(request):
    if not request.user.is_authenticated:
        return redirect('auth_view')
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return redirect('auth_view')

    # Обработка формы регистрации персонала
    staff_form = None
    registration_success = False

    if request.method == 'POST' and 'register_staff' in request.POST:
        staff_form = StaffRegistrationForm(request.POST)
        if staff_form.is_valid():
            try:
                user = staff_form.save()
                registration_success = True
                # Сохраняем информацию о успешной регистрации в сессии
                request.session['staff_registration_success'] = True
                request.session['registered_username'] = user.username
                request.session['registered_role'] = user.profile.role
                return redirect('admin_home_page')
            except Exception as e:
                messages.error(request, f"Ошибка при создании пользователя: {str(e)}")
        else:
            # Форма не валидна - сохраняем в сессии информацию об ошибке
            request.session['staff_registration_errors'] = True
    else:
        staff_form = StaffRegistrationForm()

    # Проверяем, было ли успешное создание пользователя в сессии
    if 'staff_registration_success' in request.session:
        registration_success = True
        registered_username = request.session.get('registered_username', '')
        registered_role = request.session.get('registered_role', '')
        # Очищаем данные из сессии после использования
        del request.session['staff_registration_success']
        if 'registered_username' in request.session:
            del request.session['registered_username']
        if 'registered_role' in request.session:
            del request.session['registered_role']
    else:
        registered_username = ''
        registered_role = ''

    return render(request, 'main/admin_dashboard/admin_home_page.html', {
        'staff_form': staff_form,
        'registration_success': registration_success,
        'registered_username': registered_username,
        'registered_role': registered_role,
    })


def redirect_by_role(user):
    try:
        role = user.profile.role
    except Profile.DoesNotExist:
        role = 'student'

    match role:
        case 'chef':
            return redirect('chef_dashboard/chef_home_page')
        case 'admin':
            return redirect('admin_dashboard/admin_home_page')
        case 'student':
            return redirect('student_dashboard/student_home_page')
    return redirect('login')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'main/index.html')


def student_home_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        return redirect('login')
    return render(request, 'main/student_dashboard/student_home_page.html')


def chef_home_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'chef':
        return redirect('login')
    return render(request, 'main/chef_dashboard/chef_home_page.html')


def index(request):
    return render(request, 'main/index.html')


# views.py
def admin_card_edit(request):
    if request.method == 'POST' and 'add' in request.POST:
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Блюдо добавлено!")
            return redirect('admin_card_edit')
        else:
            # Форма не валидна — покажем ошибки через messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form = CardForm()

    # Удаление (остаётся без изменений)
    if request.method == 'POST' and 'delete' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('admin_card_edit')

    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/admin_dashboard/admin_card_edit.html', {'form': form, 'cards': cards})


# --- Просмотр блюд + заказ ---
def card_view(request):
    # Удаляем старые заказы (на случай, если задача не сработала)
    _cleanup_old_orders()

    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/card_view.html', {'cards': cards})


# --- Создание заказа ---
def order_create(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    Order.objects.create(card=card)
    messages.success(request, f"Вы заказали: {card.title}!")
    return redirect('card_view')


# --- Страница заказов ---
def order_list(request):
    _cleanup_old_orders()  # на всякий случай
    orders = Order.objects.select_related('card').all().order_by('-ordered_at')
    return render(request, 'main/order_list.html', {'orders': orders})


# --- Вспомогательная функция: удалить заказы старше 23:00 прошлого дня ---
def _cleanup_old_orders():
    now = timezone.localtime(timezone.now())
    # Если сейчас после 23:00, то удаляем всё
    if now.time() >= time(23, 0):
        Order.objects.all().delete()
        return

    # Иначе удаляем заказы, созданные **вчера или раньше**
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    Order.objects.filter(ordered_at__lt=today_start).delete()


def student_menu(request):
    if request.method == 'POST' and 'add' in request.POST:
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Блюдо добавлено!")
            return redirect('student_card_edit')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form = CardForm()

    # Удаление (остаётся без изменений)
    if request.method == 'POST' and 'delete' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('student_menu')

    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/student_dashboard/student_menu.html', {'form': form, 'cards': cards})

def student_feedback(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/student_dashboard/student_feedback.html')


def card_delete(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/admin_dashboard/card_delete.html')


def student_my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/student_dashboard/student_my_orders.html')


def admin_buys(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/admin_dashboard/admin_buys.html')


def admin_finance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/admin_dashboard/admin_finance.html')


def admin_statistics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/admin_dashboard/admin_statistics.html')


def admin_users(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/admin_dashboard/admin_users.html')



def chef_card_edit(request):
    if request.method == 'POST' and 'add' in request.POST:
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Блюдо добавлено!")
            return redirect('chef_card_edit')
        else:
            # Форма не валидна — покажем ошибки через messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form = CardForm()

    # Удаление (остаётся без изменений)
    if request.method == 'POST' and 'delete' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('chef_card_edit')

    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/chef_dashboard/chef_card_edit.html', {'form': form, 'cards': cards})

def chef_remaining_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/chef_dashboard/chef_remaining_product.html')

def chef_buys(request):
    if request.method == 'POST' and 'add' in request.POST:
        form_buys = CardFormBuys(request.POST)
        if form_buys.is_valid():
            form_buys.save()
            messages.success(request, "Запрос отправлен!")
            return redirect('chef_buys')
        else:
            # Форма не валидна — покажем ошибки через messages
            for field, errors in form_buys.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form_buys = CardFormBuys()

    # Удаление (остаётся без изменений)
    if request.method == 'POST' and 'delete' in request.POST:
        card_id_buys = request.POST.get('card_id_buys')
        form_buys = get_object_or_404(CardBuys, id=card_id_buys)
        form_buys.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('chef_buys')
    buys = CardBuys.objects.all().order_by( 'title')
    return render(request, 'main/chef_dashboard/chef_buys.html', {'form_buys': form_buys, 'buys': buys})

def chef_statistics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/chef_dashboard/chef_statistics.html')

def chef_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'main/chef_dashboard/chef_orders.html')