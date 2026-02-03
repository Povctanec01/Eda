from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from main.models import Card, Order, CardBuys, Profile, Allergen, ProductRemaining
from main.forms import CardForm, CardFormBuys, ProductRemainingForm
from datetime import timedelta, time
from django.utils import timezone
from django import forms
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator

@login_required
def chef_home_page(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'chef'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Доступ запрещён'}, status=403)
        return redirect('login')

    products = ProductRemaining.objects.all().order_by('name')
    low_stock_count = sum(1 for product in products if product.is_low_stock())

    # Обработка POST-запросов
    if request.method == 'POST':
        # Удаление заявки на закупку
        if 'delete' in request.POST:
            card_id_buys = request.POST.get('card_id_buys')
            buy = get_object_or_404(CardBuys, id=card_id_buys)
            buy.delete()
            messages.success(request, "Заявка удалена.")
            return redirect('chef_home_page')

        # Отметка заказа как готового
        order_id = request.POST.get('order_id')
        if order_id:
            order = get_object_or_404(Order, id=order_id, status='pending')
            order.status = 'ready'
            order.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('chef_home_page')

    # GET-часть
    form_buys = CardFormBuys()
    buys = CardBuys.objects.all().order_by('-created_at')[:2]
    recent_orders = Order.objects.filter(status='pending').select_related('user', 'card').order_by('ordered_at')[:3]
    all_orders_count = Order.objects.filter(status='pending').count()

    return render(request, 'main/chef_dashboard/chef_home_page.html', {
        'orders': recent_orders,
        'all_orders_count': all_orders_count,
        'form_buys': form_buys,
        'buys': buys,
        'low_stock_count': low_stock_count,
    })


class AllergenForm(forms.ModelForm):
    class Meta:
        model = Allergen
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название аллергена'})
        }

