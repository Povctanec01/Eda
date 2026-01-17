# main/urls.py
from django.urls import path
from .views import common_views, student_views, chef_views, admin_views

urlpatterns = [
    path('', common_views.index, name='index'),
    path('index.html', common_views.index),
    path('logout/', common_views.logout_view, name='logout'),
    path('login/', common_views.auth_view, name='login'),

    # Student
    path('student_dashboard/student_home_page', student_views.student_home_page,name='student_dashboard/student_home_page'),
    path('student_feedback', student_views.student_feedback, name='student_feedback'),
    path('student_menu', student_views.student_menu, name='student_menu'),
    path('student_my_orders', student_views.student_my_orders, name='student_my_orders'),
    path('student_order_history', student_views.student_order_history, name='student_order_history'),
    path('student_settings', student_views.student_settings, name='student_settings'),
    path('student/order/create/<int:card_id>/', student_views.student_order_create, name='student_order_create'),

    # Chef
    path('chef_dashboard/chef_home_page', chef_views.chef_home_page, name='chef_dashboard/chef_home_page'),
    path('chef_card_edit/', chef_views.chef_card_edit, name='chef_card_edit'),
    path('chef_remaining_product', chef_views.chef_remaining_product, name='chef_remaining_product'),
    path('chef_buys', chef_views.chef_buys, name='chef_buys'),
    path('chef_statistics', chef_views.chef_statistics, name='chef_statistics'),
    path('chef_orders', chef_views.chef_orders, name='chef_orders'),
    path('chef_settings', chef_views.chef_settings, name='chef_settings'),

    # Admin
    path('admin_dashboard/admin_home_page', admin_views.admin_home_page, name='admin_dashboard/admin_home_page'),
    path('admin_buys', admin_views.admin_buys, name='admin_buys'),
    path('admin_finance', admin_views.admin_finance, name='admin_finance'),
    path('admin_statistics', admin_views.admin_statistics, name='admin_statistics'),
    path('admin_users_statistics', admin_views.admin_users_statistics, name='admin_users_statistics'),
    path('admin_settings', admin_views.admin_settings, name='admin_settings'),
    path('admin_card_edit/', admin_views.admin_card_edit, name='admin_card_edit'),
    path('delete/<int:card_id>/', common_views.index, name='card_delete'),  # заменил на index временно
    path('admin/users/delete-selected/', admin_views.admin_users_delete_selected, name='admin_users_delete_selected'),
]