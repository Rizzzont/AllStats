from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_excel, name='upload'),
    path('main/', views.main, name="main"),
    path('analytics/', views.analytics, name="analytics"),
    path('recomendations/', views.recomendations, name="recomendations"),
    path('private_requests/', views.private_requests, name="private_requests"),
    path('delete/', views.delete_data, name='delete_data'),

]

handler404 = views.custom_404_view