@login_required
def chef_allergens(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')

    query = request.GET.get('q', '').strip()
    allergens = Allergen.objects.all().order_by('name')

    if query:
        allergens = allergens.filter(name__icontains=query)

    # Пагинация - 10 элементов на страницу
    paginator = Paginator(allergens, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        if 'add' in request.POST:
            form = AllergenForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Аллерген добавлен!")
                return redirect('chef_allergens')
            else:
                for error in form.errors.values():
                    messages.error(request, f"Ошибка: {error}")
        elif 'delete' in request.POST:
            allergen_id = request.POST.get('allergen_id')
            allergen = get_object_or_404(Allergen, id=allergen_id)
            allergen.delete()
            messages.success(request, f"Аллерген «{allergen.name}» удалён.")
            return redirect('chef_allergens')

    form = AllergenForm()
    return render(request, 'main/chef_dashboard/chef_allergens.html', {
        'form': form,
        'allergens': page_obj,  # Используем page_obj вместо полного queryset
        'page_obj': page_obj,   # Для пагинации в шаблоне
        'query': query
    })


@login_required
def chef_settings(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
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
                return redirect('chef_settings')

            # Проверка совпадения новых паролей
            if new_password1 != new_password2:
                messages.error(request, "Новые пароли не совпадают.")
                return redirect('chef_settings')

            # Проверка длины пароля
            if len(new_password1) < 8:
                messages.error(request, "Пароль должен содержать минимум 8 символов.")
                return redirect('chef_settings')

            # Изменение пароля
            request.user.set_password(new_password1)
            request.user.save()

            # Обновляем сессию, чтобы пользователь не разлогинился
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, "Пароль успешно изменён!")
            return redirect('chef_settings')

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
        return redirect('chef_settings')

    # GET: просто показываем страницу настроек
    return render(request, 'main/chef_dashboard/chef_settings.html')

@login_required
def chef_orders(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id, status='pending')
        order.status = 'ready'
        order.save()
        return JsonResponse({'success': True})
    orders = Order.objects.filter(status='pending').select_related('user', 'card').order_by('ordered_at')
    return render(request, 'main/chef_dashboard/chef_orders.html', {'orders': orders})

@login_required
def chef_card_edit(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')

    if request.method == 'POST' and 'add' in request.POST:
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Блюдо добавлено!")
            return redirect('chef_card_edit')
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
        return redirect('chef_card_edit')

    if request.method == 'POST' and 'toggle_visibility' in request.POST:
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        card.is_hidden = not card.is_hidden  # Переключаем статус
        card.save()

        action = "скрыто" if card.is_hidden else "отображено"
        messages.success(request, f"Блюдо «{card.title}» {action}.")
        return redirect('chef_card_edit')


    # Получаем все блюда, включая скрытые
    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/chef_dashboard/chef_card_edit.html', {
        'form': form,
        'cards': cards
    })


@login_required
def chef_buys(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')
    one_week_ago = timezone.now() - timedelta(days=7)
    buys_queryset = CardBuys.objects.filter(created_at__gte=one_week_ago)

    pending_count = buys_queryset.filter(status='pending').count()
    rejected_count = buys_queryset.filter(status='rejected').count()
    approved_count = buys_queryset.filter(status='approved').count()
    if request.method == 'POST' and 'add' in request.POST:
        form_buys = CardFormBuys(request.POST)
        if form_buys.is_valid():
            form_buys.save()
            messages.success(request, "Запрос отправлен!")
            return redirect('chef_buys')
        else:
            for field, errors in form_buys.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка: {error}")
    else:
        form_buys = CardFormBuys()
    if 'delete' in request.POST:
        card_id_buys = request.POST.get('card_id_buys')
        buy = get_object_or_404(CardBuys, id=card_id_buys)
        buy.delete()
        messages.success(request, "Блюдо удалено.")
        return redirect('chef_buys')
    buys = CardBuys.objects.all().order_by('-created_at')
    return render(request, 'main/chef_dashboard/chef_buys.html', {
        'form_buys': form_buys,
        'buys': buys,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'approved_count': approved_count,
    })


@login_required
def chef_remaining_product(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')

    # Получаем все продукты
    products = ProductRemaining.objects.all().order_by('name')

    # Форма для добавления нового продукта
    form = ProductRemainingForm()

    # Обработка POST-запросов
    if request.method == 'POST':
        # Проверяем, это AJAX-запрос или обычный POST
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Добавление нового продукта
        if 'add_product' in request.POST and not is_ajax:
            form = ProductRemainingForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Продукт успешно добавлен!")
                return redirect('chef_remaining_product')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Ошибка в поле '{field}': {error}")

        # Удаление продукта
        elif 'delete_product' in request.POST and not is_ajax:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(ProductRemaining, id=product_id)
            product_name = product.name
            product.delete()
            messages.success(request, f"Продукт '{product_name}' удалён.")
            return redirect('chef_remaining_product')

        # Обновление количества продукта
        elif 'update_quantity' in request.POST:
            product_id = request.POST.get('product_id')
            new_quantity = request.POST.get('new_quantity')

            try:
                product = get_object_or_404(ProductRemaining, id=product_id)
                product.quantity = Decimal(new_quantity)
                product.save()

                # Если это AJAX-запрос, возвращаем JSON
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'product_id': product.id,  # ВАЖНО: возвращаем ID
                        'product_name': product.name,
                        'new_quantity': str(product.quantity),
                        'unit': product.unit,
                        'is_low_stock': product.is_low_stock()
                    })
                else:
                    messages.success(request, f"Количество '{product.name}' обновлено.")
                    return redirect('chef_remaining_product')

            except (ValueError, ValidationError) as e:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': str(e)})
                else:
                    messages.error(request, f"Ошибка обновления: {str(e)}")
                    return redirect('chef_remaining_product')

    # Подсчёт низких запасов
    low_stock_count = sum(1 for product in products if product.is_low_stock())

    return render(request, 'main/chef_dashboard/chef_remaining_product.html', {
        'products': products,
        'form': form,
        'low_stock_count': low_stock_count,
        'total_products': products.count()
    })


@login_required
def edit_product_modal(request, product_id):
    """Представление для редактирования продукта через модальное окно"""
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return JsonResponse({'success': False, 'error': 'Доступ запрещён'}, status=403)

    product = get_object_or_404(ProductRemaining, id=product_id)

    if request.method == 'POST':
        form = ProductRemainingForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'product_name': product.name,
                'quantity': str(product.quantity),
                'unit': product.unit,
                'min_quantity': str(product.min_quantity)
            })
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})

    # Для GET-запроса возвращаем HTML формы
    form = ProductRemainingForm(instance=product)
    html = render_to_string('main/chef_dashboard/edit_product_modal.html', {
        'form': form,
        'product': product
    }, request=request)

    return JsonResponse({'success': True, 'html': html})

@login_required
def chef_statistics(request):
    if not request.user.is_authenticated or request.user.profile.role != 'chef':
        return redirect('login')

    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    today_start = timezone.make_aware(timezone.datetime.combine(now.date(), time.min))
    today_end = timezone.make_aware(timezone.datetime.combine(now.date(), time.max))

    # Все готовые, но не забранные заказы
    unclaimed_orders = Order.objects.filter(
        status='ready',
        ordered_at__range=(today_start, today_end)
    ).select_related('user', 'card').order_by('ordered_at')

    unclaimed_count = unclaimed_orders.count()

    return render(request, 'main/chef_dashboard/chef_statistics.html', {
        'unclaimed_orders': unclaimed_orders,
        'unclaimed_count': unclaimed_count,
    })


@require_GET
@login_required
def get_allergens(request):
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    limit = 30
    offset = (page - 1) * limit

    allergens = Allergen.objects.all()
    if query:
        allergens = allergens.filter(name__icontains=query)

    total_count = allergens.count()
    allergens = allergens[offset:offset + limit]

    results = []
    for a in allergens:
        results.append({
            'id': a.id,
            'text': a.name
        })

    return JsonResponse({
        'items': results,
        'total_count': total_count
    })