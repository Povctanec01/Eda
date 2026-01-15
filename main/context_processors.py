from django.apps import apps

def chef_orders_count(request):
    try:
        if request.user.is_authenticated:
            Profile = apps.get_model('main', 'Profile')
            Order = apps.get_model('main', 'Order')
            if hasattr(request.user, 'profile') and request.user.profile.role == 'chef':
                count = Order.objects.filter(status='pending').count()
                return {'chef_active_orders_count': count}
    except Exception:
        pass
    return {'chef_active_orders_count': 0}