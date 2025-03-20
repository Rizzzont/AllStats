from django.urls import path
from . import views
from users import views as user_views

urlpatterns = [
    path('', views.index, name="main"),
    path('analytics/', views.analytics, name="analytics"),
    path('recomendations/', views.recomendations, name="recomendations"),
    path('private_requests/', views.private_requests, name="private_requests"),
    path('register/', user_views, name="register"),
    path('login/', views.login, name="login"),
]

