from main.views.student_views import update_critical_allergens, update_non_critical_allergens
from main.views.student_views import submit_review, delete_review
from .views import common_views, student_views, chef_views, admin_views
from .views.chef_views import chef_allergens
from django.urls import path

handler404 = common_views.custom_404
handler500 = common_views.custom_500

urlpatterns = [
    path('',common_views.index, name='index'),
    path('index.html',common_views.index),
    path('logout/',common_views.logout_view, name='logout'),
    path('login/',common_views.auth_view, name='login'),
    path('enter-profile/',common_views.enter_profile, name='enter_profile'),

#student
    path('student_home_page',student_views.student_home_page, name='student_home_page'),
    path('student_feedback',student_views.student_feedback, name='student_feedback'),
    path('student_menu',student_views.student_menu, name='student_menu'),
    path('student_my_orders',student_views.student_my_orders, name='student_my_orders'),
    path('studen_buffet', student_views.student_buffet, name='student_buffet'),
    path('student_allergens', student_views.student_allergens, name='student_allergens'),
    path('student/likes', student_views.student_likes, name='student_likes'),
    path('student_settings', student_views.student_settings, name='student_settings'),
    path('student/order/create/<int:card_id>/',student_views.student_order_create, name='student_order_create'),
    path('student/order/<int:order_id>/mark-received/',student_views.student_mark_received, name='student_mark_received'),
    path('student/allergens/critical/update/',update_critical_allergens, name='update_critical_allergens'),
    path('student/allergens/non-critical/update/',update_non_critical_allergens, name='update_non_critical_allergens'),
    path('student/top-up-balance/', student_views.top_up_balance, name='student_top_up_balance'),
    path('student/toggle-like/<int:card_id>/', student_views.toggle_like, name='toggle_like'),
    path('student/submit-review/', submit_review, name='submit_review'),
    path('student/delete-review/<int:review_id>/', delete_review, name='delete_review'),


#chef
    path('chef_home_page',chef_views.chef_home_page, name='chef_home_page'),
    path('chef_card_edit',chef_views.chef_card_edit, name='chef_card_edit'),
    path('chef_remaining_product',chef_views.chef_remaining_product, name='chef_remaining_product'),
    path('chef_buys',chef_views.chef_buys, name='chef_buys'),
    path('chef_statistics',chef_views.chef_statistics, name='chef_statistics'),
    path('chef_orders',chef_views.chef_orders, name='chef_orders'),
    path('chef_buffet', chef_views.chef_buffet, name='chef_buffet'),
    path('chef_settings',chef_views.chef_settings, name='chef_settings'),
    path('chef/remaining-product/', chef_views.chef_remaining_product, name='chef_remaining_product'),
    path('chef/allergens/',chef_views.chef_allergens, name='chef_allergens'),
    path('chef/allergens/',chef_allergens, name='chef_allergens'),
    path('chef/get-allergens/',chef_views.get_allergens, name='get_allergens'),


#admin
    path('admin_dashboard/admin_home_page',admin_views.admin_home_page, name='admin_home_page'),
    path('admin_dashboard/buys',admin_views.admin_buys, name='admin_buys'),
    path('admin_dashboard/finance',admin_views.admin_finance, name='admin_finance'),
    path('admin_dashboard/statistics_buys',admin_views.admin_statistics_buys, name='admin_statistics_buys'),
    path('admin_dashboard/users_statistics',admin_views.admin_users_statistics, name='admin_users_statistics'),
    path('admin_dashboard/card_edit',admin_views.admin_card_edit, name='admin_card_edit'),
    path('admin_dashboard/settings', admin_views.admin_settings, name='admin_settings'),
    path('admin_dashboard/users/delete-selected/', admin_views.admin_users_delete_selected,name='admin_users_delete_selected'),
    path('delete/<int:card_id>/',common_views.index, name='card_delete'),
    path('admin_finance/pdf/', admin_views.generate_finance_pdf, name='generate_finance_pdf'),

]