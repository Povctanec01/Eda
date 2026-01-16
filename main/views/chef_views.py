# main/views/chef_views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from ..models import Card, Order, CardBuys, Profile
from ..forms import CardForm, CardFormBuys
from datetime import timedelta
from django.utils import timezone

@login_required
def chef_home_page(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'chef':
        return redirect('login')

    # Обработка POST-запросов
    if request.method == 'POST':
        # Удаление заявки на закупку
        if 'delete' in request.POST:
            card_id_buys = request.POST.get('card_id_buys')
            buy = get_object_or_404(CardBuys, id=card_id_buys)
            buy.delete()
            messages.success(request, "Заявка удалена.")
            return redirect('chef_dashboard/chef_home_page')

        # Отметка заказа как готового
        order_id = request.POST.get('order_id')
        if order_id:
            order = get_object_or_404(Order, id=order_id, status='pending')
            order.status = 'ready'
            order.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('chef_dashboard/chef_home_page')

    # GET-часть
    form_buys = CardFormBuys()
    buys = CardBuys.objects.all().order_by('-created_at')[:2]
    recent_orders = Order.objects.filter(status='pending').select_related('user', 'card').order_by('ordered_at')[:3]
    all_orders_count = Order.objects.filter(status='pending').count()

    return render(request, 'main/chef_dashboard/chef_home_page.html', {
        'orders': recent_orders,
        'all_orders_count': all_orders_count,
        'form_buys': form_buys,
        'buys': buys
    })

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
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'chef':
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
    cards = Card.objects.all().order_by('meal_type', 'title')
    return render(request, 'main/chef_dashboard/chef_card_edit.html', {'form': form, 'cards': cards})

@login_required
def chef_buys(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'chef':
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
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'main/chef_dashboard/chef_remaining_product.html')

@login_required
def chef_statistics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'main/chef_dashboard/chef_statistics.html')