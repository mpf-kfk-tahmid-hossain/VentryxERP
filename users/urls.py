from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),
    path('list/', views.user_list, name='user_list'),
    path('roles/', views.role_list, name='role_list'),
    path('activities/', views.user_activities, name='activities'),
    path('assign-role/', views.assign_role, name='assign_role'),
    path('remove-role/', views.remove_role, name='remove_role'),
]
