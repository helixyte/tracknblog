# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('update/', views.update_location, name='update_location'),
    path('latest/', views.get_latest_location, name='get_latest_location'),
]
