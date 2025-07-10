from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Gear
    path('gear/', views.gear_list, name='gear_list'),
    path('gear/add/', views.gear_add, name='gear_add'),
    path('gear/<int:pk>/edit/', views.gear_edit, name='gear_edit'),
    path('gear/<int:pk>/delete/', views.gear_delete, name='gear_delete'),
]
