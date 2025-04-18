# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
]
