# main/views/common_views.py
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from ..models import Profile


# main/views/common_views.py (добавьте эту функцию)

def enter_profile(request):
    """Переход в профиль при нажатии на кнопку 'Войти в профиль'"""
    if not request.user.is_authenticated:
        return redirect('login')

    return redirect_to_profile(request.user)
def auth_view(request):
    """Страница входа/регистрации"""
    # Если пользователь уже авторизован, сразу переходим в профиль
    if request.user.is_authenticated:
        return redirect_to_profile(request.user)

    login_form = AuthenticationForm()
    register_form = UserCreationForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect_to_profile(user)

        elif 'register_submit' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                user.profile.role = 'student'
                user.profile.save()
                login(request, user)
                return redirect_to_profile(user)

    return render(request, 'main/login.html', {
        'login_form': login_form,
        'register_form': register_form,
    })


def redirect_to_profile(user):
    """Перенаправление в профиль пользователя"""
    try:
        profile = user.profile
        role = profile.role

        match role:
            case 'chef':
                return redirect('chef_dashboard/chef_home_page')
            case 'admin':
                return redirect('admin_dashboard/admin_home_page')
            case 'student':
                return redirect('student_dashboard/student_home_page')
            case _:
                return redirect('index')

    except Profile.DoesNotExist:
        # Если профиль не создан - создаем его
        Profile.objects.create(user=user, role='student')
        return redirect('student_dashboard/student_home_page')


def logout_view(request):
    """Выход из системы"""
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'main/index.html')


def index(request):
    """Главная страница"""
    # Если пользователь авторизован И включена настройка автоперехода
    if request.user.is_authenticated:
        try:
            profile = request.user.profile

            # Проверяем настройку автоперехода
            if profile.auto_redirect_to_home:
                return redirect_to_profile(request.user)

            # Если автопереход выключен - остаемся на главной

        except Profile.DoesNotExist:
            # Если профиль не создан - создаем его
            Profile.objects.create(user=request.user, role='student')

    # Для неавторизованных или если автопереход выключен - показываем обычную главную
    return render(request, 'main/index.html')