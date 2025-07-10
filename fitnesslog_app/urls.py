from django.urls import path
from . import views

urlpatterns = [
    path('', views.summary, name='summary'),

    # Gear
    path('gear/', views.gear_list, name='gear_list'),
    path('gear/add/', views.gear_add, name='gear_add'),
    path('gear/<int:pk>/edit/', views.gear_edit, name='gear_edit'),
    path('gear/<int:pk>/delete/', views.gear_delete, name='gear_delete'),
    path('gear/refresh/', views.gear_refresh, name='gear_refresh'),

    # Sport
    path('sports/', views.sport_list, name='sport_list'),
    path('sport/add/', views.sport_add, name='sport_add'),
    path('sport/<int:pk>/edit/', views.sport_edit, name='sport_edit'),
    path('sport/<int:pk>/delete/', views.sport_delete, name='sport_delete'),

    # HRzones
    path('hrzones/', views.hrzones_list, name='hrzones_list'),
    path('hrzones/add/', views.hrzones_add, name='hrzones_add'),
    path('hrzones/<int:pk>/edit/', views.hrzones_edit, name='hrzones_edit'),
    path('hrzones/<int:pk>/delete/', views.hrzones_delete, name='hrzones_delete'),

    # Activity
    path('activity/', views.activity_list, name='activity_list'),
    path('activity/add/', views.activity_add, name='activity_add'),
    path('activity/add-from-file/', views.activity_add_from_file, name='activity_add_from_file'),
    path('activity/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activity/<int:pk>/delete/', views.activity_delete, name='activity_delete'),

    # Injury
    path('injury/', views.injury_list, name='injury_list'),
    path('injury/add/', views.injury_add, name='injury_add'),
    path('injury/<int:pk>/edit/', views.injury_edit, name='injury_edit'),
    path('injury/<int:pk>/delete/', views.injury_delete, name='injury_delete'),

    # Illness
    path('illness/', views.illness_list, name='illness_list'),
    path('illness/add/', views.illness_add, name='illness_add'),
    path('illness/<int:pk>/edit/', views.illness_edit, name='illness_edit'),
    path('illness/<int:pk>/delete/', views.illness_delete, name='illness_delete'),
]
