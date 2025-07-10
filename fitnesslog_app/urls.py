from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Gear
    path('gear/', views.gear_list, name='gear_list'),
    path('gear/add/', views.gear_add, name='gear_add'),
    path('gear/<int:pk>/edit/', views.gear_edit, name='gear_edit'),
    path('gear/<int:pk>/delete/', views.gear_delete, name='gear_delete'),
    path('gear/refresh/', views.gear_refresh, name='gear_refresh'),

    # Sport
    path('sport/', views.sport_list, name='sport_list'),
    path('sport/add/', views.sport_add, name='sport_add'),
    path('sport/<int:pk>/edit/', views.sport_edit, name='sport_edit'),
    path('sport/<int:pk>/delete/', views.sport_delete, name='hrzones_delete'),

    # HRzones
    path('hzones/', views.hrzones_list, name='hrzones_list'),
    path('hrzones/add/', views.hrzones_add, name='hrzones_add'),
    path('hrzones/<int:pk>/edit/', views.hrzones_edit, name='hrzones_edit'),
    path('hrzones/<int:pk>/delete/', views.hrzones_delete, name='hrzones_delete'),
]
