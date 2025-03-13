from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="main"),
    path('analytics/', views.analytics, name="analytics"),
    path('recomendations/', views.recomendations, name="recomendations"),
    path('private_requests', views.private_requests, name="private_requests"),
]

