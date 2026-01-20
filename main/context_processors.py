from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from .models import CardBuys
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

def admin_sidebar_context(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
        one_week_ago = timezone.now() - timedelta(days=7)
        pending_count = CardBuys.objects.filter(
            created_at__gte=one_week_ago,
            status='pending'
        ).count()
        return {'pending_count': pending_count}
    return {}


def student_unclaimed_orders_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        from .models import Order
        count = Order.objects.filter(user=request.user, status='ready').count()
        return {'unclaimed_orders_count': count}
    return {'unclaimed_orders_count': 0}