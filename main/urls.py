
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),
    path('index.html', views.index),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.auth_view, name='login'),

    path('student_dashboard/student_home_page', views.student_home_page, name='student_dashboard/student_home_page'),
    path('student_feedback', views.student_feedback , name='student_feedback'),
    path('student_menu', views.student_menu , name='student_menu'),
    path('student_my_orders', views.student_my_orders , name='student_my_orders'),

    path('chef_dashboard/chef_home_page', views.chef_home_page, name='chef_dashboard/chef_home_page'),
    path('chef_card_edit/', views.chef_card_edit , name='chef_card_edit'),
    path('chef_remaining_product', views.chef_remaining_product , name='chef_remaining_product'),
    path('chef_buys', views.chef_buys , name='chef_buys'),
    path('chef_statistics', views.chef_statistics , name='chef_statistics'),
    path('chef_orders', views.chef_orders , name='chef_orders'),

    path('admin_dashboard/admin_home_page', views.admin_home_page, name='admin_dashboard/admin_home_page'),
    path('admin_buys', views.admin_buys , name='admin_buys'),
    path('admin_finance', views.admin_finance , name='admin_finance'),
    path('admin_statistics', views.admin_statistics , name='admin_statistics'),
    path('admin_users_statistics', views.admin_users_statistics , name='admin_users_statistics'),
    path('admin_card_edit/', views.admin_card_edit, name='admin_card_edit'),
    path('order/<int:card_id>/', views.order_create, name='order_create'),
    path('delete/<int:card_id>/', views.card_delete, name='card_delete'),
    path('student/order/<int:card_id>/', views.student_order_create, name='student_order_create'),
]