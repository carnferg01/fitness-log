from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Gear
    path('gear/', views.gear_list, name='gear_list'),
    path('gear/add/', views.gear_add, name='gear_add'),
]
