from django.urls import path

from . import views

urlpatterns = [
    path('', views.cycle_list, name='cycle_list'),
    path('new/', views.cycle_create, name='cycle_create'),
    path('<int:pk>/edit/', views.cycle_update, name='cycle_update'),
    path('<int:pk>/delete/', views.cycle_delete, name='cycle_delete'),
    path('all/', views.cycle_admin_list, name='cycle_admin_list'),
]
