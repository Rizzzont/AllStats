from django.urls import path
from . import views
from users import views as user_views

urlpatterns = [
    path('', views.index, name="main"),
    path('analytics/', views.analytics, name="analytics"),
    path('recomendations/', views.recomendations, name="recomendations"),
    path('private_requests/', views.private_requests, name="private_requests"),
    path('login/', user_views.login_view, name='login'),
    path('register/', user_views.register_view, name='register'),
    path('logout/', user_views.logout_view, name='logout'),
]

handler404 = views.custom_404_view