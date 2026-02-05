from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from main.models import Profile

#Переход в профиль при нажатии на кнопку 'Войти в профиль'
def enter_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect_to_profile(request.user)

#login
def auth_view(request):
    # Редирект на домашнюю страницу в
    if request.user.is_authenticated:
        return redirect_to_profile(request.user)
    login_form = AuthenticationForm()
    register_form = UserCreationForm()

    #Авторизация
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

        #Регестрация
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

#Редиректы
def redirect_to_profile(user):
    try:
        profile = user.profile
        role = profile.role

        match role:
            case 'chef':
                # Проверяем, является ли поваром
                if profile.role == 'chef':
                    return redirect('chef_home_page')
            case 'admin':
                # Проверяем, является ли администратором (суперпользователем)
                if user.is_superuser or profile.role == 'admin':
                    return redirect('admin_home_page')
            case 'student':
                if profile.role == 'student':
                    return redirect('student_home_page')
            case _:
                return redirect('index')

    except Profile.DoesNotExist:
        Profile.objects.create(user=user, role='student')
        return redirect('student_home_page')

    # Если возникла ошибка
    return redirect('index')

#Выход
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'main/index.html')

#Главная страница
def index(request):
    # Если пользователь авторизован И включена настройка автоперехода
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.auto_redirect_to_home:
                return redirect_to_profile(request.user)

        except Profile.DoesNotExist:
            # Если профиль не создан - создаем его
            Profile.objects.create(user=request.user, role='student')

    return render(request, 'main/index.html')