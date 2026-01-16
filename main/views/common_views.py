# main/views/common_views.py
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from ..models import Profile

def auth_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
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
                    return redirect_by_role(user)
        elif 'register_submit' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                user.profile.role = 'admin'
                user.profile.save()
                login(request, user)
                return redirect_by_role(user)
    return render(request, 'main/login.html', {
        'login_form': login_form,
        'register_form': register_form,
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

def index(request):
    return render(request, 'main/index.html')